import asyncio
import re
import chainlit as cl
from rag_chain import load_rag


WELCOME_MESSAGE = """
# 💊 MediPill

의약품 문서 기반 RAG 질의응답 시스템입니다.

예시 질문:
- 타이레놀 복용 시 주의사항 알려줘
- 감기약 먹으면 졸릴 수 있나요?
- 3살 아이가 타이레놀 먹어도 될까요?
- 배가 아픈데 어떤 약 먹어야 할까?

⚠️ 본 시스템은 참고용 정보만 제공하며, 진단·처방을 대체하지 않습니다.
"""


TYPE_LABELS = {
    "drug": "의약품 정보 검색",
    "symptom": "증상 기반 일반의약품 안내",
    "disease": "의료·건강 질의응답",
    "general": "일반 문서 검색",
}


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def fix_markdown_ranges(text: str) -> str:
    text = text.replace("~~", "~")
    text = re.sub(r"(\d+)\s*~\s*(\d+)", r"\1\\~\2", text)
    return text


def clean_markdown(text: str) -> str:
    text = fix_markdown_ranges(text)
    text = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")

    raw_lines = [line.rstrip() for line in text.splitlines()]
    lines = []

    for line in raw_lines:
        stripped = line.strip()

        if not stripped:
            if lines and lines[-1] != "":
                lines.append("")
            continue

        if lines:
            prev = lines[-1]

            if is_table_line(prev) and is_table_line(stripped):
                lines.append(stripped)
                continue

            if not is_table_line(prev) and is_table_line(stripped):
                if prev != "":
                    lines.append("")
                lines.append(stripped)
                continue

            if is_table_line(prev) and not is_table_line(stripped):
                lines.append("")
                lines.append(stripped)
                continue

        lines.append(stripped)

    return "\n".join(lines).strip()


def short_sources(sources: list[dict], limit: int = 3) -> str:
    if not sources:
        return "### 참고 출처\n- 검색된 출처 없음"

    lines = ["### 참고 출처"]

    for i, src in enumerate(sources[:limit], start=1):
        title = src.get("title", "제목 없음")
        manufacturer = src.get("manufacturer", "")
        source = src.get("source", "")

        detail = f"**{title}**"

        if manufacturer:
            detail += f" / {manufacturer}"

        if source:
            detail += f" / {source}"

        lines.append(f"{i}. {detail}")

    if len(sources) > limit:
        lines.append(f"\n외 {len(sources) - limit}개 문서 참고")

    return "\n".join(lines)

def is_no_answer(answer: str) -> bool:
    no_answer_phrases = [
        "제공된 문서에서 확인할 수 없습니다",
        "문서에서 확인할 수 없습니다",
        "확인할 수 없습니다",
        "검색된 문서에서 확인할 수 없습니다",
    ]

    return any(
        phrase in answer
        for phrase in no_answer_phrases
    )

def make_final_answer(answer: str, sources: list[dict], question_type: str) -> str:
    type_label = TYPE_LABELS.get(question_type, "문서 검색")
    answer = clean_markdown(answer)

    if is_no_answer(answer):
        return (
            f"**질문 유형:** {type_label}\n\n"
            f"{answer}\n\n"
            f"---\n\n"
            f"⚠️ 본 답변은 의료 문서 기반 참고 정보이며, 진단·처방을 대체하지 않습니다.\n"
            f"정확한 판단은 의사 또는 약사와 상담하세요."
        )

    return (
        f"**질문 유형:** {type_label}\n\n"
        f"{answer}\n\n"
        f"---\n\n"
        f"{short_sources(sources)}\n\n"
        f"---\n\n"
        f"⚠️ 본 답변은 의료 문서 기반 참고 정보이며, 진단·처방을 대체하지 않습니다.\n"
        f"정확한 판단은 의사 또는 약사와 상담하세요."
    )


async def stream_text(msg: cl.Message, text: str, delay: float = 0.01):
    msg.content = ""

    for char in text:
        msg.content += char
        await msg.update()
        await asyncio.sleep(delay)


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("ask", load_rag())
    await cl.Message(content=WELCOME_MESSAGE).send()


@cl.on_message
async def on_message(message: cl.Message):
    ask = cl.user_session.get("ask") or load_rag()
    cl.user_session.set("ask", ask)

    msg = cl.Message(content="")
    await msg.send()

    try:
        await stream_text(
            msg,
            "문서를 검색하고 답변을 생성하는 중입니다...",
            delay=0.01,
        )

        answer, sources, question_type = await asyncio.to_thread(
            ask,
            message.content,
        )

        final_answer = make_final_answer(
            answer,
            sources,
            question_type,
        )

        await stream_text(
            msg,
            final_answer,
            delay=0.005,
        )

    except Exception as e:
        await stream_text(
            msg,
            f"오류가 발생했습니다.\n\n```text\n{e}\n```",
            delay=0.005,
        )