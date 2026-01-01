# 🔍 기상청 API 문제 해결 체크리스트

## ✅ 즉시 확인 사항

### 1단계: 테스트 스크립트 실행
```bash
python test_weather_api.py
```

**기대 결과**:
- [ ] HTTP 상태 코드 200
- [ ] Result Code: 00
- [ ] 데이터 개수 > 0

---

### 2단계: API 키 유효성 확인

**현재 API 키**: 
```
6e5230b95ef0ab65ad4fb63e83f1b512f525f5a708933928098464ffa47da789
```

**확인 방법**:
- [ ] [공공데이터포털](https://www.data.go.kr) 로그인
- [ ] 마이페이지 > 활용신청 현황 확인
- [ ] 키 상태가 "정상"인지 확인

**키가 만료되었다면**:
1. 새 키 발급
2. `app.py`의 `KMA_API_KEY` 값 교체
3. `test_weather_api.py`의 `KMA_API_KEY` 값 교체

---

### 3단계: 수정 사항 적용 확인

**app.py 파일 확인**:
```python
# 이 코드가 있어야 함:
base_times = [2, 5, 8, 11, 14, 17, 20, 23]  # ✅ 리스트 형태
current_total_minutes = current_hour * 60 + current_minute  # ✅ 분 단위 계산
```

**만약 이전 코드라면**:
```python
# ❌ 이전 코드:
base_times = ['0200', '0500', '0800', ...]  # 문자열 형태
```
→ 제공된 수정 파일로 교체 필요

---

### 4단계: Flask 앱 실행 테스트
```bash
python app.py
```

**콘솔에서 확인**:
- [ ] `[DEBUG] 현재 시각: ...` 메시지 표시
- [ ] `[DEBUG] Base Date: ...` 메시지 표시
- [ ] 에러 메시지 없음

**브라우저에서 확인**:
- [ ] `http://127.0.0.1:5000` 접속 가능
- [ ] 예측 결과 정상 표시

---

## 🚨 여전히 문제가 있다면

### HTTP 상태 코드가 200이 아닌 경우
- **403 Forbidden**: API 키가 잘못되었거나 만료됨
- **500 Internal Server Error**: API 서버 문제 (잠시 후 재시도)
- **Timeout**: 네트워크 연결 확인

### Result Code가 '00'이 아닌 경우
- **01**: APPLICATION_ERROR
- **02**: DB_ERROR
- **03**: NODATA_ERROR (해당 시각에 데이터 없음)
- **04**: HTTP_ERROR
- **05**: SERVICETIMEOUT_ERROR
- **10**: INVALID_REQUEST_PARAMETER_ERROR
- **11**: NO_MANDATORY_REQUEST_PARAMETERS_ERROR
- **12**: NO_OPENAPI_SERVICE_ERROR
- **20**: SERVICE_ACCESS_DENIED_ERROR
- **22**: LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR
- **30**: SERVICE_KEY_IS_NOT_REGISTERED_ERROR
- **31**: DEADLINE_HAS_EXPIRED_ERROR
- **32**: UNREGISTERED_IP_ERROR
- **33**: UNSIGNED_CALL_ERROR
- **99**: UNKNOWN_ERROR

### 가장 흔한 에러 코드
- **30**: API 키가 등록되지 않음 → 새 키 발급
- **31**: API 키 사용 기한 만료 → 새 키 발급
- **03**: 데이터 없음 → base_time이 잘못 계산됨

---

## 💡 빠른 해결 팁

### 팁 1: 현재 시각 확인
```python
from datetime import datetime
print(datetime.now())
```

### 팁 2: base_time 계산 검증
현재 시각이 14:30이라면:
- current_total_minutes = 14 * 60 + 30 = 870
- 23:00 + 10분 = 1390분 → 870 < 1390 ❌
- 20:00 + 10분 = 1210분 → 870 < 1210 ❌
- 17:00 + 10분 = 1030분 → 870 < 1030 ❌
- 14:00 + 10분 = 850분 → 870 >= 850 ✅
- **결과**: base_time = '1400' ✅

### 팁 3: 수동 API 호출 테스트
```python
import requests
url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
params = {
    'serviceKey': '여기에_API_키_입력',
    'pageNo': '1',
    'numOfRows': '10',
    'dataType': 'JSON',
    'base_date': '20260101',
    'base_time': '1400',
    'nx': '60',
    'ny': '122'
}
response = requests.get(url, params=params)
print(response.json())
```

---

## 📞 추가 지원

문제가 지속되면 다음 정보와 함께 문의하세요:

1. 콘솔 에러 메시지 전체
2. `test_weather_api.py` 실행 결과
3. 현재 시각
4. API 키 상태 (활성/만료)

---

**작성일**: 2026-01-01  
**버전**: 1.0
