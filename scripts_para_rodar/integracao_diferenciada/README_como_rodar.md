# Frente C — Integração diferenciada com controle de 1/f: como rodar

Este script (`integracao_diferenciada_1f.py`) foi **escrito por um agente e não executado por ele** — segue a regra de governança do `PLANO_ESTRATEGICO_cientifico.md` §0.1 ("agentes não executam cálculos, apenas escrevem scripts; quem roda é o autor, localmente"). A verificação feita pelo agente foi só de **sintaxe** (`python -m py_compile`), não de execução.

## Por que este script existe

`embasamento/SINTESE_pilares.md` (achado #1, 2026-08-06) identificou que o resultado mais forte do projeto — a ordenação de LZc/entropia de permutação por estágio de sono — tem um confundidor parcial: Höhn, Hahn, Lendner & Hoedlmoser (2024, *eNeuro* 11(3), ENEURO.0259-23.2024) mostram que, em banda larga, complexidade e inclinação espectral (1/f) "track highly similar information". A recomendação foi **redefinir a Frente C como prioridade**: testar se a discriminação por estágio sobrevive **acima e além** do 1/f.

Este script faz exatamente isso, e também cumpre a especificação original da Frente C (`PLANO_ESTRATEGICO_cientifico.md` §3): operacionalizar "integração diferenciada" (integração alta E diferenciação alta, não hipersincronia) e comparar sua discriminação (AUC) com a complexidade pura (LZc/PE).

## Limitação metodológica — leia antes de rodar

O Sleep-EDF Cassette só tem **2 canais EEG** (Fpz-Cz, Pz-Oz). Isso **não permite** medidas grafo-teóricas de integração/segregação multi-região (que exigiriam ~8+ canais/ROIs). O script usa proxies de 2 canais, documentados no próprio código:

- **Sincronia bruta** (hipersincronia): coerência espectral broadband entre os 2 canais.
- **Integração**: informação mútua (aproximação gaussiana, `-0.5·ln(1-r²)`) entre os 2 canais.
- **Diferenciação**: entropia de permutação média dos 2 canais (riqueza da dinâmica de cada canal).
- **Índice integração-diferenciada**: integração × diferenciação (as duas precisam estar altas simultaneamente).

Isso é uma simplificação deliberada, não uma análise de rede completa. Reportar como tal no manuscrito — nunca como "medida grafo-teórica" sem essa ressalva.

## Dependências

Além do `requirements.txt` da raiz do projeto (numpy, pandas, matplotlib, scikit-learn), este script precisa:

```
pip install mne antropy scipy fooof
```

Nota: o pacote `fooof` foi renomeado para `specparam` em versões recentes (mesma API básica). O script tenta `from fooof import FOOOF` primeiro e cai para `from specparam import SpectralModel as FOOOF` automaticamente — instale qualquer um dos dois:

```
pip install fooof
# ou, se o pip reclamar que fooof está descontinuado:
pip install specparam
```

`mne` e `antropy` já devem estar no seu `.venv` (usados por `analise_lzc_sleepedf.py` e `analise_sono_v2.py`) — confirme com `pip show mne antropy`.

## Comando

Primeiro, uma rodada pequena para checar que tudo roda sem erro antes da amostra cheia (recomendado — o ajuste FOOOF por época é mais lento que LZc/PE, então vale confirmar com poucos sujeitos primeiro):

```
python integracao_diferenciada_1f.py --n-subjects 3 --data-dir <pasta_cache>
```

Depois, a amostra completa (mesmo tamanho do recompute V2, Bloco K — ~36-40 sujeitos válidos):

```
python integracao_diferenciada_1f.py --n-subjects 41 --data-dir <pasta_cache>
```

`<pasta_cache>` é a mesma pasta de cache do `mne.datasets` já usada nos scripts anteriores (`PHYSIONET_SLEEP_PATH` ou o caminho que você passou em `analise_sono_v2.py` — reutiliza o cache existente, não baixa de novo).

**Aviso de tempo**: o ajuste FOOOF é feito por canal, por época — com 2 canais × ~1300 épocas/sujeito × 40 sujeitos, isso é bem mais lento que o recompute V2 original (que só calculava LZc/PE). Rode a versão com `--n-subjects 3` primeiro para ter uma estimativa de tempo antes de disparar a amostra cheia.

## Saídas esperadas (nesta pasta)

- `integracao_diferenciada_por_epoca.csv` — todas as métricas, por época (subject, stage, lzc, pe, exponent_1f, sync_bruta, integracao_mi, diferenciacao_pe, indice_integ_diferenciada).
- `integracao_diferenciada_por_estagio.csv` — médias/desvios por estágio.
- `auc_comparativo.csv` — AUC (W-vs-N3) de cada métrica, **bruta** e **residualizada por 1/f** (a comparação mais importante — é o teste direto do achado #1).
- `correlacao_parcial.csv` — correlação de Spearman com o estágio, bruta e parcial controlando 1/f.
- `integracao_diferenciada_por_estagio.png` — boxplots comparativos das 6 métricas.
- `scatter_lzc_vs_1f.png` — dispersão LZc × expoente 1/f, colorido por estágio (visualiza o confundidor diretamente).
- `resumo_frente_c.md` — relatório narrativo gerado automaticamente, com uma seção "Leitura" que **não é uma conclusão pronta** — é um guia de como interpretar as tabelas. A interpretação final deve ser feita por um agente depois, olhando os números reais.

## Depois de rodar

Devolva os 7 arquivos de saída (ou pelo menos os 3 CSVs + o `resumo_frente_c.md`) para o agente interpretar. Ele deve:

1. Ler `auc_comparativo.csv`: se `auc_w_vs_n3_residualizada_1f` de `lzc`/`pe`/`indice_integ_diferenciada` ficar próxima da bruta, a discriminação sobrevive ao controle por 1/f. Se cair perto de 0.5, o resultado favorece a leitura do confundidor.
2. Comparar `sync_bruta` (hipersincronia) contra `indice_integ_diferenciada`: a teoria prevê que o índice combinado discrimina melhor que a sincronia pura — se não for o caso, reportar honestamente.
3. Atualizar `CHECKLIST_pendencias.md` (Bloco C, item da Frente C) e `embasamento/SINTESE_pilares.md` com o resultado, seguindo a mesma prática de honestidade do Bloco K (resultado negativo é dado, não fracasso).
