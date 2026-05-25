"""
Testes para Indicadores de Performance de Liderança
"""

import pytest
from lideranca_conectada.indicadores import (
    IndicadoresPerformance,
    PainelLideranca,
    StatusIndicador,
    TipoIndicador,
)


class TestIndicadoresPerformance:
    def test_status_sem_dados(self):
        ind = IndicadoresPerformance(
            nome="KPI Teste",
            descricao="Desc",
            tipo=TipoIndicador.RESULTADO,
            unidade="%",
            meta=80.0,
        )
        assert ind.status == StatusIndicador.SEM_DADOS
        assert ind.variacao_percentual is None

    def test_status_acima_meta(self):
        ind = IndicadoresPerformance(
            nome="KPI Teste",
            descricao="Desc",
            tipo=TipoIndicador.RESULTADO,
            unidade="%",
            meta=80.0,
            valor_atual=90.0,
        )
        assert ind.status == StatusIndicador.ACIMA_META

    def test_status_na_meta(self):
        ind = IndicadoresPerformance(
            nome="KPI Teste",
            descricao="Desc",
            tipo=TipoIndicador.RESULTADO,
            unidade="%",
            meta=80.0,
            valor_atual=75.0,  # 6.25% abaixo — dentro da tolerância de 10%
        )
        assert ind.status == StatusIndicador.NA_META

    def test_status_atencao(self):
        ind = IndicadoresPerformance(
            nome="KPI Teste",
            descricao="Desc",
            tipo=TipoIndicador.RESULTADO,
            unidade="%",
            meta=80.0,
            valor_atual=68.0,  # 15% abaixo — atenção (10–20%)
        )
        assert ind.status == StatusIndicador.ATENCAO

    def test_status_abaixo_meta(self):
        ind = IndicadoresPerformance(
            nome="KPI Teste",
            descricao="Desc",
            tipo=TipoIndicador.RESULTADO,
            unidade="%",
            meta=80.0,
            valor_atual=50.0,  # 37.5% abaixo — crítico
        )
        assert ind.status == StatusIndicador.ABAIXO_META

    def test_variacao_percentual(self):
        ind = IndicadoresPerformance(
            nome="KPI Teste",
            descricao="Desc",
            tipo=TipoIndicador.RESULTADO,
            unidade="%",
            meta=100.0,
            valor_atual=90.0,
        )
        assert ind.variacao_percentual == -10.0

    def test_atualizar_valor(self):
        ind = IndicadoresPerformance(
            nome="KPI Teste",
            descricao="Desc",
            tipo=TipoIndicador.RESULTADO,
            unidade="%",
            meta=80.0,
        )
        ind.atualizar(85.0)
        assert ind.valor_atual == 85.0
        assert ind.status == StatusIndicador.ACIMA_META

    def test_str_com_dados(self):
        ind = IndicadoresPerformance(
            nome="NPS",
            descricao="Desc",
            tipo=TipoIndicador.RESULTADO,
            unidade="pts",
            meta=50.0,
            valor_atual=60.0,
        )
        resultado = str(ind)
        assert "NPS" in resultado
        assert "60.0" in resultado


class TestPainelLideranca:
    def test_painel_padrao_criado_com_indicadores(self):
        painel = PainelLideranca.painel_padrao("Ana Lima", "Equipe Comercial")
        assert painel.nome_lider == "Ana Lima"
        assert painel.equipe == "Equipe Comercial"
        assert len(painel.indicadores) > 0

    def test_adicionar_indicador_customizado(self):
        painel = PainelLideranca(nome_lider="Bob", equipe="Dev")
        ind = IndicadoresPerformance(
            nome="Velocidade Scrum",
            descricao="Story points por sprint",
            tipo=TipoIndicador.PROCESSO,
            unidade="SP",
            meta=40.0,
        )
        painel.adicionar_indicador(ind)
        assert len(painel.indicadores) == 1

    def test_atualizar_indicador_existente(self):
        painel = PainelLideranca.painel_padrao("Carlos", "Equipe TI")
        painel.atualizar_indicador("Atingimento de Metas", 85.0)
        for ind in painel.indicadores:
            if ind.nome == "Atingimento de Metas":
                assert ind.valor_atual == 85.0
                break

    def test_atualizar_indicador_inexistente(self):
        painel = PainelLideranca.painel_padrao("Carlos", "Equipe TI")
        with pytest.raises(KeyError, match="Indicador Inexistente"):
            painel.atualizar_indicador("Indicador Inexistente", 10.0)

    def test_score_saude_sem_dados(self):
        painel = PainelLideranca(nome_lider="Vazio", equipe="Sem dados")
        assert painel.score_saude_lideranca == 0.0

    def test_score_saude_todos_acima_meta(self):
        painel = PainelLideranca.painel_padrao("Líder Excelente", "Equipe Perfeita")
        for ind in painel.indicadores:
            ind.atualizar(ind.meta * 1.1)  # 10% acima da meta
        assert painel.score_saude_lideranca == 100.0

    def test_score_saude_todos_abaixo_meta(self):
        painel = PainelLideranca.painel_padrao("Líder em Crise", "Equipe Crítica")
        for ind in painel.indicadores:
            ind.atualizar(ind.meta * 0.5)  # 50% abaixo da meta
        # Score deve ser baixo — abaixo de 60 (mix de ABAIXO_META=20 e ATENCAO=50)
        assert painel.score_saude_lideranca < 60.0

    def test_resumo_status_agrupa_corretamente(self):
        painel = PainelLideranca.painel_padrao("Gestor", "Time")
        painel.atualizar_indicador("Atingimento de Metas", 90.0)  # acima da meta
        resumo = painel.resumo_status
        assert "Atingimento de Metas" in resumo[StatusIndicador.ACIMA_META]

    def test_relatorio_contem_cabecalho(self):
        painel = PainelLideranca.painel_padrao("Maria", "Equipe Alpha")
        relatorio = painel.gerar_relatorio()
        assert "Maria" in relatorio
        assert "Equipe Alpha" in relatorio
        assert "Score de Saúde" in relatorio
