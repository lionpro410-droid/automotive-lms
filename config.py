import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'automotive_lms_super_secret_key'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit upload size to 16MB