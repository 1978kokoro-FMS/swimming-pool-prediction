import pandas as pd

# LV 1에서 성공했던 코드를 그대로 가져옵니다.
# '절대 경로' 부분은 본인의 파일 경로를 그대로 사용하세요.
file_name = r'C:\Users\Kokoro\Desktop\gym_analysis\records.xlsx'

xls = pd.ExcelFile(file_name)
sheet_names = xls.sheet_names
all_sheets = []

for sheet in sheet_names:
    df_sheet = pd.read_excel(file_name, sheet_name=sheet)
    all_sheets.append(df_sheet)

df = pd.concat(all_sheets, ignore_index=True)

# ----------------------------------------------------
# LV 2-1: 여기서부터 새로운 코드입니다.
# ----------------------------------------------------

print("--- 전체 데이터 기본 정보 ---")
# info()는 각 열에 데이터가 몇 개씩 들어있는지 보여줍니다.
# 전체 데이터 개수(RangeIndex)보다 Non-Null Count가 적으면 빈 값이 있다는 뜻입니다.
df.info()

print("\n--- 컬럼별 결측치(빈 값) 개수 ---")
# isnull().sum()은 각 열(컬럼)에 비어있는 칸이 몇 개인지 직접 세어줍니다.
print(df.isnull().sum())