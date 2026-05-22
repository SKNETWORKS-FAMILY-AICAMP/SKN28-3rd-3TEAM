# src/rag_chain.py

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

def format_docs(docs):
    formatted = []

    for i, doc in enumerate(docs, start=1):
        formatted.append(
            f"""
[문서 {i}]
제목: {doc.metadata.get("title", "제목 없음")}
출처: {doc.metadata.get("source", "출처 없음")}
URL: {doc.metadata.get("url", "")}
내용:
{doc.page_content}
"""
        )

    return "\n\n".join(formatted)

def load_rag():
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vectorstore = FAISS.load_local(
        "vectorstore/faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 4}
    )

    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template("""
당신은 의료·의약 문서 기반 RAG 질의응답 시스템 'MediPick'입니다.

반드시 지켜야 할 규칙:
1. 아래 [검색된 문서]에 있는 내용만 근거로 답변하세요.
2. 문서에서 확인할 수 없는 내용은 추측하지 말고 "제공된 문서에서 확인할 수 없습니다."라고 답하세요.
3. 진단, 처방, 복용 지시처럼 단정적인 표현은 피하세요.
4. 문서 안에 있는 내용을 기반으로 환자가 증상에 따른 약을 추천 받길 원한다면 어떤 약이 좋은지 추천해주세요.
5. 사용자가 응급 증상, 심각한 통증, 호흡곤란, 의식 저하 등을 언급하면 즉시 의료진 또는 응급실 상담을 권고하세요.
7. 답변 마지막에 참고한 문서 출처를 요약하세요.
8. 일반 사용자가 이해하기 쉽게 한국어로 답변하세요.

[검색된 문서]
{context}

[사용자 질문]
{question}

[답변]
""")

    def ask(question: str):
        docs = retriever.invoke(question)
        context = format_docs(docs)

        messages = prompt.format_messages(
            context=context,
            question=question
        )

        response = llm.invoke(messages)

        sources = []
        seen = set()

        for doc in docs:
            key = (
                doc.metadata.get("title", ""),
                doc.metadata.get("source", ""),
                doc.metadata.get("url", "")
            )

            if key not in seen:
                seen.add(key)
                sources.append({
                    "title": doc.metadata.get("title", "제목 없음"),
                    "source": doc.metadata.get("source", "출처 없음"),
                    "url": doc.metadata.get("url", "")
                })

        return response.content, sources

    return ask