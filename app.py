import requests
from flask import Flask, render_template, jsonify, request
from predict import predict_visitors
from datetime import datetime, timedelta

# Flask 앱을 생성합니다.
app = Flask(__name__)

# --- 본인의 API 인증키를 여기에 붙여넣으세요 ---
KMA_API_KEY = "6e5230b95ef0ab65ad4fb63e83f1b512f525f5a708933928098464ffa47da789"

def get_weather_forecast(target_date):
    """기상청 단기예보 API를 호출하여 특정 날짜의 날씨 예보를 가져오는 함수"""
    
    base_date = (target_date - timedelta(days=1)).strftime('%Y%m%d')
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        'serviceKey': KMA_API_KEY,
        'pageNo': '1',
        'numOfRows': '1000',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': '2300',
        'nx': '60',   # 의왕시 내손동 X 좌표
        'ny': '122'  # 의왕시 내손동 Y 좌표
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status() # HTTP 오류가 있으면 예외 발생
        weather_data = response.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
    except requests.exceptions.RequestException as e:
        print(f"API 호출 오류: {e}")
        return None

    forecast = {}
    if not weather_data: return None

    for item in weather_data:
        if item['fcstDate'] != target_date.strftime('%Y%m%d'): continue
        hour = int(item['fcstTime'][:2])
        if hour not in forecast:
            forecast[hour] = {'기온': 0, '강수량': 0, '습도': 0, '적설': 0}
        category, value = item['category'], item['fcstValue']
        if category == 'TMP': forecast[hour]['기온'] = float(value)
        elif category == 'PCP':
            try:
                if 'mm' in value: value = value.replace('mm', '')
                forecast[hour]['강수량'] = float(value)
            except (ValueError, TypeError): forecast[hour]['강수량'] = 0.0
        elif category == 'REH': forecast[hour]['습도'] = float(value)
        elif category == 'SNO':
            try:
                if 'cm' in value: value = value.replace('cm', '')
                forecast[hour]['적설'] = float(value)
            except (ValueError, TypeError): forecast[hour]['적설'] = 0.0
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

