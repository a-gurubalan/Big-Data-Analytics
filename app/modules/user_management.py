
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from database.db import get_db_connection

from pathlib import Path
import uuid


user_bp = Blueprint("user", __name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


# --------------------------------
# USER REGISTRATION
# --------------------------------

@user_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not full_name or not email or not password:
            flash("Please fill in all fields.")
            return redirect(url_for("user.register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.")
            return redirect(url_for("user.register"))

        password_hash = generate_password_hash(password)

        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO users
                (full_name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (full_name, email, password_hash)
            )

            connection.commit()

            flash("Registration successful. Please login.")

            return redirect(url_for("user.login"))

        except Exception as error:

            connection.rollback()

            current_app.logger.exception(
                "Registration error"
            )

            flash("Registration failed. Email may already exist.")

        finally:
            connection.close()

    return render_template("register.html")


# --------------------------------
# USER LOGIN
# --------------------------------

@user_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = get_db_connection()

        try:
            user = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

        finally:
            connection.close()

        if user and check_password_hash(
            user["password_hash"], password
        ):

            session.clear()

            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]

            return redirect(url_for("user.dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


# --------------------------------
# USER DASHBOARD
# --------------------------------

@user_bp.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("user.login"))

    if session.get("role") == "admin":
        return redirect(url_for("user.admin_dashboard"))

    connection = get_db_connection()

    try:
        records = connection.execute(
            """
            SELECT *
            FROM waste_records
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (session["user_id"],)
        ).fetchall()

    finally:
        connection.close()

    return render_template(
        "user_dashboard.html",
        full_name=session["full_name"],
        records=records
    )


# --------------------------------
# WASTE IMAGE UPLOAD AND AI PREDICTION
# --------------------------------

@user_bp.route("/upload", methods=["GET", "POST"])
def upload_waste():

    print("DEBUG: Upload route opened")

    if "user_id" not in session:
        print("DEBUG: User not logged in")
        return redirect(url_for("user.login"))

    print("DEBUG: Logged-in user ID:", session["user_id"])

    if request.method == "POST":

        print("DEBUG: POST request received")

        image = request.files.get("waste_image")

        if not image or not image.filename:
            flash("Please select an image.")
            return redirect(url_for("user.upload_waste"))

        print("DEBUG: Image selected:", image.filename)

        if "." not in image.filename:
            flash("Invalid image filename.")
            return redirect(url_for("user.upload_waste"))

        extension = image.filename.rsplit(".", 1)[-1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            flash("Only JPG, JPEG and PNG images are allowed.")
            return redirect(url_for("user.upload_waste"))

        # Validate image

        try:
            from PIL import Image

            image.stream.seek(0)

            with Image.open(image.stream) as img:
                img.verify()

            image.stream.seek(0)

            print("DEBUG: Image validation successful")

        except Exception as error:

            print("DEBUG: Image validation failed:", error)

            flash("Invalid or corrupted image.")

            return redirect(url_for("user.upload_waste"))

        # Generate unique filename

        safe_name = secure_filename(image.filename)

        unique_name = f"{uuid.uuid4().hex}_{safe_name}"

        upload_folder = Path(
            current_app.config["UPLOAD_FOLDER"]
        )

        upload_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        image_path = upload_folder / unique_name

        try:
            image.save(image_path)

            print("DEBUG: Image saved:", image_path)

        except Exception as error:

            print("DEBUG: Image saving failed:", error)

            flash("Could not save uploaded image.")

            return redirect(url_for("user.upload_waste"))

        # AI prediction

        prediction = None
        confidence = None
        prediction_error = None

        try:
            from ai_model.predict import predict_waste

            print("DEBUG: Starting AI prediction")

            result = predict_waste(str(image_path))

            prediction = result["category"]
            confidence = result["confidence"]

            print("DEBUG: Prediction:", prediction)
            print("DEBUG: Confidence:", confidence)

        except Exception as error:

            prediction_error = str(error)

            print("DEBUG: AI prediction failed:", error)

            current_app.logger.exception(
                "AI prediction failed"
            )

        # Save result in SQLite

        connection = get_db_connection()

        try:

            print("DEBUG: Saving waste record...")
            print("DEBUG: User ID:", session["user_id"])
            print("DEBUG: Prediction:", prediction)

            cursor = connection.execute(
                """
                INSERT INTO waste_records
                (
                    user_id,
                    image_path,
                    predicted_label,
                    confidence_score,
                    review_status
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    f"uploads/{unique_name}",
                    prediction,
                    confidence,
                    "Needs manual review"
                )
            )

            connection.commit()

            print("DEBUG: Waste record saved successfully!")
            print("DEBUG: New waste ID:", cursor.lastrowid)

        except Exception as error:

            connection.rollback()

            image_path.unlink(missing_ok=True)

            print("DEBUG: Database insertion failed:", error)

            current_app.logger.exception(
                "Database upload error"
            )

            flash("Could not save the image record.")

            return redirect(url_for("user.upload_waste"))

        finally:
            connection.close()

        print("DEBUG: Upload process completed")

        return render_template(
            "classification.html",
            prediction=prediction,
            confidence=confidence,
            prediction_error=prediction_error
        )

    return render_template("upload_waste.html")


# --------------------------------
# ADMIN DASHBOARD
# --------------------------------

@user_bp.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("user.login"))

    if session.get("role") != "admin":
        return "Access denied: Admin only", 403

    connection = get_db_connection()

    try:

        total_users = connection.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        total_waste = connection.execute(
            "SELECT COUNT(*) FROM waste_records"
        ).fetchone()[0]

        pending = connection.execute(
            """
            SELECT COUNT(*)
            FROM waste_records
            WHERE review_status != 'Reviewed'
               OR review_status IS NULL
            """
        ).fetchone()[0]

        ewaste = connection.execute(
            """
            SELECT COUNT(*)
            FROM waste_records
            WHERE LOWER(predicted_label) = 'e_waste'
            """
        ).fetchone()[0]

        natural_waste = connection.execute(
            """
            SELECT COUNT(*)
            FROM waste_records
            WHERE LOWER(predicted_label) = 'natural_waste'
            """
        ).fetchone()[0]

        reviewed = connection.execute(
            """
            SELECT COUNT(*)
            FROM waste_records
            WHERE review_status = 'Reviewed'
            """
        ).fetchone()[0]

    finally:
        connection.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_waste=total_waste,
        pending=pending,
        ewaste=ewaste,
        natural_waste=natural_waste,
        reviewed=reviewed
    )


# --------------------------------
# LOGOUT
# --------------------------------

@user_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("user.login"))
