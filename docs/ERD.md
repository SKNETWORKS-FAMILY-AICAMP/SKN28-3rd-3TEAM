# MediPill ERD

## 테이블 목록

| 테이블명 | 설명 |
|----------|------|
| auth_user | Django 기본 사용자 테이블 |
| profiles_healthprofile | 사용자 건강정보 테이블 |
| chats_chathistory | 상담 이력 테이블 |

---

## User

| 컬럼 | 설명 |
|------|------|
| id | 사용자 ID |
| username | 로그인 ID |
| email | 이메일 |
| password | 암호화된 비밀번호 |
| date_joined | 가입일 |

---

## HealthProfile

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer | 건강정보 ID |
| user_id | FK | 사용자 ID |
| age | Integer | 나이 |
| gender | String | 성별 |
| height | Float | 키 |
| weight | Float | 체중 |
| allergies | Text | 알레르기 |
| diseases | Text | 기저질환 |
| current_medications | Text | 복용 중인 약물 |
| created_at | DateTime | 생성일 |
| updated_at | DateTime | 수정일 |

---

## ChatHistory

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer | 상담 이력 ID |
| user_id | FK | 사용자 ID |
| question | Text | 사용자 질문 |
| answer | Text | AI 답변 |
| created_at | DateTime | 생성일 |

---

## 관계

```text
User 1 ─── 1 HealthProfile

User 1 ─── N ChatHistory
```

## 설명

한 명의 사용자는 하나의 건강정보를 가진다.

한 명의 사용자는 여러 개의 상담 이력을 가질 수 있다.

사용자가 질문을 입력하면 시스템은 해당 사용자의 건강정보를 조회하고, 질문과 함께 LLM 프롬프트를 구성한다.

생성된 답변은 ChatHistory 테이블에 저장된다.