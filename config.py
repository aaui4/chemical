from pathlib import Path

class Config:
    SECRET_KEY = "secret_key"

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = 'chemicalsimulator926@gmail.com'

    # بدون فراغات
    MAIL_PASSWORD = 'squyaqezltkljign'

    MAIL_DEFAULT_SENDER = 'chemicalsimulator926@gmail.com'

    # يمنع انتظار طويل
    MAIL_TIMEOUT = 10

    UPLOAD_FOLDER = Path("static/uploads/")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}

    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en','ar']