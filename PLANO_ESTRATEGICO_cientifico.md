> ## ⚠️ DOCUMENTO CONGELADO — REGISTRO HISTÓRICO, NÃO É UM PLANO ATIVO
>
> Criado em **2026-08-05**. As frentes A a G que ele define foram executadas e encerradas entre **2026-08-06 e 2026-08-07** (registro granular em `CHECKLIST_pendencias.md`, Blocos L a R). Desde então o documento é preservado **na íntegra e sem atualização**, como registro de por que o projeto tomou o rumo que tomou. Nenhum agente deve tratá-lo como instrução vigente.
>
> **Os números, diagnósticos e prioridades abaixo refletem 2026-08-05 e não descrevem o estado atual do projeto.** Vários foram superados pelos resultados das próprias frentes que este plano encomendou — o diagnóstico da §1, em particular, descreve a discriminação de sono *antes* do controle por inclinação espectral 1/f que a Frente C viria a impor e que derrubou a leitura mecanística.
>
> **Onde está o estado atual:**
> - `README.md` (raiz) — visão geral do que está e do que não está demonstrado;
> - `CHECKLIST_pendencias.md` — histórico granular, bloco a bloco, de tudo que foi executado;
> - `embasamento/registro_falsificabilidade.md` — estatuto empírico de cada predição, uma a uma.
>
> **Regras específicas deste documento que estão revogadas — não seguir:**
> - **§0.2, "Git: branch, commits pequenos e descritivos, sem push."** Revogada como proibição. O repositório hoje tem remote `origin` no GitHub; `main` e `revisao-2026-08` rastreiam origin, estão ambos publicados, e há merges regulares de `revisao-2026-08` para `main`. A convenção vigente é a do `AGENTS.md`: não fazer push sem pedido explícito do autor — o que é diferente de nunca fazer.
> - **§8, "PRÓXIMO PASSO IMEDIATO".** Revogada. Manda começar pela Frente A, concluída em 2026-08-06 (`embasamento/mapa_evidencias_pilares.md` e `embasamento/SINTESE_pilares.md`). Não há próximo passo a extrair deste documento.
> - **§0.1, separação entre escrever e executar cálculo.** Não revogada, mas flexibilizada pelo autor: vale para cálculos pesados o bastante para justificar, não como regra geral (`CHECKLIST_pendencias.md`, seção "O que agora depende de você", item 11).
>
> As regras de honestidade científica (§2 e §7 — verificar toda referência, declarar contra-evidência, reportar resultados negativos, não apresentar simulação sintética como validação empírica) continuam vigentes como cultura do projeto.

# Plano Estratégico — Fortalecimento do Embasamento Científico
## Projeto *Conscience* ("Consciência como Regime Integrado")

Documento de estratégia para as próximas fases. Público-alvo: **Claude Code e Codex** (e o autor). Vive na raiz do repositório para que qualquer agente o leia antes de trabalhar.

Data de criação: 2026-08-05 · Branch de trabalho: `revisao-2026-08` (sem push). — **⚠️ "sem push" revogado, mesma correção da §0.2 abaixo: `revisao-2026-08` e `main` estão publicados em `origin`.**

---

## 0. GOVERNANÇA — leia antes de qualquer tarefa

### 0.1 REGRA CRÍTICA — separação entre escrever cálculo e executar cálculo
> **Os agentes (Claude Code ou Codex) NÃO executam cálculos, simulações, análises numéricas, métricas de EEG, estatística ou ajustes de modelo.**
> **Os agentes APENAS escrevem os scripts Python** — com dependências declaradas, instruções de execução e o formato de saída esperado. **Quem roda os scripts é o autor, localmente, no VS Code**, e devolve os resultados para o agente interpretar.
>
> Isso vale para tudo que produz números: rodar os modelos V1–V5, simulações, cálculo de LZc / entropia de permutação / integração-segregação, testes estatísticos, calibração, análises de sensibilidade.
>
> **Não é cálculo** (e portanto é permitido ao agente): busca na web, leitura de literatura, redação de texto, desenho de experimentos, escrita e revisão de código, revisão crítica. A busca online ampla por múltiplos agentes é encorajada.
>
> Todo entregável computacional segue o padrão: `script.py` + `README_como_rodar.md` (dependências, comando, saída esperada) → **o agente para aqui** → o autor roda → o agente interpreta o resultado numa etapa seguinte.

