
from flask import Flask
from pathlib import Path
from app.modules.user_management import user_bp
from app.modules.recommendations import recommendation_bp
from app.modules.reports import reports_bp
from app.modules.review import review_bp

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)


app.register_blueprint(review_bp)
app.register_blueprint(reports_bp)
app.config["SECRET_KEY"] = "replace-this-with-a-random-secret"
app.config["UPLOAD_FOLDER"] = BASE_DIR / "uploads"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.register_blueprint(recommendation_bp)


app.register_blueprint(user_bp)

@app.route("/")
def home():
    return """
    <h1>Smart Waste Analytics</h1>
    <a href="/register">Register</a><br>
    <a href="/login">Login</a>
    """

if __name__ == "__main__":
    app.run(debug=True)
