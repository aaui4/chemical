import os
from database.db import get_db

# تحديد مسار قاعدة البيانات بشكل آمن  
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "chemical.db")


def create_tables():
    db = get_db()
    cursor = db.cursor()

    # ===== user =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin', 'user')) NOT NULL
    )
    """)
    columns = cursor.execute("PRAGMA table_info(user)").fetchall()
    if not any(c[1] == "avatar" for c in columns):
        cursor.execute("ALTER TABLE user ADD COLUMN avatar TEXT DEFAULT 'default.png'")
        print("تم إضافة العمود avatar")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now','localtime'))
)
""")

    # ===== chemical_elements =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chemical_elements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        symbol TEXT NOT NULL,
        atomicNumber INTEGER,
        atomicMass REAL,
        default_color TEXT,
        state TEXT CHECK(state IN ('solid','liquid','gas'))
    )
    """)

    # ===== chemical_reactions =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chemical_reactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equation TEXT NOT NULL,
        type TEXT,
        temperature REAL,
        pressure REAL
    )
    """)

    # ===== simulations =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS simulation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        reaction_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        result TEXT,
        FOREIGN KEY (user_id) REFERENCES user(id),
        FOREIGN KEY (reaction_id) REFERENCES chemical_reactions(id)
    )
    """)

    # ===== reaction_results =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reaction_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        simulation_id INTEGER UNIQUE NOT NULL,
        products TEXT,
        energyReleased REAL,
        state TEXT,
        color TEXT,
        FOREIGN KEY (simulation_id) REFERENCES simulations(id)
    )
    """)

    # ===== reaction_elements (many-to-many) =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reaction_elements (
        reaction_id INTEGER NOT NULL,
        element_id INTEGER NOT NULL,
        quantity REAL,
        PRIMARY KEY (reaction_id, element_id),
        FOREIGN KEY (reaction_id) REFERENCES chemical_reactions(id),
        FOREIGN KEY (element_id) REFERENCES chemical_elements(id)
    )
    """)

    db.commit()