# LZc multivariada (2 canais) — resumo (gerado automaticamente, a interpretar depois)

Recomendação 3 do parecer de neurociência (`pareceres_especialistas/neurociencia.md`):
testar um índice de complexidade genuinamente multivariado (concatenação binária dos
2 canais, não LZc por canal seguida de média) antes de fechar a conclusão negativa sobre
"integração diferenciada" no sono.

Sujeitos solicitados: 0-40 | processados com sucesso: 36
IDs processados: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 35, 36, 37, 38]
Falhas: [(32, 'No matching events found for N3 (event id 4)'), (33, 'No matching events found for N3 (event id 4)'), (34, 'No matching events found for N3 (event id 4)')]
Total de épocas com 1/f válido: 39086

## Tabela completa
          metrica                                            descricao                                 tipo  auc_epoca_pooled_ingenua  auc_bootstrap_sujeito  ic95_low  ic95_high  p_valor_bootstrap  n_sujeitos  p_valor_fdr_bh
lzc_mean_channels        LZc média por canal (comparador já existente)                                bruta                  0.991901               0.991901  0.986481   0.995673              0.000          36           0.000
lzc_mean_channels        LZc média por canal (comparador já existente)           residualizada_1f_in_sample                  0.550446               0.550446  0.459214   0.634044              0.296          36           0.375
lzc_mean_channels        LZc média por canal (comparador já existente) residualizada_1f_out_of_sample_5fold                       NaN               0.553886  0.454736   0.638504              0.302          36           0.375
 lzc_multivariado LZc multivariada (concatenação binária dos 2 canais)                                bruta                  0.991888               0.991888  0.986952   0.995646              0.000          36           0.000
 lzc_multivariado LZc multivariada (concatenação binária dos 2 canais)           residualizada_1f_in_sample                  0.545444               0.545444  0.453833   0.627330              0.375          36           0.375
 lzc_multivariado LZc multivariada (concatenação binária dos 2 canais) residualizada_1f_out_of_sample_5fold                       NaN               0.549059  0.456536   0.632991              0.335          36           0.375

## Como ler

- **auc_epoca_pooled_ingenua**: trata cada época como observação independente — superestima
  a precisão (mesma ressalva já registrada no Cap. 11 para a análise original). Reportado
  só para comparabilidade com os relatórios anteriores do projeto.
- **auc_bootstrap_sujeito**: a estimativa correta para inferência — reamostra sujeitos
  inteiros (n=36), não épocas. É esta, não a ingênua, que decide o resultado.
- **bruta**: LZc sem nenhum controle por 1/f.
- **residualizada_1f_in_sample**: mesmo procedimento já usado em `integracao_diferenciada_1f.py`
  (regressão metric~exponent_1f ajustada nos mesmos dados que está corrigindo).
- **residualizada_1f_out_of_sample_Nfold**: regressão treinada em sujeitos de treino e
  aplicada a sujeitos de teste nunca vistos pelo ajuste (K-fold por sujeito) — o teste mais
  limpo, e o que o Cap. 11 do manuscrito já nomeia como "protocolo VNext" ainda em aberto.

## Leitura (preencher/revisar após rodar — não inventar conclusão aqui)

- Se `lzc_multivariado` (bootstrap por sujeito, residualizada out-of-sample) tiver IC95%
  excluindo 0,5 e p_valor_fdr_bh < 0,05, a complexidade multivariada sobrevive ao controle
  por 1/f mesmo fora da amostra — evidência real de estrutura conjunta entre os 2 canais
  além do confundidor espectral, e o Cap. 11 deveria ser atualizado para refletir isso.
- Se cair para perto de 0,5 (como já aconteceu com `lzc_mean_channels` e com o índice de
  integração×diferenciação de `integracao_diferenciada_1f.py`), isso reforça — com um teste
  ainda mais rigoroso (multivariado de verdade, out-of-sample) — a leitura já registrada no
  Cap. 11: o achado bruto de complexidade por estágio de sono permanece robusto, mas não
  resiste, em nenhuma operacionalização tentada até agora, como evidência específica de
  integração diferenciada acima do confundidor espectral.
- Comparar `lzc_multivariado` bruto com `lzc_mean_channels` bruto: se a versão multivariada
  discriminar sensivelmente melhor mesmo antes do controle por 1/f, isso já seria um
  resultado interessante por si (capturar estrutura conjunta que a média por canal
  descarta), independente do que aconteça depois do controle.
