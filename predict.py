import pandas as pd
import joblib
import holidays
from datetime import date

# 1. 학습된 남/여 모델과 한국 공휴일 정보를 불러옵니다.
try:
    model_male = joblib.load('model_male.pkl')
    model_female = joblib.load('model_female.pkl')
    kr_holidays = holidays.KR()
    print("성공: 공휴일 예측 모델 로딩 완료.")
except FileNotFoundError:
    print("오류: 저장된 모델 파일(model_male.pkl, model_female.pkl)을 찾을 수 없습니다.")
    model_male, model_female = None, None

def predict_visitors(year, month, day, hour, day_of_week, temp, rain, humidity, snow, is_holiday):
    """
    미래 시간, 날씨, 공휴일 정보를 입력받아 남/여 이용객 수를 예측하는 함수
    """
    if model_male is None or model_female is None:
        return {'오류': '모델이 로드되지 않았습니다.'}
    
    # 2. AI 모델에 입력할 형식으로 데이터를 만듭니다. (is_holiday 추가)
    input_data = pd.DataFrame({
        '년': [year], '월': [month], '일': [day], '시간': [hour], '요일': [day_of_week],
        '기온': [temp], '강수량': [rain], '습도': [humidity], '적설': [snow],
        '공휴일': [is_holiday]
    })
    
    # 3. 남/여 모델로 각각 예측을 수행합니다.
    pred_male = model_male.predict(input_data)[0]
    pred_female = model_female.predict(input_data)[0]
    
    # 4. 예측 결과를 반환합니다.
    return {
        '남자_예상': max(0, round(pred_male)), 
        '여자_예상': max(0, round(pred_female))
    }

def is_holiday_check(target_date):
    """주어진 날짜가 공휴일인지 확인하는 함수"""
    return 1 if target_date in kr_holidays else 0

