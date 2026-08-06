# Checklist Mestre de Pendências — Projeto *Conscience*

> Documento de trabalho para consolidação do projeto rumo a um preprint/livro circulável.
> Status: `[ ]` pendente · `[~]` parcial · `[x]` concluído · `[!]` precisa decisão do autor.
> Responsável: 🤖 executável na sessão · 🧑 depende do autor · 🔁 iterativo.

Criado em 2026-08-05 · **Atualizado após execução em 2026-08-05 (sessão Claude Code, branch `revisao-2026-08`).**

Ver `RELATORIO_claude_code.md` para o detalhamento completo desta sessão.

---

## Bloco A — Integridade bibliográfica → **resolvido**

- [x] **A1.** Extrair e catalogar todas as citações. 🤖 — feito na sessão anterior.
- [x] **A2.** Verificar cada referência contra fonte real. 🤖 — todas as ~28 (25 aprovadas + 3 novas de alostase) são reais e corretamente atribuídas.
- [x] **A3.** Corrigir metadados e remover `utm_source=chatgpt.com`. 🤖 — aplicado diretamente no `Versao atual.md` (fonte), não só no `.docx`.
- [x] **A4.** Reescrever formulações que afirmam mais do que a fonte sustenta. 🤖 — os 3 ajustes de atribuição/escopo (notas a/b/c) aplicados: Thomas et al. (2016) no Cap. 9, escopo de "A beautiful loop" no Cap. 10. Nota (a) sobre Mudrik et al. já estava formulada com cautela no texto original.
- [x] **A5.** Marcar livros lidos integralmente × influência conceitual. 🧑→🤖 — confirmado pelo autor: Sapolsky (3 livros), Dawkins, Gleick lidos integralmente (verbos fortes mantidos); Chalmers como referência conceitual (enquadramento já adequado no texto).
- [x] **A6.** Bibliografia padronizada (Vancouver numerada). 🤖 — seção "Referências" (28 itens) agora está no `Versao atual.md`, não só no `.docx` antigo.

## Bloco B — Consistência do formalismo → **resolvido**

- [x] **B1.** Inventário de variáveis/símbolos. 🤖
- [x] **B2.** Cruzar prosa ↔ código; achar símbolos órfãos. 🤖
- [x] **B3.** Coerência das fórmulas do Cap. 13 com a implementação. 🤖 — interceptos incluídos (η₀, coherence_bias, arousal_bias declarados); 𝓜=M/(M+1) explicitado.
- [x] **B4.** Classificar estatuto de cada variável. 🤖 — tabela símbolo→estatuto inserida no Cap. 13.
- [x] **B5.** Padronizar a ressalva "dados sintéticos". 🤖 — frase-padrão nas equações do Cap. 13 e na seção de Referências.
- [x] **Achado crítico (S(t)/𝒞_hum não simulados):** declarado explicitamente no corpo do Cap. 13, não apenas nos relatórios de auditoria.

## Bloco C — Robustez computacional → **reproduzido e reforçado**

- [x] **C1.** Reproduzir os 3 scripts. 🤖 — V2 e V3 na precisão de máquina; toy reproduz com divergência de ~0,004 em `deep_sleep` (provável não-portabilidade de `np.linalg.eigvals` entre builds de BLAS/LAPACK — ver `RELATORIO_claude_code.md`).
- [x] **C2.** Reexecutar V3 com n_runs/T maiores. 🤖 — `dados atuais/reforco_outputs/` (n_runs=40, T=60): ordenação preservada, separação aumenta com séries mais longas.
- [x] **C3.** Verificar determinismo/sementes. 🤖 — confirmado (toy autodeterminístico nesta máquina; a divergência vs. baseline é entre ambientes, não dentro do mesmo ambiente).
- [x] **C4.** Não sobrescrever o baseline. 🤖 — `reforco_outputs/` separado, baseline intacto (hash conferido).
- [x] **C5.** Substituir/confrontar dados sintéticos com empíricos. 🤖 — **recompute real feito** sobre Sleep-EDF Expanded (LZc por estágio). Ver seção 2 de `RELATORIO_claude_code.md` para tabela, figura e interpretação.

