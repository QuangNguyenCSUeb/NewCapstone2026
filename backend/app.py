from flask import Flask, send_from_directory
from config import Config
from database.models import init_db
from database.db import get_latest_scan
from api.routes import api
import os

app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path=""
)

app.register_blueprint(api)


@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")


@app.route("/report")
def report():
    return send_from_directory("../frontend", "report.html")


def initialize():
    print("[startup] Initializing database...")
    init_db()
    print("[startup] Database ready.")
    scan = get_latest_scan()
    if not scan:
        print("[startup] No scans found — waiting for first paste.")
    else:
        print(f"[startup] Last scan: {scan['created_at']}")


if __name__ == "__main__":
    initialize()
    print(f"[startup] Running at http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )