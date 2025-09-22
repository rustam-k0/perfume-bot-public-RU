import sqlite3

DB_PATH = "data/perfumes.db"  # путь к вашей базе

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

brand = "Tom Ford"
cur.execute("SELECT * FROM OriginalPerfume WHERE brand = ?", (brand,))
rows = cur.fetchall()

if rows:
    print(f"В базе есть духи бренда {brand}:")
    for r in rows:
        print(f"- {r['brand']}: {r['name']}")
else:
    print(f"В базе нет духов бренда {brand}.")

conn.close()