## Bloco D — Arquitetura editorial → **substancialmente concluído**

- [x] **D1.** Sumário consolidado. 🤖 — ver `andaime_editorial.md`.
- [x] **D2.** Mapa de lacunas por capítulo. 🤖
- [x] **D3.** Padronizar chamadas de referência no corpo. 🤖 — resolvido: todo o corpo agora usa `[n]` numerado (adotado do `.docx` ao reestruturar em capítulos separados).
- [x] **D4.** Expandir capítulos em prosa. 🤖 — Cap. 3 mesclado (`Cap3_expandido.md`); Caps. 5, 7, 11 expandidos; listas dos Caps. 4, 6, 10, 12 convertidas em prosa.
- [ ] **D5.** Revisão em camadas antes de publicar. 🔁 — ainda não passou por uma leitura integral "de capa a capa" pós-edição pelo autor.
- [!] **D6.** Versão editorial em DOCX/PDF. 🧑 — **adiada a pedido do autor nesta sessão**. `Consciencia_versao_editorial_limpa.docx` existente está **desatualizado** (não reflete nenhuma mudança desta sessão). Gerar nova versão a partir de `Versao atual.md` quando o autor pedir.

## Bloco E — Higiene do repositório → **feito, com uma correção importante**

- [x] **E1.** Consolidar READMEs de `dados atuais/`. 🤖 — `dados atuais/README.md` único.
- [x] **E2.** Resolver duplicatas de figuras/CSV. 🤖 — feito, **com correção**: 9 das 10 figuras sinalizadas não eram duplicatas (eram saídas do V2 sem essa etiqueta); renomeadas para `*_v2.png` em vez de apagadas. Detalhes em `RELATORIO_claude_code.md`.
- [x] **E3.** `requirements.txt` revisado. 🤖 — mantido; ambiente de execução real ficou em `.venv/` (não versionado, listado no `.gitignore`), com `mne`/`yasa`/`antropy`/`python-docx`/`reportlab`/`pypandoc` adicionais para as tarefas desta sessão.
- [x] **E4.** Registrar mudanças na documentação. 🤖 — este checklist + `RELATORIO_claude_code.md`.

## Bloco F — Recompute empírico real (Sleep-EDF) → ver `RELATORIO_claude_code.md`

- [x] **F1.** Baixar Sleep-EDF Expanded (subset sleep-cassette, PhysioNet). 🤖
- [x] **F2.** Calcular LZc por época de 30s, agregado por estágio (W, REM, N1, N2, N3). 🤖
- [x] **F3.** Confirmar ordenação W≈REM>N2>N3 e reportar AUC W-vs-N3. 🤖
- [x] **F4.** Comparar com a ordenação do índice 𝒞 do modelo. 🤖
- [x] **F5.** Salvar script, tabela, figura e relatório curto. 🤖 — `recompute_empirico_sleepedf/`.

## Bloco G (opcional) — Expansão de capítulos → **concluído**

- [x] Expandir Cap. 5 (exemplo: dependência química/responsabilidade penal). 🤖
- [x] Expandir Cap. 7 (reamarração ao núcleo integrativo). 🤖
- [x] Expandir Cap. 11 (Trauma: remover afirmação sem fonte, reformular como interpretação explícita). 🤖
- [x] Converter listas dos Caps. 4, 6, 10, 12 em prosa, com exemplos concretos onde pedido. 🤖

## Bloco H — Reestruturação em capítulos separados → **concluído**

- [x] Converter `Consciencia_versao_editorial_limpa.docx` para markdown (Pandoc) e comparar com `Versao atual.md`. 🤖 — confirmado que o `.docx` estava desatualizado em tudo, exceto o estilo de citação `[n]`.
- [x] Adotar o estilo de citação `[n]` no corpo do texto (resolve D3). 🤖
- [x] Separar o manuscrito em 17 arquivos por capítulo em `capitulos/`. 🤖
- [x] Criar índice (`capitulos/README.md`) e script de reconstrução (`capitulos/build_manuscript.py`). 🤖
- [x] Verificar por diff que nada foi perdido na reestruturação. 🤖

