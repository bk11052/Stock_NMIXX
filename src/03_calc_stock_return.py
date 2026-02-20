import pandas as pd
import yfinance as yf

# 기존 데이터 로드
df = pd.read_csv("data/stock_cleaned.csv")
df["DATE"] = pd.to_datetime(df["DATE"])

print("데이터 로드 완료")

# 수량 컬럼만 추출 (DATE, holding_count, trade_count 제외)
qty_cols = df.columns.drop(["DATE", "holding_count", "trade_count"])

# =============================
# 주가 다운로드
# =============================
tickers = qty_cols.tolist()

# 첫날이 주말 또는 공휴일 가능성
start_data = df["DATE"].min() - pd.Timedelta(days=7)
end_data = df["DATE"].max()

price_df = yf.download(
    tickers,
    start=start_data,
    end=end_data,
    progress=False
)["Close"]

# ---------------------------------
# 인덱스를 컬럼으로 변환
# ---------------------------------
price_df = price_df.reset_index()
price_df.rename(columns={"Date": "DATE"}, inplace=True)

# ---------------------------------
# 주말을 포함한 전체 날짜 범위 생성함
# ---------------------------------
full_dates = pd.DataFrame({
    "DATE": pd.date_range(start=start_data, end=end_data)
})

# ---------------------------------
# 전체 날짜 기준으로 데이터 확장
# ---------------------------------
price_df = pd.merge(full_dates, price_df, on="DATE", how="left")

# ---------------------------------
# 거래일이 아닌 날은 직전 종가로 채움
# ---------------------------------
price_cols = price_df.columns.drop("DATE")
price_df[price_cols] = price_df[price_cols].ffill()

# ---------------------------------
# 가격 컬럼에 "_price" 접미사 붙임
# ---------------------------------
price_df.rename(
    columns={col: col + "_price" for col in price_cols},
    inplace=True
)

print("========= price_df (주말 채움 완료) ==========")
print(price_df.head())

print("주가 다운로드 완료")


# =============================
# 데이터 병합함 (Merge)
# =============================
merged = pd.merge(df, price_df, on="DATE", how="left")

# 날짜 기준으로 정렬함
merged = merged.sort_values("DATE")

# 수량 컬럼의 NaN 값은 0으로 채움
merged[tickers] = merged[tickers].fillna(0)

# 가격 컬럼만 직전 값으로 채움 (ffill)
price_cols = [col for col in merged.columns if col.endswith("_price")]
merged[price_cols] = merged[price_cols].ffill()

print("주가 merge 완료")

# =============================
# 포트폴리오 가치 계산함
# =============================

# 성능 경고(PerformanceWarning) 방지를 위해 데이터프레임 복사본 생성함
merged = merged.copy()
portfolio_value = 0

for ticker in tickers:
    qty_col = ticker
    price_col = ticker + "_price"
    
    # 주가 누락(NaN)으로 인해 전체 합산이 NaN이 되는 것을 막기 위해 0으로 채워서 더함 (미상장 주식)
    portfolio_value += (merged[qty_col] * merged[price_col]).fillna(0)

merged["portfolio_value"] = portfolio_value

print("포트폴리오 가치 계산 완료")
print(merged[["DATE", "portfolio_value"]].head())

# =====================================
# 일일 수익률 계산
# =====================================
# 1. 어제 기준 총 포트폴리오 가치
merged["prev_portfolio_value"] = merged["portfolio_value"].shift(1)

# 2. 어제 보유했던 수량 그대로 오늘 주가를 반영했을 때의 '순수 포트폴리오 가치'
pure_today_value = 0
for ticker in tickers:
    qty_col = ticker
    price_col = ticker + "_price"
    
    # 어제 수량 * 오늘 주가
    prev_qty = merged[qty_col].shift(1).fillna(0)
    pure_today_value += (prev_qty * merged[price_col]).fillna(0)

merged["pure_today_value"] = pure_today_value

# 3. 진짜 일일 수익률 계산: (오늘 순수가치 - 어제 가치) / 어제 가치
# (분모가 0이 되어 무한대(inf)가 뜨는 것을 방지하기 위해 예외 처리)
merged["daily_return"] = (merged["pure_today_value"] - merged["prev_portfolio_value"]) / merged["prev_portfolio_value"].replace(0, pd.NA)

# 필요 없어진 계산용 임시 컬럼 삭제 (깔끔하게 유지)
merged.drop(columns=["prev_portfolio_value", "pure_today_value"], inplace=True)

print("✅ 진짜 수익률 계산 완료")
print(merged[["DATE", "portfolio_value", "daily_return"]].head(10))

# =====================================
# CSV 파일로 저장
# =====================================
merged.to_csv("data/portfolio_with_price.csv", index=False)

print("파일 저장 완료")
print('print(merged[["DATE", tickers[0], tickers[0] + "_price"]].head(10))')
print(merged[["DATE", tickers[0], tickers[0] + "_price"]].head(10))

print("어떤 종목이 NaN을 많이 가지고 있는지 확인")
print(merged[[col for col in merged.columns if col.endswith("_price")]].isna().sum().sort_values(ascending=False).head(10))