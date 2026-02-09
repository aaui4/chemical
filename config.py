# config.py
from pathlib import Path

class Config:
    #  Secret key
    SECRET_KEY = "secret_key"

    #  Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'kindkiki9@gmail.com'
    MAIL_PASSWORD = 'bcfo evel snsr dvuq'

    #  Uploads
    UPLOAD_FOLDER = Path("static/uploads/")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    #  Allowed extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}