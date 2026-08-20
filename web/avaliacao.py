from flask import Blueprint, flash, redirect, render_template, request, url_for

from db import execute, query

avaliacao_bp = Blueprint("avaliacao", __name__)


@avaliacao_bp.route("/avaliacao/<int:po_id>", methods=["GET", "POST"])
def avaliar(po_id):
    po = query(
        """SELECT po.id, po.palestra_id, po.organizacao_id, po.data_realizacao,
                  p.titulo AS palestra_titulo, o.nome AS organizacao_nome
           FROM palestras_organizacoes po
           LEFT JOIN palestras p ON p.id = po.palestra_id
           LEFT JOIN organizacoes o ON o.id = po.organizacao_id
           WHERE po.id = %s""",
        (po_id,),
        one=True,
    )
    if not po:
        return render_template("avaliacao/nao_encontrada.html"), 404

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        nota_geral = request.form.get("nota_geral", type=int)
        nota_conteudo = request.form.get("nota_conteudo", type=int)
        nota_aplicabilidade = request.form.get("nota_aplicabilidade", type=int)
        nota_facilitador = request.form.get("nota_facilitador", type=int)
        o_que_aprendeu = request.form.get("o_que_aprendeu", "").strip()
        o_que_vai_aplicar = request.form.get("o_que_vai_aplicar", "").strip()
        sugestoes = request.form.get("sugestoes", "").strip()

        notas = [nota_geral, nota_conteudo, nota_aplicabilidade, nota_facilitador]
        if not nome or not email or any(n is None or n < 1 or n > 5 for n in notas):
            flash("Preencha todos os campos obrigatórios e avalie de 1 a 5.", "error")
            return render_template("avaliacao/form.html", po=po, dados=request.form)

        execute(
            """INSERT INTO avaliacoes (palestra_organizacao_id, nome_respondente, email_respondente,
               nota_geral, nota_conteudo, nota_aplicabilidade, nota_facilitador,
               o_que_aprendeu, o_que_vai_aplicar, sugestoes)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                po_id, nome, email, nota_geral, nota_conteudo,
                nota_aplicabilidade, nota_facilitador,
                o_que_aprendeu, o_que_vai_aplicar, sugestoes,
            ),
        )
        return render_template("avaliacao/obrigado.html", po=po)

    return render_template("avaliacao/form.html", po=po, dados=None)
