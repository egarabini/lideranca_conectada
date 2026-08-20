import csv
import functools
import io
import os

from flask import (
    Blueprint,
    Response,
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


@admin_bp.route("/admin")
def admin_index():
    """Rota /admin (sem barra) - redireciona para login ou dashboard"""
    if session.get("admin_user_id"):
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("admin.login"))


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
        """SELECT id, nome as nome, empresa as empresa, cargo as cargo, status, created_at
           FROM leads
           ORDER BY created_at DESC LIMIT 8"""
    ) or []

    # Dados para gráficos
    leads_por_mes = query(
        """SELECT TO_CHAR(created_at, 'YYYY-MM') AS mes, COUNT(*) AS total
           FROM leads GROUP BY mes ORDER BY mes"""
    ) or []

    leads_por_status = query(
        "SELECT status, COUNT(*) AS total FROM leads GROUP BY status"
    ) or []

    avaliacoes_por_palestra = query(
        """SELECT p.titulo, ROUND(AVG(a.nota_geral), 1) AS media, COUNT(a.id) AS total
           FROM avaliacoes a
           JOIN palestras_organizacoes po ON po.id = a.palestra_organizacao_id
           JOIN palestras p ON p.id = po.palestra_id
           GROUP BY p.titulo ORDER BY media DESC"""
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
        leads_por_mes=leads_por_mes,
        leads_por_status=leads_por_status,
        avaliacoes_por_palestra=avaliacoes_por_palestra,
    )


# ---------------- LEADS ----------------
@admin_bp.route("/leads")
@login_required
def leads():
    status = request.args.get("status", "")
    if status:
        rows = query(
            """SELECT l.id, l.status, l.source, l.created_at, l.updated_at,
                  p.nome_completo as nome, p.email as email, p.telefone as whatsapp,
                  p.nome_empresa as empresa, p.cargo_funcao as cargo, p.cidade_uf,
                  o.nome AS organizacao_nome
               FROM leads l
               LEFT JOIN organizacoes o ON o.id = l.organizacao_id
               WHERE l.status = %s ORDER BY l.created_at DESC""",
            (status,),
        ) or []
    else:
        rows = query(
            """SELECT l.id, l.status, l.source, l.created_at, l.updated_at,
                  l.nome as nome, l.email as email, l.whatsapp as whatsapp,
                  l.empresa as empresa, l.cargo as cargo, l.cidade_uf as cidade_uf,
                  o.nome AS organizacao_nome
               FROM leads l
               LEFT JOIN organizacoes o ON o.id = l.organizacao_id
               ORDER BY l.created_at DESC"""
        ) or []
    organizacoes = query("SELECT id, nome FROM organizacoes ORDER BY nome") or []
    return render_template(
        "admin/leads.html",
        leads=rows,
        status=status,
        lead_status=LEAD_STATUS,
        organizacoes=organizacoes,
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


@admin_bp.route("/leads/<int:lead_id>/vincular", methods=["POST"])
@login_required
def lead_vincular(lead_id):
    organizacao_id = request.form.get("organizacao_id", type=int)
    if organizacao_id:
        execute(
            "UPDATE leads SET organizacao_id = %s, updated_at = NOW() WHERE id = %s",
            (organizacao_id, lead_id),
        )
        flash("Lead vinculado à organização.", "success")
    return redirect(request.referrer or url_for("admin.leads"))


@admin_bp.route("/leads/exportar")
@login_required
def leads_exportar():
    status = request.args.get("status", "")
    if status:
        rows = query(
            """SELECT l.id, l.status, l.created_at,
                  l.nome as nome, l.email as email, l.whatsapp as whatsapp,
                  l.empresa as empresa, l.cargo as cargo, l.cidade_uf as cidade_uf
               FROM leads l
               WHERE l.status = %s ORDER BY l.created_at DESC""",
            (status,)
        ) or []
    else:
        rows = query(
            """SELECT l.id, l.status, l.created_at,
                  l.nome as nome, l.email as email, l.whatsapp as whatsapp,
                  l.empresa as empresa, l.cargo as cargo, l.cidade_uf as cidade_uf
               FROM leads l
               ORDER BY l.created_at DESC"""
        ) or []

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["ID", "Nome", "E-mail", "WhatsApp", "Empresa", "Cargo",
                     "Cidade/UF", "Status", "Data"])
    for r in rows:
        writer.writerow([
            r["id"], r["nome"], r["email"], r["whatsapp"], r["empresa"],
            r["cargo"], r["cidade_uf"] or "",
            r["status"], r["created_at"].strftime("%d/%m/%Y %H:%M") if r["created_at"] else "",
        ])

    filename = "leads.csv"
    if status:
        filename = f"leads_{status}.csv"

    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ---------------- PESSOAS ----------------
