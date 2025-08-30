import pandas as pd
import joblib

# 1. 학습된 남/여 모델을 불러옵니다.
try:
    model_male = joblib.load('model_male.pkl')
    model_female = joblib.load('model_female.pkl')
    print("모델 로딩 성공!")
except FileNotFoundError:
    print("오류: 저장된 모델 파일(model_male.pkl, model_female.pkl)을 찾을 수 없습니다.")
    model_male, model_female = None, None

def predict_visitors(year, month, day, hour, day_of_week, temp, rain, humidity, snow):
    """
    미래 시간과 날씨 정보를 입력받아 남/여 이용객 수를 예측하는 함수
    """
    if model_male is None or model_female is None:
        return {'오류': '모델이 로드되지 않았습니다.'}

    # 2. AI 모델에 입력할 형식으로 데이터를 만듭니다.
    input_data = pd.DataFrame({
        '년': [year], '월': [month], '일': [day], '시간': [hour], '요일': [day_of_week],
        '기온': [temp], '강수량': [rain], '습도': [humidity], '적설': [snow]
    })

    # 3. 남/여 모델로 각각 예측을 수행합니다.
    pred_male = model_male.predict(input_data)[0]
    pred_female = model_female.predict(input_data)[0]

    # 4. 예측 결과를 반환합니다. (0보다 작은 값은 0으로 처리)
    return {
        '남자_예상': max(0, round(pred_male)), 
        '여자_예상': max(0, round(pred_female))
    }