import sqlite3

conn = sqlite3.connect("cricket.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS matches")

cursor.execute("""
CREATE TABLE matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team1 TEXT,
    team2 TEXT,
    status TEXT,
    score TEXT
)
""")

conn.commit()
conn.close()

print("✅ Fresh DB created")