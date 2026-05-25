import os

import psycopg
from flask import Flask, jsonify, render_template

app = Flask(__name__, static_folder='static')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        return jsonify({"status": "ok", "database": "not_configured"})

    try:
        with psycopg.connect(database_url, connect_timeout=3) as conn:
            with conn.cursor() as cursor:
                cursor.execute("select 1")
                cursor.fetchone()
    except Exception as exc:
        return jsonify({"status": "error", "database": "unavailable", "detail": str(exc)}), 503

    return jsonify({"status": "ok", "database": "available"})

if __name__ == "__main__":
    app.run(debug=True)
