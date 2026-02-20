import json
import pandas as pd
import glob
import os

# 1. 인스타그램 특유의 한글 깨짐 현상 복원 함수
def fix_text(text):
    if not isinstance(text, str):
        return ""
    try:
        return text.encode('latin1').decode('utf-8')
    except:
        return text

# 2. 엔믹스 관련 키워드 및 계정 목록 설정
NMIXX_KEYWORDS = ["엔믹스", "앤믹스", "nmixx", "해원", "설윤", "윤아", "릴리", "배이", "지우", "규진", 
                  "haewon", "sullyoon", "lily", "baey", "jiwoo", "kyujin", 
                  "오해원", "설윤아", "릴리", "배진솔", "지우", "장규진",
                  "bluevalentine", "blue_valentine"]

def is_nmixx_content(text, owner):
    text = str(text).lower()
    owner = str(owner).lower()
    
    # 텍스트나 원본 계정 이름에 키워드가 하나라도 포함되면 True 반환 (대소문자 무시)
    for keyword in NMIXX_KEYWORDS:
        keyword_lower = keyword.lower() # 키워드도 소문자로 강제 변환

        if keyword_lower in text or keyword_lower in owner:
            return True
    return False

# 3. 데이터 추출 및 데이터프레임 생성
def process_instagram_dms(data_dir="data"):
    all_messages = []
    
    # data 폴더 안의 모든 message_*.json 파일 읽기
    json_files = glob.glob(os.path.join(data_dir, "message_*.json"))
    
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            for msg in data.get("messages", []):
                sender = fix_text(msg.get("sender_name"))
                timestamp_ms = msg.get("timestamp_ms")
                content = fix_text(msg.get("content"))
                
                # 공유된 콘텐츠 정보 추출
                share_info = msg.get("share", {})
                share_text = fix_text(share_info.get("share_text", ""))
                content_owner = fix_text(share_info.get("original_content_owner", ""))
                
                all_messages.append({
                    "sender": sender,
                    "timestamp_ms": timestamp_ms,
                    "content": content,
                    "share_text": share_text,
                    "content_owner": content_owner
                })
                
    df = pd.DataFrame(all_messages)
    
    # 4. 시간 데이터 변환 (밀리초 -> 한국시간 기준 날짜)
    df['datetime'] = pd.to_datetime(df['timestamp_ms'], unit='ms')
    # UTC에서 한국 시간(KST)으로 변환하려면 9시간 더해
    df['datetime'] = df['datetime'] + pd.Timedelta(hours=9)
    df['DATE'] = df['datetime'].dt.strftime('%Y-%m-%d')
    
    # 5. 양경훈이 보낸 메시지 중, 엔믹스 관련 메시지만 필터링
    df_kyunghoon = df[df['sender'] == "양경훈"].copy()
    
    # 엔믹스 판독기 적용 (직접 쓴 텍스트, 공유한 글, 원본 계정명 모두 검사)
    df_kyunghoon['is_nmixx'] = df_kyunghoon.apply(
        lambda row: is_nmixx_content(row['content'] + " " + row['share_text'], row['content_owner']), 
        axis=1
    )
    
    df_nmixx_only = df_kyunghoon[df_kyunghoon['is_nmixx'] == True]
    
    # 6. 날짜별 엔믹스 DM 전송 횟수 집계
    daily_nmixx_count = df_nmixx_only.groupby('DATE').size().reset_index(name='nmixx_dm_count')
    
    return daily_nmixx_count

# 실행 및 저장
if __name__ == "__main__":
    result_df = process_instagram_dms("data")
    print("=== 양경훈의 날짜별 엔믹스 DM 전송 횟수 ===")
    print(result_df.head(10))
    
    # 집계 결과를 새로운 CSV로 저장
    result_df.to_csv("data/nmixx_dm_daily.csv", index=False)
    print("\n✅ data/nmixx_dm_daily.csv 로 저장 완료!")