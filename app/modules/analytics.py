
from flask import Blueprint, render_template, redirect, url_for, session
from pathlib import Path
import json

analytics_bp = Blueprint("analytics", __name__)

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Dashboard JSON file
DATA_FILE = BASE_DIR / "analytics" / "dashboard_data.json"


@analytics_bp.route("/analytics")
def analytics():

    # Check login
    if "user_id" not in session:
        return redirect(url_for("user.login"))

    # Admin access only
    if session.get("role") != "admin":
        return "Access denied: Admin only", 403

    # Default values
    dashboard_data = {
        "total_records": 0,
        "categories": [],
        "statuses": []
    }

    # Read JSON data
    if DATA_FILE.exists():
        try:
            loaded_data = json.loads(
                DATA_FILE.read_text(encoding="utf-8")
            )

            if isinstance(loaded_data, dict):
                dashboard_data.update(loaded_data)

        except (json.JSONDecodeError, OSError) as error:
            print("Dashboard data error:", error)

    else:
        print("Dashboard JSON file not found:", DATA_FILE)

    # Total records
    total_records = dashboard_data.get("total_records", 0)

    # Category data
    categories = dashboard_data.get("categories", [])

    category_labels = [
        item["label"] for item in categories
    ]

    category_values = [
        item["value"] for item in categories
    ]

    # Review status data
    statuses = dashboard_data.get("statuses", [])

    status_labels = [
        item["label"] for item in statuses
    ]

    status_values = [
        item["value"] for item in statuses
    ]

    # Render dashboard
    return render_template(
        "analytics.html",
        total_records=total_records,
        category_labels=category_labels,
        category_values=category_values,
        status_labels=status_labels,
        status_values=status_values
    )
