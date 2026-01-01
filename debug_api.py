#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
기상청 API 상세 디버깅 스크립트
"""

import requests
from datetime import datetime, timedelta
import json

# API 키 (app.py와 동일)
KMA_API_KEY = "94057a00005793242a78b4e2274cef1b9da37a65d7acd6598f852bced75ddb6d"

def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_api_key_format():
    """API 키 형식 검증"""
    print_section("1. API 키 검증")
    
    print(f"API 키 길이: {len(KMA_API_KEY)}자")
    print(f"API 키 앞부분: {KMA_API_KEY[:30]}...")
    print(f"API 키 뒷부분: ...{KMA_API_KEY[-30:]}")
    
    if len(KMA_API_KEY) < 50:
        print("⚠️  경고: API 키가 너무 짧을 수 있습니다.")
    else:
        print("✅ API 키 길이 정상")
    
    # 공백이나 특수문자 체크
    if ' ' in KMA_API_KEY:
        print("❌ 오류: API 키에 공백이 포함되어 있습니다!")
    elif '\n' in KMA_API_KEY or '\r' in KMA_API_KEY:
        print("❌ 오류: API 키에 줄바꿈 문자가 포함되어 있습니다!")
    else:
        print("✅ API 키에 공백/줄바꿈 없음")

def check_network():
    """네트워크 연결 확인"""
    print_section("2. 네트워크 연결 확인")
    
    test_urls = [
        ("Google", "https://www.google.com"),
        ("공공데이터포털", "https://www.data.go.kr"),
        ("기상청 API", "http://apis.data.go.kr")
    ]
    
    for name, url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {name} 연결 성공 (HTTP {response.status_code})")
        except requests.exceptions.Timeout:
            print(f"❌ {name} 연결 시간 초과")
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} 연결 실패 (인터넷 연결 확인 필요)")
        except Exception as e:
            print(f"❌ {name} 오류: {e}")

def calculate_base_time():
    """Base date와 base time 계산"""
    print_section("3. Base Date/Time 계산")
    
    now = datetime.now()
    print(f"현재 시각: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    base_times = [2, 5, 8, 11, 14, 17, 20, 23]
    current_hour = now.hour
    current_minute = now.minute
    current_total_minutes = current_hour * 60 + current_minute
    
    print(f"현재 시각 (분 단위): {current_total_minutes}분")
    print(f"발표 시각: {base_times} (각 +10분 후 데이터 제공)")
    
    base_time = None
    base_date = now.strftime('%Y%m%d')
    
    print("\n계산 과정:")
    for bt_hour in reversed(base_times):
        bt_total_minutes = bt_hour * 60 + 10
        status = "✅" if current_total_minutes >= bt_total_minutes else "❌"
        print(f"  {status} {bt_hour:02d}:10 ({bt_total_minutes}분) vs 현재 ({current_total_minutes}분)")
        
        if current_total_minutes >= bt_total_minutes and base_time is None:
            base_time = f"{bt_hour:02d}00"
            print(f"    → 선택됨!")
    
    if base_time is None:
        base_date = (now - timedelta(days=1)).strftime('%Y%m%d')
        base_time = '2300'
        print(f"\n  모든 조건 불만족 → 전날 23시 데이터 사용")
    
    print(f"\n최종 결정:")
    print(f"  Base Date: {base_date}")
    print(f"  Base Time: {base_time}")
    
    return base_date, base_time

def test_api_call(base_date, base_time):
    """실제 API 호출 테스트"""
    print_section("4. API 호출 테스트")
    
    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        'serviceKey': KMA_API_KEY,
        'pageNo': '1',
        'numOfRows': '100',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': '60',
        'ny': '122'
    }
    
    print(f"요청 URL: {url}")
    print(f"\n파라미터:")
    for key, value in params.items():
        if key == 'serviceKey':
            print(f"  {key}: {value[:20]}...{value[-20:]}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n⏳ API 호출 중...")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        print(f"\n✅ HTTP 응답 받음")
        print(f"  상태 코드: {response.status_code}")
        print(f"  응답 크기: {len(response.text)} bytes")
        
        if response.status_code != 200:
            print(f"\n❌ HTTP 오류!")
            print(f"응답 내용:\n{response.text[:500]}")
            return None
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"\n❌ JSON 파싱 실패!")
            print(f"응답 내용:\n{response.text[:500]}")
            return None
        
        # 응답 구조 분석
        header = data.get('response', {}).get('header', {})
        result_code = header.get('resultCode')
        result_msg = header.get('resultMsg')
        
        print(f"\nAPI 응답:")
        print(f"  Result Code: {result_code}")
        print(f"  Result Message: {result_msg}")
        
        if result_code != '00':
            print(f"\n❌ API 오류 발생!")
            print(f"\n에러 코드 의미:")
            error_meanings = {
                '01': 'APPLICATION_ERROR',
                '02': 'DB_ERROR',
                '03': 'NODATA_ERROR (데이터 없음)',
                '04': 'HTTP_ERROR',
                '05': 'SERVICETIMEOUT_ERROR',
                '10': 'INVALID_REQUEST_PARAMETER_ERROR',
                '11': 'NO_MANDATORY_REQUEST_PARAMETERS_ERROR',
                '12': 'NO_OPENAPI_SERVICE_ERROR',
                '20': 'SERVICE_ACCESS_DENIED_ERROR',
                '22': 'LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR',
                '30': 'SERVICE_KEY_IS_NOT_REGISTERED_ERROR (API 키 미등록)',
                '31': 'DEADLINE_HAS_EXPIRED_ERROR (API 키 기한 만료)',
                '32': 'UNREGISTERED_IP_ERROR',
                '33': 'UNSIGNED_CALL_ERROR',
                '99': 'UNKNOWN_ERROR'
            }
            meaning = error_meanings.get(result_code, '알 수 없는 오류')
            print(f"  {result_code}: {meaning}")
            
            print(f"\n전체 응답:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return None
        
        # 데이터 개수 확인
        items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        
        if not items:
            print(f"\n❌ 반환된 데이터가 없습니다.")
            return None
        
        print(f"\n✅ 성공!")
        print(f"  총 데이터 개수: {len(items)}개")
        
        # 샘플 데이터 표시
        print(f"\n샘플 데이터 (처음 3개):")
        for i, item in enumerate(items[:3], 1):
            print(f"  {i}. {item.get('fcstDate')} {item.get('fcstTime')} - "
                  f"{item.get('category')}: {item.get('fcstValue')}")
        
        # 카테고리별 개수
        categories = {}
        for item in items:
            cat = item.get('category')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n카테고리별 데이터:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}개")
        
        return data
        
    except requests.exceptions.Timeout:
        print(f"\n❌ API 호출 시간 초과 (30초)")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 연결 오류: {e}")
        return None
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """메인 함수"""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  기상청 API 상세 디버깅 스크립트".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    # 1. API 키 검증
    check_api_key_format()
    
    # 2. 네트워크 확인
    check_network()
    
    # 3. Base date/time 계산
    base_date, base_time = calculate_base_time()
    
    # 4. API 호출 테스트
    result = test_api_call(base_date, base_time)
    
    # 최종 결과
    print_section("최종 결과")
    
    if result:
        print("✅ 모든 테스트 통과!")
        print("\nAPI가 정상적으로 작동하고 있습니다.")
        print("만약 Flask 앱에서 여전히 문제가 발생한다면,")
        print("app.py를 다시 시작해보세요.")
    else:
        print("❌ 테스트 실패!")
        print("\n가능한 해결 방법:")
        print("1. API 키 확인:")
        print("   - https://www.data.go.kr 접속")
        print("   - 마이페이지 > 활용신청 현황 확인")
        print("   - 만료되었다면 새 키 발급")
        print("")
        print("2. 새 API 키를 발급받았다면:")
        print("   python update_api_key.py 실행")
        print("")
        print("3. 네트워크 확인:")
        print("   - 방화벽 설정")
        print("   - 인터넷 연결 상태")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 치명적 오류: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")
    input("Enter 키를 눌러 종료...")
