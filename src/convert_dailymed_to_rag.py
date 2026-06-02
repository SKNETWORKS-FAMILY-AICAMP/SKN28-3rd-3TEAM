# src/convert_dailymed_to_rag.py

import json
import time
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

load_dotenv()


INPUT_PATH = "data/processed/dailymed_rag_ready.json"
OUTPUT_PATH = "data/processed/dailymed_section_docs.json"


class KoreanSearchHint(BaseModel):
    korean_drug_name: str = Field(
        description="영문 약명을 한국어로 표기한 이름"
    )
    korean_keywords: list[str] = Field(
        description="한국어 검색에 도움이 되는 키워드 목록"
    )
    korean_summary: str = Field(
        description="해당 섹션 내용을 한국어로 짧게 설명"
    )


def get_llm():
    return ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0
    )


def generate_korean_hint(
    llm,
    drug_name: str,
    title: str,
    section: str,
    text: str
) -> KoreanSearchHint:
    prompt = f"""
당신은 의료·의약 RAG 시스템의 전처리 도우미입니다.

목표:
영문 의약품 문서를 한국어 질문으로도 검색할 수 있도록
한국어 검색 힌트를 생성하세요.

규칙:
- 원문 내용을 바꾸거나 임의로 추가하지 마세요.
- 약명은 일반적으로 한국어에서 쓰는 표기로 작성하세요.
- 예: amoxicillin → 아목시실린
- 예: ibuprofen → 이부프로펜
- 예: acetaminophen → 아세트아미노펜
- section이 dosage이면 복용법, 용량, 성인 용량, 소아 용량, 체중별 용량 같은 검색 키워드를 포함하세요.
- section이 warnings이면 주의사항, 경고, 금기, 알레르기 같은 검색 키워드를 포함하세요.
- section이 adverse_reactions이면 부작용, 이상반응 같은 검색 키워드를 포함하세요.
- section이 dose_patterns이면 체중별 용량, mg/kg/day, 시간 간격 같은 검색 키워드를 포함하세요.
- korean_summary는 2~4문장으로 작성하세요.
- 실제 처방이나 복용 지시를 하지 마세요.

영문 약명:
{drug_name}

제품명:
{title}

문서 섹션:
{section}

원문 일부:
{text[:3000]}
"""

    structured_llm = llm.with_structured_output(KoreanSearchHint)
    return structured_llm.invoke(prompt)


def safe_generate_korean_hint(
    llm,
    drug_name: str,
    title: str,
    section: str,
    text: str,
    max_retries: int = 3
) -> KoreanSearchHint:
    for attempt in range(1, max_retries + 1):
        try:
            return generate_korean_hint(
                llm=llm,
                drug_name=drug_name,
                title=title,
                section=section,
                text=text
            )

        except Exception as e:
            print(f"[힌트 생성 실패] {drug_name} / {section} / {attempt}회차")
            print(e)
            time.sleep(2 * attempt)

    return KoreanSearchHint(
        korean_drug_name=drug_name,
        korean_keywords=[
            drug_name,
            section,
            "의약품",
            "복용법",
            "주의사항",
            "부작용"
        ],
        korean_summary="한국어 검색 힌트 생성에 실패하여 기본 키워드만 사용합니다."
    )


def make_hint_block(hint: KoreanSearchHint) -> str:
    keywords = ", ".join(hint.korean_keywords)

    return f"""
[한국어 검색 힌트]
한글 약명: {hint.korean_drug_name}
검색 키워드: {keywords}
요약: {hint.korean_summary}
"""


def create_section_doc(
    title: str,
    content: str,
    drug_name: str,
    section: str,
    original_title: str,
    setid: str = "",
    source: str = "DailyMed"
):
    return {
        "title": title,
        "content": content.strip(),
        "source": source,
        "url": "",
        "metadata": {
            "type": "drug",
            "country": "US",
            "language": "en",
            "drug_name": drug_name,
            "original_title": original_title,
            "setid": setid,
            "section": section,
            "contains_dosage": section in ["dosage", "dose_patterns"],
            "contains_warning": section == "warnings",
            "contains_side_effect": section == "adverse_reactions"
        }
    }


def build_section_content(
    item: dict,
    section: Literal[
        "dosage",
        "warnings",
        "adverse_reactions",
        "dose_patterns"
    ],
    original_text: str,
    hint: KoreanSearchHint
) -> str:
    drug_name = item.get("drug_name", "")
    title = item.get("title", drug_name)

    section_label_map = {
        "dosage": "복용법/용량",
        "warnings": "주의사항/경고",
        "adverse_reactions": "부작용/이상반응",
        "dose_patterns": "추출 용량 패턴"
    }

    section_label = section_label_map.get(section, section)

    return f"""
의약품명: {title}
원문 약명: {drug_name}
문서 구분: {section_label}

{make_hint_block(hint)}

[영문 원문]
{original_text}
"""


def build_dose_patterns_text(item: dict) -> str:
    dose_patterns = item.get("dose_patterns", [])

    lines = []

    for idx, pattern in enumerate(dose_patterns, start=1):
        pattern_type = pattern.get("type", "")
        matched = pattern.get("matched", "")
        context = pattern.get("context", "")

        lines.append(
            f"{idx}. 유형: {pattern_type}\n"
            f"   추출 용량: {matched}\n"
            f"   문맥: {context}"
        )

    return "\n\n".join(lines)


def split_drug_document(
    item: dict,
    llm
) -> list[dict]:
    docs = []

    drug_name = item.get("drug_name", "")
    original_title = item.get("title", drug_name)
    setid = item.get("setid", "")

    section_sources = {
        "dosage": item.get("dosage_text", ""),
        "warnings": item.get("warnings_text", ""),
        "adverse_reactions": item.get("adverse_reactions_text", ""),
        "dose_patterns": build_dose_patterns_text(item)
    }

    for section, original_text in section_sources.items():
        if not original_text:
            continue

        print(f"[힌트 생성] {drug_name} / {section}")

        hint = safe_generate_korean_hint(
            llm=llm,
            drug_name=drug_name,
            title=original_title,
            section=section,
            text=original_text
        )

        content = build_section_content(
            item=item,
            section=section,
            original_text=original_text,
            hint=hint
        )

        docs.append(
            create_section_doc(
                title=f"{drug_name} - {section}",
                content=content,
                drug_name=drug_name,
                section=section,
                original_title=original_title,
                setid=setid
            )
        )

    return docs


def convert_dailymed_file(
    input_path: str = INPUT_PATH,
    output_path: str = OUTPUT_PATH
):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]

    llm = get_llm()
    all_docs = []

    for idx, item in enumerate(data, start=1):
        drug_name = item.get("drug_name", "")
        print("=" * 80)
        print(f"[{idx}/{len(data)}] 변환 중: {drug_name}")
        print("=" * 80)

        section_docs = split_drug_document(
            item=item,
            llm=llm
        )

        all_docs.extend(section_docs)

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            all_docs,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("=" * 80)
    print("DailyMed 섹션 분리 + 한국어 검색 힌트 생성 완료")
    print(f"원본 약품 수: {len(data)}")
    print(f"생성 문서 수: {len(all_docs)}")
    print(f"저장 위치: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    convert_dailymed_file()