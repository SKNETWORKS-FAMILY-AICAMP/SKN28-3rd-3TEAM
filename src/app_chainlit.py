import asyncio

import chainlit as cl

from rag_chain import load_rag


WELCOME_MESSAGE = """
# MediPill

의약품 문서 기반 RAG 질의응답 시스템입니다.

예시 질문:
- 타이레놀 복용 전 주의사항 알려줘
- 감기약 먹으면 졸릴 수 있나요?
- 3살 아이가 타이레놀 먹어도 될까요?
- 배가 아픈데 어떤 약을 약국에서 상담하면 좋을까요?

본 서비스는 문서 기반 참고 정보를 제공하며, 진단이나 처방을 대체하지 않습니다.
"""


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def clean_markdown(text: str) -> str:
    raw_lines = [line.strip() for line in text.splitlines()]
    normalized_lines: list[str] = []

    for index, line in enumerate(raw_lines):
        previous_line = next(
            (value for value in reversed(raw_lines[:index]) if value),
            "",
        )
        next_line = next(
            (value for value in raw_lines[index + 1:] if value),
            "",
        )

        if not line and is_table_line(previous_line) and is_table_line(next_line):
            continue

        normalized_lines.append(line)

    lines: list[str] = []

    for line in normalized_lines:
        previous = lines[-1] if lines else ""

        if not line:
            if lines and previous:
                lines.append("")
            continue

        if lines and is_table_line(previous) and is_table_line(line):
            lines.append(line)
        elif lines and previous and not is_table_line(previous) and is_table_line(line):
            lines.append("")
            lines.append(line)
        elif lines and is_table_line(previous) and not is_table_line(line):
            lines.append("")
            lines.append(line)
        else:
            lines.append(line)

    return "\n".join(lines).strip()


def short_sources(sources: list[dict], limit: int = 3) -> str:
    if not sources:
        return "## 참고 출처\n- 검색된 출처 없음"

    lines = ["## 참고 출처"]

    for i, src in enumerate(sources[:limit], start=1):
        title = src.get("title", "제목 없음")
        manufacturer = src.get("manufacturer", "")
        url = src.get("url", "")

        label = f"**{title}**"
        if manufacturer:
            label += f" / {manufacturer}"
        if url:
            label += f"\n   - {url}"

        lines.append(f"{i}. {label}")

    if len(sources) > limit:
        lines.append(f"\n외 {len(sources) - limit}개 문서 참고")

    return "\n".join(lines)


def make_followup_questions(question_type: str) -> str:
    if question_type == "drug":
        questions = [
            ("나이/체중", "복용하려는 사람의 나이와 체중은 어떻게 되나요?"),
            ("복용 중인 약", "현재 복용 중인 다른 약이나 건강기능식품이 있나요?"),
            ("알레르기", "약물 알레르기나 과거 부작용 경험이 있나요?"),
            ("기저질환", "간질환, 신장질환, 위장질환 같은 기저질환이 있나요?"),
            ("임신/수유", "임신 중이거나 수유 중인가요?"),
        ]
    elif question_type in ["symptom", "disease"]:
        questions = [
            ("시작 시점", "증상은 언제부터 시작되었나요?"),
            ("증상 정도", "증상 정도는 가벼운 편인가요, 심한 편인가요?"),
            ("동반 증상", "고열, 구토, 설사, 호흡곤란, 심한 통증이 있나요?"),
            ("복용 중인 약", "현재 복용 중인 약이 있나요?"),
            ("개인 조건", "나이, 임신 여부, 기저질환 여부를 알려주실 수 있나요?"),
        ]
    else:
        questions = [
            ("기본 정보", "나이, 현재 증상, 복용 중인 약 정보를 알려주세요."),
            ("약 정보", "특정 약 이름이나 성분명을 알고 있다면 함께 입력해주세요."),
        ]

    lines = [
        "## 추가로 확인하면 좋은 질문",
        "| 항목 | 사용자에게 물어볼 내용 |",
        "|---|---|",
    ]
    for item, question in questions:
        lines.append(f"| {item} | {question} |")

    return "\n".join(lines)


def safety_check_table() -> str:
    return "\n".join(
        [
            "## 복용 전 체크표",
            "| 확인 항목 | 왜 확인해야 하나요? |",
            "|---|---|",
            "| 같은 성분 중복 | 같은 성분의 약을 함께 먹으면 과량 복용 위험이 있습니다. |",
            "| 어린이/임산부/수유부/고령자 | 대상에 따라 복용 가능 여부나 용량 확인이 필요할 수 있습니다. |",
            "| 기저질환 | 간질환, 신장질환, 위장질환 등이 있으면 주의가 필요할 수 있습니다. |",
            "| 알레르기/부작용 경험 | 이전에 이상 반응이 있었다면 복용 전 확인이 필요합니다. |",
            "| 증상 악화/지속 | 증상이 심하거나 오래 지속되면 진료 또는 약사 상담이 우선입니다. |",
        ]
    )


def make_final_answer(answer: str, sources: list[dict], question_type: str) -> str:
    type_label = {
        "drug": "의약품 정보 검색",
        "symptom": "증상 기반 일반의약품 상담",
        "disease": "건강 정보 질의",
        "general": "일반 문서 검색",
    }.get(question_type, "문서 검색")

    return (
        f"# MediPill 답변\n\n"
        f"## 질문 유형\n"
        f"| 구분 | 내용 |\n"
        f"|---|---|\n"
        f"| 질문 유형 | {type_label} |\n\n"
        f"## 핵심 답변\n"
        f"{clean_markdown(answer)}\n\n"
        f"{safety_check_table()}\n\n"
        f"{make_followup_questions(question_type)}\n\n"
        f"---\n\n"
        f"{short_sources(sources)}\n\n"
        f"---\n\n"
        f"본 답변은 의료 문서 기반 참고 정보이며, 진단이나 처방을 대체하지 않습니다.\n"
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

        answer, sources, question_type = await asyncio.to_thread(ask, message.content)
        final_answer = make_final_answer(answer, sources, question_type)

        await stream_text(msg, final_answer, delay=0.005)

    except Exception as e:
        await stream_text(
            msg,
            f"오류가 발생했습니다.\n\n```text\n{e}\n```",
            delay=0.005,
        )
