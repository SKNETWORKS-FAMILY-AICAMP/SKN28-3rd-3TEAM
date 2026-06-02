# src/build_vector_db.py

import json
import os
from glob import glob
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

PROCESSED_DIR = Path("data/processed")
VECTORSTORE_DIR = Path("vectorstore/faiss_index")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_BATCH_SIZE = 100


def load_all_json_docs() -> list[Document]:
    docs: list[Document] = []

    for path in glob(str(PROCESSED_DIR / "*.json")):
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)

        for item in items:
            content = item.get("content", "").strip()
            if not content:
                continue

            metadata = {
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "url": item.get("url", ""),
                **item.get("metadata", {}),
            }

            docs.append(
                Document(
                    page_content=content,
                    metadata=metadata,
                )
            )

    return docs


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    return splitter.split_documents(documents)


def build_vector_db() -> None:
    os.makedirs(VECTORSTORE_DIR.parent, exist_ok=True)

    documents = load_all_json_docs()

    if not documents:
        raise ValueError(
            "data/processed 폴더에 문서가 없습니다. 먼저 collect_korea_drug.py를 실행하세요."
        )

    split_docs = split_documents(documents)

    print(f"원본 문서 수: {len(documents)}")
    print(f"분할된 chunk 수: {len(split_docs)}")

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        chunk_size=EMBEDDING_BATCH_SIZE,
    )

    vectorstore = FAISS.from_documents(
        documents=split_docs,
        embedding=embeddings,
    )

    vectorstore.save_local(str(VECTORSTORE_DIR))

    print(f"FAISS 저장 완료: {len(split_docs)}개 chunk")
    print(f"저장 위치: {VECTORSTORE_DIR}")


if __name__ == "__main__":
    build_vector_db()
