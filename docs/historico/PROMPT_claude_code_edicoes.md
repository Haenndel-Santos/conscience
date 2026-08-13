# Prompt para o Claude Code — aplicar as edições do Cap. 11 e das Referências

Você é o Claude Code atuando no repositório local do projeto **Conscience** (`C:\Haenndel Projects\conscience`), na branch `revisao-2026-08`. O manuscrito é o arquivo **`Versao atual.md`**.

Já existe um arquivo com as edições exatas a aplicar: **`_revisao_2026-08-05/edicoes_cap11_e_referencias.md`**. Ele é a **fonte da verdade** — contém os blocos "find → replace" literais. Sua tarefa é aplicar essas três edições em `Versao atual.md`, verificar e commitar.

## Antes de começar
- Confirme que está na branch `revisao-2026-08` (`git status`). Se não estiver, faça checkout dela.
- Confirme que o working tree está limpo antes de editar (para o diff sair isolado).
- **Leia primeiro** `_revisao_2026-08-05/edicoes_cap11_e_referencias.md` na íntegra e use o texto de lá exatamente como está.

## Regras invioláveis (do `.codex/PROJECT_RULES.md`)
- Não invente nada. Aplique apenas o que está no arquivo de edições.
- Não reescreva outras partes do manuscrito. Só as três edições abaixo.
- Preserve a voz autoral e o estilo de citação **em bloco** `([domínio](url))` que o corpo do texto já usa (NÃO converta para marcadores numéricos [n] agora — isso é outra tarefa).
- Não renumere a lista de Referências existente; apenas substitua o item 13 e acrescente o item 29.

## As três edições (todas em `Versao atual.md`)

**Edição 1 — Cap. 11, subseção "Sonho":** inserir o novo parágrafo (o que começa com *"Um primeiro confronto com dados reais…"*) logo **após** o parágrafo que termina em *"…sugere que essa camada é empiricamente acessível."* e **antes** de `### Psicodélicos`. Use o texto exato do arquivo de edições (Edição 1).

**Edição 2 — Cap. 11, subseção "Trauma":** substituir **todo** o parágrafo atual da subseção Trauma (o que começa com *"O trauma é talvez o teste mais exigente — e aqui a teoria oferece uma interpretação…"*) pelo novo parágrafo do arquivo de edições (Edição 2), que passa a citar Lanius et al. (2010) no estilo em bloco `([psychiatryonline.org](…))`. A frase de ressalva antiga ("qualquer referência precisa … exige verificação textual") deve desaparecer, pois a referência agora existe e está verificada. A menção opcional a Nicholson/Lanius (2015) é **opcional** — só inclua se quiser reforçar; caso inclua, mantenha-a exatamente como no arquivo de edições.

**Edição 3 — seção "Referências":**
- (3a) Substituir o **item 13** (Whyte et al., hoje terminando em "confirmar DOI/paginação final na prova") pela forma final do arquivo de edições (Physics of Life Reviews 2026, vol. 56; PII e arXiv; DOI/paginação a confirmar na prova).
- (3b) Após o item **28** (McEwen) e **antes** da *Nota* final, inserir o novo subtítulo `### Referência adicionada nesta revisão (trauma, Cap. 11)` seguido do **item 29** (Lanius et al. 2010), conforme o arquivo de edições.
- (3c) Na *Nota* final, trocar "as referências 26–28 foram verificadas… em 2026-08-05" por "as referências **26–29** foram verificadas contra PubMed/página do periódico em 2026-08-05".

## Verificação (obrigatória antes do commit)
- Rode `git diff Versao atual.md` e confirme que **apenas** essas três edições apareceram — um parágrafo novo na subseção Sonho, o parágrafo da subseção Trauma substituído, e as três mudanças na seção Referências. Nenhuma outra linha deve mudar.
- Confirme que os blocos de citação novos estão bem formados (`([psychiatryonline.org](https://psychiatryonline.org/doi/10.1176/appi.ajp.2009.09081168))`).
- Confirme que a lista de referências continua com numeração contígua (…, 28, [novo subtítulo], 29) e que a Nota final foi atualizada.

## Commit
- Faça **um** commit descritivo, por exemplo: `Cap.11: confronto empírico do REM + citação de trauma (Lanius 2010); finaliza ref. Whyte et al. (2026) e adiciona ref. 29`.
- **Não** faça push.

## (Opcional) Regenerar o entregável
Se quiser deixar pronto para compartilhar, regenere a versão editorial limpa em **DOCX e PDF** a partir do `Versao atual.md` já editado (pandoc), nomeando com a data. Não é obrigatório.

## Relatório final (em português)
Ao terminar, escreva um resumo curto: quais trechos mudaram (com o hash do commit), a confirmação de que o `git diff` ficou isolado às três edições, e qualquer pendência (por exemplo, o DOI/paginação do Whyte a confirmar na prova, ou a decisão sobre incluir a ref. opcional de 2015).
