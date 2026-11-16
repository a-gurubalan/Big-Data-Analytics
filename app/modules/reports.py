
from flask import Blueprint, session, redirect, url_for, render_template, send_file
from database.db import get_db_connection
from pathlib import Path
from datetime import datetime
import csv
import io

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/reports")
def reports():
    if "user_id" not in session:
        return redirect(url_for("user.login"))

    if session.get("role") != "admin":
        return "Access denied: Admin only", 403

    connection = get_db_connection()

    try:
        data = {
            "total_users": connection.execute(
                "SELECT COUNT(*) FROM users"
            ).fetchone()[0],
            "total_waste": connection.execute(
                "SELECT COUNT(*) FROM waste_records"
            ).fetchone()[0],
            "ewaste": connection.execute(
                "SELECT COUNT(*) FROM waste_records WHERE LOWER(predicted_label) = 'e_waste'"
            ).fetchone()[0],
            "natural_waste": connection.execute(
                "SELECT COUNT(*) FROM waste_records WHERE LOWER(predicted_label) = 'natural_waste'"
            ).fetchone()[0],
            "pending": connection.execute(
                "SELECT COUNT(*) FROM waste_records WHERE review_status != 'Reviewed' OR review_status IS NULL"
            ).fetchone()[0],
            "reviewed": connection.execute(
                "SELECT COUNT(*) FROM waste_records WHERE review_status = 'Reviewed'"
            ).fetchone()[0]
        }
    finally:
        connection.close()

    return render_template("reports.html", data=data)


@reports_bp.route("/reports/download")
def download_report():
    if "user_id" not in session:
        return redirect(url_for("user.login"))

    if session.get("role") != "admin":
        return "Access denied: Admin only", 403

    connection = get_db_connection()

    try:
        data = [
            ["Metric", "Value"],
            ["Total Registered Users", connection.execute(
                "SELECT COUNT(*) FROM users"
            ).fetchone()[0]],
            ["Total Waste Uploads", connection.execute(
                "SELECT COUNT(*) FROM waste_records"
            ).fetchone()[0]],
            ["E-Waste Records", connection.execute(
                "SELECT COUNT(*) FROM waste_records WHERE LOWER(predicted_label) = 'e_waste'"
            ).fetchone()[0]],
            ["Natural Waste Records", connection.execute(
                "SELECT COUNT(*) FROM waste_records WHERE LOWER(predicted_label) = 'natural_waste'"
            ).fetchone()[0]],
            ["Pending Reviews", connection.execute(
                "SELECT COUNT(*) FROM waste_records WHERE review_status != 'Reviewed' OR review_status IS NULL"
            ).fetchone()[0]],
            ["Reviewed Records", connection.execute(
                "SELECT COUNT(*) FROM waste_records WHERE review_status = 'Reviewed'"
            ).fetchone()[0]]
        ]
    finally:
        connection.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(data)

    filename = f"waste_report_{datetime.now():%Y%m%d_%H%M%S}.csv"

    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename
    )
