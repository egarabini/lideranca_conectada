"""
Estratégias de Liderança para Performance Sustentável
=======================================================
Este módulo define as principais estratégias de liderança voltadas para
a performance sustentável das equipes e da organização como um todo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class PilarLideranca(Enum):
    """Pilares fundamentais da liderança conectada 360 graus."""

    PROPOSITO = "Propósito e Valores"
    PESSOAS = "Desenvolvimento de Pessoas"
    PERFORMANCE = "Gestão de Performance"
    PROCESSOS = "Processos e Eficiência"
    PARCERIA = "Parcerias e Colaboração"


class NivelMaturidade(Enum):
    """Níveis de maturidade da liderança."""

    INICIANTE = 1
    DESENVOLVIMENTO = 2
    PROFICIENTE = 3
    AVANCADO = 4
    REFERENCIA = 5


@dataclass
class Competencia:
    """Representa uma competência de liderança."""

    nome: str
    descricao: str
    pilar: PilarLideranca
    acoes_praticas: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"[{self.pilar.value}] {self.nome}"


@dataclass
class EstrategiaLideranca:
    """
    Estratégia de liderança para performance sustentável.

    Agrega competências e práticas que permitem ao líder
    desenvolver equipes de alta performance de forma duradoura.
    """

    nome: str
    objetivo: str
    competencias: List[Competencia] = field(default_factory=list)
    nivel_recomendado: NivelMaturidade = NivelMaturidade.DESENVOLVIMENTO

    # Estratégias pré-definidas como métodos de classe
    @classmethod
    def lideranca_pelo_proposito(cls) -> "EstrategiaLideranca":
        """Estratégia baseada em propósito e alinhamento de valores."""
        return cls(
            nome="Liderança pelo Propósito",
            objetivo=(
                "Conectar os colaboradores ao propósito maior da organização, "
                "elevando engajamento e senso de pertencimento."
            ),
            competencias=[
                Competencia(
                    nome="Comunicação do Propósito",
                    descricao="Capacidade de articular e transmitir a visão e os valores da organização.",
                    pilar=PilarLideranca.PROPOSITO,
                    acoes_praticas=[
                        "Realizar reuniões mensais de alinhamento estratégico com a equipe.",
                        "Conectar metas individuais ao propósito organizacional nas avaliações.",
                        "Compartilhar histórias de impacto real do trabalho da equipe.",
                    ],
                ),
                Competencia(
                    nome="Cultura de Pertencimento",
                    descricao="Criação de ambiente inclusivo onde todos se sintam valorizados.",
                    pilar=PilarLideranca.PESSOAS,
                    acoes_praticas=[
                        "Reconhecer contribuições individuais publicamente.",
                        "Promover diversidade de perspectivas nas tomadas de decisão.",
                        "Estabelecer rituais de equipe que reforcem a identidade coletiva.",
                    ],
                ),
            ],
            nivel_recomendado=NivelMaturidade.PROFICIENTE,
        )

    @classmethod
    def gestao_por_resultados_humanizados(cls) -> "EstrategiaLideranca":
        """Estratégia de resultados com foco no bem-estar das pessoas."""
        return cls(
            nome="Gestão por Resultados Humanizados",
            objetivo=(
                "Alcançar alta performance de forma sustentável, equilibrando "
                "metas desafiadoras com o bem-estar e o desenvolvimento das pessoas."
            ),
            competencias=[
                Competencia(
                    nome="Definição de Metas OKR",
                    descricao="Uso de Objectives and Key Results para alinhar esforços com resultados estratégicos.",
                    pilar=PilarLideranca.PERFORMANCE,
                    acoes_praticas=[
                        "Definir 3 a 5 objetivos trimestrais ambiciosos mas alcançáveis.",
                        "Acompanhar key results semanalmente em check-ins rápidos.",
                        "Celebrar progressos intermediários, não apenas resultados finais.",
                    ],
                ),
                Competencia(
                    nome="Feedback Contínuo",
                    descricao="Cultura de feedback regular, construtivo e orientado ao crescimento.",
                    pilar=PilarLideranca.PESSOAS,
                    acoes_praticas=[
                        "Conduzir 1:1s semanais ou quinzenais com cada membro da equipe.",
                        "Utilizar o modelo SBI (Situação, Comportamento, Impacto) no feedback.",
                        "Criar espaços seguros para o feedback ascendente (bottom-up).",
                    ],
                ),
                Competencia(
                    nome="Gestão de Energia e Bem-estar",
                    descricao="Monitoramento e promoção ativos da saúde física e mental da equipe.",
                    pilar=PilarLideranca.PESSOAS,
                    acoes_praticas=[
                        "Monitorar indicadores de burnout e engajamento regularmente.",
                        "Incentivar pausas e respeitar limites de jornada.",
                        "Oferecer flexibilidade como ferramenta de retenção e produtividade.",
                    ],
                ),
            ],
            nivel_recomendado=NivelMaturidade.AVANCADO,
        )

    @classmethod
    def desenvolvimento_continuo_de_talentos(cls) -> "EstrategiaLideranca":
        """Estratégia focada na evolução contínua dos talentos da equipe."""
        return cls(
            nome="Desenvolvimento Contínuo de Talentos",
            objetivo=(
                "Construir um pipeline de talentos capaz de sustentar o crescimento "
                "da organização e garantir sucessão e continuidade."
            ),
            competencias=[
                Competencia(
                    nome="Mapeamento de Talentos",
                    descricao="Identificação sistemática de potenciais e lacunas de competências.",
                    pilar=PilarLideranca.PESSOAS,
                    acoes_praticas=[
                        "Aplicar matriz 9-box para avaliar performance e potencial.",
                        "Criar PDI (Plano de Desenvolvimento Individual) para cada colaborador.",
                        "Revisar planos de sucessão anualmente.",
                    ],
                ),
                Competencia(
                    nome="Delegação com Desenvolvimento",
                    descricao="Uso estratégico da delegação como ferramenta de crescimento.",
                    pilar=PilarLideranca.PROCESSOS,
                    acoes_praticas=[
                        "Delegar tarefas desafiadoras como oportunidades de crescimento.",
                        "Acompanhar com suporte estruturado (scaffolding) sem microgerenciar.",
                        "Debriefar aprendizados após cada entrega relevante.",
                    ],
                ),
                Competencia(
                    nome="Aprendizagem Organizacional",
                    descricao="Criação de cultura de aprendizado contínuo e compartilhamento de conhecimento.",
                    pilar=PilarLideranca.PARCERIA,
                    acoes_praticas=[
                        "Implementar comunidades de prática dentro da organização.",
                        "Promover sessões de lessons learned após projetos.",
                        "Incentivar e financiar capacitações externas estratégicas.",
                    ],
                ),
            ],
            nivel_recomendado=NivelMaturidade.AVANCADO,
        )

    @classmethod
    def lideranca_colaborativa_e_sistemica(cls) -> "EstrategiaLideranca":
        """Estratégia de liderança colaborativa com visão sistêmica."""
        return cls(
            nome="Liderança Colaborativa e Sistêmica",
            objetivo=(
                "Desenvolver líderes capazes de operar em ambientes complexos, "
                "conectando silos organizacionais e promovendo colaboração transversal."
            ),
            competencias=[
                Competencia(
                    nome="Pensamento Sistêmico",
                    descricao="Capacidade de enxergar a organização como um sistema interdependente.",
                    pilar=PilarLideranca.PROCESSOS,
                    acoes_praticas=[
                        "Mapear impactos das decisões em outras áreas antes de agir.",
                        "Participar de fóruns interdepartamentais regularmente.",
                        "Utilizar ferramentas de gestão visual (VSM, mapas de dependência).",
                    ],
                ),
                Competencia(
                    nome="Influência sem Autoridade",
                    descricao="Construção de alianças e influência positiva além da hierarquia formal.",
                    pilar=PilarLideranca.PARCERIA,
                    acoes_praticas=[
                        "Desenvolver rede de relacionamentos estratégicos internos.",
                        "Praticar escuta ativa em negociações e alinhamentos.",
                        "Gerar valor para parceiros internos antes de solicitar apoio.",
                    ],
                ),
            ],
            nivel_recomendado=NivelMaturidade.REFERENCIA,
        )

    def resumo(self) -> str:
        """Retorna um resumo textual da estratégia."""
        linhas = [
            f"Estratégia: {self.nome}",
            f"Objetivo: {self.objetivo}",
            f"Nível recomendado: {self.nivel_recomendado.name} ({self.nivel_recomendado.value}/5)",
            "",
            "Competências:",
        ]
        for comp in self.competencias:
            linhas.append(f"  • {comp}")
            for acao in comp.acoes_praticas:
                linhas.append(f"      - {acao}")
        return "\n".join(linhas)


@dataclass
class PerformanceSustentavel:
    """
    Modelo de performance sustentável para equipes e organizações.

    Performance sustentável é aquela que pode ser mantida ao longo do tempo
    sem comprometer o bem-estar das pessoas nem os recursos organizacionais.
    """

    DIMENSOES = [
        "Resultados e Metas",
        "Engajamento e Satisfação",
        "Saúde e Bem-estar",
        "Desenvolvimento e Aprendizagem",
        "Colaboração e Clima",
        "Inovação e Melhoria Contínua",
    ]

    equipe: str
    scores: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        for dim in self.DIMENSOES:
            if dim not in self.scores:
                self.scores[dim] = 0

    def avaliar(self, dimensao: str, score: int) -> None:
        """
        Registra a avaliação de uma dimensão de performance.

        Args:
            dimensao: Nome da dimensão (deve ser uma das DIMENSOES pré-definidas).
            score: Pontuação de 1 a 10.

        Raises:
            ValueError: Se a dimensão for inválida ou o score estiver fora do intervalo.
        """
        if dimensao not in self.DIMENSOES:
            raise ValueError(
                f"Dimensão '{dimensao}' inválida. Escolha uma de: {self.DIMENSOES}"
            )
        if not 1 <= score <= 10:
            raise ValueError("O score deve estar entre 1 e 10.")
        self.scores[dimensao] = score

    @property
    def score_geral(self) -> float:
        """Calcula o score geral de performance sustentável."""
        valores = [v for v in self.scores.values() if v > 0]
        if not valores:
            return 0.0
        return round(sum(valores) / len(valores), 2)

    @property
    def pontos_de_atencao(self) -> List[str]:
        """Retorna dimensões com score abaixo de 6 (necessitam atenção)."""
        return [dim for dim, score in self.scores.items() if 0 < score < 6]

    @property
    def pontos_fortes(self) -> List[str]:
        """Retorna dimensões com score igual ou acima de 8 (pontos fortes)."""
        return [dim for dim, score in self.scores.items() if score >= 8]

    def diagnostico(self) -> str:
        """Gera um diagnóstico textual da performance da equipe."""
        linhas = [
            f"Diagnóstico de Performance Sustentável — Equipe: {self.equipe}",
            f"Score Geral: {self.score_geral}/10",
            "",
        ]

        if self.pontos_fortes:
            linhas.append("Pontos Fortes:")
            for pf in self.pontos_fortes:
                linhas.append(f"  ✓ {pf} ({self.scores[pf]}/10)")
            linhas.append("")

        if self.pontos_de_atencao:
            linhas.append("Pontos de Atenção:")
            for pa in self.pontos_de_atencao:
                linhas.append(f"  ⚠ {pa} ({self.scores[pa]}/10)")
            linhas.append("")

        if self.score_geral >= 8:
            linhas.append("Avaliação: Equipe em zona de alta performance sustentável.")
        elif self.score_geral >= 6:
            linhas.append("Avaliação: Equipe em zona de performance satisfatória com oportunidades de melhoria.")
        elif self.score_geral > 0:
            linhas.append("Avaliação: Equipe requer intervenção estratégica imediata.")
        else:
            linhas.append("Avaliação: Nenhuma dimensão foi avaliada ainda.")

        return "\n".join(linhas)