## Bloco I — Cap. 11 e referências finais → **concluído**

- [x] Cap. 11 (Sonho): confronto do REM com o recompute de LZc, como predição diferencial. 🤖
- [x] Cap. 11 (Trauma): citação real (Lanius et al. 2010; Nicholson et al. 2015) em vez da ressalva "sem fonte". 🤖 — ambas verificadas de forma independente (PubMed) antes de entrar no manuscrito.
- [x] Referência 13 (Whyte et al.) finalizada: DOI e paginação confirmados via Crossref (10.1016/j.plrev.2025.11.002, vol. 56, p. 4-28). 🤖
- [x] Referências 29 e 30 adicionadas; nota de verificação atualizada para "26–30". 🤖

## Bloco J — V4: prova de conceito da camada social → **concluído**

- [x] `dados atuais/consciousness_model_v4_social.py`: N=6 agentes rodando a dinâmica interna intocada do V3 + canal social mínimo. 🤖 — V3 não foi alterado (confirmado via `git status`).
- [x] $M_r$, $P_u$, $R_a$ operacionalizados como proxies provisórios, documentados na docstring do script. 🤖
- [x] Três cenários (privado / compartilhado não ratificado / publicamente ratificado). 🤖
- [x] Predição testada: $S$/$\mathcal{C}_{hum}$ crescem i→ii→iii, $C_{base}$ estável. 🤖 — AUC(ratificado vs. privado) = 1,0 para $S$/$\mathcal{C}_{hum}$, 0,458 (acaso) para $C_{base}$.
- [x] Saídas em `dados atuais/social_outputs/` (script reprodutível, tabela, figura, README). 🤖 — baseline do V3 preservado.
- [x] Reprodutibilidade por seed confirmada. 🤖
- [x] Cap. 13 e `auditoria_formalismo.md` (Nota 5) atualizados: $S(t)$/$\mathcal{C}_{hum}$ passam de "não simulados" para "minimamente simulados (prova de conceito, V4)". 🤖
- [!] **Revisão crítica encontrada** (`_revisao_2026-08-05/revisao_critica_St_V4.md`, origem não identificada) aponta que a AUC=1,0 de $S$ é **quase tautológica** (os cenários são definidos exatamente pelas variáveis que compõem $S$) e que o achado defensável é outro ($C_{base}$ no acaso = camada social não-redundante com o índice individual). Avaliei o argumento de forma independente e **concordo com o diagnóstico central**. 🧑 decidir se quer que eu reescreva a leitura do resultado no relatório/manuscrito e/ou avance para uma V5 com teste comportamental não-circular (jogo de coordenação tipo stag-hunt) — ver seção correspondente do relatório.

## Bloco K — Recompute empírico V2: amostra ampliada + 2ª métrica + anestesia → **concluído**

- [x] Sleep-EDF escalado de 10 para 36 sujeitos (39.086 épocas); truncamentos documentados (3 sujeitos sem N3; 2 índices ausentes do dataset). 🤖
- [x] Entropia de permutação (Bandt & Pompe 2002, verificada) como 2ª métrica independente. 🤖 — concordância perfeita com LZc no sono (Spearman=1,0 na ordenação, 0,72 época-a-época); AUC W-vs-N3 reforçada (LZc=0,9919, PE=0,9840).
- [x] Dataset de anestesia por propofol (Cambridge/Chennu et al. 2016) baixado e processado — 20/20 sujeitos, sem bloqueio de licença/download. 🤖
- [!] **Predição de anestesia NÃO confirmada**: `basal` teve a *menor* complexidade das 4 condições (não a maior); AUC basal-vs-moderada abaixo do acaso (LZc=0,33; PE=0,45); as duas métricas concordam pouco entre si (Spearman=0,40). Resultado negativo/misto reportado com honestidade, com hipóteses explicativas (ritmo alfa em repouso; dissociação responsividade/dose já documentada pelos próprios autores do dataset) — não confirmadas experimentalmente nesta sessão. 🧑 decidir se quer uma análise de acompanhamento estratificada por responsividade comportamental (dados já presentes em `datainfo.mat`, não utilizados nesta rodada).
- [x] Saídas em `recompute_empirico_v2/` (nova pasta); `recompute_empirico_sleepedf/` preservada intocada. 🤖
- [x] Reprodutibilidade confirmada (métricas determinísticas; nenhuma amostragem aleatória própria). 🤖