@admin_bp.route("/pessoas")
@login_required
def pessoas():
    rows = query(
        """SELECT p.id, p.nome_completo, p.email, p.telefone, p.ind_whatsapp,
                  p.nome_empresa, p.cargo_funcao, p.cidade_uf, p.criado_em
           FROM pessoas p
           ORDER BY p.criado_em DESC"""
    ) or []
    total = query("SELECT COUNT(*) AS c FROM pessoas", one=True)["c"]
    return render_template("admin/pessoas.html", pessoas=rows, total=total)


@admin_bp.route("/pessoas/<int:pessoa_id>/editar", methods=["GET", "POST"])
@login_required
def pessoa_editar(pessoa_id):
    pessoa = query("SELECT * FROM pessoas WHERE id = %s", (pessoa_id,), one=True)
    if not pessoa:
        flash("Pessoa não encontrada.", "error")
        return redirect(url_for("admin.pessoas"))

    if request.method == "POST":
        nome_completo = request.form.get("nome_completo", "").strip()
        email = request.form.get("email", "").strip()
        telefone = request.form.get("telefone", "").strip()
        nome_empresa = request.form.get("nome_empresa", "").strip()
        cargo_funcao = request.form.get("cargo_funcao", "").strip()
        cidade_uf = request.form.get("cidade_uf", "").strip()
        ind_whatsapp = bool(request.form.get("ind_whatsapp"))

        if not nome_completo or not email:
            flash("Nome e e-mail são obrigatórios.", "error")
        else:
            execute(
                """UPDATE pessoas SET nome_completo = %s, email = %s, telefone = %s,
                   ind_whatsapp = %s, nome_empresa = %s, cargo_funcao = %s, cidade_uf = %s,
                   alterado_em = NOW()
                   WHERE id = %s""",
                (nome_completo, email, telefone, ind_whatsapp, nome_empresa,
                 cargo_funcao, cidade_uf, pessoa_id),
            )
            flash("Pessoa atualizada.", "success")
            return redirect(url_for("admin.pessoas"))

    return render_template("admin/pessoa_form.html", pessoa=pessoa)


@admin_bp.route("/pessoas/<int:pessoa_id>/delete", methods=["POST"])
@login_required
def pessoa_delete(pessoa_id):
    execute("DELETE FROM pessoas WHERE id = %s", (pessoa_id,))
    flash("Pessoa excluída.", "success")
    return redirect(url_for("admin.pessoas"))


# ---------------- PARTICIPANTES ----------------
@admin_bp.route("/participantes")
@login_required
def participantes():
    # Verificar se há filtro por palestra
    palestra_filtro = request.args.get("palestra", type=int)

    # Construir query base
    if palestra_filtro:
        rows = query(
            """SELECT pa.id, pa.palestra_id, pa.criado_em,
                      p.nome_completo, p.email, p.telefone,
                      pal.titulo AS palestra_titulo, o.nome AS organizacao_nome
               FROM participantes pa
               JOIN pessoas p ON pa.pessoa_id = p.id
               JOIN palestras pal ON pal.id = pa.palestra_id
               LEFT JOIN palestras_organizacoes po ON po.palestra_id = pa.palestra_id
               LEFT JOIN organizacoes o ON o.id = po.organizacao_id
               WHERE pa.palestra_id = %s
               ORDER BY pa.criado_em DESC""",
            (palestra_filtro,)
        ) or []
        total = query("SELECT COUNT(*) AS c FROM participantes WHERE palestra_id = %s",
                      (palestra_filtro,), one=True)["c"]
    else:
        rows = query(
            """SELECT pa.id, pa.palestra_id, pa.criado_em,
                      p.nome_completo, p.email, p.telefone,
                      pal.titulo AS palestra_titulo, o.nome AS organizacao_nome
               FROM participantes pa
               JOIN pessoas p ON pa.pessoa_id = p.id
               JOIN palestras pal ON pal.id = pa.palestra_id
               LEFT JOIN palestras_organizacoes po ON po.palestra_id = pa.palestra_id
               LEFT JOIN organizacoes o ON o.id = po.organizacao_id
               ORDER BY pa.criado_em DESC"""
        ) or []
        total = query("SELECT COUNT(*) AS c FROM participantes", one=True)["c"]

    # Obter palestras para filtro
    palestras = query("SELECT id, titulo FROM palestras WHERE ativo = TRUE ORDER BY titulo") or []

    return render_template("admin/participantes.html", participantes=rows,
                          total=total, palestras=palestras, palestra_filtro=palestra_filtro)


