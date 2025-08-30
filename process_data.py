import pandas as pd

file_name = 'records.xlsx'

# 엑셀 파일을 열어서 건너뛸 행 수를 확인하고 이 숫자를 수정해주세요.
# 만약 제목 행이 2번째 줄에 있다면 rows_to_skip = 1 입니다.
rows_to_skip = 1 

xls = pd.ExcelFile(file_name)
sheet_names = xls.sheet_names
all_sheets = []

print("모든 시트의 데이터를 정리하며 불러옵니다...")
for sheet in sheet_names:
    df_sheet = pd.read_excel(file_name, sheet_name=sheet, skiprows=rows_to_skip)
    all_sheets.append(df_sheet)

df = pd.concat(all_sheets, ignore_index=True)

print("\n데이터 정리 및 합치기 성공!")
print("--- 정리된 데이터 상위 5줄 ---")
print(df.head())
# --- LV 3-1: 여기서부터 새로운 코드입니다. ---

print("\n--- 시간 데이터 변환 및 특성 생성 ---")

# '입장시간' 컬럼을 컴퓨터가 이해하는 시간 형태로 변환합니다.
# 만약 에러가 발생하면, errors='coerce' 옵션이 잘못된 형식을 NaN으로 만듭니다.
df['입장시간'] = pd.to_datetime(df['입장시간'], errors='coerce')

# 변환된 '입장시간'에서 새로운 시간 특성을 추출합니다.
df['년'] = df['입장시간'].dt.year
df['월'] = df['입장시간'].dt.month
df['일'] = df['입장시간'].dt.day
df['요일'] = df['입장시간'].dt.dayofweek  # 월요일=0, 일요일=6
df['시간'] = df['입장시간'].dt.hour

# 비어있는 시간 데이터(NaN)가 얼마나 있는지 확인합니다.
print("시간 변환 후 비어있는 데이터 개수:", df['입장시간'].isnull().sum())

# 새로 만들어진 컬럼들을 확인합니다.
print("\n--- 시간 특성이 추가된 데이터 ---")
print(df[['입장시간', '년', '월', '일', '요일', '시간']].head())

# --- LV 3-2: 여기서부터 새로운 코드입니다. ---

print("\n--- 일별/시간별 이용객 수 집계 ---")

# '입장시간'이 비어있는 데이터는 분석에서 제외합니다.
df_cleaned = df.dropna(subset=['입장시간'])

# '년', '월', '일', '시간'을 기준으로 그룹을 만들고, 각 그룹의 데이터 수를 셉니다.
# 이것이 바로 해당 시간의 이용객 수가 됩니다.
hourly_users = df_cleaned.groupby(['년', '월', '일', '시간']).size().reset_index(name='이용객수')

print(hourly_users.head())