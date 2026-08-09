import functools
import os

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from db import execute, query

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

LEAD_STATUS = ["novo", "contatado", "convertido", "descartado"]


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_user_id"):
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)

    return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        user = query(
            "SELECT * FROM usuarios WHERE email = %s AND ativo = TRUE", (email,), one=True
        )
        if user and check_password_hash(user["senha_hash"], senha):
            session["admin_user_id"] = user["id"]
            session["admin_user_nome"] = user["nome"]
            session["admin_user_email"] = user["email"]
            return redirect(url_for("admin.dashboard"))
        flash("E-mail ou senha inválidos.", "error")
    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
@login_required
def dashboard():
    total_leads = query("SELECT COUNT(*) AS c FROM leads", one=True)["c"]
    leads_novos = query(
        "SELECT COUNT(*) AS c FROM leads WHERE status = 'novo'", one=True
    )["c"]
    leads_convertidos = query(
        "SELECT COUNT(*) AS c FROM leads WHERE status = 'convertido'", one=True
    )["c"]
    total_organizacoes = query("SELECT COUNT(*) AS c FROM organizacoes", one=True)["c"]
    total_palestras = query("SELECT COUNT(*) AS c FROM palestras", one=True)["c"]
    total_avaliacoes = query("SELECT COUNT(*) AS c FROM avaliacoes", one=True)["c"]

    leads_recentes = query(
        "SELECT id, nome, empresa, cargo, status, created_at FROM leads ORDER BY created_at DESC LIMIT 8"
    ) or []

    return render_template(
        "admin/dashboard.html",
        total_leads=total_leads,
        leads_novos=leads_novos,
        leads_convertidos=leads_convertidos,
        total_organizacoes=total_organizacoes,
        total_palestras=total_palestras,
        total_avaliacoes=total_avaliacoes,
        leads_recentes=leads_recentes,
    )


# ---------------- LEADS ----------------
@admin_bp.route("/leads")
@login_required
def leads():
    status = request.args.get("status", "")
    if status:
        rows = query(
            "SELECT * FROM leads WHERE status = %s ORDER BY created_at DESC", (status,)
        ) or []
    else:
        rows = query("SELECT * FROM leads ORDER BY created_at DESC") or []
    return render_template(
        "admin/leads.html", leads=rows, status=status, lead_status=LEAD_STATUS
    )


@admin_bp.route("/leads/<int:lead_id>/status", methods=["POST"])
@login_required
def lead_status(lead_id):
    novo_status = request.form.get("status", "")
    if novo_status in LEAD_STATUS:
        execute(
            "UPDATE leads SET status = %s, updated_at = NOW() WHERE id = %s",
            (novo_status, lead_id),
        )
        flash("Status do lead atualizado.", "success")
    return redirect(request.referrer or url_for("admin.leads"))


@admin_bp.route("/leads/<int:lead_id>/delete", methods=["POST"])
@login_required
def lead_delete(lead_id):
    execute("DELETE FROM leads WHERE id = %s", (lead_id,))
    flash("Lead removido.", "success")
    return redirect(url_for("admin.leads"))


# ---------------- ORGANIZAÇÕES ----------------
@admin_bp.route("/organizacoes")
@login_required
def organizacoes():
    rows = query("SELECT * FROM organizacoes ORDER BY nome") or []
    return render_template("admin/organizacoes.html", organizacoes=rows)