@admin_bp.route("/participantes/novo", methods=["GET", "POST"])
@login_required
def participantes_criar():
    if request.method == "POST":
        palestra_id = request.form.get("palestra_id", type=int)
        pessoa_id = request.form.get("pessoa_id", type=int)

        if not palestra_id or not pessoa_id:
            flash("Selecione uma palestra e uma pessoa.", "error")
        else:
            try:
                execute(
                    "INSERT INTO participantes (palestra_id, pessoa_id) VALUES (%s, %s)",
                    (palestra_id, pessoa_id),
                )
                flash("Participante registrado.", "success")
                return redirect(url_for("admin.participantes"))
            except Exception:
                flash("Este participante já está registrado nesta palestra.", "error")

    palestras = query("SELECT id, titulo FROM palestras WHERE ativo = TRUE ORDER BY titulo") or []
    pessoas = query("SELECT id, nome_completo, email FROM pessoas ORDER BY nome_completo") or []
    return render_template("admin/participante_form.html",
                          palestras=palestras, pessoas=pessoas)


@admin_bp.route("/participantes/<int:participante_id>/editar", methods=["POST"])
@login_required
def participantes_editar(participante_id):
    participante = query(
        "SELECT * FROM participantes WHERE id = %s",
        (participante_id,), one=True
    )
    if not participante:
        flash("Participante não encontrado.", "error")
        return redirect(url_for("admin.participantes"))

    palestra_id = request.form.get("palestra_id", type=int)
    pessoa_id = request.form.get("pessoa_id", type=int)

    if not palestra_id or not pessoa_id:
        flash("Selecione uma palestra e uma pessoa.", "error")
    else:
        execute(
            "UPDATE participantes SET palestra_id = %s, pessoa_id = %s WHERE id = %s",
            (palestra_id, pessoa_id, participante_id),
        )
        flash("Participante atualizado.", "success")

    return redirect(url_for("admin.participantes"))


@admin_bp.route("/participantes/<int:participante_id>/delete", methods=["POST"])
@login_required
def participantes_excluir(participante_id):
    execute("DELETE FROM participantes WHERE id = %s", (participante_id,))
    flash("Participante excluído.", "success")
    return redirect(url_for("admin.participantes"))


