# Protocolo VNext-01 — Irreversibilidade temporal e normalização por surrogates de fase no EEG humano de sono

**Estatuto:** protocolo prospectivo congelado — *timestamped preregistration draft* —, **não
executado**. A distinção é deliberada e vale ser mantida: este documento é congelado antes de
qualquer análise e sua data fica registrada no histórico do repositório, o que é boa evidência
temporal, mas **não é um pré-registro depositado**. Branches podem ser reescritas; um commit em
`main` é bem mais forte que um em branch de trabalho, e ainda assim não equivale a um registro em
plataforma própria. Antes de qualquer publicação derivada deste protocolo, depositar esta versão
congelada em **OSF ou Zenodo**, com DOI permanente, e citar o DOI aqui. Onde o texto abaixo usa
"pré-registrado" e "pré-registro", leia-se no sentido de disciplina metodológica — fixar decisões
antes de ver o dado —, não no sentido de depósito formal já realizado. Escrito em 2026-08-13 por agente, sob a
regra 0.1 do `PLANO_ESTRATEGICO_cientifico.md` (agentes escrevem cálculo, não executam cálculo).
Nenhum número deste documento é resultado: os números citados vêm de arquivos do projeto, com a
fonte indicada em cada caso, ou são **estipulações de desenho** explicitamente marcadas como tais.

**Contrato que este documento cumpre:** os sete itens da §6 do `MAPA_TRABALHO_Conscience_V05.md`,
reproduzidos como seções §2 a §8, na ordem original.

**Regra de congelamento.** Este arquivo deve ser commitado *antes* de qualquer execução. A partir do
commit de congelamento, toda alteração entra na §16 (registro de emendas) com data, motivo e se
ocorreu antes ou depois de o autor ter visto qualquer resultado da fase correspondente. Uma emenda
posterior à visualização de resultados não invalida o protocolo, mas rebaixa a análise afetada de
confirmatória a exploratória — sem exceção.

---

## 1. O impasse que este protocolo ataca

O projeto tem um resultado bruto forte e uma interpretação mecanística falhada. LZc e entropia de
permutação separam vigília de sono profundo com AUC por sujeito de 0,991 (n=36, `resultados_por_sujeito.csv`);
residualizadas pelo expoente aperiódico fora da amostra, caem para 0,500 [0,425–0,577], p=0,96 — o acaso
quase exato. As predições 1.2, 1.3 e 1.3b estão ❌ FALHOU no `registro_falsificabilidade.md`.

Três fatos impedem tratar isso como questão encerrada, e um quarto impede tratá-la como reaberta
de qualquer maneira.

**Primeiro: o poder.** No tamanho de efeito observado (dz=−0,099) o teste tinha 16,7% de poder
(`nota_calibracao_teste.md`, v3, n_sim=2000). Um nulo obtido com 16,7% de poder é ausência de
evidência. Ele é decisivo contra um mecanismo de efeito grande (91% de poder em dz≥0,5) e mudo
contra um efeito pequeno.

**Segundo: a medida não foi a medida.** A Frente C foi desenhada para operar a alegação-assinatura
da teoria — integração alta *e* diferenciação alta simultaneamente — com **medidas grafo-teóricas de
integração e segregação**. O Sleep-EDF Cassette tem 2 canais reais de escalpo (Fpz-Cz, Pz-Oz), o que,
como o próprio cabeçalho de `integracao_diferenciada_1f.py` declara, "NÃO permite medidas
grafo-teóricas de integração/segregação multi-região (que exigiriam ≥8-16 canais/ROIs)". O que foi
testado foi um proxy declaradamente degradado: informação mútua × entropia de permutação entre dois
eletrodos. A predição 1.3 falhou **com esse proxy**, e é honesto registrar que ela nunca foi testada
com a medida para a qual foi formulada.

**Terceiro: o controle é o mínimo da área.** O padrão metodológico é normalização por surrogates de
fase, que preserva o espectro inteiro; o projeto usa residualização por FOOOF, que remove apenas o
expoente (`nota_estado_da_arte_1f.md`, §3).

**Quarto, e em sentido contrário: refazer 1.2 em dataset maior seria replicar o já replicado.**
Maschke et al. (2025) fizeram exatamente esse teste com 225 pacientes e 256 canais e obtiveram o
mesmo colapso — r(197)=0,86 entre expoente e LZc, valor diagnóstico da LZc desaparecendo na
correlação parcial, r caindo a 0,24 sob surrogates de fase. A linha de fuga "faltou resolução
espacial" não se sustenta **para 1.2**.

Esta última conclusão é sólida e **não se transfere para 1.3**. São perguntas diferentes que a
`nota_estado_da_arte_1f.md` trata como uma só, e essa é a confusão que este protocolo desfaz:

| | 1.2 | 1.3 |
|---|---|---|
| Pergunta | a complexidade de sinal sobrevive ao controle aperiódico? | integração diferenciada supera sincronia bruta? |
| Medida exigida | LZc/PE, univariada | integração vs. segregação em rede |
| Canais necessários | 1–2 bastam | ≥8–16 |
| Estado | testada, falhou, **replicada externamente em escala** | testada só por proxy de 2 canais; **nunca testada com a medida que a define** |
| Refazer em dataset maior | replicaria o já replicado | é o primeiro teste adequado |

O protocolo tem, portanto, dois braços com estatutos distintos, e uma prioridade lógica entre eles.

---

## 2. Contrato, item 1 — Pergunta e estimando primário

### 2.1 A pergunta

**Existe, no EEG humano de sono, estrutura temporal que discrimine vigília de sono profundo e que
seja inacessível, por construção, a qualquer descrição linear-gaussiana estacionária do sinal — isto
é, a qualquer descrição que o espectro de potência já esgote?**

A pergunta é deliberadamente mais fraca do que a alegação-assinatura da teoria. Ela não pergunta se
há integração diferenciada; pergunta se há **qualquer coisa** além da assinatura espectral. É a
pergunta que o impasse atual torna primeira: enquanto ela não for respondida, toda medida candidata
de complexidade permanece sob a suspeita que Maschke et al. (2025) e Berger et al. (2017)
levantaram, e nenhuma delas tem, na literatura publicada, demonstração de que sobrevive ao controle
aperiódico (`nota_estado_da_arte_1f.md`, §4).

### 2.1.1 O que um resultado positivo autoriza concluir — e o que não

Esta restrição é vinculante para todo o documento e para qualquer relatório derivado dele. Um
resultado positivo significa, exatamente:

> **existe estrutura temporal incompatível com o nulo IAAFT — isto é, com a classe de descrições
> lineares-gaussianas-estacionárias que esse nulo representa.**

Não significa "encontramos não linearidade", e menos ainda "encontramos a não linearidade da
consciência". A irreversibilidade temporal é **sensível a mais de uma causa**, e o nulo IAAFT é uma
classe de hipóteses, não uma única. Um positivo é compatível com pelo menos cinco origens que este
desenho não separa entre si: dinâmica genuinamente não linear; **processo linear não gaussiano** — a
literatura sobre o teorema de Weiss é explícita em que a irreversibilidade implica dinâmica não
linear *ou* distribuição não gaussiana, e a segunda alternativa não exige não linearidade alguma;
**não estacionariedade** dentro da
época; **assimetria de forma de onda** (a onda lenta do sono profundo é o caso óbvio, e a §14.2 já a
nomeia como a explicação alternativa mais provável de um resultado direcionalmente invertido); e
dependências temporais de ordem superior que o nulo preserva mal. A primeira, a terceira e a quarta
já constam como ameaças pré-declaradas em §14 — a linguagem da conclusão precisa ser consistente com
essa cautela, e não mais forte que ela. A segunda merece registro à parte, porque é a origem que mais
facilmente seria relatada como "achamos não linearidade" sem que houvesse não linearidade nenhuma.

Consequência prática: nenhum relatório deste protocolo deve escrever "estrutura não linear" onde o
que foi testado é "incompatibilidade com o nulo IAAFT". Separar as cinco origens acima é trabalho
de um protocolo posterior, com nulos adicionais desenhados para discriminá-las — e é uma pergunta
logicamente anterior a qualquer alegação sobre integração diferenciada, que por sua vez é anterior
a qualquer alegação sobre consciência. A ordem é: existe excedente sobre o espectro → de que tipo é
o excedente → ele é de rede → ele corresponde ao mecanismo que a teoria propõe. Este protocolo
responde apenas ao primeiro elo.

### 2.2 O estimando primário

**Estimando:** a média, na população de adultos saudáveis registrados em polissonografia noturna, da
área sob a curva ROC calculada **dentro de cada participante**, discriminando épocas de vigília de
épocas de sono profundo pela **irreversibilidade temporal normalizada por surrogates IAAFT** do sinal
de escalpo.

**Unidade de amostragem:** o participante. **Unidade de observação:** a época de 30 s.

**Direção pré-declarada:** a vigília é a classe positiva. A teoria prevê AUC > 0,5 — vigília
temporalmente **mais irreversível** que sono profundo. Um resultado AUC < 0,5 com discriminação forte
é falsificação direcional, não sucesso, e a §14.2 já registra qual é a explicação alternativa
disponível para ele antes de ele acontecer.

### 2.3 Por que irreversibilidade, e por que ela resolve o que a residualização não resolve

O argumento é matemático antes de ser empírico. Processos lineares gaussianos estacionários são
reversíveis no tempo (Weiss 1975, *J Appl Probab* 12(4):831–836, DOI 10.2307/3212735). Um surrogate
que preserva o espectro de potência e a distribuição de amplitudes preserva, portanto, tudo que uma
descrição linear-gaussiana pode conter, e tem irreversibilidade nula em expectativa. Segue que:

> ✅ **Premissa verificada (2026-08-13), com um reforço e uma correção.** A referência foi conferida
> contra o registro do Cambridge Core: Gideon Weiss (Tel-Aviv University), *Journal of Applied
> Probability* 12(4), dezembro de 1975, pp. 831–836, DOI 10.2307/3212735. A direção de que este
> protocolo depende está confirmada — processos lineares gaussianos são reversíveis —, e a recíproca
> também: entre processos ARMA discretos, a reversibilidade **caracteriza unicamente** os gaussianos.
> A definição de reversibilidade usada é a igualdade das distribuições conjuntas de
> $\{X(t_1),\dots,X(t_n)\}$ e $\{X(-t_1),\dots,X(-t_n)\}$.
>
> **Reforço.** A literatura metodológica registra que não só os processos lineares gaussianos, mas
> também **transformações não lineares estáticas** deles são reversíveis. Isso é precisamente o nulo
> que o IAAFT constrói — o alinhamento entre a medida e o nulo é, portanto, mais estreito do que a
> formulação original desta seção afirmava, e é a razão adicional para o estimador de padrões
> ordinais, invariante a transformação monótona da amplitude, ser a companheira natural do IAAFT.
>
> **Correção.** Pela mesma fonte, a irreversibilidade implica "dinâmica não linear **ou** (linear ou
> não linear) **não gaussiana**". Um processo **linear não gaussiano** também produz positivo. Essa
> origem foi acrescentada à lista da §2.1.1, que antes tinha quatro e agora tem cinco.
>
> **Limite desta verificação.** O acesso ao texto integral estava indisponível no momento da consulta;
> foram lidos abstract, metadados e a definição formal, não o corpo do artigo. As condições técnicas
> exatas — estacionariedade, causalidade, inovações iid — **não foram conferidas na fonte primária**.
> A direção necessária está corroborada por duas vias independentes, mas a leitura integral segue
> recomendada antes de qualquer publicação derivada.

