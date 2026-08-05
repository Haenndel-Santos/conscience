# Checklist Mestre de Pendências — Projeto *Conscience*

> Documento de trabalho para consolidação do projeto rumo a um preprint/livro circulável.
> Status: `[ ]` pendente · `[~]` parcial · `[x]` concluído · `[!]` precisa decisão do autor.
> Responsável: 🤖 executável na sessão · 🧑 depende do autor · 🔁 iterativo.

Criado em 2026-08-05 · **Atualizado após execução em 2026-08-05.**

---

## Bloco A — Integridade bibliográfica  → **essencialmente resolvido**

- [x] **A1.** Extrair e catalogar todas as citações. 🤖 — 21 artigos + 6 livros catalogados.
- [x] **A2.** Verificar cada referência contra fonte real. 🤖 — **todas as ~27 são reais e corretamente atribuídas** (verificadas em PubMed/Crossref/periódico). Ver `verificacao_referencias.md`.
- [x] **A3.** Corrigir metadados e remover `utm_source=chatgpt.com`. 🤖 — aplicado na versão editorial limpa (`.docx`).
- [~] **A4.** Reescrever formulações que afirmam mais do que a fonte sustenta. 🤖→🧑 — 3 pontos sinalizados (notas a/b/c do relatório); aguarda aprovação do autor.
- [!] **A5.** Marcar livros lidos integralmente × influência conceitual. 🧑 — **precisa da sua confirmação** (Sapolsky, Dawkins, Gleick, Pinker, Chalmers).
- [x] **A6.** Bibliografia padronizada (Vancouver numerada). 🤖 — pronta e anexada ao `.docx`.

## Bloco B — Consistência do formalismo  → **auditado**

- [x] **B1.** Inventário de variáveis/símbolos. 🤖
- [x] **B2.** Cruzar prosa ↔ código; achar símbolos órfãos. 🤖 — feito. Ver `auditoria_formalismo.md`.
- [x] **B3.** Coerência das fórmulas do Cap.13 com a implementação. 🤖 — 3 discrepâncias documentadas (fator `coherence_bias` em Ψ_eff; intercepto de Q; 𝓜=M/(M+1) em 𝒞).
- [x] **B4.** Classificar estatuto de cada variável. 🤖 — tabela símbolo→estatuto pronta.
- [x] **B5.** Padronizar a ressalva "dados sintéticos". 🤖 — recomendação registrada; frase-padrão já no `.docx`.
- [!] **Achado crítico:** a camada social **S(t) / 𝒞_hum não é simulada** em nenhum script. Decidir como declarar isso no texto (recomendo: "esboço programático, não simulação"). 🧑

## Bloco C — Robustez computacional  → **reproduzido e reforçado**

- [x] **C1.** Reproduzir os 3 scripts. 🤖 — V3 reproduz o baseline **na precisão de máquina** (|Δ|≈0). Ver `reproducao_simulacoes.md`.
- [x] **C2.** Reexecutar V3 com n_runs/T maiores. 🤖 — n_runs=40, T=60: ordenação preservada, separação mantida (AUC=1,0), CV 3–7%.
- [x] **C3.** Verificar determinismo/sementes. 🤖 — modelos determinísticos por seed; documentado.
- [x] **C4.** Não sobrescrever o baseline. 🤖 — saídas em `reforco_outputs/`.
- [~] **C5.** Substituir/confrontar dados sintéticos com empíricos. 🤖→🧑 — **confronto inicial feito** (ver `confronto_empirico.md`): predições centrais confirmadas pela literatura; mapa de datasets abertos + protocolo definido. Recomputo sobre EEG bruto pendente de acesso a dados (bloqueado nesta sessão).

## Bloco D — Arquitetura editorial  → **andaime pronto; expansão pendente**

- [x] **D1.** Sumário consolidado. 🤖 — ver `andaime_editorial.md`.
- [x] **D2.** Mapa de lacunas por capítulo. 🤖 — feito (caps. 3, 5, 7 e 11 são os mais carentes).
- [~] **D3.** Padronizar chamadas de referência no corpo. 🤖 — números [n] inseridos na versão limpa; falta a passagem final autor-data se preferir esse estilo.
- [~] **D4.** Expandir capítulos em prosa. 🔁🧑 — **Cap. 3 expandido** (`Cap3_expandido.md`), aguarda sua revisão/merge. Próximos: 5→7→11→(converter listas em 4,6,10,12).
- [ ] **D5.** Revisão em camadas antes de publicar. 🔁
- [~] **D6.** Versão editorial. 🤖 — **compilação limpa em DOCX pronta** (`Consciencia_versao_editorial_limpa.docx`); a versão *expandida* depende de D4.

## Bloco E — Higiene do repositório  → **feito**

- [x] **E1.** Consolidar READMEs de `dados atuais/`. 🤖 — `README_dados_consolidado.md`.
- [!] **E2.** Resolver duplicatas de figuras / CSV. 🧑 — **não consigo apagar arquivos no seu disco a partir desta sessão** (sem shell no seu computador). Lista exata para você deletar em `dados atuais/`: `summary2.csv`, `Toy_model_summary_by_regime.csv` (ambos são dados do V2, duplicados de `Consciousness_Model_V2_Summary.csv`), e as figuras redundantes `anxiety_indices 2.png`, `anxiety_phase 2.png`, `deep_sleep_indices 2.png`, `deep_sleep_phase 2.png`, `reflex_indices 2.png`, `reflex_phase 2.png`, `regime_comparison 2.png`, `wake_indices 2.png`, `wake_phase 2.png`, `wake_phase 3.png`.
- [x] **E3.** `requirements.txt` revisado. 🤖 — criado.
- [x] **E4.** Registrar mudanças na documentação. 🤖 — estes relatórios.

---

## Registro de execução (2026-08-05)

Executado nesta sessão: verificação bibliográfica completa (4 verificadores em paralelo), auditoria de formalismo texto↔código, reprodução exata + reforço estatístico das simulações, andaime editorial (sumário + lacunas), higiene do repositório e compilação de uma versão editorial limpa em DOCX com bibliografia verificada.

Artefatos gerados: `verificacao_referencias.md`, `auditoria_formalismo.md`, `reproducao_simulacoes.md`, `andaime_editorial.md`, `README_dados_consolidado.md`, `requirements.txt`, `Consciencia_versao_editorial_limpa.docx`, e saídas em `reforco_outputs/`.

## O que agora depende de você (🧑)
1. **A5** — confirmar quais livros foram lidos integralmente (libera os verbos "mostra/demonstra").
2. **A4/B5** — aprovar os 3 ajustes de atribuição/escopo e a declaração de que S(t) é esboço, não simulação.
3. **D4** — dizer por qual capítulo começar a expansão (sugiro Cap. 3).
4. **E2** — confirmar deleção das duplicatas de CSV/figuras.
5. **C5** — se/quando houver dados empíricos para confrontar o modelo.