@admin_bp.route("/participantes/<int:participante_id>/respostas")
@login_required
def participante_respostas(participante_id):
    # Buscar dados do participante
    participante = query(
        """SELECT pa.id, pa.palestra_id, pa.criado_em,
                  p.nome_completo, p.email,
                  pal.titulo AS palestra_titulo, pal.formulario_investigacao_id,
                  o.nome AS organizacao_nome
           FROM participantes pa
           JOIN pessoas p ON pa.pessoa_id = p.id
           JOIN palestras pal ON pal.id = pa.palestra_id
           LEFT JOIN palestras_organizacoes po ON po.palestra_id = pa.palestra_id
           LEFT JOIN organizacoes o ON o.id = po.organizacao_id
           WHERE pa.id = %s""",
        (participante_id,), one=True
    )

    if not participante:
        flash("Participante não encontrado.", "error")
        return redirect(url_for("admin.participantes"))

    # Buscar respostas do formulário para este participante específico
    respostas = []
    if participante.get("formulario_investigacao_id"):
        respostas = query(
            """SELECT q.pergunta, q.bloco, r.valor, q.tipo_resposta
               FROM respostas_formulario r
               JOIN questoes q ON q.id = r.questao_id
               WHERE q.formulario_id = %s AND r.participante_id = %s
               ORDER BY q.ordem""",
            (participante["formulario_investigacao_id"], participante_id)
        ) or []

    return render_template("admin/participante_respostas.html",
                          participante=participante, respostas=respostas)


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

    # Buscar palestras já realizadas nesta organização
    palestras_realizadas = query(
        """SELECT po.id AS po_id, po.data_realizacao, po.observacoes,
                  p.id AS palestra_id, p.titulo AS palestra_titulo
           FROM palestras_organizacoes po
           JOIN palestras p ON p.id = po.palestra_id
           WHERE po.organizacao_id = %s
           ORDER BY po.data_realizacao DESC NULLS LAST, p.titulo""",
        (org_id,),
    ) or []

    # Buscar todas as palestras disponíveis
    todas_palestras = query("SELECT id, titulo FROM palestras WHERE ativo = TRUE ORDER BY titulo") or []

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
    # Debug
    print(f"DEBUG organizacao_editar: org_id={org_id}")
    print(f"DEBUG palestras_realizadas: {len(palestras_realizadas)} itens")
    print(f"DEBUG todas_palestras: {len(todas_palestras)} itens")

    return render_template("admin/organizacao_form.html", org=org, palestras_realizadas=palestras_realizadas, todas_palestras=todas_palestras)


@admin_bp.route("/organizacoes/<int:org_id>/palestras/adicionar", methods=["POST"])
@login_required
def organizacao_palestra_adicionar(org_id):
    """Associa uma palestra a uma organização"""
    palestra_id = request.form.get("palestra_id", type=int)
    data_realizacao = request.form.get("data_realizacao", "").strip() or None
    observacoes = request.form.get("observacoes", "").strip() or None

    if not palestra_id:
        flash("Selecione uma palestra.", "error")
        return redirect(url_for("admin.organizacao_editar", org_id=org_id))

    try:
        execute(
            """INSERT INTO palestras_organizacoes (palestra_id, organizacao_id, data_realizacao, observacoes)
               VALUES (%s, %s, %s, %s)""",
            (palestra_id, org_id, data_realizacao, observacoes),
        )
        flash("Palestra associada à organização.", "success")
    except Exception:
        flash("Esta palestra já está associada a esta organização.", "error")
    return redirect(url_for("admin.organizacao_editar", org_id=org_id))


@admin_bp.route("/organizacoes/palestras/<int:po_id>/remover", methods=["POST"])
@login_required
def organizacao_palestra_remover(po_id):
    """Remove a associação entre palestra e organização"""
    # Buscar a organização_id antes de deletar para redirecionar corretamente
    po = query("SELECT organizacao_id FROM palestras_organizacoes WHERE id = %s", (po_id,), one=True)
    if not po:
        flash("Associação não encontrada.", "error")
        return redirect(url_for("admin.organizacoes"))

    execute("DELETE FROM palestras_organizacoes WHERE id = %s", (po_id,))
    flash("Palestra removida da organização.", "success")
    return redirect(url_for("admin.organizacao_editar", org_id=po["organizacao_id"]))


@admin_bp.route("/organizacoes/palestras/<int:po_id>/editar", methods=["POST"])
@login_required
def organizacao_palestra_editar(po_id):
    """Edita os dados de uma realização de palestra (data, observações)"""
    po = query(
        """SELECT po.id, po.organizacao_id, po.palestra_id, po.data_realizacao, po.observacoes,
                  p.titulo AS palestra_titulo, o.nome AS organizacao_nome
           FROM palestras_organizacoes po
           JOIN palestras p ON p.id = po.palestra_id
           JOIN organizacoes o ON o.id = po.organizacao_id
           WHERE po.id = %s""",
        (po_id,),
        one=True,
    )

    if not po:
        flash("Associação não encontrada.", "error")
        return redirect(url_for("admin.organizacoes"))

    data_realizacao = request.form.get("data_realizacao", "").strip() or None
    observacoes = request.form.get("observacoes", "").strip() or None

    execute(
        """UPDATE palestras_organizacoes SET data_realizacao = %s, observacoes = %s WHERE id = %s""",
        (data_realizacao, observacoes, po_id),
    )
    flash("Dados da realização atualizados.", "success")
    return redirect(url_for("admin.organizacao_editar", org_id=po["organizacao_id"]))


