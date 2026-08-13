# Prompt para o Claude Code — commit + push + merge no GitHub (com segurança)

Você é o Claude Code no repositório local do projeto **Conscience**. Rode isto **na máquina onde existe a branch `revisao-2026-08`** (a "haenndel", que será desligada em breve — **preservar o trabalho é a prioridade nº 1**). Objetivo: commitar o trabalho pendente, enviar ao GitHub e fazer o merge na `main`.

## Regras de segurança (leia antes de agir)
- **Preservar primeiro:** faça o `push` da branch **antes** de qualquer merge. O push é o backup.
- **NÃO commitar dados brutos nem ambientes.** O dataset de propofol tem ~3,4 GB e há downloads de EEG (Sleep-EDF) — se isso for para o GitHub, o push quebra e o repositório fica inutilizável. Exclua `.venv/`, `__pycache__/`, `*.pyc`, `*.edf`, `*.edf.gz`, `*.mat`, `*.set`, `*.fif`, `*.npy` grandes e quaisquer pastas de download bruto. **Verifique tamanhos antes de dar `git add`.**
- **NÃO** force-push, **NÃO** reescreva histórico, **NÃO** rode `git rebase`, `reset --hard` ou `filter-branch`.
- Se faltar autenticação/remote e não der para resolver com segurança, **pare e reporte** — não invente credenciais nem URLs.

## Passos

1. **Situação.** `git status`, `git branch --show-current`, `git log --oneline -20`. Confirme que está em `revisao-2026-08` (senão `git checkout revisao-2026-08`).

2. **Higiene de `.gitignore` (crítico).** Cheque dados grandes rastreados ou prestes a entrar:
   - `du -sh .venv "dados atuais" recompute_empirico_sleepedf recompute_empirico_v2 2>/dev/null` e `git status --porcelain`.
   - Atualize/crie `.gitignore` com: `.venv/`, `__pycache__/`, `*.pyc`, `*.edf`, `*.edf.gz`, `*.mat`, `*.set`, `*.fif`, `*.npy` (se grandes), e as pastas de download bruto dentro de `recompute_empirico*`.
   - Se algum dado grande **já** estiver rastreado, remova do índice sem apagar do disco: `git rm --cached -r <caminho>`, e adicione ao `.gitignore`.
   - Reporte o que foi excluído.

3. **Stage do que deve ir.** Só depois do `.gitignore` garantido: scripts `.py`; markdown (`Versao atual.md`, `PLANO_ESTRATEGICO_cientifico.md`, pasta `embasamento/`, `capitulos/`, `RELATORIO_claude_code.md`, `CHECKLIST_pendencias.md`, os `PROMPT_*.md`, `_revisao_2026-08-05/`); tabelas de resultado pequenas (CSV/PNG de resumo) — **sem** dados brutos. Então `git add -A`.

4. **Commit.** Mensagem clara, ex.: `Revisão 2026-08: expansões, formalismo, empírico v2, embasamento (Frente A) e planos`.

5. **Remote GitHub.** `git remote -v`.
   - Se já existe `origin` no GitHub, use-o.
   - Se NÃO existe: `gh auth status`. Se autenticado: `gh repo create conscience --private --source=. --remote=origin` (ajuste o nome se preferir). Se `gh` não estiver autenticado, **pare** e peça `gh auth login` ou a URL do remote. Prefira remote **HTTPS**.

6. **Push da branch (backup — faça já).** `git push -u origin revisao-2026-08`. Confirme que apareceu no GitHub **antes** de prosseguir.

7. **Merge na `main`.**
   - `git checkout main` (se a `main` não existir localmente, **reporte antes de agir** — pode ser preciso criá-la a partir do commit inicial).
   - `git merge --no-ff revisao-2026-08 -m "Merge revisao-2026-08 na main"`.
   - `git push origin main`.
   - *(Alternativa via GitHub, se preferir o merge pela interface: `gh pr create --base main --head revisao-2026-08 --fill` e depois `gh pr merge --merge`.)*

8. **Verificação.** `git log --oneline --graph -15`; confirme que a `main` remota contém o merge; reporte a **URL do repositório** e a do **commit de merge**.

## Relatório final (em português)
O que foi commitado; o que foi **excluído** do versionamento (dados brutos/.venv) e por quê; a URL do repositório no GitHub; e se o merge na `main` foi concluído ou se algo precisou parar para sua decisão.
