# src/rag_chain.py

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

TYPE_LABELS = {
    "drug": ["약", "의약품", "복용", "부작용", "주의사항", "효능", "타이레놀", "감기약", "두통약", "진통제", "소화제", "먹어도"],
    "disease": ["증상", "질병", "고혈압", "당뇨", "감기", "독감", "관리", "치료", "예방", "원인"]
}

AMBIGUOUS_WORDS = ["먹어도", "먹어야", "뭐 먹어", "무슨 약", "어떤거", "어떤 거", "추천", "알려줘", "골라줘"]
SPECIFIC_WORDS = ["어린이", "소아", "임산부", "수유", "고령자", "제품명", "현탁액", "정", "캡슐", "시럽", "3살", "4살", "5살"]


QUERY_PROMPT = """
사용자의 의약품 질문을 RAG 검색용 검색어 5개로 바꿔주세요.
규칙: 쉬운 표현을 의약품 문서 표현으로 바꾸고, 유사 증상/성분/효능/부작용을 포함하세요.
설명 없이 검색어만 한 줄에 하나씩 출력하세요. 제품명이나 대상 조건이 있으면 반드시 포함하세요.

예시:
질문: 배가 아픈데 약 어떤거 먹어야할까
복통 위통 소화불량 위장약
속쓰림 위산과다 제산제
복부불쾌감 소화제
위장장애 구역 구토
소화불량 복부팽만

질문: 3살 아이가 타이레놀 먹어도 될까요?
타이레놀 어린이 소아 3세
아세트아미노펜 어린이 현탁액
소아 해열 진통 아세트아미노펜
타이레놀 연령 제한 복용
어린이 해열진통제 복용법

사용자 질문:
{question}
"""

DRUG_PROMPT = """
당신은 의약품 정보 검색 도우미 MediPick입니다.

규칙:
- 반드시 [검색된 문서]에 근거해서만 답변하세요.
- 문서에 없는 내용은 "제공된 문서에서 확인할 수 없습니다."라고 답하세요.
- 특정 약 복용을 추천하거나 지시하지 마세요.
- 여러 제품이 검색되면 제품명과 제조사를 구분하세요.
- 같은 브랜드라도 제형, 성분, 대상 연령, 복용법이 다를 수 있음을 설명하세요.
- 어린이, 임산부, 고령자, 병용 약물, 부작용 질문은 보수적으로 안내하고 의사/약사 상담을 권고하세요.
- 사용자의 질문과 직접 관련 있는 내용만 간결하게 답변하세요.

답변 형식:
### 답변
핵심 답변을 2~4문장으로 작성하세요.

### 제품별 확인 결과
관련 의약품을 제품명/제조사 기준으로 정리하고, 연령·제형·주의사항을 비교하세요.

### 주의해야 할 제품/조건
금기, 연령 제한, 병용 주의, 부작용을 정리하세요.

### 문서 근거
검색된 문서 근거를 요약하세요.

### 주의
최종 복용 여부, 용량, 제품 선택은 의사 또는 약사와 상담해야 한다고 안내하세요.

[검색된 문서]
{context}

[사용자 질문]
{question}

[답변]
"""

DISEASE_PROMPT = """
당신은 의료·건강 정보 검색 도우미 MediPick입니다.
반드시 문서에 근거해서만 답변하고, 진단하지 마세요.
문서에 없는 내용은 확인할 수 없다고 답하세요.

답변 형식:
### 요약
### 관련 증상 또는 관리 방법
### 주의해야 할 상황

[검색된 문서]
{context}

[사용자 질문]
{question}

[답변]
"""

GENERAL_PROMPT = """
당신은 MediPick입니다.
반드시 [검색된 문서]에 근거해서만 답변하세요.
문서에 없는 내용은 확인할 수 없다고 답하세요.

[검색된 문서]
{context}

[사용자 질문]
{question}

[답변]
"""


def classify_question(question: str) -> str:
    for qtype, keywords in TYPE_LABELS.items():
        if any(k in question for k in keywords):
            return qtype
    return "general"


