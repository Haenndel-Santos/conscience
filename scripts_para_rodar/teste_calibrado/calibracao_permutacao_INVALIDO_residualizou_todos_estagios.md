# Calibracao por permutacao — erro tipo I dos dois testes

Gerado por `calibracao_permutacao.py` em 2026-08-13 09:19.
`--n-cal 200 --n-boot 1000`, alfa nominal = 0,05.

## Metodo

O nulo e imposto **permutando os rotulos de estado entre as epocas de cada sujeito**,
preservando as contagens por estado. Isso destroi qualquer efeito de estado mantendo a
distribuicao marginal de cada sujeito intacta, e faz a AUC ter esperanca exatamente 0,5 —
que e a hipotese que os dois testes afirmam avaliar.

> **Corrige a calibracao anterior.** `calibracao_teste_anestesia.py` impunha o nulo
> recentrando as *medias* dos dois estados. AUC nao e funcao da media, e sim de dominancia
> estocastica: com distribuicoes assimetricas, medias iguais nao implicam AUC=0,5. Aquele
> procedimento injetava efeito real e o chamava de nulo. Os numeros dele (61% e 14%) nao
> sao taxas de erro tipo I validas.

## Resultado

                                      desenho  n_sujeitos  auc_agrupada_sob_nulo  erro_tipo1_antigo  antigo_ic_low  antigo_ic_high  erro_tipo1_novo  novo_ic_low  novo_ic_high  n_cal  n_boot
ANESTESIA (basal vs moderada, LZc resid. 1/f)          20               0.497194              0.055       0.030985        0.095788             0.04     0.020405      0.076933    200    1000
               SONO (N3 vs W, LZc resid. 1/f)          36               0.582831              1.000       0.981154        1.000000             0.07     0.042152      0.114056    200    1000

## Como ler
- Um teste calibrado rejeita ~5% das vezes sob este nulo. Acima disso e anticonservador
  (rejeita demais, produz falsos positivos); bem abaixo e conservador (perde poder).
- `auc_agrupada_sob_nulo` diagnostica a agregacao tipo Simpson: se ficar acima de 0,5 mesmo
  com os rotulos permutados dentro de cada sujeito, o desequilibrio de epocas entre estados
  esta inflando a AUC do pool, e qualquer teste que compare essa AUC contra 0,5 herda o viés.
- A comparacao entre as duas linhas de erro tipo I e o que decide qual teste usar.
