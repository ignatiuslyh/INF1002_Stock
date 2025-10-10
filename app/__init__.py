# P5-4_PythonProject/app/__init__.py
from flask import Flask
from config import Config 

def create_app(config_class=Config):
    # Initialize the Flask application instance
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config_class)
    
    # 1. IMPORT the routes module from the local package
    # The leading dot (.) indicates a relative import within the 'app' package.
    from . import routes 
    
    # Alternatively, and often clearer if using Blueprints directly:
    from .routes import main_bp 
    app.register_blueprint(main_bp)
    
    # 2. REGISTER the Blueprint with the application instance

    return app