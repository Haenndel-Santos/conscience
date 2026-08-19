# Revisão pré-merge da `fase0-instrumentacao`, sondagem de Z12 e verificação das seis referências

> **Estatuto.** Documento de revisão escrito por agente em 2026-08-17, contra
> `fase0-instrumentacao` em `fd07b60`, ainda sem merge. **Nada da instrumentação congelada foi
> alterado**, e nenhuma das etapas 0.4 ou 0.6 foi executada: os números da §1 vêm de uma
> reexecução da *lógica de decisão* de `poder_vnext01.py` em ambiente separado, com `n_sim=400`,
> para revisão de código, e não fecham nem substituem a etapa 0.6. A §2 é uma **sondagem**
> exploratória de 6 dos 39 registros, sem veredito de critério — a etapa 0.4 continua sendo do
> autor. A §3 é verificação bibliográfica direta contra PubMed, PMC e a página do periódico.
>
> As decisões que este documento recomenda são todas do autor. Nenhuma foi tomada aqui.

---

## 1. Revisão da instrumentação congelada

### F1 — `reference_power_pass` e `robust_power_pass` passam por construção 🔴 bloqueante

`poder_vnext01.py:327-333`:

```python
def passa(sub: pd.DataFrame) -> bool:
    alvo = sub[sub["auc_media_verdadeira"] >= AUC_SUPORTE]
    return bool(not alvo.empty and (alvo["poder_regra_suporte"] >= PODER_ALVO).any())
```

O `.any()` sobre todos os efeitos ≥ 0,60 significa que **o maior efeito da grade decide**. Como
`AUC_GRADE` termina em 0,70 e 0,75, onde o poder é altíssimo, os dois campos de decisão saem `True`
qualquer que seja a dispersão. Medido, com o próprio código, em `dp = 0,2346`:

| AUC verdadeira | `poder_wilcoxon` | `poder_regra_suporte` |
|---|---|---|
| 0,50 | 0,045 | 0,003 |
| **0,55** ← menor efeito de interesse (§6.4) | **0,195** | **0,035** |
| 0,58 | 0,443 | 0,138 |
| **0,60** ← limiar de suporte (§6.1) | 0,627 | **0,230** |
| 0,62 | 0,785 | 0,417 |
| 0,65 | 0,920 | 0,642 |
| 0,70 | 0,993 | 0,930 |
| 0,75 | 1,000 | 0,990 |

`passa()` como escrito → `True`. `passa()` com `.all()` (equivalente a avaliar em AUC = 0,60,
porque o poder é monótono) → `False`.

O portão do protocolo não é nenhum dos dois. §10.3: *"nenhum braço confirmatório é executado sem
que a análise de poder mostre que ele detecta o **menor efeito de interesse (§6.4)** com pelo menos
80% de poder"*, e §6.4 fixa esse menor efeito em **AUC = 0,55**. O poder ali é **0,035** na regra
conjuntiva e **0,195** no Wilcoxon isolado. O relatório da etapa 0.6, rodado como está, imprimiria
`reference_power_pass = True` e `robust_power_pass = True` para um desenho que falha o portão do
próprio protocolo por uma ordem de grandeza.

