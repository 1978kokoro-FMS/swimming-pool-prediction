import requests
from flask import Flask, render_template, jsonify, request
from predict import predict_visitors
from datetime import datetime, timedelta

# Flask 앱을 생성합니다.
app = Flask(__name__)

# --- 본인의 API 인증키를 여기에 붙여넣으세요 ---
KMA_API_KEY = "6e5230b95ef0ab65ad4fb63e83f1b512f525f5a708933928098464ffa47da789"

# app.py 파일에서 이 함수 부분을 교체해주세요.

def get_weather_forecast(target_date):
    """기상청 단기예보 API를 호출하여 특정 날짜의 날씨 예보를 가져오는 함수 (안정성 강화 버전)"""
    base_date = (target_date - timedelta(days=1)).strftime('%Y%m%d')
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        'serviceKey': KMA_API_KEY, 'pageNo': '1', 'numOfRows': '1000',
        'dataType': 'JSON', 'base_date': base_date, 'base_time': '2300',
        'nx': '60', 'ny': '122'
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code != 200:
            print(f"API 에러: HTTP 상태 코드 {response.status_code}")
            return None

        data = response.json()
        # API가 보내는 에러 코드 확인
        if data.get('response', {}).get('header', {}).get('resultCode') != '00':
            error_msg = data.get('response', {}).get('header', {}).get('resultMsg', '알 수 없는 오류')
            print(f"API 에러 메시지: {error_msg}")
            return None

        weather_data = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
    except (requests.exceptions.RequestException, ValueError) as e: # JSON 디코딩 오류 포함
        print(f"API 호출 또는 JSON 파싱 오류: {e}")
        return None

    forecast = {}
    if not weather_data: return None

    for item in weather_data:
        if item.get('fcstDate') != target_date.strftime('%Y%m%d'): continue
        hour = int(item.get('fcstTime', '0000')[:2])
        if hour not in forecast:
            forecast[hour] = {'기온': 0, '강수량': 0, '습도': 0, '적설': 0}

        category, value = item.get('category'), item.get('fcstValue')
        if value is None: continue

        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            numeric_value = 0.0

        if category == 'TMP': forecast[hour]['기온'] = numeric_value
        elif category == 'REH': forecast[hour]['습도'] = numeric_value
        elif category == 'PCP': forecast[hour]['강수량'] = numeric_value
        elif category == 'SNO': forecast[hour]['적설'] = numeric_value
    return forecast

@app.route('/')
def home():
    """기본 홈페이지를 렌더링합니다."""
    return render_template('index.html')

@app.route('/predict')
def predict():
    """날짜를 받아 예측을 수행하고 결과를 반환합니다."""
    try:
        date_str = request.args.get('date')
        target_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now() + timedelta(days=1)
        today = datetime.now()
        date_difference = (target_date.replace(hour=0, minute=0, second=0, microsecond=0) - 
                           today.replace(hour=0, minute=0, second=0, microsecond=0)).days
        
        weather_forecast = None
        weather_source = ""

        if 0 <= date_difference <= 2:
            weather_forecast = get_weather_forecast(target_date)
            weather_source = "기상청 단기예보"
            if not weather_forecast:
                weather_forecast = {}
                weather_source = "기본값 사용 (API 호출 실패)"
        else:
            print("예보 기간을 벗어나 날씨 정보 없이 예측합니다.")
            weather_forecast = {}
            weather_source = "날씨 정보 미포함 (예보 기간 초과)"

        predictions_by_hour = []
        for hour in range(6, 23):
            weather = weather_forecast.get(hour, {'기온': 22.0, '강수량': 0, '습도': 55.0, '적설': 0})
            prediction = predict_visitors(
                year=target_date.year, month=target_date.month, day=target_date.day,
                hour=hour, day_of_week=target_date.weekday(),
                temp=weather['기온'], rain=weather['강수량'],
                humidity=weather['습도'], snow=weather['적설']
            )
            prediction['hour'] = hour
            prediction.update(weather)
            predictions_by_hour.append(prediction)
        
        return jsonify({
            'weather_source': weather_source,
            'predictions': predictions_by_hour
        })
    except Exception as e:
        print(f"predict 함수에서 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


