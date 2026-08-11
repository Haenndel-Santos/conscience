# Frente E — Calibração/identificabilidade do modelo V3 (resumo, a interpretar por um agente depois)

Rodado com n_samples=500, n_starts=8, n_runs=6, T=20.0, dt=0.1, seed=42.

Alvo empírico (referência, não um alvo de otimização direta — a otimização maximiza AUC, não distância até este número): AUC real W-vs-N3 (LZc, Sleep-EDF n=36) = 0.9919.

## Relatório de identificabilidade

- fracao_amostras_auc_maior_igual_0_95: 0.998
- fracao_amostras_auc_maior_igual_0_90: 0.998
- fracao_amostras_auc_menor_0_70: 0.0
- espalhamento_relativo_top10pct_por_param: {'w_mb': 1.1209832470905454, 'w_me': 1.0141420143563016, 'w_k': 0.9533198393317821, 'w_r': 0.9741981009386924, 'c_w_psi': 0.9514415180582821, 'c_w_q': 1.0354901337227829, 'c_w_m': 0.956315103404134, 'c_w_b': 0.9329151624790165}
- correlacao_spearman_param_x_auc: {'w_mb': -0.03551212830667682, 'w_me': 0.06931843385626436, 'w_k': -0.05536170220735208, 'w_r': -0.04884856077119301, 'c_w_psi': 0.06373574119669945, 'c_w_q': 0.07366052814703708, 'c_w_m': 0.06776768589527411, 'c_w_b': -0.06032409568252089}
- distancia_media_normalizada_entre_otimos_multistart: 0.41687913926453113
- auc_medio_otimizacao_multistart: 1.0
- auc_minimo_otimizacao_multistart: 1.0

## Leitura (preencher/revisar após rodar — não inventar conclusão aqui)
- Fração de amostras aleatórias (limites amplos, 0 a 2x cada peso) com
  AUC>=0,95: 99.8%.
  AUC>=0,90: 99.8%.
  AUC<0,70: 0.0%.
  - Se a fração com AUC alto for GRANDE (>50-70%), isso sustenta a leitura
    de que a separação wake/deep_sleep é quase garantida "por construção" —
    reproduzir o AUC real (0,992) não é uma restrição forte sobre o modelo.
  - Se a fração for PEQUENA, isso é evidência de uma restrição mais real.
- Distância média normalizada entre os ótimos finais da otimização
  multi-start: 0.417
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
