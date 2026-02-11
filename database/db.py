import sqlite3
import os
from flask import g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chemical.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row  # مهم جدًا ليعمل user["password"]
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
