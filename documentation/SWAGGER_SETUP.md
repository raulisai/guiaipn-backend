# Configuración de Swagger

## Instalación

Para habilitar la documentación Swagger en el proyecto, instala la nueva dependencia:

```bash
pip install flask-swagger-ui==4.11.1
```

O instala todas las dependencias actualizadas:

```bash
pip install -r requirements.txt
```

## Acceso a la Documentación

Una vez que el servidor esté corriendo:

```bash
python run.py
```

Accede a la documentación interactiva en:

```
http://localhost:5000/api/docs
```

## Características Implementadas

✅ **Swagger UI integrado** - Interfaz interactiva para explorar la API  
✅ **Especificación OpenAPI 3.0.3** - Estándar de la industria  
✅ **Documentación completa** - Todos los endpoints actuales documentados  
✅ **Autenticación JWT** - Soporte para probar endpoints protegidos  
✅ **Esquemas de datos** - Modelos de request/response definidos  
✅ **Ejemplos incluidos** - Requests y responses de ejemplo  
✅ **Tags organizados** - Endpoints agrupados por funcionalidad  

## Endpoints Documentados

### Health Check
- `GET /health`

### Autenticación
- `POST /api/v1/auth/verify` - Verificar token JWT
- `GET /api/v1/auth/profile` - Obtener perfil (requiere auth)

### Preguntas
- `GET /api/v1/questions/` - Listar preguntas (con paginación)
- `GET /api/v1/questions/{question_id}` - Obtener pregunta específica

### Sesiones
- `GET /api/v1/sessions/` - Listar sesiones (requiere auth)
- `GET /api/v1/sessions/{session_id}` - Obtener sesión específica (requiere auth)

## Cómo Probar Endpoints Protegidos

1. **Obtén un token JWT válido** desde Supabase
2. En Swagger UI, haz clic en el botón **"Authorize"** (candado verde en la esquina superior derecha)
3. Ingresa el token en el formato: `Bearer <tu-token-aqui>`
4. Haz clic en **"Authorize"** y luego **"Close"**
5. Ahora puedes probar los endpoints que requieren autenticación

## Actualizar la Documentación

Para agregar o modificar la documentación de endpoints:

1. Edita el archivo `app/api/openapi.yaml`
2. Reinicia el servidor Flask
3. Recarga la página de Swagger UI

### Ejemplo: Agregar un nuevo endpoint

```yaml
paths:
  /api/v1/nuevo-endpoint:
    get:
      summary: Descripción breve
      description: Descripción detallada del endpoint
      tags:
        - nombre-del-tag
      responses:
        '200':
          description: Respuesta exitosa
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: string
```

## Archivos Relacionados

- `app/api/openapi.yaml` - Especificación OpenAPI completa
- `app/api/swagger.py` - Configuración de Swagger UI
- `app/api/README.md` - Documentación detallada de la API
- `app/__init__.py` - Integración de Swagger en la app Flask

## Recursos Adicionales

- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI Documentation](https://swagger.io/tools/swagger-ui/)
- [Flask-Swagger-UI](https://github.com/sveint/flask-swagger-ui)

## Troubleshooting

### Swagger UI no carga

1. Verifica que el servidor esté corriendo
2. Verifica que `flask-swagger-ui` esté instalado
3. Revisa los logs del servidor para errores

### El archivo openapi.yaml no se encuentra

1. Verifica que el archivo exista en `app/api/openapi.yaml`
2. Verifica que la ruta en `swagger.py` sea correcta
3. Reinicia el servidor

### Los cambios no se reflejan

1. Reinicia el servidor Flask
2. Limpia la caché del navegador (Ctrl+Shift+R)
3. Verifica que el archivo YAML tenga sintaxis válida
