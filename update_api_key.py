"""
기상청 API 키 업데이트 도구
"""

import os
import re

def update_api_key():
    """app.py와 test_weather_api.py의 API 키를 업데이트합니다."""
    
    print("=" * 60)
    print("기상청 API 키 업데이트 도구")
    print("=" * 60)
    print()
    print("공공데이터포털(https://www.data.go.kr)에서")
    print("새 API 인증키를 발급받으셨나요?")
    print()
    
    new_key = input("새 API 키를 입력하세요: ").strip()
    
    if not new_key:
        print("\n❌ API 키가 입력되지 않았습니다.")
        return
    
    if len(new_key) < 50:
        print(f"\n⚠️  경고: API 키가 너무 짧습니다. (길이: {len(new_key)})")
        confirm = input("계속하시겠습니까? (y/n): ").strip().lower()
        if confirm != 'y':
            print("취소되었습니다.")
            return
    
    print(f"\n입력된 API 키: {new_key[:20]}...{new_key[-20:]}")
    confirm = input("\n이 API 키로 업데이트하시겠습니까? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("취소되었습니다.")
        return
    
    files_to_update = [
        'app.py',
        'test_weather_api.py',
        'debug_api.py'
    ]
    
    updated_count = 0
    
    for filename in files_to_update:
        if not os.path.exists(filename):
            print(f"\n⚠️  파일을 찾을 수 없습니다: {filename}")
            continue
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # API 키 패턴 찾기 및 교체
            pattern = r'KMA_API_KEY\s*=\s*["\']([^"\']+)["\']'
            
            if re.search(pattern, content):
                new_content = re.sub(
                    pattern,
                    f'KMA_API_KEY = "{new_key}"',
                    content
                )
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ {filename} 업데이트 완료")
                updated_count += 1
            else:
                print(f"⚠️  {filename}에서 API 키를 찾을 수 없습니다.")
        
        except Exception as e:
            print(f"❌ {filename} 업데이트 실패: {e}")
    
    print()
    print("=" * 60)
    if updated_count > 0:
        print(f"✅ {updated_count}개 파일이 업데이트되었습니다.")
        print()
        print("다음 단계:")
        print("1. Flask 앱이 실행 중이면 Ctrl+C로 종료하세요")
        print("2. 앱을 다시 실행하세요: python app.py")
        print("3. 브라우저를 새로고침하세요")
    else:
        print("❌ 업데이트된 파일이 없습니다.")
    print("=" * 60)

if __name__ == '__main__':
    try:
        update_api_key()
    except KeyboardInterrupt:
        print("\n\n취소되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    
    input("\nEnter 키를 눌러 종료...")
