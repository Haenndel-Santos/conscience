# Andaime Editorial — do núcleo ao livro

Data: 2026-08-05 · Base: `Versao atual.txt`. Objetivo: consolidar sumário (D1) e mapear, capítulo a capítulo, o que falta para virar livro (D2).

## Sumário consolidado (D1)

Estrutura atual identificada no núcleo (título: *Consciência como Regime Integrado — Corpo, Gradiente, Determinismo Estratificado e Coordenação Intersubjetiva*):

0. Nota metodológica
1. Introdução — a aposta integrativa e os cinco compromissos
2. Cap. 1 — A origem integrativa da consciência
3. Cap. 2 — Corpo, interocepção e constituição da experiência
4. Cap. 3 — Stress, alostase e deformação do campo consciente
5. Cap. 4 — Causalidade estratificada e comportamento
6. Cap. 5 — Agência integrada e crítica ao livre-arbítrio metafísico
7. Cap. 6 — Automação inteligente e economia da consciência
8. Cap. 7 — Evolução distal, replicadores e veículos
9. Cap. 8 — Não linearidade, integração diferenciada e regimes
10. Cap. 9 — Common knowledge, ratificação pública e consciência intersubjetiva
11. Cap. 10 — Diálogo com Active Inference e Free Energy Principle
12. Cap. 11 — Sonho, psicodélicos, animais e trauma como testes de estresse
13. Cap. 12 — Consciência biológica e inteligência artificial
14. Cap. 13 — Esboço formal revisado
15. Conclusão

**Faltam, para leitura como livro:** prefácio, sumário paginado, seção de Referências (agora disponível — ver `verificacao_referencias.md`) e, possivelmente, um capítulo de "Programa empírico" que descreva as simulações como método (hoje elas aparecem diluídas na nota metodológica e no Cap. 8/13).

## Duas correções estruturais imediatas (antes de qualquer versão pública)

1. **Remover o texto de bastidor.** O arquivo começa com "Perfeito. Abaixo está uma reescrita de núcleo…" e termina com "Se você quiser, o próximo passo mais útil é eu transformar esse texto…". O `PROJECT_RULES.md` proíbe explicitamente linguagem como "esta versão", "anteriormente", "o usuário pediu". Esses trechos devem sair da versão editorial.
2. **Reduzir bullet points nos capítulos argumentativos.** Caps. 4, 6, 10 e 12 usam listas onde o `PROJECT_RULES` pede prosa contínua com frases-tese. Converter em parágrafos.

## Mapa de lacunas por capítulo (D2)

| Cap. | Estado | O que falta |
|---|---|---|
| Nota metod. | Sólida | Acrescentar que a camada social (S) é esboço, não simulação (ver auditoria de formalismo). |
| Introdução | Forte | Ok; talvez uma frase-tese de abertura mais memorável. |
| 1 — Origem integrativa | Bem desenvolvido | Manter; é um dos capítulos mais maduros. Bom tratamento do hard problem "relocalizado". |
| 2 — Corpo/interocepção | Bem desenvolvido, bem citado | Corrigir grafia Loescher; confirmar ano das refs (ver bibliografia). |
| 3 — Stress/alostase | **Curto** | Falta um **exemplo concreto** (ex.: caso clínico de stress crônico) e amarração mais explícita ao índice 𝒞. Introduz dois princípios sem ilustrá-los. |
| 4 — Causalidade estratificada | Depende de listas | Converter a lista de "profundidades temporais" em prosa; dar um exemplo que percorra os níveis num único ato. |
| 5 — Agência integrada | Bom, **curto** | Falta exemplo (dependência química, responsabilidade penal) que mostre "agência sem livre-arbítrio metafísico" na prática. |
| 6 — Automação inteligente | Depende de listas | Prosa + exemplo (dirigir no automático, erro que "chama" a consciência). |
| 7 — Evolução/Dawkins | **Curto** | Reamarrar ao núcleo integrativo; hoje termina reconhecendo o limite mas sem costurar de volta à experiência. |
| 8 — Não linearidade/regimes | Bom, conecta às simulações | Referenciar explicitamente os números do modelo (saturação, thresholds) como ilustração, com a ressalva "sintético". |
| 9 — Common knowledge | Bom, formaliza S(t) | **Declarar que S(t) não é simulado.** Atribuir corretamente Thomas et al. (2016) em vez de "Pinker". |
| 10 — FEP/Active Inference | Bom posicionamento | Prosa nas listas; ajustar escopo da ref. "beautiful loop" (sono não é foco). |
| 11 — Sonho/psicodélicos/animais/trauma | **Subseções curtas** | Cada caso deve *testar* a teoria, não ser anexo. **Trauma está sem citação** — adicionar fonte ou marcar como interpretação. |
| 12 — IA | Forte, previsão diferencial clara | Prosa nas listas; manter a previsão sobre corporificação como ponto alto. |
| 13 — Esboço formal | Estrutura ok | Aplicar as correções da auditoria de formalismo (interceptos, 𝓜=M/(M+1), versão canônica V3, marcar S/𝒞_hum como não implementados). |
| Conclusão | Forte | Manter a frase-núcleo final; é boa. |

## Sequência recomendada de expansão (D4 — ritmo do autor)

Prioridade por relação custo/impacto: **3 → 5 → 7** (os três capítulos curtos que mais ganhariam com um exemplo cada) → depois **11** (transformar as quatro subseções em testes reais) → por fim conversão de listas em **4, 6, 10, 12**. Cada expansão deve passar por `theory-core-guardian` (coerência) e `formalism-and-model-guardian` quando tocar variáveis.
