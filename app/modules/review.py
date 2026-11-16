
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db import get_db_connection

review_bp = Blueprint("review", __name__)

@review_bp.route("/admin/review")
def review_records():
    if "user_id" not in session:
        return redirect(url_for("user.login"))

    if session.get("role") != "admin":
        return "Access denied: Admin only", 403

    connection = get_db_connection()

    try:
        records = connection.execute("""
            SELECT
                wr.waste_id,
                wr.predicted_label,
                wr.confidence_score,
                wr.review_status,
                wr.created_at,
                u.full_name
            FROM waste_records wr
            LEFT JOIN users u ON wr.user_id = u.user_id
            ORDER BY wr.created_at DESC
        """).fetchall()
    finally:
        connection.close()

    return render_template("review.html", records=records)


@review_bp.route("/admin/review/<int:waste_id>", methods=["POST"])
def update_review(waste_id):
    if "user_id" not in session:
        return redirect(url_for("user.login"))

    if session.get("role") != "admin":
        return "Access denied: Admin only", 403

    category = request.form.get("category", "").strip()

    allowed_categories = {"e_waste", "natural_waste"}

    if category not in allowed_categories:
        flash("Invalid waste category.")
        return redirect(url_for("review.review_records"))

    connection = get_db_connection()

    try:
        cursor = connection.execute("""
            UPDATE waste_records
            SET predicted_label = ?, review_status = 'Reviewed'
            WHERE waste_id = ?
        """, (category, waste_id))

        connection.commit()

        if cursor.rowcount == 0:
            flash("Waste record not found.")
        else:
            flash("Waste classification reviewed successfully.")

    except Exception:
        connection.rollback()
        flash("Could not update the review.")

    finally:
        connection.close()

    return redirect(url_for("review.review_records"))
