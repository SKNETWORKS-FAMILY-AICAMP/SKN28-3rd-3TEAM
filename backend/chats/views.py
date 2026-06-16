import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import ChatHistory
from .serializers import ChatHistorySerializer

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def convert_label(value):
    labels = {
        "FEMALE": "여성",
        "MALE": "남성",
        "OTHER": "기타",
        "UNKNOWN": "미입력",
        "NONE": "해당 없음",
        "PREGNANT": "임신 중",
        "BREASTFEEDING": "수유 중",
    }
    return labels.get(value, value)


def build_profile_context(profile):
    return f"""
나이: {profile.age}세
성별: {convert_label(profile.gender)}
키: {profile.height}cm
체중: {profile.weight}kg
혈액형: {convert_label(profile.blood_type)}
임신/수유 여부: {convert_label(profile.pregnancy_status)}
알레르기: {profile.allergies}
기저질환: {profile.diseases}
복용 중인 약물: {profile.current_medications}
"""


def build_personalized_warnings(profile):
    warnings = []

    if profile.allergies and profile.allergies != "없음":
        warnings.append(f"알레르기 정보: {profile.allergies}")

    if profile.diseases and profile.diseases != "없음":
        warnings.append(f"기저질환 정보: {profile.diseases}")

    if profile.current_medications and profile.current_medications != "없음":
        warnings.append(f"복용 중인 약물 정보: {profile.current_medications}")

    if profile.pregnancy_status == "PREGNANT":
        warnings.append("임신 중")

    if profile.pregnancy_status == "BREASTFEEDING":
        warnings.append("수유 중")

    if not warnings:
        warnings.append("등록된 고위험 건강정보 없음")

    return "\n".join([f"- {item}" for item in warnings])


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat(request):
    user = request.user
    question = request.data.get("question")

    if not question:
        return Response(
            {"error": "질문을 입력해주세요."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        profile = user.health_profile
        profile_context = build_profile_context(profile)
        personalized_warnings = build_personalized_warnings(profile)
    except Exception:
        profile_context = "사용자 건강정보가 등록되어 있지 않습니다."
        personalized_warnings = "건강정보 없음"

    prompt = f"""
당신은 의약품 정보 제공을 돕는 AI 상담 보조 시스템입니다.

아래 사용자의 건강정보는 답변 생성에 참고만 하세요.
답변 본문에 건강정보 전체를 그대로 나열하지 마세요.

사용자 건강정보:
{profile_context}

개인화 주의 포인트:
{personalized_warnings}

사용자 질문:
{question}

답변 조건:
- 사용자가 물어본 질문에 먼저 답하세요.
- 건강정보 전체를 반복해서 보여주지 마세요.
- 필요한 경우에만 알레르기, 기저질환, 복용 중인 약물, 임신/수유 여부를 자연스럽게 언급하세요.
- 답변은 아래 형식으로 작성하세요.

1. 간단 답변
2. 개인 건강정보 기준 주의사항
3. 추가 확인이 필요한 경우
4. 전문가 상담 권고

마지막에는 반드시 아래 문장을 포함하세요.
"본 답변은 참고용이며, 정확한 복용 여부는 의사 또는 약사와 상담하시기 바랍니다."
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 의약품 정보를 쉽게 설명하는 한국어 AI 상담 보조 시스템입니다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
        )

        answer = response.choices[0].message.content

    except Exception:
        answer = f"""
1. 간단 답변
질문하신 약은 개인의 건강 상태와 함께 복용 중인 약물에 따라 주의사항이 달라질 수 있습니다.

2. 개인 건강정보 기준 주의사항
등록된 건강정보를 기준으로 확인이 필요한 부분은 다음과 같습니다.

{personalized_warnings}

해당 항목이 있는 경우, 일반적인 복용 기준과 다르게 주의가 필요할 수 있습니다.

3. 추가 확인이 필요한 경우
정확한 판단을 위해서는 약의 성분명, 복용량, 복용 횟수, 현재 복용 중인 다른 약물을 함께 확인하는 것이 좋습니다.

4. 전문가 상담 권고
특히 알레르기, 기저질환, 임신/수유 여부, 다른 약물 복용 여부가 있는 경우에는 의사 또는 약사와 상담 후 복용하는 것이 안전합니다.

본 답변은 참고용이며, 정확한 복용 여부는 의사 또는 약사와 상담하시기 바랍니다.
"""

    chat_history = ChatHistory.objects.create(
        user=user,
        question=question,
        answer=answer
    )

    return Response({
        "id": chat_history.id,
        "question": question,
        "answer": answer
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chat_history(request):
    histories = ChatHistory.objects.filter(user=request.user).order_by("-created_at")
    serializer = ChatHistorySerializer(histories, many=True)
    return Response(serializer.data)