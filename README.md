# 🩺 Medipick
의료·의약 문서 기반 RAG 질의응답 시스템

---

# 📌 프로젝트 소개

Medipick은 의료·의약 문서를 기반으로 사용자의 질문에 신뢰성 있는 답변을 제공하는 RAG(Retrieval-Augmented Generation) 기반 AI 시스템입니다.

단순 생성형 AI 응답이 아닌,
실제 의료 문서를 검색한 뒤 해당 내용을 기반으로 답변을 생성하여 의료 AI의 환각(Hallucination)을 줄이고 신뢰성을 높이는 것을 목표로 합니다.

---

# 🎯 프로젝트 목표

- 의료·의약 정보의 신뢰성 향상
- 문서 기반 의료 질의응답 시스템 구축
- 출처 기반 응답 제공
- 의료 AI 환각(Hallucination) 감소
- RAG 구조 이해 및 구현

---

# ✨ 주요 기능

## 1️⃣ 의료·의약 질의응답

사용자의 자연어 질문에 대해 관련 의료 문서를 검색한 후 답변 생성

### 예시
- "고혈압 증상 알려줘"
- "당뇨 관리 방법 알려줘"
- "감기약 공복 복용 가능한가요?"

---

## 2️⃣ 의약품 정보 검색

의약품 설명서를 기반으로:

- 효능
- 복용 방법
- 부작용
- 주의사항

등의 정보를 제공

---

## 3️⃣ 응급처치 가이드

응급 상황 발생 시 단계별 응급처치 방법 제공

### 예시
- 심폐소생술(CPR)
- 화상 응급처치
- 출혈 응급처치

---

## 4️⃣ 출처 기반 응답 제공

답변 생성 시 참고한 문서와 출처를 함께 제공

### 제공 정보
- 문서명
- 기관명
- 참고 문장

---

## 5️⃣ 의료 문서 요약

긴 의료 문서를 핵심 내용 중심으로 요약 제공

---

# 🏗️ 시스템 아키텍처

```text
의료 문서 수집
        ↓
PDF/Text 전처리
        ↓
Chunking
        ↓
Embedding 생성
        ↓
Vector DB 저장 (ChromaDB)
━━━━━━━━━━━━━━━━━━
사용자 질문 입력
        ↓
질문 유형 분석
        ↓
Retriever 검색
        ↓
LLM 답변 생성
        ↓
출처 기반 응답 제공
```

---

# ⚙️ 기술 스택

## AI / RAG
- LangChain
- OpenAI API
- OpenAI Embedding Model

## Vector Database
- ChromaDB

## Frontend
- Streamlit

## Language
- Python

---

# 📂 프로젝트 구조

```text
SKN28-3rd-3TEAM/
│
├── data/
│   ├── raw/                # 원본 의료 문서
│   └── processed/          # 전처리된 문서
│
├── vector_db/              # ChromaDB 저장 공간
│
├── app.py                  # Streamlit UI
├── ingest.py               # 문서 임베딩 및 DB 저장
├── rag.py                  # Retrieval + Generation
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# 🚀 실행 방법

## 1️⃣ 저장소 Clone

```bash
git clone https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN28-3rd-3TEAM.git
cd SKN28-3rd-3TEAM
```

---

## 2️⃣ 가상환경 생성

```bash
python -m venv venv
```

---

## 3️⃣ 가상환경 실행

### Windows

```bash
venv\Scripts\activate
```

---

## 4️⃣ 라이브러리 설치

```bash
pip install -r requirements.txt
```

---

## 5️⃣ OpenAI API Key 설정

`.env`

```env
OPENAI_API_KEY=your_api_key
```

---

## 6️⃣ 문서 임베딩 실행

```bash
python ingest.py
```

---

## 7️⃣ Streamlit 실행

```bash
streamlit run app.py
```

---

# 📌 향후 개발 예정 기능

- 질문 유형 자동 분류
- 병용 금기 약물 안내
- 음성 기반 질의응답
- 의료 문서 자동 요약 고도화
- 사용자 맞춤 건강 정보 제공

---

# 👥 팀원 역할

| 이름 | 역할 |
|---|---|
| 김민욱 | RAG / LLM 개발 |
| 김주영 | 데이터 전처리 |
| 김소윤| UI / Streamlit |
| 심윤성| 발표 및 기획 |

---

# ⚠️ 주의사항

본 시스템은 의료 진단 목적이 아닌 정보 제공 시스템입니다.

정확한 진단 및 치료는 반드시 전문 의료진과 상담해야 합니다.

---

# 📖 기대 효과

- 의료 정보 접근성 향상
- 신뢰 기반 의료 AI 서비스 구현
- RAG 구조 학습 및 실전 적용
- 생성형 AI의 의료 분야 활용 가능성 검증