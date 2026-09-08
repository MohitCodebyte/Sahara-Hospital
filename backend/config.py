import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sahara-hospital-secret-key-2024'
    PORT = int(os.environ.get('PORT', 5000))
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
