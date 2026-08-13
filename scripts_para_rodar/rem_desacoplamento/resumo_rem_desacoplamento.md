# REM: complexidade interna vs. desacoplamento cortico-muscular (gerado automaticamente)

ATENÇÃO: este script testa acoplamento EEG-EMG (cortico-muscular), um proxy relacionado
mas DISTINTO de ME(t) tal como definida no Cap. 13 (acoplamento cérebro-AMBIENTE). O
Sleep-EDF Cassette não tem sensor de estímulo ambiental — ME(t) literal não é testável
com este dataset. Ler os resultados abaixo como teste desse proxy específico (atonia
muscular durante REM), não como confirmação direta da predição ME(t) do capítulo.

Sujeitos: 36 processados, 39086 épocas. Falhas: [(32, 'No matching events found for N3 (event id 4)'), (33, 'No matching events found for N3 (event id 4)'), (34, 'No matching events found for N3 (event id 4)')].

## Médias por estágio
            lzc                        emg_rms                      eeg_emg_coherence                  indice_desacoplamento                 
           mean       std  count          mean           std  count              mean       std  count                  mean       std  count
stage                                                                                                                                        
W      0.647329  0.120146   8923  4.616695e-11  5.634312e-11   8923          0.071463  0.015718   8923              0.358115  0.406589   8923
REM    0.533726  0.074794   6155  6.449970e-11  5.085821e-11   6155          0.073201  0.014473   6155              0.057646  0.349739   6155
N1     0.577160  0.090781   3264  5.923410e-11  4.601729e-11   3264          0.071863  0.017577   3264              0.133447  0.387202   3264
N2     0.473706  0.078712  16772  5.604950e-11  4.102736e-11  16772          0.072271  0.011982  16772             -0.136402  0.335550  16772
N3     0.316382  0.058485   3972  5.376867e-11  4.075450e-11   3972          0.071629  0.011125   3972             -0.427519  0.261899   3972

## Testes (REM vs. cada outro estágio, bootstrap por sujeito, FDR)
              metrica comparacao      auc  ic95_low  ic95_high  p_valor_bootstrap  n_sujeitos  p_valor_fdr_bh
              emg_rms   REM vs W 0.667504  0.582683   0.746432              0.000          36        0.000000
              emg_rms  REM vs N1 0.522032  0.447581   0.594277              0.593          36        0.593000
              emg_rms  REM vs N2 0.526449  0.482150   0.574946              0.243          36        0.265091
              emg_rms  REM vs N3 0.539351  0.482169   0.597077              0.188          36        0.225600
    eeg_emg_coherence   REM vs W 0.538978  0.528659   0.548817              0.000          36        0.000000
    eeg_emg_coherence  REM vs N1 0.535897  0.516113   0.555766              0.000          36        0.000000
    eeg_emg_coherence  REM vs N2 0.510129  0.500633   0.519506              0.033          36        0.049500
    eeg_emg_coherence  REM vs N3 0.519228  0.506433   0.531495              0.000          36        0.000000
indice_desacoplamento   REM vs W 0.285191  0.231066   0.339867              0.000          36        0.000000
indice_desacoplamento  REM vs N1 0.444512  0.389996   0.497330              0.038          36        0.050667
indice_desacoplamento  REM vs N2 0.653428  0.618590   0.688127              0.000          36        0.000000
indice_desacoplamento  REM vs N3 0.860573  0.832291   0.884911              0.000          36        0.000000

## Como ler (preencher depois — não inventar conclusão aqui)
- Se `emg_rms` for menor em REM que em W/N1/N2/N3 (AUC<0,5 favorecendo REM como "menor"),
  isso replica a atonia muscular do REM — achado clássico e esperado da polissonografia,
  não uma novidade teórica por si, mas a base sobre a qual o índice de desacoplamento
  é construído.
- O teste mais diretamente relevante à predição do Cap. 11 é `indice_desacoplamento`: se
  for consistentemente MAIOR em REM que nos outros 4 estágios (LZc alta relativa + EMG
  baixo relativo, dentro do mesmo sujeito), isso é evidência a favor da leitura
  "internamente rico, externamente desacoplado" — na forma operacionalizável disponível
  com este dataset (cortico-muscular, não cortico-ambiental).
- Se REM não se distinguir dos outros estágios nesse índice, é um resultado negativo
  válido para esta operacionalização específica — não decide a predição ME(t) original,
  que continua exigindo um dataset com estímulo ambiental registrado para ser testada
  de verdade.
