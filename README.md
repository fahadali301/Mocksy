# Mocksy API

## Dynamic CV Interview Flow

The interview is now stateful and dynamic:
- Upload CV first (extracts and stores CV text)
- Start interview to get the first AI question
- Send answers turn-by-turn
- Send `exit` as answer to finish and receive final evaluation for all answers

## Endpoints

### 1) Upload CV
`POST /cv/upload`

Returns CV metadata and preview text.

### 2) Start Interview
`POST /interview/start`

Request body:
```json
{
  "cv_id": 1,
  "role": "Backend Developer"
}
```

Response:
```json
{
  "interview_id": 12,
  "status": "active",
  "next_question": "Tell me about the API project you listed on your CV..."
}
```

### 3) Submit Turn (Continue or Exit)
`POST /interview/turn`

Request body (continue):
```json
{
  "interview_id": 12,
  "answer": "I used FastAPI with PostgreSQL and JWT auth..."
}
```

Continue response:
```json
{
  "interview_id": 12,
  "status": "active",
  "next_question": "How did you handle database migrations in that project?"
}
```

Request body (exit):
```json
{
  "interview_id": 12,
  "answer": "exit"
}
```

Exit response:
```json
{
  "interview_id": 12,
  "status": "completed",
  "result": {
    "overall_score": 7,
    "summary": "Good understanding with room to improve depth.",
    "strengths": ["API design", "practical examples"],
    "improvements": ["deeper system design", "testing detail"]
  }
}
```

## Auth
All protected endpoints require:
`Authorization: Bearer <token>`