**O controle aperiódico deixa de ser um teste estatístico e passa a ser uma propriedade da medida.**
Não se residualiza nada. Não se condiciona a nada. Não se pergunta se o expoente é mediador ou
confundidor, porque o expoente não entra na conta — ele está integralmente preservado no nulo. A
estatística normalizada mede exatamente o excedente sobre o que o espectro explica, seja qual for o
papel causal do espectro.

Isso é o oposto do que a residualização faz. A residualização remove variância compartilhada, e
remover variância compartilhada com um mediador é sobrecontrole — o problema que a
`nota_estado_da_arte_1f.md` identifica como lacuna genuína e sem discussão publicada em EEG de
consciência. Ver §11.

Há dois custos honestos nessa troca, declarados aqui e não descobertos depois. O primeiro é que a
premissa de estacionariedade é uma idealização, e sua violação é a principal ameaça ao desenho
(§14.1). O segundo é que irreversibilidade **não é** integração diferenciada: ela testa se existe
algo além do espectro, não se esse algo é o que a teoria diz. Um resultado positivo aqui não
confirma o Postulado 3; abre a possibilidade de testá-lo. Este protocolo não usará linguagem que
sugira o contrário em nenhuma circunstância.

---

## 3. Contrato, item 2 — Dados, inclusão/exclusão e unidade de divisão

### 3.1 Braço A — Sleep-EDF Cassette (dado em disco)

**Fonte:** `dados_sleepedf/physionet-sleep-data/`, 39 pares PSG/Hipnograma em cache local. Canais
`Fpz-Cz` e `Pz-Oz`, 100 Hz, épocas de 30 s, filtro 0,5–40 Hz — as mesmas convenções de
`analise_sono_v2.py` e `integracao_diferenciada_1f.py`, deliberadamente não alteradas, para que os
números novos sejam comparáveis com a linha de base.

