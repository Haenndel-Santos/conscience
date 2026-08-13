# O confundidor aperiódico: estado da arte e o que ele muda no projeto

> ⚠️ **Origem deste documento: levantamento por agentes de IA.**
> Três agentes de pesquisa independentes produziram o material desta nota em 2026-08-13,
> com busca em PubMed, bioRxiv e web. **As referências abaixo foram verificadas pelos
> agentes contra PubMed/DOI, mas NÃO foram reverificadas pelo autor**, ao contrário das
> referências 1–106 do manuscrito. Nenhuma deve entrar em `capitulos/17_referencias.md`
> antes de verificação direta. Ver a seção "Estatuto de verificação" ao final.
> Os números da seção 2 são exceção: foram calculados por mim sobre os dados do próprio
> projeto, e são reprodutíveis por `scripts_para_rodar/teste_calibrado/diagnostico_supressao.py`.

---

## Resumo executivo — o que muda

1. **O resultado negativo do sono tem replicação independente em escala.** Não é artefato
   dos 2 canais do Sleep-EDF. Isso **reforça** o Cap. 11 em vez de enfraquecê-lo.
2. **A assimetria sono-vs-anestesia tem explicação, e ela desfavorece a leitura otimista
   da anestesia:** é supressão estatística, não sobrevivência a um controle.
3. **O controle usado pelo projeto é o mínimo da área.** O padrão é normalização por
   surrogates de fase, que preserva o espectro inteiro. O projeto precisa reportar as duas
   versões para dialogar com a literatura.
4. **O próximo passo não é dataset novo — é controle mais forte sobre o dado em disco.**

---

## 1. Replicação independente do resultado negativo

**Maschke, Belloli, Manasova, Sitt & Blain-Moraes (2025), *Cerebral Cortex* 35(9):bhaf254,
DOI 10.1093/cercor/bhaf254** (PMID 40972153; preprint medRxiv 10.1101/2024.03.20.24304639).

225 pacientes com distúrbio de consciência, EEG de **256 canais**, 250 Hz. Fizeram o mesmo
teste do projeto, por duas vias:

> ✅ **Verificada contra a página do periódico (Oxford Academic) em 2026-08-13.** Autores,
> periódico, volume/número/artigo e os três números abaixo conferem literalmente. Duas
> precisões que a leitura por agente não trouxe: os 225 são a amostra **da análise final**
> (303 pacientes não responsivos foram avaliados inicialmente), e os 256 canais são a rede
> de aquisição (GSN-HydroCel-257) — após pré-processamento restam **no máximo 195**. O
> título completo é "The role of etiology in the identification of clinical markers of
> consciousness: comparing EEG alpha power, complexity, and spectral exponent". Nada disso
> altera o argumento: 195 canais analisados continuam sendo cerca de cem vezes os 2 do
> Sleep-EDF. Falta ainda a reverificação pelo autor, na convenção do projeto.

- expoente espectral (1–40 Hz) × LZc normalizada por shuffle: **r(197) = 0,86**;
- correlação parcial controlando o expoente: **o valor diagnóstico da LZc desaparece**;
- normalização por surrogates de fase aleatorizada: r cai para **0,24**, e "todos os efeitos
  diagnósticos desapareceram após corrigir a LZc por diferenças de fase".

Conclusão dos autores: LZc e expoente espectral são "largamente congruentes em vez de
complementares".

**Consequência para o projeto:** com 100× mais canais e n 6× maior, o mesmo colapso. A
leitura de que "faltou resolução espacial" não se sustenta para esta pergunta específica.
Buscar um dataset de sono maior para refazer este teste seria replicar o já replicado.

Dois agentes de busca independentes chegaram a este artigo por caminhos distintos — sinal
razoável de que é o trabalho central da questão, não um achado marginal.

**Reforço analítico:** Berger, Schneider, Kochs & Jordan (2017), *Entropy* 19(12):692,
DOI 10.3390/e19120692 — para padrões ordinais de três amostras, a entropia de permutação
aproxima o **centróide do espectro de potência ponderado**. A PE de ordem baixa é, em
primeira aproximação, uma estatística espectral. O colapso de 0,991 → 0,547 no projeto era
esperado por construção.

---

## 2. A assimetria sono-vs-anestesia: supressão, não sobrevivência

O Cap. 11 registrava o contraste como "nítido, e permanece sem explicação". Ele tem
explicação, obtida dos próprios dados do projeto (Spearman, época a época):

| | métrica × estado | **expoente × estado** | métrica × expoente | padrão |
|---|---|---|---|---|
| Sono (N3→W), n=12.895 épocas | +0,787 | **−0,790** | −0,875 | confundimento / mediação |
| Anestesia (basal→moderada), n=1.506 épocas | +0,293 | **+0,071** | −0,788 | **supressão** |

**No sono**, o expoente rastreia o estado tão bem quanto a complexidade e é quase colinear
com ela. Residualizar remove o sinal junto com o suposto confundidor — e nada sobra.

