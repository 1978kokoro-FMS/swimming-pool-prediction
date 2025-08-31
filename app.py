import requests
from flask import Flask, render_template, jsonify, request
from predict import predict_visitors
from datetime import datetime, timedelta

app = Flask(__name__)
KMA_API_KEY = "여기에_본인의_인증키를_붙여넣으세요"

def get_weather_forecast(target_date):
    """기상청 단기예보 API를 호출하여 특정 날짜의 날씨 예보를 가져오는 함수"""
    base_date = (target_date - timedelta(days=1)).strftime('%Y%m%d')
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        'serviceKey': KMA_API_KEY, 'pageNo': '1', 'numOfRows': '1000',
        'dataType': 'JSON', 'base_date': base_date, 'base_time': '2300',
        'nx': '60', 'ny': '122'
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        weather_data = response.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
    except requests.exceptions.RequestException as e:
        print(f"API 호출 오류: {e}")
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

@app.route('/analysis')
def analysis():
    """분석 정보 페이지를 렌더링합니다."""
    return render_template('analysis.html')

@app.route('/predict')
def predict():
    """날짜를 받아 예측을 수행하고 결과를 반환합니다."""
    try:
        date_str = request.args.get('date')
        target_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now() + timedelta(days=1)
        today = datetime.now()
        date_difference = (target_date.replace(hour=0) - today.replace(hour=0)).days

        if date_difference < 0:
            return jsonify({
                'error': '지난 날짜',
                'message': f'{target_date.strftime("%Y-%m-%d")}는 지난 날짜이므로 예측 대상이 아닙니다.'
            }), 400
        
        weather_forecast = None
        weather_source = ""
        if 0 <= date_difference <= 2:
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
    app.run(debug=True)
```eof
## 2단계: 프론트엔드 추가 (`analysis.html` & `index.html`)

사용자가 볼 **'분석 정보' 페이지**를 새로 만들고, 기존 **메인 페이지**는 지난 날짜를 처리하도록 수정합니다.

### **2-1. `analysis.html` 파일 생성**
`templates` 폴더 안에 **`analysis.html`**이라는 새 파일을 만들고 아래 코드를 붙여넣으세요.

```html:Analysis Information Page:templates/analysis.html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>AI 예측 모델 분석 정보</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px; color: #333; }
        h1, h2 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .info-section { margin-bottom: 30px; text-align: left; }
        .info-section p { line-height: 1.6; }
        .back-link { display: inline-block; margin-top: 20px; padding: 10px 15px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>AI 예측 모델 분석 정보</h1>

    <div class="info-section">
        <h2>AI 모델이 고려하는 주요 요소</h2>
        <p>본 AI 예측 모델은 단순히 과거 이용객 수만 보는 것이 아니라, 다음과 같은 복합적인 요소들의 상호작용과 패턴을 학습하여 미래 이용객 수를 예측합니다.</p>
        <ul>
            <li><strong>시간적 요소:</strong> 특정 시간대(오전/오후), 요일(주중/주말), 월별/계절별 주기성 등 시간의 흐름에 따른 패턴을 분석합니다.</li>
            <li><strong>기상 요소:</strong> 기온, 강수량, 습도, 적설량 등 날씨 변화가 이용객 수에 미치는 영향을 분석합니다. 예를 들어, 너무 덥거나 비가 많이 오는 날의 이용객 변화 패턴을 학습합니다.</li>
            <li><strong>복합 요소:</strong> '주말이지만 비가 오는 날', '평일 저녁이지만 유난히 더운 날'처럼 여러 요소가 결합했을 때 나타나는 특별한 패턴을 통계적으로 분석하여 예측에 반영합니다.</li>
        </ul>
    </div>

    <div class="info-section">
        <h2>모델 성능 및 오차 범위</h2>
        <p>
            현재 운영 중인 모델은 과거 3년간의 데이터를 학습한 결과, 다음과 같은 평균 오차 범위를 가집니다. 이는 예측값이 실제값과 평균적으로 어느 정도 차이가 나는지를 의미합니다.
        </p>
        <ul>
            <li><strong>남자 이용객 모델:</strong> 평균 오차 약 ±3명</li>
            <li><strong>여자 이용객 모델:</strong> 평균 오차 약 ±5명</li>
        </ul>
        <p>
            이 오차는 지속적인 데이터 축적과 모델 개선을 통해 점차 줄여나갈 수 있습니다.
        </p>
    </div>

    <a href="/" class="back-link">예측 페이지로 돌아가기</a>
</body>
</html>
```eof
### **2-2. `index.html` 파일 수정**
기존 `index.html` 파일을 열고, **`<head>` 태그 안쪽**과 **자바스크립트의 `getPrediction` 함수** 부분을 아래와 같이 수정 및 추가해주세요.

```html:AI Prediction Webpage:templates/index.html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>수영장 이용객 예측</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* ... 이전 스타일 코드는 그대로 ... */
        /* 분석 정보 페이지로 가는 링크 스타일 추가 */
        .analysis-link { font-size: 14px; margin-top: 15px; }
    </style>
</head>
<body>
    <h1>AI 수영장 이용객 예측</h1>
    
    <div class="controls">
        <label for="predict-date">예측할 날짜 선택:</label>
        <input type="date" id="predict-date">
        <button onclick="getPrediction()">그래프로 예측 보기!</button>
    </div>
    
    <p class="analysis-link"><a href="/analysis">AI 예측 모델 분석 정보 자세히 보기</a></p>

    <script>
        // ... (이전 스크립트 코드는 그대로) ...

        function getPrediction() {
            const selectedDate = document.getElementById('predict-date').value;
            // ... (이전 코드는 그대로) ...

            fetch(`/predict?date=${selectedDate}`)
                .then(response => response.json().then(data => ({ status: response.status, body: data })))
                .then(({ status, body }) => {
                    // ★★★ 여기가 핵심 수정 부분입니다 ★★★
                    if (status !== 200) { // HTTP 상태 코드가 200(성공)이 아닐 때
                        // 지난 날짜 오류 또는 기타 서버 오류 처리
                        chartContainer.innerHTML = `<p style="color: red;">${body.message || body.error}</p>`;
                        weatherDiv.style.display = 'none';
                        explanationBox.style.display = 'none';
                        return;
                    }

                    const predictions = body.predictions;
                    const weather_source_text = body.weather_source;
                    // ... (이후 차트 그리기 및 정보 표시는 이전 코드와 동일) ...
                })
                .catch(err => {
                    // ... (이전 코드는 그대로) ...
                });
        }
    </script>
</body>
</html>
```eof
## 3단계: 실행 및 확인

1.  **로컬 PC에서 수정한 `app.py`, `index.html`, `analysis.html` 파일을 모두 서버에 업로드**합니다. (gcloud scp 명령어 사용)
2.  서버 터미널에서 **서버를 재시작**합니다. (`pkill gunicorn` 후 다시 실행)

이제 웹페이지에 접속하면 다음과 같은 기능이 추가된 것을 확인할 수 있습니다.
* **지난 날짜를 선택**하고 예측 버튼을 누르면 "예측 대상이 아닙니다"라는 메시지가 나타납니다.
* 그래프 예측 버튼 아래에 **"AI 예측 모델 분석 정보 자세히 보기"** 링크가 생기고, 클릭하면 AI가 고려하는 요소와 오차 범위가 정리된 새 페이지로 이동합니다.
