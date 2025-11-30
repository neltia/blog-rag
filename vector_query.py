import os
from dotenv import load_dotenv
from serving.rag_service import BlogRAGService

# .env 로드
load_dotenv()


def main():
    if not os.getenv("GROQ_API_KEY"):
        print("[*] 환경변수 오류: GROQ_API_KEY가 설정되지 않았습니다.")
        return

    # 서비스 인스턴스 생성 (이때 경로들이 자동 설정됨)
    rag = BlogRAGService()

    print("\n" + "=" * 40)
    print("[*]  RAG Test CLI")
    print(f"[*]  Blog Data Dir : {rag.data_dir}")
    print(f"[*]  Vector DB Dir : {rag.db_dir}")
    print("=" * 40 + "\n")

    # 1. 인덱싱 여부 확인
    print("새로운 데이터를 인덱싱 하시겠습니까?")
    print("('y' 입력 시 기존 DB 삭제 후 재생성, 엔터 누르면 건너뜀)")
    choice = input("> ").strip().lower()

    if choice == 'y':
        # 수정된 경로(data/chroma_db)에 DB 생성됨
        rag.index_data(force_refresh=True)
    else:
        print("[*] 인덱싱 건너뜀.")

    # 2. 질의 루프
    print("\n[*] 질문을 입력하세요 (exit/q 로 종료)")
    while True:
        try:
            q = input("\nQ: ").strip()
            if q.lower() in ('exit', 'q'):
                break
            if not q:
                continue

            # DB 조회 및 답변 생성
            answer = rag.query(q)
            print(f"\nA: {answer}")
            print("-" * 20)

        except Exception as e:
            print(f"[*] Error: {e}")


if __name__ == "__main__":
    main()