---

## O que agora depende de você (🧑)

1. **DOCX/PDF** — dizer quando quer que eu gere a versão editorial a partir de `Versao atual.md` (agora sempre reconstruído de `capitulos/`).
2. **Nova política de edição** — a partir de agora, edite os arquivos em `capitulos/`, não `Versao atual.md` diretamente (ele é regenerado por `capitulos/build_manuscript.py` e uma edição direta nele seria perdida).
3. **`Consciencia_versao_editorial_limpa.docx`** — ficou obsoleto (conteúdo desatualizado + estrutura de arquivo único). Decidir se quer que eu remova ou mantenha como registro histórico.
4. ~~`_revisao_2026-08-05/edicoes_cap11_e_referencias.md` não rastreado~~ — **commitado** em `1eedb1b`, junto com os demais arquivos de apoio (ver item 11).
5. **D5** — ler a versão integral pós-edição antes de qualquer circulação pública.
6. ~~Amostra do recompute empírico~~ — **ampliada no Bloco K** (10→36 sujeitos, + entropia de permutação, + dataset de anestesia).
7. **V5 (opcional, futuro)** — o V4 não realimenta a ratificação social de volta na valoração individual $V(t)$ de cada agente, por escolha de design (para não alterar o V3). Existe um prompt pronto para isso em `PROMPT_claude_code_V5_social.md` (ainda não executado) — decidir se quer que eu rode esse prompt.
8. **Revisão crítica do V4** (`_revisao_2026-08-05/revisao_critica_St_V4.md`) — argumento tecnicamente correto (avaliei de forma independente): a AUC=1,0 de S(t) é quase tautológica; propõe reescrever a leitura do resultado e, como próximo passo não-circular, a V5 do item 7. Decidir se quer que eu aplique a correção de texto e/ou construa a V5.
9. **Predição de anestesia não confirmada (Bloco K)** — decidir se quer uma análise de acompanhamento usando os dados de responsividade comportamental do `datainfo.mat` do dataset de propofol (não usados nesta rodada), que poderiam esclarecer se o resultado muda ao separar sujeitos que de fato perderam responsividade.
10. ~~**Repositório GitHub**~~ — **resolvido**: merge direto de `revisao-2026-08` para `main` feito a seu pedido; confirmado via `git branch -vv` que ambos os branches apontam para `5516898`, em sincronia com `origin/main` e `origin/revisao-2026-08`.
11. ~~**Decisão de governança — `PLANO_ESTRATEGICO_cientifico.md`**~~ — **resolvido**: você esclareceu que a regra "agentes não executam, só escrevem scripts" vale apenas para **cálculos complexos que gastariam muitos tokens**, não como regra geral. Sessão continua executando diretamente (downloads, EEG, simulações) como até aqui; só passo a preferir "escrever script + você roda" quando o cálculo for pesado o bastante para justificar.
12. **Achado da sessão paralela (Codex/Cowork) — ver Bloco L abaixo.** Decidir: (a) se quer que eu rode a checagem de spectral slope proposta; (b) como tratar a citação incorreta antes que ela circule; (c) o que fazer com o restante dos achados dessa outra sessão, que não pude verificar (pasta `C:\Haenndel Projects 2\` não existe nesta máquina).

## Bloco L — Verificação de achado citado por outra sessão (Codex/Cowork) → **citação corrigida; achado científico parcialmente sustentado**

Contexto: você colou a narração de uma sessão paralela (aparentemente rodando em outra máquina/pasta, `C:\Haenndel Projects 2\conscience` — não localizável a partir daqui) que apontou um possível confundidor sério para o recompute de LZc por estágio de sono (Blocos F e K): a ideia de que a LZc seria "substancialmente explicada" pela inclinação espectral (1/f slope), citando "Bruzzone et al. (2024, eNeuro)". Como de praxe neste projeto, verifiquei a citação de forma independente antes de aceitar a implicação, em vez de repassá-la como se fosse confirmada.

- [x] **L1.** Localizar a pasta da outra sessão. 🤖 — `C:\Haenndel Projects 2\` **não existe** nesta máquina; não há como inspecionar os arquivos reais (`mapa_evidencias_pilares.md`, `SINTESE_pilares.md`) a partir daqui, só a narração colada.
- [x] **L2.** Verificar a citação "Bruzzone et al. (2024, eNeuro)". 🤖 — **citação incorreta**: não existe autor "Bruzzone" no artigo. O artigo real é **Höhn, Hahn, Lendner & Hoedlmoser (2024)**, "Spectral Slope and Lempel–Ziv Complexity as Robust Markers of Brain States during Sleep and Wakefulness", *eNeuro* 11(3), ENEURO.0259-23.2024, DOI `10.1523/ENEURO.0259-23.2024` (confirmado via PubMed, PMID 38471778).
- [x] **L3.** Verificar o conteúdo da alegação (não só o nome). 🤖 — o artigo **não conclui que a LZc é redundante/inválida**. Ele reporta que, na banda larga (1–45 Hz, a banda usada no nosso recompute), slope e LZc "track highly similar information about the underlying brain state" (covariam fortemente entre vigília→N3) — isso **é** um confundidor real e digno de nota. Mas na banda estreita (30–45 Hz) os autores mostram que os dois **divergem** e concluem explicitamente que "the two parameters are not redundant". A recomendação do artigo é que o slope é mais prático/generalizável, não que a LZc esteja errada.
- [ ] **L4 (proposta, não executada).** Testar o confundidor nos nossos próprios dados: calcular o expoente aperiódico (1/f slope, ex. via `specparam`/FOOOF) nas mesmas épocas do Sleep-EDF (`recompute_empirico_sleepedf/` e `recompute_empirico_v2/`) e correlacionar com LZc/PE por estágio. Isso responderia diretamente "quanto do nosso resultado de LZc é slope" em vez de inferir de um artigo com outro dataset. 🧑 decidir se quer que eu implemente.

**Leitura honesta para o manuscrito/relatório:** o resultado de LZc por estágio de sono (Blocos F/K) continua válido como está reportado — é um dado real, reproduzido com 2 métricas independentes em 36 sujeitos — mas o confundidor espectral é uma ressalva legítima que ainda não está registrada em `RELATORIO_claude_code.md` nem em `recompute_empirico_v2/RELATORIO_v2.md`. Recomendo adicionar essa ressalva (citando Höhn et al. corretamente) independentemente de rodarmos L4.

**Sobre confiar no restante da outra sessão:** como o achado "mais sério" que ela sinalizou veio com o nome do autor errado, isso é motivo para tratar os outros 4 pontos que ela reportou (distanciamento de IIT, reformulação compatibilista de livre-arbítrio, "detecção de publicidade" na camada social, reformulação via criticalidade) com a mesma cautela — não confirmei nenhum deles e não consigo acessar os arquivos-fonte dela a partir desta máquina. Também não está claro se "Frente B" (próxima etapa que essa sessão perguntou) foi uma pergunta dirigida a você ou só ao usuário dela mesma — vale esclarecer se são a mesma pessoa/repo em duas máquinas ou dois fluxos de fato independentes.
