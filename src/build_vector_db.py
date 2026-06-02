# src/build_vector_db.py

import os
import json
from glob import glob
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


PROCESSED_DIR = "data/processed"
VECTORSTORE_DIR = "vectorstore/faiss_index"


def load_json_documents():
    docs = []

    json_files = glob(f"{PROCESSED_DIR}/*.json")

    print("읽을 JSON 파일 목록:")
    for file_path in json_files:
        print("-", file_path)

    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            items = json.load(f)

        if isinstance(items, dict):
            items = [items]

        for item in items:
            content = item.get("content", "")

            if not content:
                continue

            item_metadata = item.get("metadata", {})

            metadata = {
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "url": item.get("url", ""),
                **item_metadata
            }

            docs.append(
                Document(
                    page_content=content,
                    metadata=metadata
                )
            )

    return docs


def build_vector_db():
    documents = load_json_documents()

    print(f"로드된 원본 문서 수: {len(documents)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=100
    )

    split_docs = splitter.split_documents(documents)

    print(f"청크 분리 후 문서 수: {len(split_docs)}")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vectorstore = FAISS.from_documents(
        split_docs,
        embeddings
    )

    Path(VECTORSTORE_DIR).mkdir(
        parents=True,
        exist_ok=True
    )

    vectorstore.save_local(VECTORSTORE_DIR)

    print("=" * 60)
    print("FAISS 벡터 DB 생성 완료")
    print(f"저장 위치: {VECTORSTORE_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    build_vector_db()