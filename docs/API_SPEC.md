# MediPill API 명세서

## Base URL

```text
http://127.0.0.1:8000
```

## 인증 방식

JWT Bearer Token

```text
Authorization: Bearer {access_token}
```

---

## 1. 회원가입

### POST /api/accounts/signup/

### Request

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "1234"
}
```

### Response

```json
{
  "message": "회원가입이 완료되었습니다.",
  "user_id": 1
}
```

---

## 2. 로그인

### POST /api/token/

### Request

```json
{
  "username": "testuser",
  "password": "1234"
}
```

### Response

```json
{
  "refresh": "refresh_token",
  "access": "access_token"
}
```

---

## 3. 건강정보 등록

### POST /api/profile/

### Header

```text
Authorization: Bearer {access_token}
```

### Request

```json
{
  "age": 24,
  "gender": "FEMALE",
  "height": 162.5,
  "weight": 52.0,
  "allergies": "페니실린",
  "diseases": "없음",
  "current_medications": "없음"
}
```

### Response

```json
{
  "message": "건강정보가 저장되었습니다.",
  "profile": {
    "id": 1,
    "age": 24,
    "gender": "FEMALE",
    "height": 162.5,
    "weight": 52.0,
    "allergies": "페니실린",
    "diseases": "없음",
    "current_medications": "없음"
  }
}
```

---

## 4. 건강정보 조회

### GET /api/profile/

### Header

```text
Authorization: Bearer {access_token}
```

### Response

```json
{
  "id": 1,
  "age": 24,
  "gender": "FEMALE",
  "height": 162.5,
  "weight": 52.0,
  "allergies": "페니실린",
  "diseases": "없음",
  "current_medications": "없음"
}
```

---

## 5. 건강정보 수정

### PUT /api/profile/

### Header

```text
Authorization: Bearer {access_token}
```

### Request

```json
{
  "age": 25,
  "gender": "FEMALE",
  "height": 162.5,
  "weight": 53.0,
  "allergies": "페니실린",
  "diseases": "없음",
  "current_medications": "철분제"
}
```

---

## 6. 채팅 요청

### POST /api/chat/

### Header

```text
Authorization: Bearer {access_token}
```

### Request

```json
{
  "question": "Can I take Tylenol on an empty stomach?"
}
```

### Response

```json
{
  "id": 1,
  "question": "Can I take Tylenol on an empty stomach?",
  "answer": "LLM 또는 데모 응답"
}
```

---

## 7. 상담 이력 조회

### GET /api/chat/history/

### Header

```text
Authorization: Bearer {access_token}
```

### Response

```json
[
  {
    "id": 1,
    "question": "Can I take Tylenol on an empty stomach?",
    "answer": "LLM 또는 데모 응답",
    "created_at": "2026-06-16T13:00:00+09:00"
  }
]
```