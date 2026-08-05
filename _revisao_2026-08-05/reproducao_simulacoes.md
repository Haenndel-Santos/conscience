# Reprodução e Reforço das Simulações — Projeto *Conscience*

Data: 2026-08-05 · Ambiente: Python 3.11, numpy 2.4, pandas 3.0, scikit-learn 1.8.
Saídas reforçadas em `reforco_outputs/` (o baseline **não** foi sobrescrito).

## 1. Reprodutibilidade (item C1) — ✅ perfeita

Rodando `consciousness_model_v3.monte_carlo()` com os defaults (n_runs=10, T=28, dt=0,10, seed=42), o resumo por regime reproduz o `regime_summary.csv` do baseline **na precisão de máquina**:

| Regime | 𝒞 médio (novo) | 𝒞 médio (baseline) | \|Δ\| |
|---|---|---|---|
| wake | 0,591601 | 0,591601 | 0 |
| anxiety | 0,517084 | 0,517084 | 0 |
| deep_sleep | 0,375441 | 0,375441 | 5,6·10⁻¹⁷ |
| reflex | 0,318297 | 0,318297 | 0 |

Os modelos são **determinísticos por semente** — os resultados publicados são integralmente reproduzíveis. As curvas ROC também reproduzem (C_idx_mean com AUC = 1,0 em todas as tarefas).

Toy e V2 também reproduzem: toy → wake 0,5591 / anxiety 0,5222 / deep_sleep 0,3806 / reflex 0,2946; V2 → wake 0,6430 / anxiety 0,5488 / deep_sleep 0,3696 / reflex 0,3139.

## 2. Reforço estatístico (item C2) — ✅ resultados estáveis

`monte_carlo(n_runs=40, T=60, dt=0,10)` — 4× mais execuções e série ~2× mais longa:

| Regime | 𝒞 médio (T=60, n=40) | desvio | CV% | 𝒞 médio baseline (T=28, n=10) |
|---|---|---|---|---|
| wake | 0,6245 | 0,0191 | 3,05% | 0,5916 |
| anxiety | 0,5371 | 0,0226 | 4,21% | 0,5171 |
| deep_sleep | 0,3400 | 0,0233 | 6,84% | 0,3754 |
| reflex | 0,2762 | 0,0110 | 4,00% | 0,3183 |

Leitura dos resultados:
- **A ordenação dos regimes é preservada**: wake > anxiety > deep_sleep > reflex, no baseline e no reforçado.
- **A separação melhora com séries mais longas**: com T=60 os estados integrados (wake/anxiety) sobem e os subintegrados (deep_sleep/reflex) descem, alargando a distância entre eles. Isso é consistente com a tese de que a integração precisa de tempo para se acumular nas janelas de correlação/recursividade.
- **A variabilidade continua baixa**: CV entre 3% e 6,8%, na mesma ordem de grandeza do baseline (1,6%–3,6%). O `deep_sleep` é o regime mais ruidoso, o que faz sentido (baixo acoplamento, sinais mais fracos).
- **A discriminação se mantém perfeita**: todas as tarefas de classificação continuam com **AUC = 1,0**. No reforçado, para `wake_vs_anxiety` e `wake_vs_nonwake` o melhor discriminador passa a ser Ψ_eff (empatado em AUC=1,0 com 𝒞), reforçando a leitura de que a ansiedade se distingue da vigília sobretudo pela **integração efetiva** (não pelo arousal/acoplamento bruto).

## 3. Achado de organização (item E1/E2)

Ao comparar reproduções com os arquivos do baseline, os rótulos de dois CSVs estão **trocados**:
- `summary.csv` contém os números do **toy model** (wake 0,559).
- `Toy_model_summary_by_regime.csv` contém, na verdade, os números do **V2** (wake 0,643) — idêntico a `Consciousness_Model_V2_Summary.csv` e `summary2.csv`.

Ou seja, o arquivo chamado "Toy_model_summary_by_regime.csv" **não** é do toy model. Recomendo renomear/consolidar (ver Bloco E).

## 4. Limite honesto (item C5)

Tudo isto é **prova de conceito sobre dados sintéticos**: os regimes são definidos por parâmetros escolhidos (`RegimeConfig`), então a separação perfeita (AUC=1,0) reflete a coerência interna do modelo, **não** validação empírica. O próximo salto real é confrontar o modelo com dados/achados externos (ver Bloco C5 e D).
