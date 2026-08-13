# Teste calibrado (AUC por sujeito) — resultados

Gerado por `teste_auc_por_sujeito.py` em 2026-08-13 12:30.
`--n-folds 5`.

Substitui o `cluster_bootstrap_auc` (AUC agrupada por época + bootstrap de sujeitos) no
desenho do sono, onde o desequilíbrio de épocas (2,25:1) o torna inválido.

## Calibração (de `calibracao_permutacao.py`, permutação de rótulos dentro do sujeito)

| desenho | AUC agrupada sob o nulo | teste ANTIGO | teste NOVO |
|---|---|---|---|
| Anestesia (épocas 1,01:1) | 0,4972 | 5,5% [3,1–9,6%] | 4,0% [2,0–7,7%] |
| Sono (épocas 2,25:1) | ~~0,5828~~ **0,5510** | ~~**100,0%** [98,1–100%]~~ **10,5%** [7,0–15,5%] | 7,0% [4,2–11,4%] |

> ⚠️ **Correção (2026-08-13).** Os dois valores tachados na linha do sono vieram da rodada
> arquivada como `_INVALIDO_residualizou_todos_estagios`, que ajustava a residualização por
> 1/f sobre os **cinco** estágios antes de filtrar o par W/N3 — contra a convenção do projeto,
> que é filtrar o par primeiro e só então residualizar. Os valores corretos, em negrito, são
> os de `varredura_desenhos.csv` (linha `SONO W vs N3 — LZc resid. 1/f`). Não citar 100,0%
> nem 0,5828 em lugar nenhum.

O teste antigo é válido no desenho balanceado da anestesia e **suspeito** — não inválido — no
do sono: com erro tipo I de 10,5% contra 5% nominal, ele rejeita cerca de duas vezes mais do
que deveria, o que não chega a explicar os p-valores obtidos e por isso não derruba nenhuma
conclusão já registrada. (A varredura completa dos 15 desenhos, em `varredura_desenhos.md`,
classifica este desenho como SUSPEITO e encontra 3 desenhos genuinamente inválidos, nenhum
deles o do sono.) O teste novo é calibrado nos dois; a varredura reporta para ele 6,5%
[3,8–10,8%] neste desenho, contra os 7,0% [4,2–11,4%] da rodada de permutação acima —
diferença de ruído de simulação entre duas rodadas, sem efeito em veredito algum.

