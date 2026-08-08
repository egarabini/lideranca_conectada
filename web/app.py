import os

import psycopg
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, static_folder='static')

LEADS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    whatsapp VARCHAR(20) NOT NULL,
    empresa VARCHAR(255) NOT NULL,
    cargo VARCHAR(255) NOT NULL,
    colaboradores VARCHAR(50) NOT NULL,
    cidade_uf VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100) DEFAULT 'lp'
);
"""


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None
    return psycopg.connect(database_url, connect_timeout=5)


def init_db():
    try:
        conn = get_db_connection()
        if conn is None:
            return
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(LEADS_TABLE_SQL)
        conn.close()
    except Exception:
        pass


init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/lp")
def landing_page():
    return render_template("lp.html")


@app.route("/api/leads", methods=["POST"])
def create_lead():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Dados inválidos"}), 400

    required_fields = ["nome", "email", "whatsapp", "empresa", "cargo", "colaboradores"]
    labels = {
        "nome": "Nome",
        "email": "E-mail",
        "whatsapp": "WhatsApp",
        "empresa": "Empresa",
        "cargo": "Cargo / Função",
        "colaboradores": "Número de colaboradores",
    }
    errors = []

    for field in required_fields:
        value = data.get(field, "").strip() if isinstance(data.get(field), str) else ""
        if not value:
            errors.append({"field": field, "message": f"{labels[field]} é obrigatório"})

    if errors:
        return jsonify({"status": "error", "errors": errors}), 400

    source = data.get("source", "lp") or "lp"
    cidade_uf = data.get("cidade_uf", "")
    if isinstance(cidade_uf, str):
        cidade_uf = cidade_uf.strip()

    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Serviço indisponível"}), 503

    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO leads (nome, email, whatsapp, empresa, cargo, colaboradores, cidade_uf, source) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        data["nome"].strip(),
                        data["email"].strip(),
                        data["whatsapp"].strip(),
                        data["empresa"].strip(),
                        data["cargo"].strip(),
                        data["colaboradores"].strip(),
                        cidade_uf,
                        source,
                    ),
                )
        conn.close()
        return jsonify({"status": "success", "message": "Lead recebido com sucesso"}), 201
    except Exception as exc:
        return jsonify({"status": "error", "message": "Erro ao salvar", "detail": str(exc)}), 500


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
