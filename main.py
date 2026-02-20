import subprocess
import sys

# 실행할 스크립트들을 순서대로 리스트업
pipeline_steps = [
    "src/01_extract_dms.py",
    "src/02_data_preprocessing.py",
    "src/03_calc_stock_return.py",
    "src/04_merge_datasets.py",
    # "src/check_outliers.py", # 필요할 때만 주석 해제
    "src/05_visualize_trends.py",
    "src/06_analyze_correlation.py"
]

print("🚀 [StockNMIXX] 데이터 파이프라인 실행을 시작합니다...\n")

for step in pipeline_steps:
    print(f"▶️ 실행 중: {step}")
    try:
        # python3 명령어로 해당 스크립트 실행
        subprocess.run(["python3", step], check=True)
        print(f"✅ 완료: {step}\n")
    except subprocess.CalledProcessError:
        print(f"❌ 에러 발생: {step} 실행 중 문제가 발생하여 파이프라인을 중단합니다.")
        sys.exit(1)

print("🎉 모든 파이프라인이 성공적으로 완료되었습니다!")