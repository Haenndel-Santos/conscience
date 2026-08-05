# Dados atuais — leitura consolidada dos três modelos

Consolida `README.md`, `README2.md` e `README3.md` num único mapa. As três versões são iterações do mesmo modelo incorporado de consciência.

## Versões do modelo

| Versão | Script | Foco | Saídas principais |
|---|---|---|---|
| **Toy** | `consciousness_toy_model.py` | Estrutura mínima, auditável, 4 regimes (wake, deep_sleep, anxiety, reflex). Variáveis: Ψ_eff, Q, 𝒞, B, M. | `summary.csv`, `*_indices.png`, `*_phase.png`, `regime_comparison.png` |
| **V2** | `consciousness_model_v2.py` | Definições operacionais de B, Ψ, M, Q; comparação de regimes, *coupling sweep*, *phase map* (acoplamento × valoração corporal). | `Consciousness_Model_V2_Summary.csv`, `coupling_sweep.png`, `phase_map.png` |
| **V3** | `consciousness_model_v3.py` | Limiares, curvas ROC, testes de ablação, regras falsificáveis, análise de saturação, Monte Carlo. | `regime_summary.csv`, `thresholds_table.csv`, `auc_table.csv`, `ablation_table.csv`, `saturation_table.csv`, `falsifiable_rules.csv`, `roc_grid.png` |

## ⚠️ Correção de rótulo (verificada por reprodução em 2026-08-05)

- `summary.csv` → dados do **Toy** (wake 𝒞≈0,559).
- `Consciousness_Model_V2_Summary.csv` = `summary2.csv` → dados do **V2** (wake 𝒞≈0,643).
- `Toy_model_summary_by_regime.csv` → **contém dados do V2, não do Toy** (rótulo enganoso). Sugestão: renomear para `V2_summary_by_regime.csv` ou remover como duplicata.

## Variáveis (todas as versões)

- **Ψ_eff** — integração efetiva = [E/(E+E₀)]·(αB + βME + γK + δR).
- **Q** — potencial fenomenológico (proxy, *não* qualia).
- **𝒞 / C_idx** — índice de consciência (indicador de regime).
- **B** — acoplamento cérebro–corpo (correlação cruzada média).
- **ME** — acoplamento cérebro–ambiente. **K** — complexidade. **R** — recursividade.
- **M** — traço de memória. **E** — disponibilidade de recurso. **V** — valoração (corporal + social).
- Camada social **S(t)** do manuscrito **não é implementada** aqui (ver `auditoria_formalismo.md`).

## Reprodutibilidade

Modelos determinísticos por semente (seed=42). `consciousness_model_v3.monte_carlo()` reproduz `regime_summary.csv` na precisão de máquina. Dependências em `requirements.txt`.
