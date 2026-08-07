# Nota — Frente F (V5): teste não-circular de common knowledge

Data: 2026-08-07. Resultado da execução real de `dados atuais/consciousness_model_v5_social.py` (parâmetros default, 80 trials/cenário), interpretado por um agente após a execução do autor — mesma disciplina de honestidade das notas anteriores (`nota_anestesia.md`).

## O que foi testado

A V4 (`consciousness_model_v4_social.py`) tinha dois problemas documentados: o resultado principal era quase tautológico (S era construído a partir das mesmas variáveis que definem os cenários) e a camada social ficava desacoplada do comportamento dos agentes. A V5 corrige os dois com um teste que podia falhar: um jogo de coordenação com risco real (tipo stag-hunt), em que cada agente escolhe entre uma ação segura e uma ação arriscada que só compensa se um número suficiente de agentes também a escolher — e o sucesso dessa coordenação, não o índice social em si, é a métrica-alvo.

## Resultado

| Cenário | Taxa de sucesso de coordenação | P_u médio na decisão | K_ck médio na decisão |
|---|---|---|---|
| privado | 0,000 | 0,0 | 0,000 |
| compartilhado (não ratificado) | 0,000 | 1,0 | 0,000 |
| ratificado (common knowledge) | **0,913** | 1,0 | 1,000 |

**Ablação (a) — remoção do sinal de ratificação:** com o feedback do indicador de common knowledge desligado, a coordenação de "ratificado" colapsa para 0,000 — o mesmo nível dos outros dois cenários. Isso é evidência de que o mecanismo alegado (não algum outro efeito não controlado) é de fato o responsável pelo resultado.

**Ablação (b) — checagem de não-circularidade:** "compartilhado" teve P_u tão alto quanto "ratificado" (1,0 nos dois) — ou seja, a informação chegou igualmente a todos — mas não coordenou. Isso é a evidência central de que é especificamente o reconhecimento recíproco (não a mera amplitude da informação) que habilita a coordenação neste teste.

**Sweep de p_ack (transição de fase):** o sucesso de coordenação sobe de 0% (p_ack≈0) para ~90-100% (p_ack≈0,05-0,08) numa faixa de transição real, não um salto instantâneo de um único ponto para outro. Há uma queda não-monotônica no topo da faixa testada (p_ack=0,12 e 0,20 caem para 0,80, depois de picos de 0,96-1,00 em p_ack=0,05-0,08) — mais provavelmente ruído amostral (só 25 trials por ponto) do que um efeito real; não foi investigada a fundo. Registrado como está, sem forçar uma leitura.

## Leitura honesta

Os três critérios que o desenho anti-circularidade do teste foi feito para poder revelar (padrão privado<compartilhado<ratificado; não-circularidade via P_u; colapso na ablação) **se confirmaram na execução real**. Dentro desta operacionalização mínima, a predição qualitativa do Cap. 9 — que o conhecimento comum habilita uma coordenação arriscada que o conhecimento apenas compartilhado não habilita — é internamente consistente e passou no teste que foi desenhado para poder falhar.

Isso **não** é validação empírica de nada sobre cognição social real, comunicação humana real, ou consciência de máquina — é uma simulação sintética de prova de conceito, com proxies operacionais simples (P_u/R_a/M_r herdados da V4; um jogo de coordenação de 2 ações; feedback linear simples sobre um traço de memória). Ver a seção "HONESTIDADE METODOLÓGICA" na docstring do script para a lista completa de ressalvas.

## Parágrafo sugerido para o Cap. 9 (rascunho — decisão do autor incorporar ou não, ver CHECKLIST_pendencias.md, item R7)

> Uma instanciação mínima e sintética do modelo (V5) mostra que, dado um jogo de coordenação com risco, o conhecimento comum (reconhecimento recíproco de que os outros também sabem) habilita uma coordenação comportamental arriscada que o conhecimento meramente compartilhado (informação amplamente distribuída, mas sem reconhecimento recíproco) não habilita — mesmo quando os dois cenários têm exatamente a mesma informação disponível. O resultado sobreviveu a uma ablação de controle (remover o mecanismo de reconhecimento recíproco colapsa a coordenação de volta ao nível basal) e a uma checagem de não-circularidade (o cenário "compartilhado" teve acesso à informação tão amplo quanto o "ratificado", mas não coordenou). Este é um resultado de simulação sintética de prova de conceito, coerente com a literatura de common knowledge (Thomas et al. 2014, 2016) e com o email game de Rubinstein — não uma demonstração de cognição social real ou de consciência intersubjetiva.

## Arquivos relacionados

- Script: `dados atuais/consciousness_model_v5_social.py`.
- Saídas completas da execução do autor: `dados atuais/social_v5_outputs/` (no computador do autor — não replicadas neste documento além dos números-resumo acima).
- `embasamento/registro_falsificabilidade.md`, predição 5.2 (atualizada com este resultado).
- `CHECKLIST_pendencias.md`, Bloco R.
