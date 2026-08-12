# Frente C — Resumo (gerado automaticamente, a interpretar por um agente depois)

Sujeitos solicitados: 0-40 | processados com sucesso: 36
IDs processados: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 35, 36, 37, 38]
Falhas: [(32, 'No matching events found for N3 (event id 4)'), (33, 'No matching events found for N3 (event id 4)'), (34, 'No matching events found for N3 (event id 4)')]
Total de épocas com 1/f válido: 39086

## AUC W-vs-N3 (bruta vs. residualizada por 1/f)
                  metrica  auc_w_vs_n3_bruta  auc_w_vs_n3_residualizada_1f
                      lzc           0.991901                      0.697609
                       pe           0.984022                      0.604278
              exponent_1f           0.006025                           NaN
               sync_bruta           0.148172                      0.595139
            integracao_mi           0.198268                      0.593812
indice_integ_diferenciada           0.222870                      0.597033

## Correlação de Spearman com estágio (bruta vs. parcial controlando 1/f)
                  metrica  spearman_bruta  spearman_parcial_1f
                      lzc        0.683449            -0.010070
                       pe        0.737917             0.087933
               sync_bruta       -0.429789            -0.105346
            integracao_mi       -0.413935            -0.061783
indice_integ_diferenciada       -0.386795            -0.066612

## Leitura (preencher/revisar após rodar — não inventar conclusão aqui)
- Se `auc_w_vs_n3_residualizada_1f` de `lzc`/`pe`/`indice_integ_diferenciada` permanecer
  alta (próxima da bruta), a discriminação sobrevive ao controle por 1/f — reforça a
  leitura de "integração diferenciada", não apenas confundidor espectral.
- Se cair para perto de 0.5, o resultado é mais consistente com a hipótese do
  confundidor (Höhn et al. 2024) — reportar com a mesma honestidade do Bloco K
  (resultado negativo é dado, não fracasso).
- `sync_bruta` (hipersincronia) NÃO deveria discriminar tão bem quanto
  `indice_integ_diferenciada` — se discriminar igual ou melhor, isso enfraquece a
  alegação-assinatura da teoria (integração diferenciada > sincronia pura) e deve ser
  reportado como tal, não maquiado.

## Limitação metodológica (ver docstring do script)
Sleep-EDF Cassette só tem 2 canais EEG (Fpz-Cz, Pz-Oz). `integracao_mi`,
`diferenciacao_pe`, `sync_bruta` e `indice_integ_diferenciada` são proxies de 2 canais,
não medidas grafo-teóricas de rede multi-região. Reportar como tal.
