# Calibracao do teste de bootstrap por sujeito (erro tipo I empirico)

Gerado por `calibracao_teste_anestesia.py` em 2026-08-13 00:52.
`--n-boot 1000 --n-sim 500`, alfa nominal = 0,05.

O nulo e imposto aos dados REAIS: para cada sujeito, os dois estados sao recentrados num
mesmo nivel, zerando toda diferenca pareada. Variancia intra-sujeito e heterogeneidade
entre sujeitos ficam intactas. Sujeitos sao reamostrados com reposicao a cada replica.
Sob um teste calibrado, a fracao de rejeicoes deveria ficar em ~5%.

                                                desenho  n_sujeitos  n_epocas_a  n_epocas_b  razao_epocas  auc_media_sob_nulo  erro_tipo1  ic95_low  ic95_high  n_sim  n_boot
ANESTESIA (propofol, basal vs moderada, LZc resid. 1/f)          20         755         751      1.005326            0.507711        0.14  0.112322   0.173168    500    1000
              SONO (Sleep-EDF, N3 vs W, LZc resid. 1/f)          36        3972        8923      0.445142            0.567421        0.61  0.566563   0.651759    500    1000

## Como ler
- **erro_tipo1 >> 0,05** significa que o teste rejeita demais: os p-valores e q-valores
  produzidos por ele NAO estao calibrados, e resultados "significativos" obtidos com ele
  precisam ser reavaliados.
- **auc_media_sob_nulo** e o diagnostico da causa: se estiver bem acima de 0,5 mesmo com
  toda diferenca pareada zerada, a inflacao vem da agregacao por epoca (sujeitos com
  niveis diferentes e contagens desiguais de epocas em cada condicao), nao do bootstrap.
- **razao_epocas** proxima de 1 indica desenho balanceado, que tende a sofrer menos.
- Um resultado NEGATIVO obtido com um teste anticonservador fica MAIS forte, nao mais
  fraco: o teste rejeita facil e ainda assim nao rejeitou.
