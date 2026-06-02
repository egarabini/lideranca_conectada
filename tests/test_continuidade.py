"""
Testes para Continuidade do Negócio — Liderança Conectada 360 Graus
"""

import pytest
from lideranca_conectada.continuidade import (
    NivelRisco,
    PlanoAcaoContinuidade,
    PlanoContinuidade,
    RiscoOrganizacional,
    StatusPlano,
)


class TestRiscoOrganizacional:
    def test_score_risco_calculo(self):
        risco = RiscoOrganizacional(
            nome="Risco Teste",
            descricao="Desc",
            nivel=NivelRisco.MEDIO,
            probabilidade=3,
            impacto=4,
        )
        assert risco.score_risco == 12

    def test_classificacao_automatica_critico(self):
        risco = RiscoOrganizacional(
            nome="Risco Crítico",
            descricao="Desc",
            nivel=NivelRisco.CRITICO,
            probabilidade=5,
            impacto=5,
        )
        assert risco.classificacao_automatica == NivelRisco.CRITICO

    def test_classificacao_automatica_baixo(self):
        risco = RiscoOrganizacional(
            nome="Risco Baixo",
            descricao="Desc",
            nivel=NivelRisco.BAIXO,
            probabilidade=1,
            impacto=2,
        )
        assert risco.classificacao_automatica == NivelRisco.BAIXO

    def test_probabilidade_invalida(self):
        with pytest.raises(ValueError, match="Probabilidade"):
            RiscoOrganizacional(
                nome="R",
                descricao="D",
                nivel=NivelRisco.BAIXO,
                probabilidade=6,
                impacto=1,
            )

    def test_impacto_invalido(self):
        with pytest.raises(ValueError, match="Impacto"):
            RiscoOrganizacional(
                nome="R",
                descricao="D",
                nivel=NivelRisco.BAIXO,
                probabilidade=1,
                impacto=0,
            )

    def test_str_inclui_nivel_e_nome(self):
        risco = RiscoOrganizacional(
            nome="Saída de Talento",
            descricao="Desc",
            nivel=NivelRisco.ALTO,
            probabilidade=3,
            impacto=4,
        )
        resultado = str(risco)
        assert "Saída de Talento" in resultado
        assert "12" in resultado  # score 3*4


class TestPlanoAcaoContinuidade:
    def test_criar_acao(self):
        acao = PlanoAcaoContinuidade(
            descricao="Criar backup",
            responsavel="TI",
            prazo_dias=30,
        )
        assert not acao.concluida

    def test_concluir_acao(self):
        acao = PlanoAcaoContinuidade(
            descricao="Criar backup",
            responsavel="TI",
            prazo_dias=30,
        )
        acao.concluir("Backup implementado com sucesso")
        assert acao.concluida
        assert "sucesso" in acao.observacoes

    def test_str_pendente(self):
        acao = PlanoAcaoContinuidade(
            descricao="Ação Pendente",
            responsavel="Fulano",
            prazo_dias=15,
        )
        assert "○" in str(acao)

    def test_str_concluida(self):
        acao = PlanoAcaoContinuidade(
            descricao="Ação Concluída",
            responsavel="Fulano",
            prazo_dias=15,
        )
        acao.concluir()
        assert "✓" in str(acao)


class TestPlanoContinuidade:
    def test_pcn_retencao_de_talentos(self):
        plano = PlanoContinuidade.pcn_retencao_de_talentos("João Silva")
        assert len(plano.riscos) == 2
        assert len(plano.acoes) == 3
        assert plano.status == StatusPlano.ATIVO
        assert plano.responsavel_lideranca == "João Silva"

    def test_pcn_disrupcao_operacional(self):
        plano = PlanoContinuidade.pcn_disrupcao_operacional()
        assert len(plano.riscos) == 2
        assert len(plano.acoes) == 3

    def test_pcn_transformacao_digital(self):
        plano = PlanoContinuidade.pcn_transformacao_digital()
        assert len(plano.riscos) == 2
        assert len(plano.acoes) == 3

    def test_adicionar_risco(self):
        plano = PlanoContinuidade(nome="Plano Teste", escopo="Escopo teste")
        risco = RiscoOrganizacional(
            nome="Novo Risco",
            descricao="Desc",
            nivel=NivelRisco.MEDIO,
            probabilidade=2,
            impacto=3,
        )
        plano.adicionar_risco(risco)
        assert len(plano.riscos) == 1

    def test_adicionar_acao(self):
        plano = PlanoContinuidade(nome="Plano Teste", escopo="Escopo teste")
        acao = PlanoAcaoContinuidade(
            descricao="Nova ação",
            responsavel="Gestor",
            prazo_dias=30,
        )
        plano.adicionar_acao(acao)
        assert len(plano.acoes) == 1

    def test_percentual_conclusao_zero(self):
        plano = PlanoContinuidade.pcn_retencao_de_talentos()
        assert plano.percentual_conclusao == 0.0

    def test_percentual_conclusao_parcial(self):
        plano = PlanoContinuidade.pcn_retencao_de_talentos()
        plano.acoes[0].concluir()
        assert plano.percentual_conclusao == pytest.approx(33.3, rel=0.01)

    def test_percentual_conclusao_sem_acoes(self):
        plano = PlanoContinuidade(nome="Plano Vazio", escopo="Vazio")
        assert plano.percentual_conclusao == 0.0

    def test_riscos_criticos(self):
        plano = PlanoContinuidade.pcn_disrupcao_operacional()
        criticos = plano.riscos_criticos
        assert len(criticos) > 0
        for r in criticos:
            assert r.classificacao_automatica in (NivelRisco.CRITICO, NivelRisco.ALTO)

    def test_relatorio_contem_elementos_chave(self):
        plano = PlanoContinuidade.pcn_retencao_de_talentos("Maria")
        relatorio = plano.relatorio()
        assert "PLANO DE CONTINUIDADE" in relatorio
        assert "Maria" in relatorio
        assert "RISCOS" in relatorio
        assert "AÇÕES" in relatorio
