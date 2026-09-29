import sqlite3
import settings

conn = sqlite3.connect(settings.DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT id, time, class_name, conf, image_path FROM alarms ORDER BY id DESC LIMIT 10")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()
