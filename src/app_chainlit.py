# src/app_chainlit.py

import chainlit as cl
from rag_chain import load_rag

@cl.on_chat_start
async def on_chat_start():
    ask = load_rag()
    cl.user_session.set("ask", ask)

    await cl.Message(
        content="""
# 💊 MediPick

의료·의약 문서 기반 RAG 질의응답 시스템입니다.

예시 질문:
- 타이레놀 복용 시 주의사항 알려줘
- 아세트아미노펜 부작용 알려줘
- 이 약은 어떻게 보관해야 해?
- 공복에 복용해도 되는지 알려줘

⚠️ 본 시스템은 참고용 의료 정보만 제공합니다. 진단이나 처방은 반드시 의료 전문가와 상담하세요.
"""
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    ask = cl.user_session.get("ask")

    if ask is None:
        ask = load_rag()
        cl.user_session.set("ask", ask)

    question = message.content

    thinking_msg = cl.Message(content="문서를 검색하고 답변을 생성하는 중입니다...")
    await thinking_msg.send()

    try:
        answer, sources = ask(question)

        source_text = "\n\n### 참고 출처\n"

        for idx, src in enumerate(sources, start=1):
            source_text += f"{idx}. **{src['title']}**\n"
            source_text += f"   - 출처: {src['source']}\n"
            source_text += f"   - URL: {src['url']}\n"

        final_answer = f"{answer}\n\n---\n{source_text}"

        thinking_msg.content = final_answer
        await thinking_msg.update()

    except Exception as e:
        thinking_msg.content = f"오류가 발생했습니다.\n\n```text\n{str(e)}\n```"
        await thinking_msg.update()