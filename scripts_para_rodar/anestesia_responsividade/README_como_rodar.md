# Frente D — reanálise de anestesia por responsividade: como rodar

Este script (`reanalise_responsividade_propofol.py`) foi **escrito por um agente e não executado por ele** — mesma regra de governança aplicada à Frente C (`PLANO_ESTRATEGICO_cientifico.md` §0.1). A verificação feita pelo agente foi só de **sintaxe** (`python -m py_compile`, passou sem erros), não de execução.

## Por que este script existe

O recompute V2 (`recompute_empirico_v2/analise_anestesia_propofol.py`, Bloco K) encontrou um resultado **negativo/misto**: a predição de que a complexidade cairia com a profundidade da sedação não se confirmou (AUC basal-vs-moderada abaixo do acaso: LZc=0,33, PE=0,45; "basal" teve a *menor* complexidade das 4 condições).

Duas frentes de pesquisa (100% busca, sem cálculo) investigaram explicações candidatas para esse negativo, ver `embasamento/nota_anestesia.md` para a leitura completa:

1. Um agente pesquisou hipóteses de alfa (potência alfa occipital reduzindo complexidade basal; anteriorização do alfa causando aumento paradoxal) — conclusão: hipótese do alfa basal tem apoio real mas indireto; hipótese de anteriorização é a mais fraca e parcialmente contraindicada por Boncompte et al. (2021).
2. Um segundo agente confirmou, via texto integral do artigo original (Chennu et al. 2016, PLOS Comp Biol, PMC4713143) e via documentação oficial do FieldTrip Toolbox, que **o próprio dataset já contém dados de responsividade comportamental** (`datainfo.mat`, colunas 3-5: concentração de propofol, tempo de reação, respostas corretas em 40) — usados pelos autores originais para classificar 13 sujeitos como "responsive" e 7 como "drowsy", mas **nunca usados no recompute V2 do projeto** (que só olhou a coluna de estado nominal).

A explicação mais bem sustentada encontrada foi **Newman, Maschke, Mashour & Blain-Moraes (2026, *British Journal of Anaesthesia* 137(2):525-534)** — um estudo que reanalisou **este mesmo dataset Chennu** e encontrou que sujeitos que permanecem responsivos sob sedação moderada mostram um aumento *paradoxal* de complexidade Lempel-Ziv, enquanto sujeitos não-responsivos mostram a queda esperada. Isso é uma explicação candidata forte, já publicada, para por que a análise agregada (que mistura os dois subgrupos) deu um resultado sem tendência clara.

Este script testa diretamente se os dados do projeto replicam esse padrão.

## Limitação metodológica — leia antes de rodar

A classificação "responsive"/"drowsy" usada aqui é uma **reconstrução aproximada**, não os rótulos originais exatos de Chennu et al. (2016):

- O artigo original não deixou os rótulos binários prontos em nenhum arquivo aberto (`datainfo.mat` só tem as 5 colunas cruas; não há S1 Table nem CSV suplementar com o rótulo já calculado).
- O artigo descreve o método em palavras (comparar IC 95% do hit rate binomial no basal vs. sedação moderada por sujeito), mas **não especifica o tipo exato de intervalo de confiança** (Wald, Wilson, Clopper-Pearson). Este script usa Wilson (escolha padrão e robusta para n=40), documentada explicitamente no código.
- Isso deve reproduzir *aproximadamente* a divisão 13 "responsive" / 7 "drowsy" relatada no artigo, mas pequenas diferenças metodológicas podem mudar a classificação de 1-2 sujeitos. O script reporta o número real obtido — não assuma que vai bater exatamente 13/7.

Também não presuma que a estrutura interna exata de `datainfo.mat` (nomes de campo, ordem de colunas) é garantida — ela foi confirmada via documentação oficial do FieldTrip Toolbox e da página do repositório Apollo/Cambridge, não por inspeção direta do binário (arquivo de 3,44 GB, não baixado pelo agente). Se a leitura vier em formato inesperado, o script imprime a estrutura bruta em vez de falhar silenciosamente — **confira a saída do terminal na primeira rodada**.

## Dependências

Mesmas do `analise_anestesia_propofol.py` original (já devem estar no seu `.venv`):

```
pip install mne antropy scipy scikit-learn pymatreader
```

`pymatreader` é o único pacote possivelmente novo em relação ao recompute V2 (usado para ler `datainfo.mat` de forma mais robusta que `scipy.io.loadmat` puro, que costuma ter problemas com tabelas MATLAB heterogêneas). Confirme com `pip show pymatreader mne antropy`.

## Comando

```
python reanalise_responsividade_propofol.py --data-dir <pasta_Sedation-RestingState> --max-subjects 3
```

Rodada pequena primeiro (recomendado) para conferir que `datainfo.mat` está sendo lido no formato esperado — **olhe o log do Passo 1 e Passo 2** antes de prosseguir para a amostra cheia. Se aparecer o aviso "[AVISO IMPORTANTE] Não foi possível extrair colunas 3-5...", pare e mande a estrutura bruta impressa para o agente interpretar antes de continuar.

Depois, a amostra completa (mesmos 20 sujeitos do Bloco K):

```
python reanalise_responsividade_propofol.py --data-dir <pasta_Sedation-RestingState>
```

`<pasta_Sedation-RestingState>` é a mesma pasta já extraída e usada por `analise_anestesia_propofol.py` (reaproveita os `.set` e o `datainfo.mat` existentes — não baixa nada de novo).

## Saídas esperadas (nesta pasta)

- `responsividade_por_sujeito.csv` — hit rate basal/moderada, IC de Wilson, classificação responsive/drowsy reconstruída, por sujeito.
- `propofol_responsividade_por_epoca.csv` — LZc/PE por época, com grupo de responsividade anexado.
- `comparacao_por_grupo.csv` — **o teste central**: médias de LZc/PE e AUC (basal-vs-moderada) separadas por grupo responsive vs. drowsy.
- `correlacao_basal_vs_mudanca.csv` — correlação de Spearman entre complexidade basal e mudança de complexidade sob sedação moderada, por sujeito (análogo ao r=-0,88 de Newman et al. 2026, mas com LZc/PE em vez da complexidade estatística Tipo II deles — não é uma tentativa de reproduzir o número exato).
- `comparacao_por_grupo.png` — figura comparativa (LZc e PE por estado, uma linha por grupo).
- `resumo_frente_d.md` — relatório narrativo gerado automaticamente, com uma seção "Leitura" que não é conclusão pronta — é um guia para interpretar as tabelas depois.

## Depois de rodar

Devolva pelo menos `comparacao_por_grupo.csv`, `correlacao_basal_vs_mudanca.csv`, `responsividade_por_sujeito.csv` e `resumo_frente_d.md` para o agente interpretar. Ele deve:

1. Ler `comparacao_por_grupo.csv`: se o grupo "responsive" tiver `auc_lzc_basal_vs_moderada_positivo_moderada` > 0,5 (LZc maior na sedação moderada) e o grupo "drowsy" tiver AUC < 0,5 (LZc menor), isso **replica** o achado de Newman et al. (2026) neste mesmo dataset e explica o resultado negativo agregado do Bloco K como mistura de subgrupos opostos.
2. Se não replicar, é um resultado negativo igualmente válido — reportar com a mesma honestidade do Bloco K, sem forçar a leitura.
3. Atualizar `embasamento/nota_anestesia.md` e `recompute_empirico_v2/RELATORIO_v2.md` com o resultado real (positivo ou negativo).
4. Atualizar `CHECKLIST_pendencias.md` (Bloco O) marcando a execução como concluída.