### 0.2 Regras invioláveis (de `.codex/PROJECT_RULES.md`)
- Nunca inventar referências, dados ou citações. Toda referência nova é verificada em fonte real (PubMed/Crossref/página do periódico) antes de entrar em qualquer texto; se não confirmar, marcar "a verificar".
- Distinguir sempre hipótese / proxy operacional / variável provisória / evidência. Simulação sintética **não** é validação empírica.
- Preservar a voz autoral; não reescrever prosa além do necessário.
- **Resultados negativos são dados, não fracassos** — reportar, nunca maquiar.
- Git: branch, commits pequenos e descritivos, **sem push**. — **⚠️ REGRA REVOGADA: o repositório tem remote `origin` no GitHub, `main` e `revisao-2026-08` rastreiam origin e são publicados, com merges regulares para `main`. A convenção vigente é a do `AGENTS.md` (não fazer push sem pedido explícito do autor), não a proibição registrada aqui.**

### 0.3 Formato de cada tarefa
Cada tarefa deste plano declara: **responsável** (agente / autor), **tipo** (busca · script · redação · revisão · execução), **entregável** e **critério de conclusão**.

---

## 1. DIAGNÓSTICO CIENTÍFICO ATUAL (onde estamos, honestamente)

**Teoria.** Núcleo maduro, 13 capítulos, ~30 referências reais e verificadas. Posicionamento honesto quanto ao hard problem.

**Modelo (V1–V5).** Prova de conceito sintética. Os regimes se separam de forma limpa, mas em boa parte **por construção** — o que limita o que os números sozinhos provam. A camada social V4 deu um resultado quase tautológico (já diagnosticado em `_revisao_2026-08-05/revisao_critica_St_V4.md`); a V5 (teste de coordenação) está desenhada, não construída.

**Confronto empírico — este é o ativo mais forte e mais frágil ao mesmo tempo:**
- **Sono (FORTE, agora replicado):** 36 sujeitos do Sleep-EDF, 39.086 épocas. LZc e entropia de permutação concordam **perfeitamente** na ordenação (W > N1 > REM > N2 > N3, Spearman = 1,0) e discriminam quase perfeitamente (AUC W-vs-N3: LZc = 0,992; PE = 0,984). Duas métricas independentes, ~4× mais dados que a primeira rodada. Isto é uma confirmação genuína da predição central de ordenação de complexidade por estado de arousal.
- **Anestesia (NEGATIVO honesto):** 20 sujeitos (propofol, Chennu et al. 2016). A predição **falhou** — o estado `basal` teve a *menor* complexidade das quatro condições, e a AUC basal-vs-moderada ficou abaixo do acaso (0,33 / 0,45). As duas métricas mal concordam (Spearman = 0,40). Reportado com integridade. Hipóteses: alfa forte em olhos fechados reduz a complexidade de banda larga; sedação leve pode desorganizar o alfa e *aumentar* a complexidade medida; e Chennu et al. mostra que **responsividade se dissocia da dose** — "sedação moderada" nominal ≠ inconsciência confirmada.

**As duas maiores lacunas científicas:**
1. **A afirmação-assinatura da teoria — "integração *diferenciada*, não hipersincronia" — permanece praticamente não testada.** LZc e PE medem complexidade, não a coincidência de integração alta *com* diferenciação alta. O teste mais específico desta teoria ainda não foi feito.
2. **Cada pilar teórico precisa de um mapa de evidências explícito** (o que sustenta, o que desafia, o que é especulativo), com força de evidência declarada.

---

## 2. PRINCÍPIOS QUE GUIAM O FORTALECIMENTO
1. **Falsificabilidade primeiro:** cada afirmação da teoria deve virar uma predição com estatuto empírico explícito (confirmada / falhou / não testada).
2. **Ancoragem literal:** cada pilar ancorado em literatura verificada, com **força de evidência** e **contra-evidência** declaradas.
3. **Confronto direcional:** enquanto não houver calibração formal, o confronto com dados é de ordenação/direção, nunca de unidades absolutas.
4. **Separar modelo de teoria:** distinguir "o que o modelo sintético mostra" de "o que a teoria afirma sobre o mundo".
5. **Negativos são informação:** o resultado da anestesia é tão valioso quanto o do sono — orienta onde a teoria tem limite.