def clean_lines(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        line = line.strip("-•1234567890. ").strip()
        if line and line not in lines:
            lines.append(line)
    return lines


def generate_search_queries(question: str, llm) -> list[str]:
    response = llm.invoke(QUERY_PROMPT.format(question=question))
    queries = clean_lines(response.content)
    return ([question] + [q for q in queries if q != question])[:6]


def product_key(doc):
    return (
        doc.metadata.get("title", "제품명 없음"),
        doc.metadata.get("manufacturer", "")
    )


def deduplicate_docs(docs, max_docs=10):
    seen, result = set(), []

    for doc in docs:
        key = product_key(doc)
        if key not in seen:
            seen.add(key)
            result.append(doc)
        if len(result) >= max_docs:
            break

    return result


def group_products(docs):
    groups = {}

    for doc in docs:
        title, manufacturer = product_key(doc)
        key = f"{title}|{manufacturer}"

        if key not in groups:
            groups[key] = {
                "title": title,
                "manufacturer": manufacturer,
                "docs": []
            }

        groups[key]["docs"].append(doc)

    return list(groups.values())


def is_ambiguous(question: str, groups: list) -> bool:
    has_ambiguous = any(w in question for w in AMBIGUOUS_WORDS)
    has_specific = any(w in question for w in SPECIFIC_WORDS)

    return has_ambiguous and len(groups) >= 2 and not has_specific


def make_clarifying_message(groups: list) -> str:
    product_lines = []

    for group in groups[:5]:
        title = group["title"]
        manufacturer = group["manufacturer"]

        if manufacturer:
            product_lines.append(f"- {title} / {manufacturer}")
        else:
            product_lines.append(f"- {title}")

    products = "\n".join(product_lines)

    return f"""
### 답변
질문하신 내용은 여러 의약품 후보가 검색되어, 현재 정보만으로는 특정 제품을 하나로 정하기 어렵습니다.

### 검색된 관련 의약품 예시
{products}

### 추가로 확인이 필요한 정보
1. 복용하려는 사람의 나이와 체중
2. 정확한 제품명
3. 증상의 종류와 지속 시간
4. 임신 여부, 기저질환, 복용 중인 다른 약 여부

### 주의
특정 약을 직접 추천하거나 복용을 지시할 수는 없습니다.
다만 제품 설명서 기준으로 어떤 제품이 어떤 조건에 해당하는지는 비교해드릴 수 있습니다.
"""


def retrieve_docs(question: str, retriever, llm, max_docs=10):
    queries = generate_search_queries(question, llm)

    print("=" * 80)
    print("원본 질문:", question)
    print("생성된 검색어:", queries)
    print("=" * 80)

    docs = []
    for query in queries:
        docs.extend(retriever.invoke(query))

    docs = deduplicate_docs(docs, max_docs=max_docs)
    return docs, group_products(docs)


def format_docs(docs):
    formatted = []

    for i, doc in enumerate(docs, start=1):
        title = doc.metadata.get("title", "제목 없음")
        manufacturer = doc.metadata.get("manufacturer", "")
        source = doc.metadata.get("source", "출처 없음")
        url = doc.metadata.get("url", "")

        manufacturer_line = (
            f"제조사: {manufacturer}\n"
            if manufacturer else ""
        )

        formatted.append(
            f"[문서 {i}]\n"
            f"제목: {title}\n"
            f"{manufacturer_line}"
            f"출처: {source}\n"
            f"URL: {url}\n"
            f"내용:\n{doc.page_content}"
        )

    return "\n\n".join(formatted)


def make_sources(docs):
    sources = []
    seen = set()

    for doc in docs:
        title = doc.metadata.get("title", "제목 없음")
        manufacturer = doc.metadata.get("manufacturer", "")
        source = doc.metadata.get("source", "출처 없음")
        url = doc.metadata.get("url", "")

        key = (title, manufacturer, source, url)

        if key in seen:
            continue

        seen.add(key)

        sources.append({
            "title": title,
            "manufacturer": manufacturer,
            "source": source,
            "url": url
        })

    return sources


def load_rag():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = FAISS.load_local(
        "vectorstore/faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 12, "fetch_k": 30, "lambda_mult": 0.5}
    )

    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    prompts = {
        "drug": ChatPromptTemplate.from_template(DRUG_PROMPT),
        "disease": ChatPromptTemplate.from_template(DISEASE_PROMPT),
        "general": ChatPromptTemplate.from_template(GENERAL_PROMPT)
    }

    def ask(question: str):
        qtype = classify_question(question)
        docs, groups = retrieve_docs(question, retriever, llm, max_docs=10)

        if qtype == "drug" and is_ambiguous(question, groups):
            return make_clarifying_message(groups), make_sources(docs[:5]), qtype

        context = format_docs(docs)
        messages = prompts[qtype].format_messages(
            context=context,
            question=question
        )

        answer = llm.invoke(messages).content
        return answer, make_sources(docs), qtype

    return ask