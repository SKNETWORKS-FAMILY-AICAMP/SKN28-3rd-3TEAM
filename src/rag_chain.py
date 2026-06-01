# src/rag_chain.py

import json
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever

from rag_prompts import (
    ANALYZER_PROMPT,
    PLANNER_PROMPT,
    DOC_SELECTOR_PROMPT,
    DRUG_PROMPT,
    SYMPTOM_PROMPT,
    DISEASE_PROMPT,
    GENERAL_PROMPT,
)

from rag_utils import (
    load_processed_docs,
    build_queries_from_plan,
    hybrid_retrieve,
    format_docs,
    format_docs_for_selector,
    make_sources,
    should_clarify,
    make_clarifying_answer,
)

load_dotenv()


Intent = Literal[
    "drug_info",
    "drug_safety",
    "side_effect",
    "dosage",
    "interaction",
    "symptom_to_otc",
    "disease_info",
    "general",
]

TargetGroup = Literal[
    "child",
    "adult",
    "elderly",
    "pregnant",
    "unknown",
]

RiskLevel = Literal[
    "low",
    "medium",
    "high",
    "unknown",
]

DocDecisionType = Literal[
    "possible_match",
    "not_match",
    "unclear",
]


class QueryAnalysis(BaseModel):
    intent: Intent = Field(description="사용자 질문 의도")
    symptoms: list[str] = Field(default_factory=list)
    drug_names: list[str] = Field(default_factory=list)
    drug_categories: list[str] = Field(default_factory=list)
    target_age: int | None = None
    target_group: TargetGroup = "unknown"
    asked_about: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = "unknown"
    needs_clarification: bool = False
    search_queries: list[str] = Field(default_factory=list)


class RetrievalPlan(BaseModel):
    search_queries: list[str] = Field(default_factory=list)
    broad_queries: list[str] = Field(default_factory=list)
    must_include_terms: list[str] = Field(default_factory=list)
    exclude_terms: list[str] = Field(default_factory=list)


class DocDecision(BaseModel):
    index: int
    title: str
    decision: DocDecisionType
    reason: str


class DocSelectionResult(BaseModel):
    selected_indexes: list[int] = Field(default_factory=list)
    decisions: list[DocDecision] = Field(default_factory=list)


def analyze_query(question, llm):
    analyzer = llm.with_structured_output(QueryAnalysis)

    return analyzer.invoke(
        ANALYZER_PROMPT.format(question=question)
    )


def build_retrieval_plan(question, analysis, llm):
    planner = llm.with_structured_output(RetrievalPlan)

    return planner.invoke(
        PLANNER_PROMPT.format(
            question=question,
            analysis=json.dumps(
                analysis.model_dump(),
                ensure_ascii=False,
                indent=2
            )
        )
    )


def resolve_prompt_type(analysis: QueryAnalysis) -> str:
    """
    Analyzer가 intent를 general로 잘못 분류하더라도,
    구조화된 필드(symptoms, drug_categories, drug_names)를 보고
    답변 프롬프트 타입을 보정한다.
    """

    if analysis.intent == "symptom_to_otc":
        return "symptom"

    if analysis.intent == "disease_info":
        return "disease"

    if analysis.intent in [
        "drug_info",
        "drug_safety",
        "side_effect",
        "dosage",
        "interaction",
    ]:
        return "drug"

    # intent가 general이어도 증상/약 카테고리가 있으면 증상 기반 답변으로 처리
    if analysis.symptoms or analysis.drug_categories:
        return "symptom"

    # 약 이름이 있으면 의약품 정보 답변으로 처리
    if analysis.drug_names:
        return "drug"

    return "general"


def select_docs_with_llm(question, analysis, plan, docs, llm):
    if not docs:
        return []

    selector = llm.with_structured_output(DocSelectionResult)

    result = selector.invoke(
        DOC_SELECTOR_PROMPT.format(
            question=question,
            analysis=json.dumps(
                analysis.model_dump(),
                ensure_ascii=False,
                indent=2
            ),
            plan=json.dumps(
                plan.model_dump(),
                ensure_ascii=False,
                indent=2
            ),
            documents=format_docs_for_selector(docs)
        )
    )

    selected = [
        docs[idx]
        for idx in result.selected_indexes
        if 0 <= idx < len(docs)
    ]

    if selected:
        return selected[:8]

    unclear_indexes = [
        decision.index
        for decision in result.decisions
        if decision.decision == "unclear"
    ]

    selected = [
        docs[idx]
        for idx in unclear_indexes
        if 0 <= idx < len(docs)
    ]

    return selected[:8] if selected else docs[:5]


def load_rag():
    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0
    )

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vectorstore = FAISS.load_local(
        "vectorstore/faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    vector_retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 10,
            "fetch_k": 40,
            "lambda_mult": 0.4
        }
    )

    raw_docs = load_processed_docs()

    bm25_retriever = BM25Retriever.from_documents(raw_docs)
    bm25_retriever.k = 10

    prompts = {
        "drug": ChatPromptTemplate.from_template(DRUG_PROMPT),
        "symptom": ChatPromptTemplate.from_template(SYMPTOM_PROMPT),
        "disease": ChatPromptTemplate.from_template(DISEASE_PROMPT),
        "general": ChatPromptTemplate.from_template(GENERAL_PROMPT),
    }

    def ask(question: str):
        # 1. LLM Query Analyzer
        analysis = analyze_query(question, llm)

        # 2. LLM Retrieval Planner
        plan = build_retrieval_plan(question, analysis, llm)
        queries = build_queries_from_plan(question, analysis, plan)

        # 기존 choose_prompt_type 대신 구조화 결과 기반 보정 함수 사용
        prompt_type = resolve_prompt_type(analysis)

        print("=" * 80)
        print("[사용자 질문]", question)
        print("[질문 분석]", analysis.model_dump())
        print("[검색 계획]", plan.model_dump())
        print("[검색어]", queries)
        print("[프롬프트 타입]", prompt_type)
        print("=" * 80)

        # 3. Hybrid Retriever
        retrieved_docs = hybrid_retrieve(
            queries=queries,
            vector_retriever=vector_retriever,
            bm25_retriever=bm25_retriever,
            max_docs=30
        )

        # 4. LLM Document Selector
        selected_docs = select_docs_with_llm(
            question=question,
            analysis=analysis,
            plan=plan,
            docs=retrieved_docs,
            llm=llm
        )

        # 5. Clarification
        if should_clarify(analysis, selected_docs):
            return make_clarifying_answer(selected_docs), make_sources(selected_docs), prompt_type

        # 6. Answer Generator
        messages = prompts[prompt_type].format_messages(
            question=question,
            context=format_docs(selected_docs),
            analysis=json.dumps(
                analysis.model_dump(),
                ensure_ascii=False,
                indent=2
            ),
            plan=json.dumps(
                plan.model_dump(),
                ensure_ascii=False,
                indent=2
            )
        )

        answer = llm.invoke(messages).content

        return answer, make_sources(selected_docs), prompt_type

    return ask