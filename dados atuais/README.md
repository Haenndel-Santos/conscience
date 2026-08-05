# Dados atuais — leitura consolidada dos três modelos

Consolida os antigos `README.md`, `README2.md` e `README3.md` num único mapa. As três versões são iterações do mesmo modelo incorporado de consciência.

## Versões do modelo

| Versão | Script | Foco | Saídas principais |
|---|---|---|---|
| **Toy** | `consciousness_toy_model.py` | Estrutura mínima, auditável, 4 regimes (wake, deep_sleep, anxiety, reflex). Variáveis: Ψ_eff, Q, 𝒞, B, M. | `summary.csv`, `*_indices.png`, `*_phase.png`, `regime_comparison.png` |
| **V2** | `consciousness_model_v2.py` | Definições operacionais de B, Ψ, M, Q; comparação de regimes, *coupling sweep*, *phase map* (acoplamento × valoração corporal). | `Consciousness_Model_V2_Summary.csv`, `coupling_sweep.png`, `phase_map.png`, `*_indices_v2.png`, `*_phase_v2.png`, `regime_comparison_v2.png` |
| **V3** (canônica) | `consciousness_model_v3.py` | Limiares, curvas ROC, testes de ablação, regras falsificáveis, análise de saturação, Monte Carlo. | `regime_summary.csv`, `thresholds_table.csv`, `auc_table.csv`, `ablation_table.csv`, `saturation_table.csv`, `falsifiable_rules.csv`, `roc_grid.png` |

V3 é a versão canônica dos coeficientes do modelo (ver `Versao atual.txt`, Cap. 13, e `_revisao_2026-08-05/auditoria_formalismo.md`).

## Higiene do repositório (2026-08-05)

Auditoria anterior (`_revisao_2026-08-05/reproducao_simulacoes.md`) apontou rótulos trocados entre `summary.csv` e `Toy_model_summary_by_regime.csv`, e classificou como "duplicatas simples" um conjunto de PNGs com sufixo " 2"/" 3". Uma reverificação por conteúdo (hashes + inspeção visual + leitura do código-fonte) nesta sessão corrigiu o diagnóstico:

- **CSVs duplicados de fato** (removidos): `summary2.csv` (idêntico a `Consciousness_Model_V2_Summary.csv`, só sem a coluna de índice) e `Toy_model_summary_by_regime.csv` (idêntico a `summary.csv`, dados do **toy model**, não do V2 — a atribuição anterior a "V2" estava incorreta; os valores batem com `summary.csv`, wake≈0,559, não com o V2, wake≈0,643).
- **PNGs que pareciam duplicados mas não eram**: `consciousness_toy_model.py` e `consciousness_model_v2.py` geram arquivos com **exatamente os mesmos nomes** (`{regime}_indices.png`, `{regime}_phase.png`, `regime_comparison.png`). Ao copiar as saídas dos dois scripts para a mesma pasta, o sistema operacional renomeou automaticamente as segundas cópias com sufixo " 2"/" 3". Comparação de hash mostrou que essas figuras **não são bit-idênticas** às suas homônimas, e inspeção visual confirmou que são gráficos genuinamente diferentes (títulos, eixos e valores do V2, não do toy). Essas 9 figuras foram **renomeadas** (não apagadas) para o padrão `*_v2.png`:
  - `anxiety_indices_v2.png`, `anxiety_phase_v2.png`, `deep_sleep_indices_v2.png`, `deep_sleep_phase_v2.png`, `reflex_indices_v2.png`, `reflex_phase_v2.png`, `regime_comparison_v2.png`, `wake_indices_v2.png`, `wake_phase_v2.png`.
  - A décima ocorrência, `wake_phase 3.png`, era byte-idêntica a `wake_phase 2.png` (mesmo hash SHA-256) — essa sim uma cópia redundante da figura V2 — e foi removida.

Detalhes completos em `RELATORIO_claude_code.md` (raiz do projeto).

## Variáveis (todas as versões)

- **Ψ_eff** — integração efetiva = [E/(E+E₀)]·(αB + βME + γK + δR). Multiplicada por `coherence_bias` (parâmetro de regime, fora do núcleo conceitual da equação).
- **Q** — potencial fenomenológico (proxy, *não* qualia). Inclui intercepto (−1,05 no V3).
- **𝒞 / C_idx** — índice de consciência (indicador de regime, não escala linear absoluta). O termo de memória usa 𝓜 = M/(M+1) (memória saturada), não M cru.
- **B** — acoplamento cérebro–corpo (correlação cruzada média).
- **ME** — acoplamento cérebro–ambiente. **K** — complexidade. **R** — recursividade.
- **M** — traço de memória. **E** — disponibilidade de recurso. **V** — valoração (corporal + social).
- Camada social **S(t)** e **𝒞_hum** do manuscrito **não são implementadas** em nenhum script — permanecem esboço conceitual (ver `_revisao_2026-08-05/auditoria_formalismo.md`).

## Reprodutibilidade

Modelos determinísticos por semente (seed=42). `consciousness_model_v3.monte_carlo()` reproduz `regime_summary.csv` na precisão de máquina. Dependências em `requirements.txt` (ambiente de execução usado nesta sessão: `.venv/` na raiz do projeto, não versionado).

Execução reforçada do V3 (n_runs=40, T=60) disponível em `reforco_outputs/`, sem sobrescrever o baseline.
