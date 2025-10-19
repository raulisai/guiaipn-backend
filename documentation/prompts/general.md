

architecture-guiaIpn

A — Prompts para el agente

Usa estos prompts como tasks para un agente. Cada prompt incluye el system (contexto) y user (tarea específica). Pega uno por uno en tu agente y ejecútalos en orden.

1) Inicializar repo + scaffold

System:

Eres un asistente desarrollador que crea scaffolds de backend en Python/Flask con buenas prácticas, tests y Docker. Sigue estrictamente la estructura de carpetas provista en la arquitectura y no cambies la lógica.

User:

Crea el scaffold del proyecto backend/ siguiendo esta estructura (app factory, config, extensions, blueprints, socket_events, services, repositories, models, utils, migrations, tests). Genera:

requirements.txt con Flask, Flask-SocketIO, redis, supabase-py, psycopg[binary], python-dotenv, pytest, black.

run.py que levante app y socketio.

app/__init__.py (app factory), app/config.py, app/extensions.py.

Dockerfile y docker-compose.yml que incluyan redis y postgres (supabase es externo, pero incluye postgres para dev).
Añade README.md con comandos para levantar en dev. Devuelve solo archivos (path + contenido).

2) Implementar Auth (Supabase token validation)

System:

Eres un backend engineer que implementa validación JWT con Supabase en Flask-SocketIO.

User:

Implementa app/auth/supabase.py con:

función verify_token(token: str) -> dict | None que valida con Supabase REST /auth/v1/user o usa la librería supabase (prefiere service key desde env).

decorator @require_auth_socket para usar en handlers de Socket.IO (que valide auth.token en connect).
Añade tests unitarios tests/unit/test_auth.py. Devuelve código y tests.

3) SessionService y Redis

System:

Eres un backend engineer experto en Redis para sesiones.

User:

Implementa app/services/session_service.py y app/repositories/session_repository.py que:

creen/obtengan/actualicen sesiones en Redis con TTL 1800s siguiendo el formato session:{session_id} de tu arquitectura.

funciones: create_session(user_id), get_session(session_id), update_session(session_id, data), renew_ttl(session_id).
Incluye manejo de conexión Redis en app/extensions.py y tests de integración (usa fakeredis).

4) QuestionService + utils text_processing

System:

Eres un ingeniero de NLP ligero: normalización y hash.

User:

Implementa app/services/question_service.py y app/utils/text_processing.py:

normalize_text(text) (lowercase, unaccent, remove punctuation, collapse spaces).

generate_hash(text) SHA256.

QuestionService.process_question(user_id, question_text) que: valida, normaliza, genera hash, busca en Supabase (o tabla local predefined_answers si en dev), devuelve cached answer id o None. No generes IA aún. Añade tests.

5) AIService (OpenAI) — generador estructurado

System:

Eres un integrador de APIs IA que produce respuestas JSON estructuradas.

User:

Implementa app/services/ai_service.py con:

build_prompt(question, context) que devuelva prompt system+user solicitando formato JSON: {"steps":[{"title":"", "type":"text|image|math", "content":"", "canvas_commands": []}], "total_duration": 120}.

generate_answer(question, context) que llame a OpenAI (env OPENAI_API_KEY) con completions/ChatCompletions y parse JSON seguro. Si la respuesta no es JSON válido, intenta reparación (2 intentos) y si falla, lanza excepción.
Añade test que simule la respuesta de OpenAI con responses o unittest.mock.

6) StreamingService + Socket handlers (ask_question flow)

System:

Eres un desarrollador de tiempo real con Flask-SocketIO.

User:

Implementa app/socket_events/questions.py y app/services/streaming_service.py:

Handler @socket.on('ask_question') que recibe {'question':..., 'context':...}; verifica rate limit, llama a QuestionService.process_question.

Si existe cached answer: llama StreamingService.start_streaming(answer, session_id) que emite explanation_start, step_start, content_chunk, canvas_command y step_complete, explanation_complete.

Si no existe: emite waiting_phrase, llama AIService.generate_answer, guarda en DB (predefined_answers), luego stream.

Implementa pausas (pause_explanation) y resume (resume_explanation) que actualizan Redis y controlan envío.
Añade tests de socket (pytest-socketio).

7) Credit usage + consume_credits

System:

Eres un ingeniero de backend que implementa control monetización/credits.

User:

Implementa app/services/credit_service.py y app/repositories/credit_repository.py:

check_credits(user_id, credits_needed) consulta profiles en Supabase; en dev usa mock.

consume_credits(user_id, credits, action_type, interaction_id=None) actualiza profiles vía Supabase service key y crea registro en credit_usage.
Manejo de errores y rollback si falla guardar credit_usage. Incluye tests.

8) Migrations SQL + seed

System:

Eres un DBA que genera scripts SQL compatibles con Supabase (Postgres).

