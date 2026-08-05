# Prompt para o Claude Code — Projeto *Conscience*

Você é o Claude Code atuando no repositório local do projeto **Conscience** (pasta `C:\Haenndel Projects\conscience`), um projeto autoral de teoria da consciência ("Consciência como Regime Integrado") que tem duas pernas: um **manuscrito** (`Versao atual.txt`) e um **modelo computacional** de prova de conceito (`dados atuais/` com os scripts `consciousness_toy_model.py`, `consciousness_model_v2.py`, `consciousness_model_v3.py`).

Uma revisão prévia já foi feita e deixou relatórios prontos. Seu trabalho agora é **aplicar essas conclusões no repositório** (editar arquivos, rodar código, baixar dados, regenerar entregáveis) e **relatar tudo em português, de forma clara**, para que o projeto siga sendo desenvolvido.

---

## 1. Leia primeiro (nesta ordem)

1. `.codex/PROJECT_RULES.md`, `.codex/WORKFLOW.md` e `.codex/README.md` — **as regras invioláveis do projeto**.
2. `CHECKLIST_pendencias.md` (raiz) — o mapa mestre de pendências e status.
3. Na pasta `_revisao_2026-08-05/`:
   - `verificacao_referencias.md` — todas as referências já verificadas (são reais) + correções de metadados e a bibliografia padronizada.
   - `auditoria_formalismo.md` — discrepâncias texto↔código do formalismo.
   - `reproducao_simulacoes.md` — resultados de reprodução/reforço das simulações.
   - `andaime_editorial.md` — sumário consolidado e mapa de lacunas por capítulo.
   - `README_dados_consolidado.md` — mapa das 3 versões do modelo + correção de rótulos de CSV.
   - `Cap3_expandido.md` — o Capítulo 3 já reescrito e expandido, pronto para mesclar.
   - `confronto_empirico.md` — confronto do modelo com a literatura + protocolo para o recompute empírico real.
4. `Versao atual.txt` — o manuscrito atual.

Não refaça as análises acima; **aplique** o que elas concluíram. Onde uma decisão de conteúdo for necessária e não estiver coberta, pare e pergunte.

## 2. Regras invioláveis (do PROJECT_RULES.md — cumpra à risca)

- **Nunca invente referências, dados ou citações.** Toda referência nova que você introduzir precisa ser verificada em fonte real (PubMed/Crossref/página do periódico) antes de entrar no manuscrito; se não conseguir verificar, marque como "a verificar" e não afirme.
- Preserve a **voz autoral** e o núcleo teórico. Não reescreva a prosa do autor além do que as tarefas pedem.
- Distinga sempre **hipótese / proxy / variável provisória / evidência**. Nunca trate formalismo ou simulação sintética como prova empírica.
- Evite linguagem de bastidor ("esta versão", "anteriormente", "o usuário pediu") no manuscrito.
- **Segurança de versões:** antes de editar, crie um branch git (`git checkout -b revisao-2026-08`) e faça backup de `Versao atual.txt` (ex.: `Versao atual.backup.txt`). Faça commits pequenos e descritivos a cada tarefa. Não faça push sem o autor pedir.

## 3. Decisões já tomadas pelo autor (aplique-as)

