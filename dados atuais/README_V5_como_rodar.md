# V5 — teste não-circular de common knowledge: como rodar

`consciousness_model_v5_social.py` foi **escrito por um agente e não executado por ele nos parâmetros reais** — mesma regra de governança das Frentes C/D/E/G (`PLANO_ESTRATEGICO_cientifico.md` §0.1). O agente verificou sintaxe (`python -m py_compile`, passou) e rodou um teste de fumaça com parâmetros bem reduzidos (`--n-trials 6 --n-trials-sweep 3 --n-trials-robustez 2`, poucos agentes/segundos) para (a) confirmar que a lógica não quebra e (b) **calibrar** três parâmetros do jogo de coordenação (ver seção própria abaixo) — os números finais citados em qualquer relatório devem vir da execução real com os parâmetros default (ou maiores), não desse teste de fumaça.

## O que este script testa

Ver a docstring completa em `consciousness_model_v5_social.py` (leia antes de citar qualquer número deste script em qualquer lugar) e `PROMPT_claude_code_V5_social.md` (o prompt original que especificou esta Frente). Resumo: a V4 mostrou que S(t)/C_hum(t) discriminam cenários de common knowledge, mas de forma quase tautológica e desacoplada do comportamento dos agentes. A V5 corrige isso com três mudanças (feedback real na dinâmica individual; K_ck como indicador de limiar, não gradiente; e um jogo de coordenação tipo stag-hunt com risco real) e testa uma predição que **pode falhar**: que a coordenação comportamental arriscada só tem sucesso no cenário "ratificado" (common knowledge), não em "compartilhado" (informação ampla sem reconhecimento recíproco) nem em "privado".

## Calibração dos parâmetros do jogo (documentado para transparência)

Os parâmetros `feedback_gain`, `decision_threshold`, `decision_gain` e `k_ck_gain` **não são "de manual"** — foram calibrados pelo agente, por simulação, antes de fixar os defaults do script. Isso foi necessário porque a primeira tentativa (valores herdados "razoáveis" da V4, sem calibração) saturou TODOS os cenários em 100% de sucesso de coordenação — inclusive "privado", que não tem nenhuma camada social — porque o traço de memória `M` de um agente V3 no regime `wake`, sozinho, já converge para ~1,45-1,60 ao longo de T~30-35s por dinâmica própria do V3 (nada a ver com a camada social). Um limiar de decisão mal calibrado (ex.: 1,0) fica abaixo dessa convergência natural, então até "privado" coordena — o que não testaria nada.

O agente rodou um pequeno grid search (poucos trials, parâmetros reduzidos) para encontrar uma região em que:
- **privado** fique perto de 0% de sucesso (a dinâmica basal do V3, sem camada social, fica abaixo do limiar de decisão);
- **ratificado** fique claramente acima de 0% (idealmente >50-100%, quando o feedback de K_ck empurra M para cima do limiar).

O resultado desse teste de fumaça (8 agentes, T=35, seed=1, poucos trials) com os defaults finais (`k_ck_gain=40`, `feedback_gain=0,03`, `decision_threshold=1,75`, `decision_gain=10`):

```
privado:        0% de sucesso de coordenação
compartilhado:   0% de sucesso de coordenação (P_u médio na decisão = 1,0 — alto, mas sem efeito)
ratificado:    100% de sucesso de coordenação (K_ck médio na decisão = 1,0)
ratificado, ablação (a) sem feedback: 0% (colapsa de volta ao nível basal)
```

E o sweep de p_ack (probabilidade de reconhecimento) mostrou uma faixa de transição genuína (não um salto instantâneo de um único ponto para outro): a taxa de sucesso passa de 0% para ~33-100% conforme p_ack sobe de ~0,004 para ~0,015, com os demais parâmetros nos defaults.

**Isto NÃO é o resultado final do experimento** — é só a confirmação de que o ponto de partida dos parâmetros não está numa região trivialmente saturada (que não testaria nada) nem trivialmente nula (que também não testaria nada). O resultado que importa é o que o autor obtiver rodando os parâmetros default (`--n-trials 80` ou mais) — que pode, em princípio, divergir do padrão do teste de fumaça (mais trials reduzem ruído, mas não mudam a estrutura do teste). Se divergir marcadamente do padrão esperado, isso deve ser reportado como tal, não maquiado.

Se quiser recalibrar esses parâmetros (por exemplo, para tornar o teste "mais difícil" — menos saturado, com taxas de sucesso intermediárias em vez de 0%/100%), os quatro parâmetros relevantes estão documentados com comentários em `SocialLayerParamsV5` no topo do script.

