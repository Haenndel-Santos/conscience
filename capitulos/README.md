# Manuscrito — arquivos por capítulo

Cada capítulo do manuscrito *Consciência como Regime Integrado* vive em um arquivo Markdown separado nesta pasta, para facilitar revisão capítulo a capítulo. O prefixo numérico define a ordem de leitura.

| Arquivo | Conteúdo |
|---|---|
| [00_nota_metodologica.md](00_nota_metodologica.md) | Título do livro + Nota metodológica |
| [01_introducao.md](01_introducao.md) | Introdução |
| [02_capitulo_01.md](02_capitulo_01.md) | Cap. 1 — A origem integrativa da consciência |
| [03_capitulo_02.md](03_capitulo_02.md) | Cap. 2 — Corpo, interocepção e constituição da experiência |
| [04_capitulo_03.md](04_capitulo_03.md) | Cap. 3 — Stress, alostase e deformação do campo consciente |
| [05_capitulo_04.md](05_capitulo_04.md) | Cap. 4 — Causalidade estratificada e comportamento |
| [06_capitulo_05.md](06_capitulo_05.md) | Cap. 5 — Agência integrada e crítica ao livre-arbítrio metafísico |
| [07_capitulo_06.md](07_capitulo_06.md) | Cap. 6 — Automação inteligente e economia da consciência |
| [08_capitulo_07.md](08_capitulo_07.md) | Cap. 7 — Evolução distal, replicadores e veículos |
| [09_capitulo_08.md](09_capitulo_08.md) | Cap. 8 — Não linearidade, integração diferenciada e regimes |
| [10_capitulo_09.md](10_capitulo_09.md) | Cap. 9 — Common knowledge, ratificação pública e consciência intersubjetiva |
| [11_capitulo_10.md](11_capitulo_10.md) | Cap. 10 — Diálogo com Active Inference e Free Energy Principle |
| [12_capitulo_11.md](12_capitulo_11.md) | Cap. 11 — Sonho, anestesia, psicodélicos, animais e trauma como testes de estresse da teoria |
| [13_capitulo_12.md](13_capitulo_12.md) | Cap. 12 — Consciência biológica e inteligência artificial |
| [14_capitulo_13.md](14_capitulo_13.md) | Cap. 13 — Esboço formal revisado |
| [15_capitulo_14.md](15_capitulo_14.md) | Cap. 14 — Posicionamento frente a teorias rivais da consciência |
| [16_conclusao.md](16_conclusao.md) | Conclusão |
| [17_referencias.md](17_referencias.md) | Referências (101 itens numerados) |

## Origem e histórico

Estes arquivos foram gerados em 2026-08-05 a partir de `Versao atual.md` (a versão já corrigida na sessão de revisão desta data: bibliografia, estrutura editorial, formalismo do Cap. 13, expansão de capítulos). As citações no corpo do texto foram convertidas do estilo hiperlink inline para o estilo numerado `[n]`, adotado de `Consciencia_versao_editorial_limpa.docx` (a "versão editorial limpa" de uma sessão anterior) — essa era a única melhoria real que o `.docx` trazia; todo o resto dele estava desatualizado (Cap. 3 na versão curta antiga, Cap. 9 com o erro de atribuição a "Pinker", e as fórmulas do Cap. 13 corrompidas pela conversão Word → texto). Ver `RELATORIO_claude_code.md` na raiz do projeto para o histórico completo da revisão.

## Como este conjunto se relaciona com `Versao atual.md`

A partir de agora, **os arquivos desta pasta são a fonte de verdade** para edição capítulo a capítulo. `Versao atual.md`, na raiz do projeto, é **regenerado a partir destes arquivos** pelo script `build_manuscript.py` — não deve ser editado diretamente, porque qualquer edição direta nele seria perdida na próxima regeneração.

Para reconstruir o manuscrito completo em um único arquivo (por exemplo, antes de gerar DOCX/PDF):

```bash
python capitulos/build_manuscript.py
```

Isso sobrescreve `Versao atual.md` na raiz do projeto com a concatenação, na ordem certa, de todos os arquivos desta pasta.
