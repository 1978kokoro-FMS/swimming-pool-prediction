import requests
from flask import Flask, render_template, jsonify, request
# predict.py에서 predict_visitors와 is_holiday_check 함수를 모두 가져옵니다.
from predict import predict_visitors, is_holiday_check
from datetime import datetime, timedelta

app = Flask(__name__)

# --- 1단계에서 발급받은 본인의 API 인증키를 여기에 붙여넣으세요 ---
KMA_API_KEY = "94057a00005793242a78b4e2274cef1b9da37a65d7acd6598f852bced75ddb6d"

def get_weather_forecast(target_date):
    """기상청 단기예보 API를 호출하여 특정 날짜의 날씨 예보를 가져오는 함수 (개선 버전)"""
    # 현재 시각 기준으로 가장 최근 발표 시각 계산
    now = datetime.now()
    
    # 단기예보 발표 시각: 02, 05, 08, 11, 14, 17, 20, 23시 (하루 8회)
    # 각 발표 시각 이후 10분부터 데이터 제공
    base_times = [2, 5, 8, 11, 14, 17, 20, 23]
    
    current_hour = now.hour
    current_minute = now.minute
    current_total_minutes = current_hour * 60 + current_minute
    
    # 가장 최근 발표 시각 찾기 (발표 시각 + 10분 이후)
    base_time = None
    base_date = now.strftime('%Y%m%d')
    
    for bt_hour in reversed(base_times):
        bt_total_minutes = bt_hour * 60 + 10  # 발표 시각 + 10분
        if current_total_minutes >= bt_total_minutes:
            base_time = f"{bt_hour:02d}00"
            break
    
    # 조건을 만족하는 시각이 없으면 전날 23시 데이터 사용
    if base_time is None:
        base_date = (now - timedelta(days=1)).strftime('%Y%m%d')
        base_time = '2300'
    
    print(f"[DEBUG] 현재 시각: {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"[DEBUG] Base Date: {base_date}, Base Time: {base_time}")
    
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        'serviceKey': KMA_API_KEY, 'pageNo': '1', 'numOfRows': '1000',
        'dataType': 'JSON', 'base_date': base_date, 'base_time': base_time,
        'nx': '60', 'ny': '122'
    }
    
    try:
        print(f"[DEBUG] API 호출 중...")
        response = requests.get(url, params=params, timeout=30)
        print(f"[DEBUG] HTTP 상태 코드: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[ERROR] API 에러: HTTP 상태 코드 {response.status_code}")
            print(f"[ERROR] 응답 내용: {response.text[:500]}")
            return None
        
        data = response.json()
        result_code = data.get('response', {}).get('header', {}).get('resultCode')
        result_msg = data.get('response', {}).get('header', {}).get('resultMsg', '알 수 없는 오류')
        
        print(f"[DEBUG] API Result Code: {result_code}")
        print(f"[DEBUG] API Result Message: {result_msg}")
        
        if result_code != '00':
            print(f"[ERROR] API 에러 메시지: {result_msg}")
            return None
            
        weather_data = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        print(f"[DEBUG] 받은 데이터 개수: {len(weather_data)}")
    except requests.exceptions.Timeout:
        print(f"[ERROR] API 호출 시간 초과 (30초)")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API 호출 오류: {e}")
        return None
    except ValueError as e:
        print(f"[ERROR] JSON 파싱 오류: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] 예상치 못한 오류: {e}")
        return None

    forecast = {}
    if not weather_data:
        print(f"[WARNING] 날씨 데이터가 비어있습니다.")
        return None

    target_date_str = target_date.strftime('%Y%m%d')
    print(f"[DEBUG] 목표 날짜: {target_date_str}")
    
    for item in weather_data:
        if item.get('fcstDate') != target_date_str: 
            continue
        hour = int(item.get('fcstTime', '0000')[:2])
        if hour not in forecast:
            forecast[hour] = {'기온': 0, '강수량': 0, '습도': 0, '적설': 0}
        
        category, value = item.get('category'), item.get('fcstValue')
        if value is None: continue

        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            numeric_value = 0.0

        if category == 'TMP': 
            forecast[hour]['기온'] = numeric_value
        elif category == 'REH': 
            forecast[hour]['습도'] = numeric_value
        elif category == 'PCP': 
            # 강수럄 처리 ('강수없음' → 0)
            if value == '강수없음':
                forecast[hour]['강수량'] = 0.0
            else:
                try:
                    forecast[hour]['강수량'] = float(value.replace('mm', ''))
                except:
                    forecast[hour]['강수량'] = numeric_value
        elif category == 'SNO': 
            # 적설 처리 ('적설없음' → 0)
            if value == '적설없음':
                forecast[hour]['적설'] = 0.0
            else:
                try:
                    forecast[hour]['적설'] = float(value.replace('cm', ''))
                except:
                    forecast[hour]['적설'] = numeric_value
    
    print(f"[DEBUG] 추출된 시간대: {sorted(forecast.keys())}")
    return forecast