## Resultados

     bloco      grupo                   metrica                   tipo  n_sujeitos  epocas_min  epocas_mediana  auc_media  auc_mediana   auc_dp  ic95_low  ic95_high  frac_sujeitos_acima_05   p_wilcoxon      p_ttest  q_fdr_bloco  auc_antiga_pooled  p_antigo_bootstrap
      sono      todos                       lzc                  bruta          36         128             312   0.991214     0.998824 0.018982  0.984441   0.996427                1.000000 1.654783e-07 2.813897e-51 4.964348e-07              0.992               0.000
      sono      todos                       lzc     resid_1f_in_sample          36         128             312   0.495121     0.532952 0.226402  0.423190   0.568471                0.555556 9.814319e-01 8.978520e-01 9.814319e-01              0.550               0.280
      sono      todos                       lzc resid_1f_out_of_sample          36         128             312   0.500108     0.528590 0.234574  0.425028   0.577079                0.555556 9.566913e-01 9.978083e-01 9.814319e-01              0.554               0.280
      sono      todos                        pe                  bruta          36         128             312   0.990902     0.999649 0.018253  0.984553   0.996099                1.000000 1.310222e-07 7.320303e-52 4.913332e-07              0.984               0.000
      sono      todos                        pe     resid_1f_in_sample          36         128             312   0.546302     0.606788 0.277954  0.454328   0.634649                0.555556 3.074205e-01 3.244229e-01 5.123675e-01              0.580               0.190
      sono      todos                        pe resid_1f_out_of_sample          36         128             312   0.546840     0.626883 0.284515  0.456454   0.635172                0.555556 3.000293e-01 3.300363e-01 5.123675e-01                NaN                 NaN
      sono      todos                sync_bruta                  bruta          36         128             312   0.139845     0.084870 0.155438  0.092675   0.192498                0.055556 2.037268e-10 8.111402e-16 1.527951e-09                NaN                 NaN
      sono      todos                sync_bruta     resid_1f_in_sample          36         128             312   0.450514     0.462369 0.267862  0.365169   0.536036                0.416667 3.000293e-01 2.752229e-01 5.123675e-01                NaN                 NaN
      sono      todos                sync_bruta resid_1f_out_of_sample          36         128             312   0.450494     0.479747 0.270880  0.362667   0.537362                0.444444 2.785544e-01 2.803209e-01 5.123675e-01                NaN                 NaN
      sono      todos             integracao_mi                  bruta          36         128             312   0.180433     0.145412 0.153344  0.133067   0.230515                0.027778 1.455192e-10 1.808570e-14 1.527951e-09                NaN                 NaN
      sono      todos             integracao_mi     resid_1f_in_sample          36         128             312   0.491381     0.490312 0.279006  0.401285   0.580760                0.472222 8.828057e-01 8.540315e-01 9.814319e-01                NaN                 NaN
      sono      todos             integracao_mi resid_1f_out_of_sample          36         128             312   0.493136     0.501747 0.278141  0.404743   0.582860                0.500000 9.196639e-01 8.831344e-01 9.814319e-01                NaN                 NaN
      sono      todos indice_integ_diferenciada                  bruta          36         128             312   0.201203     0.171118 0.163455  0.149294   0.253742                0.055556 4.074536e-10 7.156108e-13 2.037268e-09                NaN                 NaN
      sono      todos indice_integ_diferenciada     resid_1f_in_sample          36         128             312   0.482966     0.482492 0.272997  0.396006   0.570941                0.444444 7.740053e-01 7.103753e-01 9.814319e-01                NaN                 NaN
      sono      todos indice_integ_diferenciada resid_1f_out_of_sample          36         128             312   0.483794     0.486606 0.275109  0.395057   0.571610                0.444444 8.099021e-01 7.258752e-01 9.814319e-01                NaN                 NaN
