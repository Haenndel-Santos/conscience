# Prompts para o Claude Code — camada social S(t) e aprofundamento empírico

Dois prompts independentes. Recomendo rodar em **sessões separadas** do Claude Code (uma por frente). Ambos assumem o repositório `C:\Haenndel Projects\conscience`, branch `revisao-2026-08`, e as regras de `.codex/PROJECT_RULES.md` e `.codex/WORKFLOW.md`.

Regras comuns a ambos:
- Trabalhe na branch `revisao-2026-08` (crie sub-branch se preferir). Commits pequenos e descritivos. **Não faça push.**
- Não sobrescreva baselines nem os scripts V2/V3 existentes — crie arquivos novos.
- Honestidade metodológica: proxies e simulações sintéticas **não** são prova; declare o estatuto de cada variável. Nunca invente referências — verifique antes de citar.
- Ao terminar, escreva um relatório em português e atualize o `CHECKLIST_pendencias.md`.

---

# PROMPT 1 — Implementar a camada social S(t) e o índice 𝒞_hum

Você é o Claude Code no projeto Conscience. Hoje o modelo (V3) é de agente único e a camada social da teoria existe só no papel: o Cap. 9 define `S(t) = λ1·M_r(t) + λ2·P_u(t) + λ3·R_a(t)` (mentalização recursiva, publicidade, ratificação) e `𝒞_hum(t) = w1·Ψ_eff + w2·Q + w3·𝓜 + w4·B + w5·S`, mas nenhum script implementa S. Sua tarefa é criar uma **prova de conceito mínima** que simule S(t) e 𝒞_hum, sem quebrar o V3.

Leia antes: `dados atuais/consciousness_model_v3.py`, o Cap. 9 e o Cap. 13 de `Versao atual.md`, e `_revisao_2026-08-05/auditoria_formalismo.md`.

Projeto e requisitos:
1. Crie `dados atuais/consciousness_model_v4_social.py`. Reutilize a dinâmica interna do V3 por agente (pode importar/adaptar), mas agora com **N agentes** (ex.: N=6) que se comunicam por um canal público.
2. Operacionalize as três componentes de S como **proxies provisórios**, documentando cada um:
   - `M_r(t)` — mentalização recursiva: profundidade alcançada de "eu sei que você sabe que eu sei…" (nível de aninhamento de crenças recíprocas), limitada a um teto; cresce com sinalização recíproca bem-sucedida.
   - `P_u(t)` — publicidade: fração de agentes que receberam o conteúdo no canal compartilhado.
   - `R_a(t)` — ratificação: grau de reconhecimento mútuo (agentes confirmando recebimento), que converte publicidade em *common knowledge*.
   - `S(t) = λ1·M_r + λ2·P_u + λ3·R_a`; `𝒞_hum = 𝒞_base(média dos agentes) + w5·S`. Deixe λ e w5 como parâmetros nomeados.
3. Implemente **três cenários** que correspondem aos três níveis do Cap. 9:
   - (i) **privado** — sem transmissão no canal público;
   - (ii) **compartilhado não ratificado** — transmissão sem reconhecimento mútuo;
   - (iii) **publicamente ratificado** — transmissão + reconhecimento recursivo (common knowledge).
4. **Predição a testar** (análoga ao ROC do V3): S(t) e 𝒞_hum devem crescer de (i)→(ii)→(iii), enquanto o 𝒞_base permanece aproximadamente estável — mostrando que S acrescenta a dimensão social que o índice privado não capta. Reporte a discriminação (AUC) de S e de 𝒞_hum para "ratificado vs privado", e mostre que 𝒞_base sozinho não discrimina.
5. Saídas em `dados atuais/social_outputs/`: script reproduzível (seeds fixas), tabela-resumo por cenário, curva/figura, e um `README.md` curto. Não sobrescreva nada do V3.
6. **Honestidade obrigatória:** S(t) é um *proxy operacional de um processo social*, não uma afirmação de que o modelo capta consciência intersubjetiva real; o common knowledge aqui é uma instanciação mínima inspirada em Thomas et al. (2014/2016). Deixe isso explícito no README e no relatório.
7. Atualize o texto: no Cap. 13 de `Versao atual.md`, troque a declaração "S(t)/𝒞_hum **não** são simulados" por "S(t)/𝒞_hum são **minimamente simulados** (prova de conceito, V4)", mantendo a ressalva de que é sintético. Atualize também `_revisao_2026-08-05/auditoria_formalismo.md` na Nota 5.