**Na anestesia**, o expoente **quase não rastreia o estado** (ρ=+0,07), mas segue fortemente
acoplado à LZc (ρ=−0,79). Removê-lo desmascara a associação que já existia no dado bruto.
Este é o padrão clássico de **variável supressora**.

**Os dois testes não são a mesma operação.** No sono, o controle testa uma explicação
rival genuína. Na anestesia, remove um incômodo correlacionado com a métrica mas quase
ortogonal ao estado. Chamar ambos de "o controle de 1/f" obscurece isso, e a leitura de que
o achado da anestesia "sobreviveu ao controle que matou o sono" **não se sustenta** — o
efeito já estava no dado bruto (AUC por sujeito 0,702, p=0,0063), e a residualização o
afiou em vez de testá-lo.

---

## 3. O controle do projeto é o mínimo da área

O padrão metodológico nesta literatura **não é residualização por FOOOF** — é
**normalização por surrogates de fase aleatorizada**, que preserva o espectro de potência
inteiro (expoente, offset, picos alfa e sigma), não apenas o expoente. Usado por
Schartner et al. (2017, *Sci Rep* 7:46421, DOI 10.1038/srep46421), Toker et al. (2022,
*PNAS*, DOI 10.1073/pnas.2024455119) e Maschke et al. (2025).

O IAAFT (Schreiber & Schmitz 1996, *Phys Rev Lett* 77:635) preserva **simultaneamente** o
espectro e a distribuição de amplitudes — nulo mais estrito que a randomização simples.

**Vantagens sobre a residualização, para este projeto:** o nulo captura o espectro inteiro,
não supõe forma funcional para a relação métrica~expoente, e gera uma estatística por época
que entra direto no teste de Wilcoxon dentro-sujeito já validado.

**Um ponto a favor do projeto que não está dito no manuscrito:** Westfall & Yarkoni (2016),
*PLoS ONE* 11(3):e0152719, DOI 10.1371/journal.pone.0152719 — controlar por covariável
medida com ruído é controle **incompleto**, e o viés resultante favorece detectar validade
incremental **espúria** (erro tipo I chegando a ~100% com n grande e confiabilidade
moderada). O expoente aperiódico é estimado com erro. **O projeto tinha o viés a seu favor
e ainda assim não achou nada** — isso torna o nulo mais forte, não mais frágil.

### Mediador ou confundidor: lacuna real da literatura

Se o estado altera o balanço E/I, que altera o expoente, que altera a LZc, o expoente é
**mediador** e residualizar é sobrecontrole. Nenhum teste estatístico distingue os dois
papéis com dados observacionais.

**Não há discussão publicada desse ponto em EEG de consciência** — nem em Maschke 2025, nem
em Höhn 2024, nem no guideline metodológico de Ping et al. (2025, *Mil Med Res* 12:90,
DOI 10.1186/s40779-025-00682-4). É lacuna genuína, e uma oportunidade para o projeto ser o
primeiro a formulá-la — ao custo de não haver literatura para citar.

Como decidir na prática: **pelo que se quer afirmar**. Se a tese é "existe uma propriedade
de integração diferenciada que não se reduz a lentidão espectral", o controle é o teste
certo — é teste de *validade incremental*. O resultado deve então ser reportado como
**redundância informacional**, não como "a complexidade não se relaciona com consciência".
São afirmações muito diferentes e só a primeira é sustentada.

---

## 4. O que medir

**Nenhuma medida observacional de complexidade tem, na literatura publicada, demonstração
de que sobrevive a um controle explícito do expoente aperiódico.** PCI, PCI^ST, wSMI,
dPTE/transfer entropy, PAC, microestados e ΦID nunca foram residualizados — não são imunes,
são **não testados**. Qualquer alegação de que "vão além do 1/f" é hoje proposta teórica.

Três evidências apontam partilha substancial mesmo na tradição perturbacional: Colombo 2019
(expoente de repouso altamente correlacionado com PCI), Nilsen 2024 (ρ=0,652 entre PCI^ST e
expoente 20–40 Hz), Maschke 2024 (*Commun Biol* 7:946) — PCI individual previsível só com
EEG espontâneo.

Único caso positivo publicado: Schartner et al. 2017, mas em estado **psicodélico**, não em
perda de consciência.

### Recomendação: irreversibilidade temporal

Processos lineares gaussianos estacionários são **reversíveis no tempo** (Weiss 1975,
*J Appl Probab* 12:831) — logo surrogates com espectro idêntico têm irreversibilidade nula
em expectativa. **O controle aperiódico é automático, por construção, não estatístico.**

Funciona com 1 canal, custo computacional trivial. Já discrimina vigília/sono/anestesia em
ECoG de macaco (de la Fuente et al. 2023, *Cereb Cortex* 33(5):1856,
DOI 10.1093/cercor/bhac177) e LFP de rato (Camassa et al. 2024, *Sci Rep*,
DOI 10.1038/s41598-024-74649-1), mas **ainda não foi aplicada a EEG humano de sono** —
contribuição original em vez de replicação.

