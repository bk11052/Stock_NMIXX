import pandas as pd
import numpy as np

# CSV 불러오기
df = pd.read_csv("data/stock.csv")
print("데이터 로드 완료")

# NaN → 0 변환
df = df.fillna(0)

# DATE → datetime 변환 (현재는 문자열)
df["DATE"] = pd.to_datetime(df["DATE"], format="%Y.%m.%d")
df = df.sort_values("DATE")

# 수량을 정수로
qty_cols = df.columns.drop("DATE")
df[qty_cols] = df[qty_cols].astype(int)

# 일별 보유종목 개수 생성
df["holding_count"] = (df.drop(columns=["DATE"]) > 0).sum(axis=1)

# 일별 거래 발생 여부 변수 생성
df_diff = df.drop(columns=["DATE"]).diff().abs()
df["trade_count"] = (df_diff > 0).sum(axis=1)

print(df.head())

df.to_csv("data/stock_cleaned.csv", index=False)
print("전처리 완료 및 저장 완료")