@app.route('/')
def home():
    """기본 홈페이지를 렌더링합니다."""
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    """분석 정보 페이지를 렌더링합니다."""
    return render_template('analysis.html')

@app.route('/predict_live')
def predict_live():
    """현재 시간부터 48시간 동안의 예측을 반환합니다."""
    try:
        now = datetime.now()
        today = now.date()
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)

        weather_today = get_weather_forecast(datetime.combine(today, datetime.min.time())) or {}
        weather_tomorrow = get_weather_forecast(datetime.combine(tomorrow, datetime.min.time())) or {}
        weather_day_after = get_weather_forecast(datetime.combine(day_after, datetime.min.time())) or {}

        full_weather_forecast = {}
        for h, v in weather_today.items(): full_weather_forecast[(today, h)] = v
        for h, v in weather_tomorrow.items(): full_weather_forecast[(tomorrow, h)] = v
        for h, v in weather_day_after.items(): full_weather_forecast[(day_after, h)] = v
        
        predictions_48h = []
        for h_offset in range(48):
            target_dt = now + timedelta(hours=h_offset)
            if not (6 <= target_dt.hour <= 22): continue

            weather = full_weather_forecast.get((target_dt.date(), target_dt.hour), {'기온': 22.0, '강수량': 0, '습도': 55.0, '적설': 0})
            
            # 해당 날짜가 공휴일인지 확인합니다.
            is_holiday = is_holiday_check(target_dt.date())
            
            prediction = predict_visitors(
                year=target_dt.year, month=target_dt.month, day=target_dt.day,
                hour=target_dt.hour, day_of_week=target_dt.weekday(),
                temp=weather['기온'], rain=weather['강수량'],
                humidity=weather['습도'], snow=weather['적설'],
                is_holiday=is_holiday # 공휴일 정보를 전달합니다.
            )
            
            day_label = "오늘" if target_dt.date() == today else "내일" if target_dt.date() == tomorrow else "모레"
            prediction['label'] = f"{day_label} {target_dt.hour}시"
            predictions_48h.append(prediction)
        
        return jsonify({'predictions': predictions_48h})
    except Exception as e:
        print(f"predict_live 함수에서 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict')
def predict():
    """특정 날짜의 예측을 반환합니다."""
    try:
        date_str = request.args.get('date')
        target_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now()
        today = datetime.now()
        
        if target_date.date() < today.date():
            return jsonify({'error': '지난 날짜', 'message': f'{target_date.strftime("%Y-%m-%d")}는 지난 날짜이므로 예측 대상이 아닙니다.'}), 400
        
        weather_forecast = None
        weather_source = ""
        if (target_date.date() - today.date()).days <= 2:
             weather_forecast = get_weather_forecast(target_date)
             weather_source = "기상청 단기예보"
             if not weather_forecast:
                weather_forecast = {}
                weather_source = "기본값 사용 (API 호출 실패)"
        else:
            weather_forecast = {}
            weather_source = "날씨 정보 미포함 (예보 기간 초과)"
        
        predictions_by_hour = []
        for hour in range(6, 23):
            weather = weather_forecast.get(hour, {'기온': 22.0, '강수량': 0, '습도': 55.0, '적설': 0})
            # 해당 날짜가 공휴일인지 확인합니다.
            is_holiday = is_holiday_check(target_date.date())
            prediction = predict_visitors(
                year=target_date.year, month=target_date.month, day=target_date.day,
                hour=hour, day_of_week=target_date.weekday(),
                temp=weather['기온'], rain=weather['강수량'],
                humidity=weather['습도'], snow=weather['적설'],
                is_holiday=is_holiday # 공휴일 정보를 전달합니다.
            )
            prediction['hour'] = hour
            prediction.update(weather)
            predictions_by_hour.append(prediction)
        
        return jsonify({ 'weather_source': weather_source, 'predictions': predictions_by_hour })
    except Exception as e:
        print(f"predict 함수에서 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
