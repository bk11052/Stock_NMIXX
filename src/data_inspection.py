import pandas as pd
import numpy as np

# CSV 불러오기
df = pd.read_csv("data/stock.csv")
print("데이터 로드 완료")

# 상위 5개 확인
print("================== 상위 5개 확인 ==================")
print(df.head())

# 하위 5개 확인
print("================== 하위 5개 확인 ==================")
print(df.tail())

# shape 확인
print("================== shape 확인 ==================")
print("Shape:", df.shape)

# 컬럼 확인
print("================== 컬럼 확인 ==================")
print("Columns:", df.columns.tolist())

# 데이터 타입 확인
print("================== 데이터 타입 확인 ==================")
print(df.dtypes)

# 컬럼별 결측치 개수
print("================== 컬럼별 결측치 개수 ==================")
print(df.isnull().sum())

# 결측치 비율
print("================== 결측치 비율 ==================")
print((df.isnull().sum() / len(df)) * 100)

print("================== ==================")
print(df.describe())

