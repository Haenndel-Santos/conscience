# Frente E — Calibração/identificabilidade do modelo V3 (resumo, a interpretar por um agente depois)

Rodado com n_samples=200, n_starts=5, n_runs=4, T=15.0, dt=0.1, seed=42.

Alvo empírico (referência, não um alvo de otimização direta — a otimização maximiza AUC, não distância até este número): AUC real W-vs-N3 (LZc, Sleep-EDF n=36) = 0.9919.

## Relatório de identificabilidade

- fracao_amostras_auc_maior_igual_0_95: 1.0
- fracao_amostras_auc_maior_igual_0_90: 1.0
- fracao_amostras_auc_menor_0_70: 0.0
- espalhamento_relativo_top10pct_por_param: {'w_mb': 0.893373875698759, 'w_me': 0.7737274809496277, 'w_k': 0.9311689355863352, 'w_r': 1.0900701228408514, 'c_w_psi': 1.0367359900308584, 'c_w_q': 0.8509514230584829, 'c_w_m': 0.7704955831564047, 'c_w_b': 1.0635019144722573}
- correlacao_spearman_param_x_auc: {'w_mb': nan, 'w_me': nan, 'w_k': nan, 'w_r': nan, 'c_w_psi': nan, 'c_w_q': nan, 'c_w_m': nan, 'c_w_b': nan}
- distancia_media_normalizada_entre_otimos_multistart: 0.3782093792134057
- auc_medio_otimizacao_multistart: 1.0
- auc_minimo_otimizacao_multistart: 1.0

## Leitura (preencher/revisar após rodar — não inventar conclusão aqui)
- Fração de amostras aleatórias (limites amplos, 0 a 2x cada peso) com
  AUC>=0,95: 100.0%.
  AUC>=0,90: 100.0%.
  AUC<0,70: 0.0%.
  - Se a fração com AUC alto for GRANDE (>50-70%), isso sustenta a leitura
    de que a separação wake/deep_sleep é quase garantida "por construção" —
    reproduzir o AUC real (0,992) não é uma restrição forte sobre o modelo.
  - Se a fração for PEQUENA, isso é evidência de uma restrição mais real.
- Distância média normalizada entre os ótimos finais da otimização
  multi-start: 0.378
  (0 = todos os pontos de partida convergem para o MESMO lugar; próximo de 1
  = convergem para lugares muito diferentes do espaço de busca).
  - Valor alto = não-identificabilidade: várias combinações de pesos bem
    diferentes dão o mesmo resultado, o que enfraquece a leitura de "ajuste
    genuíno único".
- Correlação de Spearman entre cada peso e o AUC (busca aleatória) indica
  quais pesos, se algum, realmente controlam a separação — pesos com
  |rho| baixo são pouco identificáveis a partir deste teste (o AUC não
  reage a eles).
- Se as correlações e o espalhamento relativo vierem todos como "nan", é
  porque o AUC saturou em um único valor (ex.: 1,0) em TODAS as amostras —
  ou seja, nem variou o suficiente para calcular uma correlação. Isso não é
  um erro do script: é, em si, o resultado mais extremo possível a favor da
  leitura "por construção" (qualquer combinação de pesos testada já satura
  a separação).
- Nenhuma dessas leituras substitui um teste estatístico formal — são
  descritivas, para orientar o agente que interpretar os números depois.
