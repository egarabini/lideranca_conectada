from flask import Blueprint, flash, render_template, request

from db import execute, query

investigacao_bp = Blueprint("investigacao", __name__)


def _get_po(po_id):
    return query(
        """SELECT po.id, po.palestra_id, po.organizacao_id, po.data_realizacao,
                  p.titulo AS palestra_titulo, o.nome AS organizacao_nome,
                  p.formulario_investigacao_id
           FROM palestras_organizacoes po
           LEFT JOIN palestras p ON p.id = po.palestra_id
           LEFT JOIN organizacoes o ON o.id = po.organizacao_id
           WHERE po.id = %s""",
        (po_id,),
        one=True,
    )


def _get_questoes(formulario_id):
    return query(
        "SELECT * FROM questoes WHERE formulario_id = %s ORDER BY ordem, id",
        (formulario_id,),
    ) or []


def _get_formulario(formulario_id):
    return query(
        "SELECT * FROM formularios WHERE id = %s AND ativo = TRUE", (formulario_id,), one=True
    )


@investigacao_bp.route("/investigacao/<int:po_id>", methods=["GET", "POST"])
def responder(po_id):
    po = _get_po(po_id)
    if not po:
        return render_template("investigacao/nao_encontrada.html"), 404

    formulario = _get_formulario(po["formulario_investigacao_id"])
    if not formulario:
        return render_template("investigacao/nao_encontrada.html"), 404

    questoes = _get_questoes(formulario["id"])

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        cargo = request.form.get("cargo", "").strip()
        departamento = request.form.get("departamento", "").strip()

        if not nome or not email:
            flash("Preencha nome e e-mail.", "error")
            return render_template(
                "investigacao/form.html", po=po, formulario=formulario,
                questoes=questoes, dados=request.form,
            )

        # Valida obrigatórias
        for q in questoes:
            if not q["obrigatoria"]:
                continue
            valor = _valor_questao(q, request.form)
            if not valor:
                flash("Preencha todos os campos obrigatórios.", "error")
                return render_template(
                    "investigacao/form.html", po=po, formulario=formulario,
                    questoes=questoes, dados=request.form,
                )

        # Persiste uma linha por questão
        for q in questoes:
            valor = _valor_questao(q, request.form)
            if valor is None:
                continue
            execute(
                """INSERT INTO respostas_formulario
                   (formulario_id, questao_id, palestra_organizacao_id, nome_respondente,
                    email_respondente, cargo, departamento, valor)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (formulario["id"], q["id"], po_id, nome, email, cargo, departamento, valor),
            )
        return render_template("investigacao/obrigado.html", po=po, formulario=formulario)

    return render_template(
        "investigacao/form.html", po=po, formulario=formulario,
        questoes=questoes, dados=None,
    )


def _valor_questao(q, form):
    tipo = q["tipo_resposta"]
    if tipo == "checkbox":
        vals = form.getlist(f"q_{q['id']}")
        if not vals:
            return None
        if q["tem_outro"] and "Outro" in vals:
            outro = form.get(f"q_{q['id']}_outro", "").strip()
            vals = [v for v in vals if v != "Outro"]
            if outro:
                vals.append(f"Outro: {outro}")
        return ", ".join(vals)
    if tipo == "escala":
        v = form.get(f"q_{q['id']}", type=int)
        return v if v is not None else None
    v = form.get(f"q_{q['id']}", "").strip()
    if not v:
        return None
    if q["tem_outro"] and v == "Outro":
        outro = form.get(f"q_{q['id']}_outro", "").strip()
        return f"Outro: {outro}" if outro else "Outro"
    return v
