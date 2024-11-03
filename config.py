import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_hard_to_guess_string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    COOKIE_NAME = 'auth_token'
    MAX_CONTENT_LENGTH = 1024*1024 
    UPLOAD_PATH = "uploads"
