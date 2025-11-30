import gradio as gr
from serving.rag_service import rag_service


def chat_fn(message, history):
    """채팅 핸들러"""
    try:
        return rag_service.query(message)
    except Exception as e:
        return f"[*] 오류 발생: {str(e)}"


def reindex_fn():
    try:
        rag_service.index_data(force_refresh=True)
        return "[*] 기존 데이터 기반 재인덱싱 완료!"
    except Exception as e:
        return f"[*] 인덱싱 실패: {str(e)}"


def create_ui():
    """Gradio Blocks 생성 함수"""
    with gr.Blocks(title="Blog RAG System", fill_height=True) as demo:
        gr.Markdown("## Naver Blog RAG System")
        gr.Markdown("블로그 게시글을 수집하고 질의응답을 수행합니다.")

        with gr.Tab("질문하기"):
            gr.ChatInterface(
                fn=chat_fn,
                examples=["최근 블로그 글 요약해줘", "이 블로그의 주요 주제는?"],
                title="Blog Chatbot",
                fill_height=True,
                fill_width=True
            )

        with gr.Tab("데이터 관리"):
            gr.Markdown("### 데이터 관리")

            # 재인덱싱 버튼
            reindex_btn = gr.Button("기존 파일 재인덱싱 (DB 초기화)", variant="secondary")
            output_log = gr.Textbox(label="실행 로그", interactive=False, lines=20)

            # 버튼 클릭 이벤트
            reindex_btn.click(fn=reindex_fn, inputs=[], outputs=[output_log])

    return demo
