import os

import psycopg
from flask import Flask, jsonify, render_template, request

# Configurar DATABASE_URL se não estiver definido
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://david:troque_por_senha_segura@127.0.0.1:5433/lideranca_test"

from admin import admin_bp
from avaliacao import avaliacao_bp
from db import execute, get_db_connection, init_db, query
from formularios import formularios_bp
from investigacao import investigacao_bp

app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv("SECRET_KEY", "lideranca-conectada-dev-secret")

app.register_blueprint(admin_bp)
app.register_blueprint(avaliacao_bp)
app.register_blueprint(investigacao_bp)
app.register_blueprint(formularios_bp)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/lp")
def landing_page():
    return render_template("lp.html")


@app.route("/lp_<int:palestra_id>")
def lp_palestra(palestra_id):
    """Landing page específica para cada palestra"""
    palestra = query("SELECT id, titulo, descricao FROM palestras WHERE id = %s AND ativo = TRUE", (palestra_id,), one=True)
    if not palestra:
        return render_template("404.html"), 404

    formulario = query(
        """SELECT f.id, f.titulo, f.descricao, f.texto_final
           FROM formularios f
           WHERE f.id = (SELECT formulario_investigacao_id FROM palestras WHERE id = %s)
           AND f.ativo = TRUE""",
        (palestra_id,),
        one=True
    )

    questoes = query(
        """SELECT id, ordem, bloco, pergunta, tipo_resposta, obrigatoria, tem_outro, opcoes
           FROM questoes
           WHERE formulario_id = %s
           ORDER BY ordem""",
        (formulario["id"],),
    ) if formulario else []

    return render_template("lp_palestra.html", palestra=palestra, formulario=formulario, questoes=questoes)