Verificação e entrega: confirme reprodutibilidade por seed; rode o cenário e cheque o `git diff` isolado; um commit por etapa (código; depois texto). Relatório em português: definições operacionais adotadas, resultado da predição (tabela + AUC), limites honestos, e o que ficou em aberto (ex.: passar de proxy a um modelo de agentes mais rico).

---

# PROMPT 2 — Aprofundar o confronto empírico (mais sujeitos, 2ª métrica, extremo de anestesia)

Você é o Claude Code no projeto Conscience. Já existe um recompute empírico inicial em `recompute_empirico_sleepedf/` (LZc por estágio de sono, 10 sujeitos do Sleep-EDF; resultado: W>N1>REM>N2>N3, AUC W-vs-N3=0,995). Sua tarefa é torná-lo mais robusto, sem sobrescrever o que existe.

Leia antes: `recompute_empirico_sleepedf/` (script e relatório) e `_revisao_2026-08-05/confronto_empirico.md` (Parte 4, protocolo).

Tarefas:
1. **Escalar os sujeitos.** Estenda a análise do Sleep-EDF Expanded (https://physionet.org/content/sleep-edfx/) para uma amostra bem maior (ex.: 30–50 noites do Sleep-Cassette, ou todas se viável). Reporte n e como os sujeitos foram selecionados; registre qualquer truncamento (sem silenciar cortes).
2. **Segunda métrica independente.** Além da LZc, calcule a **entropia de permutação** (ordinal, Bandt & Pompe) por época de 30 s e agregue por estágio. Use `antropy` (`pip install antropy`) ou implemente o algoritmo ordinal. Verifique se as duas métricas dão ordenações **concordantes** (robustez cross-métrica).
3. **Extremo de baixa integração — anestesia.** Baixe o dataset aberto de EEG de propofol de Cambridge (Chennu/Bekinschtein; EEG 91 canais; estados basal→sedação leve→moderada→recuperação; licença CC BY): https://www.repository.cam.ac.uk/handle/1810/252736 . Calcule LZc e entropia de permutação por estado e teste a predição de que a complexidade **cai** com a profundidade da sedação, estendendo o gradiente vigília>sono para o eixo vigília>anestesia. Se o download/licença bloquear, relate e siga com o Sleep-EDF ampliado.
4. **Confronto com o modelo.** Compare as ordenações empíricas (sono e anestesia) com a ordenação do índice 𝒞 do modelo (V3) e com os benchmarks publicados de `confronto_empirico.md`. Deixe claro que o confronto é de **ordenação/direção**, não de valores absolutos (o modelo não está em unidades de EEG).
5. Saídas em `recompute_empirico_v2/` (pasta nova): scripts reproduzíveis, tabelas (por dataset e por métrica), figuras (complexidade por estágio/estado, com ±desvio), AUCs, e um relatório curto. Não sobrescreva `recompute_empirico_sleepedf/`.
6. **Referências.** Se for citar métricas/achados no manuscrito, verifique cada referência antes (ex.: entropia de permutação = Bandt & Pompe, Phys Rev Lett 2002; confirme). Não introduza citação não verificada.

Verificação e entrega: cheque reprodutibilidade (seeds/versões), e que nenhuma pasta antiga foi sobrescrita. Commits pequenos (ex.: "empírico v2: Sleep-EDF ampliado + entropia de permutação"; "empírico v2: anestesia propofol"). Relatório em português: n e amostragem, tabela LZc × entropia de permutação por estado, se as métricas concordam, se a predição (vigília > sono profundo > anestesia) se confirmou, e limites honestos (medida global de escalpo, acesso a dados, etc.).
