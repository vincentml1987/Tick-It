import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tickit.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
