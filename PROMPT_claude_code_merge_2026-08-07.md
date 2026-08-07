# Prompt para o Claude Code — commit + push + merge no GitHub (sessão de 2026-08-07)

Você é o Claude Code no repositório local do projeto **Conscience**, na máquina "Haenndel Projects 2" (`C:\Haenndel Projects 2\conscience\conscience`). Objetivo: commitar todo o trabalho pendente da sessão de hoje (Frentes C, D, G, E e F), enviar a branch `revisao-2026-08` ao GitHub como backup, e depois fazer o merge na `main`.

Este prompt segue o mesmo modelo de segurança de `PROMPT_claude_code_git_push.md` (já existente no repositório, de uma sessão anterior) — leia-o também se quiser contexto adicional, mas trate ESTE prompt como a fonte de verdade para a execução de hoje.

## Contexto do que deve entrar no commit (para você escrever uma mensagem precisa, não para você conferir cegamente — confirme tudo com `git status`/`git diff` antes)

Nesta sessão (Cowork, 2026-08-07), sobre a branch `revisao-2026-08`:
- **Frente C concluída**: `scripts_para_rodar/integracao_diferenciada/` rodou na amostra completa (n=36 sujeitos válidos de 41) — resultado negativo para a interpretação de "integração diferenciada": a discriminação de LZc/PE por estágio de sono não sobrevive ao controle pela inclinação espectral 1/f.
- **Frente D concluída**: `scripts_para_rodar/anestesia_responsividade/` — replicou Newman et al. (2026), resultado positivo.
- **Frente G concluída**: `embasamento/registro_falsificabilidade.md` (27 predições com estatuto) e `scripts_para_rodar/estatistica/reforco_estatistico.py` (IC bootstrap, effect size, correção FDR) rodados sobre todos os resultados anteriores.
- **Frente E escrita, aguardando execução do autor** (ainda não rodada — não deve aparecer como "concluída" na mensagem de commit): `scripts_para_rodar/robustez_modelo/sensibilidade_v3.py` e `calibracao_v3.py`.
- **Frente F concluída**: `dados atuais/consciousness_model_v5_social.py` (V5 — teste não-circular de coordenação social) rodado; resultado positivo (passou nos 3 critérios de não-circularidade). Saídas em `dados atuais/social_v5_outputs/`.
- Documentos atualizados: `CHECKLIST_pendencias.md` (Blocos N–R), `embasamento/registro_falsificabilidade.md`, `embasamento/SINTESE_pilares.md`, `embasamento/nota_v5_social.md` (novo), `embasamento/nota_anestesia.md`, `recompute_empirico_v2/RELATORIO_v2.md`.

Confirme esta lista contra `git status` real antes de escrever a mensagem — não assuma que é exaustiva nem que nada mais mudou.

## Regras de segurança (leia antes de agir)

- **Preservar primeiro:** faça o `push` da branch **antes** de qualquer merge. O push é o backup.
- **NÃO commitar dados brutos nem ambientes.** Exclua `.venv/`, `__pycache__/`, `*.pyc`, `*.edf`, `*.edf.gz`, `*.mat`, `*.set`, `*.fif`, `*.npy` grandes, `dados_sleepedf/`, e a pasta extraída do propofol (`Sedation-RestingState/` ou equivalente) — e qualquer coisa dentro de `dados atuais/social_v5_outputs/` ou `scripts_para_rodar/*/*.png` que seja muito grande (checar tamanho; PNGs de figura normalmente são pequenos e OK, mas confirme). **Verifique tamanhos antes de dar `git add`.**
- **NÃO** force-push, **NÃO** reescreva histórico, **NÃO** rode `git rebase`, `reset --hard` ou `filter-branch`.
- Se faltar autenticação/remote e não der para resolver com segurança, **pare e reporte** — não invente credenciais nem URLs.
- Se encontrar qualquer arquivo com aparência de credencial/segredo (`.env`, chaves, tokens) nos itens a commitar, **pare e avise** em vez de commitar.

