import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
import platform

# 한글 폰트 및 마이너스 기호 깨짐 방지 설정
if platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

def run_analysis():
    # 1. 병합된 최종 데이터 불러오기 (수익률 계산이 완료된 데이터)
    df = pd.read_csv("data/final_analysis_data.csv")
    df['DATE'] = pd.to_datetime(df['DATE'])

    # NaN 값이 있으면 상관계수 계산 시 에러가 나므로 제외
    clean_df = df.dropna(subset=['daily_return', 'nmixx_dm_count']).copy()

    print("=== 📊 본격적인 상관관계 및 이벤트 분석 시작 ===\n")

    # -------------------------------------------------------------
    # [Part 0] 피어슨 상관계수 (선형 관계)
    # -------------------------------------------------------------
    pearson_corr, pearson_p = pearsonr(clean_df['daily_return'], clean_df['nmixx_dm_count'])
    print("[Part 0] 피어슨 상관계수 (기본 선형 검증)")
    print(f" - 상관계수(r): {pearson_corr:.3f}")
    print(f" - p-value: {pearson_p:.3f}")
    
    if pearson_p > 0.05:
        print(" 💡 해석: p-value가 0.05보다 커서 통계적으로 유의하지 않습니다.")
        print("    (원인 분석: DM 데이터의 80% 이상이 '0'인 극단적 비대칭성 때문에 선형 모델이 작동하지 않음)\n")
    else:
        print(" 💡 해석: 어? 피어슨으로도 유의미한 결과가 나왔습니다!\n")

    # -------------------------------------------------------------
    # [Part 1] 스피어만 상관계수 (순위 기반 검증)
    # -------------------------------------------------------------
    spearman_corr, spearman_p = spearmanr(clean_df['daily_return'], clean_df['nmixx_dm_count'])
    print("[Part 1] 스피어만 상관계수 (순위 기반 검증)")
    print(f" - 상관계수(rho): {spearman_corr:.3f}")
    print(f" - p-value: {spearman_p:.3f}")
    
    if spearman_p < 0.05:
        print(" 🎯 해석: [성공] p-value < 0.05 달성!")
        print("    주식 수익률이 낮을수록 엔믹스 DM을 많이 보내는 경향이 통계적으로 입증되었습니다.\n")
    else:
        print(" 💡 해석: 데이터 기간이나 모수가 부족하여 전체적인 통계적 유의성은 입증되지 않았습니다.\n")

    # -------------------------------------------------------------
    # [Part 2] 이벤트 분석 (Event Study) - 상승/하락 자유자재로 분석
    # -------------------------------------------------------------
    print("[Part 2] 행동 패턴 증명: 주가 이벤트 분석")
    baseline_dm = clean_df['nmixx_dm_count'].mean()
    print(f" - 평상시 1일 평균 DM 전송량: {baseline_dm:.2f}회\n")

    # 이벤트를 분석하고 그래프까지 그려주는 만능 함수
    def analyze_and_plot_event(threshold_val, condition_type, event_title, filename):
        if condition_type == "down":
            event_indices = clean_df[clean_df['daily_return'] <= threshold_val].index
        else: # "up"
            event_indices = clean_df[clean_df['daily_return'] >= threshold_val].index
            
        print(f"[{event_title}] 포착된 이벤트 횟수: {len(event_indices)}회")
        
        if len(event_indices) > 0:
            d_minus_1, d_day, d_plus_1, d_plus_2 = [], [], [], []
            
            # 각 이벤트 전후의 DM 횟수 수집
            for idx in event_indices:
                if idx - 1 in clean_df.index: d_minus_1.append(clean_df.loc[idx - 1, 'nmixx_dm_count'])
                d_day.append(clean_df.loc[idx, 'nmixx_dm_count'])
                if idx + 1 in clean_df.index: d_plus_1.append(clean_df.loc[idx + 1, 'nmixx_dm_count'])
                if idx + 2 in clean_df.index: d_plus_2.append(clean_df.loc[idx + 2, 'nmixx_dm_count'])
                
            avg_d_minus_1 = np.mean(d_minus_1) if d_minus_1 else 0
            avg_d_day = np.mean(d_day)
            avg_d_plus_1 = np.mean(d_plus_1) if d_plus_1 else 0
            avg_d_plus_2 = np.mean(d_plus_2) if d_plus_2 else 0
            
            multiplier = avg_d_plus_1 / baseline_dm if baseline_dm > 0 else 0
            print(f" 🎯 결론: {event_title} 다음 날(D+1), DM 전송량이 평소보다 평균 {multiplier:.1f}배입니다!\n")

            # === 시각화 (바 차트) ===
            labels = ['평상시\n(Baseline)', 'D-1\n(이벤트 전날)', 'D-Day\n(이벤트 당일)', 'D+1\n(다음날)', 'D+2\n(다다음날)']
            values = [baseline_dm, avg_d_minus_1, avg_d_day, avg_d_plus_1, avg_d_plus_2]
            
            # 폭락(down)은 빨간색 톤, 폭등(up)은 파란색 톤으로 그래프 색상 자동 변경
            colors = ['gray', 'lightcoral', 'firebrick', 'red', 'lightcoral'] if condition_type == "down" else ['gray', 'lightblue', 'royalblue', 'blue', 'lightblue']

            plt.figure(figsize=(10, 6))
            bars = plt.bar(labels, values, color=colors)
            
            # 평상시 기준선 그리기
            plt.axhline(baseline_dm, color='black', linestyle='--', label='평상시 평균 기준선')
            
            # 막대 위에 수치 텍스트 표시
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 2), ha='center', va='bottom', fontweight='bold')

            plt.title(f'{event_title} 전후 양경훈의 엔믹스 DM 전송량 변화', fontsize=16, fontweight='bold')
            plt.ylabel('평균 DM 전송 횟수')
            plt.legend()
            plt.tight_layout()
            
            plt.savefig(f'data/{filename}', dpi=300)
            print(f"✅ data/{filename} 로 그래프 저장 완료!\n")
            plt.show()
        else:
            print(" 💡 기간 내에 해당 조건을 만족하는 날이 없어서 그래프를 생략합니다.\n")

    # =========================================================
    # 🚀 여기서 원하는 이벤트를 마음대로 설정해서 실행하세요!
    # =========================================================
    
    # 1. 10% 이상 대폭락했을 때 (저장 파일명: event_down_10.png)
    analyze_and_plot_event(-0.10, "down", "주가 대폭락(-10% 이하)", "event_down_10.png")
    
    # 2. 10% 이상 대폭등했을 때 (저장 파일명: event_up_10.png)
    analyze_and_plot_event(0.10, "up", "주가 대폭등(+10% 이상)", "event_up_10.png")
    
    # (참고) 만약 -5% 하락도 보고 싶다면 아래 주석을 풀면 됩니다.
    # analyze_and_plot_event(-0.05, "down", "주가 하락(-5% 이하)", "event_down_5.png")

if __name__ == "__main__":
    run_analysis()