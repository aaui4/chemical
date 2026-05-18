# config.py
from pathlib import Path

class Config:
    #  Secret key
    SECRET_KEY = "secret_key"

    #  Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'kindkiki9@gmail.com'
    MAIL_PASSWORD = 'bcfoevelsnsrdvuq'

    #  Uploads
    UPLOAD_FOLDER = Path("static/uploads/")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    #  Allowed extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    #  Babel (إضافة فقط)
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en', 'ar']