import sqlite3
import os
from flask import g

# تحديد مسار قاعدة البيانات بشكل آمن
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # مسار مجلد database
DATABASE = os.path.join(BASE_DIR, "chemical.db")       # path كامل للملف

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        # تفعيل Foreign Keys
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()