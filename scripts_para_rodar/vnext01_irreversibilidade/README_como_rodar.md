# Instrumentação da Fase 0 — VNext-01

> ⚠️ **Código preparado, ainda NÃO executado sobre os dados-alvo.**
> Nenhum dos dois scripts de análise foi rodado. Nenhum número deste diretório é resultado.
> Este diretório existe para ser **revisado e mergeado antes** da execução, de modo que o
> SHA que você roda seja exatamente o SHA que foi revisado.

Corresponde às etapas **0.3–0.6** da Fase 0 do [`PROTOCOLO_VNext_01.md`](../../PROTOCOLO_VNext_01.md).

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
python poder_vnext01.py --n-sim 2000 --out-dir saida_vnext01
```

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

**Fallback pré-declarado**, se o CSV sumir ou sobrarem menos de 3 cenários: multiplicadores
0,5× / 0,75× / 1,0× / 1,25× / 1,5× sobre 0,2346 — aproximadamente 0,1173 / 0,1760 / 0,2346 /
0,2933 / 0,3519.

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

### A decisão sai em dois campos, não em um PASS/FAIL

| Campo | Significado |
|---|---|
| `reference_power_pass` | o critério de 80% é satisfeito **no cenário de referência** (dp = 0,2346) |
| `robust_power_pass` | o critério é satisfeito em **toda** a faixa pré-declarada |

**Se apenas o primeiro passar, isso não é falha da simulação.** É um resultado metodológico:
a adequação de n=36 depende de uma suposição ainda desconhecida sobre a dispersão da métrica
nova. Qualquer relatório deve então dizer *"tem poder suficiente **se** a métrica nova tiver
dispersão próxima à da LZc residualizada"* — nunca *"o estudo tem 80% de poder"*.

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
