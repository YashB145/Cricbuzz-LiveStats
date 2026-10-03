import sqlite3

conn = sqlite3.connect("cricket.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM matches")

rows = cursor.fetchall()

print("Total rows:", len(rows))  # 👈 add this

for row in rows:
    print(row)

conn.close()