
from database.db import get_db_connection

email = input("Enter the registered email to make admin: ").strip().lower()

connection = get_db_connection()

cursor = connection.execute(
    "UPDATE users SET role = 'admin' WHERE email = ?",
    (email,)
)

connection.commit()

if cursor.rowcount == 1:
    print("Admin role assigned successfully!")
else:
    print("Email not found. Register this account first.")

connection.close()
