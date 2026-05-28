# MediPill AI

## RAG-Based Multimodal Medical LLM System

MediPill AI는 공식 의료 문서를 기반으로 Retrieval-Augmented Generation(RAG)을 수행하는 멀티모달 의료 LLM 시스템입니다.

본 프로젝트는 생성형 AI의 Hallucination 문제를 줄이기 위해 DailyMed, RxNav 등 공식 의료 데이터를 기반으로 Retrieval 구조를 구성하였으며, Grounded Response 기반 의료 질의응답 시스템 구현을 목표로 합니다.

또한 텍스트 질의뿐 아니라 알약 이미지 기반 입력까지 지원하는 멀티모달 구조를 통해 의료 정보 접근성을 확장하고자 하였습니다.

---

# Introduction

기존 생성형 AI 기반 의료 QA 시스템은 다음과 같은 한계를 가질 수 있습니다.

* 출처가 불명확한 답변 생성
* 최신 의료 정보 반영 한계
* Hallucination 발생 가능성
* 설명 가능한 근거 부족
* 이미지 기반 의료 질의 처리 한계

의료 분야에서는 잘못된 정보 생성이 실제 사용자에게 위험할 수 있기 때문에, 단순 생성형 응답이 아닌 공식 문서를 기반으로 한 Grounded AI 구조가 중요합니다.

MediPill AI는 이러한 문제를 해결하기 위해 Retrieval-Augmented Generation(RAG) 기반 구조를 적용하였으며, 공식 의료 문서를 검색한 뒤 해당 Context를 기반으로 LLM 응답을 생성합니다.

---

# Project Objectives

* 의료 분야 Hallucination 최소화
* 공식 의료 문서 기반 Grounded QA 구현
* Explainable Medical AI 구조 설계
* 의료 특화 RAG Pipeline 구축
* Multimodal 기반 의료 질의응답 확장
* Vision AI 기반 Drug Identification 연동
* 공식 의료 데이터 기반 Retrieval 구조 구현

---

# Why RAG in Medical AI?

의료 분야에서는 생성형 AI의 답변 정확성과 근거가 매우 중요합니다.

기존 LLM은 학습 데이터에 의존하여 답변을 생성하기 때문에:

* 최신 의약품 정보 반영이 어렵고
* 허위 정보를 생성할 가능성이 있으며
* 답변 근거를 명확히 설명하기 어렵습니다.

MediPill AI는 Retrieval-Augmented Generation(RAG)을 통해:

1. 공식 의료 문서를 검색하고
2. 관련 Context를 추출한 뒤
3. 해당 정보를 기반으로 LLM 응답을 생성합니다.

이를 통해 단순 생성형 응답이 아닌 Grounded Medical Response를 제공합니다.

---

# Core Features

## 1. Medical RAG Question Answering

사용자의 의료 질문에 대해 관련 의약품 문서를 Retrieval하고, 검색된 Context 기반으로 답변을 생성합니다.

### Example Queries

```text id="n7u6qg"
- 타이레놀 공복 복용 가능한가요?
- 대표적인 부작용은 무엇인가요?
- 어린이도 복용 가능한 약인가요?
- 약물 상호작용이 있나요?
```

---

## 2. Official Medical Document Retrieval

FDA/NLM 공식 의료 데이터베이스를 기반으로 Retrieval을 수행합니다.

### Medical Sources

* DailyMed
* RxNav
* openFDA

### Retrieved Information

* 효능 및 효과
* 용법 및 용량
* 금기사항
* 부작용
* 약물 상호작용
* 경고 및 주의사항

---

## 3. Grounded Medical Response

LLM이 직접 답변을 생성하는 것이 아니라, Retrieval된 의료 문서를 기반으로 응답을 생성합니다.

### Included Evidence

* DailyMed SPL 문서
* Retrieval Context
* 의약품명 및 성분명
* 검색 근거 문서
* 문서 섹션 정보

이를 통해 사용자는 AI 응답의 근거를 직접 확인할 수 있습니다.

---

## 4. Multimodal Drug Identification

사용자는 텍스트뿐 아니라 알약 이미지를 통해서도 의료 질의를 수행할 수 있습니다.

Vision AI 기반 알약 식별 결과는 Retrieval을 수행하기 위한 입력 정보로 활용됩니다.

### Multimodal Flow

```text id="g9q4wg"
Pill Image
    ↓
Vision AI / OCR
    ↓
Drug Identification
    ↓
Medical Document Retrieval
    ↓
Context Injection
    ↓
LLM Response
```

---

