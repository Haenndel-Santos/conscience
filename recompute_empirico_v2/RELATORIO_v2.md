# Recompute Empírico V2 — Amostra Ampliada + Segunda Métrica + Extremo de Anestesia

Data: 2026-08-05/06 · Protocolo: `_revisao_2026-08-05/confronto_empirico.md`, Parte 4 · Estende (sem sobrescrever) `recompute_empirico_sleepedf/`.

## 1. Amostragem

### Sleep-EDF Cassette (sono)

- **Dataset:** Sleep-EDF Expanded, subset *sleep-cassette* (PhysioNet, ODC-BY, sem cadastro), via `mne.datasets.sleep_physionet.age.fetch_data`.
- **Amostra solicitada:** sujeitos de índice 0 a 40 (41 índices), recording 1 — critério de seleção: os primeiros N índices do subset, mesmo critério da v1, apenas estendido.
- **Truncamento/exclusões (registrados integralmente):**
  - Índices **36** e **39**: ausentes do dataset por construção (36 não tem gravação "recording 1"; 39 não existe no corpus) — limitação conhecida e documentada do próprio Sleep-EDF Cassette, não uma escolha nossa.
  - Índices **32, 33, 34**: baixados com sucesso, mas **excluídos da análise** porque não contêm nenhuma época de estágio N3 (sono de ondas lentas) — provavelmente sujeitos sem sono profundo detectável na noite gravada (comum em amostras com sujeitos mais velhos, que é o foco etário do Sleep-EDF Cassette). Sem N3, a tarefa de classificação W-vs-N3 e a linha de N3 na tabela ficariam vazias para esses sujeitos; excluí-los é mais honesto do que preenchê-los artificialmente.
  - **N final: 36 sujeitos, 39.086 épocas de 30 s** — 3,6× a amostra da v1 (10 sujeitos, 10.850 épocas).
- Ambiente: mesmo pipeline da v1 (filtro 0,5–40 Hz, canais EEG Fpz-Cz/Pz-Oz, recorte de 30 min de vigília antes/depois do período de sono).

### Propofol (Cambridge/Chennu et al. 2016) — extremo de anestesia

- **Dataset:** "Brain connectivity during propofol sedation" — Chennu S, O'Connor S, Adapa R, Menon DK, Bekinschtein TA. *Brain Connectivity Dissociates Responsiveness from Drug Exposure during Propofol-Induced Transitions of Consciousness*. PLOS Computational Biology. 2016. DOI 10.1371/journal.pcbi.1004669 (verificado via busca web nesta sessão — usado apenas para atribuição do dataset, não inserido no manuscrito). Dados abertos, CC BY 2.0 UK: [repository.cam.ac.uk/handle/1810/252736](https://www.repository.cam.ac.uk/handle/1810/252736).
- **Amostra: 20 de 20 sujeitos disponíveis no dataset — sem truncamento.** EEG de 91 canais, 250 Hz, 4 estados por sujeito (basal, sedação leve, sedação moderada, recuperação), ~7 min cada, já pré-segmentados pelos autores originais em épocas de ~10 s (artefato removido, referenciado à média dos canais). Mapeamento arquivo → estado obtido de `datainfo.mat` e verificado programaticamente: 20 sujeitos × 4 estados = 80 arquivos `.set`, sem exceção ao padrão.
- **Download:** 3,44 GB (zip único), obtido diretamente do link de bitstream do repositório Apollo (Cambridge) — **sem bloqueio de licença ou acesso**, ao contrário do que se antecipava como risco.
- **Total de épocas analisadas:** 3.082.

## 2. LZc × Entropia de Permutação — concordância

### Sleep-EDF (36 sujeitos, 39.086 épocas)

| Estágio | LZc (média±dp) | PE (média±dp) | N épocas |
|---|---|---|---|
| **W** | **0,4531 ± 0,0801** | **0,7796 ± 0,0237** | 8.923 |
| N1 | 0,4062 ± 0,0608 | 0,7576 ± 0,0205 | 3.264 |
| REM | 0,3773 ± 0,0501 | 0,7517 ± 0,0193 | 6.155 |
| N2 | 0,3372 ± 0,0527 | 0,7268 ± 0,0241 | 16.772 |
| **N3** | **0,2326 ± 0,0391** | **0,6908 ± 0,0268** | 3.972 |

