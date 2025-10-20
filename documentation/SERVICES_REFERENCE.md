# 🛠️ Referencia de Servicios

## AIService

**Ubicación:** `app/services/ai_service.py`

```python
class AIService:
    def generate_answer(question: str, context: dict) -> dict
    def generate_exam_explanation(question: dict, user_answer: str) -> dict
    def generate_clarification(question: str, context: dict) -> dict
    def generate_follow_up(question: str, original: dict, previous: dict) -> dict
```

## StreamingService

**Ubicación:** `app/services/streaming_service.py`

```python
class StreamingService:
    CHUNK_SIZE = 50
    CHUNK_DELAY = 0.05
    
    def start_streaming(answer_data: dict, session_id: str)
    def resume_streaming(session_id: str, answer_data: dict)
    def stream_explanation(explanation: dict, emit_func)
    def stream_answer(answer: dict, emit_func)
```

## SessionService

**Ubicación:** `app/services/session_service.py`

```python
class SessionService:
    DEFAULT_TTL = 1800  # 30 minutos
    
    def create_session(user_id: str, connection_id: str) -> str
    def get_session(session_id: str) -> dict
    def update_session(session_id: str, data: dict) -> bool
    def end_session(session_id: str) -> bool
    def pause_streaming(session_id: str, position: int) -> bool
    def resume_streaming(session_id: str) -> dict
```

## QuestionService

**Ubicación:** `app/services/question_service.py`

```python
class QuestionService:
    MIN_QUESTION_LENGTH = 5
    MAX_QUESTION_LENGTH = 1000
    
    def validate_question(question_text: str)
    def process_question(user_id: str, question_text: str) -> dict
    def get_cached_answer(question_hash: str) -> dict | None
```

## Repositorios

### SessionRepository
```python
def create(session_id: str, data: dict, ttl: int)
def get(session_id: str) -> dict | None
def update(session_id: str, data: dict, ttl: int)
def delete(session_id: str) -> bool
def exists(session_id: str) -> bool
```

### AIAnswersRepository
```python
def create(data: dict) -> dict
def get_by_hash(question_hash: str) -> dict | None
def increment_usage(answer_id: str)
```

### QuestionRepository
```python
def get_by_id(question_id: str) -> dict | None
def get_by_subject(subject: str, limit: int) -> list
def get_random(subject: str, difficulty: str) -> dict | None
```
