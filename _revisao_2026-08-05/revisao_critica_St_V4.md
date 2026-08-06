# Revisão crítica — camada social S(t) (V4)

Data: 2026-08-05 · Objeto: `dados atuais/consciousness_model_v4_social.py` e o relatório do Claude Code (3 cenários, 6 agentes). Autor da revisão: revisão Cowork.

## Veredito em uma frase
A implementação está **correta e fiel à fórmula aditiva do Cap. 13**, e a diligência foi boa (o bug de M_r foi pego e unificado). Porém, o número de destaque é em grande parte **tautológico**, e o achado realmente defensável é outro. O fator limitante não é o código — é a **própria fórmula** (aditiva e linear).

## 1. A AUC=1,0 de S é definitória, não uma descoberta
S foi definido como função da transmissão (P_u) e do reconhecimento (R_a, com M_r destravado só sob R_a). Os três cenários se distinguem *exatamente* por transmissão e reconhecimento. Logo, S crescer de privado → compartilhado → ratificado está **garantido por construção**. É o risco que havíamos sinalizado ("o cenário embutindo a resposta").
→ **Ação:** no manuscrito/relatório, não escrever "a predição do Cap. 9 se confirmou". Escrever "a operacionalização se comporta como projetada". A AUC de S é teste de consistência, não evidência.

## 2. O resultado defensável é o 𝒞_base no acaso (0,46)
Como o canal social é desacoplado da dinâmica interna, o índice privado é **comprovadamente cego** à diferença entre saber em privado e saber em comum. Isso demonstra **não-redundância**: a camada social não é recuperável do índice privado, então 𝒞_hum = 𝒞_base + w5·S **não é dupla contagem**.
→ **Ação:** liderar a narrativa com isto, não com a AUC de S.

## 3. Crítica de design (é teoria, não código)

**3a. Desacoplamento é fiel à fórmula, mas fino diante da teoria.** O Cap. 9 (e Thomas et al.) afirma que o common knowledge *transforma* a coordenação — faz coisas no mundo. No V4, S é aditivo e nunca toca o estado dos agentes: a ratificação muda o índice, mas não muda o que os agentes *fazem*. Isso é "socialidade como leitura", não "socialidade como regime".

**3b. Common knowledge deveria ser regime/limiar, não gradiente linear.** A passagem "compartilhado → comum" é uma descontinuidade (Thomas et al.; e o próprio Cap. 8 do manuscrito, sobre regimes vs gradientes). Aqui está como S linear com contador M_r de 0/1/2. Tornar a etapa ratificação→common-knowledge uma não-linearidade/limiar faria o conhecimento comum *emergir* como transição de fase — mais fiel à teoria e não-tautológico.

## 4. O teste não-circular que falta (alvo da V5)
Acrescentar uma **tarefa de coordenação com risco** (tipo stag-hunt: a ação coordenada só compensa se os outros também a tomarem; caso contrário, é pior que a ação segura). Medir o **sucesso comportamental de coordenação** nos três cenários. Predição falsificável: o cenário *compartilhado-não-ratificado* **deve falhar** em coordenar, apesar de P_u alto — porque conhecimento compartilhado não basta para justificar a ação arriscada; é preciso saber que os outros sabem (common knowledge). Se a coordenação subisse suavemente com P_u independentemente da ratificação, isso **refutaria** a tese. Esse é o experimento que permite afirmar que a camada social *faz* algo. (Espelha o paradigma empírico de Thomas et al. e a intuição do "email game" de Rubinstein.)

## 5. Prosa do manuscrito
Bom que o Cap. 13 já diz "minimamente simulado". Garantir que o texto ao redor afirme apenas o mostrado — a dimensão social é **não-redundante** com o índice privado — e **não** que o modelo "demonstra common knowledge" ou consciência intersubjetiva. Evitar "confirma" para S.

## Resumo das ações
1. Reescrever a leitura do resultado (não-redundância como achado; AUC de S como consistência).
2. V5: (a) feedback da ratificação no estado/valoração individual; (b) limiar/não-linearidade para common knowledge; (c) tarefa de coordenação com risco como teste não-circular, com controle mostrando que compartilhado-não-ratificado falha.
3. Manter as ressalvas de honestidade (proxy sintético; contador raso; sinal probabilístico ≠ teoria da mente).
