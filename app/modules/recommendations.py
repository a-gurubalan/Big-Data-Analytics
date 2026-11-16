
from flask import Blueprint, render_template, redirect, url_for, session
from database.db import get_db_connection

recommendation_bp = Blueprint("recommendation", __name__)

@recommendation_bp.route("/recommendations")
def recommendations():
    if "user_id" not in session:
        return redirect(url_for("user.login"))

    connection = get_db_connection()

    try:
        records = connection.execute("""
            SELECT
                wr.waste_id,
                wr.predicted_label,
                wr.confidence_score,
                wr.review_status,
                wc.category_name,
                r.action_title,
                r.instructions,
                r.disposal_method
            FROM waste_records wr
            LEFT JOIN waste_categories wc
                ON wr.category_id = wc.category_id
            LEFT JOIN recommendations r
                ON wc.category_id = r.category_id
            WHERE wr.user_id = ?
            ORDER BY wr.created_at DESC
        """, (session["user_id"],)).fetchall()
    finally:
        connection.close()

    return render_template(
        "recommendations.html",
        records=records
    )
