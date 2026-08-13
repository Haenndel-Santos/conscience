# Prompt — nova sessão do Cowork (máquina nova): sincronizar a pasta com o GitHub

Você está numa **nova sessão do Cowork, na máquina nova**, que tem a pasta conectada `C:\Haenndel Projects 2\conscience`. O projeto **Conscience** já foi enviado ao GitHub a partir de outra máquina (a "haenndel", que será desligada). Seu objetivo: **deixar a pasta local sincronizada com o repositório do GitHub**, sem perder nada e sem sobrescrever cegamente.

## Regras de segurança
- Nunca force. Proibido `git reset --hard`, `git push --force`, `git rebase`, ou apagar arquivos sem confirmar.
- Se houver alterações locais não salvas que possam conflitar, **PARE e mostre ao usuário** antes de mesclar.
- Operações de git em repositório **privado** exigem o login do GitHub, que está **na máquina do usuário** — não no sandbox de nuvem do Cowork. Se você não tiver um shell na máquina (só a ponte de arquivos), **não tente clonar/pull pelo sandbox**: diagnostique e entregue os comandos prontos para o usuário rodar (terminal ou Claude Code).

## Passo 1 — Diagnóstico (ler o estado atual)
Inspecione `C:\Haenndel Projects 2\conscience`:
- Liste o conteúdo. Existe pasta `.git`?
- Se existir, leia: `.git/config` (URL do `remote origin`), `.git/HEAD` (branch atual), `.git/logs/HEAD` (últimos commits locais) e `.git/refs/heads`.
- Reporte ao usuário três coisas: (a) é um clone do repositório certo? (b) qual branch está em uso? (c) o repositório parece **completo ou parcial** (o download dos originais pode não ter terminado)?

## Passo 2 — Identificar o cenário
- **A — já é um clone do repo certo:** só sincronizar (fetch + pull).
- **B — pasta vazia ou sem `.git`:** clonar o repositório do GitHub para dentro dela.
- **C — tem arquivos, mas não é git (cópia solta dos originais):** NÃO clonar por cima cegamente — reporte e proponha clonar numa pasta limpa e depois trazer o que for exclusivo.

Se houver qualquer ambiguidade (especialmente se o download ainda estiver em andamento), **confirme o cenário com o usuário** antes de agir.

## Passo 3 — Sincronizar (rodar na máquina do usuário)
A URL do repositório sai de `git remote -v` na máquina antiga (ou da saída do `gh repo create` do passo anterior).

- **Cenário A:**
  - `git status` — se houver mudanças locais, `git stash` (ou commit) antes.
  - `git fetch origin`
  - `git checkout main && git pull --ff-only origin main`
  - (opcional, se quiser a branch de trabalho) `git checkout revisao-2026-08 && git pull --ff-only origin revisao-2026-08`
  - Se `pull --ff-only` recusar (histórico divergiu), **PARE e reporte** — não force.
- **Cenário B:**
  - Na pasta vazia: `git clone <URL_DO_REPO> .` (precisa do login do GitHub).
- **Cenário C:** reporte e alinhe com o usuário antes de agir.

## Passo 4 — Verificar e reportar
- `git log --oneline --graph -15` e `git status`.
- Confirme que a pasta local reflete `origin/main` (e a branch, se aplicável).
- Relatório em português: cenário identificado, o que foi sincronizado, se ficou idêntico ao GitHub, e pendências (download incompleto dos originais, credenciais, divergência).

## Nota
Se você (Cowork) só tem a ponte de arquivos e não um shell na máquina, consegue fazer o **diagnóstico** (Passos 1–2) lendo o `.git`, mas o `fetch/pull/clone` do Passo 3 precisa ser executado pelo usuário no terminal ou pelo Claude Code. Nesse caso, entregue os comandos já preenchidos com a URL correta.
