# 💊 MediPill AI

<div align="center">

### Public Medical Data 기반 의료 RAG 질의응답 시스템

의약품 공공데이터와 LLM 기반 Retrieval-Augmented Generation(RAG)을 결합하여  
신뢰 가능한 의료 정보를 제공하는 Explainable Medical AI Project

</div>

---

# Introduction

MediPill AI는 식품의약품안전처 및 공공 의약품 데이터를 기반으로 구축한  
의료·의약 특화 RAG(Retrieval-Augmented Generation) 질의응답 시스템입니다.

기존 생성형 AI는 의료 분야에서 다음과 같은 문제를 가질 수 있습니다.

- Hallucination(허위 정보 생성)
- 출처 없는 답변
- 최신 의료 데이터 반영 한계
- 설명 가능성 부족(Explainability)

MediPill AI는 이러한 문제를 해결하기 위해:

1. 실제 공공 의약품 데이터를 검색(Retrieval)
2. 검색 결과를 기반으로 Context 구성
3. LLM이 근거 기반 응답 생성

구조를 적용하여 의료 AI의 신뢰성을 향상시키는 것을 목표로 합니다.

---

#  Project Objectives

- 의료 분야 Hallucination 최소화
- 공공 의약품 데이터 기반 QA 시스템 구축
- Retrieval 기반 Explainable AI 구현
- Vector Database 기반 검색 최적화
- 의료 특화 RAG Pipeline 설계 및 구현
- 사용자 친화적 의약품 정보 제공
- OCR 기반 약품 인식 기능 확장 가능성 확보

---

# Core Features

## 1. Medical RAG Question Answering

사용자의 자연어 질문을 분석한 후 관련 의약품 문서를 검색하고, 검색된 데이터를 기반으로 답변을 생성합니다.

### Example Queries

```text
- 타이레놀 복용 시 주의사항 알려줘
- 어린이도 복용 가능한가요?
- 공복 복용 가능한 약인가요?
- 대표적인 부작용은 무엇인가요?
- 동일 성분 의약품도 존재하나요?
```

---

## 2. Retrieval-Based Response Generation

LLM이 직접 답변을 생성하는 것이 아니라,  
검색된 의약품 문서를 기반으로 응답을 생성합니다.

### 제공 정보

- 제품명
- 제조사
- 품목기준코드
- 주요 성분
- 효능 및 효과
- 용법 및 용량
- 복용 시 주의사항
- 부작용 정보
- 약물 상호작용
- 보관 방법

---

## 3. Explainable AI Response

생성된 답변과 함께 실제 참고한 데이터 출처를 제공합니다.

### Included Metadata

- 의약품명
- 업체명
- 품목기준코드
- 검색 문서 일부
- 공공데이터 출처
- Retrieval Context

이를 통해 사용자는 답변의 신뢰성과 근거를 직접 검증할 수 있습니다.

---

## 4. Medical Information Summarization

긴 의약품 설명서를 사용자가 이해하기 쉬운 형태로 요약합니다.

### Summary Examples

- 핵심 복용법 요약
- 주요 부작용 요약
- 복용 금기사항 요약
- 고령자/어린이 복용 주의사항 요약

---

## 5. OCR-Based Future Expansion

향후 OCR 및 Computer Vision 기술을 활용하여:

- 알약 이미지 인식
- 약 봉투 OCR
- 약품 코드 추출
- 자동 의약품 검색

기능으로 확장 가능한 구조를 고려하고 있습니다.

---

#  System Architecture

```text
┌─────────────────────────────┐
│ Public Medical Data Sources │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Data Cleaning & Preprocess  │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Document Chunking           │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Embedding Generation        │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Vector Database (FAISS)     │
└──────────────┬──────────────┘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
               ↓
┌─────────────────────────────┐
│ User Question Input         │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Query Embedding             │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Similar Document Retrieval  │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Context Construction        │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ LLM Response Generation     │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Answer + Source Evidence    │
└─────────────────────────────┘
```

---

# ⚙ Tech Stack

## AI / NLP

- Python
- LangChain
- OpenAI API
- HuggingFace Transformers
- Sentence Transformers

---

## Vector Database

- FAISS
- ChromaDB

---

## Backend

- FastAPI
- Flask

---

## Frontend

- Streamlit

---

## Data Processing

- Pandas
- NumPy
- Regex
- BeautifulSoup

---

## OCR / Vision (Planned)

- EasyOCR
- OpenCV
- YOLO

---

# Dataset & Data Sources

## Public Medical Data

- 식품의약품안전처 의약품 API
- 의약품안전나라
- 공공데이터포털
- 보건의료 빅데이터 개방 시스템

---

#  RAG Pipeline

```text
User Query
    ↓
Query Embedding
    ↓
Vector Similarity Search
    ↓
Relevant Medical Document Retrieval
    ↓
Context Injection
    ↓
LLM Answer Generation
    ↓
Grounded Response with Evidence
```

---

# Future Work

- OCR 기반 알약 검색 기능
- 음성 기반 의료 질의응답
- 약물 상호작용 자동 탐지
- 복약 관리 기능
- 모바일 앱 서비스화
- 다국어 의료 질의응답 지원

---

# Expected Impact

MediPill AI는 단순 챗봇이 아닌,  
공공 의료 데이터를 기반으로 신뢰 가능한 정보를 제공하는  
Explainable Medical AI System을 목표로 합니다.

이를 통해:

- 의료 AI의 신뢰성 향상
- Hallucination 감소
- 의료 정보 접근성 향상
- 공공데이터 활용 사례 확대

를 기대할 수 있습니다.

---

#  Team

| Role | Description |
|---|---|
| Data Engineering | 의료 데이터 수집 및 전처리 |
| RAG Pipeline | 문서 검색 및 임베딩 구축 |
| LLM Engineering | 질의응답 모델 구성 |
| Backend | API 및 서버 개발 |
| Frontend | 사용자 인터페이스 구현 |
| OCR Research | 이미지 기반 약품 인식 연구 |

---

#  License

This project is intended for academic and educational purposes.

Medical information provided by this system should not be considered as professional medical advice.