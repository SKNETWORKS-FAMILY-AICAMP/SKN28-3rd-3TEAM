# MediPill AI

MediPill AI는 한국 의약품 문서 데이터를 기반으로 사용자의 의약품/증상 관련 질문에 답변하는 RAG 기반 챗봇입니다.

사용자 질문을 그대로 LLM에 전달하는 방식이 아니라, 수집된 의약품 문서를 검색한 뒤 검색 결과를 근거로 답변을 생성합니다. 이를 통해 답변의 근거를 명확히 하고, 의료/의약품 분야에서 발생할 수 있는 부정확한 답변을 줄이는 것을 목표로 합니다.

> 본 프로젝트는 학습 및 프로젝트 목적의 참고 정보 제공 시스템입니다. 진단, 처방, 복용 지시를 대체하지 않습니다.

---

## 주요 기능

- 한국 의약품 문서 기반 질의응답
- 증상 기반 일반의약품 상담 방향 안내
- 의약품명, 증상, 대상자 조건을 고려한 문서 검색
- FAISS 벡터 검색과 BM25 키워드 검색을 함께 사용하는 Hybrid Retrieval
- 검색된 문서를 LLM이 다시 선별한 뒤 답변 생성
- Chainlit 기반 챗봇 UI 제공
- 답변을 표 형태로 정리하여 사용자 가독성 개선

---

## 데이터 및 전처리

### 데이터 구성

현재 프로젝트에는 한국 의약품 관련 원천 데이터와 전처리 데이터가 포함되어 있습니다.

```text
data/raw/
data/processed/
vectorstore/faiss_index/
```

- `data/raw/`: 수집된 원천 XML/CSV 데이터
- `data/processed/`: RAG 검색에 사용할 수 있도록 정리된 JSON 문서
- `vectorstore/faiss_index/`: 전처리 문서를 임베딩하여 저장한 FAISS 인덱스

### 전처리 방식

수집된 문서는 제품명, 출처, URL, 제조사 등 메타데이터와 본문 내용을 포함하는 형태로 정리됩니다.

RAG 검색을 위해 문서 본문은 chunk 단위로 분할됩니다.

```python
chunk_size = 1000
chunk_overlap = 100
```

- `chunk_size`: 한 번에 임베딩할 문서 조각의 최대 크기
- `chunk_overlap`: 문맥이 끊기지 않도록 앞뒤 chunk가 겹치는 범위

chunk로 나눈 문서는 OpenAI Embedding 모델을 통해 벡터화한 뒤 FAISS에 저장합니다.

---

## 시스템 아키텍처

현재 RAG 흐름은 다음과 같습니다.

```text
사용자 질문
    ↓
질문 분석
    ↓
검색 계획 생성
    ↓
FAISS 벡터 검색 + BM25 키워드 검색
    ↓
검색 문서 후보 수집
    ↓
LLM 기반 문서 선택
    ↓
선택된 문서 기반 답변 생성
    ↓
Chainlit UI로 답변 출력
```

### 구성 요소

| 구성 요소 | 역할 |
|---|---|
| Query Analyzer | 사용자 질문의 의도, 약 이름, 증상, 대상 조건을 분석 |
| Retrieval Planner | 검색에 사용할 질의어와 확장 검색어 생성 |
| FAISS Retriever | 임베딩 기반 의미 검색 수행 |
| BM25 Retriever | 키워드 기반 검색 수행 |
| Document Selector | 검색된 문서 중 답변 근거로 사용할 문서 선별 |
| Answer Generator | 선택된 문서를 근거로 최종 답변 생성 |
| Chainlit UI | 사용자가 질문하고 답변을 확인하는 챗봇 화면 제공 |

---

## 답변 형식

답변은 사용자가 쉽게 확인할 수 있도록 다음 구조로 출력됩니다.

- 질문 유형
- 핵심 답변
- 확인된 정보
- 복용 전 체크표
- 추가로 확인하면 좋은 질문
- 참고 출처
- 주의 문구

특히 의약품 정보, 약국 상담 가능 약 종류, 추가 확인 항목은 표 형태로 제공하여 가독성을 높였습니다.

---

## 실행 방법

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 만들고 OpenAI API Key를 설정합니다.

```text
OPENAI_API_KEY=your_api_key
```

### 3. 벡터 DB 생성

전처리된 문서를 기반으로 FAISS 벡터 DB를 생성합니다.

```bash
python src/build_vector_db.py
```

실행하면 원본 문서 수와 분할된 chunk 수가 출력됩니다.

### 4. Chainlit 앱 실행

```bash
chainlit run src/app_chainlit.py
```

실행 후 브라우저에서 Chainlit 챗봇 화면을 통해 질문할 수 있습니다.

---

## 주요 파일

| 파일 | 설명 |
|---|---|
| `src/collect_korea_drug.py` | 한국 의약품 데이터 수집 스크립트 |
| `src/build_vector_db.py` | 전처리 문서를 chunk로 나누고 FAISS 인덱스를 생성 |
| `src/rag_chain.py` | 질문 분석, 검색 계획, 문서 검색, 답변 생성 흐름 구현 |
| `src/rag_prompts.py` | 질문 분석/검색 계획/답변 생성을 위한 프롬프트 |
| `src/rag_utils.py` | 문서 로드, 검색 결과 정리, 출처 생성 등 유틸 함수 |
| `src/app_chainlit.py` | Chainlit 챗봇 UI 및 최종 답변 포맷 구성 |

---

## 기술 스택

- Python
- Chainlit
- LangChain
- OpenAI API
- FAISS
- BM25 Retriever
- python-dotenv

---

## 팀원

| 이름 | 역할 |
|---|---|
| 김소윤 | Vision AI / UI |
| 김민욱 | RAG Pipeline |
| 심윤성 | Data Collection / Preprocessing |
| 김주영 | Frontend / Chat UI |

---

## Disclaimer

본 시스템의 답변은 의료 문서 기반 참고 정보입니다.

정확한 진단, 처방, 복용 가능 여부 판단은 의사 또는 약사와 상담해야 합니다.
