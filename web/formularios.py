import functools

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from db import execute, query

formularios_bp = Blueprint("formularios", __name__, url_prefix="/admin/formularios")

TIPOS_RESPOSTA = [
    ("radio", "Múltipla escolha (uma opção)"),
    ("checkbox", "Múltipla escolha (várias opções)"),
    ("escala", "Escala 0-10"),
    ("texto", "Texto aberto"),
]


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_user_id"):
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)

    return wrapped


def _parse_opcoes(form):
    texto = form.get("opcoes_text", "")
    opcoes = [linha.strip() for linha in texto.splitlines() if linha.strip()]
    return "\n".join(opcoes)


@formularios_bp.route("/")
@login_required
def lista():
    formularios = query(
        """SELECT f.*,
                  (SELECT COUNT(*) FROM questoes q WHERE q.formulario_id = f.id) AS n_questoes,
                  (SELECT COUNT(*) FROM palestras p WHERE p.formulario_investigacao_id = f.id) AS n_palestras_inv,
                  (SELECT COUNT(*) FROM palestras p WHERE p.formulario_avaliacao_id = f.id) AS n_palestras_av
           FROM formularios f ORDER BY f.criado_em DESC"""
    ) or []
    return render_template("admin/formularios.html", formularios=formularios)


@formularios_bp.route("/nova", methods=["GET", "POST"])
@login_required
def nova():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        texto_final = request.form.get("texto_final", "").strip()
        tipo = request.form.get("tipo", "investigacao").strip()
        if not titulo:
            flash("Informe o título do formulário.", "error")
        else:
            execute(
                "INSERT INTO formularios (titulo, descricao, tipo, texto_final) VALUES (%s, %s, %s, %s)",
                (titulo, descricao, tipo, texto_final),
            )
            fid = query("SELECT MAX(id) AS id FROM formularios", one=True)["id"]
            flash("Formulário criado. Adicione as questões.", "success")
            return redirect(url_for("formularios.editar", fid=fid))
    return render_template("admin/formulario_form.html", formulario=None, tipos_resposta=TIPOS_RESPOSTA)


@formularios_bp.route("/<int:fid>/editar", methods=["GET", "POST"])
@login_required
def editar(fid):
    formulario = query("SELECT * FROM formularios WHERE id = %s", (fid,), one=True)
    if not formulario:
        flash("Formulário não encontrado.", "error")
        return redirect(url_for("formularios.lista"))
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        texto_final = request.form.get("texto_final", "").strip()
        tipo = request.form.get("tipo", "investigacao").strip()
        ativo = bool(request.form.get("ativo"))
        if not titulo:
            flash("Informe o título do formulário.", "error")
        else:
            execute(
                "UPDATE formularios SET titulo = %s, descricao = %s, texto_final = %s, tipo = %s, ativo = %s WHERE id = %s",
                (titulo, descricao, texto_final, tipo, ativo, fid),
            )
            flash("Formulário atualizado.", "success")
            return redirect(url_for("formularios.editar", fid=fid))
    questoes = query(
        "SELECT * FROM questoes WHERE formulario_id = %s ORDER BY ordem, id", (fid,)
    ) or []
    return render_template(
        "admin/formulario_form.html",
        formulario=formulario,
        questoes=questoes,
        tipos_resposta=TIPOS_RESPOSTA,
    )


@formularios_bp.route("/<int:fid>/delete", methods=["POST"])
@login_required
def delete(fid):
    execute("DELETE FROM formularios WHERE id = %s", (fid,))
    flash("Formulário excluído.", "success")
    return redirect(url_for("formularios.lista"))


@formularios_bp.route("/<int:fid>/questoes/nova", methods=["GET", "POST"])
@login_required
def questao_nova(fid):
    formulario = query("SELECT * FROM formularios WHERE id = %s", (fid,), one=True)
    if not formulario:
        flash("Formulário não encontrado.", "error")
        return redirect(url_for("formularios.lista"))
    if request.method == "POST":
        pergunta = request.form.get("pergunta", "").strip()
        if not pergunta:
            flash("Informe a pergunta.", "error")
        else:
            ordem = request.form.get("ordem", type=int) or 0
            bloco = request.form.get("bloco", "").strip()
            tipo = request.form.get("tipo_resposta", "texto").strip()
            obrigatoria = 1 if request.form.get("obrigatoria") else 0
            tem_outro = 1 if request.form.get("tem_outro") else 0
            opcoes = _parse_opcoes(request.form)
            execute(
                """INSERT INTO questoes
                   (formulario_id, ordem, bloco, pergunta, tipo_resposta, obrigatoria, tem_outro, opcoes)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (fid, ordem, bloco, pergunta, tipo, obrigatoria, tem_outro, opcoes),
            )
            flash("Questão adicionada.", "success")
            return redirect(url_for("formularios.editar", fid=fid))
    return render_template(
        "admin/questao_form.html",
        formulario=formulario,
        questao=None,
        tipos_resposta=TIPOS_RESPOSTA,
    )


@formularios_bp.route("/<int:fid>/questoes/<int:qid>/editar", methods=["GET", "POST"])
@login_required
def questao_editar(fid, qid):
    formulario = query("SELECT * FROM formularios WHERE id = %s", (fid,), one=True)
    questao = query("SELECT * FROM questoes WHERE id = %s AND formulario_id = %s", (qid, fid), one=True)
    if not formulario or not questao:
        flash("Questão não encontrada.", "error")
        return redirect(url_for("formularios.editar", fid=fid))
    if request.method == "POST":
        pergunta = request.form.get("pergunta", "").strip()
        if not pergunta:
            flash("Informe a pergunta.", "error")
        else:
            ordem = request.form.get("ordem", type=int) or 0
            bloco = request.form.get("bloco", "").strip()
            tipo = request.form.get("tipo_resposta", "texto").strip()
            obrigatoria = 1 if request.form.get("obrigatoria") else 0
            tem_outro = 1 if request.form.get("tem_outro") else 0
            opcoes = _parse_opcoes(request.form)
            execute(
                """UPDATE questoes SET ordem = %s, bloco = %s, pergunta = %s, tipo_resposta = %s,
                   obrigatoria = %s, tem_outro = %s, opcoes = %s WHERE id = %s""",
                (ordem, bloco, pergunta, tipo, obrigatoria, tem_outro, opcoes, qid),
            )
            flash("Questão atualizada.", "success")
            return redirect(url_for("formularios.editar", fid=fid))
    return render_template(
        "admin/questao_form.html",
        formulario=formulario,
        questao=questao,
        tipos_resposta=TIPOS_RESPOSTA,
    )


@formularios_bp.route("/<int:fid>/questoes/<int:qid>/delete", methods=["POST"])
@login_required
def questao_delete(fid, qid):
    execute("DELETE FROM questoes WHERE id = %s AND formulario_id = %s", (qid, fid))
    flash("Questão excluída.", "success")
    return redirect(url_for("formularios.editar", fid=fid))