## 5. Medical Document Chunking

수집한 의료 문서를 섹션 단위로 분할하여 RAG 검색에 적합한 형태로 Chunking합니다.

### Example Sections

* INDICATIONS AND USAGE
* DOSAGE AND ADMINISTRATION
* WARNINGS
* ADVERSE REACTIONS
* DRUG INTERACTIONS

---

## 6. Vector Database Retrieval

Chunking된 의료 문서를 Embedding하여 Vector Database에 저장하고 의미 기반 검색을 수행합니다.

### Supported Vector Databases

* FAISS
* ChromaDB

---

# RAG Pipeline

```text id="a48u1l"
User Query
    ↓
Drug Name Detection
    ↓
Medical Document Retrieval
    ↓
Relevant Context Extraction
    ↓
LLM Context Injection
    ↓
Grounded Medical Response
```

---

# System Architecture

```text id="pkfzt4"
                         ┌────────────────────┐
                         │ DailyMed API       │
                         └─────────┬──────────┘
                                   │
                         ┌─────────▼──────────┐
                         │ SPL XML Collection │
                         └─────────┬──────────┘
                                   │
                         ┌─────────▼──────────┐
                         │ XML Parsing        │
                         └─────────┬──────────┘
                                   │
                         ┌─────────▼──────────┐
                         │ Chunking           │
                         └─────────┬──────────┘
                                   │
                         ┌─────────▼──────────┐
                         │ Embedding          │
                         └─────────┬──────────┘
                                   │
                         ┌─────────▼──────────┐
                         │ Vector DB          │
                         └─────────┬──────────┘
                                   │
                         ┌─────────▼──────────┐
                         │ Retrieval          │
                         └─────────┬──────────┘
                                   │
                         ┌─────────▼──────────┐
                         │ LLM Generation     │
                         └────────────────────┘
```

---

# User Scenario

## Scenario 1. Text-Based Medical QA

1. 사용자가 의료 질문을 입력한다.
2. 시스템이 약품명 및 핵심 키워드를 분석한다.
3. 관련 의료 문서를 Retrieval한다.
4. 검색된 Context 기반으로 LLM 응답을 생성한다.
5. 사용자는 근거 기반 의료 정보를 확인한다.

---

## Scenario 2. Image-Based Medical QA

1. 사용자가 알약 이미지를 업로드한다.
2. Vision AI가 알약을 식별한다.
3. 의약품 정보를 기반으로 의료 문서를 Retrieval한다.
4. Retrieval된 Context를 기반으로 답변을 생성한다.
5. 사용자는 관련 의료 정보를 확인한다.

---

# Tech Stack

## LLM / RAG

* LangChain
* OpenAI API
* Sentence Transformers
* HuggingFace

---

## Vision AI

* YOLOv8
* OpenCV
* Pillow

---

## Vector Database

* FAISS
* ChromaDB

---

## Backend

* FastAPI
* Flask

---

## Frontend

* Streamlit

---

## Data Processing

* Pandas
* NumPy
* BeautifulSoup
* XML Parsing

---

# Expected Outcomes

* 의료 특화 RAG 구조 구현
* Grounded LLM 기반 의료 QA 시스템 개발
* Retrieval 기반 Explainable AI 검증
* Multimodal Medical AI 구조 설계
* 의료 데이터 기반 AI 서비스 확장 가능성 검증

---

# Future Extensions

* OCR 기반 약 봉투 인식
* 실시간 카메라 기반 질의응답
* 음성 기반 의료 QA
* 한국 의약품 데이터 확장
* 약물 상호작용 자동 분석
* 모바일 기반 의료 서비스화

---

# Team Members

| Name | Role                | Responsibility             |
| ---- | ------------------- | -------------------------- |
| 김소윤  | Vision AI Engineer  | 알약 이미지 인식 및 멀티모달 입력 구조 개발  |
| 김민욱  | RAG Engineer        | Retrieval 및 QA Pipeline 구현 |
| 심윤성  | Data Engineer       | 의료 문서 수집 및 전처리             |
| 김주영  | Frontend Engineer   | 사용자 인터페이스 개발               |
| Team | Medical AI Research | 의료 특화 RAG 시스템 설계 및 검증      |

---

# References

* Shape and Text Imprint Recognition of Pill Image Taken with a Smartphone
  https://s-space.snu.ac.kr/handle/10371/137361

---

# Disclaimer

This project is intended for academic and educational purposes only.

The medical information generated by this system should not be considered professional medical advice.

Always consult licensed medical professionals before taking any medication.
