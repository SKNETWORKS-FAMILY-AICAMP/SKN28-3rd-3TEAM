# src/build_vector_db.py

import os
import json
from glob import glob
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

os.makedirs("vectorstore", exist_ok=True)

def load_all_json_docs():
    docs = []

    for path in glob("data/processed/*.json"):
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)

        for item in items:
            docs.append(
                Document(
                    page_content=item["content"],
                    metadata={
                        "title": item.get("title", ""),
                        "source": item.get("source", ""),
                        "url": item.get("url", "")
                    }
                )
            )

    return docs

def build_vector_db():
    documents = load_all_json_docs()

    if not documents:
        raise ValueError("data/processed 폴더에 문서가 없습니다. 먼저 collect_openfda.py를 실행하세요.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120
    )

    split_docs = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vectorstore = FAISS.from_documents(
        documents=split_docs,
        embedding=embeddings
    )

    vectorstore.save_local("vectorstore/faiss_index")

    print(f"FAISS 저장 완료: {len(split_docs)}개 chunk")

if __name__ == "__main__":
    build_vector_db()