## Passos

1. **Situação.** `git status`, `git branch --show-current`, `git log --oneline -20`. Confirme que está em `revisao-2026-08` (senão `git checkout revisao-2026-08`).

2. **Higiene de `.gitignore` (crítico).** Cheque dados grandes rastreados ou prestes a entrar:
   - `git status --porcelain` e, para qualquer pasta suspeita, `du -sh <pasta>` (ou equivalente `Get-ChildItem -Recurse | Measure-Object -Property Length -Sum` no PowerShell).
   - Confirme que `.gitignore` já cobre `.venv/`, `__pycache__/`, `*.pyc`, `*.edf`, `*.edf.gz`, `*.mat`, `*.set`, `*.fif`, `*.npy` (se grandes), `dados_sleepedf/`, e as pastas de download bruto do propofol. Se faltar algo, adicione.
   - Se algum dado grande **já** estiver rastreado ou prestes a ser adicionado, remova/exclua do stage (`git rm --cached -r <caminho>` se já commitado antes, ou simplesmente não dê `git add` nele) e adicione ao `.gitignore`.
   - Reporte o que foi excluído.

3. **Stage do que deve ir.** Só depois do `.gitignore` garantido: todos os `.py` novos/alterados; todo `.md` novo/alterado (`CHECKLIST_pendencias.md`, `embasamento/*.md`, os `README_como_rodar.md`/`README_V5_como_rodar.md` novos, `recompute_empirico_v2/RELATORIO_v2.md`); CSVs/PNGs de resultado pequenos gerados pelos scripts (resumos, não dados brutos). Então `git add -A` (depois de já ter confirmado no passo 2 que não há dado grande no meio).

4. **Commit.** Mensagem clara e específica (não genérica), cobrindo o que de fato mudou — algo como:
   ```
   Frentes C/D/G concluídas (resultado final n=36; replicação Newman et al.; registro de falsificabilidade + reforço estatístico); Frente E escrita (aguardando execução); Frente F concluída (V5 — teste não-circular de coordenação social, resultado positivo)
   ```
   Ajuste conforme o que `git status`/`git diff` realmente mostrar.

5. **Remote GitHub.** `git remote -v`.
   - Se já existe `origin`, use-o.
   - Se não existir: `gh auth status`; se autenticado, `gh repo create conscience --private --source=. --remote=origin` (ajuste o nome se preferir); se `gh` não estiver autenticado, **pare** e peça `gh auth login` ou a URL do remote. Prefira HTTPS.

6. **Push da branch (backup — faça já).** `git push -u origin revisao-2026-08`. Confirme que apareceu no GitHub antes de prosseguir.

7. **Merge na `main`.**
   - `git checkout main` (se não existir localmente, **reporte antes de agir**).
   - Traga a `main` atualizada primeiro, se houver remoto: `git pull origin main` (sem rebase).
   - `git merge --no-ff revisao-2026-08 -m "Merge revisao-2026-08 na main: Frentes C/D/G concluídas, Frente F (V5) concluída, Frente E escrita"`.
   - Se houver conflito, **pare e reporte** os arquivos em conflito — não resolva automaticamente sem mostrar o que está em jogo.
   - `git push origin main`.
   - *(Alternativa via GitHub, se preferir merge pela interface: `gh pr create --base main --head revisao-2026-08 --fill` e depois `gh pr merge --merge`.)*

8. **Verificação.** `git log --oneline --graph -15`; confirme que a `main` remota contém o merge; reporte a URL do repositório e a do commit de merge.

## Relatório final (em português)

O que foi commitado (lista de arquivos/pastas, não só a mensagem); o que foi **excluído** do versionamento (dados brutos/.venv) e por quê; a URL do repositório no GitHub; a URL do commit de merge; e se algo precisou parar para decisão sua (conflito, falta de autenticação, arquivo suspeito).