---

## 3. FRENTES DE TRABALHO (priorizadas)

### FRENTE A — Mapa de evidências dos pilares da teoria  ·  PRIORIDADE MÁXIMA
**Tipo:** busca multi-agente ampla + redação (100% executável por agentes, sem cálculo).
**Objetivo:** para cada pilar da teoria, produzir um mapa: evidência de sustentação mais forte (com citações reais), desafios/contra-evidência mais fortes, estado do consenso, e lacunas.

**Como executar:** disparar **agentes em paralelo, um por pilar** (ferramenta Task/Agent). Cada agente faz busca ampla e retorna um documento estruturado. **Regras para os agentes:** só citar fontes reais e verificáveis (com URL/DOI); declarar força de evidência (forte/moderada/fraca/mista); **incluir obrigatoriamente a contra-evidência**; marcar o que é especulativo.

**Pilares (um mapa por pilar):**
1. Origem integrativa e **integração diferenciada** (Luppi 2019; Sanz Perl 2021; IIT; medidas de integração×diferenciação).
2. Corpo constitutivo / interocepção (Tallon-Baudry; Engelen 2023; Cea & Signorelli 2025; Seth).
3. Determinismo estratificado / crítica ao livre-arbítrio (Sapolsky; neurociência da decisão; debate Libet e sucessores).
4. Não-linearidade, regimes e transições (criticalidade cerebral; caos; avalanches neuronais).
5. Common knowledge / camada social (Thomas et al. 2014/2016; Pinker; Rubinstein "email game").
6. Automação inteligente / economia da consciência (processamento preditivo; global workspace; automaticidade).
7. Fronteira IA / corporificação (Butlin et al. 2025; Aru; Porębski & Figura 2025; embodiment).
8. Hard problem / posicionamento honesto (Chalmers; Seth "real problem"; meta-problem).

**Entregável:** `embasamento/mapa_evidencias_<pilar>.md` (8 arquivos) + `embasamento/SINTESE_pilares.md` (visão geral: quais pilares estão bem sustentados, quais são frágeis, onde a teoria diverge do consenso).
**Critério de conclusão:** cada pilar com ≥3 fontes de sustentação verificadas, ≥1 contra-evidência séria, e uma frase honesta de força geral.

### FRENTE B — Posicionamento rigoroso frente às teorias rivais  ·  ALTA
**Tipo:** busca multi-agente + redação.
**Objetivo:** comparação sistemática com IIT, GNWT, FEP/Active Inference, Teorias de Ordem Superior (HOT), Recurrent Processing e Attention Schema. Para cada: afirmação central, onde a *Conscience* concorda/diverge, e **predições que a distinguem empiricamente**.
**Como executar:** um agente por teoria rival (paralelo), mesmas regras de honestidade da Frente A.
**Entregável:** `embasamento/posicionamento_teorias_rivais.md` com tabela comparativa + seção "predições distintivas" (o que a nossa teoria prevê que uma rival não prevê). Alimenta um capítulo do manuscrito.
**Critério:** cada teoria com ≥1 predição distintiva testável em relação à *Conscience*.

### FRENTE C — O teste que falta: operacionalizar "integração diferenciada"  ·  ALTA
**Tipo:** desenho + **escrita de scripts** (agente escreve; **autor roda**).
**Objetivo:** testar a afirmação-assinatura da teoria — que a consciência exige integração *diferenciada* (integração alta E diferenciação alta), distinta tanto de complexidade pura quanto de hipersincronia.
**O agente deve ESCREVER (não rodar) scripts que:**
- Calculem, sobre os mesmos dados do Sleep-EDF (e da anestesia re-binada, Frente D), medidas que **separem integração de segregação/diferenciação** — p.ex. medidas grafo-teóricas de integração vs. segregação, e um índice combinado de "integração diferenciada".
- Incluam uma medida de **sincronia global** para demonstrar o outro lado da tese: que hipersincronia (alta integração, baixa diferenciação) **não** acompanha os estados de maior consciência.
- Testem se o índice de integração diferenciada **discrimina melhor** os estados do que complexidade pura (LZc/PE) — comparação de AUCs.
**Entregável:** `scripts_para_rodar/integracao_diferenciada/` com script(s) + `README_como_rodar.md` (dependências, comando, saída esperada). **O agente para aqui.** Após o autor rodar, um agente interpreta.
**Critério:** script roda em uma amostra pequena do Sleep-EDF sem erro (verificação de sintaxe, não de execução pelo agente — o agente pode apenas fazer *lint*/leitura, não executar) e a saída esperada está documentada.

