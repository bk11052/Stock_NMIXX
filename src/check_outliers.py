import pandas as pd

# 데이터 불러오기
df = pd.read_csv("data/final_analysis_data.csv")

# 수익률이 30% (0.3) 이상이거나, 100% (1.0) 이상인 미친(?) 날짜만 필터링
# (그래프 Y축이 % 단위로 140인지, 소수점으로 1.4인지에 따라 숫자가 다를 수 있어 넉넉하게 잡습니다)
abnormal_returns = df[df['daily_return_lag1'] > 0.1]

# 날짜, 포트폴리오 가치, 전날 수익률만 뽑아서 출력
print("=== 🚨 비정상적인 폭등(스파이크) 날짜 추적 ===")
print(abnormal_returns[['DATE', 'portfolio_value', 'daily_return_lag1']].sort_values(by='daily_return_lag1', ascending=False))