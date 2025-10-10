import os
from datetime import timedelta

class Config:
    """Base configuration settings for the Flask application."""
    
    # 1. SECRET_KEY: Loaded from Railway environment variable for security.
    # THIS KEY MUST BE SET IN YOUR RAILWAY VARIABLES.
    # The second value is a safe fallback only for local development/testing.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'P5-4-fallback-secret-key-NEVER-USE-IN-PROD'
    
    # Session configuration (required since you use session data for ticker/period)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_TYPE = 'filesystem' # Stores sessions on disk
    
    # Set default values for environment settings
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    DEBUG = FLASK_ENV == 'development'