### FRENTE D — Resolver honestamente o negativo da anestesia  ·  ALTA
**Tipo:** busca + **escrita de script** (agente escreve; autor roda).
**Objetivo:** decidir, com integridade, se a predição da anestesia se sustenta sob análise adequada, ou se vira uma **condição-limite documentada** da teoria.
**Passos:**
- Busca (agente): literatura sobre por que a complexidade de banda larga se comporta de forma não-monotônica sob propofol leve, e o confound do alfa de olhos fechados; confirmar o achado de Chennu et al. de dissociação responsividade×dose.
- Script (agente escreve; autor roda): reanálise usando os dados de **responsividade** (`datainfo.mat`) — re-binar por responsividade real em vez de dose nominal; e testar métricas menos sensíveis ao alfa.
**Entregável:** `scripts_para_rodar/anestesia_responsividade/` (script + README) e uma nota `embasamento/nota_anestesia.md` com a leitura da literatura.
**Critério:** o autor consegue rodar a reanálise; a conclusão (predição salva, parcialmente salva, ou condição-limite) fica registrada honestamente.

### FRENTE E — Robustez e identificabilidade do modelo sintético  ·  MÉDIA
**Tipo:** **escrita de scripts** (agente escreve; autor roda).
**Objetivo:** enfrentar a crítica de que os regimes se separam "por construção".
**O agente escreve scripts que:**
- Façam **análise de sensibilidade**: perturbar os parâmetros do V3 e verificar se a ordenação/AUC sobrevive.
- Tentem uma **calibração**: constranger parâmetros do modelo para reproduzir a ordenação empírica de LZc/PE observada no Sleep-EDF, e reportar se o modelo é um ajuste genuíno ou uma tautologia.
**Entregável:** `scripts_para_rodar/robustez_modelo/` (scripts + README). Autor roda; agente interpreta depois.
**Critério:** scripts prontos e documentados; hipótese de teste explícita ("se a separação some sob perturbação X, o resultado é frágil").

### FRENTE F — Camada social: construir a V5 (teste de coordenação)  ·  MÉDIA
**Tipo:** **escrita de script** (agente escreve; autor roda) + ancoragem em literatura.
**Objetivo:** o teste não-circular já desenhado em `docs/historico/PROMPT_claude_code_V5_social.md` — jogo de coordenação com risco (stag-hunt), predição de que "compartilhado-não-ratificado" falha em coordenar. Ancorar em Thomas et al. e no email game de Rubinstein (busca do agente).
**Entregável:** `dados atuais/consciousness_model_v5_social.py` (o agente **escreve**; o autor **roda**) + README com o experimento e as ablações de controle. Interpretação após o autor rodar.
**Critério:** script escrito com as salvaguardas anti-circularidade do prompt V5; saída esperada documentada.

### FRENTE G — Registro de falsificabilidade + rigor estatístico  ·  MÉDIA
**Tipo:** redação + **escrita de scripts** estatísticos (agente escreve; autor roda).
**Objetivo:** um registro vivo de todas as predições da teoria, cada uma com operacionalização e **estatuto empírico atual**; e reforço estatístico (intervalos de confiança, tamanhos de efeito, correções para múltiplas comparações) dos resultados já obtidos.
**Entregável:** `embasamento/registro_falsificabilidade.md` (tabela: predição · operacionalização · dado · estatuto) + `scripts_para_rodar/estatistica/` (scripts de IC/effect size; autor roda).
**Critério:** toda predição citada no manuscrito aparece no registro com um estatuto.

