# V5 — teste não-circular de common knowledge (coordenação com risco)

Simulação multiagente que estende a V4 (ver docstring de
`consciousness_model_v5_social.py` para as três mudanças em relação à V4:
feedback real na dinâmica individual, K_ck com limiar, e jogo de coordenação
tipo stag-hunt) e testa se a coordenação comportamental arriscada — não o
próprio índice S — sobe especificamente no cenário de common knowledge.

**IMPORTANTE — leia antes de citar estes números em qualquer lugar:**
resultados de simulação sintética de prova de conceito. Não constituem
validação empírica de nada sobre cognição social real, comunicação humana
real, jogos de coordenação reais, ou consciência de máquina. Ver seção de
"HONESTIDADE METODOLÓGICA" na docstring do script.

## Resultado central (80 trials por cenário, seed=42)

```
               taxa_sucesso_coordenacao  frac_arriscada_media  P_u_medio_na_decisao  R_a_medio_na_decisao  K_ck_medio_na_decisao  M_medio_na_decisao  payoff_medio
scenario                                                                                                                                                          
privado                          0.0000              0.051562                   0.0                   0.0               0.000000            1.454234      0.948438
compartilhado                    0.0000              0.051562                   1.0                   0.0               0.000045            1.454337      0.948438
ratificado                       0.9125              0.768750                   1.0                   1.0               1.000000            1.873456      1.693750
```

**Taxa de sucesso de coordenação:** privado=0.000, compartilhado=0.000, ratificado=0.912.

## Ablação (a) — remoção do sinal de ratificação

Com `disable_feedback=True` (K_ck deixa de alimentar M mesmo no cenário
"ratificado"): taxa de sucesso de coordenação = 0.000
(comparar com ratificado COM feedback = 0.912, e com o nível
de privado/compartilhado = 0.000/0.000).
Ver `ablacao_sem_feedback_resumo.csv`.

## Ablação (b) — "compartilhado" apesar de P_u alto

P_u médio no instante da decisão: compartilhado=1.000,
ratificado=1.000. Se os dois forem parecidos (ambos altos) MAS
a coordenação continuar baixa em "compartilhado", isso é a checagem central
de não-circularidade: informação ampla (P_u alto) não é suficiente sozinha
para coordenar — precisa de reconhecimento recíproco (R_a>0, K_ck>0).

## Sweep de p_ack (transição de fase?)

Ver `sweep_p_ack.csv` / `sweep_p_ack.png` — K_ck médio e taxa de sucesso de
coordenação no instante da decisão, para 14 valores de p_ack
entre 0.0 e 0.2 (25 trials por
valor). A leitura de "transição abrupta vs. rampa suave" é visual/descritiva
neste script — não um teste estatístico formal de ponto de mudança.

## Robustez (N de agentes, limiar de coordenação)

Ver `robustez_n_e_limiar.csv` — grade pequena de N∈{6,8,12} ×
limiar∈{0,5, 0,6, 0,75}, 15 trials por combinação.

## Leitura preliminar automática (NÃO é a conclusão do agente — é um resumo
mecânico dos números acima; um agente deve revisar tudo antes de aceitar)

- Padrão previsto (ratificado > compartilhado E ratificado > privado): SIM.
- "Compartilhado" ficou perto do nível de "privado" apesar de P_u alto (não-circularidade): SIM (consistente com a teoria).
- Ablação (a) fez a coordenação de "ratificado" colapsar de volta ao nível basal: SIM (consistente — o mecanismo alegado é mesmo o responsável).

**Se as três linhas acima vierem "SIM"/consistentes, a predição do Cap. 9
passou neste teste específico — reportar como prova de conceito sintética
bem-sucedida, sem alegar mais que isso (não é validação empírica).** Se
qualquer uma vier "NÃO", o teste falhou ou ficou ambíguo neste ponto do
espaço de parâmetros — reportar honestamente, não maquiar (o próprio prompt
que originou este script pede isso explicitamente).

## Reprodutibilidade

Duas execuções do cenário "ratificado" com a mesma seed produzem série
temporal E resultado de decisão idênticos: True.

## Arquivos gerados

- `series_temporais_exemplo.csv` / `.png` — uma execução por cenário (seed fixa), K_ck/M/S/C_hum ao longo do tempo.
- `monte_carlo_decisoes.csv` — 80 trials por cenário (dados brutos da decisão do jogo).
- `resumo_coordenacao_por_cenario.csv` — resultado central (tabela acima).
- `ablacao_sem_feedback_resumo.csv` — ablação (a).
- `sweep_p_ack.csv` / `.png` — sweep de p_ack (transição de fase).
- `robustez_n_e_limiar.csv` — robustez a N de agentes e ao limiar de coordenação.

## Parâmetros usados nesta execução

```
SocialLayerParamsV5(n_agents=8, t_broadcast=8.0, t_decision=30.0, p_receive=0.05, p_ack=0.04, depth_cap=2, r_a_deep_threshold=0.8, lambda1=0.3333333333333333, lambda2=0.3333333333333333, lambda3=0.3333333333333333, w5=0.25, k_ck_gain=40.0, k_ck_threshold=0.25, feedback_gain=0.03, disable_feedback=False, decision_gain=10.0, decision_threshold=1.75, payoff_safe=1.0, payoff_stag_success=2.0, payoff_stag_fail=0.0, coord_threshold_frac=0.6)
```