**Concordância excelente:** as duas métricas produzem a **mesma ordenação exata** por estágio (Spearman = **1,0000**): W > N1 > REM > N2 > N3. Correlação época-a-época (todas as 39.086 épocas): Spearman = **0,7235** — forte, mas não perfeita, indicando que as métricas capturam uma propriedade fortemente relacionada, porém não idêntica.

**AUC W-vs-N3:** LZc = **0,9919**, PE = **0,9840** — ambas quase perfeitas, e **reforçam** (com amostra 3,6× maior e uma métrica totalmente independente) o resultado já robusto da v1 (LZc, AUC=0,9948, N=10).

### Propofol (20 sujeitos, 3.082 épocas)

Concordância **fraca**: Spearman entre as ordenações por estado = **0,40**. LZc ordena `sedação moderada > sedação leve > recuperação > basal`; PE ordena `sedação leve > recuperação > sedação moderada > basal`. As duas métricas concordam em apenas um ponto: **`basal` tem a menor complexidade das quatro condições em ambas** — mas discordam sobre qual estado de sedação é o "pico".

**Leitura honesta:** as duas métricas concordam fortemente quando o efeito subjacente é grande e robusto (sono), e discordam quando o efeito é pequeno e possivelmente não-monotônico ou heterogêneo entre sujeitos (anestesia parcial). Isso é, em si, informação útil: a força da concordância entre métricas independentes pode servir como um indicador informal da robustez do próprio efeito biológico.

## 3. Extremo de anestesia (Cambridge/propofol)

### Resultado

| Estado | LZc (média±dp) | PE (média±dp) | N épocas |
|---|---|---|---|
| basal | 0,4233 ± 0,0520 | 0,6917 ± 0,0286 | 755 |
| sedação leve | 0,4477 ± 0,0629 | 0,6984 ± 0,0242 | 780 |
| sedação moderada | 0,4508 ± 0,0643 | 0,6949 ± 0,0217 | 751 |
| recuperação | 0,4426 ± 0,0416 | 0,6983 ± 0,0255 | 796 |

**AUC "basal vs. sedação moderada":** LZc = **0,3306**, PE = **0,4533** — ambas abaixo ou próximas do nível de acaso (0,5), e na **direção oposta** à predição (basal tende a ter complexidade *menor*, não maior, que a sedação moderada).

### A predição se confirmou? **Não — resultado negativo/misto, reportado com honestidade.**

A hipótese testada era: complexidade cai com a profundidade da sedação, estendendo o gradiente vigília>sono para vigília>anestesia. **Isso não se confirmou nesta amostra, com estas métricas, nestes níveis de sedação:**

- ❌ `basal` (vigília, olhos fechados, repouso) teve a **menor** complexidade média das quatro condições — não a maior — em ambas as métricas.
- ❌ A ordenação entre os dois níveis de sedação é **inconsistente entre as duas métricas** (LZc favorece "moderada" como pico; PE favorece "leve").
- ⚠️ O efeito é **pequeno** frente à variabilidade intra-estado: as diferenças de médias entre estados (~0,03 em LZc) são menores que um desvio-padrão dentro de qualquer estado (~0,05–0,06) — não é um sinal robusto como o observado no sono (onde a diferença W-vs-N3 foi de ~0,22, muito maior que os desvios-padrão intra-estágio de ~0,04–0,08).

**Interpretação honesta (hipóteses explicativas, não achados adicionais confirmados nesta sessão):**

