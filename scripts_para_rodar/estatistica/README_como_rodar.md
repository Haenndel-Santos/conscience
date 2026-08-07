# Frente G — Reforço estatístico: como rodar

Este script (`reforco_estatistico.py`) foi **escrito por um agente e não executado por ele** — mesma regra de governança das Frentes C e D (`PLANO_ESTRATEGICO_cientifico.md` §0.1), reiterada explicitamente na especificação da própria Frente G ("scripts de IC/effect size; autor roda"). A verificação do agente foi de **sintaxe** (`python -m py_compile`, passou) e de **execução em dados sintéticos** (não nos dados reais do projeto) para confirmar que a lógica roda sem erro — os números reportados abaixo em "o que esperar" vêm dos dados reais que você já gerou, não deste teste sintético.

## Por que este script existe

Os recomputes já feitos (Blocos F/K/N/O) reportam pontos estimados — AUC, correlação de Spearman — mas até agora sem intervalo de confiança, sem effect size padronizado, e sem correção para múltiplas comparações (várias métricas foram testadas no mesmo conjunto de sujeitos, em rodadas diferentes, sem nunca serem corrigidas em conjunto). A Frente G do plano pede exatamente isso: "reforço estatístico... dos resultados já obtidos" — não um novo experimento, um reforço de rigor sobre o que já existe.

## O que o script faz

Para cada comparação já reportada, recalcula:

- **AUC com IC 95%**, via bootstrap por **sujeito** (não por época) — ver a justificativa detalhada na docstring do script: épocas do mesmo sujeito são correlacionadas, então bootstrap por época daria um IC artificialmente estreito (pseudo-replicação). Reamostrar sujeitos inteiros preserva a unidade real de replicação (n=36 no sono, n=20 no propofol).
- **Effect size**: correlação rank-biserial (2·AUC−1) para as comparações de AUC; Cohen's d pareado (sobre médias por sujeito) para o sono; o próprio ρ de Spearman para as correlações.
- **Correção de Benjamini-Hochberg (FDR)** sobre todos os p-valores coletados juntos — escolhida em vez de Bonferroni por ser menos conservadora quando os testes não são todos independentes (várias métricas no mesmo dataset).

Cobre quatro fontes, cada uma lida do CSV por época já existente (nenhum dado novo é baixado ou recalculado do zero):

1. **Bloco F/K** — Sleep-EDF, W vs N3 (LZc, PE).
2. **Bloco K** — propofol por dose nominal, basal vs sedação moderada (LZc, PE) — usa a mesma convenção de `analise_anestesia_propofol.py` (positivo = basal).
3. **Bloco O** — propofol por responsividade (Frente D), basal vs moderada, separado por grupo responsive/drowsy, mais a correlação basal×mudança — usa a convenção de `reanalise_responsividade_propofol.py` (positivo = sedação moderada), proposital e diferente da do Bloco K (documentado no próprio script).
4. **Bloco N** — Frente C (integração diferenciada + 1/f), se o CSV já existir: AUC bruta e residualizada por 1/f para LZc, PE, sincronia bruta, integração (MI) e índice combinado. A residualização é recalculada aqui (regressão linear simples sobre o expoente 1/f), não importada do outro script, para este ficar autocontido.

Se algum CSV de entrada não existir ainda (por exemplo, a Frente C com `--n-subjects 41` ainda não terminou quando você for rodar isto), o script **avisa e pula essa seção** em vez de falhar — rode de novo depois.

## Dependências

Já devem estar todas instaladas no seu `.venv` (usadas pelos scripts anteriores): `numpy`, `pandas`, `scipy`, `scikit-learn`. Nenhuma dependência nova.

## Comando

```
python reforco_estatistico.py --project-root <caminho_para_a_raiz_do_projeto>
```

Se você rodar de dentro da própria pasta `scripts_para_rodar/estatistica/`, o `--project-root` pode ser omitido (o padrão já assume dois níveis acima). Exemplo, rodando de dentro dessa pasta:

```
python reforco_estatistico.py
```

O bootstrap (2000 reamostragens por padrão, `--n-boot` para ajustar) é rápido — os CSVs de entrada são pequenos (milhares de linhas, não EEG bruto) — deve rodar em segundos a poucos minutos, bem mais rápido que os scripts da Frente C/D.

## Saídas esperadas (nesta pasta)

- `reforco_estatistico_resultados.csv` — uma linha por comparação: bloco, comparação, métrica, tipo (AUC/Spearman/Cohen's d), estatística, IC95, effect size, p-valor bruto, **p-valor corrigido por FDR**.
- `resumo_reforco_estatistico.md` — relatório narrativo com uma seção "Leitura" que não é conclusão pronta, é guia de interpretação.

## Depois de rodar

Devolva `reforco_estatistico_resultados.csv` e `resumo_reforco_estatistico.md` para um agente interpretar. Ele deve:

1. Conferir se os pontos estimados (coluna `estatistica`) batem com os números já reportados em `RELATORIO_v2.md`, `resumo_frente_c.md` e `resumo_frente_d.md` — devem ser idênticos ou muito próximos; se não baterem, é sinal de bug, não de resultado novo.
2. Verificar onde o IC95 exclui o valor nulo (0,5 para AUC, 0 para Spearman) **e** `p_valor_fdr_bh < 0,05` — só esses resultados devem ser chamados de "robustos" no manuscrito.
3. Atualizar `embasamento/registro_falsificabilidade.md` (Frente G) com os IC/effect sizes/p-valores corrigidos, substituindo os pontos estimados "nus" que estavam lá antes.