@app.route("/api/participante", methods=["POST"])
def criar_participante():
    """Cria participante e registra respostas do formulário"""
    # Try to get JSON
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"status": "error", "message": "Dados inválidos"}), 400

    # Validar campos obrigatórios da pessoa
    campos_pessoa = ["nome_completo", "telefone", "email", "cidade_uf"]
    labels_pessoa = {
        "nome_completo": "Nome completo",
        "telefone": "Telefone",
        "email": "E-mail",
        "cidade_uf": "Cidade/UF"
    }
    errors = []

    for field in campos_pessoa:
        value = data.get(field, "").strip() if isinstance(data.get(field), str) else ""
        if not value:
            errors.append({"field": field, "message": f"{labels_pessoa[field]} é obrigatório"})

    # Validar e-mail
    email = data.get("email", "").strip().lower()
    if email and "@" not in email:
        errors.append({"field": "email", "message": "E-mail inválido"})

    # Validar telefone (básico)
    telefone = data.get("telefone", "").strip()
    if telefone and len(telefone) < 10:
        errors.append({"field": "telefone", "message": "Telefone inválido (mínimo 10 dígitos)"})

    # Validar respostas do formulário
    respostas = data.get("respostas", {})
    formulario_id = data.get("formulario_id")
    palestra_id = data.get("palestra_id")

    if not formulario_id or not palestra_id:
        errors.append({"field": "formulario", "message": "Formulário ou palestra não identificados"})

    if errors:
        return jsonify({"status": "error", "errors": errors}), 400

    # Buscar questões obrigatórias
    questoes_obrigatorias = query(
        "SELECT id, pergunta FROM questoes WHERE formulario_id = %s AND obrigatoria = TRUE",
        (formulario_id,)
    )

    for questao in questoes_obrigatorias:
        questao_id = str(questao["id"])
        if questao_id not in respostas or not respostas[questao_id]:
            errors.append({
                "field": f"questao_{questao_id}",
                "message": f"Pergunta obrigatória: {questao['pergunta'][:50]}..."
            })

    if errors:
        return jsonify({"status": "error", "errors": errors}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Serviço indisponível"}), 503

    try:
        with conn:
            with conn.cursor() as cursor:
                # Verificar se pessoa já existe pelo e-mail
                cursor.execute("SELECT id FROM pessoas WHERE LOWER(email) = %s", (email,))
                pessoa_result = cursor.fetchone()

                if pessoa_result:
                    pessoa_id = pessoa_result[0]
                    # Atualizar dados se fornecidos
                    cursor.execute("""
                        UPDATE pessoas SET
                            nome_completo = %s,
                            telefone = %s,
                            ind_whatsapp = %s,
                            nome_empresa = %s,
                            cargo_funcao = %s,
                            cidade_uf = %s,
                            alterado_em = NOW()
                        WHERE id = %s
                    """, (
                        data.get("nome_completo").strip(),
                        telefone,
                        data.get("ind_whatsapp", True),
                        data.get("nome_empresa", "").strip(),
                        data.get("cargo_funcao", "").strip(),
                        data.get("cidade_uf").strip(),
                        pessoa_id
                    ))
                else:
                    # Criar nova pessoa
                    cursor.execute("""
                        INSERT INTO pessoas (nome_completo, telefone, ind_whatsapp, email, nome_empresa, cargo_funcao, cidade_uf)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        data.get("nome_completo").strip(),
                        telefone,
                        data.get("ind_whatsapp", True),
                        email,
                        data.get("nome_empresa", "").strip(),
                        data.get("cargo_funcao", "").strip(),
                        data.get("cidade_uf").strip(),
                    ))
                    pessoa_id = cursor.fetchone()[0]

                # Criar vínculo participante (se ainda não existir) e obter ID
                cursor.execute("""
                    INSERT INTO participantes (palestra_id, pessoa_id)
                    VALUES (%s, %s)
                    ON CONFLICT (palestra_id, pessoa_id) DO UPDATE SET id = participantes.id
                    RETURNING id
                """, (palestra_id, pessoa_id))
                participante_id = cursor.fetchone()[0]

                # Registrar respostas do formulário
                for questao_id, valor in respostas.items():
                    # Verificar se a questão tem campo "outro"
                    tem_outro_query = query("SELECT tem_outro FROM questoes WHERE id = %s", (questao_id,), one=True)
                    tem_outro = tem_outro_query["tem_outro"] if tem_outro_query else False

                    valor_outro = valor.get("outro", "") if isinstance(valor, dict) and tem_outro else None
                    valor_principal = valor["valor"] if isinstance(valor, dict) else valor

                    cursor.execute("""
                        INSERT INTO respostas_formulario (questao_id, participante_id, valor)
                        VALUES (%s, %s, %s)
                    """, (questao_id, participante_id, str(valor_principal)))

        conn.close()

        return jsonify({
            "status": "success",
            "message": "Participante registrado com sucesso!",
            "pessoa_id": pessoa_id
        }), 201

    except Exception as exc:
        return jsonify({"status": "error", "message": "Erro ao salvar", "detail": str(exc)}), 500


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

        # Confere se o e-mail é de um participante de palestra ativa com formulário associado
        redirect_url = _redirect_participante(data["email"].strip().lower())
        payload = {"status": "success", "message": "Lead recebido com sucesso"}
        if redirect_url:
            payload["redirect"] = redirect_url
        return jsonify(payload), 201
    except Exception as exc:
        return jsonify({"status": "error", "message": "Erro ao salvar", "detail": str(exc)}), 500


def _redirect_participante(email):
    """Se o e-mail pertence a um participante de uma palestra ativa com formulário
    de investigação associado, retorna a URL do formulário (via vínculo)."""
    try:
        row = query(
            """SELECT po.id AS po_id
               FROM participantes pa
               JOIN pessoas pes ON pes.id = pa.pessoa_id
               JOIN palestras p ON p.id = pa.palestra_id
               JOIN palestras_organizacoes po ON po.palestra_id = p.id
               WHERE LOWER(pes.email) = %s
                 AND p.formulario_investigacao_id IS NOT NULL
               ORDER BY po.id
               LIMIT 1""",
            (email,),
            one=True,
        )
        if row:
            return f"/investigacao/{row['po_id']}"
    except Exception:
        pass
    return None


@app.route("/health")
def health():
    from db import get_db_connection

    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "database": "unavailable"}), 503

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        conn.close()
        return jsonify({"status": "ok", "database": "available"})
    except Exception as exc:
        return jsonify({"status": "error", "database": "error", "detail": str(exc)}), 503


# Inicializar banco de dados e registrar rotas
init_db()

# Log para depuração
print("=" * 50)
print("ALL ROUTES:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint}")
print("=" * 50)


if __name__ == "__main__":
    app.run(debug=True)