1. **Vigília de olhos fechados em repouso tem ritmo alfa forte e regular** (~8–12 Hz, tipicamente proeminente em regiões posteriores). Uma oscilação forte e regular **reduz** medidas de complexidade de banda larga como LZc e entropia de permutação, porque o sinal fica mais previsível — um fenômeno de EEG bem documentado, distinto de "vigília ativa" com olhos abertos, que tende a ser mais complexa.
2. **Sedação leve/moderada por propofol pode desorganizar esse ritmo alfa posterior** e induzir atividade alfa anteriorizada e conteúdo de banda lenta, o que pode **aumentar** a complexidade de banda larga medida mesmo com redução da consciência — uma dissociação entre mudança espectral e "quantidade de consciência" já discutida na literatura de anestesia.
3. **Os níveis de sedação deste dataset não são anestesia geral/perda de consciência confirmada para todos os sujeitos.** O próprio artigo de Chennu et al. (2016) que acompanha este dataset tem como achado central que a **responsividade comportamental se dissocia da exposição à droga** — ou seja, "sedação moderada" (rótulo nominal, por dose) não significa necessariamente "inconsciente" para todos os 20 sujeitos. A predição "vigília > anestesia" pressupõe perda de consciência efetiva, que este desenho (sedação parcial, sem uso da informação de responsividade nesta análise) não garante uniformemente. A figura (`propofol_lzc_pe_por_estado.png`) mostra uma cauda de épocas com complexidade bem mais baixa dentro de "leve" e "moderada" — compatível com alguns sujeitos genuinamente perdendo responsividade enquanto outros não, mas **isso não foi testado formalmente aqui** (exigiria cruzar com os dados comportamentais/de responsividade presentes no `datainfo.mat`, que fica como item em aberto).

Nenhuma dessas três hipóteses foi testada adicionalmente nesta sessão — são explicações plausíveis, fundamentadas em fenômenos conhecidos de EEG e no próprio artigo do dataset, não conclusões novas confirmadas.

## 4. Confronto com o índice 𝒞(t) do modelo

O modelo (`consciousness_model_v3.py`) prevê a ordenação **wake > anxiety > deep_sleep > reflex** para 𝒞(t) (valores de referência: wake≈0,59–0,62; anxiety≈0,52–0,54; deep_sleep≈0,34–0,38; reflex≈0,28–0,32 — ver `dados atuais/regime_summary.csv` e `reforco_outputs/`). O confronto abaixo é **sempre de ordenação/direção**, nunca de valores absolutos — o índice sintético não está calibrado em unidades de EEG e as duas métricas empíricas (LZc, PE) têm escalas próprias.

| Domínio | Extremo "alto" | Extremo "baixo" | Direção prevista pelo modelo confirmada? |
|---|---|---|---|
| Modelo (V3, sintético) | wake (𝒞≈0,60) | deep_sleep/reflex (𝒞≈0,30–0,38) | — (é a própria predição) |
| Sono real (Sleep-EDF, N=36, LZc+PE) | W (LZc=0,453; PE=0,780) | N3 (LZc=0,233; PE=0,691) | ✅ **Sim** — AUC≈0,98–0,99, direção e magnitude de separação fortemente alinhadas |
| Anestesia real (propofol, N=20, LZc+PE) | sedação leve/moderada (LZc mais alto) | basal (LZc=0,423, o mais baixo) | ❌ **Não** — a direção observada é oposta à esperada por analogia com o sono; efeito pequeno e inconsistente entre métricas |

**Leitura honesta do confronto:** o eixo central da teoria (integração alta ≠ integração baixa, com separação grande e replicável) recebe **apoio forte e agora mais robusto** do lado do sono — replicado com quase 4× mais dados e uma segunda métrica totalmente independente, que concorda perfeitamente com a primeira. Do lado da anestesia, o recompute **não estende** esse padrão da forma simples que se antecipava; o resultado é honesto o suficiente para apontar que "vigília > sono profundo" e "vigília > sedação farmacológica parcial" **não são o mesmo tipo de comparação** — a segunda depende de confirmar perda de consciência real, não apenas dose nominal de droga, algo que este desenho específico (e esta análise) não capturam.

## 5. Limites honestos

