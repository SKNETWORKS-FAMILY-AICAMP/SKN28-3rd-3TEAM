# API 테스트 결과 정리

## 1. 테스트 목적

MediPill 백엔드 API가 정상적으로 동작하는지 확인하기 위해 회원가입, 로그인, 건강정보 등록 및 조회, 채팅 요청, 상담 이력 조회 기능을 테스트하였다.

---

## 2. 테스트 환경

- Backend Framework: Django
- API Framework: Django REST Framework
- 인증 방식: JWT
- DB: SQLite
- 테스트 도구: PowerShell Invoke-RestMethod
- 서버 주소: http://127.0.0.1:8000

---

## 3. API 테스트 결과

| 번호 | 기능 | Method | URL | 테스트 결과 |
|---|---|---|---|---|
| 1 | 회원가입 | POST | /api/accounts/signup/ | 성공 |
| 2 | 로그인/JWT 발급 | POST | /api/token/ | 성공 |
| 3 | 건강정보 등록 | POST | /api/profile/ | 성공 |
| 4 | 건강정보 조회 | GET | /api/profile/ | 성공 |
| 5 | 채팅 요청 | POST | /api/chat/ | 성공 |
| 6 | 상담 이력 조회 | GET | /api/chat/history/ | 성공 |

---

## 4. 상세 테스트 내용

### 4.1 회원가입 API

요청 URL:
POST /api/accounts/signup/

요청 데이터:
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "1234"
}

결과:
회원가입이 정상적으로 완료되었으며 user_id가 반환되었다.

---

### 4.2 로그인 API

요청 URL:
POST /api/token/

요청 데이터:
{
  "username": "testuser",
  "password": "1234"
}

결과:
access token과 refresh token이 정상적으로 발급되었다.

---

### 4.3 건강정보 등록 API

요청 URL:
POST /api/profile/

인증:
Bearer Access Token

요청 데이터:
{
  "age": 24,
  "gender": "FEMALE",
  "height": 162.5,
  "weight": 52.0,
  "allergies": "페니실린",
  "diseases": "없음",
  "current_medications": "없음"
}

결과:
로그인한 사용자 기준으로 건강정보가 정상 저장되었다.

---

### 4.4 건강정보 조회 API

요청 URL:
GET /api/profile/

인증:
Bearer Access Token

결과:
저장된 사용자의 나이, 성별, 키, 체중, 알레르기, 기저질환, 복용 중인 약물 정보가 정상 조회되었다.

---

### 4.5 채팅 API

요청 URL:
POST /api/chat/

인증:
Bearer Access Token

요청 데이터:
{
  "question": "Can I take Tylenol on an empty stomach?"
}

결과:
사용자 질문을 받아 건강정보 기반 프롬프트를 생성하고, 답변 생성 로직까지 정상 실행되었다. 생성된 질문과 답변은 상담 이력 테이블에 저장되었다.

---

### 4.6 상담 이력 조회 API

요청 URL:
GET /api/chat/history/

인증:
Bearer Access Token

결과:
사용자의 이전 질문과 답변 내역이 정상적으로 조회되었다.

---

## 5. LLM 연동 테스트 결과

OpenAI API 키를 .env 파일에 저장하고 Django 서버에서 환경변수로 불러오는 것까지 성공하였다.

다만 실제 OpenAI API 호출 시 다음 오류가 발생하였다.

Error code: 429 - insufficient_quota

이는 코드 오류가 아니라 OpenAI API 사용량 또는 결제 한도 문제로 발생한 오류이다. 따라서 현재 프로젝트에서는 LLM 호출 구조를 구현한 뒤, 발표용 데모에서는 예시 응답을 반환하는 방식으로 처리하였다.

---

## 6. 테스트 결론

MediPill 백엔드의 핵심 API인 회원가입, 로그인, 건강정보 등록 및 조회, 채팅 요청, 상담 이력 저장 및 조회 기능은 정상적으로 동작하였다.

LLM 연동의 경우 API 키 로드 및 호출 구조까지 구현되었으며, 실제 응답 생성은 API 사용량 제한으로 인해 데모 응답 방식으로 대체하였다.

따라서 현재 백엔드는 프론트엔드와 연동 가능한 수준의 MVP 기능을 갖추었다.