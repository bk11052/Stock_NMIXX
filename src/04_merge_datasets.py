import pandas as pd

# 1. 데이터 불러오기
# (경로는 실제 파일이 있는 위치에 맞게 수정해주세요)
portfolio_df = pd.read_csv("data/portfolio_with_price.csv")
dm_df = pd.read_csv("data/nmixx_dm_daily.csv")

# DATE 컬럼을 날짜 타입으로 확실하게 변환
portfolio_df['DATE'] = pd.to_datetime(portfolio_df['DATE'])
dm_df['DATE'] = pd.to_datetime(dm_df['DATE'])

# 2. 주식 포트폴리오 데이터를 기준으로 DM 데이터 병합 (Left Join)
# 이렇게 하면 주식 데이터의 날짜(주말 포함)를 뼈대로 삼고 DM 횟수가 갖다 붙습니다.
merged_df = pd.merge(portfolio_df, dm_df, on='DATE', how='left')

# DM을 한 번도 안 보낸 날은 NaN으로 뜨므로 0으로 채워줍니다.
merged_df['nmixx_dm_count'] = merged_df['nmixx_dm_count'].fillna(0).astype(int)

# 3. (핵심) 전날 주가 등락률 컬럼 추가 (Lag 1)
# '오늘 DM 횟수'와 '어제 밤 미국장 수익률'을 비교하기 위함입니다.
# 만약 daily_return 컬럼이 있다면 이를 1칸 밑으로 밀어줍니다.
if 'daily_return' in merged_df.columns:
    merged_df['daily_return_lag1'] = merged_df['daily_return'].shift(1)

# 4. 최종 데이터 확인 및 저장
print("=== 최종 병합 데이터 미리보기 ===")
# 주요 컬럼만 뽑아서 확인해봅니다
display_cols = ['DATE', 'portfolio_value', 'daily_return', 'daily_return_lag1', 'nmixx_dm_count']
# 있는 컬럼만 필터링해서 출력
display_cols = [col for col in display_cols if col in merged_df.columns]
print(merged_df[display_cols].head(10))

merged_df.to_csv("data/final_analysis_data.csv", index=False)
print("\n✅ data/final_analysis_data.csv 로 분석용 최종 데이터 저장 완료!")