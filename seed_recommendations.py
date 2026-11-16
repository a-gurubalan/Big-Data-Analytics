
from database.db import get_db_connection

connection = get_db_connection()

try:
    # Check required tables
    tables = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }

    required = {"waste_categories", "recommendations"}

    if not required.issubset(tables):
        raise RuntimeError(
            "Missing tables. Run python -m database.db first."
        )

    sample_data = [
        {
            "name": "E-Waste",
            "group": "e_waste",
            "bio": "Non-biodegradable",
            "description": "Discarded electronic devices and components.",
            "title": "Safe E-Waste Recycling",
            "instructions": (
                "Keep electronic waste separate. Do not burn or dismantle "
                "batteries. Give old electronics to an authorized e-waste "
                "collection or recycling centre."
            ),
            "method": "Authorized e-waste collection centre"
        },
        {
            "name": "Natural Waste",
            "group": "natural_waste",
            "bio": "Usually biodegradable",
            "description": "Organic waste such as fruit and vegetable scraps.",
            "title": "Composting Natural Waste",
            "instructions": (
                "Separate organic waste from plastic and metal. Use suitable "
                "fruit and vegetable scraps for composting."
            ),
            "method": "Composting or municipal organic waste collection"
        }
    ]

    for item in sample_data:
        connection.execute("""
            INSERT INTO waste_categories
            (category_name, waste_group, biodegradability, description)
            SELECT ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM waste_categories WHERE category_name = ?
            )
        """, (
            item["name"], item["group"], item["bio"],
            item["description"], item["name"]
        ))

        category = connection.execute(
            "SELECT category_id FROM waste_categories WHERE category_name = ?",
            (item["name"],)
        ).fetchone()

        connection.execute("""
            INSERT INTO recommendations
            (category_id, action_title, instructions, disposal_method)
            SELECT ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM recommendations
                WHERE category_id = ? AND action_title = ?
            )
        """, (
            category["category_id"],
            item["title"],
            item["instructions"],
            item["method"],
            category["category_id"],
            item["title"]
        ))

    connection.commit()
    print("Sample waste categories and recommendations inserted!")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
