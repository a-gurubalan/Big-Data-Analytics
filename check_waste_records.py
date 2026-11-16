
from database.db import get_db_connection

connection = get_db_connection()

rows = connection.execute("""
    SELECT waste_id, user_id, predicted_label,
           confidence_score, review_status, created_at
    FROM waste_records
""").fetchall()

print("\nTOTAL WASTE RECORDS:", len(rows))

for row in rows:
    print(dict(row))

connection.close()
