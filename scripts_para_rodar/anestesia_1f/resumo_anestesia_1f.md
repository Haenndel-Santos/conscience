# Controle por 1/f — anestesia (propofol) — resumo (gerado automaticamente, a interpretar depois)

Pergunta: o resultado de anestesia já escrito no Cap. 11 (responsividade explica o
padrão "paradoxal") sobrevive ao mesmo controle por inclinação espectral 1/f que
esvaziou o resultado equivalente do sono?

Sujeitos: 20 (13 responsive, 7 drowsy). Falhas: nenhuma.

## Tabela completa
     grupo metrica                                 tipo      auc  ic95_low  ic95_high  p_valor_bootstrap  n_sujeitos  p_valor_fdr_bh
     todos     lzc                                bruta 0.669366  0.550744   0.789304              0.004          20        0.012000
     todos     lzc           residualizada_1f_in_sample 0.831686  0.737127   0.918432              0.000          20        0.000000
     todos     lzc residualizada_1f_out_of_sample_5fold 0.829121  0.729701   0.913801              0.000          20        0.000000
     todos      pe                                bruta 0.546667  0.412200   0.678132              0.511          20        0.511000
     todos      pe           residualizada_1f_in_sample 0.615832  0.493678   0.749545              0.070          20        0.105000
     todos      pe residualizada_1f_out_of_sample_5fold 0.609884  0.481683   0.735163              0.095          20        0.114000
responsive     lzc                                bruta 0.791360  0.668590   0.918768              0.000          13        0.000000
responsive     lzc           residualizada_1f_in_sample 0.890817  0.807170   0.960158              0.000          13        0.000000
responsive     lzc residualizada_1f_out_of_sample_5fold 0.890104  0.813262   0.956043              0.000          13        0.000000
responsive      pe                                bruta 0.642311  0.482301   0.804791              0.093          13        0.114000
responsive      pe           residualizada_1f_in_sample 0.660499  0.492597   0.819265              0.057          13        0.093273
responsive      pe residualizada_1f_out_of_sample_5fold 0.639977  0.481417   0.797940              0.091          13        0.114000
    drowsy     lzc                                bruta 0.410908  0.320793   0.494682              0.049           7        0.088200
    drowsy     lzc           residualizada_1f_in_sample 0.755006  0.555096   0.948095              0.017           7        0.043714
    drowsy     lzc residualizada_1f_out_of_sample_5fold 0.742245  0.522745   0.936315              0.035           7        0.070000
    drowsy      pe                                bruta 0.283180  0.117904   0.462569              0.020           7        0.045000
    drowsy      pe           residualizada_1f_in_sample 0.393547  0.156226   0.605920              0.345           7        0.388125
    drowsy      pe residualizada_1f_out_of_sample_5fold 0.401534  0.176748   0.615473              0.413           7        0.437294

## Como ler
- **bruta**: LZc/PE sem nenhum controle por 1/f — deve reproduzir, aproximadamente, os
  números já publicados em `comparacao_por_grupo.csv` (Bloco O) para responsive/drowsy.
- **residualizada_1f_in_sample / out_of_sample**: mesmo padrão agora aplicado ao sono —
  fora da amostra é o teste mais rigoroso (ajuste nunca treinado nos dados que corrige).
- Comparar "todos" com "responsive"/"drowsy": se o padrão paradoxal (responsive) e o
  padrão esperado (drowsy) sobreviverem à residualização, o achado de anestesia é mais
  robusto que o de sono. Se ambos colapsarem para ~0,5 como o sono colapsou, a leitura
  precisa mudar: o "resultado positivo" da anestesia seria, ele também, majoritariamente
  uma assinatura espectral (Colombo et al. 2019 já mostrou isso ser plausível neste
  mesmo paradigma farmacológico).

## Não inventar conclusão aqui — reportar o número real, qualquer que seja.
