"""
Indicadores de Performance de Liderança — Liderança Conectada 360 Graus
=========================================================================
Este módulo define os KPIs e o painel de monitoramento para líderes
acompanharem a performance sustentável de suas equipes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class TipoIndicador(Enum):
    """Classificação do tipo de indicador de performance."""

    RESULTADO = "Resultado"          # Lagging indicators — o que já aconteceu
    PROCESSO = "Processo"            # Leading indicators — o que vai acontecer
    PESSOAS = "Pessoas"              # Indicadores relacionados a capital humano
    QUALIDADE = "Qualidade"          # Indicadores de qualidade e excelência
    INOVACAO = "Inovação"            # Indicadores de inovação e aprendizado


class StatusIndicador(Enum):
    """Status atual do indicador em relação à meta."""

    ACIMA_META = "Acima da Meta"
    NA_META = "Na Meta"
    ATENCAO = "Atenção"
    ABAIXO_META = "Abaixo da Meta"
    SEM_DADOS = "Sem Dados"


@dataclass
class IndicadoresPerformance:
    """
    Indicador de performance (KPI) para monitoramento de liderança.

    Cada indicador tem uma meta, um valor atual e classificação
    que orienta a tomada de decisão do líder.
    """

    nome: str
    descricao: str
    tipo: TipoIndicador
    unidade: str
    meta: float
    valor_atual: Optional[float] = None
    tolerancia_atencao: float = 0.10  # 10% abaixo da meta → atenção
    tolerancia_critica: float = 0.20  # 20% abaixo da meta → crítico

    @property
    def status(self) -> StatusIndicador:
        """Calcula o status do indicador em relação à meta."""
        if self.valor_atual is None:
            return StatusIndicador.SEM_DADOS
        if self.valor_atual >= self.meta:
            return StatusIndicador.ACIMA_META
        deficit = (self.meta - self.valor_atual) / self.meta
        if deficit <= self.tolerancia_atencao:
            return StatusIndicador.NA_META
        if deficit <= self.tolerancia_critica:
            return StatusIndicador.ATENCAO
        return StatusIndicador.ABAIXO_META

    @property
    def variacao_percentual(self) -> Optional[float]:
        """Calcula a variação percentual em relação à meta."""
        if self.valor_atual is None:
            return None
        return round((self.valor_atual - self.meta) / self.meta * 100, 1)

    def atualizar(self, novo_valor: float) -> None:
        """Atualiza o valor atual do indicador."""
        self.valor_atual = novo_valor

    def __str__(self) -> str:
        status_emoji = {
            StatusIndicador.ACIMA_META: "🟢",
            StatusIndicador.NA_META: "🟡",
            StatusIndicador.ATENCAO: "🟠",
            StatusIndicador.ABAIXO_META: "🔴",
            StatusIndicador.SEM_DADOS: "⚪",
        }
        emoji = status_emoji[self.status]
        valor_str = (
            f"{self.valor_atual} {self.unidade}"
            if self.valor_atual is not None
            else "sem dados"
        )
        return f"{emoji} {self.nome}: {valor_str} (meta: {self.meta} {self.unidade})"


@dataclass
class PainelLideranca:
    """
    Painel de indicadores para o líder monitorar performance sustentável.

    Consolida KPIs de múltiplas dimensões e gera visão integrada
    para tomada de decisão baseada em dados.
    """

    nome_lider: str
    equipe: str
    indicadores: List[IndicadoresPerformance] = field(default_factory=list)

    @classmethod
    def painel_padrao(cls, nome_lider: str, equipe: str) -> "PainelLideranca":
        """
        Cria um painel com os indicadores padrão de liderança sustentável.

        Inclui KPIs de resultado, processo, pessoas, qualidade e inovação
        alinhados às melhores práticas de gestão.
        """
        painel = cls(nome_lider=nome_lider, equipe=equipe)
        painel.indicadores = [
            # --- Indicadores de Resultado ---
            IndicadoresPerformance(
                nome="Atingimento de Metas",
                descricao="Percentual de objetivos trimestrais alcançados pela equipe.",
                tipo=TipoIndicador.RESULTADO,
                unidade="%",
                meta=80.0,
                tolerancia_atencao=0.10,
                tolerancia_critica=0.20,
            ),
            IndicadoresPerformance(
                nome="NPS de Clientes",
                descricao="Net Promoter Score dos clientes atendidos pela equipe.",
                tipo=TipoIndicador.RESULTADO,
                unidade="pts",
                meta=50.0,
                tolerancia_atencao=0.15,
                tolerancia_critica=0.30,
            ),
            # --- Indicadores de Pessoas ---
            IndicadoresPerformance(
                nome="eNPS (Engajamento)",
                descricao="Employee Net Promoter Score — satisfação e engajamento da equipe.",
                tipo=TipoIndicador.PESSOAS,
                unidade="pts",
                meta=30.0,
                tolerancia_atencao=0.20,
                tolerancia_critica=0.40,
            ),
            IndicadoresPerformance(
                nome="Taxa de Retenção",
                descricao="Percentual de colaboradores que permanecem na equipe no período.",
                tipo=TipoIndicador.PESSOAS,
                unidade="%",
                meta=90.0,
                tolerancia_atencao=0.05,
                tolerancia_critica=0.10,
            ),
            IndicadoresPerformance(
                nome="Horas de Desenvolvimento",
                descricao="Média de horas de treinamento e desenvolvimento por colaborador.",
                tipo=TipoIndicador.PESSOAS,
                unidade="h/mês",
                meta=8.0,
                tolerancia_atencao=0.25,
                tolerancia_critica=0.50,
            ),
            # --- Indicadores de Processo ---
            IndicadoresPerformance(
                nome="Frequência de 1:1s",
                descricao="Percentual de colaboradores com 1:1 realizado no período.",
                tipo=TipoIndicador.PROCESSO,
                unidade="%",
                meta=100.0,
                tolerancia_atencao=0.10,
                tolerancia_critica=0.20,
            ),
            IndicadoresPerformance(
                nome="Cobertura de PDIs",
                descricao="Percentual de colaboradores com Plano de Desenvolvimento Individual ativo.",
                tipo=TipoIndicador.PROCESSO,
                unidade="%",
                meta=100.0,
                tolerancia_atencao=0.10,
                tolerancia_critica=0.30,
            ),
            # --- Indicadores de Qualidade ---
            IndicadoresPerformance(
                nome="Taxa de Retrabalho",
                descricao="Percentual de entregas que precisaram ser refeitas.",
                tipo=TipoIndicador.QUALIDADE,
                unidade="%",
                meta=5.0,  # Meta máxima — quanto menor, melhor
                tolerancia_atencao=0.20,
                tolerancia_critica=0.50,
            ),
            # --- Indicadores de Inovação ---
            IndicadoresPerformance(
                nome="Iniciativas de Melhoria",
                descricao="Número de iniciativas de melhoria contínua propostas pela equipe.",
                tipo=TipoIndicador.INOVACAO,
                unidade="iniciativas/tri",
                meta=3.0,
                tolerancia_atencao=0.33,
                tolerancia_critica=0.67,
            ),
        ]
        return painel

    def adicionar_indicador(self, indicador: IndicadoresPerformance) -> None:
        """Adiciona um indicador customizado ao painel."""
        self.indicadores.append(indicador)

    def atualizar_indicador(self, nome: str, valor: float) -> None:
        """
        Atualiza o valor de um indicador pelo nome.

        Raises:
            KeyError: Se o indicador não for encontrado.
        """
        for ind in self.indicadores:
            if ind.nome == nome:
                ind.atualizar(valor)
                return
        raise KeyError(f"Indicador '{nome}' não encontrado no painel.")

    @property
    def resumo_status(self) -> Dict[StatusIndicador, List[str]]:
        """Agrupa indicadores por status para visão rápida."""
        resultado: Dict[StatusIndicador, List[str]] = {s: [] for s in StatusIndicador}
        for ind in self.indicadores:
            resultado[ind.status].append(ind.nome)
        return resultado

    @property
    def score_saude_lideranca(self) -> float:
        """
        Calcula o score de saúde de liderança (0 a 100).

        Pontuação baseada no status dos indicadores:
        - Acima da meta: 100 pts
        - Na meta: 80 pts
        - Atenção: 50 pts
        - Abaixo da meta: 20 pts
        - Sem dados: 0 pts (não penaliza, mas não contribui)
        """
        pesos = {
            StatusIndicador.ACIMA_META: 100,
            StatusIndicador.NA_META: 80,
            StatusIndicador.ATENCAO: 50,
            StatusIndicador.ABAIXO_META: 20,
            StatusIndicador.SEM_DADOS: None,
        }
        pontuacoes = [
            pesos[ind.status]
            for ind in self.indicadores
            if pesos[ind.status] is not None
        ]
        if not pontuacoes:
            return 0.0
        return round(sum(pontuacoes) / len(pontuacoes), 1)

    def gerar_relatorio(self) -> str:
        """Gera o relatório completo do painel de liderança."""
        linhas = [
            f"PAINEL DE LIDERANÇA — {self.nome_lider}",
            f"Equipe: {self.equipe}",
            f"Score de Saúde: {self.score_saude_lideranca}/100",
            "=" * 55,
            "",
        ]

        # Agrupa por tipo
        por_tipo: Dict[TipoIndicador, List[IndicadoresPerformance]] = {}
        for ind in self.indicadores:
            por_tipo.setdefault(ind.tipo, []).append(ind)

        for tipo, inds in por_tipo.items():
            linhas.append(f"▸ {tipo.value}")
            for ind in inds:
                linhas.append(f"  {ind}")
            linhas.append("")

        # Resumo executivo
        resumo = self.resumo_status
        criticos = resumo.get(StatusIndicador.ABAIXO_META, [])
        atencao = resumo.get(StatusIndicador.ATENCAO, [])

        if criticos or atencao:
            linhas.append("AÇÕES PRIORITÁRIAS:")
            for nome in criticos:
                linhas.append(f"  🔴 Ação imediata: {nome}")
            for nome in atencao:
                linhas.append(f"  🟠 Monitorar: {nome}")
        else:
            linhas.append("✅ Todos os indicadores monitorados estão dentro das metas.")

        return "\n".join(linhas)