@admin_bp.route("/organizacoes/nova", methods=["GET", "POST"])
@login_required
def organizacao_nova():
    if request.method == "POST":
        execute(
            """INSERT INTO organizacoes (nome, cnpj, segmento, contato_nome, contato_email, contato_telefone)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                request.form.get("nome", "").strip(),
                request.form.get("cnpj", "").strip(),
                request.form.get("segmento", "").strip(),
                request.form.get("contato_nome", "").strip(),
                request.form.get("contato_email", "").strip(),
                request.form.get("contato_telefone", "").strip(),
            ),
        )
        flash("Organização criada.", "success")
        return redirect(url_for("admin.organizacoes"))
    return render_template("admin/organizacao_form.html", org=None)


@admin_bp.route("/organizacoes/<int:org_id>/editar", methods=["GET", "POST"])
@login_required
def organizacao_editar(org_id):
    org = query("SELECT * FROM organizacoes WHERE id = %s", (org_id,), one=True)
    if not org:
        flash("Organização não encontrada.", "error")
        return redirect(url_for("admin.organizacoes"))
    if request.method == "POST":
        execute(
            """UPDATE organizacoes SET nome=%s, cnpj=%s, segmento=%s, contato_nome=%s,
               contato_email=%s, contato_telefone=%s WHERE id=%s""",
            (
                request.form.get("nome", "").strip(),
                request.form.get("cnpj", "").strip(),
                request.form.get("segmento", "").strip(),
                request.form.get("contato_nome", "").strip(),
                request.form.get("contato_email", "").strip(),
                request.form.get("contato_telefone", "").strip(),
                org_id,
            ),
        )
        flash("Organização atualizada.", "success")
        return redirect(url_for("admin.organizacoes"))
    return render_template("admin/organizacao_form.html", org=org)


@admin_bp.route("/organizacoes/<int:org_id>/delete", methods=["POST"])
@login_required
def organizacao_delete(org_id):
    execute("DELETE FROM organizacoes WHERE id = %s", (org_id,))
    flash("Organização removida.", "success")
    return redirect(url_for("admin.organizacoes"))


# ---------------- PALESTRAS ----------------
@admin_bp.route("/palestras")
@login_required
def palestras():
    rows = query("SELECT * FROM palestras ORDER BY data_realizacao DESC NULLS LAST") or []
    return render_template("admin/palestras.html", palestras=rows)


@admin_bp.route("/palestras/nova", methods=["GET", "POST"])
@login_required
def palestra_nova():
    if request.method == "POST":
        execute(
            """INSERT INTO palestras (titulo, descricao, data_realizacao, local, modalidade, carga_horaria)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                request.form.get("titulo", "").strip(),
                request.form.get("descricao", "").strip(),
                request.form.get("data_realizacao") or None,
                request.form.get("local", "").strip(),
                request.form.get("modalidade", "presencial"),
                request.form.get("carga_horaria") or None,
            ),
        )
        flash("Palestra criada.", "success")
        return redirect(url_for("admin.palestras"))
    return render_template("admin/palestra_form.html", palestra=None)


@admin_bp.route("/palestras/<int:palestra_id>/editar", methods=["GET", "POST"])
@login_required
def palestra_editar(palestra_id):
    palestra = query(
        "SELECT * FROM palestras WHERE id = %s", (palestra_id,), one=True
    )
    if not palestra:
        flash("Palestra não encontrada.", "error")
        return redirect(url_for("admin.palestras"))
    if request.method == "POST":
        execute(
            """UPDATE palestras SET titulo=%s, descricao=%s, data_realizacao=%s, local=%s,
               modalidade=%s, carga_horaria=%s WHERE id=%s""",
            (
                request.form.get("titulo", "").strip(),
                request.form.get("descricao", "").strip(),
                request.form.get("data_realizacao") or None,
                request.form.get("local", "").strip(),
                request.form.get("modalidade", "presencial"),
                request.form.get("carga_horaria") or None,
                palestra_id,
            ),
        )
        flash("Palestra atualizada.", "success")
        return redirect(url_for("admin.palestras"))
    return render_template("admin/palestra_form.html", palestra=palestra)


@admin_bp.route("/palestras/<int:palestra_id>/delete", methods=["POST"])
@login_required
def palestra_delete(palestra_id):
    execute("DELETE FROM palestras WHERE id = %s", (palestra_id,))
    flash("Palestra removida.", "success")
    return redirect(url_for("admin.palestras"))


# ---------------- AVALIAÇÕES ----------------
@admin_bp.route("/avaliacoes")
@login_required
def avaliacoes():
    rows = query(
        """SELECT a.*, p.titulo AS palestra_titulo, o.nome AS organizacao_nome
           FROM avaliacoes a
           LEFT JOIN palestras_organizacoes po ON po.id = a.palestra_organizacao_id
           LEFT JOIN palestras p ON p.id = po.palestra_id
           LEFT JOIN organizacoes o ON o.id = po.organizacao_id
           ORDER BY a.criado_em DESC"""
    ) or []
    return render_template("admin/avaliacoes.html", avaliacoes=rows)


# ---------------- USUÁRIOS ----------------
@admin_bp.route("/usuarios")
@login_required
def usuarios():
    rows = query("SELECT id, email, nome, ativo, criado_em FROM usuarios ORDER BY nome") or []
    return render_template("admin/usuarios.html", usuarios=rows)


@admin_bp.route("/usuarios/novo", methods=["GET", "POST"])
@login_required
def usuario_novo():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "")
        if email and nome and senha:
            senha_hash = generate_password_hash(senha)
            try:
                execute(
                    "INSERT INTO usuarios (email, nome, senha_hash) VALUES (%s, %s, %s)",
                    (email, nome, senha_hash),
                )
                flash("Usuário criado.", "success")
                return redirect(url_for("admin.usuarios"))
            except Exception:
                flash("E-mail já cadastrado.", "error")
        else:
            flash("Preencha todos os campos.", "error")
    return render_template("admin/usuario_form.html", usuario=None)


@admin_bp.route("/usuarios/<int:usuario_id>/delete", methods=["POST"])
@login_required
def usuario_delete(usuario_id):
    if usuario_id == session.get("admin_user_id"):
        flash("Você não pode remover o próprio usuário.", "error")
    else:
        execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        flash("Usuário removido.", "success")
    return redirect(url_for("admin.usuarios"))
