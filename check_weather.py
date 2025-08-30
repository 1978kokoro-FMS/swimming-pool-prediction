import pandas as pd
import glob

print("--- 날씨 CSV 파일 내용 확인 ---")
try:
    # 폴더에 있는 날씨 파일 중 첫 번째 파일을 찾습니다.
    weather_file = glob.glob('weather*.csv')[0]
    print(f"'{weather_file}' 파일을 읽습니다.")

    # 파일에 맞게 skiprows 값을 1 또는 2로 설정하세요.
    df_weather = pd.read_csv(weather_file, encoding='cp949', skiprows=1)

    print("\n[파일 상위 5줄 미리보기]")
    print(df_weather.head())

    print("\n[실제 컬럼 이름 목록]")
    print(list(df_weather.columns))

except Exception as e:
    print(f"오류가 발생했습니다: {e}")