import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 깨짐 방지 설정
import platform
if platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False 

def plot_trends():
    # 1. 데이터 불러오기
    df = pd.read_csv("data/final_analysis_data.csv")
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    # 2. 그래프 그리기 준비
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle('양경훈의 주식 수익률과 엔믹스 DM 전송량 비교', fontsize=16, fontweight='bold')

    # 3. 위쪽 그래프: 주식 수익률 선 그래프 (Seaborn 유지)
    sns.lineplot(data=df, x='DATE', y='daily_return_lag1', ax=ax1, color='crimson', marker='o', linewidth=2)
    ax1.axhline(0, color='black', linestyle='--', linewidth=1) 
    ax1.set_title('전날 주식 수익률 흐름 (Lag 1)', fontsize=12)
    ax1.set_ylabel('수익률')
    ax1.grid(True, alpha=0.3)

    # 4. 아래쪽 그래프: 엔믹스 DM 횟수 막대 그래프 (Matplotlib의 bar로 변경 ⭐️)
    ax2.bar(df['DATE'], df['nmixx_dm_count'], color='royalblue')
    ax2.set_title('당일 엔믹스(NMIXX) 관련 DM 전송 횟수', fontsize=12)
    ax2.set_ylabel('DM 전송 횟수')
    ax2.set_xlabel('날짜')
    ax2.grid(True, axis='y', alpha=0.3)

    # 5. X축 날짜 텍스트 겹치지 않게 포맷팅 (마법의 자동 정렬 함수)
    fig.autofmt_xdate()

    plt.tight_layout()
    
    # 그래프를 파일로 저장하고 화면에 띄우기
    plt.savefig('data/trend_visualization.png', dpi=300)
    print("✅ data/trend_visualization.png 로 그래프 이미지가 저장되었습니다!")
    plt.show()

if __name__ == "__main__":
    plot_trends()