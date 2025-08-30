import pandas as pd

file_name = 'records.xlsx'

# 엑셀 파일 자체를 엽니다.
xls = pd.ExcelFile(file_name)

# 모든 시트의 이름을 가져옵니다. (['2206', '2207', '2208', ...])
sheet_names = xls.sheet_names

# 각 시트의 데이터를 임시로 저장할 리스트를 만듭니다.
all_sheets = []

# for문을 이용해 모든 시트를 하나씩 순서대로 읽습니다.
for sheet in sheet_names:
    print(f"{sheet} 시트를 읽는 중...")
    # 각 시트를 읽어서 all_sheets 리스트에 추가합니다.
    df_sheet = pd.read_excel(file_name, sheet_name=sheet)
    all_sheets.append(df_sheet)

# 읽어온 모든 시트 데이터를 위아래로 합쳐서 하나의 큰 데이터로 만듭니다.
df = pd.concat(all_sheets, ignore_index=True)

print("\n모든 시트 데이터 합치기 성공!")
print("--- 전체 데이터 상위 5줄 ---")
print(df.head())
print("\n--- 전체 데이터 하위 5줄 ---")
print(df.tail())