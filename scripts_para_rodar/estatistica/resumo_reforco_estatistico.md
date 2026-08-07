# Frente G — Resumo do reforço estatístico (gerado automaticamente, a interpretar depois)

Total de comparações calculadas: 22
Comparações com p-valor associado (bootstrap ou analítico): 20
Sobrevivem à correção de Benjamini-Hochberg (FDR, q<0.05): 11

## Como ler a tabela

- **estatistica**: valor pontual (AUC, Spearman rho, ou Cohen's d) já reportado nos Blocos F/K/N/O.
- **ic95_low / ic95_high**: intervalo de confiança 95%, via bootstrap por SUJEITO (não por época —
  ver docstring do script para a justificativa: bootstrap por época daria IC artificialmente estreito).
- **effect_size**: para AUC, a correlação rank-biserial (2·AUC−1, varia de −1 a 1, 0 = sem discriminação);
  para Spearman, o próprio rho; para Cohen's d, o próprio d (pareado, sobre médias por sujeito).
- **p_valor**: bootstrap (para AUC) ou analítico já reportado (para Spearman).
- **p_valor_fdr_bh**: p-valor corrigido por Benjamini-Hochberg (FDR) considerando TODOS os testes
  desta tabela em conjunto — é este valor, não o p_valor bruto, que deveria ser citado no manuscrito
  ao afirmar significância, porque múltiplas métricas/comparações foram testadas no mesmo conjunto
  de sujeitos ao longo dos Blocos F/K/N/O.

## Leitura (preencher depois de rodar — não inventar conclusão aqui)
- Onde o IC95 do AUC exclui 0,5 (ou o IC95 do rho exclui 0), e o p_valor_fdr_bh < 0,05, o resultado
  é robusto a essa correção.
- Onde o IC95 é largo e cruza 0,5/0 (comum com n pequeno, ex. o grupo "drowsy" da Frente D com n=7),
  isso deve ser reportado como incerteza real, não escondido atrás do ponto estimado.
- Comparar esta tabela com os relatórios narrativos originais (RELATORIO_v2.md, resumo_frente_c.md,
  resumo_frente_d.md) — nenhuma conclusão qualitativa deveria mudar, mas a precisão declarada muda.