# ---------------- PALESTRAS ----------------


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
    vinculos = query(
        """SELECT po.id, po.palestra_id, po.organizacao_id, po.data_realizacao,
                  p.titulo AS palestra_titulo, o.nome AS organizacao_nome
           FROM palestras_organizacoes po
           LEFT JOIN palestras p ON p.id = po.palestra_id
           LEFT JOIN organizacoes o ON o.id = po.organizacao_id
           ORDER BY po.palestra_id"""
    ) or []
    organizacoes = query("SELECT id, nome FROM organizacoes ORDER BY nome") or []
    formularios = query(
        "SELECT id, titulo, tipo FROM formularios WHERE ativo = TRUE ORDER BY titulo"
    ) or []
    participantes = query(
        """SELECT pa.id, pa.palestra_id, pa.criado_em,
                  pes.nome_completo as nome, pes.email,
                  pal.titulo AS palestra_titulo
           FROM participantes pa
           LEFT JOIN palestras pal ON pal.id = pa.palestra_id
           LEFT JOIN pessoas pes ON pes.id = pa.pessoa_id
           ORDER BY pa.palestra_id, pes.nome_completo"""
    ) or []
    return render_template(
        "admin/palestras.html",
        palestras=rows,
        vinculos=vinculos,
        organizacoes=organizacoes,
        formularios=formularios,
        participantes=participantes,
    )


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

    # Buscar organizações onde esta palestra foi realizada
    organizacoes_realizadas = query(
        """SELECT po.id AS po_id, po.data_realizacao, po.observacoes,
                  o.id AS organizacao_id, o.nome AS organizacao_nome
           FROM palestras_organizacoes po
           JOIN organizacoes o ON o.id = po.organizacao_id
           WHERE po.palestra_id = %s
           ORDER BY po.data_realizacao DESC NULLS LAST, o.nome""",
        (palestra_id,),
    ) or []

    # Buscar todas as organizações disponíveis
    todas_organizacoes = query("SELECT id, nome FROM organizacoes WHERE ativo = TRUE ORDER BY nome") or []

    # Buscar formulários disponíveis para associação
    formularios_investigacao = query(
        "SELECT id, titulo FROM formularios WHERE tipo = 'investigacao' AND ativo = TRUE ORDER BY titulo"
    ) or []
    formularios_avaliacao = query(
        "SELECT id, titulo FROM formularios WHERE tipo = 'avaliacao' AND ativo = TRUE ORDER BY titulo"
    ) or []

    if request.method == "POST":
        execute(
            """UPDATE palestras SET titulo=%s, descricao=%s, data_realizacao=%s, local=%s,
               modalidade=%s, carga_horaria=%s, formulario_investigacao_id=%s, formulario_avaliacao_id=%s
               WHERE id=%s""",
            (
                request.form.get("titulo", "").strip(),
                request.form.get("descricao", "").strip(),
                request.form.get("data_realizacao") or None,
                request.form.get("local", "").strip(),
                request.form.get("modalidade", "presencial"),
                request.form.get("carga_horaria") or None,
                request.form.get("formulario_investigacao_id") or None,
                request.form.get("formulario_avaliacao_id") or None,
                palestra_id,
            ),
        )
        flash("Palestra atualizada.", "success")
        return redirect(url_for("admin.palestras"))

    return render_template(
        "admin/palestra_form.html",
        palestra=palestra,
        organizacoes_realizadas=organizacoes_realizadas,
        todas_organizacoes=todas_organizacoes,
        formularios_investigacao=formularios_investigacao,
        formularios_avaliacao=formularios_avaliacao,
    )


@admin_bp.route("/palestras/<int:palestra_id>/organizacoes/adicionar", methods=["POST"])
@login_required
def palestra_organizacao_adicionar(palestra_id):
    """Associa uma organização a uma palestra"""
    organizacao_id = request.form.get("organizacao_id", type=int)
    data_realizacao = request.form.get("data_realizacao", "").strip() or None
    observacoes = request.form.get("observacoes", "").strip() or None

    if not organizacao_id:
        flash("Selecione uma organização.", "error")
        return redirect(url_for("admin.palestra_editar", palestra_id=palestra_id))

    try:
        execute(
            """INSERT INTO palestras_organizacoes (palestra_id, organizacao_id, data_realizacao, observacoes)
               VALUES (%s, %s, %s, %s)""",
            (palestra_id, organizacao_id, data_realizacao, observacoes),
        )
        flash("Organização associada à palestra.", "success")
    except Exception:
        flash("Esta organização já está associada a esta palestra.", "error")
    return redirect(url_for("admin.palestra_editar", palestra_id=palestra_id))


