"""
Continuidade do Negócio — Liderança Conectada 360 Graus
=========================================================
Este módulo define as estruturas e ferramentas para planejamento
de continuidade do negócio (PCN/BCP) sob a ótica da liderança.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class NivelRisco(Enum):
    """Classificação do nível de risco organizacional."""

    BAIXO = "Baixo"
    MEDIO = "Médio"
    ALTO = "Alto"
    CRITICO = "Crítico"


class StatusPlano(Enum):
    """Status do plano de continuidade."""

    RASCUNHO = "Rascunho"
    ATIVO = "Ativo"
    EM_REVISAO = "Em Revisão"
    OBSOLETO = "Obsoleto"


@dataclass
class RiscoOrganizacional:
    """
    Representa um risco identificado que pode impactar
    a continuidade do negócio ou a performance da equipe.
    """

    nome: str
    descricao: str
    nivel: NivelRisco
    probabilidade: int  # 1 a 5
    impacto: int  # 1 a 5
    responsavel: Optional[str] = None
    acoes_mitigacao: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 1 <= self.probabilidade <= 5:
            raise ValueError("Probabilidade deve ser entre 1 e 5.")
        if not 1 <= self.impacto <= 5:
            raise ValueError("Impacto deve ser entre 1 e 5.")

    @property
    def score_risco(self) -> int:
        """Calcula o score de risco (probabilidade × impacto)."""
        return self.probabilidade * self.impacto

    @property
    def classificacao_automatica(self) -> NivelRisco:
        """Classifica o risco automaticamente com base no score."""
        score = self.score_risco
        if score <= 4:
            return NivelRisco.BAIXO
        if score <= 9:
            return NivelRisco.MEDIO
        if score <= 16:
            return NivelRisco.ALTO
        return NivelRisco.CRITICO

    def __str__(self) -> str:
        return (
            f"[{self.nivel.value}] {self.nome} "
            f"(Score: {self.score_risco} | P:{self.probabilidade} × I:{self.impacto})"
        )


@dataclass
class PlanoAcaoContinuidade:
    """Ação concreta dentro do plano de continuidade do negócio."""

    descricao: str
    responsavel: str
    prazo_dias: int
    concluida: bool = False
    observacoes: str = ""

    def concluir(self, observacoes: str = "") -> None:
        """Marca a ação como concluída."""
        self.concluida = True
        if observacoes:
            self.observacoes = observacoes

    def __str__(self) -> str:
        status = "✓" if self.concluida else "○"
        return f"[{status}] {self.descricao} — {self.responsavel} ({self.prazo_dias}d)"


@dataclass
class PlanoContinuidade:
    """
    Plano de Continuidade do Negócio (PCN) orientado à liderança.

    O PCN é um documento vivo que descreve como a organização irá
    manter operações essenciais durante e após uma interrupção.
    """

    nome: str
    escopo: str
    status: StatusPlano = StatusPlano.RASCUNHO
    riscos: List[RiscoOrganizacional] = field(default_factory=list)
    acoes: List[PlanoAcaoContinuidade] = field(default_factory=list)
    responsavel_lideranca: Optional[str] = None

    # Templates de PCN pré-definidos como métodos de classe

    @classmethod
    def pcn_retencao_de_talentos(cls, responsavel: str = "") -> "PlanoContinuidade":
        """Template de PCN para risco de perda de talentos-chave."""
        plano = cls(
            nome="PCN — Retenção e Sucessão de Talentos",
            escopo=(
                "Garantir a continuidade operacional e a transferência de conhecimento "
                "em caso de saída de colaboradores estratégicos."
            ),
            status=StatusPlano.ATIVO,
            responsavel_lideranca=responsavel,
        )
        plano.riscos = [
            RiscoOrganizacional(
                nome="Saída de Colaborador-Chave",
                descricao="Perda repentina de profissional com conhecimento crítico e pouca redundância.",
                nivel=NivelRisco.ALTO,
                probabilidade=3,
                impacto=5,
                responsavel=responsavel,
                acoes_mitigacao=[
                    "Mapear colaboradores críticos e suas competências únicas.",
                    "Criar planos de sucessão formais com backup designado.",
                    "Implementar programa de documentação e transferência de conhecimento.",
                    "Revisar política de remuneração e retenção anualmente.",
                ],
            ),
            RiscoOrganizacional(
                nome="Alta Rotatividade de Equipe",
                descricao="Turnover elevado degradando capacidade operacional e cultura organizacional.",
                nivel=NivelRisco.MEDIO,
                probabilidade=3,
                impacto=3,
                responsavel=responsavel,
                acoes_mitigacao=[
                    "Monitorar eNPS (Employee Net Promoter Score) trimestralmente.",
                    "Conduzir entrevistas de desligamento estruturadas.",
                    "Implementar programas de desenvolvimento de carreira.",
                ],
            ),
        ]
        plano.acoes = [
            PlanoAcaoContinuidade(
                descricao="Levantar mapa de dependências de conhecimento por colaborador",
                responsavel=responsavel or "RH + Liderança",
                prazo_dias=30,
            ),
            PlanoAcaoContinuidade(
                descricao="Criar repositório centralizado de procedimentos e documentação técnica",
                responsavel=responsavel or "Liderança de TI",
                prazo_dias=60,
            ),
            PlanoAcaoContinuidade(
                descricao="Definir e formalizar planos de sucessão para posições críticas",
                responsavel=responsavel or "RH + Diretoria",
                prazo_dias=90,
            ),
        ]
        return plano

    @classmethod
    def pcn_disrupcao_operacional(cls, responsavel: str = "") -> "PlanoContinuidade":
        """Template de PCN para disrupções operacionais."""
        plano = cls(
            nome="PCN — Disrupção Operacional e Crise",
            escopo=(
                "Manter a capacidade mínima de operação durante crises, desastres "
                "ou interrupções significativas nos processos de negócio."
            ),
            status=StatusPlano.ATIVO,
            responsavel_lideranca=responsavel,
        )
        plano.riscos = [
            RiscoOrganizacional(
                nome="Falha de Infraestrutura Crítica",
                descricao="Indisponibilidade de sistemas, dados ou ferramentas essenciais à operação.",
                nivel=NivelRisco.CRITICO,
                probabilidade=2,
                impacto=5,
                responsavel=responsavel,
                acoes_mitigacao=[
                    "Implementar arquitetura de alta disponibilidade e backups regulares.",
                    "Definir RTO (Recovery Time Objective) e RPO (Recovery Point Objective).",
                    "Realizar simulações de recuperação de desastres semestralmente.",
                ],
            ),
            RiscoOrganizacional(
                nome="Crise de Imagem ou Reputação",
                descricao="Evento que compromete a credibilidade da organização perante clientes e mercado.",
                nivel=NivelRisco.ALTO,
                probabilidade=2,
                impacto=4,
                responsavel=responsavel,
                acoes_mitigacao=[
                    "Definir protocolo de comunicação de crise com porta-vozes designados.",
                    "Treinar líderes em gestão de crises e comunicação transparente.",
                    "Monitorar presença digital e menções à marca continuamente.",
                ],
            ),
        ]
        plano.acoes = [
            PlanoAcaoContinuidade(
                descricao="Criar comitê de gestão de crises com representantes de cada área",
                responsavel=responsavel or "Diretoria",
                prazo_dias=15,
            ),
            PlanoAcaoContinuidade(
                descricao="Documentar árvore de comunicação e escalada em situações de crise",
                responsavel=responsavel or "Comunicação + RH",
                prazo_dias=30,
            ),
            PlanoAcaoContinuidade(
                descricao="Realizar simulação de crise (tabletop exercise) com lideranças",
                responsavel=responsavel or "Comitê de Crise",
                prazo_dias=90,
            ),
        ]
        return plano

    @classmethod
    def pcn_transformacao_digital(cls, responsavel: str = "") -> "PlanoContinuidade":
        """Template de PCN para riscos na jornada de transformação digital."""
        plano = cls(
            nome="PCN — Transformação Digital e Mudança Organizacional",
            escopo=(
                "Gerenciar riscos e garantir continuidade durante processos de "
                "transformação digital, mudanças estruturais e adoção de novas tecnologias."
            ),
            status=StatusPlano.ATIVO,
            responsavel_lideranca=responsavel,
        )
        plano.riscos = [
            RiscoOrganizacional(
                nome="Resistência à Mudança",
                descricao="Baixa adoção de novas práticas, ferramentas ou estruturas organizacionais.",
                nivel=NivelRisco.MEDIO,
                probabilidade=4,
                impacto=3,
                responsavel=responsavel,
                acoes_mitigacao=[
                    "Engajar líderes como agentes de mudança desde o início.",
                    "Comunicar o 'porquê' da mudança de forma clara e constante.",
                    "Criar quick wins visíveis para construir confiança no processo.",
                ],
            ),
            RiscoOrganizacional(
                nome="Obsolescência de Competências",
                descricao="Lacuna crescente entre competências atuais e as demandadas pela transformação.",
                nivel=NivelRisco.ALTO,
                probabilidade=3,
                impacto=4,
                responsavel=responsavel,
                acoes_mitigacao=[
                    "Realizar assessment de competências digitais anualmente.",
                    "Criar trilhas de upskilling e reskilling personalizadas.",
                    "Incentivar experimentação e aprendizado contínuo no dia a dia.",
                ],
            ),
        ]
        plano.acoes = [
            PlanoAcaoContinuidade(
                descricao="Nomear Change Champions em cada área para apoiar a transformação",
                responsavel=responsavel or "Liderança + RH",
                prazo_dias=14,
            ),
            PlanoAcaoContinuidade(
                descricao="Criar programa de capacitação digital com trilhas por perfil",
                responsavel=responsavel or "T&D",
                prazo_dias=45,
            ),
            PlanoAcaoContinuidade(
                descricao="Implementar índice de adoção digital como KPI de liderança",
                responsavel=responsavel or "Diretoria",
                prazo_dias=60,
            ),
        ]
        return plano

    def adicionar_risco(self, risco: RiscoOrganizacional) -> None:
        """Adiciona um risco ao plano."""
        self.riscos.append(risco)

    def adicionar_acao(self, acao: PlanoAcaoContinuidade) -> None:
        """Adiciona uma ação ao plano."""
        self.acoes.append(acao)

    @property
    def riscos_criticos(self) -> List[RiscoOrganizacional]:
        """Retorna apenas os riscos com nível CRÍTICO ou ALTO."""
        return [
            r for r in self.riscos
            if r.classificacao_automatica in (NivelRisco.CRITICO, NivelRisco.ALTO)
        ]

    @property
    def percentual_conclusao(self) -> float:
        """Calcula o percentual de conclusão das ações do plano."""
        if not self.acoes:
            return 0.0
        concluidas = sum(1 for a in self.acoes if a.concluida)
        return round(concluidas / len(self.acoes) * 100, 1)

    def relatorio(self) -> str:
        """Gera um relatório textual do plano de continuidade."""
        linhas = [
            f"PLANO DE CONTINUIDADE DO NEGÓCIO",
            f"{'=' * 50}",
            f"Nome: {self.nome}",
            f"Escopo: {self.escopo}",
            f"Status: {self.status.value}",
            f"Responsável: {self.responsavel_lideranca or 'Não definido'}",
            f"Conclusão das Ações: {self.percentual_conclusao}%",
            "",
            f"RISCOS IDENTIFICADOS ({len(self.riscos)}):",
        ]
        for risco in self.riscos:
            linhas.append(f"  {risco}")
            for acao in risco.acoes_mitigacao:
                linhas.append(f"    → {acao}")
        linhas.append("")
        linhas.append(f"AÇÕES DO PLANO ({len(self.acoes)}):")
        for acao in self.acoes:
            linhas.append(f"  {acao}")
        return "\n".join(linhas)