---

## 5. Ameaças adicionais que valem registro

- **Halder et al. (2026), *Sci Rep*, DOI 10.1038/s41598-026-50911-6** — sob bloqueio
  neuromuscular, LZc classificou **100%** dos segmentos acordado-paralisado como
  "não-consciente" (contra 7% de erro usando potência alfa). Inclinação e LZc falham juntas:
  contaminação por EMG é confundidor comum às duas. Relevante para o teste de REM do projeto.
- **Helfrich et al. (2026), *PNAS*, DOI 10.1073/pnas.2514098123** — a redução de atividade
  aperiódica sob propofol se sobrepõe parcialmente ao sono REM, enfraquecendo o expoente
  como marcador puro de consciência.
- **Widmann et al. (2024), *Br J Anaesth* 134(2):392–401, DOI 10.1016/j.bja.2024.09.027** —
  62 acordados contra 125 sob anestesia geral (propofol, sevoflurano, desflurano): o
  **expoente sozinho dá AUC 0,98**, contra 0,96 da entropia aproximada e 0,94 da de
  permutação. Comparador duro para a alegação de anestesia do projeto.
- **Höhn et al. (2024)** é frequentemente citado como se dissesse que LZc e inclinação são
  redundantes. O que dizem é mais fraco: em banda larga convergem, mas em **30–45 Hz**
  divergem. Ressalva dos próprios autores: a complexidade em banda estreita "não produziu
  resultados particularmente significativos". O projeto ajusta em **1–40 Hz** (banda larga),
  então refazer em 30–45 Hz é teste de robustez barato, não resgate provável.

---

## 6. O nicho que continua aberto

**Ninguém aplicou o controle aperiódico ao paradigma Chennu com LZc.** O preprint mais
recente sobre esse mesmo dataset — "Reframing 'paradoxical' excitation"
(medRxiv 10.64898/2025.12.16.25342405, agora no BJA), usando Chennu n=20 + ReCCognition
n=8 — não analisa nem controla o expoente. A análise de anestesia deste projeto é original;
o que precisa mudar é como ela é **reportada** (seção 2).

---

## 7. Datasets, se e quando forem necessários

Só depois dos controles da seção 3. Em ordem de utilidade:

| Dataset | Por quê | Acesso |
|---|---|---|
| **Zenodo 806176** | Literalmente o dado de Colombo 2019: propofol, xenônio e cetamina no mesmo protocolo. Testa dependência de agente | **Restrito**, pedido via Zenodo |
| **Dryad — Farnes 2020** | Cetamina, 62 canais, 934 MB. Dissocia consciência de responsividade | Aberto, CC0 |
| **OpenNeuro ds005620** (Oslo) | Único aberto com propofol + TMS-EEG + relato subjetivo nos mesmos sujeitos, 65 canais, 5 kHz | Aberto, 83 GB. **Os rótulos de relato não estão no BIDS** |
| **ANPHY-Sleep** (OSF R26FH) | 83 eletrodos 10-10, 1000 Hz, noite inteira — viabiliza medidas grafo-teóricas | Aberto, CC BY-NC-ND, ~86 GB |
| **DOD-H** (Dreem) | 250 Hz, **5 scorers independentes** por registro | Zenodo, MIT |
| **VitalDB** | Propofol × sevoflurano × desflurano, milhares de casos | Aberto, mas só 2 canais a 128 Hz |

**Não existe dataset aberto de distúrbios de consciência com classificação CRS-R** —
confirmado no OpenNeuro, no catálogo openlists e em buscas dirigidas. As coortes
(Pitié-Salpêtrière n=303, McGill, Liège, Milão) são fechadas ou "upon reasonable request".

**Observação sobre o dataset atual:** os arquivos SC do Sleep-EDF são gravações de **~20 h
em atividade diurna normal**. O corte em ±30 min em torno do sono é convenção da literatura,
não limite do dataset. A falta de vigília ativa pode ser atacável sem trocar de dados — não
verificado se os hipnogramas cobrem as 20 h.

---

## 8. Estatuto de verificação

| Afirmação | Estatuto |
|---|---|
| Números da seção 2 (correlações) | ✅ Calculados por mim sobre os dados do projeto; reprodutíveis pelo script |
| Banda de ajuste 1–40 Hz do projeto | ✅ Conferido no código (`FIT_FREQ_RANGE`) |
| Todas as referências externas citadas aqui | ⚠️ Verificadas pelos agentes contra PubMed/DOI; **não reverificadas por mim** |
| Ausência de dataset aberto de DoC com CRS-R | ⚠️ Busca ampla, mas ausência de evidência não é evidência de ausência |
| Tamanhos, licenças e contagens de canais dos datasets | ⚠️ Reportados pelos agentes a partir de páginas oficiais; não reconferidos |

**Antes de qualquer citação desta nota entrar no manuscrito, ela precisa passar pela mesma
verificação direta contra Crossref/PubMed que as referências 1–106 já passaram.**
