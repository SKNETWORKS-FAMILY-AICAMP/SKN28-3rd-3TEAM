# MediPill AI

## Explainable Medical RAG System with Pill Image Recognition

MediPill AI는 공식 의약품 데이터와 Vision AI를 결합한 멀티모달 의료 질의응답 시스템입니다.
Retrieval-Augmented Generation(RAG) 기반 구조를 통해 생성형 AI의 Hallucination 문제를 줄이고, 근거 기반 의료 정보를 제공하는 것을 목표로 합니다.

---

# Introduction

기존 생성형 AI 기반 의료 질의응답 시스템은 다음과 같은 한계를 가질 수 있습니다.

* 출처가 불분명한 답변 생성
* 최신 의약품 정보 반영 한계
* 설명 가능성 부족
* 이미지 기반 의약품 식별 불가

MediPill AI는 이러한 문제를 해결하기 위해 공식 의약품 데이터베이스(DailyMed, RxNav)를 기반으로 Retrieval 구조를 구성하였으며, Vision AI 기반 알약 이미지 인식 기능을 결합하여 신뢰 가능한 의료 질의응답 시스템을 구현하고자 하였습니다.

---

# Project Objectives

* 의료 분야 Hallucination 최소화
* 공식 의약품 문서 기반 QA 시스템 구축
* Retrieval 기반 Explainable AI 구현
* DailyMed 기반 의료 문서 RAG 구축
* Vision 기반 알약 이미지 인식 기능 구현
* RxNav 기반 실제 의약품 정보 매핑
* 이미지 기반 의료 질의응답 확장

---

# Core Features

## 1. Medical RAG Question Answering

사용자의 자연어 질문을 분석하여 관련 의약품 문서를 검색하고, 검색된 의료 문서를 기반으로 답변을 생성합니다.

### Example Queries

```text
- 타이레놀 공복 복용 가능한가요?
- 대표적인 부작용은 무엇인가요?
- 어린이도 복용 가능한 약인가요?
- 약물 상호작용이 있나요?
```

---

## 2. DailyMed-Based Retrieval

FDA/NLM 공식 의약품 데이터베이스인 DailyMed를 기반으로 Retrieval을 수행합니다.

### Retrieved Information

* 효능 및 효과
* 용법 및 용량
* 경고 및 주의사항
* 금기사항
* 부작용
* 약물 상호작용
* 보관 방법

---

## 3. Explainable Medical AI

LLM이 직접 답변을 생성하는 것이 아니라, 검색된 의료 문서를 기반으로 응답을 생성합니다.

### Included Evidence

* DailyMed SPL 문서
* Retrieval Context
* 의약품명 및 성분명
* 문서 섹션 정보
* 검색 근거 문서

이를 통해 사용자는 AI 응답의 근거를 직접 확인할 수 있습니다.

---

## 4. Pill Image Recognition

사용자가 알약 이미지를 업로드하면 Vision AI 모델이 알약을 분류하고 실제 의약품 정보를 추정합니다.

### Vision-Based Identification Flow

```text
Pill Image
    ↓
YOLOv8 Classification
    ↓
NDC Code Extraction
    ↓
RxNav Drug Mapping
    ↓
DailyMed Retrieval
    ↓
Medical RAG Response
```

---

## 5. RxNav Drug Mapping

YOLO 모델의 예측 결과에서 NDC 코드를 추출한 뒤 RxNav API를 활용하여 실제 의약품 정보를 매핑합니다.

### Example

```text
Prediction Label:
00093-0148-01_4629A34D

↓

Mapped Drug:
Fluoxetine 10 MG Oral Tablet
```

---

## 6. Medical Document Chunking

수집한 SPL XML 문서를 섹션 단위로 분할하고 RAG 검색에 적합한 형태로 Chunking합니다.

### Example Sections

* INDICATIONS AND USAGE
* DOSAGE AND ADMINISTRATION
* WARNINGS
* ADVERSE REACTIONS
* DRUG INTERACTIONS

---

## 7. Vector Database Retrieval

Chunking된 의료 문서를 Embedding하여 Vector Database에 저장하고 의미 기반 검색을 수행합니다.

### Supported Vector Databases

* FAISS
* ChromaDB

---

# System Architecture

```text
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
                         │ Vector DB (FAISS)  │
                         └────────────────────┘


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


User Question / Pill Image
              ↓
 Retrieval & Drug Mapping
              ↓
 Context Construction
              ↓
 LLM Response Generation
              ↓
 Grounded Medical Answer
```

---

# Tech Stack

## AI / NLP

* Python
* LangChain
* OpenAI API
* HuggingFace
* Sentence Transformers

---

## Vision AI

* YOLOv8
* OpenCV
* Pillow

---

## Medical APIs

* RxNav API
* DailyMed API
* openFDA API

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
* Regular Expression

---

# Dataset & Medical Sources

## Medical Sources

* DailyMed
* RxNav
* openFDA

---

## Vision Dataset

* ePillID Benchmark Dataset

---

# RAG Pipeline

```text
User Query
    ↓
Drug Name Detection
    ↓
Relevant Medical Document Retrieval
    ↓
Context Injection
    ↓
LLM Response Generation
    ↓
Grounded Response with Evidence
```

---

# Project Structure

```text
MediPill-AI/
│
├── models/
│   ├── yolo/
│   └── embeddings/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── dailymed_xml/
│   └── chunks/
│
├── vector_db/
│   └── faiss/
│
├── scripts/
│   ├── rxnav_mapping/
│   ├── dailymed_collect/
│   ├── xml_parser/
│   └── vector_build/
│
├── app/
│   ├── rag/
│   ├── vision/
│   ├── api/
│   └── ui/
│
└── README.md
```

---

# Future Extensions

* OCR 기반 약 봉투 인식
* 실시간 카메라 기반 알약 탐지
* 다국어 의료 질의응답
* 복약 스케줄 관리
* 음성 기반 의료 QA
* 모바일 앱 서비스화
* 한국 의약품 데이터베이스 확장
* 약물 상호작용 자동 분석

---

# Expected Outcomes

* 공식 의료 데이터를 활용한 RAG 구조 구현
* Vision AI와 의료 QA의 멀티모달 결합 실험
* Explainable AI 기반 의료 질의응답 시스템 개발
* 의료 데이터 기반 AI 서비스 확장 가능성 검증

---

# Team Members

| Name               | Role                | Responsibility                   |
| ------------------ | ------------------- | -------------------------------- |
| 김소윤                | Vision AI Engineer  | YOLO 기반 알약 이미지 인식 및 OCR 파이프라인 개발 |
| 김민욱                | RAG Engineer        | Retrieval 및 QA Pipeline 구현       |
| 심윤성                | Data Engineer       | 의료 문서 수집 및 전처리                   |
| 김민욱                | Backend Engineer    | API 및 서버 개발                      |
| 김주영                | Frontend Engineer   | 사용자 인터페이스 개발                     |
| 김민욱, 김소윤, 김주영, 심윤성 | Medical AI Research | 의료 문서 기반 AI 연구 및 시스템 설계          |

---

# References

* Shape and Text Imprint Recognition of Pill Image Taken with a Smartphone
  https://s-space.snu.ac.kr/handle/10371/137361

---

# Disclaimer

This project is intended for academic and educational purposes only.

The medical information generated by this system should not be considered professional medical advice.

Always consult licensed medical professionals before taking any medication.
