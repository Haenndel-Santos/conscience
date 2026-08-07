# Frente E — Sensibilidade do modelo V3 (resumo, a interpretar por um agente depois)

Rodado com n_runs=6, n_trials=8, T=20.0, dt=0.1, seed=42.

## Fragilidade por task (magnitude de perturbação em que o AUC mediano cai)

              task  auc_baseline_mediana primeira_magnitude_auc_abaixo_0_85 primeira_magnitude_auc_abaixo_0_70
wake_vs_deep_sleep                   1.0                               None                               None
    wake_vs_reflex                   1.0                               None                               None
   wake_vs_anxiety                   1.0                               None                               None
   wake_vs_nonwake                   1.0                               None                               None
 integrated_vs_low                   1.0                               None                               None

## Leitura (preencher/revisar após rodar — não inventar conclusão aqui)
- Se o AUC mediano permanecer alto (>0,85, idealmente >0,95) até magnitudes
  de perturbação grandes (>=0,5, ou seja +-50% de ruído simultâneo em TODOS
  os pesos ao mesmo tempo), a separação de regimes é robusta — não depende
  de um ajuste fino específico dos coeficientes, o que enfraquece a crítica
  de "separa só por construção".
- Se o AUC cair abaixo de 0,85 (ou 0,70) já em magnitudes pequenas (<0,2), a
  separação é frágil — sustenta a crítica de que os coeficientes precisam
  estar calibrados de forma bem específica para o modelo funcionar.
- A sensibilidade one-at-a-time mostra quais pesos, se algum, dominam a
  separação (curvas com queda íngreme perto do multiplicador 1,0) vs. quais
  são redundantes/pouco importantes (curvas quase planas ao longo de toda a
  faixa testada).
- Nenhuma dessas duas leituras, por si, resolve a questão de identificabilidade
  (se o AJUSTE dos pesos é necessário para bater com dados reais) — isso é
  testado separadamente em `calibracao_v3.py`.
