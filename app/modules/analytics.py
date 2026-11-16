
from flask import Blueprint, render_template, redirect, url_for, session
from pathlib import Path
import json

analytics_bp = Blueprint("analytics", __name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_FILE = BASE_DIR / "analytics" / "dashboard_data.json"


@analytics_bp.route("/analytics")
def analytics():

    if "user_id" not in session:
        return redirect(url_for("user.login"))

    if session.get("role") != "admin":
        return "Access denied: Admin only", 403

    dashboard_data = {
        "total_records": 0,
        "categories": [],
        "statuses": []
    }

    if DATA_FILE.exists():
        try:
            dashboard_data = json.loads(
                DATA_FILE.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError) as error:
            print("Dashboard data error:", error)

    category_labels = [
        item["label"] for item in dashboard_data["categories"]
    ]

    category_values = [
        item["value"] for item in dashboard_data["categories"]
    ]

    status_labels = [
        item["label"] for item in dashboard_data["statuses"]
    ]

    status_values = [
        item["value"] for item in dashboard_data["statuses"]
    ]

    return render_template(
        "analytics.html",
        total_records=dashboard_data["total_records"],
        category_labels=category_labels,
        category_values=category_values,
        status_labels=status_labels,
        status_values=status_values
    )