Este é exatamente o modo de falha contra o qual o protocolo se define ("um protocolo que não pode
falhar não vale nada"), e ele está no campo que carrega a decisão.

Consistência externa que dá confiança nos números: o deslocamento de AUC de 0,05 com dp = 0,2346 é
dz = 0,213, e a tabela algébrica de §10.2 pede n ≈ 197 para 80% de poder nesse dz. Em n = 36 a
fórmula prevê poder ≈ 0,19 — a simulação dá 0,195. A álgebra de §10.2 e a simulação concordam.

**Correção mínima:** avaliar `passa()` num efeito **declarado**, não no melhor da grade. E como a
regra de suporte compara a *AUC amostral* contra 0,60, o poder em AUC verdadeira = 0,60 é ≤ 50% por
construção (a média amostral fica acima do limiar em metade das réplicas): não existe leitura de
`passa()` que seja simultaneamente 80% e ancorada em 0,60. O objeto informativo é o que o script já
calcula e não usa na decisão — `mde_por_dispersao`.

### F2 — o portão de §10.3 não pode ser satisfeito em n = 36, e isso é decisão de desenho 🔴 bloqueante

Não é defeito de código; é uma tensão interna do protocolo que a instrumentação torna visível:

- §6.4 fixa o menor efeito de interesse em AUC = 0,55;
- §10.2 deriva o limiar de suporte 0,60 de dz = 0,4669, que é o dz que **já** dá 80% de poder em
  n = 36 — isto é, 0,60 é aproximadamente o **efeito mínimo detectável**, não o menor efeito de
  interesse;
- §10.3 exige 80% de poder no menor efeito de interesse.

Os três não podem valer juntos: se 0,60 é o MDE, 0,55 está abaixo dele por definição. Pelas medidas
acima, 80% de poder na regra conjuntiva exige AUC verdadeira ≈ **0,70** (poder 0,930), muito acima
de 0,55 e de 0,60.

Isto precisa ser resolvido **antes** de rodar 0.6, não depois, e §15 já prevê o lugar: *"Se o limiar
de §6.1 precisar de ajuste, ajustar agora e registrar na §16."* As saídas honestas são reformular o
portão (por exemplo, 80% de poder no limiar de suporte com o critério de Wilcoxon, e MDE reportado
para a regra conjuntiva), rebaixar o braço a estimativa com IC pré-declarado em vez de teste, ou
aceitar que o Braço A é subpotente e dizer isso no registro. Nenhuma delas é minha escolha. O que
não pode acontecer é a ordem inversa: rodar, ver `True`, e não notar.

### F3 — `simula_aucs` não realiza a média nem a dispersão que a linha diz simular 🟠 alto

`poder_vnext01.py:182-198` trunca por reamostragem e depois clipa. A truncagem em [0,1] é a decisão
certa, mas a reamostragem é assimétrica quando a média está fora do centro, e o resultado é que a
grade fica **rotulada com parâmetros que não são os simulados**:

| nominal (média, dp) | realizado (média, dp) | erro no dp |
|---|---|---|
| (0,60; 0,2346) | (0,5824; 0,2085) | −11,1% |
| (0,75; 0,2346) | (0,6854; 0,1901) | −19,0% |
| (0,75; 0,2845) | (0,6540; 0,2171) | −23,7% |
| (0,50; 0,2845) | (0,4987; 0,2321) | −18,4% |

Dois vieses de sinal oposto e magnitude desconhecida se somam: a média realizada mais baixa **reduz**
o poder da regra de suporte (que compara a média amostral contra 0,60), e o dp encolhido **aumenta**
o poder. A célula de referência não escapa: a linha `auc_media_verdadeira = 0,60` simula média
verdadeira ≈ 0,582.

E a distorção é máxima exatamente nos cantos altos da grade — os que decidem `passa()` sob o `.any()`
de F1. Os dois defeitos se reforçam.

**Correção mínima:** amostrar de uma normal truncada com parâmetros resolvidos para que média e dp
*realizados* sejam os alvos, ou — mais simples e suficiente — manter a reamostragem e **reportar
média e dp realizados** em cada linha do CSV, para que a grade não afirme o que não faz.

### F4 — a faixa "empírica" de dispersão é degenerada; o fallback é mais informativo 🟡 médio

Aplicada ao CSV congelado, a regra de regime AUC ∈ [0,35; 0,65] deixa passar **14 linhas**, todas
`resid_1f_*`, com 13 dp distintos em **[0,2248; 0,2845]** — uma amplitude de 27%, agrupada em dois
blocos (≈0,225–0,235, a família LZc, contada 6 vezes entre `sono` e `sono-multi`; ≈0,267–0,285, a
família PE/sync/MI/índice). As 7 excluídas são todas `bruta`, e a exclusão funciona como declarado.

Consequência: `robust_power_pass` é 13 quase-repetições do cenário de referência, não uma faixa de
robustez. Ele não desce abaixo de 0,225 nem sobe acima de 0,285, e a dispersão da métrica nova é
desconhecida e pode estar fora dos dois lados. O **fallback pré-declarado** (0,1173–0,3519) é
mais largo e mais informativo que o caminho "empírico" que o substitui.

Custo não é argumento contra alargar: medi 0,73 ms por réplica, o que dá ~3 min de parede para a
varredura inteira com `n_sim=2000`. Alargar a grade é grátis.

Nota operacional relacionada: quando o CSV não é encontrado o script cai no fallback com um aviso
**só em stderr**, e a distinção sobrevive apenas no campo `origem_faixa_dispersao` do JSON. Vale
recusar-se a rodar sem `--permitir-fallback` explícito, para que o caminho degradado nunca seja
silencioso.

### F5 — o denominador de §3.2 não é imposto, e o veredito pode inverter 🟡 médio

`cobertura_hipnogramas.py:245-247` conta sobre **todos** os pares PSG/hipnograma encontrados no
cache — 39 no `.cache_sleepedf/` — e compara contra `MIN_PARTICIPANTES = 30`. Mas §3.2 diz "30 dos
**36** participantes", e os 36 são os que sobreviveram às exclusões (3 sem N3, 2 índices ausentes).
Os 3 sem N3 não são identificados nem removidos.

Cenário concreto em que o veredito inverte: se os 3 sem N3 satisfizerem o mínimo de vigília e
exatamente 30 dos 39 satisfizerem, o script imprime `SATISFEITO` enquanto apenas 27 dos 36
analisados satisfazem. O critério real falhou. Pela §2 abaixo, a margem observada é folgadíssima e
isso provavelmente não morde neste dataset — mas o script não sabe disso, e é ele que carrega o
veredito.

**Correção mínima:** receber a lista dos 36 (ou derivá-la pela mesma regra de exclusão) e computar o
critério sobre ela, reportando os demais registros à parte.

### F6 — `hipnograma_cobre_registro` é verdadeiro por construção 🟡 médio

`cobertura_hipnogramas.py:177-178` testa `duracao_anotada_total_s >= 0.95 * dur_total_s`, e
`duracao_anotada_total_s` **inclui** as anotações `Sleep stage ?`. Medi: a anotação `?` final desses
hipnogramas estende o total anotado a 24,00 h contra 21,8–23,4 h de sinal. O indicador seria
verdadeiro mesmo num hipnograma que não pontuasse nada. O script já calcula
`duracao_pontuada_total_s`, que é a quantidade certa — só não é a usada no booleano.

### F7 — a discrepância espectral do IAAFT não é medida em lugar nenhum 🟠 alto

Era a pergunta específica sobre `testes_instrumentacao.py`, e a resposta é **não**. O arquivo não
contém nenhuma referência a IAAFT, surrogate ou espectro: seus sete testes cobrem Wilcoxon, regra
conjuntiva, suporte do gerador, monotonia do poder em efeito e em dispersão, a regra de regime e a
guarda de bytecode. E não é omissão local — `grep -ril iaaft` no repositório inteiro retorna
**três arquivos, todos markdown** (`PROTOCOLO_VNext_01.md`, `CHECKLIST_pendencias.md`,
`nota_estado_da_arte_1f.md`). Não existe uma linha de código de IAAFT no projeto.

A ameaça está corretamente pré-registrada em três documentos, e em todos eles a obrigação é atribuída
ao *smoke test* ("o smoke test passa a ter de reportá-la", "vai passar a ter número quando o smoke
test começar a quantificar o erro espectral"). Esse smoke test é da Fase 1 e ainda não foi escrito.
Não há inconsistência entre o commit e o código; há uma obrigação declarada sem implementação, e
como ela entra direto no zero da métrica (a normalização é contra o ensemble), ela precisa nascer
junto do gerador, com tolerância declarada antes de ver o número — não depois.

### F8 — o que os testes não cobrem é exatamente onde estão F1 e F3 🟡 médio

- `passa()` é função aninhada em `main()`, portanto inalcançável por teste. A lógica de decisão do
  script é a única parte sem cobertura, e é onde está o defeito bloqueante.
- `teste_gerador_respeita_suporte` passa trivialmente, porque o `np.clip` final garante o interior
  por construção. Nenhum teste compara média ou dp **realizados** contra os nominais — que é o que
  teria pegado F3. Os casos escolhidos no teste, (0,95; 0,30) e (0,05; 0,30), são justamente os de
  distorção mais violenta, e passam.

### F9 — miudezas 🟢 baixo

- `--permitir-download` é aceito e nunca usado; o script não baixa nada em nenhum caminho.
- §10.3 chama a análise de poder de "Etapa 0.4"; §15 a numera 0.5 (escrever) e 0.6 (rodar). 0.4 é
  rodar a cobertura. Confunde o portão bloqueante com a checagem descritiva.
- `stats.__name__ and __import__("scipy").__version__` (linha 384) funciona, mas o `and` não faz nada.

### O que está correto, e não é pouco

Vale registrar, porque a lista acima é longa: o Wilcoxon é cópia fiel e há teste que o compara com o
original em 20 amostras; a guarda de bytecode contra "procurar o dp que faz passar" é bem construída
e a explicação do falso positivo anterior está no lugar certo; a regra conjuntiva de §6.1 está
implementada como conjuntiva e testada com o caso AUC = 0,58 / p = 0,01 que a revisão da PR #2
levantou; a exclusão pela regra de regime é auditável e nominal, e funciona como declarado; o corte
de `cobertura_hipnogramas.py` reproduz `analise_sono_v2.py` fielmente, inclusive o `min(crop_end,
raw.times[-1])` e as âncoras em `[1]` e `[-2]`; a ressalva de que a contagem é limite superior antes
de rejeição de artefato está no relatório e no nome do campo; `mde_por_dispersao` é a saída
metodologicamente correta e já está sendo computada; e a verificação multi-semente com
`mc_ruido_cruza_alvo` é a guarda certa contra ruído de Monte Carlo no limiar.

---

## 2. A pergunta das ~20 h: os hipnogramas cobrem o registro inteiro

**Sondagem** de 6 dos 39 registros do `.cache_sleepedf/physionet-sleep-data/`, lendo apenas anotação
e a duração do PSG. Nenhuma métrica de EEG calculada, nenhum sinal carregado.

| registro | PSG (h) | anotado (h) | **pontuado** (h) | 1ª anot. pontuada | corte atual (h) | % do registro usado | épocas W **fora** | épocas W dentro |
|---|---|---|---|---|---|---|---|---|
| SC4001E0 | 22,08 | 24,00 | **22,08** | W, 8,51 h | 6,97 | 31,5% | **1814** | 183 |
| SC4071E0 | 23,42 | 24,00 | **23,42** | W, 7,78 h | 8,07 | 34,5% | **1841** | 117 |
| SC4151E0 | 21,83 | 24,00 | **21,83** | W, 7,45 h | 7,87 | 36,0% | **1676** | 160 |
| SC4231E0 | 22,88 | 24,00 | **22,88** | W, 8,81 h | 7,54 | 33,0% | **1841** | 125 |
| SC4301E0 | 22,05 | 24,00 | **22,05** | W, 7,82 h | 7,67 | 34,8% | **1725** | 201 |
| SC4401E0 | 21,92 | 24,00 | **21,92** | W, 7,61 h | 8,82 | 40,3% | **1571** | 405 |

Três coisas, e nenhuma é marginal:

1. **A duração pontuada é igual à duração do PSG, em todos os seis.** Os hipnogramas não cobrem
   "parte" das ~22 h: pontuam o registro inteiro com estágios reais. As 24,00 h de "anotado" são a
   anotação `Sleep stage ?` final estendida além do fim do sinal — o que é também a demonstração
   empírica de F6.
2. **A primeira anotação pontuada é um bloco de vigília de 7,5 a 8,8 h**, em todos os seis. A leitura
   de código registrada em §3.2 — que pular `sleep_annots[0]` só faz sentido se ele for um bloco longo
   de vigília — deixa de ser pista e passa a ser verificada.
3. **Existem 1571–1841 épocas de W fora da janela de corte**, isto é 13–15 h de vigília anotada por
   registro, contra 117–405 épocas dentro. O critério de §3.2 pede ≥ 30 épocas fora em ≥ 30 dos 36
   participantes: a margem é de **~50× o limiar**, antes de rejeição de artefato.

Verificação de consistência: as épocas W *dentro* do corte (117–405, mediana ≈ 160) reproduzem a
escala da linha de base do projeto (8.923 épocas W / 36 ≈ 248 por participante), o que confirma que a
reprodução do corte está certa.

Implicações, todas para decisão do autor:

- O critério de §3.2 vai passar com folga enorme, e o braço secundário **W(ativo) vs N3** fica
  autorizado — sem trocar de dataset, sobre dado já em disco. Isso não é conclusão da etapa 0.4: é
  previsão que a etapa 0.4 vai confirmar ou não sobre os 36 registros com rejeição de artefato.
- O corte atual usa **31–40%** do registro. As outras ~14 h existem, estão pontuadas, e são vigília
  diurna ativa — a limitação que inverteu a comparação REM-vs-W no proxy de EMG (Z5) e que enfraquece
  o índice de desacoplamento.
- Isso **não** enfraquece a recusa de §3.2 em fazer o contraste primário depender da checagem. Os
  confundidores alinhados ao contraste (hora do dia, deriva de impedância, EMG, movimento) continuam
  todos de pé, e §14.3 continua sendo a condição. A vigília ativa recuperada troca um problema por
  outro; a diferença é que agora existem os dois braços, e §3.2 já declarou que divergência entre
  eles é achado e não menu.

---

## 3. As seis referências, verificadas diretamente

Fonte: PubMed / PMC (metadados e texto integral) e a página do periódico. Nenhuma das seis consta de
`capitulos/17_referencias.md` — as duas ocorrências de "Maschke" e "Berger" naquele arquivo são
Newman et al. 2026 (Maschke como coautora) e Peter L. Berger 1966 (sociologia).

| Referência | Identificadores conferidos | Veredito |
|---|---|---|
| **Maschke, Belloli, Manasova, Sitt & Blain-Moraes (2025)**, *Cereb Cortex* 35(9):bhaf254 | DOI 10.1093/cercor/bhaf254, PMID 40972153, PMC12448740 | ✅ **Confere, agora contra o texto integral.** Autores, ordem, periódico, volume/número/artigo e título ("The role of etiology in the identification of clinical markers of consciousness: comparing EEG alpha power, complexity, and spectral exponent") conferem. Os dois números centrais estão no corpo, literalmente: *r*(197) = 0,86, P < 0,001 entre expoente espectral 1–40 Hz e LZc normalizada por shuffle; *r*(197) = 0,24, P < 0,001 sob surrogates de fase. Amostra final 225 de 303 avaliados. **Uma precisão nova:** os canais retidos são **185,09 ± 8,77** em média (máximo de 195 disponíveis), não "no máximo 195" — o registro de AA9 pode ficar mais preciso. |
| **Westfall & Yarkoni (2016)**, *PLoS ONE* 11(3):e0152719 | DOI 10.1371/journal.pone.0152719, PMID 27031707 | ✅ **Confere.** Título "Statistically Controlling for Confounding Constructs Is Harder than You Think". O resumo diz literalmente que as taxas de erro tipo I são mais altas — "in some cases approaching 100%" — quando a amostra é grande e a confiabilidade é moderada. A leitura do projeto (o viés estava a favor de achar validade incremental espúria, e ainda assim não houve efeito) está correta. |
| **Berger, Schneider, Kochs & Jordan (2017)**, *Entropy* 19(12):692 | DOI 10.3390/e19120692 (resolve para mdpi.com/1099-4300/19/12/692) | ✅ **Confere**, com ressalva de acesso: o MDPI devolveu 403 à leitura direta, e a confirmação veio pela resolução do DOI mais busca. Autores, ordem, volume, número e artigo conferem. Título: "Permutation entropy: too complex a measure for EEG time series?" — o título é ele mesmo o argumento. A afirmação sobre padrões ordinais de três amostras aproximarem o centróide do espectro de potência ponderado confere. **Duas coisas que valem entrar no texto:** (a) o resultado é sobre ordem 3, que é a `pe_epoch` do projeto (`order=3, delay=1`), e **não** transfere direto para a métrica primária nova, que usa m = 4; (b) mais importante, ele é argumento *a favor* do desenho novo e o protocolo não o usa — o espectro de potência é invariante à reversão temporal, então uma estatística puramente espectral tem irreversibilidade identicamente nula, e a assimetria ordinal acessa estrutura que **não é determinada** por estatísticas espectrais de segunda ordem — a reversão temporal preserva o espectro de potência, mas pode alterar dependências temporais de ordem superior. (Deliberadamente **não** dizemos "ortogonal": ortogonalidade tem sentido matemático mais forte — correlação zero, projeções ortogonais — que não foi demonstrado e que este argumento não estabelece.) Isso reforça §2.3 melhor do que o texto atual. |
| **Widmann et al. (2024)**, *Br J Anaesth* 134(2):392–401 | DOI 10.1016/j.bja.2024.09.027, PMID 39609175 | ✅ **Confere, com uma correção de ano.** n = 62 acordados e n = 125 sob anestesia geral (sevoflurano, desflurano, propofol), expoente espectral AUC = 0,98 (0,94–1,00), ApEn 0,96 (0,93–0,98), PeEn 0,94 (0,90–0,97) — os três números conferem literalmente. **O volume 134(2) é de fevereiro de 2025**; 2024-11-28 é a publicação online antecipada. Citar como "Widmann et al. (2024)" com paginação de 2025 é inconsistente: escolher um dos dois. Autores: Widmann, Ostertag, Zinn, Pilge, García, Kratzer, Schneider, Kreuzer. |
| **Halder et al. (2026)**, *Sci Rep* | DOI 10.1038/s41598-026-50911-6, PMID 42069748, 2026-05-02 | ✅ **Confere.** Título "An experimental study of the effect of neuromuscular blockade on EEG-based measures of awareness"; autores Halder, Juel, Pope, Hardy, Willoughby, Storm. O resumo diz literalmente: erros de 7% dos segmentos acordado-paralisado classificados como não-conscientes usando potência alfa, **a 100% usando LZc**. **Duas precisões a acrescentar:** n = **6** voluntários saudáveis (EEG de alta densidade, três condições) — a nota não diz o n, e ele é pequeno; e a afirmação de que "inclinação e LZc falham juntas" é mais forte do que o resumo autoriza: o resumo diz que *a maioria* das medidas falha, com a inclinação espectral entre as investigadas, mas o comportamento conjunto das duas exige o corpo do artigo. Marcar como inferência até a leitura integral. |
| **Helfrich et al. (2026)**, *PNAS* | DOI 10.1073/pnas.2514098123, PMID 42114012, PNAS **123(21):e2514098123**, 2026-05-11 | ✅ **Confere.** Título "Spectral mapping reveals a resemblance of the anesthetic brain state to both sleep and coma". O resumo diz literalmente que a redução de atividade aperiódica se sobrepõe parcialmente ao sono REM e pode refletir excitabilidade cortical diminuída. **Duas precisões:** a nota omite volume, número e eLocator, que existem; e o primeiro autor é **Janna D. Helfrich** enquanto o último é Randolph F. Helfrich — "Helfrich et al." sem inicial é ambíguo num artigo com dois Helfrich. A cláusula "enfraquecendo o expoente como marcador puro de consciência" é inferência do projeto, não afirmação dos autores; a inferência é razoável e deve ser marcada como tal. |

Nenhuma autoria errada, nenhum DOI quebrado, nenhum número inventado nas seis. O saldo da verificação
são precisões (n = 6 em Halder, 185 canais em Maschke, ano em Widmann, volume e inicial em Helfrich),
uma inferência a marcar como inferência (Halder, comportamento conjunto), e um argumento novo a favor
do desenho que a verificação de Berger revelou e que o protocolo ainda não usa.

---

## 4. Estado das correções

Aplicadas em 2026-08-17, sobre `fase0-instrumentacao`, **antes do merge e antes de qualquer
execução das etapas 0.4 ou 0.6**. Registradas na §16 do protocolo.

| | Estado | O que ficou no lugar |
|---|---|---|
| **F1** | ✅ aplicada | `passa()` (aninhada, intestável) virou `avalia_portao()` no nível do módulo, ancorada em `AUC_ANCORA_PODER = 0,55`. A monotonia do poder é verificada em execução, não assumida. A célula da checagem multi-semente passou de 0,60 para a âncora. |
| **F2** | ⚠️ **aberta, do autor** | Registrada como caixa de aviso na §10.3 e como AA8b no checklist. O script mede a tensão e reporta em campos separados; `AUC_ANCORA_PODER` carrega o valor que §10.3 declara literalmente, e mudá-la é emenda de §16. |
| **F3** | ✅ aplicada | Beta parametrizada em (média, dp). Momentos exatos em forma fechada, viabilidade contra o limite universal `dp² < m(1−m)`, `media_realizada`/`dp_realizado` em cada linha, e checagem de fidelidade em múltiplos do erro-padrão em vez de tolerância fixa. Células inviáveis saem **sem** poder, não com poder aproximado. |
| **F4** | ✅ aplicada | Grade = união das duas famílias já congeladas: 17 cenários, 0,1173–0,3519 (era 13 em 0,2248–0,2845). Procedência de cada cenário no CSV e no JSON. O caminho degradado exige `--permitir-fallback` e sai com código 2 sem ele. |
| **F5** | ✅ aplicada | Coorte derivada por N3 anotado dentro do corte. **Verificado: a regra devolve exatamente 36**, excluindo `SC4321E0`, `SC4331F0` e `SC4341F0` — reproduz a exclusão do projeto. Sem 36, nenhum veredito e código de saída 3. `--coorte` aceita lista explícita. |
| **F6** | ✅ aplicada | Booleano passou para a duração **pontuada**; as duas frações saem no CSV. |
| **F7** | ⚠️ **aberta, Fase 1** | Não corrigível aqui: não existe gerador de IAAFT para instrumentar. Registrada como AA8c. |
| **F8** | ✅ aplicada | Três testes novos, cada um fixando a propriedade que o defeito violava: portão não passa por efeito grande, momentos realizados == alvos em 7 células, união das faixas. Suíte inteira passa. |
| **F9** | ✅ aplicada | `--permitir-download` removido; `stats.__name__ and` removido. A numeração de etapa em §10.3 fica para o autor, porque mexer nela é editar o texto do portão. |

Uma correção que a própria aplicação exigiu, e que não estava na lista: o teste de suporte do
gerador passou a aceitar o intervalo **fechado** [0,1]. AUC = 1,0 e AUC = 0,0 são valores legítimos
de uma AUC — separação perfeita —, e a versão anterior os proibia por efeito colateral do
`np.clip(x, 1e-9, 1-1e-9)` que existia para consertar a truncagem, não por uma razão sobre a AUC.

### O que continua não tendo sido feito

- **As etapas 0.4 e 0.6 não foram executadas para o registro.** Os scripts foram rodados como
  *smoke test* de código, com saídas descartadas fora do repositório: `poder_vnext01.py` com
  `n_sim` de 50 a 400 (auto-marcado SMOKE TEST, incapaz de fechar 0.6) e `cobertura_hipnogramas.py`
  sobre o cache, para verificar que a coorte de F5 sai com 36. O artefato de registro é o que o
  autor rodar.
- **Nenhuma análise exploratória proibida foi tocada:** nada de τ ∈ {25, 50, 75}, nada de 30–45 Hz,
  nenhuma métrica de irreversibilidade. Nenhum sinal de EEG foi carregado em nenhum momento —
  apenas anotações de hipnograma e a duração declarada no cabeçalho dos PSG.
- **O que o smoke test de cobertura mediu, sobre os 39 registros**, e que reforça a §2 acima: de
  **923 a 2052 épocas** de W fora do corte (mediana 1669), os 39 hipnogramas pontuam ≥96% do sinal
  (mediana 100%), e o corte atual usa 38,5% do registro. Dentro da coorte de 36, **36 satisfazem**
  o mínimo de §3.2 antes de rejeição de artefato. Isso não é a etapa 0.4; é a previsão do que ela
  vai encontrar.

---

## 5. Adendo de 2026-08-17 (segunda passada): F2 resolvida, F8 nova

Esta seção foi escrita **depois** das §§1–4, na mesma data, e **antes** de qualquer execução das
etapas 0.4 e 0.6. Nenhum desfecho do VNext-01 foi calculado. As duas decisões abaixo estão
registradas na §16 do protocolo e implementadas em `poder_vnext01.py`.

### 5.1 F2 — os limiares estavam certos; a grandeza que os lia estava errada

A §1 deixou F2 aberta, atribuída ao autor, com três saídas possíveis. A decisão tomada foi
**nenhuma das três na forma em que estavam enunciadas**, porque as três pressupunham que algum
limiar teria de ceder. Nenhum cedeu:

| Número | Papel | Decisão |
|---|---|---|
| AUC = 0,55 | Menor efeito **cientificamente** relevante (SESOI, §6.4) | **Preservado** |
| AUC = 0,60 | Limiar de **classificação** como SUPORTE (§6.1) | **Preservado** |

Subir o SESOI para 0,60 porque 0,55 exige mais participantes seria adaptar o efeito
cientificamente relevante ao tamanho da amostra disponível — a inversão exata que o protocolo
existe para impedir, e que a justificativa original de §6.4 (o projeto já tratava AUC 0,550 e
0,554 como indistinguíveis do acaso) não autoriza revogar por conveniência aritmética.

O erro estava em pedir que **uma única grandeza chamada "poder"** fizesse o trabalho de três
objetos distintos. Eles passam a ter nomes próprios (§10.3.1):

| Objeto | Definição | Estatuto |
|---|---|---|
| **Portão A** | P(Wilcoxon rejeita \| AUC = 0,55) | Poder amostral. **É o portão.** |
| **Característica operacional** | P(as três condições conjuntas de §6.1) | Classificação. **Não é poder.** |
| **MDE** | Menor efeito da grade com 80% | Independe de escolher âncora |

A segunda linha é a que mais enganava: como a regra compara a AUC **amostral** contra 0,60, essa
probabilidade é ≤ 50% por construção quando a AUC verdadeira é exatamente 0,60, e **não existe n**
que a leve a 80% ancorada em 0,55. Chamá-la de poder tornava o portão insatisfazível por álgebra,
não por falta de amostra.

Implementado em `CRITERIO_PORTAO_A`, com teste (`teste_portao_ancora_no_efeito_declarado`) que
quebra se alguém trocar o critério de volta.

### 5.2 F8 — o ramo de EQUIVALÊNCIA era inacessível, e isso não estava em lugar nenhum

**O defeito.** A §6.1 promete um ramo de EQUIVALÊNCIA — IC 95% da AUC média inteiramente contido
em [0,45; 0,55] — e conclui com "Resultado negativo é dado". Nunca se verificou se esse ramo era
alcançável. Não era.

Simulado sob o caso **mais favorável possível** — AUC verdadeira exatamente 0,500, porque qualquer
deslocamento da média só pode reduzir a probabilidade —, com o gerador Beta de F3:

| dp | P(EQUIVALÊNCIA \| AUC = 0,500), n = 36, IC 95% |
|---|---|
| 0,1173 | 0,395 |
| 0,1760 | 0,004 |
| **0,2346 (referência)** | **≈ 0,000** |
| 0,2933 | ≈ 0,000 |
| 0,3519 | ≈ 0,000 |

A aritmética por trás: com dp = 0,2346 e n = 36, o erro-padrão é ≈ 0,0391 e a semi-amplitude do
IC 95% é ≈ 0,0766 — contra margens de **±0,05**. Mesmo sob o nulo exato, o IC típico é
≈ [0,423; 0,577], e não cabe.

**A consequência, que o protocolo não declarava.** Um efeito genuinamente nulo era classificado
como INCONCLUSIVO **por construção**, não por ambiguidade do dado. Isto é, o desenho tinha
capacidade de encontrar um efeito suficientemente grande e **nenhuma** capacidade de estabelecer
que um efeito é suficientemente pequeno — uma assimetria entre os ramos da árvore de decisão que
nem §6.1 nem §10 mencionavam. Como está, a promessa "resultado negativo é dado" não era realizável.

**A correção.** A regra passou a ser **TOST a α = 0,05 contra [0,45; 0,55]**, equivalente ao IC 90%
contido nas margens. Duas coisas sobre essa troca, ambas importantes:

- ela foi feita **por ser a formulação convencional de equivalência**, e não para salvar n = 36;
- ela **não** salva n = 36: leva o n necessário para 80% de ≈ 232 a ≈ 190, e nenhum dos dois é 36.

As margens [0,45; 0,55] **não** mudaram — são as mesmas de §6.4, e movê-las teria sido a versão
de F8 do erro que §5.1 recusou.

Implementado em `testa_equivalencia()` e `poder_equivalencia()`, com teste
(`teste_portao_b_equivalencia`) que fixa, entre outras coisas, que TOST a 0,05 usa o IC 90% e não
o 95% — o erro clássico de equivalência, que aqui mudaria o n necessário em ~40 participantes.

### 5.3 A conclusão conjunta: n = 36 não é amostra confirmatória

Os dois portões são independentes — medem sensibilidade e capacidade de nulo — e **nenhum dos dois
é satisfeito**, na dispersão de referência:

| Portão | n = 36 | n para 80% |
|---|---|---|
| A — detecção em AUC = 0,55 | 0,24 | ≈ 180 |
| B — equivalência em AUC = 0,50 (TOST/IC 90%) | ≈ 0,00 | ≈ 190 |
| B — mesma pergunta, formulação anterior por IC 95% | ≈ 0,00 | ≈ 232 |

A convergência é o achado. Três cálculos que não se apoiam um no outro — a álgebra de §10.2
(n ≈ 197), a simulação do Wilcoxon real (≈ 180) e a simulação da regra de equivalência (≈ 190) —
apontam para a mesma região. O tamanho amostral necessário deixa de ser produto de um cálculo
isolado e passa a ser uma propriedade robusta da pergunta.

**O que isso não é.** Não é resultado sobre a teoria, não é resultado sobre a irreversibilidade, e
não cancela a Fase 1. O Sleep-EDF com n = 36 permanece adequado para desenvolver e validar o
gerador IAAFT (a pendência AA8c/F7, que segue aberta), calibrar o estimador, estudar a escala
temporal de §5.5.1, verificar W(ativo) por §3.2, produzir um efeito **piloto**, e — o mais
relevante para todo este cálculo — obter a **primeira estimativa da dispersão por participante da
irreversibilidade**, que hoje é desconhecida e é o insumo que falta a cada linha das tabelas acima.

**O que muda** é o estatuto do Braço A: de confirmatório para piloto/instrumental. E a função da
etapa 0.6, que deixa de ser descobrir se n = 36 passa — a resposta já é conhecida e está registrada
aqui, antes de rodar — e passa a ser quantificar formalmente quanto falta, com a instrumentação
congelada, e documentá-lo.
