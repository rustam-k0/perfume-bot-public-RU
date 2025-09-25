from database import get_connection
import os
from datetime import datetime

# Абсолютный путь к БД
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "perfumes.db")

conn = get_connection(DB_PATH)

print("=== UserMessages Analytics ===\n")

# 1. Количество уникальных пользователей и активность
unique_users = conn.execute("SELECT COUNT(DISTINCT user_id) FROM UserMessages").fetchone()[0]
print(f"1️⃣ Уникальных пользователей: {unique_users}")

activity_per_user = conn.execute("""
    SELECT user_id, COUNT(*) AS total_msgs 
    FROM UserMessages 
    GROUP BY user_id 
    ORDER BY total_msgs DESC
""").fetchall()
print("\nАктивность пользователей (user_id, total_msgs):")
for r in activity_per_user:
    print(dict(r))

# 2. Тип сообщений и команды
status_counts = conn.execute("""
    SELECT status, COUNT(*) AS cnt 
    FROM UserMessages 
    GROUP BY status
""").fetchall()
print("\n2️⃣ Статусы сообщений:")
for r in status_counts:
    print(dict(r))

# 3. Ошибки и проблемные запросы
fails = conn.execute("""
    SELECT user_id, message, notes 
    FROM UserMessages 
    WHERE status='fail'
""").fetchall()
print("\n3️⃣ Неуспешные запросы (fail):")
for r in fails:
    print(dict(r))

# 4. Анализ успешных запросов с NOTE
notes = conn.execute("""
    SELECT user_id, message, notes 
    FROM UserMessages 
    WHERE status='success' AND notes LIKE '%NOTE%'
""").fetchall()
print("\n4️⃣ Успешные запросы с NOTE (fuzzy/неточные совпадения):")
for r in notes:
    print(dict(r))

# 5. Поведение пользователей во времени
user_time_stats = conn.execute("""
    SELECT user_id, MIN(timestamp) AS first_ts, MAX(timestamp) AS last_ts, COUNT(*) AS total_msgs
    FROM UserMessages
    GROUP BY user_id
""").fetchall()
print("\n5️⃣ Временные показатели пользователей:")
for r in user_time_stats:
    r_dict = dict(r)
    r_dict['first_ts'] = datetime.fromtimestamp(r_dict['first_ts']).strftime('%Y-%m-%d %H:%M:%S')
    r_dict['last_ts'] = datetime.fromtimestamp(r_dict['last_ts']).strftime('%Y-%m-%d %H:%M:%S')
    print(r_dict)

conn.close()
