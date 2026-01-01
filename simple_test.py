#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
최소한의 API 테스트 - 가장 단순한 형태
"""

import requests
from datetime import datetime, timedelta

# API 키
API_KEY = "94057a00005793242a78b4e2274cef1b9da37a65d7acd6598f852bced75ddb6d"

print("=" * 60)
print("최소 API 테스트")
print("=" * 60)

# 가장 간단한 파라미터로 테스트
now = datetime.now()

# 오늘 날짜와 02시 기준 (가장 안전한 시간)
base_date = now.strftime('%Y%m%d')
base_time = '0200'

print(f"\n테스트 파라미터:")
print(f"  base_date: {base_date}")
print(f"  base_time: {base_time}")
print(f"  nx: 60")
print(f"  ny: 122")

url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

params = {
    'serviceKey': API_KEY,
    'pageNo': '1',
    'numOfRows': '10',
    'dataType': 'JSON',
    'base_date': base_date,
    'base_time': base_time,
    'nx': '60',
    'ny': '122'
}

print(f"\n요청 URL: {url}")
print(f"\nAPI 호출 중...\n")

try:
    response = requests.get(url, params=params, timeout=30)
    
    print(f"HTTP 상태 코드: {response.status_code}")
    print(f"응답 크기: {len(response.text)} bytes\n")
    
    if response.status_code == 200:
        try:
            data = response.json()
            header = data.get('response', {}).get('header', {})
            
            result_code = header.get('resultCode')
            result_msg = header.get('resultMsg')
            
            print(f"Result Code: {result_code}")
            print(f"Result Message: {result_msg}\n")
            
            if result_code == '00':
                items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
                print(f"✅ 성공! 데이터 {len(items)}개 받음")
                
                if items:
                    print(f"\n첫 3개 데이터:")
                    for i, item in enumerate(items[:3], 1):
                        print(f"  {i}. {item.get('category')}: {item.get('fcstValue')}")
                
            else:
                print(f"❌ API 오류!")
                print(f"\n에러 코드 의미:")
                
                error_codes = {
                    '01': 'APPLICATION_ERROR',
                    '02': 'DB_ERROR', 
                    '03': 'NODATA_ERROR',
                    '04': 'HTTP_ERROR',
                    '05': 'SERVICETIMEOUT_ERROR',
                    '10': 'INVALID_REQUEST_PARAMETER_ERROR',
                    '11': 'NO_MANDATORY_REQUEST_PARAMETERS_ERROR',
                    '12': 'NO_OPENAPI_SERVICE_ERROR',
                    '20': 'SERVICE_ACCESS_DENIED_ERROR',
                    '22': 'LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR',
                    '30': 'SERVICE_KEY_IS_NOT_REGISTERED_ERROR ← API 키 문제!',
                    '31': 'DEADLINE_HAS_EXPIRED_ERROR ← API 키 만료!',
                    '32': 'UNREGISTERED_IP_ERROR',
                    '33': 'UNSIGNED_CALL_ERROR',
                    '99': 'UNKNOWN_ERROR'
                }
                
                meaning = error_codes.get(result_code, '알 수 없는 오류')
                print(f"  {result_code}: {meaning}")
                
                print(f"\n전체 응답:")
                import json
                print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
                
        except ValueError as e:
            print(f"❌ JSON 파싱 실패!")
            print(f"  오류: {e}")
            print(f"\n응답 내용 (처음 500자):")
            print(response.text[:500])
    else:
        print(f"❌ HTTP 오류!")
        print(f"\n응답 내용:")
        print(response.text[:500])
        
except requests.exceptions.Timeout:
    print(f"❌ 시간 초과 (30초)")
except requests.exceptions.ConnectionError:
    print(f"❌ 연결 실패 - 인터넷 연결 확인 필요")
except Exception as e:
    print(f"❌ 오류 발생: {e}")

print("\n" + "=" * 60)
print("테스트 완료")
print("=" * 60)

input("\nEnter를 눌러 종료...")