### FRENTE H — Higiene e empacotamento  ·  BAIXA / contínua
- Decidir sobre os arquivos "de origem não identificada" (`_revisao_2026-08-05/*` e os `PROMPT_*.md`): **recomendação — commitá-los** como registro histórico da revisão (um commit `docs: registros da revisão 2026-08`), em vez de deixá-los untracked.
- Padronizar as citações do corpo para marcadores numéricos `[n]` ligados à lista de Referências (hoje em blocos `([domínio](url))`).
- Regenerar DOCX/PDF do manuscrito atualizado.
- Preparar, ao final, um esqueleto de **preprint** (resumo, figuras, registro de falsificabilidade como apêndice).

---

## 4. SEQUENCIAMENTO EM FASES

**Fase 1 — Ancoragem (100% agentes, sem cálculo):** Frentes A e B por completo (busca multi-agente ampla + síntese); parte de busca da Frente D; **escrita** dos scripts das Frentes C, D, E, F, G (sem rodar).

**Fase 2 — Execução local (autor no VS Code):** o autor roda os scripts das Frentes C, D, E, F, G e devolve as saídas. Agentes **interpretam** os resultados e atualizam os documentos de embasamento e o registro de falsificabilidade.

**Fase 3 — Integração no manuscrito:** mapa de evidências → reforço de cada capítulo; posicionamento rival → capítulo dedicado; registro de falsificabilidade → apêndice; empacotamento de preprint.

---

## 5. DIVISÃO DE TRABALHO — agente × autor

| Tipo de trabalho | Quem faz | Exemplos |
|---|---|---|
| Busca na web / literatura | **Agente** (multi-agente OK) | Frentes A, B, D-lit, F-lit |
| Redação / síntese / revisão | **Agente** | mapas de evidência, posicionamento, registro |
| Escrita de scripts Python | **Agente** (NÃO roda) | Frentes C, D, E, F, G |
| **Execução de scripts / cálculos** | **AUTOR (VS Code)** | rodar tudo em `scripts_para_rodar/` e os modelos |
| Interpretação dos resultados | **Agente** (após o autor rodar) | Fase 2 |

---

## 6. ESTRUTURA DE PASTAS PROPOSTA
```
/embasamento/                 ← mapas de evidência, posicionamento, notas, registro (texto)
/scripts_para_rodar/          ← scripts que o AUTOR executa no VS Code
   /integracao_diferenciada/
   /anestesia_responsividade/
   /robustez_modelo/
   /estatistica/
   README_como_rodar.md       ← visão geral + requirements
/dados atuais/                ← modelos (V1–V5) e saídas já existentes (não sobrescrever baselines)
/recompute_empirico_v2/       ← empírico já feito (intocado)
```
Cada pasta de `scripts_para_rodar/` traz seu próprio `README_como_rodar.md` (dependências, comando exato, arquivos de saída esperados) e **nenhuma execução pelo agente**.

---

## 7. REFORÇO DAS REGRAS DE HONESTIDADE CIENTÍFICA
- Verificar **cada** referência antes de citar; declarar força de evidência e contra-evidência.
- Reportar resultados negativos como dados (o caso da anestesia é o exemplo a seguir).
- Nunca apresentar simulação sintética como validação empírica.
- Não confundir "o modelo separa por construção" com "a teoria foi confirmada".
- **Agentes não rodam cálculos** — escrevem scripts; o autor executa.

---

## 8. PRÓXIMO PASSO IMEDIATO (recomendado)

> **⚠️ SEÇÃO REVOGADA — não executar.** A Frente A foi concluída em 2026-08-06 (`embasamento/mapa_evidencias_pilares.md`, `embasamento/SINTESE_pilares.md`) e a Frente C foi escrita, executada pelo autor e interpretada, com **resultado negativo** para a assinatura de integração diferenciada (`CHECKLIST_pendencias.md`, Blocos N e Z; `embasamento/registro_falsificabilidade.md`, entradas 1.2, 1.3 e 1.3b). O texto abaixo é preservado como registro da recomendação feita em 2026-08-05.

Começar pela **Frente A** com busca multi-agente ampla (é a de maior valor e 100% executável por agentes, sem depender de execução local). Em paralelo, **escrever** (não rodar) os scripts da Frente C — o teste de "integração diferenciada" —, que é o experimento mais específico e decisivo para esta teoria.
