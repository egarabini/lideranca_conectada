"""
Testes para Estratégias de Liderança — Performance Sustentável
"""

import pytest
from lideranca_conectada.estrategias import (
    Competencia,
    EstrategiaLideranca,
    NivelMaturidade,
    PerformanceSustentavel,
    PilarLideranca,
)


class TestEstrategiaLideranca:
    def test_criar_estrategia_basica(self):
        estrategia = EstrategiaLideranca(
            nome="Teste",
            objetivo="Objetivo de teste",
        )
        assert estrategia.nome == "Teste"
        assert estrategia.objetivo == "Objetivo de teste"
        assert estrategia.competencias == []
        assert estrategia.nivel_recomendado == NivelMaturidade.DESENVOLVIMENTO

    def test_lideranca_pelo_proposito(self):
        estrategia = EstrategiaLideranca.lideranca_pelo_proposito()
        assert estrategia.nome == "Liderança pelo Propósito"
        assert len(estrategia.competencias) == 2
        assert estrategia.nivel_recomendado == NivelMaturidade.PROFICIENTE
        for comp in estrategia.competencias:
            assert len(comp.acoes_praticas) > 0

    def test_gestao_por_resultados_humanizados(self):
        estrategia = EstrategiaLideranca.gestao_por_resultados_humanizados()
        assert "Humanizados" in estrategia.nome
        assert len(estrategia.competencias) == 3
        assert estrategia.nivel_recomendado == NivelMaturidade.AVANCADO

    def test_desenvolvimento_continuo_de_talentos(self):
        estrategia = EstrategiaLideranca.desenvolvimento_continuo_de_talentos()
        assert "Talentos" in estrategia.nome
        assert len(estrategia.competencias) == 3

    def test_lideranca_colaborativa_e_sistemica(self):
        estrategia = EstrategiaLideranca.lideranca_colaborativa_e_sistemica()
        assert "Colaborativa" in estrategia.nome
        assert estrategia.nivel_recomendado == NivelMaturidade.REFERENCIA

    def test_resumo_contem_nome_e_competencias(self):
        estrategia = EstrategiaLideranca.lideranca_pelo_proposito()
        resumo = estrategia.resumo()
        assert estrategia.nome in resumo
        assert "Competências:" in resumo
        for comp in estrategia.competencias:
            assert comp.nome in resumo


class TestCompetencia:
    def test_str_inclui_pilar_e_nome(self):
        comp = Competencia(
            nome="Comunicação",
            descricao="Desc",
            pilar=PilarLideranca.PESSOAS,
        )
        resultado = str(comp)
        assert PilarLideranca.PESSOAS.value in resultado
        assert "Comunicação" in resultado


class TestPerformanceSustentavel:
    def test_inicializacao_com_scores_zerados(self):
        ps = PerformanceSustentavel(equipe="Equipe Alpha")
        assert ps.score_geral == 0.0
        assert ps.pontos_de_atencao == []
        assert ps.pontos_fortes == []

    def test_avaliar_dimensao_valida(self):
        ps = PerformanceSustentavel(equipe="Equipe Alpha")
        dim = PerformanceSustentavel.DIMENSOES[0]
        ps.avaliar(dim, 8)
        assert ps.scores[dim] == 8

    def test_avaliar_dimensao_invalida(self):
        ps = PerformanceSustentavel(equipe="Equipe Alpha")
        with pytest.raises(ValueError, match="inválida"):
            ps.avaliar("Dimensão Inexistente", 5)

    def test_avaliar_score_fora_do_intervalo(self):
        ps = PerformanceSustentavel(equipe="Equipe Alpha")
        dim = PerformanceSustentavel.DIMENSOES[0]
        with pytest.raises(ValueError, match="entre 1 e 10"):
            ps.avaliar(dim, 11)
        with pytest.raises(ValueError, match="entre 1 e 10"):
            ps.avaliar(dim, 0)

    def test_score_geral_calculo(self):
        ps = PerformanceSustentavel(equipe="Equipe Beta")
        ps.avaliar(PerformanceSustentavel.DIMENSOES[0], 8)
        ps.avaliar(PerformanceSustentavel.DIMENSOES[1], 6)
        assert ps.score_geral == 7.0

    def test_pontos_de_atencao(self):
        ps = PerformanceSustentavel(equipe="Equipe Beta")
        ps.avaliar(PerformanceSustentavel.DIMENSOES[0], 4)
        ps.avaliar(PerformanceSustentavel.DIMENSOES[1], 8)
        assert PerformanceSustentavel.DIMENSOES[0] in ps.pontos_de_atencao
        assert PerformanceSustentavel.DIMENSOES[1] not in ps.pontos_de_atencao

    def test_pontos_fortes(self):
        ps = PerformanceSustentavel(equipe="Equipe Gama")
        ps.avaliar(PerformanceSustentavel.DIMENSOES[0], 9)
        ps.avaliar(PerformanceSustentavel.DIMENSOES[1], 5)
        assert PerformanceSustentavel.DIMENSOES[0] in ps.pontos_fortes
        assert PerformanceSustentavel.DIMENSOES[1] not in ps.pontos_fortes

    def test_diagnostico_alta_performance(self):
        ps = PerformanceSustentavel(equipe="Equipe Top")
        for dim in PerformanceSustentavel.DIMENSOES:
            ps.avaliar(dim, 9)
        diag = ps.diagnostico()
        assert "alta performance" in diag.lower()

    def test_diagnostico_sem_dados(self):
        ps = PerformanceSustentavel(equipe="Equipe Vazia")
        diag = ps.diagnostico()
        assert "Nenhuma dimensão" in diag