## Dependência de outro arquivo do projeto

Importa `ConsciousnessSystemV3` e `default_regimes` de `consciousness_model_v3.py`, que deve estar na MESMA pasta (`dados atuais/`) — mesma convenção da V4 (`consciousness_model_v4_social.py`). Não precisa de `--model-dir`: o script insere a própria pasta (`Path(__file__).parent`) no `sys.path`.

## Dependências

Já devem estar todas instaladas no seu `.venv` (usadas pela V3/V4): `numpy`, `pandas`, `matplotlib`, `scikit-learn`. Nenhuma dependência nova.

## Comando

Rodando de dentro da pasta `dados atuais/`:

```
python consciousness_model_v5_social.py
```

Recomendado: rodar primeiro uma versão rápida para conferir que tudo funciona na sua máquina antes da execução completa:

```
python consciousness_model_v5_social.py --n-trials 15 --n-trials-sweep 8 --n-trials-robustez 5
```

Depois, a execução completa (defaults — `n_trials=80`, `n_trials_sweep=25`, `n_trials_robustez=15`, T=40):

```
python consciousness_model_v5_social.py
```

**Tempo esperado:** cada simulação individual (`run_scenario`) leva ~1-1,5s numa máquina comum. A execução completa com os defaults roda aproximadamente 80×3 (Monte Carlo principal) + 80×3 (ablação) + 14×25 (sweep de p_ack) + 3×3×3×15 (grade de robustez) + 3 (exemplos) ≈ 1.240 simulações — **estimativa de ~20-30 minutos**. Se estiver muito lento, reduza `--n-trials`/`--n-trials-sweep`/`--n-trials-robustez`; se quiser mais precisão (menos ruído no sweep e na robustez), aumente.

## Saídas esperadas (em `dados atuais/social_v5_outputs/`)

- `series_temporais_exemplo.csv` / `.png` — K_ck(t), M médio dos agentes, S(t), C_hum(t) para uma execução de exemplo por cenário.
- `monte_carlo_decisoes.csv` — dados brutos de todas as decisões do jogo (Monte Carlo principal).
- `resumo_coordenacao_por_cenario.csv` — **resultado central**: taxa de sucesso de coordenação, P_u/R_a/K_ck/M médios na decisão, por cenário.
- `ablacao_sem_feedback_resumo.csv` — ablação (a): coordenação com o feedback de K_ck desligado.
- `sweep_p_ack.csv` / `.png` — K_ck médio e taxa de sucesso de coordenação vs. p_ack (checagem de transição de fase).
- `robustez_n_e_limiar.csv` — taxa de sucesso por cenário, variando N de agentes (6/8/12) e o limiar de coordenação exigido (0,5/0,6/0,75).
- `README.md` — relatório narrativo gerado automaticamente pelo próprio script, com uma seção "Leitura preliminar automática" que resume mecanicamente os três critérios centrais (padrão previsto, não-circularidade, colapso na ablação) — **não é a interpretação final**, é um resumo de números para o agente revisar depois.

## Depois de rodar

Devolva a pasta `social_v5_outputs/` inteira (ou pelo menos os `.csv` e o `README.md` gerado) para um agente interpretar. Ele deve, seguindo a mesma disciplina de honestidade das Frentes C/D:
1. Conferir os três critérios centrais (ver "Leitura preliminar automática" no README gerado): o padrão privado<compartilhado<ratificado apareceu? "Compartilhado" ficou perto de "privado" apesar de P_u alto? A ablação (a) fez a coordenação de "ratificado" colapsar?
2. Examinar o sweep de p_ack: há uma transição relativamente abrupta, ou uma rampa suave e gradual? (isso não invalida o teste principal, mas é uma predição adicional específica do prompt original — "transição de fase" — que também deve ser reportada honestamente, seja qual for o resultado).
3. Se o teste passou nos três critérios: atualizar o Cap. 9 do manuscrito com um parágrafo comedido (nunca "confirma", nunca alegar consciência intersubjetiva real — ver seção "Texto do manuscrito" em `PROMPT_claude_code_V5_social.md`), `embasamento/registro_falsificabilidade.md` (predição 5.2, que hoje está ⭕ NÃO TESTADA), e `CHECKLIST_pendencias.md`.
4. Se o teste falhou ou ficou ambíguo em algum critério: registrar isso tal como está, sem maquiar — é exatamente o resultado que o desenho anti-circularidade foi feito para poder revelar.
