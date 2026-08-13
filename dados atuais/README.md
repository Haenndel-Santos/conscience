# Dados atuais — leitura consolidada dos modelos

Consolida os antigos `README.md`, `README2.md` e `README3.md` num único mapa. As quatro versões são iterações do mesmo modelo incorporado de consciência.

## Versões do modelo

| Versão | Script | Foco | Saídas principais |
|---|---|---|---|
| **Toy** | `consciousness_toy_model.py` | Estrutura mínima, auditável, 4 regimes (wake, deep_sleep, anxiety, reflex). Variáveis: Ψ_eff, Q, 𝒞, B, M. | `summary.csv`, `*_indices.png`, `*_phase.png`, `regime_comparison.png` |
| **V2** | `consciousness_model_v2.py` | Definições operacionais de B, Ψ, M, Q; comparação de regimes, *coupling sweep*, *phase map* (acoplamento × valoração corporal). | `Consciousness_Model_V2_Summary.csv`, `coupling_sweep.png`, `phase_map.png`, `*_indices_v2.png`, `*_phase_v2.png`, `regime_comparison_v2.png` |
| **V3** (canônica p/ dinâmica individual) | `consciousness_model_v3.py` | Limiares, curvas ROC, testes de ablação, regras falsificáveis, análise de saturação, Monte Carlo. | `regime_summary.csv`, `thresholds_table.csv`, `auc_table.csv`, `ablation_table.csv`, `saturation_table.csv`, `falsifiable_rules.csv`, `roc_grid.png` |
| **V4** (camada social) | `consciousness_model_v4_social.py` | Prova de conceito mínima de S(t)/𝒞_hum(t): N agentes rodando a dinâmica interna do V3 (intocada), comunicando-se por um canal público. Não substitui o V3 — acrescenta uma camada por cima. | `social_outputs/resumo_por_cenario.csv`, `social_outputs/monte_carlo_runs.csv`, `social_outputs/auc_ratificado_vs_privado.txt`, `social_outputs/s_e_chum_por_cenario.png` |
| **V5** (camada social, teste não-circular) | `consciousness_model_v5_social.py` | Corrige a quase-circularidade da V4: mede **coordenação comportamental arriscada** (jogo tipo stag-hunt), não o próprio índice S. Acrescenta feedback real na dinâmica individual e K_ck como limiar, não gradiente. Ver `README_V5_como_rodar.md`. | `social_v5_outputs/resumo_coordenacao_por_cenario.csv`, `sweep_p_ack.csv`, `ablacao_sem_feedback_resumo.csv`, `robustez_n_e_limiar.csv`, `series_temporais_exemplo.csv`, `*.png` |

V3 é a versão canônica dos coeficientes do modelo individual (ver `Versao atual.md`, Cap. 13, e `_revisao_2026-08-05/auditoria_formalismo.md`). V4 é a primeira implementação (mínima, de prova de conceito) da camada social descrita no Cap. 9; V5 é a sucessora que torna o teste falseável.

**Resultado da V5 (execução real, 80 trials por cenário, seed=42, 2026-08-10):** taxa de sucesso de coordenação = 0,000 (privado), 0,000 (compartilhado), 0,912 (ratificado); a ablação sem feedback derruba os três a 0,000. **Como ler isso:** a ablação mostra que o código realiza o mecanismo pretendido — mas os parâmetros do jogo (`feedback_gain`, `decision_threshold`, `decision_gain`, `k_ck_gain`) foram calibrados por busca em grade justamente para deixar privado/compartilhado abaixo do limiar e ratificado acima. Isso é **verificação interna de mecanismo, não corroboração independente** de common knowledge ou de cognição social real. A calibração está documentada em `README_V5_como_rodar.md`.

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
- Camada social **S(t)** e **𝒞_hum** do manuscrito **não são implementadas** nos scripts toy/V2/V3. A partir do **V4**, têm uma prova de conceito mínima (ver seção acima e `_revisao_2026-08-05/auditoria_formalismo.md`, Nota 5) — mas isso não significa que a formulação plena do Cap. 9 (mentalização recursiva, publicidade, ratificação em sentido cheio) esteja implementada; V4 é proxy operacional simplificado, não simulação de crenças aninhadas ou lógica epistêmica.

## Reprodutibilidade

Modelos determinísticos por semente (seed=42). `consciousness_model_v3.monte_carlo()` reproduz `regime_summary.csv` na precisão de máquina. Dependências em `requirements.txt` (ambiente de execução usado nesta sessão: `.venv/` na raiz do projeto, não versionado).

Execução reforçada do V3 (n_runs=40, T=60) disponível em `reforco_outputs/`, sem sobrescrever o baseline.
