# Varredura: o teste antigo era válido em cada desenho?

Gerado por `varredura_desenhos.py` em 2026-08-13 10:33.
`--n-cal 200 --n-boot 500`, α nominal = 0,05.
Nulo imposto por **permutação de rótulos de estado dentro de cada sujeito**.

Veredito sobre o teste antigo: `VALIDO` se o topo do IC95 do erro tipo I ficar em ≤12%;
`INVALIDO` se nem o piso do IC chegar lá; `SUSPEITO` no meio.

## Resultado

                                     desenho  n_sujeitos  epocas_neg  epocas_pos  razao_epocas  auc_agrupada_sob_nulo  erro_tipo1_antigo  antigo_ic_low  antigo_ic_high veredito_teste_antigo  erro_tipo1_novo  novo_ic_low  novo_ic_high  resultado_auc_agrupada  resultado_p_antigo  resultado_auc_por_sujeito  resultado_p_novo
                          REM vs W — emg_rms          36        8923        6155      1.449716               0.538661              0.460       0.392329        0.529178              INVALIDO            0.060     0.034652      0.101933                0.669107               0.000                   0.661816      4.721075e-05
                         REM vs N1 — emg_rms          36        3264        6155      1.885723               0.510893              0.000       0.000000        0.018846                VALIDO            0.045     0.023852      0.083298                0.520283               0.582                   0.528056      5.290792e-01
                         REM vs N2 — emg_rms          36       16772        6155      2.724939               0.512107              0.100       0.065670        0.149407              SUSPEITO            0.040     0.020405      0.076933                0.525241               0.274                   0.505254      9.938101e-01
                         REM vs N3 — emg_rms          36        3972        6155      1.549597               0.506416              0.000       0.000000        0.018846                VALIDO            0.030     0.013820      0.063895                0.537184               0.164                   0.503259      5.812918e-01
                REM vs W — eeg_emg_coherence          36        8923        6155      1.449716               0.501761              0.070       0.042152        0.114056                VALIDO            0.085     0.053745      0.131897                0.539313               0.000                   0.545281      1.448789e-07
               REM vs N1 — eeg_emg_coherence          36        3264        6155      1.885723               0.505748              0.020       0.007804        0.050288                VALIDO            0.030     0.013820      0.063895                0.535501               0.000                   0.538287      6.088233e-05
               REM vs N2 — eeg_emg_coherence          36       16772        6155      2.724939               0.499341              0.055       0.030985        0.095788                VALIDO            0.020     0.007804      0.050288                0.510345               0.028                   0.517901      4.597575e-03
               REM vs N3 — eeg_emg_coherence          36        3972        6155      1.549597               0.503739              0.055       0.030985        0.095788                VALIDO            0.025     0.010725      0.057179                0.519306               0.000                   0.511918      3.209542e-02
            REM vs W — indice_desacoplamento          36        8923        6155      1.449716               0.494637              0.000       0.000000        0.018846                VALIDO            0.055     0.030985      0.095788                0.283867               0.000                   0.260198      9.604264e-10
           REM vs N1 — indice_desacoplamento          36        3264        6155      1.885723               0.507781              0.005       0.000883        0.027774                VALIDO            0.075     0.045975      0.120045                0.443878               0.026                   0.412429      4.354625e-03
           REM vs N2 — indice_desacoplamento          36       16772        6155      2.724939               0.508532              0.180       0.132946        0.239116              INVALIDO            0.055     0.030985      0.095788                0.653445               0.000                   0.660026      3.669993e-08
           REM vs N3 — indice_desacoplamento          36        3972        6155      1.549597               0.545205              1.000       0.981154        1.000000              INVALIDO            0.050     0.027382      0.089579                0.860729               0.000                   0.885894      2.910383e-11
               SONO W vs N3 — LZc resid. 1/f          36        3972        8923      2.246475               0.551017              0.105       0.069707        0.155181              SUSPEITO            0.065     0.038376      0.108020                0.550101               0.296                   0.495121      9.814319e-01
     SONO W vs N3 — LZc multivar. resid. 1/f          36        3972        8923      2.246475               0.547345              0.060       0.034652        0.101933                VALIDO            0.060     0.034652      0.101933                0.543819               0.332                   0.494090      9.196639e-01
ANESTESIA basal vs moderada — LZc resid. 1/f          20         755         751      1.005326               0.498946              0.030       0.013820        0.063895                VALIDO            0.030     0.013820      0.063895                0.834620               0.000                   0.891030      1.607227e-04

## Correlação entre desequilíbrio de épocas e inflação

Spearman(razão de épocas, erro tipo I do teste antigo) = **+0.191**

## Desenhos em que o teste antigo é inválido

                          desenho  razao_epocas  auc_agrupada_sob_nulo  erro_tipo1_antigo  resultado_p_antigo  resultado_auc_por_sujeito  resultado_p_novo
               REM vs W — emg_rms      1.449716               0.538661               0.46                 0.0                   0.661816      4.721075e-05
REM vs N2 — indice_desacoplamento      2.724939               0.508532               0.18                 0.0                   0.660026      3.669993e-08
REM vs N3 — indice_desacoplamento      1.549597               0.545205               1.00                 0.0                   0.885894      2.910383e-11

## Como ler
- `auc_agrupada_sob_nulo` é o diagnóstico direto: quanto mais longe de 0,5, mais o
  desequilíbrio de épocas está inflando a AUC do pool, e mais o teste antigo rejeita à toa.
- `resultado_p_antigo` só é interpretável nas linhas com veredito `VALIDO`.
- `resultado_p_novo` (AUC por sujeito + Wilcoxon) é interpretável em todas.
