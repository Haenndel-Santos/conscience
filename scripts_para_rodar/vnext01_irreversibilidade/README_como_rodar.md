# Instrumentação da Fase 0 — VNext-01

> ⚠️ **Código preparado, ainda NÃO executado sobre os dados-alvo.**
> Nenhum dos dois scripts de análise foi rodado. Nenhum número deste diretório é resultado.
> Este diretório existe para ser **revisado e mergeado antes** da execução, de modo que o
> SHA que você roda seja exatamente o SHA que foi revisado.

Corresponde às etapas **0.3–0.6** da Fase 0 do [`PROTOCOLO_VNext_01.md`](../../PROTOCOLO_VNext_01.md).

## Revisão de 2026-08-17, antes do merge

Uma revisão pré-merge encontrou dois defeitos que teriam invertido a leitura da etapa 0.6, e
mais três de menor porte. Todos foram corrigidos **antes de qualquer execução sobre os
dados-alvo**, e o registro completo, com os números que sustentam cada um, está em
[`embasamento/revisao_fase0_pre_merge.md`](../../embasamento/revisao_fase0_pre_merge.md).

| | O que estava errado | O que mudou |
|---|---|---|
| **F1** | `passa()` usava `.any()` sobre todos os efeitos ≥ 0,60, então o maior efeito da grade (AUC=0,75) decidia e os dois campos saíam `True` para qualquer dispersão | A decisão é avaliada numa **âncora declarada** (`AUC_ANCORA_PODER`), que é o menor efeito de interesse de §6.4 — o efeito que §10.3 nomeia no portão |
| **F3** | O gerador truncava uma normal por reamostragem e errava os dois momentos (a célula rotulada AUC=0,60 simulava média 0,582; dp entre 11% e 24% abaixo do alvo). Para boa parte da grade o par (média, dp) é **inviável** para qualquer normal truncada em [0,1] | Beta parametrizada em (média, dp): suporte por construção, momentos exatos em forma fechada, viabilidade checada contra o limite universal `dp² < média(1−média)`, e média e dp **realizados** reportados em cada linha |
| **F4** | A faixa "empírica" tinha 13 dp em [0,2248; 0,2845], todos residualizados — mais estreita que o próprio fallback pré-declarado | A grade é a **união** das duas famílias já congeladas (17 cenários, 0,1173–0,3519). Nenhum número novo. E o caminho degradado exige `--permitir-fallback` explícito |
| **F5** | `cobertura_hipnogramas.py` contava os 39 registros do cache contra o critério "30 dos **36**", sem identificar os 3 sem N3 | A coorte é derivada pela mesma regra de exclusão do projeto; se o tamanho derivado não for 36, **nenhum veredito é emitido**. `--coorte` aceita a lista explícita |
| **F6** | `hipnograma_cobre_registro` usava a duração anotada, que inclui `Sleep stage ?` — verdadeiro mesmo num hipnograma que não pontuasse nada | Passou a usar a duração **pontuada**; as duas saem no CSV |

**F2 segue aberta, e é decisão do autor.** §6.4 fixa o menor efeito de interesse em AUC = 0,55;
§10.2 deriva o limiar de suporte 0,60 do dz que **já** dá 80% de poder em n=36, isto é, 0,60 é
aproximadamente o efeito mínimo detectável; e §10.3 exige 80% de poder no menor efeito de
interesse. Os três não podem valer juntos. O script **não resolve** a tensão: ele a mede e a
reporta em campos separados, e `AUC_ANCORA_PODER` carrega hoje o valor que §10.3 declara
literalmente. Mudar essa constante é emenda de protocolo, com registro na §16 — não ajuste de
código.

**F7 também segue aberta, e não é corrigível aqui.** A discrepância espectral residual do IAAFT
está pré-registrada como ameaça em três documentos, mas **não existe uma linha de código de
IAAFT no projeto** — a obrigação é atribuída ao smoke test da Fase 1, que ainda não foi escrito.
Como a normalização por ensemble é o que define o zero da métrica, essa medição precisa nascer
junto do gerador de surrogates, com tolerância declarada antes de o número existir.

## Por que isto é uma PR separada

A cadeia de proveniência que o projeto está construindo é:

**literatura ✅ → protocolo ✅ → código congelado (aqui) → execução → resultado**