- Livros **lidos integralmente**: Sapolsky (*Behave*, *Determined*, *Why Zebras Don't Get Ulcers*), Dawkins (*The Selfish Gene*), Gleick (*Chaos*) → pode manter verbos fortes ("mostra", "demonstra").
- **Chalmers** = referência conceitual (o *hard problem*, "Facing Up to the Problem of Consciousness", 1995) — manter o enquadramento atual, sem verbos de leitura profunda.
- Os **3 ajustes de atribuição** do `verificacao_referencias.md` (notas a/b/c) estão **aprovados**: aplicar.
- Versão **canônica** dos coeficientes do modelo: **V3**.

## 4. Tarefas, em ordem de prioridade

### A. Higiene do repositório (rápido)
- Apague os arquivos duplicados em `dados atuais/` (o autor autorizou): `summary2.csv`, `Toy_model_summary_by_regime.csv` (ambos são dados do V2, duplicados de `Consciousness_Model_V2_Summary.csv`), e as figuras redundantes `anxiety_indices 2.png`, `anxiety_phase 2.png`, `deep_sleep_indices 2.png`, `deep_sleep_phase 2.png`, `reflex_indices 2.png`, `reflex_phase 2.png`, `regime_comparison 2.png`, `wake_indices 2.png`, `wake_phase 2.png`, `wake_phase 3.png`. Confirme por conteúdo antes de apagar.
- Consolide os três READMEs de `dados atuais/` em um só (use `README_dados_consolidado.md` como base) e mantenha o `requirements.txt` da raiz.

### B. Aplicar correções bibliográficas no manuscrito
Edite `Versao atual.txt` conforme `verificacao_referencias.md`:
- Remova o parâmetro `?utm_source=chatgpt.com` de todos os links.
- Corrija grafia: **Loescher**. Date **Cea & Signorelli (2025)** e **Milinković & Aru (2025)**.
- Cap. 9: atribua a passagem a **Thomas et al. (2016)** em vez de "Pinker".
- Cap. 10: ajuste o escopo da ref. "A beautiful loop" (o sono não é o foco central dessa referência).
- Acrescente ao final uma seção **Referências** padronizada (a lista numerada de 25 itens já está pronta no relatório e no `.docx` `Consciencia_versao_editorial_limpa.docx`).

### C. Corrigir e limpar a estrutura editorial
- **Remova o bastidor** do começo ("Perfeito. Abaixo está uma reescrita…") e do fim ("Se você quiser, o próximo passo…") de `Versao atual.txt`.
- **Mescle o Capítulo 3 expandido** (`Cap3_expandido.md`) no lugar do Cap. 3 atual, sem as "notas para consolidação" (elas são instruções, não corpo do texto). Antes de finalizar, verifique e insira uma citação textual para a alostase/carga alostática (candidatos: McEwen 1998; Sterling & Eyer 1988; Sterling 2012) — só cite os que você confirmar.

### D. Aplicar correções de formalismo (Cap. 13)
Conforme `auditoria_formalismo.md`:
- Inclua os interceptos nas fórmulas (o termo constante de Q) ou declare as equações como "esquemáticas".
- Explicite que 𝓜 no índice 𝒞 é a memória saturada, M/(M+1).
- Declare os parâmetros de regime `coherence_bias`/`arousal_bias` (que aparecem no código mas não nas equações).
- **Declare explicitamente que a camada social S(t) e o índice 𝒞_hum ainda NÃO são simulados** — são esboço conceitual.
- Adote V3 como versão canônica dos coeficientes; padronize a ressalva "resultado de simulação sintética, não validação empírica" onde houver números.
- Considere reforçar, no Cap. 13 e no Cap. 3, a definição de **integração efetiva (Ψ_eff) como integração diferenciada/flexível** (ponderando complexidade K e recursividade R), não magnitude de acoplamento — isso é o que o confronto empírico recomendou (ver `confronto_empirico.md`).

### E. Regenerar os entregáveis
- Rode os três scripts para confirmar reprodutibilidade e gere uma execução reforçada do V3 (`n_runs=40, T=60`), salvando as saídas em `dados atuais/reforco_outputs/` (não sobrescreva o baseline).
- Regenere a versão editorial limpa em **DOCX e PDF** a partir do `Versao atual.txt` já corrigido (pode usar pandoc). Nomeie com data.

### F. Recompute empírico real (o passo novo mais importante)
Execute o protocolo de `confronto_empirico.md` (Parte 4) com dados reais:
- Baixe o **Sleep-EDF Expanded** (aberto, sem cadastro: `https://physionet.org/content/sleep-edfx/`). Use `mne` e/ou `yasa` (`pip install mne yasa`).
- Para uma amostra de sujeitos, calcule a **complexidade de Lempel-Ziv (LZc)** por época de 30 s, agregada por estágio (W, REM, N1, N2, N3).
- Teste a predição do modelo: confirme a ordenação **W ≈ REM > N2 > N3** e reporte o **AUC W-vs-N3** (análogo ao V3). Compare a *forma* da ordenação empírica com a ordenação do índice 𝒞 do modelo.
- Salve: um script reproduzível, uma tabela de resultados, uma figura (LZc por estágio) e um relatório curto. **Seja honesto**: o modelo não está em unidades de EEG; o confronto é de ordenação/direção, não de valores absolutos. Verifique as referências de 2025 e a de LZc-por-estágio antes de citá-las.

### G. (Opcional, se sobrar escopo) Continuar a expansão editorial
Seguindo `andaime_editorial.md`, expanda os capítulos **5 → 7 → 11** e converta as listas dos capítulos 4, 6, 10 e 12 em prosa contínua, sempre respeitando o núcleo teórico. Cada expansão deve ter abertura conceitual, exemplo concreto, retomada do núcleo e transição.

## 5. Como entregar os resultados

Ao final, produza **em português** um arquivo `RELATORIO_claude_code.md` na raiz, contendo:
1. O que foi alterado, arquivo por arquivo (com os commits correspondentes).
2. Resultado do recompute empírico (tabela + interpretação + se confirmou a predição).
3. Referências novas que você introduziu e o status de verificação de cada uma.
4. O que ficou pendente ou precisa de decisão do autor.
5. Atualize o `CHECKLIST_pendencias.md` marcando o que foi concluído.

Mantenha o tom técnico e direto. Não invente resultados; se algo falhar (download, dependência, ambiguidade de conteúdo), relate o erro e o que tentou, e siga com o que for possível.