- **Sleep-EDF:** N=36 (de 153 disponíveis no subset completo) — ainda não é a população inteira, mas já é uma amostra substancial; 3 sujeitos excluídos por ausência de N3 (documentado acima), não por conveniência.
- **Propofol:** N=20 (100% do dataset, sem truncamento) é uma amostra pequena para conclusões populacionais fortes; a heterogeneidade visível na figura (outliers de baixa complexidade dentro de "leve"/"moderada") sugere que uma análise estratificada por responsividade comportamental real (não apenas rótulo nominal de dose) poderia revelar um padrão diferente — não feita aqui.
- **Atualização (Frente D, 2026-08-07) — a estratificação por responsividade foi feita, e o padrão sugerido acima se confirmou.** `scripts_para_rodar/anestesia_responsividade/reanalise_responsividade_propofol.py` reconstruiu a classificação responsive/drowsy dos 20 sujeitos (IC de Wilson do hit rate comportamental, basal vs. sedação moderada — bateu 13/13 responsive e 7/7 drowsy com a contagem relatada por Chennu et al. 2016) e reestratificou basal-vs-moderada por grupo: o grupo "responsive" (n=13) mostrou LZc e PE **subindo** sob sedação moderada (AUC=0,791 e 0,642, respectivamente — aumento paradoxal), e o grupo "drowsy" (n=7) mostrou as duas métricas **caindo** (AUC=0,411 e 0,283). Isso replica diretamente Newman, Maschke, Mashour & Blain-Moraes (2026, *Br J Anaesth* 137(2):525-534, DOI 10.1016/j.bja.2026.03.082), que fizeram exatamente essa reanálise no mesmo dataset. A correlação basal×mudança (Spearman, n=20) foi significativa para PE (ρ=−0,749, p=0,0001) e na mesma direção mas não-significativa para LZc (ρ=−0,340, p=0,143) — mesmo sentido qualitativo do r=−0,88 que Newman et al. relatam para uma métrica diferente (complexidade estatística Tipo II). **Leitura honesta:** o resultado negativo/misto reportado acima (item 3 da seção 3 e Bloco K) agora tem explicação candidata testada nos próprios dados — os 20 sujeitos não respondem de forma homogênea ao propofol, e a média do grupo inteiro cancela dois padrões opostos reais. Isso não reverte o resultado negativo original (que continua correto como reportado para a análise agregada por dose nominal), mas mostra que ele não é evidência contra a teoria — é evidência de que "sedação moderada" nominal não é uma variável de profundidade de consciência confiável, exatamente como o próprio Chennu et al. (2016) já argumentava. Detalhes completos em `embasamento/nota_anestesia.md`.
- Apenas duas métricas de complexidade (LZc, entropia de permutação); nenhuma delas mede diretamente "integração diferenciada" no sentido do modelo (que combina acoplamento, complexidade *e* recursividade).
- O confronto com o modelo é qualitativo/direcional, nunca de unidades ou magnitudes.
- Resultados de propofol são **negativos/mistos em relação à hipótese original** — isso está reportado tal como observado, sem tentativa de forçar uma confirmação. Um resultado negativo bem documentado é, aqui, mais valioso para a integridade do projeto do que uma confirmação forçada.
- **Possível confundidor espectral (adicionado após verificação independente):** Höhn, Hahn, Lendner & Hoedlmoser (2024), *eNeuro* 11(3), ENEURO.0259-23.2024, DOI 10.1523/ENEURO.0259-23.2024, mostram que em banda larga (1–45 Hz) a inclinação espectral (1/f slope) e a LZc covariam fortemente ("track highly similar information") entre vigília e N3 — parte do resultado de LZc por estágio pode estar refletindo essa mesma mudança espectral, não só "complexidade" em um sentido mais forte. A entropia de permutação (2ª métrica usada aqui) não resolve essa dúvida de forma independente, pois também é sensível ao conteúdo espectral do sinal. Nem slope nem uma decomposição espectral formal foram calculados nesta sessão; ver `CHECKLIST_pendencias.md`, Bloco L, item L4.
- **Atualização (Frente C + Frente G, 2026-08-07) — o confundidor foi testado diretamente nos dados do projeto, com resultado negativo para a leitura de "integração diferenciada".** `scripts_para_rodar/integracao_diferenciada/integracao_diferenciada_1f.py` recomputou LZc/PE e o expoente aperiódico (1/f, via FOOOF/specparam) por época na amostra completa do Sleep-EDF (n=36 sujeitos válidos de 41 solicitados). Resultado: a AUC W-vs-N3, quase perfeita bruta (LZc=0,992; PE=0,984, idêntica à reportada acima), **cai para 0,550 (LZc) e 0,580 (PE) depois de residualizar pelo expoente 1/f**. O reforço estatístico da Frente G (`reforco_estatistico.py`, bootstrap por sujeito, 2000 reamostragens, correção de Benjamini-Hochberg) mostra que o IC 95% de ambos os AUC residualizados **cruza 0,5** (LZc: [0,458–0,633]; PE: [0,474–0,677]) e **nenhum sobrevive à correção FDR** (q=0,359 e q=0,183) — ou seja, depois de controlar 1/f e corrigir para múltiplas comparações, não há evidência estatisticamente robusta de que LZc/PE discriminem W-vs-N3 além do que o próprio expoente 1/f já explica. A correlação de Spearman com o estágio do sono colapsa na mesma direção: 0,683→−0,010 (LZc) e 0,737→0,085 (PE). O expoente 1/f isolado quase discrimina W-vs-N3 sozinho (AUC bruta≈0,006, ou seja ≈0,994 em módulo) — mais forte, isoladamente, que qualquer uma das métricas de complexidade testadas aqui. O mesmo script também testou o índice combinado de "integração diferenciada" (informação mútua × entropia de permutação, proxy de 2 canais) contra a sincronia bruta pura: bruta, o índice combinado (AUC=0,218) **não supera** a sincronia bruta (AUC=0,148 — na verdade mais extrema); residualizados por 1/f, os dois ficam estatisticamente indistinguíveis do acaso e um do outro (nenhum sobrevive à FDR). **Leitura honesta:** o resultado de LZc/PE por estágio de sono reportado na seção 2 acima continua sendo um dado real, robusto e bem replicado — não está sendo retratado. O que não se sustentou foi a interpretação mais forte que a teoria propõe para esse dado (que ele reflita "integração diferenciada" além do declínio da inclinação espectral com o aprofundamento do sono). Isso é consistente com o confundidor de Höhn et al. (2024) explicando a maior parte da discriminação bruta observada — um resultado negativo importante, não uma falha do teste. Detalhes completos: `embasamento/registro_falsificabilidade.md` (predições 1.2, 1.3, agora ❌ FALHOU) e `CHECKLIST_pendencias.md` (Blocos N e P).