User:

Genera los archivos migrations/001_create_tables.sql, 002_add_indexes.sql, 003_seed_data.sql exactamente con el esquema que entregué (no cambiar nada). Incluye predefined_answers y voice_interactions. Devuelve los SQL.

(Cita: el esquema completo está en el archivo de arquitectura). 

architecture-guiaIpn

9) Tests, CI, Docker Compose

System:

Eres un devops que crea pipeline CI y docker compose.

User:

Añade:

pytest config y ejemplos de tests (unit + integration).

.github/workflows/ci.yml que: instale deps, ejecute linters (black), pytest, y build docker image.

docker-compose.yml con servicios: backend, redis, postgres (volúmenes), traefik opcional.
Devuelve archivos.

10) Commit-by-commit plan prompt (para agente multi-step)

System:

Eres un agente que hace commits atómicos y crea PRs.

User:

Genera una lista de commits atómicos (mensajes y archivos) para implementar todo lo anterior en orden. Limítate a 15 commits (scaffold, auth, redis, question service, ai service, streaming, credits, migrations, tests, docker, ci, docs). Devuélvelos como JSON: [{ "commit": "001-init-scaffold", "files": ["..."], "message":"..." }, ...].

B — Plan paso a paso (ejecutable)

Sigue este checklist en tu repo local. No pido confirmación — hazlos en orden.

Requisitos locales: Python 3.11+, Docker, docker-compose, Redis (para dev si no usas Docker).

Inicializar repo

git init

Añadir backend/ con scaffold (usa Prompt 1).

Crear virtualenv: python -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt

Docker / compose

Añade docker-compose.yml con servicios backend, redis, postgres (dev).

docker-compose up --build para probar.

App factory + extensions

Implementa app/__init__.py, app/extensions.py (socketio init, redis client, supabase client).

Añade run.py que carga env y arranca socketio.

Auth

Implementa app/auth/supabase.py y decorator/handler de connect.

Test: simular token inválido y válido (mock Supabase).

Redis SessionService

Implementa session_repository + SessionService (usar fakeredis en tests).

Asegura TTL 1800s.

Text utils + QuestionService

normalize_text y generate_hash.

QuestionService.process_question: buscar en predefined_answers (migración) por hash.

Migrations y seed (SQL)

Añade migrations/001_create_tables.sql y aplicar en dev Postgres.

Seed de suscripciones y ejemplo de pregunta.

AIService (OpenAI)

Implementa prompt builder y wrapper; en dev mockea llamadas a OpenAI.

Añade manejo de errores y reparacion de JSON.

StreamingService + socket handlers

Implementa ask_question, streaming chunk emitter, pause/resume, voice_start/voice_complete.

Asegura que todos los emits coincidan con tu especificación de payloads.

Credit service

Implementa check_credits + consume_credits, integrándolo en ask_question antes de procesar.

Voice flow

Implementa endpoints handlers voice_start/voice_complete que acepten base64, guarden temporalmente y llamen a VoiceService.transcribe_audio. (MVP: accept pre-transcribed text for dev).

DB writes (predefined_answers, interaction_history, voice_interactions, credit_usage)

Insertar cuando corresponda; asegura RLS y usar service key para writes.

Tests

Unit tests por servicio, handlers y integración SocketIO (pytest + pytest-asyncio si necesario).

Cobertura mínima: critical services (session, question, ai, streaming, credits).

CI/CD

Añadir GitHub Actions: lint (black), tests, build docker image.

Deploy: opción simple -> Docker image en DigitalOcean / Render / Railway; o usar Supabase Functions para endpoints si quieres offload.

Observabilidad y métricas

Logs estructurados (json) y Sentry/Prometheus opcional.

Exponer /healthz y metrics.

Documentación

Actualiza README.md con env vars list, pasos para dev, endpoints de socket y payload examples (usa lo del archivo). 

architecture-guiaIpn

Producción

Reemplaza Postgres dev por Supabase (aplicar migrations), configurar SUPABASE_SERVICE_KEY, asegurar RLS y policies.

Configurar secretos en CI/CD y rotación de keys.

B.1 — Checklist rápido (marcable)

 Scaffold + Docker ✅

 Auth + connect validation ✅

 Redis SessionService ✅

 Text utils + QuestionService ✅

 Migrations SQL aplicadas ✅

 AIService con manejo robusto ✅

 StreamingService + pause/resume ✅

 Credit usage integrado ✅

 Voice transcription MVP ✅

 Tests y CI ✅

 Deploy a staging ✅

B.2 — Comandos útiles (copiar/pegar)
# crear entorno
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# lint y tests
black .
pytest -q

# correr en dev (local)
export FLASK_ENV=development
export SUPABASE_URL=...
export SUPABASE_KEY=...
export OPENAI_API_KEY=...
python run.py

# docker
docker-compose up --build
