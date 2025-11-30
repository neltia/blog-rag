import argparse
import uvicorn
import os
from dotenv import load_dotenv
# .env 로드
load_dotenv()

# FastAPI 관련 임포트
from fastapi import FastAPI
from serving.api_router import router

# Gradio 관련 임포트
import gradio as gr
from serving.gradio_app import create_ui


def start_api_only(host, port):
    print(f"[*] Starting API Mode on {host}:{port}")
    app = FastAPI(title="Blog RAG API")
    app.include_router(router, prefix="/api/v1", tags=["RAG"])

    uvicorn.run(app, host=host, port=port)


def start_ui_only(host, port, share):
    print(f"[*] Starting UI Mode on {host}:{port}")
    demo = create_ui()
    # Gradio 자체 서버 실행
    demo.launch(server_name=host, server_port=port, share=share)


def start_all(host, port, share):
    print(f"[*] Starting Hybrid Mode (API + UI) on {host}:{port}")

    # 1. FastAPI 앱 생성
    app = FastAPI(title="Blog RAG Hybrid Service")

    # 2. API 라우터 등록
    app.include_router(router, prefix="/api/v1", tags=["RAG"])

    # 3. Gradio 마운트 (/ui 경로)
    demo = create_ui()
    app = gr.mount_gradio_app(app, demo, path="/ui")

    print(f"[*] API Docs: http://{host}:{port}/docs")
    print(f"[*] Gradio UI: http://{host}:{port}/ui")

    uvicorn.run(app, host=host, port=port)


def main():
    parser = argparse.ArgumentParser(description="Blog RAG Service Launcher")

    parser.add_argument(
        "--mode",
        type=str,
        default="all",
        choices=["api", "ui", "all"],
        help="실행 모드 선택: api (FastAPI만), ui (Gradio만), all (둘 다)"
    )
    parser.add_argument("--host", type=str, default="0.0.0.0", help="호스트 주소")
    parser.add_argument("--port", type=int, default=8000, help="포트 번호")
    parser.add_argument("--share", action="store_true", help="Gradio public link 공유 여부 (UI 모드일 때 유효)")

    args = parser.parse_args()

    if not os.getenv("GROQ_API_KEY"):
        print("[*] 경고: GROQ_API_KEY 환경변수가 설정되지 않았습니다.")

    if args.mode == "api":
        start_api_only(args.host, args.port)
    elif args.mode == "ui":
        start_ui_only(args.host, args.port, args.share)
    else:
        # Default: all
        start_all(args.host, args.port, args.share)


if __name__ == "__main__":
    main()