**Inclusão/exclusão, herdada e agora declarada explicitamente:** dos 41 índices solicitados na rodada
original, 2 não existem no dataset e 3 dos 39 registros restantes não têm épocas de N3, o que dá o
n=36 usado em todo o projeto (`CHECKLIST_pendencias.md`, linha do Bloco K: "3 sujeitos sem N3;
2 índices ausentes do dataset"). Este protocolo mantém **os mesmos 36 participantes**, e a razão é
metodológica, não de conveniência: qualquer alteração da amostra tornaria a comparação com
AUC=0,991 bruta e 0,500 residual não interpretável. A exclusão por ausência de N3 é uma exclusão
condicionada ao desfecho e deve ser reportada como tal em qualquer publicação.

**Épocas por condição, na linha de base:** 8.923 de vigília contra 3.972 de N3, razão 2,25:1, mínimo
de 128 e mediana de 312 épocas por participante (`resumo_teste_calibrado.md`). Esse desequilíbrio é
exatamente o que invalidou o teste antigo e é irrelevante para o teste calibrado, por construção.

**Unidade de divisão: o participante.** Sempre. Toda partição de validação cruzada particiona
participantes, nunca épocas — a correção registrada em Z1, onde a guarda contava épocas e o `KFold`
particionava sujeitos, é precedente suficiente para tornar isso explícito.

### 3.2 A questão da vigília ativa (Z12) e por que ela **não** altera o contraste primário

O corte atual mantém ±30 min em torno do primeiro e do último estágio anotado
(`analise_sono_v2.py`, linhas 66–72). Os arquivos SC são gravações de ~20 h em atividade diurna
normal, e não está verificado se os hipnogramas cobrem essas 20 h. Detalhe do próprio código que
sugere — sem provar — que cobrem: o corte ancora em `sleep_annots[1]` e `sleep_annots[-2]`, isto é,
**pula deliberadamente a primeira e a última anotação pontuada**, o que só faz sentido se elas forem
blocos longos de vigília. Isso é uma leitura de código, não uma verificação: quem decide é a checagem
de Z12, executada pelo autor.

A tentação é fazer o contraste primário depender do resultado dessa checagem. **O protocolo recusa
isso**, por duas razões. A primeira é forking path: deixar o denominador da comparação ser escolhido
depois de olhar o dado é precisamente o que um pré-registro existe para impedir. A segunda é que
recuperar vigília diurna não é um ganho limpo — troca um problema por outro. A vigília do corte atual
é o período calmo em torno do sono, o que já explicou a falha do proxy de EMG (Z5); a vigília diurna
está separada do sono profundo por muitas horas, e portanto difere dele também em hora do dia,
tempo desde a colocação dos eletrodos, deriva de impedância e contaminação por movimento e EMG — um
confundidor **perfeitamente alinhado ao contraste**, e a literatura já registra que a contaminação
por EMG derruba LZc e inclinação juntas (Halder et al. 2026, em `nota_estado_da_arte_1f.md`, §5).

Decisão pré-registrada:

- **Contraste primário: W(calmo) vs N3**, na definição atual, sem alteração. É onde a linha de base
  existe e onde o valor incremental da medida nova é mensurável.
- **Contraste secundário confirmatório: W(ativo) vs N3**, executado **somente se** a checagem de Z12
  atingir o critério de suficiência estipulado abaixo, com critério de sucesso próprio (§6.3) e com
  os controles de deriva do §14.3.
- **Divergência entre os dois é achado, não menu.** Se a irreversibilidade discriminar num contraste
  e não no outro, isso é informação sobre a condição de vigília do dataset e será reportado assim.

**Critério de suficiência para Z12 (estipulado, fixado antes de olhar):** o braço W(ativo) só é
executado se, em pelo menos **30 dos 36 participantes**, existirem **≥30 épocas** (15 min) anotadas
como vigília fora da janela de ±30 min do corte atual, após rejeição de artefato. Os dois números são
estipulações de desenho; sua única exigência é estarem fixados antes da checagem, e estão.

### 3.3 Braço B — dataset multicanal

Ver §12, onde a escolha é decidida e justificada, com a alternativa que foi preterida e por quê.

---

## 4. Contrato, item 3 — Ajuste por 1/f, treino separado ou cross-fitting

O contrato exige declarar o ajuste por 1/f com modelo estimado apenas em dados de treino. Este
protocolo **cumpre o item declarando que o rebaixa**, e a justificativa precisa ficar registrada
porque é uma mudança de estratégia, não um esquecimento.

A residualização por FOOOF deixa de ser o controle primário. Ela permanece no desenho em três papéis
subordinados, e em todos eles com a mesma convenção de fora da amostra que o projeto já adota — ajuste
linear métrica~expoente estimado por validação cruzada de 5 partições **sobre participantes**, nunca
sobre épocas, com o modelo de cada partição de teste treinado exclusivamente em participantes das
outras partições (`teste_auc_por_sujeito.py`; `integracao_diferenciada_1f.py`):

1. **Comparabilidade histórica.** Os comparadores LZc e PE são recomputados nas mesmas épocas, brutos
   e residualizados fora da amostra, para verificar que o pipeline novo reproduz a linha de base
   (§5.4, controle positivo).
2. **Banda de ajuste inalterada:** 1–40 Hz (`FIT_FREQ_RANGE`), limitada pelo filtro de 0,5–40 Hz já
   aplicado. Ver §13.1 sobre por que 30–45 Hz não é uma opção sob o pipeline atual.
3. **Convenção de ordem, documentada porque já custou uma conclusão errada:** filtrar o par de
   estados primeiro, residualizar depois. Residualizar sobre os cinco estágios antes de filtrar W/N3
   produziu uma AUC espúria de 0,648 que parecia reverter 1.2 (`nota_calibracao_teste.md`, §4).

E fica registrado o que substitui a residualização como controle primário: **o nulo generativo IAAFT**
(Schreiber & Schmitz 1996), que preserva simultaneamente o espectro de potência e a distribuição de
amplitudes. Não há "ajuste em treino" a declarar aqui porque não há ajuste: o nulo é gerado da própria
época, época a época, e a estatística é normalizada contra o ensemble da própria época. Não existe
vazamento entre participantes possível nessa operação — o que é uma vantagem estrutural, não um
detalhe.

> ✅ **Premissa verificada (2026-08-13), e ela fecha o argumento com Weiss.** Schreiber T, Schmitz A.
> "Improved Surrogate Data for Nonlinearity Tests". *Physical Review Letters* 1996;**77(4):635–638**,
> DOI 10.1103/PhysRevLett.77.635 (conferido no PubMed, PMID 10062864). Confirmado: o algoritmo
> iterativo produz surrogates que compartilham **simultaneamente a distribuição de amplitudes e o
> espectro de potência** com o dado, randomizando as fases de Fourier.
>
> **O ponto que importa para §2.3.** O nulo que os autores propõem é explicitamente o de
> *"nonlinear rescalings of a Gaussian linear process"* — processos lineares gaussianos **e suas
> transformações não lineares estáticas**. Essa é exatamente a classe que a literatura sobre o
> teorema de Weiss identifica como reversível no tempo. Os dois lados do argumento fecham por
> verificação independente: o **nulo teórico** do IAAFT corresponde à classe reversível que este
> protocolo quer testar. A distinção entre nulo teórico e realização computacional precisa ser
> mantida — a hipótese nula formulada pelos autores corresponde àquela classe, mas o **surrogate
> efetivamente gerado** continua sendo aproximado, porque o algoritmo iterativo termina com
> discrepância residual nas restrições. Essa não é uma ressalva retórica: é exatamente a limitação
> registrada no parágrafo seguinte, e ela vai passar a ter número quando o smoke test começar a
> quantificar o erro espectral do ensemble.
> É a justificativa mais forte disponível para a afirmação de que o controle aperiódico aqui é
> propriedade da medida, e não teste estatístico.
>
> **Limitação registrada como ameaça.** O IAAFT foi criado para corrigir o viés de achatamento do
> espectro do AAFT original, mas é um algoritmo **iterativo com critério de parada** (número máximo
> de iterações e tolerância relativa), não uma construção exata. Resta discrepância residual entre o
> espectro do surrogate e o do dado, e implementações costumam recomendar repetir a geração e
> escolher o surrogate mais bem convergido. Como a estatística primária é normalizada **contra o
> ensemble**, uma discrepância espectral residual sistemática entrava diretamente no zero da medida.
> Consequência operacional, pré-declarada: a etapa de smoke test (§15) deve reportar a discrepância
> espectral mediana entre surrogate e dado, e o critério de tolerância usado, junto com os demais
> diagnósticos — não como resultado, mas como controle de qualidade do nulo.

---

## 5. Contrato, item 4 — Métrica primária, comparadores e análises de sensibilidade

### 5.1 Métrica primária

**Irreversibilidade temporal por assimetria de padrões ordinais, normalizada por ensemble IAAFT.**

Para cada época e cada canal, compara-se a distribuição de padrões ordinais da série com a
distribuição de padrões ordinais da mesma série invertida no tempo; a estatística é a divergência
entre as duas. A escolha do estimador é justificada por três coisas: reutiliza a maquinaria ordinal
que o projeto já usa em `pe_epoch` (ordem 3, atraso 1, `antropy`), funciona com 1 canal, e é
invariante a qualquer transformação monótona da amplitude — o que a torna a companheira natural do
IAAFT, que preserva exatamente a distribuição de amplitudes.

Parâmetros pré-declarados: **ordem m=4, atraso τ=1**, sobre épocas de 30 s a 100 Hz (3.000 amostras,
o que dá em média 125 contagens por padrão com 24 padrões — margem confortável de estimação; a ordem
5, com 120 padrões, ficaria em ~25 contagens e não é usada como primária por isso). Média dos 2
canais, seguindo a convenção do projeto para LZc/PE.

**Normalização:** para cada época, gera-se um ensemble de **99 surrogates IAAFT** e reporta-se
Δ_norm = (Δ_obs − média(Δ_surr)) / desvio-padrão(Δ_surr). A normalização não é cosmética: todo
estimador de divergência por plug-in é não negativo e enviesado para cima em amostra finita, de modo
que Δ_obs é positivo mesmo em dados perfeitamente reversíveis. **É o ensemble que define o zero.**
É também por isso que Z10 e Z11 não são duas pendências espremidas no mesmo protocolo: sem o
surrogate, a medida de Z11 não tem escala interpretável.

O número 99 é estipulação. O autor deve rodar uma smoke test com `--n-subjects 3` antes da amostra
cheia — convenção já estabelecida em `README_como_rodar.md` da Frente C — e, se o tempo de parede
inviabilizar a rodada completa, reduzir o ensemble **antes** de vê-lo, registrando a mudança na §16.
Ordem de grandeza a dimensionar na smoke test: as 12.895 épocas de W/N3 × 2 canais × 99 surrogates
são ~2,55 milhões de gerações de surrogate.

### 5.2 Teste estatístico

O teste calibrado do projeto, sem alteração: AUC calculada **dentro** de cada participante (épocas de
W dele contra épocas de N3 dele), seguida de Wilcoxon dos postos sinalizados dessas 36 AUCs contra
0,5, com o teste-t de uma amostra ao lado como referência, e IC 95% por bootstrap sobre
participantes. Correção FDR dentro da família declarada na §5.5.

**Pré-requisito bloqueante:** o desenho novo passa antes pela calibração por permutação de rótulos
dentro de participante (`varredura_desenhos.py`), e o erro tipo I empírico precisa cair na janela
**2,0%–8,5%**, que é a faixa que o projeto já aceitou para os 15 desenhos existentes
(`nota_calibracao_teste.md`, §3). Fora dessa janela, os p-valores do braço não são interpretados até
o desenho ser corrigido. Isso não é formalidade: foi exatamente essa checagem que expôs um desenho
rejeitando 100% das vezes sob o nulo.

### 5.3 Comparadores adversariais

Um teste sem comparador adversarial não decide nada. Todos são calculados nas **mesmas épocas**, com
o **mesmo teste**, e entram na mesma família de FDR:

| Comparador | Papel | O que significa se ele empatar ou vencer |
|---|---|---|
| LZc bruta | controle positivo do pipeline | deve reproduzir ≈0,991; se não, o pipeline está quebrado e nada se interpreta |
| LZc residualizada fora da amostra | linha de base do impasse | deve reproduzir ≈0,500 |
| **LZc normalizada por IAAFT** | o padrão da área (Z10) | se discriminar onde a residualizada não discrimina, a diferença é sobre o controle, não sobre a teoria |
| Expoente aperiódico sozinho | o rival | se a irreversibilidade não superá-lo, não há excedente a alegar |
| **Irreversibilidade dos próprios surrogates** | controle negativo | tem de dar ≈0,5 por construção; se não der, o gerador de surrogate está errado |

A inclusão da LZc normalizada por IAAFT tem **expectativa pré-declarada de resultado nulo**: Maschke
et al. (2025) já mostraram r caindo a 0,24 sob surrogates de fase, e o IAAFT é um nulo mais estrito
que a residualização por FOOOF, porque preserva também os picos oscilatórios (alfa, sigma) que a
residualização deixa passar. Esperar que ela discrimine seria esperar contra a literatura e contra a
própria linha de base do projeto. Ela entra como **análise de comparabilidade** — para que os números
do projeto possam ser postos ao lado de Schartner (2017), Toker (2022) e Maschke (2025) —, não como
uma segunda chance da mesma hipótese. Declarar isso antes é o que impede que um acaso favorável nessa
linha seja lido depois como resgate.

### 5.4 Controles de integridade, executados e reportados antes do desfecho primário

Nenhum resultado primário é interpretado antes de os dois controles da tabela acima passarem: LZc
bruta reproduzindo ≈0,991 (tolerância estipulada: ±0,01) e irreversibilidade dos surrogates em
0,5 (tolerância estipulada: IC 95% contendo 0,5). Se qualquer um falhar, a rodada é diagnóstico de
pipeline, não teste de hipótese, e assim será registrada.

### 5.5 Família de FDR e análises de sensibilidade

**Família primária: um único teste** — irreversibilidade normalizada, W(calmo) vs N3, média dos
2 canais. Um teste primário isolado é uma escolha deliberada de proteção de poder; tudo o mais é
secundário.

**Família secundária (FDR entre si, não com o primário):** LZc normalizada por IAAFT; expoente
sozinho; irreversibilidade por canal (Fpz-Cz e Pz-Oz separados); irreversibilidade em W(ativo) vs N3,
se Z12 autorizar.

**Sensibilidade, pré-especificada e sem poder de mudar veredito:** ordem m=3 e m=5; atraso
τ ∈ {2, 4} e, pela razão de escala temporal exposta abaixo, também **τ ∈ {25, 50, 75}** (0,25 s,
0,5 s e 0,75 s a 100 Hz); estimador alternativo por grafo de visibilidade horizontal; ordenação
completa dos cinco
estágios (W, N1, REM, N2, N3) pela irreversibilidade, com Spearman contra o ordinal já convencionado
no projeto. Cada uma dessas linhas serve para descrever a robustez do resultado primário, **não para
substituí-lo**: se o primário falhar e uma sensibilidade "der certo", o registro dirá que o primário
falhou.

### 5.5.1 Os dois precedentes animais: o que eles são, e o que eles não autorizam

Etapa 0.2 executada em 2026-08-13. Os dois estimadores foram identificados, e o resultado muda o
peso que essas referências podem carregar.

| | de la Fuente et al. (2023) | Camassa et al. (2024) | **Este protocolo** |
|---|---|---|---|
| Estimador | rede neural convolucional 1D treinada para distinguir épocas diretas de invertidas | "arrow of time" do arcabouço INSIDEOUT (Deco et al.): $\lvert\rho(x_t, y_{t+\Delta t}) - \rho(x^r_t, y^r_{t+\Delta t})\rvert$ | assimetria de padrões ordinais, m=4 |
| Forma fechada | **não tem** — o classificador é a medida | assimetria de covariância defasada | sim |
| Univariado? | não — 3 primeiros componentes principais de 128 canais | **não** — é pareado por construção | **sim**, por canal |
| Escala temporal | épocas de 4 s a 256 Hz | **Δt = 0,75 s**, janelas de 10 s a 200 Hz | **τ = 1 amostra = 0,01 s** a 100 Hz |
| Amostra | 2 animais por condição, ECoG | 5 ratos, LFP | 36 humanos, EEG de escalpo |

**Classificação da transferência de evidência: apenas evidência conceitual de irreversibilidade.**
Não é a mesma métrica, e não é a mesma família de métricas — nenhum dos dois é baseado em padrões
ordinais, e o de Camassa nem sequer é univariado. Segue que **nenhum dos dois pode ancorar tamanho de
efeito** para este desenho, e a §10 não deve importar expectativa deles. O que eles sustentam é mais
modesto e ainda assim útil: que a irreversibilidade temporal **discrimina estados de consciência em
tecido cortical**, em duas espécies e duas modalidades de registro independentes.

**O que eles sustentam de forma direcional.** Camassa et al. relatam irreversibilidade **mais baixa**
em sono de ondas lentas e anestesia profunda, e **mais alta** na vigília — a mesma direção que a §2.2
pré-declara (vigília como classe positiva, AUC > 0,5). A direção, portanto, não é uma aposta cega;
o tamanho continua sendo.

**Um risco de desenho que esta verificação expôs, e que não estava registrado.** A única escala
temporal explícita na literatura precedente é a de Camassa: **Δt = 0,75 s**. O atraso primário deste
protocolo é τ = 1 amostra, isto é, **0,01 s a 100 Hz**, e a faixa de sensibilidade originalmente
prevista ia só até τ = 4 (0,04 s). São **duas ordens de grandeza** de distância. Se a assimetria
temporal do córtex vive na escala de centenas de milissegundos, um estimador ordinal com τ = 1
poderia não vê-la por construção — e um nulo obtido assim não seria evidência sobre o fenômeno, e
sim sobre a escala escolhida. Por isso a lista de sensibilidade acima foi estendida para cobrir a
faixa de Camassa. Isto é análise de sensibilidade pré-declarada, **não** um segundo teste primário:
se o primário falhar e uma escala longa "der certo", o registro dirá que o primário falhou e que
existe um achado exploratório de escala a testar em protocolo próprio.

---

## 6. Contrato, item 5 — Critério explícito de suporte, resultado inconclusivo ou falha

Os três critérios abaixo são fixados antes da execução, com números. Um protocolo que não pode falhar
não vale nada, e a forma mais comum de um protocolo não poder falhar é não declarar antes o que
contaria como falha.

Todos os limiares desta seção são **estipulações de desenho**. A justificativa do limiar central está
em §6.4.

### 6.1 Desfecho primário (W calmo vs N3, irreversibilidade normalizada, n=36)

**SUPORTE.** AUC média por participante ≥ **0,60**, com p < 0,05 no Wilcoxon, e ≥ **25 dos 36
participantes** acima de 0,5. As três condições são conjuntas. A terceira existe porque o projeto já
reporta `frac_sujeitos_acima_05` e porque um efeito carregado por poucos participantes não é o que a
teoria afirma.

**EQUIVALÊNCIA (nulo informativo).** Teste formal de equivalência por **TOST** (*two one-sided
tests*) a α = 0,05 contra as margens **[0,45; 0,55]**, o que equivale a exigir o **IC 90%** da AUC
média contido inteiramente nessas margens. Isto é um nulo positivo, não uma ausência de resultado:
significa que o efeito, se existe, é menor que o menor efeito de interesse declarado, e a leitura
registrada será a de **redundância informacional** — o EEG de sono de 2 canais, tal como este
pipeline o processa, não contém estrutura temporal incompatível com o nulo IAAFT, e a
alegação-assinatura da teoria perde mais uma operacionalização. Resultado negativo é dado.

> ⚠️ **Este ramo é inacessível em n = 36, e a frase acima não é operacionalmente realizável neste n.**
> Registrado como F8 em 2026-08-17, antes de qualquer execução do desfecho. Simulada sob o caso mais
> favorável possível — AUC verdadeira **exatamente** 0,500 —, a probabilidade de satisfazer a regra
> é ≈ 0 para toda dispersão a partir de dp = 0,2346, que é o cenário de referência. Ela só deixa de
> ser desprezível no extremo inferior da faixa varrida (0,395 em dp = 0,1173; 0,004 em dp = 0,1760),
> isto é, sob uma dispersão metade da observada para a LZc residualizada. A regra só passa
> a ser alcançável com 80% de probabilidade em **n ≈ 190** (TOST/IC 90%) ou **n ≈ 232** (a formulação
> anterior, por IC 95%). A margem de ±0,05 em torno de 0,5 é mais estreita que a própria
> semi-amplitude do IC em n = 36, que é ≈ 0,077 na dispersão de referência.
>
> A troca de IC 95% por TOST/IC 90% foi feita **por ser a formulação convencional de equivalência**,
> não para tornar o ramo alcançável — ela não o torna. As margens [0,45; 0,55] permanecem inalteradas,
> e são as mesmas de §6.4.
>
> **Consequência que o desenho passa a declarar explicitamente:** neste n, um efeito genuinamente nulo
> é classificado como INCONCLUSIVO *por construção*, e não por o dado ser ambíguo. O desenho é capaz
> de encontrar um efeito suficientemente grande e **não** é capaz de estabelecer que um efeito é
> suficientemente pequeno. Essa assimetria é propriedade do desenho, não achado científico, e o
> registro do desfecho deve nomeá-la sempre que o veredito cair em INCONCLUSIVO pela primeira via.

**FALSIFICAÇÃO DIRECIONAL.** AUC ≤ 0,40 com p < 0,05 — sono profundo **mais** irreversível que
vigília. Não é sucesso, é resultado contrário à predição, e a §14.2 já nomeia a explicação
alternativa mais provável antes de o resultado existir.

**INCONCLUSIVO.** **Todo o restante**, sem exceção. Esta é uma categoria residual por construção,
para que nenhum resultado possível fique sem destino declarado antes da execução. Ela cobre dois
cenários qualitativamente distintos, e o registro deve nomear qual ocorreu:

- *Nulo não informativo.* p ≥ 0,05 com o IC 90% se estendendo além das margens de equivalência — o
  desenho não distinguiu "não há efeito" de "há efeito e faltou n". É o cenário
  **esperado, não meramente provável**, se a variabilidade entre participantes da medida nova for
  parecida com a da LZc residualizada (desvio-padrão das AUCs ≈ 0,235,
  `resumo_teste_calibrado.md`): simulado sob efeito verdadeiro **exatamente nulo**, este é o
  destino de **94,7%** das réplicas em n = 36 — praticamente todo o complemento do erro tipo I,
  já que a equivalência é declarada em ≈ 0,04% dos casos e o resto é a rejeição espúria a 5%.
  Cair aqui, portanto, **não** é evidência de que o dado seja ambíguo — é o comportamento
  pré-declarado do desenho neste n.
- *Efeito significativo abaixo do limiar de suporte.* Direção prevista, p < 0,05, mas AUC entre 0,55
  e 0,60, ou as três condições conjuntas de SUPORTE não satisfeitas simultaneamente (por exemplo,
  AUC = 0,58 com p = 0,01 e 27 dos 36 participantes acima de 0,5). **Isto não conta como suporte** —
  o limiar de 0,60 foi estipulado antes justamente para que um efeito pequeno e significativo não
  fosse relido como confirmação depois de aparecer. Mas também não é falha, e tratá-lo como tal
  descartaria informação real.

Em qualquer dos dois, o registro declara o n necessário calculado pela análise de poder da Fase 0, e
a decisão sobre o Braço B passa a depender dele. No segundo, o registro declara adicionalmente que
o efeito observado fica **entre** o menor efeito de interesse e o limiar de detecção do desenho —
uma região que este n não resolve e que só um n maior resolveria.

**Exaustividade.** As quatro categorias acima particionam o espaço de resultados: SUPORTE exige as
três condições conjuntas; EQUIVALÊNCIA e FALSIFICAÇÃO DIRECIONAL têm critérios numéricos disjuntos
entre si e em relação a SUPORTE; INCONCLUSIVO absorve tudo o mais. Nenhum resultado possível fica
sem veredito, e nenhum veredito depende de uma regra criada depois de ver o dado.

### 6.2 Comparadores

Nenhum comparador pode converter uma falha do primário em suporte. Se a LZc normalizada por IAAFT
discriminar e a irreversibilidade não, o registro dirá que a predição deste protocolo falhou e que
uma análise de comparabilidade produziu um achado inesperado que precisa de teste próprio, em
protocolo próprio.

### 6.3 Contraste secundário W(ativo) vs N3

Mesmos limiares de §6.1, com duas exigências adicionais e conjuntas: sobreviver à FDR da família
secundária, e passar nos controles de deriva do §14.3. Se falhar apenas no controle de deriva, o
resultado é rebaixado a exploratório e reportado como tal — não descartado, não promovido.

### 6.4 Justificativa do limiar de 0,55 como menor efeito de interesse

O projeto já tratou, na prática, AUC residuais de 0,550 e 0,554 como indistinguíveis do acaso, e a
recalibração posterior mostrou que elas eram, de fato, 0,500. Declarar 0,55 como piso do que
interessa é apenas tornar explícito o critério que o projeto já aplicava implicitamente à sua própria
leitura. E o limiar de suporte em 0,60 é o que a §10 mostra ser detectável neste n sob a aproximação
adotada pelo próprio projeto — não um número escolhido por ser alcançável.

**Os dois números permanecem, e fazem trabalhos diferentes (resolução de F2, 2026-08-17).** A revisão
pré-merge mostrou que 0,55 e 0,60 haviam sido postos a carregar, juntos, uma única grandeza chamada
"poder", e que nessa leitura eles são incompatíveis. A resolução **não** altera nenhum dos dois:

| Número | Papel | Onde é usado |
|---|---|---|
| **AUC = 0,55** | Menor efeito **cientificamente** relevante (SESOI) | Âncora do Portão A de §10.3.1 e margem superior de equivalência de §6.1 |
| **AUC = 0,60** | Limiar exigido para **classificar** o resultado como SUPORTE | Condição 1 da regra conjuntiva de §6.1 |

Subir o SESOI de 0,55 para 0,60 porque 0,55 exige mais participantes seria adaptar o efeito
cientificamente relevante ao tamanho da amostra disponível — exatamente a inversão que este protocolo
existe para impedir. A decisão registrada é **preservar os dois limiares e corrigir a grandeza que os
lia**, o que está feito em §10.3.1.

**Correção de fato ao parágrafo acima, aplicada na mesma emenda.** A frase "o limiar de suporte em
0,60 é o que a §10 mostra ser detectável neste n" **não se sustenta contra a simulação**, e é
justo registrá-lo em vez de deixar os dois números lado a lado sem reconciliação. §10.2 derivou 0,60
de dz = 0,4669, mas com o desvio-padrão de referência dp = 0,2346 o dz correspondente a AUC = 0,60 é
(0,60 − 0,50)/0,2346 = **0,4263**, não 0,4669 — a tradução de §10.2 embute implicitamente uma
dispersão menor (≈ 0,214). Simulado com o Wilcoxon real em n = 36 e dp = 0,2346, o poder em
AUC = 0,60 é **0,67**, e o menor efeito da grade que alcança 80% é **AUC ≈ 0,62**. Isso **não muda
nenhuma decisão**: 0,60 permanece limiar de *classificação*, papel que não depende de ser detectável,
e o portão de poder passou a ser ancorado em 0,55 (§10.3.1). O que muda é a justificativa — 0,60 não
deve mais ser descrito como "o efeito detectável neste n", porque não é.

---

## 7. Contrato, item 6 — Validação fora da amostra, replicação independente e reanálise

O contrato exige distinguir os três, e a distinção é onde protocolos honestos costumam escorregar.

**O Braço A é reanálise do mesmo conjunto.** Mesmos 36 participantes, mesmos registros, mesmas
épocas que produziram 0,991 e 0,500. O que muda é a medida. Chamar isso de replicação seria falso, e
chamar de validação fora da amostra também: a validação cruzada de 5 partições sobre participantes
que aparece nos comparadores é fora da amostra **para o ajuste do modelo de residualização**, e nada
mais. Nenhuma frase do relatório final do Braço A pode sugerir amostra nova.

**O Braço B é primeiro teste, não replicação.** ANPHY-Sleep é amostra independente, mas a predição
1.3 nunca foi testada com medida grafo-teórica; não há o que replicar. É o primeiro teste adequado da
alegação-assinatura, e assim deve ser nomeado.

**A única replicação genuína disponível é barata e deve ser aproveitada.** Se o Braço A rodar e o
Braço B acontecer, rodar **a mesma medida de irreversibilidade** no ANPHY-Sleep custa quase nada
depois que os dados estiverem em disco, e aí sim há replicação independente de um achado próprio, em
amostra nova, com montagem e taxa de amostragem diferentes. Isso fica pré-declarado aqui para que
seja confirmatório quando acontecer, e não uma análise adicional inventada depois.

**Estatuto externo:** Maschke et al. (2025) é replicação independente **do resultado negativo de
1.2**, não deste protocolo. Continua sem citação em capítulo algum (Z9), e essa pendência é
independente desta.

---

## 8. Contrato, item 7 — Caminho de saída separado

Tudo em `scripts_para_rodar/vnext01_irreversibilidade/`, diretório novo. **Nenhum arquivo existente
é sobrescrito, movido ou apagado** — em particular, nada em `teste_calibrado/`,
`integracao_diferenciada/`, `complexidade_multivariada/`, `poder_estatistico/` ou `anestesia_1f/`.

Saídas previstas no diretório novo: `irrev_por_epoca.csv` (uma linha por época/canal, com Δ_obs,
média e desvio do ensemble, Δ_norm, e os comparadores nas mesmas épocas), `auc_por_sujeito_vnext01.csv`
(mesmo esquema de colunas de `resultados_por_sujeito.csv`, para diff direto),
`calibracao_permutacao_vnext01.csv`, `cobertura_hipnogramas.csv` (Z12), `poder_vnext01.csv` (Fase 0)
e `resumo_vnext01.md` (relatório narrativo, escrito pelo agente **depois** de o autor rodar).

Convenção de arquivos inválidos, já usada no projeto: rodadas descartadas por bug preservam o sufixo
`_INVALIDO_<motivo>` em vez de serem apagadas.

Comandos esperados, na ordem de execução:

```
python cobertura_hipnogramas.py --data-dir <pasta_cache> --out-dir saida_vnext01
python poder_vnext01.py --n-sim 2000 --out-dir saida_vnext01
python irreversibilidade_sono.py --n-subjects 41 --ordem 4 --atraso 1 --n-surrogates 99 --data-dir <pasta_cache> --out-dir saida_vnext01
python calibracao_vnext01.py --n-perm 200 --out-dir saida_vnext01
```

---

## 9. Confirmatório e exploratório, separados

| Análise | Estatuto | Família de FDR |
|---|---|---|
| Irreversibilidade normalizada, W(calmo) vs N3 | **Confirmatório primário** | isolada |
| LZc normalizada por IAAFT (Z10) | Confirmatório secundário, **com expectativa nula pré-declarada** | secundária |
| Irreversibilidade, W(ativo) vs N3 (Z12) | Confirmatório secundário, **condicionado ao critério de §3.2** | secundária |
| Irreversibilidade por canal isolado | Confirmatório secundário | secundária |
| Expoente sozinho, LZc bruta, LZc residualizada | Controles de integridade | fora de FDR |
| Irreversibilidade dos surrogates | Controle negativo | fora de FDR |
| Ordem m ∈ {3,5}, atraso τ ∈ {2,4}, grafo de visibilidade | **Exploratório** | fora de FDR |
| Ordenação dos cinco estágios por irreversibilidade | **Exploratório** | fora de FDR |
| Reajuste em 30–40 Hz (Z13 truncado) | **Exploratório, anexo** — ver §13.1 | fora de FDR |
| Braço B, medidas grafo-teóricas | **Confirmatório, em protocolo próprio** — ver §12 | a declarar |

Regra que vale para a tabela inteira: nenhuma linha exploratória pode alterar o veredito de uma linha
confirmatória, e nenhum resultado exploratório entra no manuscrito sem a etiqueta "exploratório" no
próprio texto.

---

## 10. Análise de poder a priori

### 10.1 O que é conhecido

Do próprio projeto, com o teste calibrado (`nota_calibracao_teste.md`; `CHECKLIST_pendencias.md`, Z2):
com n=36, 80% de poder exige dz entre 0,4 e 0,5, convergindo com a fórmula fechada para teste pareado
(dz ≥ 0,4669); no efeito observado (dz = −0,099) o poder foi de 16,7%; em dz ≥ 0,5, de 91%.

### 10.2 O que pode ser declarado por álgebra, e com que ressalvas

A fórmula fechada que o projeto adotou é a aproximação normal para teste pareado,
n = (z<sub>0,975</sub> + z<sub>0,80</sub>)² / dz². Ela reproduz exatamente a âncora do projeto: com
dz = 0,4669, dá n = 36. Invertida, ela dá a regra de escala abaixo — que é **consequência algébrica
da fórmula já adotada, não simulação nova**:

| dz alvo | n para 80% de poder (aprox. normal) |
|---|---|
| 0,50 | 32 |
| 0,45 | 39 |
| 0,40 | 50 |
| 0,35 | 65 |
| 0,30 | 88 |
| 0,25 | 126 |
| 0,20 | 197 |

Três ressalvas que impedem tratar esta tabela como a análise de poder do protocolo. Primeira: o teste
primário é Wilcoxon, não t — menos eficiente que o t sob normalidade e mais eficiente sob caudas
pesadas, de modo que a aproximação erra nas duas direções e só a simulação diz de quanto (foi
exatamente por isso que o projeto rodou a v3 em vez de confiar na fórmula). Segunda: **nada se sabe
sobre o tamanho de efeito da irreversibilidade em EEG humano de sono** — ninguém mediu, é o que torna
a medida original —, então qualquer dz alvo aqui é estipulação, não estimativa. Terceira: a relação
entre dz (definido sobre a diferença de médias por participante) e AUC (o estimando declarado)
depende das distribuições intra-participante e **não é fixa**; a v3 do projeto foi parametrizada em
dz e reportada em AUC porque as duas coisas foram computadas juntas, e é assim que precisa ser feito
de novo.

Um único ancoramento em AUC pode ser declarado, com sua premissa exposta: se o desvio-padrão das AUCs
por participante da medida nova for parecido com o da LZc residualizada (0,2346,
`resumo_teste_calibrado.md`), então dz = 0,4669 corresponde a um deslocamento de ≈0,11 na AUC média,
isto é, AUC ≈ 0,61. **É daí que sai o limiar de suporte de 0,60 do §6.1** — e a premissa (o
desvio-padrão se transferir de uma medida para outra) é forte e pode estar errada. Se a simulação da
Fase 0 mostrar dispersão muito diferente, o limiar de §6.1 é reajustado **antes** da execução do
Braço A e a mudança entra na §16.

### 10.3 O que o autor precisa rodar, e por quê isso é bloqueante

**Etapa 0.4 do sequenciamento: análise de poder do desenho novo, pelo teste calibrado, n_sim = 2000**,
com a mesma arquitetura da v3 e com duas exigências que a v1 não cumpriu: réplicas Monte Carlo
genuinamente reamostradas (a v1 gerava réplicas byte-idênticas e mediu ruído do teste) e poder medido
sobre o teste que será usado (a v2 mediu o poder de um teste descalibrado). As duas falhas estão
documentadas em Z2 e são o motivo de esta etapa ser explícita em vez de assumida.

A saída exigida é uma curva poder × dz para n = 36, e a curva n × dz para 80% de poder, ambas com a
tradução para AUC computada na mesma rodada. Enquanto ela não existir, **os números da tabela de
§10.2 são orientação de ordem de grandeza e não devem ser citados em nenhum texto do projeto.**

**Regra de decisão que amarra tudo:** nenhum braço confirmatório é executado sem que a análise de
poder mostre que ele responde à pergunta **nos dois sentidos** — que detecta o menor efeito de
interesse se ele existir, e que é capaz de declarar sua ausência se ele não existir. O que tornou o
teste de 1.2 não informativo não foi o resultado, foi o poder; repetir isso num dataset novo e maior
seria repetir o mesmo erro com mais gigabytes.

#### 10.3.1 Os dois portões (resolução de F2 e F8, 2026-08-17)

A revisão pré-merge mostrou que uma única grandeza chamada "poder" vinha fazendo o trabalho de três
objetos distintos. Eles passam a ser separados, com nomes próprios, e **nenhum limiar científico
muda** (ver a tabela em §6.4):

**Portão A — sensibilidade.** Probabilidade de o **teste primário pré-declarado** (Wilcoxon bilateral
de §5.2) rejeitar H₀ quando a AUC verdadeira é o SESOI de §6.4:

> P(p < 0,05 | AUC_verdadeira = 0,55) ≥ 0,80

**Portão B — capacidade de nulo informativo.** Probabilidade de satisfazer a regra de EQUIVALÊNCIA de
§6.1 (TOST a α = 0,05 contra [0,45; 0,55]) quando o efeito verdadeiro é exatamente nulo:

> P(EQUIVALÊNCIA | AUC_verdadeira = 0,50) ≥ 0,80

Um desenho só é confirmatório para esta pergunta se **os dois** forem satisfeitos. O Portão B é o que
a análise de poder convencional não captura, e é precisamente o que faltava: sem ele, um efeito
enorme poderia ser celebrado como suporte enquanto um nulo verdadeiro seria automaticamente relido
como "inconclusivo".

**O que deixa de ser chamado de poder.** A probabilidade de satisfazer as três condições conjuntas de
SUPORTE (AUC observada ≥ 0,60 **e** p < 0,05 **e** ≥ 25/36) continua sendo calculada e reportada, mas
com o estatuto correto de **característica operacional da regra de classificação** — não poder
amostral. A confusão entre as duas é o conteúdo de F2. Ela não é um defeito de estimativa: como a
regra compara a AUC *amostral* contra 0,60, essa probabilidade é ≤ 50% por construção quando a AUC
verdadeira é exatamente 0,60, e não existe n que a leve a 80% ancorada em 0,55.

**Estado dos dois portões em n = 36** (simulado antes da execução, dispersão de referência
dp = 0,2346, Beta parametrizada em (média, dp)):

| Portão | n = 36 | n para 80% |
|---|---|---|
| A — detecção em AUC = 0,55 | **0,24** | **≈ 180** |
| B — equivalência em AUC = 0,50, TOST/IC 90% | **≈ 0,00** | **≈ 190** |
| B — equivalência, formulação anterior por IC 95% | **≈ 0,00** | ≈ 232 |

**Nenhum dos dois é satisfeito em n = 36, e a conclusão registrada da Fase 0 é essa.** Os dois portões
são independentes — um mede sensibilidade, o outro capacidade de nulo — e convergem para
n ≈ 180–190, cerca de cinco vezes a amostra disponível. A convergência é informativa: o tamanho
amostral necessário deixa de ser produto de um cálculo isolado. (A álgebra de §10.2 dava n ≈ 197 para
o Portão A; a simulação do Wilcoxon real dá ≈ 180, e a diferença é o conservadorismo da aproximação
fechada, não discordância — a mesma aproximação cuja tradução dz↔AUC está corrigida ao fim de §6.4.)

**Consequência para o Braço A.** O Sleep-EDF com n = 36 **não** é amostra confirmatória para as
perguntas "há efeito ≥ 0,55?" nem "podemos excluir efeitos ≥ 0,55?". Isso não o torna inútil e não
cancela a Fase 1: ele permanece adequado para desenvolvimento e validação do gerador IAAFT, smoke
tests, calibração do estimador, o estudo de escala temporal de §5.5.1, a verificação de W(ativo) de
§3.2, a **primeira estimativa da dispersão por participante da irreversibilidade** — que hoje é
desconhecida e é o insumo que falta a todo este cálculo — e um efeito **piloto**. O que muda é o
estatuto do braço, não sua execução. A etapa 0.6 deixa de ser uma tentativa de descobrir se n = 36
passa, e passa a cumprir a função correta: quantificar formalmente quanto n = 36 não alcança, e qual
n seria necessário para um teste bilateralmente informativo.

---

## 11. Mediador ou confundidor: como este protocolo se posiciona

A `nota_estado_da_arte_1f.md` (§3) registra que a distinção entre mediador e confundidor não tem
discussão publicada em EEG de consciência — nem em Maschke 2025, nem em Höhn 2024, nem no guideline
de Ping et al. (2025) — e que nenhum teste estatístico separa os dois papéis com dados
observacionais. É lacuna genuína e oportunidade, com o custo de não haver literatura para citar.

A posição deste protocolo é deliberadamente modesta e, por isso, defensável: **ele não resolve a
questão; ele constrói um desfecho primário que não depende dela.**

Se o estado altera o balanço excitação/inibição, que altera o expoente aperiódico, que altera a
complexidade medida, então o expoente é mediador e residualizar é sobrecontrole — e todo o resultado
de 1.2 é ambíguo entre "não há nada além do espectro" e "removemos o caminho causal junto com o
ruído". Nenhuma quantidade de dado observacional desfaz essa ambiguidade, porque as duas hipóteses
implicam a mesma correlação parcial.

A irreversibilidade normalizada muda a pergunta em vez de tentar responder à antiga. Ela não
condiciona no expoente: preserva-o integralmente no nulo. Sob **qualquer** dos dois papéis causais,
uma descrição linear-gaussiana estacionária do sinal — mediadora ou confundidora — prevê
irreversibilidade normalizada nula. Um resultado positivo é excedente sobre o espectro seja o
espectro o que for na cadeia causal; um resultado nulo é evidência de redundância informacional
igualmente indiferente ao papel causal. **Essa indiferença é a contribuição metodológica do
protocolo**, e é uma contribuição menor e mais segura do que "resolver o dilema": é mostrar que
existe um estimando para o qual o dilema não precisa ser resolvido.

Duas honestidades adicionais. A primeira: essa imunidade vale exatamente na medida em que a premissa
linear-gaussiana-estacionária captura o que se quer dizer por "explicação espectral" — e a
estacionariedade é a premissa frágil (§14.1). A segunda: para a anestesia, onde a
`nota_calibracao_teste.md` registra que o 1/f é plausivelmente mediador, o mesmo argumento se
aplicaria e a mesma medida seria informativa; isso fica fora deste protocolo, e a razão está em §13.3.

---

## 12. A decisão sobre dataset

### 12.1 A decisão

**Recomendado: ANPHY-Sleep (OSF R26FH) como Braço B, em protocolo próprio (VNext-02), condicionado a
três verificações e não iniciado antes da Fase 1.** E, previamente a ele, **Farnes 2020 (Dryad, CC0,
62 canais, 934 MB) como dataset-piloto de desenvolvimento do pipeline grafo-teórico** — não como
dataset de teste.

### 12.2 Por que um dataset multicanal é necessário — e para qual pergunta exatamente

Não para refazer 1.2. Isso está replicado em 256 canais e 225 pacientes, e refazê-lo seria gastar
86 GB para chegar onde Maschke et al. (2025) já chegaram.

É para 1.3, e a razão é categórica, não quantitativa: a alegação de integração diferenciada afirma
algo sobre a **organização espacial** de integração e segregação. Dois eletrodos não expressam essa
proposição — não fracamente, não parcialmente: não a expressam. Informação mútua entre Fpz-Cz e
Pz-Oz não tem como distinguir "rede integrada e segregada" de "duas derivações correlacionadas",
porque com dois nós não existe módulo, não existe caminho alternativo, não existe eficiência global
distinta de conectividade média. A falha de 1.3 é, até aqui, a falha de um proxy que o próprio script
declarava insuficiente no cabeçalho.

### 12.3 Por que ANPHY-Sleep, entre os candidatos da §7 da nota

| Dataset | Serve para 1.3? | Decisão |
|---|---|---|
| **ANPHY-Sleep** (OSF R26FH, 83 eletrodos 10-10, 1000 Hz, noite inteira, ~86 GB, CC BY-NC-ND) | Sim: única opção aberta com sono de noite inteira e densidade que sustenta medida de rede | **Recomendado** |
| **Farnes 2020** (Dryad, cetamina, 62 canais, 934 MB, CC0) | Densidade suficiente, mas o paradigma é cetamina, não sono | **Piloto de pipeline**, e o dataset natural para a predição B.3 num protocolo futuro |
| Zenodo 806176 (Colombo 2019: propofol, xenônio, cetamina) | Acesso restrito; paradigma farmacológico, onde o 1/f é plausivelmente mediador | Preterido para 1.3 |
| OpenNeuro ds005620 (Oslo, 65 canais, TMS-EEG + relato, 83 GB) | Rótulos de relato não estão no BIDS; anestesia, não sono | Preterido; valioso para outra pergunta |
| DOD-H (Dreem, 5 scorers por registro) | Contagem de canais não verificada; valor está na confiabilidade do rótulo | Preterido para 1.3; é o dataset certo para medir ruído de estagiamento (§14.4) |
| VitalDB | 2 canais | Excluído por construção |

O custo é real e deve constar: ~86 GB de download, um pipeline de pré-processamento inteiramente novo
(montagem 10-10, referência, rejeição de artefato, ICA, possivelmente reconstrução de fonte),
reamostragem de 1000 Hz para uma taxa comparável, e um conjunto de escolhas de conectividade que o
projeto nunca fez. É a maior expansão técnica da história do projeto, e é por isso que ela não começa
antes da Fase 1 e não começa sem as três verificações abaixo.

### 12.4 As três verificações que condicionam o Braço B

1. **n de participantes do ANPHY-Sleep**, que a `nota_estado_da_arte_1f.md` não informa. Se o n
   estiver abaixo do exigido pela análise de poder da Fase 0 para o menor efeito de interesse, o
   Braço B **não** procede como confirmatório — seria repetir o erro de 1.2 com mais canais.
2. **Licença.** CC BY-NC-ND: o uso acadêmico não comercial é claro, mas a cláusula ND ("no
   derivatives") precisa ser lida antes de qualquer redistribuição de dado derivado. Publicar
   estatísticas é uma coisa; redistribuir versões pré-processadas é outra.
3. **Conteúdo real:** montagem, presença de EOG/EMG, e se as anotações de estágio seguem AASM. Todos
   os atributos da tabela da §7 da nota foram reportados por agentes de busca a partir de páginas
   oficiais e **não reconferidos** — inclusive os 83 eletrodos e os 86 GB.

### 12.5 Por que a Fase 1 vem antes, e por que não é um portão de sucesso

A prioridade da Fase 1 não é "se der certo, seguimos". Se a irreversibilidade der nulo em 2 canais, o
Braço B **continua justificado**, porque medida de rede e medida de assimetria temporal testam
proposições diferentes e a segunda não substitui a primeira.

A prioridade é de outra ordem, e é dupla: a Fase 1 constrói e valida, num dataset já em disco e com
linha de base conhecida, **exatamente a maquinaria de surrogate e de teste calibrado de que o Braço B
vai precisar** — e a Fase 0 produz o número de poder sem o qual o Braço B não pode ser dimensionado.
Começar pelos 86 GB seria construir o instrumento e o experimento ao mesmo tempo, sem controle
positivo disponível.

---

## 13. O que ficou de fora, e por quê

### 13.1 Z13 (reajuste em 30–45 Hz) sai do desenho confirmatório

Três razões, em ordem de força.

**Primeira, e decisiva: a banda não está disponível no sinal tal como o pipeline atual o processa.**
O pipeline aplica filtro passa-banda de 0,5–40 Hz (`analise_sono_v2.py`;
`integracao_diferenciada_1f.py`). Um ajuste em 30–45 Hz ajustaria 30–40 Hz de sinal real mais 40–45 Hz
de rolloff de filtro — não é a banda de Höhn et al. (2024), é uma versão truncada dela, e o que se
mediria acima de 40 Hz seria a resposta do filtro. Qualquer reajuste possível aqui é 30–40 Hz, e isso

> **Precisão sobre a causa.** É o filtro, não a taxa de amostragem. O Sleep-EDF é amostrado a 100 Hz,
> o que põe a frequência de Nyquist em 50 Hz — 40–45 Hz é, em princípio, representável no sinal
> bruto. Uma versão anterior desta seção atribuía a exclusão à amostragem e afirmava que "a banda não
> existe neste dataset"; isso está errado e foi corrigido. A consequência prática não muda — sob este
> pipeline a banda não está disponível —, mas a diferença importa para quem quiser retomar Z13: seria
> preciso construir um pipeline com filtro mais alto e **verificar também o filtro anti-aliasing de
> aquisição do próprio registro**, que pode ou não preservar 40–45 Hz de forma utilizável. Isso é
> trabalho de protocolo separado, não uma variante deste.
precisa ser dito com essas palavras se ele for feito.

**Segunda: é exatamente a banda do artefato.** 30–40 Hz de EEG de escalpo é onde vive a contaminação
por EMG, e Halder et al. (2026) mostram que essa contaminação derruba inclinação e LZc juntas — sob
bloqueio neuromuscular, a LZc classificou 100% dos segmentos acordado-paralisado como
"não-consciente". Um resultado favorável em 30–40 Hz teria uma explicação alternativa banal
esperando por ele.

**Terceira: os próprios autores desqualificam o resgate.** Höhn et al. ressalvam que a complexidade
em banda estreita "não produziu resultados particularmente significativos".

Além disso, Z13 é um teste de robustez de uma residualização que este protocolo **rebaixa a papel
secundário** (§4). Pré-registrar um teste confirmatório sobre a sensibilidade de banda de um controle
que deixou de ser o controle primário seria inflar o protocolo sem aumentar o que ele decide.

**Onde Z13 fica:** anexo exploratório, rodável a custo quase zero depois do Braço A, reportado com as
três ressalvas acima no próprio texto, e sem poder de alterar veredito algum. Ele não deixa de ser
feito; deixa de ser pré-registrado como se pudesse decidir alguma coisa.

### 13.2 O que **não** ficou de fora, contra a expectativa

Z10 e Z12 poderiam parecer candidatos a corte — o primeiro por ter resultado previsível, o segundo
por ser checagem de dado e não teste de hipótese. Ambos permanecem, por razões estruturais e não de
completude de lista. **Z10 não é um controle alternativo neste desenho: é o gerador do nulo sem o
qual a métrica de Z11 não tem zero definido** (§5.1). **Z12 não é um teste: é definição de amostra**,
e definição de amostra é a primeira coisa que um pré-registro tem de fixar (§3.2). As quatro
pendências não foram forçadas num desenho; três delas se organizaram numa dependência real, e a
quarta saiu.

### 13.3 Anestesia fica fora deste protocolo

A mesma medida de irreversibilidade seria informativa no dataset de propofol, e o argumento de
imunidade ao papel causal do 1/f é ainda mais pertinente lá, onde a
`nota_calibracao_teste.md` registra que o expoente é plausivelmente mediador. Fica fora por três
razões: são 20 participantes contra 36, num desenho cuja limitação já demonstrada é poder; o achado
de anestesia tem uma pendência de **reporte** ainda não resolvida (a leitura de supressão, §2 da nota
de estado da arte) que precisa entrar no manuscrito antes de qualquer teste novo sobre o mesmo dado;
e misturar dois paradigmas num só pré-registro dilui a família de FDR sem necessidade.

### 13.4 Refazer 1.2 em dataset maior fica fora, definitivamente

Já replicado com 100× mais canais e n 6× maior. A entrada 1.2 do `registro_falsificabilidade.md`
permanece ❌ FALHOU e este protocolo não a reabre; o que ele abre é uma pergunta adjacente e uma
medida diferente.

---

## 14. Ameaças pré-declaradas ao desenho

Declaradas antes porque uma ameaça nomeada depois do resultado vira desculpa.

### 14.1 Não estacionariedade — a ameaça principal

O IAAFT randomiza fases globalmente e produz um surrogate estacionário. Um sinal **linear mas não
estacionário** dentro da época pode, portanto, exibir irreversibilidade aparente contra seu próprio
surrogate, sem nenhuma dinâmica não linear envolvida. Isso não é hipotético em sono: épocas de 30 s
atravessam fusos, complexos K e transições de microestado.

Mitigação pré-declarada: reportar a irreversibilidade também em subépocas de 5 s agregadas por época
(análise de sensibilidade), sob a lógica de que uma janela mais curta é mais plausivelmente
estacionária; e reportar um diagnóstico de não estacionariedade por época, com a correlação entre ele
e Δ_norm. Se essa correlação for alta, o resultado primário — positivo ou negativo — é reportado com
essa ressalva em destaque. **Nenhuma dessas análises pode converter um nulo em suporte.**

### 14.2 Assimetria de forma de onda lenta

Ondas lentas de N3 têm forma acentuadamente assimétrica (descida íngreme, subida lenta), e assimetria
de forma de onda **é** uma forma de irreversibilidade temporal — genuína, e não artefatual. Se o
resultado for AUC < 0,5 (N3 mais irreversível que W), a explicação mais provável é essa, e ela não
tem nada a ver com consciência. Está registrada aqui, antes, para que não seja apresentada depois nem
como surpresa nem como resgate. Diagnóstico exploratório previsto: comparar a irreversibilidade em
épocas de N3 estratificadas por amplitude de onda lenta.

### 14.3 Deriva temporal no contraste W(ativo) vs N3

Vigília diurna e sono profundo estão separados por horas na mesma gravação. Controle pré-declarado:
repetir o contraste restringindo às épocas de vigília **mais próximas** do período de sono e comparar
o tamanho de efeito com o do contraste completo; e reportar a correlação entre Δ_norm e o tempo
decorrido desde o início da gravação, dentro de participante. Se o efeito escalar com o tempo
decorrido tanto quanto com o estágio, o braço é declarado não interpretável.

### 14.4 Ruído de rótulo

Todo o desenho depende de hipnogramas de escorador único no Sleep-EDF. Concordância entre escoradores
é imperfeita, sobretudo em N1 e REM — menos crítico para W-vs-N3, que é o par mais fácil, mas não
nulo. Não há mitigação dentro deste dataset; fica registrado como limite, e DOD-H (5 escoradores
independentes por registro) é nomeado como o caminho para quantificá-lo, em outro protocolo.

### 14.5 Custo computacional subestimado

O ensemble de surrogates multiplica o custo por duas ordens de grandeza em relação a qualquer rodada
anterior do projeto. Mitigação: smoke test obrigatória com `--n-subjects 3` antes da amostra cheia, e
redução do ensemble decidida **antes** de ver resultado, com registro na §16.

---

## 15. Sequenciamento faseado

Convenção do `CHECKLIST_pendencias.md`: 🤖 = agente escreve · 🧑 = autor executa/verifica.

### Fase 0 — Pré-execução (nada aqui produz teste de hipótese)

- [ ] **0.1** Congelar este protocolo em commit próprio, antes de qualquer script. 🤖
- [x] **0.2** **Verificação bloqueante de referências — concluída.** **Weiss (1975) está verificado** — conferido
  contra o registro do Cambridge Core em 2026-08-13: *J Appl Probab* 12(4):831–836, DOI
  10.2307/3212735, com a direção necessária confirmada e a recíproca também (ver a caixa em §2.3). A
  premissa central do protocolo, portanto, **se sustenta**, e a Fase 1 não está mais bloqueada por
  ela. Duas ressalvas ficam registradas: o texto integral não estava acessível na consulta, então as
  condições técnicas exatas (estacionariedade, causalidade, inovações iid) não foram lidas na fonte
  primária; e a verificação obrigou a acrescentar uma quinta origem possível de um positivo à §2.1.1
  (processo linear não gaussiano).
  **Schreiber & Schmitz (1996) está verificado** — *Phys Rev Lett* 77(4):635–638, DOI
  10.1103/PhysRevLett.77.635, PMID 10062864. É a segunda peça **estrutural** do protocolo, e ela
  fecha o argumento: o nulo que os autores propõem é o de *rescalings não lineares de um processo
  linear gaussiano*, exatamente a classe que Weiss identifica como reversível (caixa em §4). Uma
  limitação entrou como ameaça pré-declarada: o algoritmo é iterativo com critério de parada, resta
  discrepância espectral residual, e o smoke test passa a ter de reportá-la.
  **de la Fuente et al. (2023) e Camassa et al. (2024) estão verificados, e foram rebaixados de
  bloqueantes a contexto.** Os estimadores foram identificados (§5.5.1): rede neural convolucional
  sobre componentes principais no primeiro, assimetria de covariância defasada do arcabouço INSIDEOUT
  no segundo. Nenhum dos dois é da família ordinal deste protocolo, e o de Camassa nem é univariado.
  A transferência de evidência está classificada como **apenas conceitual** — e essa é justamente a
  razão pela qual eles **não bloqueiam a etapa 0.6**: uma referência que não pode ancorar tamanho de
  efeito não pode, por definição, bloquear uma análise de poder que não importa tamanho de efeito
  dela. A §10.3 já exige que a curva de poder seja construída sobre a variabilidade observada nos
  próprios 36 participantes, não sobre expectativa importada. O que essas duas referências passam a
  sustentar está registrado em §5.5.1: direção, não magnitude — e um risco de escala temporal que a
  verificação expôs e que mudou a lista de sensibilidade de §5.5. ✅ 🤖
- [x] **0.3** ✅ **Escrito** (`scripts_para_rodar/vnext01_irreversibilidade/`, congelado antes da execução). Escrever `cobertura_hipnogramas.py` (Z12): distribuição das descrições de anotação por
  registro, duração total coberta, e quantas épocas de vigília existem fora da janela de ±30 min. 🤖
- [ ] **0.4** Rodar 0.3 e registrar o resultado contra o critério de §3.2 — **antes** de qualquer
  métrica. 🧑
- [x] **0.5** ✅ **Escrito** (`scripts_para_rodar/vnext01_irreversibilidade/`, congelado antes da execução; varredura de dispersão com faixa empírica derivada mecanicamente, `reference_power_pass` e `robust_power_pass` separados). Escrever `poder_vnext01.py` (§10.3), com réplicas genuinamente reamostradas e sobre o
  teste calibrado. 🤖
- [ ] **0.6** Rodar 0.5 (n_sim=2000) e registrar a curva poder × dz, a tradução para AUC e os **dois
  portões de §10.3.1** — Portão A (detecção no SESOI) e Portão B (equivalência sob nulo) — cada um
  com o n necessário para 80%. Os limiares de §6.1 e §6.4 **já foram decididos e não se reabrem**
  aqui: a emenda de 2026-08-17 preservou 0,55 e 0,60 e resolveu F2 pela separação das grandezas, e a
  regra de equivalência já é TOST/IC 90%. A função desta etapa passa a ser **quantificar o quanto
  n=36 não alcança**, não descobrir se passa — a resposta pré-simulada é que não passa em nenhum dos
  dois portões, e a etapa a confirma com a instrumentação congelada e a documenta. 🧑

### Fase 1 — Braço A, Sleep-EDF (Z10 + Z11)

- [ ] **1.1** Escrever `irreversibilidade_sono.py`: métrica ordinal de irreversibilidade, ensemble
  IAAFT, comparadores (LZc bruta, LZc residualizada fora da amostra, LZc normalizada por IAAFT,
  expoente sozinho), controle negativo sobre os surrogates, saída por época. 🤖
- [ ] **1.2** Escrever `calibracao_vnext01.py`: permutação de rótulos dentro de participante para o
  desenho novo, janela de aceitação 2,0%–8,5%. 🤖
- [ ] **1.3** Rodar 1.1 com `--n-subjects 3` (smoke test) e reportar tempo de parede. 🧑
- [ ] **1.4** Decidir, se necessário, redução do ensemble — antes de ver resultado. 🧑 + 🤖
- [ ] **1.5** Rodar a amostra cheia e, em seguida, a calibração de 1.2. 🧑
- [ ] **1.6** Verificar os controles de integridade (§5.4) **antes** de olhar o desfecho primário. 🧑
- [ ] **1.7** Interpretar contra os critérios de §6, sem reabrir nenhum deles; escrever
  `resumo_vnext01.md`. 🤖
- [ ] **1.8** Atualizar `registro_falsificabilidade.md` com a nova entrada de predição (1.6, a
  numerar), qualquer que seja o resultado, e o `CHECKLIST_pendencias.md` fechando Z10, Z11 e Z12. 🤖

### Fase 2 — Decisão sobre o Braço B

- [ ] **2.1** Verificar as três condições de §12.4 (n, licença, conteúdo real). 🧑
- [ ] **2.2** Baixar Farnes 2020 (934 MB, CC0) e desenvolver o pipeline grafo-teórico nele — nunca no
  dataset confirmatório. 🧑 (download) + 🤖 (pipeline)
- [ ] **2.3** Escrever o **PROTOCOLO_VNext_02**, com os mesmos sete itens do contrato, o índice de
  integração×segregação e o comparador adversarial de sincronia bruta declarados antes, e o n
  exigido pela análise de poder de 0.6. 🤖
- [ ] **2.4** Decisão do autor sobre custo/benefício dos ~86 GB, com a Fase 1 e a análise de poder já
  na mesa. 🧑

### Anexo exploratório (a qualquer momento após 1.5, sem poder de mudar veredito)

- [ ] **A.1** Reajuste em 30–40 Hz (Z13 truncado), com as três ressalvas de §13.1 no próprio
  relatório. 🤖 escreve · 🧑 roda

---

## 16. Registro de emendas

| Data | Item alterado | Antes / depois de ver resultado da fase? | Motivo |
|---|---|---|---|
| 2026-08-17 | §6.1 (regra de EQUIVALÊNCIA e primeiro cenário de INCONCLUSIVO), §6.4 (tabela dos dois números), §10.3 (nova §10.3.1, dois portões), §15 etapa 0.6 | **Antes** — nenhuma etapa 0.4 ou 0.6 executada, nenhum desfecho calculado | **F2 resolvida e F8 registrada.** **F2 — a grandeza estava errada, não os limiares.** §6.4 fixa o SESOI em AUC = 0,55, §10.2 deriva o limiar de suporte 0,60 do dz que já dá 80% de poder em n=36 (isto é, 0,60 é aproximadamente o MDE), e §10.3 exigia 80% de poder no SESOI: os três não podiam valer juntos porque uma única grandeza chamada "poder" fazia o trabalho de três objetos. **Decisão: preservar 0,55 e preservar 0,60**, que cumprem funções diferentes (§6.4), e separar as grandezas. O portão de poder passa a ser P(Wilcoxon rejeita \| AUC = 0,55) ≥ 0,80 — o teste primário real, no SESOI. A probabilidade de satisfazer as três condições conjuntas de SUPORTE continua reportada, com o estatuto de **característica operacional da regra de classificação**, não de poder amostral. Subir o SESOI para 0,60 porque 0,55 exige mais participantes seria adaptar o efeito cientificamente relevante ao n disponível, e foi explicitamente rejeitado. **F8 — o ramo de EQUIVALÊNCIA é operacionalmente inacessível em n=36.** Simulada antes da execução sob o caso mais favorável (AUC verdadeira = 0,500), a probabilidade de satisfazer a regra pré-declarada — IC 95% inteiramente contido em [0,45; 0,55] — é 0,395 para dp = 0,1173; 0,004 para dp = 0,1760; e ≈ 0 para dp ≥ 0,2346, incluindo o cenário de referência. Um efeito genuinamente nulo seria classificado como INCONCLUSIVO **por construção**, e a frase de §6.1 "resultado negativo é dado" não era realizável neste n. A regra passou a **TOST a α = 0,05 / IC 90%**, que é a formulação convencional de equivalência — as margens [0,45; 0,55] **não** mudaram, e a troca não torna o ramo alcançável (n ≈ 190 contra n ≈ 232). **Consequência conjunta:** os dois portões são independentes e convergem para **n ≈ 180–190**, ~5× a amostra disponível; n=36 não é amostra confirmatória para este desfecho, e a etapa 0.6 passa a quantificar o quanto falta em vez de testar se passa. Achados obtidos antes de qualquer execução do desfecho: são propriedade do desenho, não resultado científico |
| 2026-08-17 | Instrumentação da Fase 0 (`poder_vnext01.py`, `cobertura_hipnogramas.py`, `testes_instrumentacao.py`); nenhuma seção do protocolo alterada | **Antes** — nenhuma etapa 0.4 ou 0.6 executada | Revisão pré-merge da `fase0-instrumentacao`, registrada em `embasamento/revisao_fase0_pre_merge.md`. Dois defeitos que teriam invertido a leitura da etapa 0.6: **(F1)** o campo de decisão usava `.any()` sobre todos os efeitos ≥ 0,60, de modo que o maior efeito da grade decidia e `reference_power_pass`/`robust_power_pass` saíam `True` para qualquer dispersão — passou a ser avaliado na âncora declarada de §6.4, que é o efeito que §10.3 nomeia; **(F3)** o gerador truncava uma normal por reamostragem e não entregava os momentos declarados (a célula rotulada AUC=0,60 simulava média 0,582; dp 11–24% abaixo do alvo), e para boa parte da grade o par (média, dp) é inviável para **qualquer** normal truncada em [0,1] — trocado por Beta parametrizada em (média, dp), com momentos realizados reportados e viabilidade checada. Mais três: **(F4)** a faixa "empírica" de dispersão era mais estreita que o próprio fallback pré-declarado e passou a ser a união das duas famílias já congeladas, sem número novo; **(F5)** a checagem de Z12 contava os 39 registros do cache contra o critério "30 dos 36" e agora deriva a coorte pela mesma regra de exclusão do projeto, sem emitir veredito se o tamanho não conferir; **(F6)** o indicador de cobertura do hipnograma usava a duração anotada, que inclui `Sleep stage ?` e o tornava verdadeiro por construção. Nenhuma correção foi motivada por uma saída observada, porque nenhum dos dois scripts havia rodado sobre os dados-alvo |
| 2026-08-13 | §6.1 (critérios de decisão), §13.1 (justificativa de Z13), §2.1.1 (nova), estatuto do cabeçalho | **Antes** — nenhuma fase executada | Revisão da PR #2. Os critérios não eram exaustivos (um efeito significativo abaixo do limiar de suporte ficava sem veredito); a exclusão de Z13 era atribuída à amostragem quando a causa é o filtro do pipeline (Nyquist a 100 Hz é 50 Hz); a linguagem de inferência deslizava de "incompatível com o nulo IAAFT" para "não linearidade"; e o estatuto de "pré-registrado" foi rebaixado a protocolo prospectivo congelado |
| 2026-08-13 | §4 (caixa IAAFT), §5.5 (faixa de τ estendida), §5.5.1 (nova), §15 etapa 0.2, §17 (tabela) | **Antes** — nenhuma fase executada | Etapa 0.2 concluída (AA7b). Os estimadores de de la Fuente e Camassa foram identificados e **não são da família ordinal deste protocolo**: a transferência caiu para evidência conceitual, e as duas referências deixaram de bloquear a etapa 0.6. A verificação expôs um risco de escala temporal não registrado — Camassa mede com Δt=0,75 s, o primário aqui usa τ=0,01 s —, e por isso a lista de sensibilidade de §5.5 foi estendida para τ ∈ {25, 50, 75} |
| 2026-08-13 | §2.3 (caixa de verificação), §2.1.1 (quarta → quinta origem), §15 etapa 0.2, §17 (tabela) | **Antes** — nenhuma fase executada | Etapa 0.2 (AA7) executada em parte. Weiss (1975) verificado contra o Cambridge Core, DOI 10.2307/3212735: a premissa se sustenta e a Fase 1 deixa de estar bloqueada por ela. A verificação obrigou a **acrescentar uma origem possível de um positivo** — processo linear não gaussiano —, que faltava na §2.1.1; e permitiu registrar que transformações não lineares estáticas de processos lineares gaussianos também são reversíveis, o que estreita o alinhamento entre a medida e o nulo IAAFT |

> **Nota sobre estas emendas.** Todas são anteriores a qualquer execução e a qualquer resultado,
> e portanto **não rebaixam nenhuma análise de confirmatória a exploratória** — a cláusula da regra de
> congelamento que produziria esse rebaixamento se aplica a emendas posteriores à visualização de
> resultados. A segunda é o caso que a própria regra existe para tornar visível: uma verificação
> bloqueante da Fase 0 mudou o conteúdo do protocolo, e a mudança está registrada com data e motivo
> em vez de silenciosamente incorporada.

---

## 17. Estatuto de verificação das afirmações deste protocolo

| Afirmação | Estatuto |
|---|---|
| Números da linha de base (AUC 0,991 / 0,500; dz −0,099; poder 16,7%; n=36; 8.923 vs 3.972 épocas; desvio-padrão 0,2346; erro tipo I 7,0%) | ✅ Lidos de arquivos do projeto, com fonte citada em cada caso |
| Convenções de pipeline (2 canais, 100 Hz, 30 s, filtro 0,5–40 Hz, `FIT_FREQ_RANGE` 1–40 Hz, corte ±30 min) | ✅ Conferidos no código |
| Inclusão/exclusão que leva 41 → 39 → 36 | ✅ Documentada no `CHECKLIST_pendencias.md` |
| **Weiss 1975** — a premissa matemática de §2.3 | ✅ **Verificada em 2026-08-13** contra o registro do Cambridge Core: *J Appl Probab* 12(4):831–836, DOI 10.2307/3212735. Direção necessária e recíproca confirmadas. Ressalva: texto integral inacessível na consulta, condições técnicas exatas não lidas na fonte primária |
| **Maschke 2025** — a replicação independente | ✅ **Verificada em 2026-08-13** contra a página do periódico (Oxford Academic); ver `nota_estado_da_arte_1f.md`, §1 |
| **Schreiber & Schmitz 1996** — o nulo IAAFT de §4 | ✅ **Verificada em 2026-08-13** no PubMed (PMID 10062864): *Phys Rev Lett* 77(4):635–638. Nulo confirmado como *rescalings não lineares de processo linear gaussiano*, fechando o argumento com Weiss |
| **de la Fuente 2023 e Camassa 2024** — os precedentes animais | ✅ **Verificadas em 2026-08-13**; estimadores identificados em §5.5.1. Transferência classificada como **apenas conceitual** — não ancoram tamanho de efeito |
| **Maschke 2025, Westfall & Yarkoni 2016, Berger 2017, Widmann 2024/2025, Halder 2026, Helfrich 2026** | ✅ **Verificadas em 2026-08-17** contra PubMed/PMC e a página do periódico, identificador por identificador (`embasamento/revisao_fase0_pre_merge.md`, §3). Nenhuma autoria errada, nenhum DOI quebrado, nenhum número inventado. Maschke conferida contra o **texto integral** (PMC12448740): *r*(197)=0,86 e *r*(197)=0,24 sob surrogates de fase estão no corpo. Precisões que a verificação acrescentou: Halder tem **n=6** voluntários; Maschke retém **185,09 ± 8,77** canais (não "no máximo 195"); Widmann 134(2) é de **fevereiro de 2025** (online 2024-11-28); Helfrich é **PNAS 123(21):e2514098123** e o primeiro autor é **Janna D.** Helfrich. Duas cláusulas são inferência do projeto e ficam marcadas como tal: o comportamento **conjunto** de inclinação e LZc em Halder, e "enfraquece o expoente como marcador puro" em Helfrich. **Segue faltando a reverificação pelo autor** (Z8), e nenhuma entra em `capitulos/17_referencias.md` antes disso |
| Demais referências externas (Schartner 2017, Toker 2022, Höhn 2024) | ⚠️ Verificadas por agentes, **não reverificadas pelo autor** (Z8). Nenhuma entra em `capitulos/17_referencias.md` antes disso |
| Atributos do ANPHY-Sleep e demais datasets (canais, tamanho, licença) | ⚠️ Reportados por agentes a partir de páginas oficiais; não reconferidos — condição 3 de §12.4 |
| Estimador de irreversibilidade usado por de la Fuente 2023 e Camassa 2024 | ✅ **Verificado em 2026-08-13** (§5.5.1): CNN sobre componentes principais e assimetria de covariância defasada (INSIDEOUT), respectivamente. **Nenhum dos dois é da família ordinal deste protocolo** — as referências valem como evidência conceitual e direcional, não como calibração de expectativa |
| Cobertura de ~20 h dos hipnogramas do Sleep-EDF | ✅ **Medida em 2026-08-17**, e a resposta é positiva com folga: a duração **pontuada** iguala a duração do PSG (mediana 100%, mínimo 96,4% dos 39 registros), a primeira anotação pontuada é um bloco de vigília de 7,5–8,8 h, e há **923 a 2052 épocas** de W anotadas fora da janela de corte (mediana 1669) contra um critério de §3.2 de ≥30. O corte atual usa 38,5% do registro (mediana). ⚠️ A medição foi feita por agente como **smoke test do código**, sem rejeição de artefato: é um limite superior, e a **etapa 0.4 continua sendo do autor** — o artefato de registro é o que ele rodar |
| Tabela de escala n × dz da §10.2 | ⚠️ Álgebra da fórmula fechada já adotada pelo projeto, **não simulação**; substituída pela saída da etapa 0.6 |
| Todos os limiares numéricos de §3.2, §5.1 e §6 | ⚠️ **Estipulações de desenho**, fixadas antes da execução; justificadas, não derivadas |
