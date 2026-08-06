# Prompt para o Claude Code — V5 da camada social (teste não-circular de common knowledge)

Você é o Claude Code no projeto Conscience (`C:\Haenndel Projects\conscience`, branch `revisao-2026-08`). A V4 tirou S(t) do papel, mas uma revisão crítica apontou que o resultado principal foi **tautológico** (S foi construído a partir do que define os cenários) e que a camada social ficou **desacoplada** do comportamento. Sua tarefa é construir a **V5**, que corrige isso com um **teste não-circular**.

Leia antes (obrigatório): `_revisao_2026-08-05/revisao_critica_St_V4.md` (a crítica que orienta este trabalho), `dados atuais/consciousness_model_v4_social.py`, e o Cap. 9 de `Versao atual.md`. Siga `.codex/PROJECT_RULES.md`. Trabalhe na branch `revisao-2026-08`, commits pequenos, **sem push**. Não sobrescreva a V4 — crie arquivos novos.

## Objetivo
Mostrar (ou falhar honestamente em mostrar) que o **common knowledge faz algo que o conhecimento apenas compartilhado não faz** — ou seja, que a camada social muda um **resultado comportamental**, não apenas o índice. O experimento precisa poder **falhar**.

## Três mudanças em relação à V4

**1. Feedback da ratificação no estado individual.** A ratificação/common-knowledge deve realimentar a dinâmica interna dos agentes (ex.: modular a valoração/estado de forma que estar num estado publicamente ratificado altere a *disposição de agir*), não só entrar como termo aditivo no índice. Documente a escolha.

**2. Common knowledge como limiar (não gradiente).** Implemente um indicador de common knowledge com **não-linearidade/limiar** — ex.: `K_ck = sigmoid(ganho·(R_a·M_r − limiar))`, ~0 abaixo do limiar e saltando para ~1 acima. Faça um **sweep de p_ack** (probabilidade de reconhecimento) e mostre se há **transição de fase** (salto abrupto) em K_ck, e não uma rampa linear.

**3. Teste não-circular: tarefa de coordenação COM RISCO.** Este é o ponto central. Implemente um jogo de coordenação tipo **stag-hunt**: cada agente escolhe entre uma ação "segura" (retorno baixo garantido) e uma ação "coordenada" (retorno alto **se** um número suficiente de agentes também a escolher, e retorno pior que a segura caso contrário). A métrica-alvo é o **sucesso de coordenação comportamental** (fração de rodadas em que a coordenação arriscada dá certo) — um resultado que **não é o próprio S**.

## A predição falsificável (o coração do experimento)
- **privado:** sem sinal público → coordenação ~ acaso.
- **compartilhado-não-ratificado:** todos podem ter recebido o sinal (P_u alto), mas **sem** saber que os outros receberam → a teoria prevê que a coordenação arriscada **falha** (não se justifica arriscar sem saber que os outros sabem).
- **ratificado / common knowledge:** os agentes sabem que os outros sabem → a coordenação arriscada **tem sucesso**.

Se, ao rodar, a coordenação subir suavemente com P_u **independentemente** da ratificação, isso **refuta** a tese de que é o common knowledge (e não a mera informação compartilhada) que habilita a coordenação — e você deve reportar isso honestamente como refutação, não maquiar.

## Anti-circularidade (obrigatório — não "trapacear")
- Os agentes no cenário compartilhado-não-ratificado devem ter **a mesma informação e a mesma capacidade de agir** que no ratificado; a **única** diferença é saber que os outros também sabem. Não codifique a coordenação como uma consequência direta de P_u.
- Inclua **ablações de controle**: (a) remover o sinal de ratificação e confirmar que a coordenação colapsa; (b) confirmar numericamente que compartilhado-não-ratificado realmente não coordena, mesmo com P_u alto. Se qualquer controle não se comportar como esperado, relate.
- O retorno da ação coordenada deve depender do comportamento agregado real dos agentes, não de um rótulo de cenário.

## Saídas e verificação
- Novo arquivo `dados atuais/consciousness_model_v5_social.py`; saídas em `dados atuais/social_v5_outputs/` (não sobrescreva `social_outputs/` da V4).
- Reprodutibilidade por seed. Inclua o sweep de p_ack (transição de fase) e, se viável, uma checagem de robustez variando N e o limiar.
- Tabelas: sucesso de coordenação por cenário; K_ck, S, 𝒞_hum por cenário; curva de K_ck e de coordenação vs p_ack. Figuras correspondentes.

## Texto do manuscrito (só se os resultados sustentarem)
- Se o teste passar (coordenação sobe só no regime de common knowledge, com a fase de transição), atualize o Cap. 9 com um parágrafo **honesto e comedido**: uma instanciação mínima mostra que o conhecimento comum habilita uma coordenação arriscada que o conhecimento apenas compartilhado não habilita — coerente com Thomas et al. Marque como prova de conceito sintética.
- **Não** afirme que o modelo demonstra consciência intersubjetiva. Não use "confirma" para S. Se o teste falhar ou for ambíguo, registre isso no manuscrito e no relatório em vez de esconder.

## Relatório final (em português)
Definições operacionais (feedback, K_ck com limiar, jogo de coordenação e payoffs), resultado do teste (tabela de coordenação por cenário + curva vs p_ack), resultado das ablações de controle, se a predição passou/falhou/foi ambígua, limites honestos, e o que fica para uma V6. Atualize o `CHECKLIST_pendencias.md`. Commits pequenos, sem push.
