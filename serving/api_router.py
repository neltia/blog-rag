from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from serving.rag_service import rag_service

router = APIRouter()


# 요청 바디 모델 정의
class QueryRequest(BaseModel):
    query: str


class CrawlRequest(BaseModel):
    url: str


@router.post("/search")
async def search(request: QueryRequest):
    """
    RAG 검색 엔드포인트
    """
    try:
        print(f"[*] API 검색 요청 수신: {request.query}")
        answer = rag_service.query(request.query)
        return {"answer": answer}
    except Exception as e:
        print(f"[*] API 검색 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index")
async def index_docs():
    """
    강제 재인덱싱
    """
    try:
        print("[*] API 인덱싱 요청 수신")
        rag_service.index_data(force_refresh=True)
        return {"status": "success", "message": "[*] 전체 재인덱싱 완료"}
    except Exception as e:
        print(f"[*] API 인덱싱 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
