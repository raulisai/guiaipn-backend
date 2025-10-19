---
trigger: manual
description: when code
---

# RULES.md — Guía de desarrollo backend (Flask / IA / SocketIO)

Este documento establece las **reglas y estándares obligatorios** para todo desarrollador que participe en el proyecto **Guía IPN**. Su propósito es mantener consistencia, calidad, seguridad y escalabilidad en el backend.

---

## 1. Principios generales

* **Separación de responsabilidades:** cada módulo tiene un propósito único (routes → services → repositories → models → utils).
* **Código limpio:** legible, documentado y sin duplicaciones.
* **Commit pequeño y atómico:** cada cambio debe cumplir una sola finalidad.
* **Automatización:** todo proceso repetible (tests, build, deploy) debe automatizarse.
* **Seguridad por diseño:** nunca exponer credenciales ni datos sensibles.

---

## 2. Estructura del proyecto

La estructura base es **obligatoria** y no debe modificarse sin aprobación técnica.

```
backend/
├── app/
│   ├── api/v1/                # Blueprints HTTP
|   |-- auth/
│   ├── socket_events/         # Eventos SocketIO
│   ├── services/              # Lógica de negocio
│   ├── repositories/          # Acceso a datos (Redis, Supabase)
│   ├── models/                # Schemas y modelos
│   ├── utils/                 # Funciones puras y helpers
│   ├── extensions.py          # Inicialización de dependencias
│   ├── config.py              # Configuraciones globales
│   └── __init__.py            # App factory
├── tests/                     # Unit & integration tests
├── run.py                     # Entry point
└── RULES.md                   # Este documento
```

---

## 3. Convenciones de código

### 3.1 Estilo

* Seguir **PEP8** y usar **Black** para formatear.
* Usar **snake_case** para funciones y variables, **PascalCase** para clases.
* Nombrar módulos y archivos en minúsculas, sin guiones.
* Documentar cada clase y función pública con docstrings breves.

### 3.2 Imports

* Ordenar: estándar → terceros → locales.
* Usar imports absolutos; evitar relativos como `from ..utils`.

### 3.3 Manejo de errores

* No lanzar excepciones genéricas (`Exception`), crear excepciones específicas.
* Capturar, loggear y devolver respuestas HTTP o eventos coherentes.
* No ocultar errores críticos con `try/except` vacíos.

### 3.4 Validaciones

* Todo endpoint debe validar payloads con **Pydantic** o similar.
* Ningún dato entra al sistema sin validación previa.

---

## 4. Commits y branches

### 4.1 Convenciones de commit

Usar el estándar **Conventional Commits**:

```
feat: nueva funcionalidad
fix: corrección de bug
docs: cambios en documentación
style: formato, espacios, puntos y comas
refactor: refactorización de código
perf: mejora de rendimiento
test: añadir o actualizar pruebas
chore: tareas de mantenimiento
```

Ejemplo: `feat(api): añadir endpoint /questions/ask`

### 4.2 Estrategia de ramas

* `main`: rama estable y desplegable.
* `develop`: rama de integración (opcional si hay equipo grande).
* `feature/<nombre>`: para nuevas funcionalidades.
* `fix/<nombre>`: para correcciones.

Antes de hacer merge a `main`, toda feature debe:

1. Pasar CI/CD.
2. Tener code review aprobado.
3. Estar probada localmente.

---

## 5. Estructura de un módulo

Cada módulo debe seguir este flujo:

**1. Controller (route)** → recibe la petición, valida datos y llama al service.
**2. Service** → aplica lógica de negocio y orquesta repositorios o IA.
**3. Repository** → acceso a datos (Supabase, Redis, etc.).
**4. Model / Schema** → valida la estructura de entrada/salida.

Ejemplo simplificado:

```py
# route
@bp.route('/ask', methods=['POST'])
def ask():
    data = AskQuestionSchema(**request.get_json())
    return jsonify(QuestionService.process_question(data.question))
```

---

## 6. Tests

### 6.1 Unit tests

* Cada service y repository debe tener pruebas unitarias.
* Usar mocks para dependencias externas (Redis, OpenAI, Supabase).
* Cobertura mínima: **70%**.

### 6.2 Integration tests

* Probar endpoints y flujos principales (Flask test client).
* Ejecutar en entorno aislado (Docker o contenedores de test).

### 6.3 Nomenclatura

* Archivos: `test_<nombre_modulo>.py`.
* Tests: `def test_<funcion>_when_<condicion>_then_<resultado>()`.

---

## 7. Seguridad

* Nunca subir `.env` al repo (solo `.env.example`).
* Las llaves y tokens se leen desde variables de entorno.
* Validar y sanitizar todos los inputs.
* Deshabilitar `DEBUG` en producción.
* Usar HTTPS en todos los entornos externos.
* Logs no deben contener datos sensibles.

---

## 8. Versionado de API (`v1`, `v2`, ...)

* **`v1`** es la versión inicial estable de la API.
* Cada cambio que **rompa compatibilidad** crea una nueva versión (`v2`).
* Estructura de ruta:

  * `/api/v1/questions/ask`
  * `/api/v2/...` (cuando haya breaking changes)

Ventajas:

* Permite actualizar clientes sin afectar versiones anteriores.
* Control de migraciones.

---

## 9. Documentación

* Cada endpoint debe tener descripción y ejemplo en **Swagger** u OpenAPI.
* README principal con:

  * Cómo levantar el entorno local.
  * Cómo correr tests.
  * Cómo desplegar.
* Añadir docstrings en todos los services y repositories.

---

## 10. CI/CD y despliegue

* El pipeline debe ejecutar en cada push:

  1. Linter (`flake8`, `black`).
  2. Tests unitarios.
  3. Tests de integración.
  4. Build de imagen Docker.

* Despliegue solo desde `main`.

* Staging y producción deben tener configuraciones separadas.

---

## 11. Logs y métricas

* Usar `logging` estándar con formato JSON.
* Nivel por defecto: `INFO`.
* Loggear request_id, endpoint, duración, errores.
* Configurar métricas Prometheus o similar (opcional en esta fase).

---

## 12. Definition of Done (DoD)

Una tarea se considera terminada cuando:

1. Cumple con los criterios de aceptación del issue.
2. Tiene tests unitarios e integración.
3. El código pasa linter y type checker.
4. Está documentada.
5. CI pasa.
6. Fue revisada y aprobada por otro desarrollador.

---

## 13. Checklist de PR

* [ ] Código formateado (Black)
* [ ] Tests ejecutados y pasan
* [ ] Validaciones completas
* [ ] Sin datos sensibles
* [ ] Commit message conforme al estándar
* [ ] Documentación actualizada

---

## 14. Contacto y soporte

Cualquier duda técnica o propuesta de mejora debe discutirse en el canal interno del equipo antes de modificar estas reglas.

**Responsable técnico:** Arquitecto backend o líder de proyecto.

---

> ⚙️ *Cumplir con estas reglas es obligatorio. Su incumplimiento puede bloquear merges o despliegues.*