@admin_bp.route("/palestras/organizacoes/<int:po_id>/remover", methods=["POST"])
@login_required
def palestra_organizacao_remover(po_id):
    """Remove a associação entre palestra e organização"""
    # Buscar a palestra_id antes de deletar para redirecionar corretamente
    po = query("SELECT palestra_id FROM palestras_organizacoes WHERE id = %s", (po_id,), one=True)
    if not po:
        flash("Associação não encontrada.", "error")
        return redirect(url_for("admin.palestras"))

    execute("DELETE FROM palestras_organizacoes WHERE id = %s", (po_id,))
    flash("Organização removida da palestra.", "success")
    return redirect(url_for("admin.palestra_editar", palestra_id=po["palestra_id"]))


@admin_bp.route("/palestras/organizacoes/<int:po_id>/editar", methods=["POST"])
@login_required
def palestra_organizacao_editar(po_id):
    """Edita os dados de uma realização (data, observações)"""
    po = query(
        """SELECT po.id, po.palestra_id, po.organizacao_id, po.data_realizacao, po.observacoes,
                  p.titulo AS palestra_titulo, o.nome AS organizacao_nome
           FROM palestras_organizacoes po
           JOIN palestras p ON p.id = po.palestra_id
           JOIN organizacoes o ON o.id = po.organizacao_id
           WHERE po.id = %s""",
        (po_id,),
        one=True,
    )

    if not po:
        flash("Associação não encontrada.", "error")
        return redirect(url_for("admin.palestras"))

    data_realizacao = request.form.get("data_realizacao", "").strip() or None
    observacoes = request.form.get("observacoes", "").strip() or None

    execute(
        """UPDATE palestras_organizacoes SET data_realizacao = %s, observacoes = %s WHERE id = %s""",
        (data_realizacao, observacoes, po_id),
    )
    flash("Dados da realização atualizados.", "success")
    return redirect(url_for("admin.palestra_editar", palestra_id=po["palestra_id"]))


@admin_bp.route("/palestras/<int:palestra_id>/delete", methods=["POST"])
@login_required
def palestra_delete(palestra_id):
    execute("DELETE FROM palestras WHERE id = %s", (palestra_id,))
    flash("Palestra removida.", "success")
    return redirect(url_for("admin.palestras"))


@admin_bp.route("/palestras/<int:palestra_id>/vincular", methods=["POST"])
@login_required
def palestra_vincular(palestra_id):
    organizacao_id = request.form.get("organizacao_id", type=int)
    data_realizacao = request.form.get("data_realizacao") or None
    if organizacao_id:
        try:
            execute(
                """INSERT INTO palestras_organizacoes (palestra_id, organizacao_id, data_realizacao)
                   VALUES (%s, %s, %s)""",
                (palestra_id, organizacao_id, data_realizacao),
            )
            flash("Organização vinculada à palestra.", "success")
        except Exception:
            flash("Este vínculo já existe.", "error")
    return redirect(url_for("admin.palestras"))


@admin_bp.route("/palestras/<int:palestra_id>/formulario", methods=["POST"])
@login_required
def palestra_formulario(palestra_id):
    inv = request.form.get("formulario_investigacao_id", type=int)
    av = request.form.get("formulario_avaliacao_id", type=int)
    execute(
        "UPDATE palestras SET formulario_investigacao_id = %s, formulario_avaliacao_id = %s WHERE id = %s",
        (inv or None, av or None, palestra_id),
    )
    flash("Formulários associados à palestra.", "success")
    return redirect(url_for("admin.palestras"))


@admin_bp.route("/vinculos/<int:vinculo_id>/delete", methods=["POST"])
@login_required
def vinculo_delete(vinculo_id):
    execute("DELETE FROM palestras_organizacoes WHERE id = %s", (vinculo_id,))
    flash("Vínculo removido.", "success")
    return redirect(url_for("admin.palestras"))