sono-multi      todos         lzc_mean_channels                  bruta          36         128             312   0.991214     0.998824 0.018982  0.984472   0.996505                1.000000 1.654783e-07 2.813897e-51 4.964348e-07                NaN                 NaN
sono-multi      todos         lzc_mean_channels     resid_1f_in_sample          36         128             312   0.495121     0.532952 0.226402  0.423450   0.568927                0.555556 9.814319e-01 8.978520e-01 9.938101e-01                NaN                 NaN
sono-multi      todos         lzc_mean_channels resid_1f_out_of_sample          36         128             312   0.497997     0.540309 0.226525  0.425192   0.570149                0.583333 9.938101e-01 9.579840e-01 9.938101e-01                NaN                 NaN
sono-multi      todos          lzc_multivariado                  bruta          36         128             312   0.991041     0.998728 0.019548  0.983934   0.996445                1.000000 1.654783e-07 7.958614e-51 4.964348e-07              0.992               0.000
sono-multi      todos          lzc_multivariado     resid_1f_in_sample          36         128             312   0.494090     0.529089 0.226836  0.421463   0.568482                0.527778 9.196639e-01 8.766753e-01 9.938101e-01                NaN                 NaN
sono-multi      todos          lzc_multivariado resid_1f_out_of_sample          36         128             312   0.494076     0.526489 0.224752  0.421650   0.566516                0.555556 9.319914e-01 8.752414e-01 9.938101e-01              0.549               0.375
 anestesia      todos                       lzc                  bruta          20          58              77   0.702276     0.900326 0.339349  0.554042   0.841894                0.650000 6.332564e-03 1.527656e-02 1.899769e-02              0.669               0.004
 anestesia      todos                       lzc     resid_1f_in_sample          20          58              77   0.891030     0.952505 0.181843  0.800743   0.955236                0.950000 1.607227e-04 9.839433e-09 1.098633e-03              0.832               0.000
 anestesia      todos                       lzc resid_1f_out_of_sample          20          58              77   0.885192     0.958408 0.187412  0.796324   0.951419                0.950000 1.865822e-04 2.009589e-08 1.098633e-03              0.829               0.000
 anestesia      todos                        pe                  bruta          20          58              77   0.548395     0.526932 0.367249  0.387748   0.701021                0.550000 5.958195e-01 5.625899e-01 5.958195e-01              0.547               0.511
 anestesia      todos                        pe     resid_1f_in_sample          20          58              77   0.581627     0.760339 0.397250  0.410070   0.744965                0.550000 3.883762e-01 3.696501e-01 4.909172e-01                NaN                 NaN
 anestesia      todos                        pe resid_1f_out_of_sample          20          58              77   0.581130     0.761679 0.392357  0.409858   0.746502                0.550000 4.090977e-01 3.667011e-01 4.909172e-01              0.610               0.095
 anestesia responsive                       lzc                  bruta          13          63              79   0.897291     0.939024 0.208114  0.776579   0.971895                0.923077 4.882812e-04 1.691207e-05 1.757813e-03              0.791               0.000
 anestesia responsive                       lzc     resid_1f_in_sample          13          63              79   0.934793     0.973734 0.091204  0.884027   0.977631                1.000000 2.441406e-04 8.112501e-10 1.098633e-03                NaN                 NaN
 anestesia responsive                       lzc resid_1f_out_of_sample          13          63              79   0.932180     0.973734 0.101745  0.872453   0.978611                1.000000 2.441406e-04 3.063195e-09 1.098633e-03              0.890               0.000
 anestesia responsive                        pe                  bruta          13          63              79   0.687794     0.803627 0.345766  0.498650   0.856627                0.769231 6.811523e-02 7.385633e-02 1.362305e-01                NaN                 NaN
 anestesia responsive                        pe     resid_1f_in_sample          13          63              79   0.624074     0.777361 0.372822  0.424225   0.811443                0.615385 1.677246e-01 2.533277e-01 2.515869e-01                NaN                 NaN
 anestesia responsive                        pe resid_1f_out_of_sample          13          63              79   0.617530     0.786116 0.379738  0.410433   0.807440                0.615385 2.438965e-01 2.863003e-01 3.377028e-01                NaN                 NaN
 anestesia     drowsy                       lzc                  bruta           7          58              71   0.340106     0.328455 0.206433  0.217931   0.492116                0.142857 1.093750e-01 8.632801e-02 1.789773e-01              0.411               0.049
 anestesia     drowsy                       lzc     resid_1f_in_sample           7          58              71   0.816167     0.930180 0.274495  0.605698   0.957348                0.857143 3.125000e-02 2.258673e-02 7.031250e-02                NaN                 NaN
 anestesia     drowsy                       lzc resid_1f_out_of_sample           7          58              71   0.810204     0.904151 0.278322  0.595188   0.951807                0.857143 3.125000e-02 2.565185e-02 7.031250e-02              0.742               0.035
 anestesia     drowsy                        pe                  bruta           7          58              71   0.289510     0.369270 0.260177  0.120341   0.476067                0.142857 1.093750e-01 7.609964e-02 1.789773e-01              0.283               0.020
 anestesia     drowsy                        pe     resid_1f_in_sample           7          58              71   0.393405     0.441441 0.376793  0.144644   0.654795                0.428571 4.687500e-01 4.824657e-01 4.963235e-01                NaN                 NaN
 anestesia     drowsy                        pe resid_1f_out_of_sample           7          58              71   0.401770     0.441441 0.379700  0.157025   0.662341                0.428571 4.687500e-01 5.192286e-01 4.963235e-01              0.402               0.413
       rem   REM vs W                   emg_rms                  bruta          36         162             363   0.661816     0.693313 0.204416  0.595429   0.726167                0.777778 4.721075e-05 3.409990e-05 1.133058e-04                NaN                 NaN
       rem   REM vs W         eeg_emg_coherence                  bruta          36         162             363   0.545281     0.549647 0.040474  0.532247   0.558206                0.888889 1.448789e-07 9.003837e-08 4.346366e-07                NaN                 NaN
       rem   REM vs W     indice_desacoplamento                  bruta          36         162             363   0.260198     0.269479 0.149905  0.210363   0.309333                0.083333 9.604264e-10 2.452222e-11 5.762558e-09                NaN                 NaN
       rem  REM vs N1                   emg_rms                  bruta          36         102             257   0.528056     0.513721 0.198947  0.466707   0.593303                0.500000 5.290792e-01 4.032180e-01 6.341365e-01                NaN                 NaN
       rem  REM vs N1         eeg_emg_coherence                  bruta          36         102             257   0.538287     0.533653 0.052429  0.522095   0.555302                0.833333 6.088233e-05 1.021623e-04 1.217647e-04                NaN                 NaN
       rem  REM vs N1     indice_desacoplamento                  bruta          36         102             257   0.412429     0.382520 0.170586  0.356808   0.468321                0.305556 4.354625e-03 4.012292e-03 6.896363e-03                NaN                 NaN
       rem  REM vs N2                   emg_rms                  bruta          36         285             646   0.505254     0.466576 0.143009  0.460912   0.553944                0.472222 9.938101e-01 8.268083e-01 9.938101e-01                NaN                 NaN
       rem  REM vs N2         eeg_emg_coherence                  bruta          36         285             646   0.517901     0.514436 0.034320  0.507280   0.529461                0.666667 4.597575e-03 3.522031e-03 6.896363e-03                NaN                 NaN
       rem  REM vs N2     indice_desacoplamento                  bruta          36         285             646   0.660026     0.680913 0.112993  0.621365   0.694360                0.916667 3.669993e-08 5.004183e-10 1.467997e-07                NaN                 NaN
       rem  REM vs N3                   emg_rms                  bruta          36          56             270   0.503259     0.481502 0.177492  0.447474   0.560995                0.416667 5.812918e-01 9.129173e-01 6.341365e-01                NaN                 NaN
       rem  REM vs N3         eeg_emg_coherence                  bruta          36          56             270   0.511918     0.518956 0.072594  0.486618   0.533415                0.694444 3.209542e-02 3.313785e-01 4.279390e-02                NaN                 NaN
       rem  REM vs N3     indice_desacoplamento                  bruta          36          56             270   0.885894     0.896853 0.070969  0.861385   0.907060                1.000000 2.910383e-11 8.598259e-28 3.492460e-10                NaN                 NaN

## Onde a conclusão mudou em relação ao teste antigo

    bloco  grupo metrica  tipo  auc_antiga_pooled  p_antigo_bootstrap  auc_media  p_wilcoxon
anestesia drowsy     lzc bruta              0.411               0.049   0.340106    0.109375
anestesia drowsy      pe bruta              0.283               0.020   0.289510    0.109375

## Como ler
- `auc_media` é a média das AUCs **calculadas dentro de cada sujeito** — não é
  comparável em valor absoluto com `auc_antiga_pooled`, que agrupava épocas de todos os
  sujeitos. A AUC por sujeito é tipicamente mais próxima de 0,5, porque não incorpora a
  separação entre sujeitos. A comparação que importa é de **significância**, não de valor.
- `frac_sujeitos_acima_05` mostra a consistência do efeito entre sujeitos: um efeito real
  aparece na maioria dos sujeitos, não só na média.
- `epocas_min` sinaliza sujeitos com poucas épocas, cuja AUC individual é ruidosa.
- `q_fdr_bloco` é Benjamini-Hochberg dentro de cada bloco, como os scripts originais faziam.
