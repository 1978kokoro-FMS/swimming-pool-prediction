#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
기상청 단기예보 API 테스트 스크립트
"""

import requests
from datetime import datetime, timedelta

# API 키 (app.py와 동일)
KMA_API_KEY = "94057a00005793242a78b4e2274cef1b9da37a65d7acd6598f852bced75ddb6d"

def test_weather_api():
    """기상청 API 호출 테스트"""
    
    print("=" * 60)
    print("기상청 단기예보 API 테스트")
    print("=" * 60)
    
    # 오늘 날짜 기준으로 테스트
    target_date = datetime.now()
    
    # base_date와 base_time 계산 (현재 시각 기준)
    now = datetime.now()
    
    # 단기예보는 02, 05, 08, 11, 14, 17, 20, 23시에 발표
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
    
    print(f"\n📅 테스트 날짜: {target_date.strftime('%Y년 %m월 %d일')}")
    print(f"📅 Base Date: {base_date}")
    print(f"🕐 Base Time: {base_time}")
    print(f"📍 좌표: nx=60, ny=122 (의왕)")
    
    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        'serviceKey': KMA_API_KEY,
        'pageNo': '1',
        'numOfRows': '1000',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': '60',
        'ny': '122'
    }
    
    print(f"\n🔗 API URL: {url}")
    print(f"📋 Parameters:")
    for key, value in params.items():
        if key == 'serviceKey':
            print(f"   {key}: {value[:20]}...{value[-20:]}")
        else:
            print(f"   {key}: {value}")
    
    print("\n⏳ API 호출 중...")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        print(f"\n📡 HTTP 상태 코드: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ API 호출 실패: HTTP {response.status_code}")
            print(f"응답 내용:\n{response.text[:500]}")
            return
        
        data = response.json()
        
        # 응답 구조 확인
        header = data.get('response', {}).get('header', {})
        result_code = header.get('resultCode')
        result_msg = header.get('resultMsg')
        
        print(f"\n📊 API 응답:")
        print(f"   Result Code: {result_code}")
        print(f"   Result Message: {result_msg}")
        
        if result_code != '00':
            print(f"\n❌ API 에러 발생!")
            print(f"전체 응답 내용:")
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
            return
        
        # 데이터 개수 확인
        items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        
        if not items:
            print(f"\n❌ 반환된 데이터가 없습니다.")
            return
        
        print(f"\n✅ 성공! 총 {len(items)}개의 데이터 항목 반환됨")
        
        # 샘플 데이터 출력 (첫 5개)
        print(f"\n📋 샘플 데이터 (처음 5개):")
        for i, item in enumerate(items[:5]):
            print(f"   {i+1}. {item.get('fcstDate')} {item.get('fcstTime')} - {item.get('category')}: {item.get('fcstValue')}")
        
        # 오늘 데이터만 추출
        today_str = target_date.strftime('%Y%m%d')
        today_items = [item for item in items if item.get('fcstDate') == today_str]
        
        print(f"\n📅 오늘({today_str}) 예보 데이터: {len(today_items)}개")
        
        # 카테고리별 데이터 확인
        categories = {}
        for item in today_items:
            cat = item.get('category')
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        print(f"\n📊 카테고리별 데이터 개수:")
        for cat, count in sorted(categories.items()):
            print(f"   {cat}: {count}개")
        
        # 주요 카테고리 (TMP, REH, PCP, SNO) 확인
        required_cats = ['TMP', 'REH', 'PCP', 'SNO']
        missing_cats = [cat for cat in required_cats if cat not in categories]
        
        if missing_cats:
            print(f"\n⚠️  누락된 카테고리: {', '.join(missing_cats)}")
        else:
            print(f"\n✅ 모든 필수 카테고리 데이터 존재!")
        
    except requests.exceptions.Timeout:
        print("\n❌ API 호출 시간 초과 (30초)")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API 호출 오류: {e}")
    except ValueError as e:
        print(f"\n❌ JSON 파싱 오류: {e}")
    except Exception as e:
        print(f"\n❌ 알 수 없는 오류: {e}")
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)

if __name__ == '__main__':
    test_weather_api()