## Referências usadas nesta análise (verificadas nesta sessão)

- Bandt C, Pompe B. Permutation entropy: a natural complexity measure for time series. *Physical Review Letters*. 2002;88:174102. doi:10.1103/PhysRevLett.88.174102 — ✅ Verificada via busca web (múltiplas bases de citação acadêmica); usada apenas para atribuição do método (`antropy.perm_entropy`), não inserida no manuscrito.
- Chennu S, O'Connor S, Adapa R, Menon DK, Bekinschtein TA. Brain Connectivity Dissociates Responsiveness from Drug Exposure during Propofol-Induced Transitions of Consciousness. *PLOS Computational Biology*. 2016. DOI 10.1371/journal.pcbi.1004669 — ✅ Verificada via busca web; usada apenas para atribuição do dataset, não inserida no manuscrito.
- Denis D, et al. (2022) e Zhang Y, et al. (2009) — já verificadas e citadas em `recompute_empirico_sleepedf/RELATORIO_lzc_sleepedf.md`; não reverificadas nesta sessão (sem novo uso que exigisse isso).

## Reprodutibilidade

- Ambos os scripts são determinísticos dado o mesmo conjunto de dados de entrada (nenhuma amostragem aleatória própria é usada — LZc e PE são funções determinísticas do sinal). A fonte de não-determinismo possível é upstream (versão do `antropy`/`mne`/`scipy` instalada; ambiente registrado em `requirements.txt` e `.venv/`).
- Sleep-EDF: `python analise_sono_v2.py --n-subjects 41 --data-dir <pasta>`.
- Propofol: `python analise_anestesia_propofol.py --data-dir <pasta_extraida>` (extrai `sedation-restingstate.zip` antes).
- **Nenhuma pasta antiga foi sobrescrita**: `recompute_empirico_sleepedf/` permanece intocada; todas as saídas novas ficam em `recompute_empirico_v2/`.

## Arquivos gerados

- `analise_sono_v2.py`, `analise_anestesia_propofol.py` — scripts completos, reprodutíveis.
- `sleepedf_por_epoca.csv` (39.086 linhas), `sleepedf_por_estagio.csv`, `sleepedf_resumo.txt`, `sleepedf_lzc_pe_por_estagio.png` — Sleep-EDF ampliado.
- `propofol_por_epoca.csv` (3.082 linhas), `propofol_por_estado.csv`, `propofol_resumo.txt`, `propofol_lzc_pe_por_estado.png` — propofol.