Cada elo precisa ser auditável isoladamente. Misturar código ainda não validado com
premissa já verificada tornaria impossível dizer, no histórico, qual dos dois falhou se
algo falhar. Por isso a verificação bibliográfica (PR #3) foi mergeada antes, e por isso
estes scripts vêm antes de qualquer execução.

O ganho concreto: se a saída for desfavorável à teoria, ninguém poderá alegar que a
implementação foi adaptada retrospectivamente para produzir o resultado desejado.

## O que roda, e em que ordem

```bash
python cobertura_hipnogramas.py --data-dir <pasta_cache_sleep_edf> --out-dir saida_vnext01
```

```bash
python poder_vnext01.py --n-sim 2000 --out-dir saida_vnext01
```

A varredura de poder leva ~4 min de parede (17 cenários de dispersão × 9 efeitos × 2000
réplicas, medidos a 0,73 ms por réplica).

`poder_vnext01.py` **não lê dado de EEG** — opera sobre parâmetros de desenho e sobre
desvios-padrão já congelados em `../teste_calibrado/resultados_por_sujeito.csv`. Pode rodar
em qualquer máquina, em segundos a minutos.

`cobertura_hipnogramas.py` precisa dos arquivos do Sleep-EDF já em cache. Ele **não baixa
nada** por padrão.

### Testes de corretude (opcional, rápido)

```bash
python testes_instrumentacao.py
```

Verificam invariantes de implementação — não produzem número científico e não tocam EEG.
Foram executados na preparação desta PR e passaram; a saída não é resultado de nada.

---

## `cobertura_hipnogramas.py` — checagem Z12 (etapas 0.3–0.4)

**Pergunta.** Os hipnogramas do Sleep-EDF cobrem as ~20 h da gravação? Se cobrirem, existe
vigília **ativa** recuperável sem trocar de dataset — o que ataca de uma vez a falha do
proxy de EMG no REM e a natureza do contraste W-vs-N3, hoje feito contra o período calmo em
torno do sono.

**Critério, fixado em §3.2 antes desta checagem:** o braço W(ativo) só é executado se, em
pelo menos **30 dos 36 participantes**, existirem **≥30 épocas** (15 min) anotadas como
vigília fora da janela de ±30 min do corte atual.

**A coorte contada é a de §3.2, não o cache (F5).** O cache tem 39 pares PSG/hipnograma, e os 36
são os que sobreviveram às exclusões do projeto — 3 sem N3, 2 índices ausentes do dataset. O
script deriva a coorte pela mesma regra (N3 anotado **dentro** da janela de corte, que é onde o
pipeline epoca) e conta sobre ela. **Se o tamanho derivado não for 36, nenhum veredito é
emitido** e o script sai com código 3: contar 30 de um denominador diferente responde a outra
pergunta, e não há leitura em que isso seja conservador. `--coorte <arquivo>` aceita a lista
explícita de registros e tem precedência sobre a derivação.

**Filosofia: descritivo e determinístico.** O script não calcula métrica, não filtra sinal,
não rejeita artefato e **não decide** se o braço será executado. Ele conta, contra um
critério que já existia, e reporta quem satisfaz, quem não satisfaz e por quê.

**Uma ressalva que o próprio critério carrega.** §3.2 diz "após rejeição de artefato". Este
script mede a cobertura **anotada, sem rejeição de artefato**, porque rejeitar artefato
exigiria carregar o sinal e aplicar um pipeline — o que faria dele um script de análise. A
contagem é, portanto, um **limite superior**. O veredito sai como
`criterio_satisfeito_antes_de_artefato`, e a leitura pré-declarada é:

| Resultado | Leitura |
|---|---|
| Não satisfeito nem no limite superior | Decisão tomada: W(ativo) não é executado. O contraste primário segue como está — que é o desenho pré-declarado de qualquer forma. |
| Satisfeito com folga | Braço autorizado, **ainda** sujeito aos controles de deriva de §14.3 (hora do dia, impedância, EMG), que são confundidores alinhados ao contraste e não somem por haver dado disponível. |
| Satisfeito por margem apertada | A passada de rejeição de artefato passa a ser obrigatória antes da decisão. |

**Reproduz exatamente o corte do pipeline atual** (`analise_sono_v2.py`, linhas 66–72),
inclusive a âncora em `sleep_annots[1]` e `[-2]`, que pula a primeira e a última anotação
pontuada — comportamento que só faz sentido se essas forem blocos longos de vigília, e que
este script mede.

**Saídas:** `cobertura_hipnogramas.csv` (uma linha por registro, machine-readable),
`cobertura_hipnogramas_meta.json` (veredito, critério, versões), `cobertura_hipnogramas.md`
(relatório humano).

---

## `poder_vnext01.py` — poder a priori (etapas 0.5–0.6)

### O problema que ele resolve

A dispersão por participante da métrica **nova** (irreversibilidade normalizada) é
**desconhecida**. O desvio-padrão de **0,2346** vem da LZc residualizada — mesma amostra de
36 participantes, mesmo teste, análise concluída — e por isso é um cenário de referência
legítimo. Mas **não é uma estimativa da variabilidade da irreversibilidade**, e fixá-lo como
se fosse transformaria uma analogia entre métricas numa premissa quantitativa.

Por isso o script varre uma **família de dispersões**, e o 0,2346 entra como referência sem
privilégio decisório.

### Como a faixa é obtida (regra mecânica, pré-declarada)

Fonte: `../teste_calibrado/resultados_por_sujeito.csv`, coluna `auc_dp`.

**Regra de inclusão:** entram as linhas cuja `auc_media` caia em **[0,35; 0,65]**.

O motivo, declarado antes de qualquer poder ser calculado: quando a AUC média se aproxima
de 0 ou 1, as AUCs por participante ficam comprimidas contra a fronteira e o desvio-padrão
despenca **por artefato de limite**, não por a métrica ser mais estável. As métricas brutas
do projeto ficam em AUC ≈0,99 (LZc, PE) ou ≈0,14–0,20 (sincronia, MI, índice), com dp de
0,018 a 0,16 — usá-las como cenários para uma métrica que se espera próxima do acaso
inflaria o poder por construção. A regra as exclui por **critério mecânico** (posição no
eixo da AUC), não por escolha caso a caso, e as excluídas são **listadas nominalmente** na
saída para auditoria.

**União com a família de multiplicadores (F4).** A faixa varrida é a união das linhas que
sobrevivem à regra com a família pré-declarada de multiplicadores 0,5× / 0,75× / 1,0× / 1,25× /
1,5× sobre 0,2346 — aproximadamente 0,1173 / 0,1760 / 0,2346 / 0,2933 / 0,3519. São 17 cenários,
de 0,1173 a 0,3519.

O motivo: as 14 linhas que a regra admite são **todas** residualizadas, agrupadas em dois blocos
estreitos (≈0,225–0,235, a família LZc, contada seis vezes entre `sono` e `sono-multi`;
≈0,267–0,285, a família PE/sincronia/MI/índice), com 27% de amplitude total. Uma varredura
confinada a esse intervalo não é teste de robustez — a dispersão da métrica **nova** é
desconhecida e pode estar fora dele pelos dois lados. A família de multiplicadores era o
fallback e é mais larga que o caminho que a substituía; usar as duas não introduz nenhum número
que não estivesse já congelado. O CSV e o JSON registram a **procedência** de cada cenário.

Se o CSV não estiver disponível, rodar só com os multiplicadores é um caminho **degradado** e
exige `--permitir-fallback` explícito. Sem a flag o script para, em vez de degradar com um aviso
em stderr que ninguém lê.

**O script nunca procura "o dp que faz passar de 80%".** Há um teste automatizado
(`testes_instrumentacao.py`) que verifica, no bytecode, que a função de seleção de dispersão
não referencia nada relacionado a poder.

### O teste simulado é o teste real

Cada réplica reproduz o teste primário pré-declarado, não uma aproximação analítica:

- AUC por participante como unidade, n = 36;
- **Wilcoxon bilateral** contra 0,5, `zero_method="wilcox"` — idêntico a
  `teste_calibrado/teste_auc_por_sujeito.py::teste_uma_amostra`, verificado por teste;
- α = 0,05.

E o poder sai sob **dois critérios**, porque a regra de decisão de §6.1 é **conjuntiva**:

| Campo | Significado |
|---|---|
| `poder_wilcoxon` | apenas p < 0,05 |
| `poder_regra_suporte` | as três condições de SUPORTE juntas: AUC ≥ 0,60 **e** p < 0,05 **e** ≥25/36 acima de 0,5 |

O segundo é o operativo. Relatar só o primeiro seria otimista de um modo que o protocolo
não autoriza — e o caso `AUC=0,58, p=0,01`, levantado na revisão da PR #2, é exatamente o
que separa os dois.

### A decisão é ancorada num efeito declarado, não no melhor caso

Todo campo de decisão é avaliado **em `AUC_ANCORA_PODER`** — o menor efeito de interesse de §6.4,
que é o efeito que §10.3 nomeia no portão. Não "em algum efeito da grade", não no melhor caso.
Como o poder cresce monotonicamente com o efeito, avaliar na âncora é a leitura mais exigente
compatível com o texto do protocolo, e a monotonia é **verificada em tempo de execução**
(`monotonia_do_poder_ok`) em vez de assumida.

| Campo | Significado |
|---|---|
| `reference_power_pass` | 80% satisfeito **na âncora**, no cenário de referência (dp = 0,2346), sob a regra conjuntiva de §6.1 |
| `robust_power_pass` | o mesmo, em **toda** a faixa varrida |
| `poder_na_ancora` | o poder na âncora, sob os dois critérios, por dispersão |
| `poder_no_limiar_de_suporte` | idem em AUC = 0,60 |
| `mde_por_dispersao` | o menor efeito da grade que atinge 80%. **É a saída informativa**, e sobrevive a qualquer resolução de F2 |

**Cuidado de leitura em `poder_no_limiar_de_suporte`:** como a regra de suporte compara a AUC
**amostral** contra 0,60, o poder em AUC verdadeira = 0,60 é ≤ 50% por construção — a média
amostral fica acima do limiar em metade das réplicas. Não existe leitura desse campo que seja
simultaneamente 80% e ancorada em 0,60.

**Se `reference_power_pass` passar e `robust_power_pass` não, isso não é falha da simulação.** É
um resultado metodológico: a adequação de n=36 depende de uma suposição ainda desconhecida sobre
a dispersão da métrica nova. Qualquer relatório deve então dizer *"tem poder suficiente **se** a
métrica nova tiver dispersão próxima à da LZc residualizada"* — nunca *"o estudo tem 80% de
poder"*.

**Se nenhum dos dois passar**, a leitura pré-declarada também existe e o script a imprime: o
portão de §10.3 não é satisfeito neste n, e o que se segue é decisão de **desenho** (F2), não de
simulação. O que não pode acontecer é essa saída ser lida como "a irreversibilidade não
funciona" — ela não é sobre a métrica, é sobre o n.

### O gerador entrega os momentos que a linha declara (F3)

Cada réplica sai de uma **Beta parametrizada em (média, dp)**: a AUC por participante vive em
[0,1], e a Beta vive nesse suporte por construção — sem truncagem, sem reamostragem, sem clip. O
mapa (média, dp) → (a, b) é fechado, então os dois momentos são acertados exatamente.

Três coisas que a saída passa a registrar, porque momentos não determinam a distribuição:

- `media_realizada` e `dp_realizado` em **cada linha**, com a checagem de fidelidade em múltiplos
  do erro-padrão (não uma tolerância fixa, que seria frouxa a `n_sim=2000` e apertada num smoke
  test);
- `alvo_viavel`: nenhuma distribuição em [0,1] com média *m* tem dp ≥ √(*m*(1−*m*)). Células que
  violam isso saem **sem poder**, não com poder aproximado;
- `forma_unimodal`: com *a* e *b* > 1 a Beta é unimodal; abaixo disso vira U ou J. Na região que
  decide — a âncora (0,55; 0,2346) dá *a*=1,92 e *b*=1,57 — ela é unimodal. Os cantos em forma de
  U são cantos onde nenhuma família seria gaussiana, porque o dp pedido está perto do supremo
  teórico do suporte.

### Congelado no script

- **`n_sim = 2000`**, conforme §10.3. Valores menores são aceitos apenas para smoke test e
  a rodada sai marcada como tal, sem poder fechar a etapa 0.6.
- **Semente explícita** (`--seed`, default `20260813`), registrada na saída.
- **Verificação multi-semente:** 5 sementes independentes na célula de referência. Se a
  faixa entre elas cruzar 80%, o campo `mc_ruido_cruza_alvo` fica `True` e o relatório
  adverte que `n_sim` precisa subir antes de a conclusão ser usada.

**Saídas:** `poder_vnext01.csv` (grade dispersão × efeito), `poder_vnext01_meta.json`
(vereditos, critério, excluídas, ruído de MC, versões).

---

## O que continua bloqueado depois disto

Mesmo com estes dois scripts mergeados e executados, **nenhum braço confirmatório roda**
até que:

- a etapa 0.6 tenha produzido a curva de poder (AA8), e
- os critérios de §6.1 tenham sido ajustados **antes** da Fase 1, se a simulação mostrar que
  precisam — com registro na §16 do protocolo.

A regra de congelamento do protocolo continua valendo: qualquer emenda posterior à
visualização de resultados rebaixa a análise afetada de confirmatória a exploratória.
