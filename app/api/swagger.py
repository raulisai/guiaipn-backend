"""
Configuración de Swagger UI para documentación de API
"""
from flask import send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import os


def init_swagger(app):
    """
    Inicializa Swagger UI en la aplicación Flask
    """
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/openapi.yaml'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "GuiaIPN API",
            'docExpansion': 'list',
            'defaultModelsExpandDepth': 3,
            'displayRequestDuration': True,
            'filter': True,
            'showExtensions': True,
            'showCommonExtensions': True,
            'syntaxHighlight.theme': 'monokai'
        }
    )
    
    app.register_blueprint(swaggerui_blueprint)
    
    # Ruta para servir el archivo OpenAPI YAML
    @app.route('/api/openapi.yaml')
    def serve_openapi_spec():
        """Sirve el archivo de especificación OpenAPI"""
        api_dir = os.path.join(app.root_path, 'api')
        return send_from_directory(api_dir, 'openapi.yaml')
