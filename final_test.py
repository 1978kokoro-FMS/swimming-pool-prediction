import pandas as pd

# 파이썬이 파일이 있다고 확인했으니, 이 파일 이름만으로 충분해야 합니다.
file_name = 'records.xlsx'

try:
    print(f"'{file_name}' 파일 읽기를 시도합니다...")

    # 가장 기본적인 방법으로 엑셀 파일의 첫 번째 시트만 읽어옵니다.
    df = pd.read_excel(file_name)

    print("\n파일 읽기 성공! 🎉")
    print("--- 데이터 미리보기 ---")
    print(df.head())

except Exception as e:
    print(f"\n오류가 발생했습니다!")
    print(f"오류 내용: {e}")