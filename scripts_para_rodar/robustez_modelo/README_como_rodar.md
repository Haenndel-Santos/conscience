# Frente E — Robustez e identificabilidade do modelo V3: como rodar

Estes scripts (`sensibilidade_v3.py`, `calibracao_v3.py`) foram **escritos por um agente e não executados por ele** — mesma regra de governança das Frentes C/D/G (`PLANO_ESTRATEGICO_cientifico.md` §0.1). A verificação do agente foi de **sintaxe** (`python -m py_compile`, passou nos dois) e de **execução em dados reduzidos** (`--T 5 --n-runs 2 --n-samples 6`, não os parâmetros reais) só para confirmar que a lógica não quebra — os números citados nos READMEs/relatórios não vêm desse teste de fumaça.

## Por que estes scripts existem

`PLANO_ESTRATEGICO_cientifico.md`, Frente E, pede uma resposta à crítica de que os regimes do modelo V3 (wake, anxiety, deep_sleep, reflex) se separam "por construção" — isto é, que os pesos do modelo podem estar implicitamente ajustados para produzir a separação desejada, tornando a separação uma tautologia em vez de uma descoberta. Dois ângulos, dois scripts:

1. **`sensibilidade_v3.py` — robustez.** A separação de regimes (AUC de C_idx entre pares de regimes) sobrevive a perturbações grandes e simultâneas em todos os pesos? Se sim, a separação não depende de ajuste fino — enfraquece a crítica. Se não, sustenta a crítica.
2. **`calibracao_v3.py` — identificabilidade.** Reproduzir a discriminação empírica real (AUC W-vs-N3 = 0,992, Sleep-EDF) é fácil (quase qualquer combinação de pesos já discrimina bem — sustenta "por construção") ou difícil (só uma região estreita do espaço de parâmetros funciona — sustenta um ajuste mais genuíno)? E os pontos de partida de uma otimização convergem para o mesmo lugar (identificável) ou para lugares muito diferentes (não-identificável)?

Nenhum dos dois scripts decide a questão sozinho — cada um produz uma peça do quadro. A seção "Leitura" no fim de cada saída é um guia de interpretação, não uma conclusão pronta (mesma disciplina da Frente C/G — resultado negativo é dado, não fracasso).

## Dependência de outro arquivo do projeto

Os dois scripts **importam** `consciousness_model_v3.py` (não reimplementam a dinâmica do modelo — seria arriscado e redundante reproduzir mal a EDO do V3). Por padrão, localizam esse arquivo em `dados atuais/`, dois níveis acima da pasta deste script (`scripts_para_rodar/robustez_modelo/`), assumindo a estrutura de pastas padrão do projeto. Se o layout for diferente na sua máquina, use `--model-dir "caminho\para\dados atuais"`.

## Dependências

Já devem estar todas instaladas no seu `.venv` (usadas pelo V3/V4): `numpy`, `pandas`, `matplotlib`, `scikit-learn`. Nenhuma dependência nova.

## Comandos

Rodando de dentro da pasta `scripts_para_rodar/robustez_modelo/`:

```
python sensibilidade_v3.py
python calibracao_v3.py
```

Os parâmetros default (`sensibilidade_v3.py`: n_runs=6, n_trials=8, T=20; `calibracao_v3.py`: n_samples=200, n_starts=5, n_runs=4, T=15) foram escolhidos para rodar em alguns minutos numa máquina comum. Se estiver lento, reduza (`--n-samples 80 --n-runs 2`); se quiser mais precisão, aumente (`--n-trials 15 --n-samples 400`).

Tempo esperado: `sensibilidade_v3.py` roda ~150-300 simulações do V3 (rápidas, sem I/O pesado) — segundos a poucos minutos. `calibracao_v3.py` roda mais simulações (busca aleatória + otimização multi-start) — pode levar de poucos minutos a ~10-15 minutos com os parâmetros default, dependendo da máquina.

## Saídas esperadas (nesta pasta)

De `sensibilidade_v3.py`:
- `sensibilidade_montecarlo.csv` / `.png` — AUC por task e magnitude de perturbação simultânea.
- `sensibilidade_oat.csv` / `.png` — AUC por task variando um peso por vez.
- `sensibilidade_fragilidade_resumo.csv` — menor magnitude de perturbação em que o AUC mediano cai abaixo de 0,85 / 0,70, por task.
- `resumo_sensibilidade.md` — narrativa + seção "Leitura".

De `calibracao_v3.py`:
- `calibracao_busca_aleatoria.csv` / `calibracao_histograma_auc.png` — AUC sob pesos sorteados amplamente.
- `calibracao_otimizacao_multistart.csv` — pesos finais e AUC de cada busca de coordenadas, a partir de múltiplos pontos de partida.
- `calibracao_identificabilidade.png` — AUC vs. cada peso individualmente.
- `resumo_calibracao.md` — relatório de identificabilidade + seção "Leitura".

## Depois de rodar

Devolva as 4 pastas de saída (ou pelo menos os `.md`/`.csv`) para um agente interpretar. Ele deve:
1. Verificar a fragilidade (`sensibilidade_fragilidade_resumo.csv`) e a fração de amostras com AUC alto na calibração (`resumo_calibracao.md`).
2. Atualizar `embasamento/SINTESE_pilares.md` (item M.1 do registro de falsificabilidade cita esta ressalva de "tautologia") e `embasamento/registro_falsificabilidade.md` (entrada M.1) com o resultado — positivo (robusto e/ou identificável) ou negativo (frágil e/ou não-identificável), com a mesma honestidade das Frentes C/D.
3. Atualizar `CHECKLIST_pendencias.md` (Bloco Q).
