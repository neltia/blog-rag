import os
import yaml
import shutil
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class BlogRAGService:
    def __init__(self):
        # 프로젝트 루트 경로 (serving 폴더의 상위 폴더)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 마크다운 파일 경로: data/blog_posts
        self.data_dir = os.path.join(self.base_dir, "data", "blog_posts")

        # 벡터 DB 저장 경로: data/chroma_db
        self.db_dir = os.path.join(self.base_dir, "data", "chroma_db")

        self.prompt_path = os.path.join(self.base_dir, "prompts", "rag_prompts.yaml")

        # 모델 초기화
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0)
        self.vector_store = None

    def _load_prompt(self):
        with open(self.prompt_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def index_data(self, force_refresh=False):
        """
        data/blog_posts 의 파일들을 읽어 data/chroma_db 에 저장
        """
        # DB 초기화 옵션
        if force_refresh and os.path.exists(self.db_dir):
            shutil.rmtree(self.db_dir)
            print(f"[*] 기존 DB 삭제 완료: {self.db_dir}")

        # 데이터 폴더 확인
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"[*] 데이터 폴더가 없어 생성했습니다: {self.data_dir}")
            return

        print(f"[*] 데이터 로딩 중... ({self.data_dir})")
        loader = DirectoryLoader(self.data_dir, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
        docs = loader.load()

        if not docs:
            print("[*] 인덱싱할 문서가 없습니다.")
            return

        print(f"[*] 문서 분할 중... (총 {len(docs)}개 파일)")
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = splitter.split_documents(docs)

        print(f"[*] 벡터 저장소 생성 및 저장 중... ({self.db_dir})")
        self.vector_store = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.db_dir
        )
        print("[*] 인덱싱 완료!")

    def get_retriever(self):
        """벡터 DB 로드 및 Retriever 반환"""
        if not self.vector_store:
            # DB 폴더가 실제로 있는지 확인
            if not os.path.exists(self.db_dir) or not os.listdir(self.db_dir):
                print("[*] 벡터 DB가 비어있습니다. 인덱싱을 먼저 진행해주세요.")
                return None

            self.vector_store = Chroma(persist_directory=self.db_dir, embedding_function=self.embeddings)

        return self.vector_store.as_retriever(search_kwargs={"k": 4})

    def query(self, question: str):
        retriever = self.get_retriever()
        if not retriever:
            return "시스템 준비가 되지 않았습니다 (DB 없음). 관리자에게 인덱싱을 요청하세요."

        prompts = self._load_prompt()
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompts['default_rag']['system']),
            ("human", prompts['default_rag']['user'])
        ])

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return chain.invoke(question)


rag_service = BlogRAGService()
