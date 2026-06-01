import json
from glob import glob
from langchain_core.documents import Document


def load_processed_docs():
    docs = []

    for path in glob("data/processed/*.json"):
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)

        for item in items:
            metadata = {
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "url": item.get("url", ""),
                **item.get("metadata", {})
            }

            docs.append(
                Document(
                    page_content=item.get("content", ""),
                    metadata=metadata
                )
            )

    return docs


def unique_clean(values, limit=None):
    result = []

    for value in values:
        if not value:
            continue

        value = str(value).strip()

        if value and value not in result:
            result.append(value)

    return result[:limit] if limit else result


def build_queries_from_plan(question, analysis, plan):
    queries = [question]
    queries += plan.search_queries
    queries += plan.broad_queries
    queries += analysis.search_queries
    queries += analysis.drug_names
    queries += analysis.drug_categories
    queries += analysis.symptoms
    queries += analysis.asked_about
    queries += plan.must_include_terms

    return unique_clean(queries, limit=20)


def choose_prompt_type(intent):
    if intent in ["drug_info", "drug_safety", "side_effect", "dosage", "interaction"]:
        return "drug"

    if intent == "symptom_to_otc":
        return "symptom"

    if intent == "disease_info":
        return "disease"

    return "general"


def product_key(doc):
    return (
        doc.metadata.get("title", ""),
        doc.metadata.get("manufacturer", "")
    )


def deduplicate_docs(docs, max_docs=30):
    seen = set()
    result = []

    for doc in docs:
        key = product_key(doc)

        if key not in seen:
            seen.add(key)
            result.append(doc)

        if len(result) >= max_docs:
            break

    return result


def hybrid_retrieve(queries, vector_retriever, bm25_retriever, max_docs=30):
    docs = []

    for query in queries:
        docs.extend(vector_retriever.invoke(query))
        docs.extend(bm25_retriever.invoke(query))

    return deduplicate_docs(docs, max_docs=max_docs)


def format_docs(docs):
    blocks = []

    for i, doc in enumerate(docs, start=1):
        title = doc.metadata.get("title", "제목 없음")
        manufacturer = doc.metadata.get("manufacturer", "")
        source = doc.metadata.get("source", "출처 없음")
        maker = f"제조사: {manufacturer}\n" if manufacturer else ""

        blocks.append(
            f"[문서 {i}]\n"
            f"제목: {title}\n"
            f"{maker}"
            f"출처: {source}\n"
            f"내용:\n{doc.page_content}"
        )

    return "\n\n".join(blocks)


def format_docs_for_selector(docs, max_chars=1400):
    blocks = []

    for i, doc in enumerate(docs):
        title = doc.metadata.get("title", "제목 없음")
        manufacturer = doc.metadata.get("manufacturer", "")
        content = doc.page_content[:max_chars]
        maker = f"제조사: {manufacturer}\n" if manufacturer else ""

        blocks.append(
            f"[index: {i}]\n"
            f"제목: {title}\n"
            f"{maker}"
            f"내용:\n{content}"
        )

    return "\n\n".join(blocks)


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


def should_clarify(analysis, selected_docs):
    # 위험 신호는 답변 프롬프트에서 진료 우선 안내
    if analysis.risk_level == "high":
        return False

    # 증상 기반 질문은 정보가 부족해도 바로 답변 생성
    # 부족한 정보는 SYMPTOM_PROMPT 안에서 "추가로 확인할 것"으로 안내
    if analysis.intent == "symptom_to_otc":
        return False

    # 질병/건강 정보도 바로 답변 생성
    if analysis.intent == "disease_info":
        return False

    # 검색 문서가 아예 없을 때만 추가 확인
    if not selected_docs:
        return True

    # 특정 약의 안전성 질문인데 나이가 없으면 추가 확인
    if analysis.intent == "drug_safety" and not analysis.target_age:
        return True

    return False


def make_clarifying_answer(docs):
    products = []

    for doc in docs[:5]:
        title = doc.metadata.get("title", "")
        manufacturer = doc.metadata.get("manufacturer", "")

        if manufacturer:
            products.append(f"- {title} / {manufacturer}")
        else:
            products.append(f"- {title}")

    product_text = "\n".join(products) if products else "- 검색된 관련 후보 없음"

    return f"""
### 답변
현재 질문만으로는 특정 약이나 복용 가능 여부를 단정하기 어렵습니다.

### 검색된 관련 후보
{product_text}

### 추가로 확인이 필요한 정보
1. 복용하려는 사람의 나이와 체중
2. 정확한 제품명
3. 증상의 종류와 지속 시간
4. 임신 여부, 기저질환, 복용 중인 다른 약 여부

### 주의
특정 약을 직접 추천하거나 복용을 지시할 수는 없습니다. 다만 제품 설명서 기준으로 어떤 조건에 해당하는지는 비교해드릴 수 있습니다.
"""