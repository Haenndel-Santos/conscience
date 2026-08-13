# Poder estatistico / efeito minimo detectavel — sono, n=36

Gerado por `poder_estatistico_sono.py` (v3, teste calibrado) em 2026-08-13 09:32.
`--n-sim 2000`, alfa = 0,05.

Pergunta: dado o desenho atual (n=36 sujeitos), qual e o menor efeito verdadeiro que este
projeto detectaria de forma confiavel (80% de poder)?

> **Terceira versao.** A v1 nao reamostrava nada (replicas identicas, MDE dz~0,2 invalido);
> a v2 media o poder do teste antigo, que rejeita 100% das vezes sob o nulo neste desenho.
> Numeros antigos preservados com sufixos `_INVALIDO_replicas_identicas` e
> `_teste_antigo_descalibrado`. **Nao cite nenhum dos dois.**

Teste avaliado aqui: AUC calculada dentro de cada sujeito, seguida de Wilcoxon dessas AUCs
contra 0,5 (`scripts_para_rodar/teste_calibrado/`).

## Efeito observado nos dados reais
- Diferenca pareada media = -0.00502, DP = 0.05055, **Cohen's dz = -0.0994**
- **AUC por sujeito = 0.4951**, com 56% dos sujeitos acima de 0,5
- AUC agrupada por epoca (ingenua, para referencia historica) = 0.5504

## Nivel 1 — formula fechada (nunca afetada pelos bugs)
80% de poder exigiria dz >= 0.4669 (4.7x o efeito observado).
90% de poder exigiria dz >= 0.5403.

## Nivel 2 — Monte Carlo com o teste calibrado

 dz_alvo  auc_por_sujeito_media  poder_estimado  poder_ic95_low  poder_ic95_high  n_sim
    0.00               0.514008          0.0720        0.061473         0.084168   2000
    0.05               0.527186          0.1100        0.097027         0.124468   2000
    0.10               0.537233          0.1665        0.150816         0.183463   2000
    0.15               0.547502          0.2395        0.221306         0.258693   2000
    0.20               0.557948          0.3595        0.338757         0.380781   2000
    0.25               0.568878          0.4665        0.444721         0.488408   2000
    0.30               0.579372          0.5515        0.529625         0.573178   2000
    0.40               0.599203          0.7095        0.689216         0.728980   2000
    0.50               0.618844          0.9130        0.899843         0.924574   2000
    0.60               0.638485          0.9660        0.957121         0.973092   2000
    0.80               0.678168          0.9980        0.994869         0.999222   2000
    1.00               0.713292          1.0000        0.998083         1.000000   2000

**Erro tipo I empirico (linha dz=0): 7.2%** — compare com os 5% nominais. Este e
o controle de sanidade que a v2 reprovava (28,3% com o teste antigo sob este mesmo nulo, e
100% sob permutacao de rotulos).

**Efeito minimo detectavel (poder >=80%): dz ~ 0.5.**

## Como ler
- Compare o MDE da simulacao com o da formula fechada (0.4669). Proximos =
  o teste calibrado tem poder semelhante ao teste-t pareado; menor = e mais sensivel.
- O que decide a leitura do resultado nulo do Cap. 11 e onde o dz OBSERVADO (-0.0994)
  cai em relacao ao MDE. Muito abaixo = o desenho nao tinha poder para distinguir "efeito
  pequeno real" de "efeito nulo", e o negativo e menos conclusivo do que parece.
- `dz` mede um efeito de MEDIA; o teste e de POSTOS. A coluna `auc_por_sujeito_media`
  mapeia um no outro, e e por ela que se deve comunicar tamanho de efeito.
- Isto usa a variancia REAL observada nos 36 sujeitos, incluindo os com poucas epocas de N3.
