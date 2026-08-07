# Frente D — Resumo (gerado automaticamente, a interpretar por um agente depois)

Sujeitos com dados de responsividade: 20 (13 'responsive', 7 'drowsy',
reconstrução aproximada via IC de Wilson — Chennu et al. 2016 relatam 13/7 no artigo original)
Arquivos EEG processados: 20 sujeitos, 3082 épocas
Falhas: nenhuma

## Comparação por grupo de responsividade (o teste central desta reanálise)
     grupo  n_sujeitos  lzc_basal  lzc_sedacao_moderada  pe_basal  pe_sedacao_moderada  auc_lzc_basal_vs_moderada_positivo_moderada  auc_pe_basal_vs_moderada_positivo_moderada
responsive          13   0.423140              0.475944  0.690883             0.703102                                     0.791360                                    0.642311
    drowsy           7   0.423621              0.399494  0.693345             0.678193                                     0.410908                                    0.283180

## Correlação complexidade basal x mudança sob sedação moderada
metrica  spearman_basal_vs_delta  p_valor  n
    lzc                -0.339850 0.142637 20
     pe                -0.748872 0.000145 20

## Leitura (preencher/revisar após rodar — não inventar conclusão aqui)
- Se o grupo 'responsive' mostrar LZc/PE MAIOR na sedação moderada que no basal (AUC
  favorecendo moderada) e o grupo 'drowsy' mostrar o padrão oposto, isso REPLICA o
  achado de Newman et al. (2026, BJA, mesmo dataset) e explica por que a análise
  agregada original (`analise_anestesia_propofol.py`) deu um resultado negativo/misto:
  os dois subgrupos se cancelam na média.
- Se não replicar, é um resultado negativo igualmente válido — reportar com a mesma
  honestidade do Bloco K, sem forçar a leitura.
- Lembrar: a classificação responsive/drowsy aqui é uma RECONSTRUÇÃO aproximada do
  método de Chennu et al. (2016), não os rótulos originais exatos dos autores — o
  número de sujeitos em cada grupo pode diferir ligeiramente de 13/7.

## Limitação metodológica
Ver docstring do script: estrutura de `datainfo.mat` confirmada via documentação do
FieldTrip Toolbox, não por inspeção direta do binário. Se a leitura falhar ou vier
incompleta, o script imprime a estrutura bruta no início da execução — confira o log.