# ---------------- PARTICIPANTES ----------------
@admin_bp.route("/palestras/<int:palestra_id>/participantes", methods=["POST"])
@login_required
def participante_novo(palestra_id):
    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip().lower()
    if not nome or not email:
        flash("Informe nome e e-mail do participante.", "error")
    else:
        try:
            # Verificar se a pessoa já existe pelo e-mail
            pessoa = query("SELECT id FROM pessoas WHERE LOWER(email) = %s", (email,), one=True)

            if pessoa:
                pessoa_id = pessoa["id"]
            else:
                # Criar nova pessoa
                execute(
                    "INSERT INTO pessoas (nome_completo, email, telefone, cidade_uf) VALUES (%s, %s, %s, %s)",
                    (nome, email, "", ""),
                )
                pessoa_id = query("SELECT lastval()")[0]["lastval"]

            # Criar vínculo participante
            execute(
                "INSERT INTO participantes (palestra_id, pessoa_id) VALUES (%s, %s)",
                (palestra_id, pessoa_id),
            )
            flash("Participante adicionado.", "success")
        except Exception as e:
            flash("Este e-mail já está cadastrado nesta palestra.", "error")
    return redirect(url_for("admin.palestras"))


@admin_bp.route("/participantes/<int:participante_id>/editar", methods=["POST"])
@login_required
def participante_editar(participante_id):
    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip().lower()
    if not nome or not email:
        flash("Informe nome e e-mail do participante.", "error")
    else:
        try:
            # Atualizar dados da pessoa
            execute(
                "UPDATE pessoas SET nome_completo = %s, email = %s WHERE id = (SELECT pessoa_id FROM participantes WHERE id = %s)",
                (nome, email, participante_id),
            )
            flash("Participante atualizado.", "success")
        except Exception:
            flash("Erro ao atualizar participante.", "error")
    return redirect(url_for("admin.palestras"))


@admin_bp.route("/participantes/<int:participante_id>/delete", methods=["POST"])
@login_required
def participante_delete(participante_id):
    execute("DELETE FROM participantes WHERE id = %s", (participante_id,))
    flash("Participante removido.", "success")
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


# ---------------- INVESTIGAÇÕES ----------------
@admin_bp.route("/investigacoes")
@login_required
def investigacoes():
    # Lista todas as respostas de formulários de investigação
    rows = query(
        """SELECT r.id,
                  r.nome_respondente,
                  r.email_respondente,
                  r.cargo,
                  r.criado_em,
                  f.titulo AS formulario_titulo,
                  p.titulo AS palestra_titulo,
                  o.nome AS organizacao_nome
           FROM respostas_formulario r
           LEFT JOIN questoes q ON q.id = r.questao_id
           LEFT JOIN formularios f ON f.id = r.formulario_id
           LEFT JOIN palestras_organizacoes po ON po.id = r.palestra_organizacao_id
           LEFT JOIN palestras p ON p.id = po.palestra_id
           LEFT JOIN organizacoes o ON o.id = po.organizacao_id
           WHERE f.tipo = 'investigacao'
           ORDER BY r.criado_em DESC"""
    ) or []
    return render_template("admin/investigacoes.html", investigacoes=rows)


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


@admin_bp.route("/trocar-senha", methods=["GET", "POST"])
@login_required
def trocar_senha():
    user_id = session.get("admin_user_id")
    if request.method == "POST":
        senha_atual = request.form.get("senha_atual", "")
        nova_senha = request.form.get("nova_senha", "")
        confirmar = request.form.get("confirmar_senha", "")

        user = query("SELECT * FROM usuarios WHERE id = %s", (user_id,), one=True)
        if not user or not check_password_hash(user["senha_hash"], senha_atual):
            flash("Senha atual incorreta.", "error")
        elif len(nova_senha) < 6:
            flash("A nova senha deve ter pelo menos 6 caracteres.", "error")
        elif nova_senha != confirmar:
            flash("A confirmação não confere com a nova senha.", "error")
        else:
            execute(
                "UPDATE usuarios SET senha_hash = %s WHERE id = %s",
                (generate_password_hash(nova_senha), user_id),
            )
            flash("Senha alterada com sucesso.", "success")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/trocar_senha.html")
