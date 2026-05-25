# Liderança Conectada 360 Graus

Framework Python para **estratégias de liderança voltadas à performance sustentável e continuidade do negócio**.

## Sobre

O módulo `lideranca_conectada` oferece um conjunto estruturado de ferramentas para líderes e organizações que desejam:

- Implementar **estratégias de liderança** baseadas em propósito, resultados humanizados, desenvolvimento de talentos e colaboração sistêmica.
- Avaliar e monitorar a **performance sustentável** de equipes por meio de diagnósticos multidimensionais.
- Planejar a **continuidade do negócio** com templates de PCN (Plano de Continuidade do Negócio) para riscos comuns.
- Acompanhar **indicadores de liderança (KPIs)** por meio de um painel integrado.

## Módulos

### `estrategias` — Estratégias de Liderança para Performance Sustentável

Quatro estratégias pré-definidas, cada uma com competências práticas e ações concretas:

| Estratégia | Foco | Nível |
|---|---|---|
| Liderança pelo Propósito | Propósito, valores e pertencimento | Proficiente |
| Gestão por Resultados Humanizados | OKRs, feedback contínuo, bem-estar | Avançado |
| Desenvolvimento Contínuo de Talentos | Pipeline de talentos e sucessão | Avançado |
| Liderança Colaborativa e Sistêmica | Pensamento sistêmico, influência | Referência |

```python
from lideranca_conectada import EstrategiaLideranca, PerformanceSustentavel

# Obter uma estratégia pré-definida
estrategia = EstrategiaLideranca.gestao_por_resultados_humanizados()
print(estrategia.resumo())

# Avaliar performance sustentável da equipe
ps = PerformanceSustentavel(equipe="Equipe Comercial")
ps.avaliar("Engajamento e Satisfação", 8)
ps.avaliar("Saúde e Bem-estar", 7)
ps.avaliar("Resultados e Metas", 9)
print(ps.diagnostico())
```

### `continuidade` — Plano de Continuidade do Negócio

Templates de PCN para os principais riscos organizacionais:

- **Retenção e Sucessão de Talentos** — saída de colaboradores-chave e alta rotatividade.
- **Disrupção Operacional e Crise** — falhas de infraestrutura e crises de reputação.
- **Transformação Digital** — resistência à mudança e obsolescência de competências.

```python
from lideranca_conectada import PlanoContinuidade

plano = PlanoContinuidade.pcn_retencao_de_talentos(responsavel="Ana Lima")
print(plano.relatorio())

# Marcar ações como concluídas
plano.acoes[0].concluir("Mapeamento realizado em workshop")
print(f"Conclusão: {plano.percentual_conclusao}%")
```

### `indicadores` — Painel de Indicadores de Liderança

KPIs organizados por dimensão para monitoramento contínuo:

| Indicador | Tipo | Meta padrão |
|---|---|---|
| Atingimento de Metas | Resultado | ≥ 80% |
| NPS de Clientes | Resultado | ≥ 50 pts |
| eNPS (Engajamento) | Pessoas | ≥ 30 pts |
| Taxa de Retenção | Pessoas | ≥ 90% |
| Horas de Desenvolvimento | Pessoas | ≥ 8 h/mês |
| Frequência de 1:1s | Processo | 100% |
| Cobertura de PDIs | Processo | 100% |
| Taxa de Retrabalho | Qualidade | ≤ 5% |
| Iniciativas de Melhoria | Inovação | ≥ 3/trimestre |

```python
from lideranca_conectada import PainelLideranca

painel = PainelLideranca.painel_padrao("Carlos Souza", "Equipe Produto")
painel.atualizar_indicador("eNPS (Engajamento)", 42)
painel.atualizar_indicador("Taxa de Retenção", 95)
painel.atualizar_indicador("Atingimento de Metas", 78)
print(painel.gerar_relatorio())
```

## Instalação

```bash
pip install -e .
```

## Testes

```bash
python -m pytest tests/ -v
```

## Estrutura do Projeto

```
lideranca_conectada/
├── lideranca_conectada/
│   ├── __init__.py          # Exportações públicas
│   ├── estrategias.py       # Estratégias de liderança e performance sustentável
│   ├── continuidade.py      # Planos de continuidade do negócio (PCN)
│   └── indicadores.py       # KPIs e painel de liderança
├── tests/
│   ├── test_estrategias.py
│   ├── test_continuidade.py
│   └── test_indicadores.py
└── setup.py
```
