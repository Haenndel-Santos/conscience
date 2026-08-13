# Poder estatistico / efeito minimo detectavel - sono, n=36 (gerado automaticamente)

Pergunta: dado o desenho atual (n=36 sujeitos, bootstrap por sujeito, alfa=0,05), qual e
o menor efeito verdadeiro (Cohen's dz pareado, e seu AUC equivalente) que este projeto
conseguiria detectar de forma confiavel (80% de poder)?

> **Esta e a versao CORRIGIDA (2026-08-12).** A anterior nao reamostrava sujeitos: todas
> as replicas Monte Carlo de um mesmo dz-alvo eram identicas, e o "poder" que ela media
> era ruido do bootstrap interno, nao variabilidade amostral. Ela reportava MDE dz~0,2,
> numero invalido. Saidas antigas preservadas com sufixo `_INVALIDO_replicas_identicas`.

Dado usado: `integracao_diferenciada_por_epoca.csv` (LZc residualizado por 1/f dentro da
amostra, W vs N3, 36 sujeitos com os dois estagios).

Efeito observado nos dados reais: diferenca pareada media = -0.00502, DP = 0.05055,
Cohen's dz = -0.0994, AUC observada (ingenua, epoca-pooled) = 0.5504.

## Formula fechada (nivel 1) - nao foi afetada pelo bug
80% de poder exigiria dz >= 0.4669 (4.7x o efeito observado).
90% de poder exigiria dz >= 0.5403.

## Simulacao Monte Carlo (nivel 2, reamostrando sujeitos com reposicao)
n_sim=300 replicas por dz-alvo, n_boot=1000 por replica.

 dz_alvo  auc_equivalente_media  auc_equivalente_dp  poder_estimado  poder_ic95_low  poder_ic95_high  n_sim  n_boot
     0.0               0.565127            0.044559        0.283333        0.235330         0.336815    300    1000
     0.1               0.590772            0.042870        0.526667        0.470187         0.582472    300    1000
     0.2               0.602941            0.045423        0.643333        0.587629         0.695413    300    1000
     0.3               0.623568            0.040945        0.793333        0.743944         0.835305    300    1000
     0.4               0.645528            0.041069        0.910000        0.872222         0.937410    300    1000
     0.5               0.657593            0.042134        0.950000        0.919152         0.969469    300    1000
     0.6               0.678885            0.036946        0.976667        0.952627         0.988652    300    1000
     0.8               0.709224            0.037519        0.993333        0.976022         0.998170    300    1000
     1.0               0.745358            0.035492        1.000000        0.987357         1.000000    300    1000

**Efeito minimo detectavel (poder >=80%) pela simulacao: dz ~ 0.4.**

## Como ler (preencher/revisar depois - nao inventar conclusao aqui)
- Compare o MDE da simulacao com o da formula fechada (0.4669). Se forem
  proximos, o teste de bootstrap por sujeito tem poder semelhante ao do teste-t pareado.
  Se o da simulacao for bem menor, o teste usado no projeto e mais sensivel do que a
  aproximacao normal sugere; se for maior, e menos.
- O que decide a leitura do resultado nulo do Cap. 11 e onde o dz OBSERVADO (-0.0994)
  cai em relacao ao MDE. Se estiver muito abaixo, o desenho nao tinha poder para
  distinguir "efeito pequeno real" de "efeito nulo", e o resultado negativo e menos
  conclusivo do que o texto atual sugere. Se o MDE for menor que o efeito observado, o
  nulo passa a ser informativo.
- O poder em dz=0,0 estima a taxa de erro tipo I do teste. Se ficar bem abaixo de 5%,
  o teste e conservador e os p-valores do projeto nao estao calibrados.
- Isto usa a variancia REAL observada nos 36 sujeitos, entao reflete a heterogeneidade
  real do dado, incluindo os sujeitos com poucas epocas de N3.
