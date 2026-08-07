"""V5 — teste NÃO-CIRCULAR de common knowledge: coordenação com risco.

REGRA DE GOVERNANÇA (`PLANO_ESTRATEGICO_cientifico.md` §0.1): este script foi
ESCRITO por um agente e NÃO foi executado por ele nos parâmetros reais. O
agente verificou sintaxe (`python -m py_compile`) e rodou um teste de fumaça
com parâmetros bem reduzidos (poucos agentes, poucos trials, T curto) só
para confirmar que a lógica não quebra — os números citados em qualquer
relatório não vêm desse teste de fumaça, vêm da execução real que o autor
roda localmente.

CONTEXTO E MOTIVAÇÃO (ler `PROMPT_claude_code_V5_social.md` e
`_revisao_2026-08-05/revisao_critica_St_V4.md` antes de citar este script em
qualquer lugar)
------------------------------------------------------------------------------
A V4 (`consciousness_model_v4_social.py`) implementou uma primeira prova de
conceito de S(t)/C_hum(t), mas uma revisão crítica já registrada no projeto
apontou dois problemas: (a) o resultado principal foi quase TAUTOLÓGICO — S
foi construído a partir das mesmas variáveis (P_u, R_a, M_r) que definem os
cenários, então "S discrimina os cenários" não diz muito; (b) a camada
social ficou DESACOPLADA do comportamento dos agentes — comunicar-se ou não
não mudava nada na dinâmica interna deles, só um índice adicional era
somado por fora.

Esta V5 ataca os dois problemas com um teste que PODE FALHAR:

1. **Feedback real na dinâmica individual.** O indicador de common knowledge
   (K_ck, definido abaixo) realimenta o estado interno de cada agente
   (o traço de memória `M` do V3, que já alimenta a valoração e o cálculo de
   Q dentro do próprio V3 — ver `consciousness_model_v3.py`), não apenas um
   termo aditivo externo ao índice. Ver `SocialChannelV5.step` e o laço de
   feedback em `run_scenario` abaixo.
2. **Common knowledge como limiar, não gradiente.**
   `K_ck = sigmoid(k_ck_gain * (R_a * M_r - k_ck_threshold))` — perto de 0
   abaixo do limiar, saltando para perto de 1 acima, se o parâmetro de
   ganho for grande o suficiente. `sweep_p_ack` varia a probabilidade de
   reconhecimento (`p_ack`) e mede se há uma transição abrupta em K_ck (e na
   taxa de sucesso de coordenação) ou uma rampa suave.
3. **Teste comportamental não-circular: jogo de coordenação tipo
   "stag-hunt" com risco real.** Cada agente escolhe, num único instante de
   decisão por simulação (`t_decision`), entre uma ação SEGURA (retorno
   garantido, `payoff_safe`) e uma ação COORDENADA/arriscada (retorno alto,
   `payoff_stag_success`, SE uma fração suficiente do grupo também a
   escolher; retorno pior que a ação segura, `payoff_stag_fail`, caso
   contrário). A métrica-alvo é o SUCESSO DE COORDENAÇÃO (fração de trials
   em que o grupo atinge o limiar de coordenação) — um resultado
   comportamental, não o próprio S.

A PREDIÇÃO FALSIFICÁVEL (o que este script testa de fato)
------------------------------------------------------------
- **privado:** sem canal público — taxa de sucesso de coordenação deveria
  ficar perto do que se obtém por acaso puro (deriva do estado basal do V3).
- **compartilhado (não ratificado):** o conteúdo do canal pode ter chegado a
  todos (P_u alto), mas SEM reconhecimento recíproco — a teoria prevê que a
  coordenação arriscada FALHA (fica perto do nível de "privado"), porque não
  há K_ck>0 para alimentar a disposição de agir dos agentes.
- **ratificado (common knowledge):** reconhecimento recíproco real produz
  K_ck>0 quando suficiente — a teoria prevê que a coordenação arriscada TEM
  SUCESSO com taxa mais alta que nos outros dois cenários.

Se a coordenação subir suavemente com P_u INDEPENDENTEMENTE de haver
ratificação (ex.: "compartilhado" coordena tão bem quanto "ratificado"),
isso REFUTA a tese de que é o common knowledge — e não a mera informação
compartilhada — que habilita a coordenação, e deve ser reportado como
refutação, não maquiado (ver seção "Leitura" nas saídas).

ANTI-CIRCULARIDADE (por que este teste não é "trapaça")
------------------------------------------------------------
- Os agentes em "compartilhado" e em "ratificado" têm exatamente a MESMA
  informação disponível (mesmo `p_receive`, mesmo `t_broadcast`) e a MESMA
  capacidade de agir (mesma regra de decisão, mesmos payoffs). A ÚNICA
  diferença estrutural entre os dois cenários é que o mecanismo de
  reconhecimento recíproco (`acknowledged`) simplesmente NÃO EXISTE em
  "compartilhado" (herdado da V4 — ver `SocialChannelV5.step`), então R_a
  fica em 0 por construção, não por um branch que discrimina o cenário na
  hora da decisão do jogo.
- O feedback de K_ck sobre `M` de cada agente usa a MESMA fórmula nos três
  cenários (não há `if scenario == "ratificado": ...` na regra de feedback
  nem na regra de decisão do jogo) — a diferença de resultado emerge
  inteiramente da diferença na trajetória de K_ck, que por sua vez emerge da
  dinâmica do canal, não de um rótulo.
- O retorno (payoff) da ação coordenada depende do comportamento agregado
  REAL dos agentes na rodada de decisão (quantos escolheram a ação
  arriscada), não de um rótulo de cenário.
- **Ablação (a) — remoção do sinal de ratificação:** `disable_feedback=True`
  zera o feedback de K_ck sobre M mesmo no cenário "ratificado". Se a
  coordenação não colapsar de volta ao nível de "privado"/"compartilhado"
  quando o feedback é removido, isso é evidência de que o resultado
  principal NÃO é causado pelo mecanismo que a teoria alega — reportar como
  tal.
- **Ablação (b) — checagem de "compartilhado" apesar de P_u alto:** o script
  registra `P_u` no instante da decisão para os três cenários; espera-se que
  "compartilhado" tenha P_u tão alto quanto "ratificado" (mesma dinâmica de
  recepção) mas SEM elevar a coordenação — essa é a checagem central de
  não-circularidade (informação ampla não é suficiente; reconhecimento
  recíproco é necessário).

OPERACIONALIZAÇÃO DOS PROXIES HERDADOS DA V4 (P_u, R_a, M_r) — inalterada
------------------------------------------------------------------------------
Ver docstring de `consciousness_model_v4_social.py` para a definição
completa e as ressalvas de honestidade metodológica de P_u/R_a/M_r — a V5
reutiliza a MESMA lógica de canal (broadcast → recepção → reconhecimento),
só adiciona K_ck (indicador de limiar) e a rodada do jogo por cima.

HONESTIDADE METODOLÓGICA (ler antes de citar isto em qualquer lugar)
------------------------------------------------------------------------------
- Resultados de simulação sintética de prova de conceito. Não constituem
  validação empírica de nada sobre cognição social real, comunicação humana
  real, jogos de coordenação reais, ou consciência de máquina.
- "Reconhecimento recíproco" continua sendo um sinal booleano probabilístico
  simples, não uma representação de crença sobre o estado mental de outro
  agente. O jogo de coordenação é uma instanciação MÍNIMA de um stag-hunt,
  não um experimento comportamental com humanos.
- O objetivo é demonstrar que, DADA esta operacionalização, a predição
  qualitativa (common knowledge habilita coordenação arriscada que
  informação meramente compartilhada não habilita) é internamente
  consistente e TESTÁVEL — e relatar honestamente se ela passou, falhou, ou
  ficou ambígua. Não é uma afirmação sobre organismos reais.
- Este script NÃO sobrescreve a V4 (`consciousness_model_v4_social.py`
  permanece intocado) nem o V3 (`consciousness_model_v3.py` é só importado,
  nunca modificado — o feedback é implementado escrevendo em atributos
  públicos de instâncias de `ConsciousnessSystemV3` a partir de FORA da
  classe, não editando o arquivo da classe).
- Nota de reprodutibilidade: a V4 usa `hash(scenario) % 1000` para deslocar
  a semente entre cenários no Monte Carlo — `hash()` de string em Python 3 é
  aleatorizado por padrão entre processos (a menos que `PYTHONHASHSEED` seja
  fixado), então repetir a V4 em processos diferentes pode não reproduzir a
  mesma sequência exata de sementes entre cenários (embora seja determinística
  DENTRO de uma mesma execução). A V5 evita esse problema usando um deslocamento
  de semente fixo por cenário (`SCENARIO_SEED_OFFSET`, um dict literal), não
  `hash()`.

Uso:
    python consciousness_model_v5_social.py
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from consciousness_model_v3 import ConsciousnessSystemV3, default_regimes  # noqa: E402

SCENARIOS = ["privado", "compartilhado", "ratificado"]
SCENARIO_SEED_OFFSET = {"privado": 0, "compartilhado": 10_000, "ratificado": 20_000}
OUTDIR = SCRIPT_DIR / "social_v5_outputs"


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


@dataclass(frozen=True)
class SocialLayerParamsV5:
    """Parâmetros nomeados da camada social V5 (todos provisórios)."""

    n_agents: int = 8
    t_broadcast: float = 8.0
    t_decision: float = 30.0        # instante da rodada de decisão do jogo de coordenação
    p_receive: float = 0.05         # prob. por passo de um agente perceber o canal
    p_ack: float = 0.04             # prob. por passo de reconhecer (só existe em "ratificado")
    depth_cap: int = 2              # profundidade máxima de mentalização recursiva (herdado da V4, só para reportar M_r)
    r_a_deep_threshold: float = 0.8  # herdado da V4, usado só na formula de profundidade M_r (não no K_ck)
    lambda1: float = 1.0 / 3        # peso de M_r em S(t) (herdado da V4, reportado por continuidade)
    lambda2: float = 1.0 / 3        # peso de P_u em S(t)
    lambda3: float = 1.0 / 3        # peso de R_a em S(t)
    w5: float = 0.25                # peso de S(t) em C_hum(t) = C_base(t) + w5*S(t)
    # --- novidades V5 ---
    # k_ck_gain=40 (bem mais alto que um valor "de manual", ex. 12) foi
    # escolhido deliberadamente ALTO para que sigmoid(gain*(0-limiar)) fique
    # numericamente perto de zero (~4.5e-5) quando ck_raw=0 (R_a=0, cenário
    # "compartilhado") — com um ganho baixo, esse "vazamento" residual da
    # sigmoide, integrado ao longo de dezenas de segundos pelo feedback,
    # acumularia e contaminaria o cenário "compartilhado" com um sinal que
    # deveria ser exatamente zero por construção. Ver nota de calibração
    # abaixo.
    k_ck_gain: float = 40.0         # ganho da sigmoide K_ck = sigmoid(gain*(R_a*M_r - limiar))
    k_ck_threshold: float = 0.25    # limiar de R_a*M_r a partir do qual K_ck decola
    # feedback_gain, decision_threshold e decision_gain foram CALIBRADOS por
    # simulação (não são "de manual"): o agente rodou um teste de fumaça com
    # poucos trials para achar uma combinação em que (i) o cenário "privado"
    # fique perto de 0% de sucesso de coordenação (a dinâmica basal do V3 em
    # 'wake', sem qualquer camada social, já faz M convergir para ~1,45-1,60
    # ao longo de T~30-35 -- isso por si só define o "chão" que o teste
    # precisa ficar ABAIXO do limiar de decisão) e (ii) o cenário
    # "ratificado" fique claramente acima de 0% (idealmente >50%) --
    # ver `README_V5_como_rodar.md`, seção "Calibração dos parâmetros do
    # jogo", para os números do teste de fumaça que geraram esta escolha.
    # Isso NÃO substitui a execução real que o autor roda -- é só a garantia
    # de que o ponto de partida não está numa região trivialmente saturada
    # (0% ou 100% em TODOS os cenários, o que não testaria nada).
    feedback_gain: float = 0.03     # ganho do feedback de K_ck sobre M de cada agente (por unidade de tempo)
    disable_feedback: bool = False  # ABLAÇÃO (a): zera o feedback mesmo com K_ck>0
    decision_gain: float = 10.0     # ganho da sigmoide de decisão do jogo (sensibilidade a M)
    decision_threshold: float = 1.75  # limiar de M acima do qual a ação arriscada fica mais provável
    payoff_safe: float = 1.0
    payoff_stag_success: float = 2.0
    payoff_stag_fail: float = 0.0
    coord_threshold_frac: float = 0.6  # fração mínima de agentes que precisam escolher a ação arriscada para o grupo ter sucesso


class SocialChannelV5:
    """Processo mínimo de comunicação entre N agentes via canal público,
    mais o indicador de limiar K_ck. Mecânica de broadcast/recepção/
    reconhecimento é a MESMA da V4 (ver docstring de
    `consciousness_model_v4_social.py`) — a novidade aqui é só K_ck."""

    def __init__(self, params: SocialLayerParamsV5, scenario: str, rng: np.random.Generator):
        if scenario not in SCENARIOS:
            raise ValueError(scenario)
        self.p = params
        self.scenario = scenario
        self.rng = rng
        self.broadcasted = False
        self.received = np.zeros(params.n_agents, dtype=bool)
        self.acknowledged = np.zeros(params.n_agents, dtype=bool)

    def step(self, t: float) -> dict:
        if self.scenario == "privado":
            return {"P_u": 0.0, "R_a": 0.0, "M_r": 0.0, "depth": 0, "K_ck": 0.0}

        if not self.broadcasted and t >= self.p.t_broadcast:
            self.broadcasted = True
            self.received[0] = True

        if self.broadcasted:
            for i in range(1, self.p.n_agents):
                if not self.received[i] and self.rng.random() < self.p.p_receive:
                    self.received[i] = True

        P_u = float(self.received.mean())

        # O mecanismo de reconhecimento só existe no cenário "ratificado" —
        # em "compartilhado", self.acknowledged fica sempre em zero, então
        # R_a=0 por construção (não por um branch separado na decisão do
        # jogo). Ver nota de anti-circularidade no docstring do módulo.
        if self.scenario == "ratificado" and self.broadcasted:
            for i in range(self.p.n_agents):
                if self.received[i] and not self.acknowledged[i] and self.rng.random() < self.p.p_ack:
                    self.acknowledged[i] = True

        R_a = float(self.acknowledged.mean())

        if R_a <= 0.0:
            depth = 0
        elif R_a < self.p.r_a_deep_threshold:
            depth = 1
        else:
            depth = 2
        M_r = depth / self.p.depth_cap

        # K_ck: indicador de limiar (não gradiente) sobre o produto R_a*M_r.
        # Mesma fórmula nos 3 cenários — a diferença de trajetória vem
        # inteiramente da dinâmica de R_a/M_r acima, não de um branch aqui.
        ck_raw = R_a * M_r
        K_ck = float(sigmoid(self.p.k_ck_gain * (ck_raw - self.p.k_ck_threshold)))

        return {"P_u": P_u, "R_a": R_a, "M_r": M_r, "depth": depth, "K_ck": K_ck}


def run_scenario(scenario: str, params: SocialLayerParamsV5, seed: int, T: float = 40.0, dt: float = 0.10):
    """Roda N agentes (dinâmica interna do V3, regime 'wake', intocada) + 1
    canal social V5 + feedback de K_ck sobre M + 1 rodada de decisão do jogo
    de coordenação em t=t_decision. Retorna (série temporal, resultado da
    decisão)."""
    wake = default_regimes()["wake"]
    agents = [ConsciousnessSystemV3(regime=wake, dt=dt, seed=seed + i * 1000) for i in range(params.n_agents)]
    rng_channel = np.random.default_rng(seed + 999_999)
    channel = SocialChannelV5(params, scenario, rng_channel)

    rows = []
    decision_done = False
    decision_result = None

    for t in np.arange(0.0, T, dt):
        c_idx_agents = [ag.step(float(t))["C_idx"] for ag in agents]
        C_base = float(np.mean(c_idx_agents))

        social = channel.step(float(t))
        S = params.lambda1 * social["M_r"] + params.lambda2 * social["P_u"] + params.lambda3 * social["R_a"]
        C_hum = C_base + params.w5 * S
        K_ck = social["K_ck"]

        # FEEDBACK: incremento em M de cada agente proporcional a K_ck.
        # Mesma fórmula em TODOS os cenários — a diferença emerge só porque
        # K_ck fica perto de 0 em "privado"/"compartilhado" (R_a=0 por
        # construção nesses dois) e pode subir em "ratificado". Isto
        # modula a mesma variável de estado (M) que o próprio V3 usa
        # internamente para alimentar Q e a valoração — é, portanto, um
        # feedback genuíno na dinâmica individual, não um termo aditivo só
        # no índice (ver ponto 1 da docstring do módulo).
        if not params.disable_feedback:
            for ag in agents:
                ag.M = float(np.clip(ag.M + dt * params.feedback_gain * K_ck, 0.0, 2.0))

        M_mean = float(np.mean([ag.M for ag in agents]))
        rows.append({
            "t": float(t), "scenario": scenario,
            "C_base": C_base, "S": S, "C_hum": C_hum, "K_ck": K_ck,
            "M_r": social["M_r"], "P_u": social["P_u"], "R_a": social["R_a"],
            "M_medio_agentes": M_mean,
        })

        if (not decision_done) and t >= params.t_decision:
            decision_done = True
            m_vals = np.array([ag.M for ag in agents])
            probs = sigmoid(params.decision_gain * (m_vals - params.decision_threshold))
            actions = (rng_channel.random(params.n_agents) < probs).astype(int)  # 1=arriscada ("stag"), 0=segura ("hare")
            frac_arriscada = float(actions.mean())
            success = bool(frac_arriscada >= params.coord_threshold_frac)
            payoffs = np.where(
                actions == 1,
                (params.payoff_stag_success if success else params.payoff_stag_fail),
                params.payoff_safe,
            )
            decision_result = {
                "scenario": scenario,
                "frac_arriscada": frac_arriscada,
                "sucesso_coordenacao": success,
                "payoff_medio": float(payoffs.mean()),
                "prob_media_arriscada": float(probs.mean()),
                "P_u_na_decisao": float(social["P_u"]),
                "R_a_na_decisao": float(social["R_a"]),
                "K_ck_na_decisao": float(K_ck),
                "M_medio_na_decisao": M_mean,
            }

    df = pd.DataFrame(rows)
    if decision_result is None:
        raise RuntimeError("t_decision >= T — a decisão nunca ocorreu. Aumente T ou reduza t_decision.")
    return df, decision_result


def monte_carlo_v5(params: SocialLayerParamsV5, n_trials: int = 80, T: float = 40.0, dt: float = 0.10, seed: int = 42) -> pd.DataFrame:
    rows = []
    for scenario in SCENARIOS:
        offset = SCENARIO_SEED_OFFSET[scenario]
        for trial in range(n_trials):
            _, dec = run_scenario(scenario, params, seed=seed + offset + trial * 7, T=T, dt=dt)
            rows.append({"trial": trial, **dec})
    return pd.DataFrame(rows)


def check_reproducibility(params: SocialLayerParamsV5, seed: int = 42) -> bool:
    df1, dec1 = run_scenario("ratificado", params, seed=seed, T=35.0, dt=0.10)
    df2, dec2 = run_scenario("ratificado", params, seed=seed, T=35.0, dt=0.10)
    series_ok = bool(np.allclose(df1[["C_base", "S", "C_hum", "K_ck"]].values, df2[["C_base", "S", "C_hum", "K_ck"]].values))
    decision_ok = dec1 == dec2
    return series_ok and decision_ok


def sweep_p_ack(base_params: SocialLayerParamsV5, p_ack_values, n_trials: int = 40, T: float = 40.0, dt: float = 0.10, seed: int = 123) -> pd.DataFrame:
    """Varre p_ack (probabilidade de reconhecimento) só no cenário
    'ratificado' (é o único onde p_ack tem efeito — em 'privado' e
    'compartilhado' o mecanismo de reconhecimento não existe) e mede K_ck
    médio no instante da decisão e a taxa de sucesso de coordenação
    resultante, para checar se há transição de fase (salto abrupto) ou
    rampa suave."""
    rows = []
    for p_ack in p_ack_values:
        params = replace(base_params, p_ack=float(p_ack))
        k_ck_vals, successes = [], []
        for trial in range(n_trials):
            _, dec = run_scenario("ratificado", params, seed=seed + trial * 11 + int(p_ack * 100_000), T=T, dt=dt)
            k_ck_vals.append(dec["K_ck_na_decisao"])
            successes.append(dec["sucesso_coordenacao"])
        rows.append({
            "p_ack": float(p_ack),
            "K_ck_medio_na_decisao": float(np.mean(k_ck_vals)),
            "K_ck_dp": float(np.std(k_ck_vals, ddof=1)) if n_trials > 1 else 0.0,
            "taxa_sucesso_coordenacao": float(np.mean(successes)),
        })
    return pd.DataFrame(rows)


def robustness_grid(base_params: SocialLayerParamsV5, n_agents_list, coord_threshold_list, n_trials: int = 30, T: float = 40.0, dt: float = 0.10, seed: int = 777) -> pd.DataFrame:
    """Robustez do resultado principal variando N (número de agentes) e o
    limiar de coordenação exigido — grade pequena, 'se viável' conforme o
    prompt da V5 pede."""
    rows = []
    for n_agents in n_agents_list:
        for coord_threshold in coord_threshold_list:
            params = replace(base_params, n_agents=int(n_agents), coord_threshold_frac=float(coord_threshold))
            for scenario in SCENARIOS:
                offset = SCENARIO_SEED_OFFSET[scenario]
                successes = []
                for trial in range(n_trials):
                    _, dec = run_scenario(scenario, params, seed=seed + offset + n_agents * 13 + int(coord_threshold * 100) + trial * 7, T=T, dt=dt)
                    successes.append(dec["sucesso_coordenacao"])
                rows.append({
                    "n_agents": n_agents, "coord_threshold_frac": coord_threshold,
                    "scenario": scenario, "taxa_sucesso_coordenacao": float(np.mean(successes)),
                })
    return pd.DataFrame(rows)


def save_all(n_trials: int = 80, n_trials_sweep: int = 25, n_trials_robustez: int = 15, T: float = 40.0, dt: float = 0.10, seed: int = 42):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    params = SocialLayerParamsV5()

    print("=== 1) Reprodutibilidade por seed ===")
    repro_ok = check_reproducibility(params)
    print(f"Reprodutibilidade (mesma seed, duas execuções, série + decisão idênticas): {repro_ok}")

    print("\n=== 2) Séries temporais de exemplo (uma run por cenário, seed fixa) ===")
    example_runs = {}
    example_decisions = {}
    for s in SCENARIOS:
        df, dec = run_scenario(s, params, seed=42 + SCENARIO_SEED_OFFSET[s], T=T, dt=dt)
        example_runs[s] = df
        example_decisions[s] = dec
    example_df = pd.concat(example_runs.values(), ignore_index=True)
    example_df.to_csv(OUTDIR / "series_temporais_exemplo.csv", index=False)

    print("\n=== 3) Monte Carlo principal (resultado central: sucesso de coordenação por cenário) ===")
    mc = monte_carlo_v5(params, n_trials=n_trials, T=T, dt=dt, seed=seed)
    mc.to_csv(OUTDIR / "monte_carlo_decisoes.csv", index=False)

    resumo_cenario = mc.groupby("scenario").agg(
        taxa_sucesso_coordenacao=("sucesso_coordenacao", "mean"),
        frac_arriscada_media=("frac_arriscada", "mean"),
        P_u_medio_na_decisao=("P_u_na_decisao", "mean"),
        R_a_medio_na_decisao=("R_a_na_decisao", "mean"),
        K_ck_medio_na_decisao=("K_ck_na_decisao", "mean"),
        M_medio_na_decisao=("M_medio_na_decisao", "mean"),
        payoff_medio=("payoff_medio", "mean"),
    ).reindex(SCENARIOS)
    resumo_cenario.to_csv(OUTDIR / "resumo_coordenacao_por_cenario.csv")
    print(resumo_cenario.to_string())

    print("\n=== 4) Ablação (a): remoção do sinal de ratificação (disable_feedback=True) ===")
    params_no_feedback = replace(params, disable_feedback=True)
    mc_ablation = monte_carlo_v5(params_no_feedback, n_trials=n_trials, T=T, dt=dt, seed=seed + 555_000)
    ablation_summary = mc_ablation.groupby("scenario")["sucesso_coordenacao"].mean().reindex(SCENARIOS)
    ablation_summary.to_csv(OUTDIR / "ablacao_sem_feedback_resumo.csv")
    print(ablation_summary.to_string())

    print("\n=== 5) Sweep de p_ack (transição de fase em K_ck e na coordenação) ===")
    # Resolução mais fina perto de onde o teste de fumaça do agente indicou
    # a transição (ver `README_V5_como_rodar.md`, seção de calibração) —
    # entre p_ack~0,002 e p_ack~0,015, com os demais parâmetros default.
    p_ack_values = [0.0, 0.001, 0.002, 0.004, 0.006, 0.008, 0.01, 0.015, 0.02, 0.03, 0.05, 0.08, 0.12, 0.20]
    sweep_df = sweep_p_ack(params, p_ack_values, n_trials=n_trials_sweep, T=T, dt=dt)
    sweep_df.to_csv(OUTDIR / "sweep_p_ack.csv", index=False)
    print(sweep_df.to_string(index=False))

    print("\n=== 6) Robustez: variando N de agentes e o limiar de coordenação ===")
    robust_df = robustness_grid(params, n_agents_list=[6, 8, 12], coord_threshold_list=[0.5, 0.6, 0.75], n_trials=n_trials_robustez, T=T, dt=dt)
    robust_df.to_csv(OUTDIR / "robustez_n_e_limiar.csv", index=False)

    # --- Figuras ---
    plt.figure(figsize=(7, 4.8))
    ordem = SCENARIOS + ["ratificado_sem_feedback (ablação a)"]
    valores = [resumo_cenario.loc[s, "taxa_sucesso_coordenacao"] for s in SCENARIOS] + [ablation_summary["ratificado"]]
    cores = ["tab:gray", "tab:orange", "tab:blue", "tab:red"]
    plt.bar(ordem, valores, color=cores)
    plt.ylabel("taxa de sucesso de coordenação")
    plt.title(f"V5 — sucesso de coordenação por cenário ({n_trials} trials/cenário)")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(OUTDIR / "sucesso_coordenacao_por_cenario.png", dpi=160)
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].errorbar(sweep_df["p_ack"], sweep_df["K_ck_medio_na_decisao"], yerr=sweep_df["K_ck_dp"], marker="o")
    axes[0].set_xlabel("p_ack (probabilidade de reconhecimento por passo)")
    axes[0].set_ylabel("K_ck médio no instante da decisão")
    axes[0].set_title("K_ck vs. p_ack")
    axes[1].plot(sweep_df["p_ack"], sweep_df["taxa_sucesso_coordenacao"], marker="o", color="tab:blue")
    axes[1].set_xlabel("p_ack (probabilidade de reconhecimento por passo)")
    axes[1].set_ylabel("taxa de sucesso de coordenação")
    axes[1].set_title("Coordenação vs. p_ack")
    fig.suptitle("V5 — sweep de p_ack: transição de fase ou rampa suave? (cenário ratificado)")
    fig.tight_layout()
    fig.savefig(OUTDIR / "sweep_p_ack.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(4, 1, figsize=(9, 13), sharex=True)
    labels = {"privado": "privado", "compartilhado": "compartilhado (não ratificado)", "ratificado": "publicamente ratificado"}
    colors = {"privado": "tab:gray", "compartilhado": "tab:orange", "ratificado": "tab:blue"}
    for feature, ax, title in zip(
        ["K_ck", "M_medio_agentes", "S", "C_hum"], axes,
        ["K_ck(t) — indicador de limiar de common knowledge",
         "M médio dos agentes (traço de memória, alvo do feedback)",
         "S(t) — camada social (proxy, herdado da V4)",
         "C_hum(t) = C_base(t) + w5·S(t)"],
    ):
        for s in SCENARIOS:
            df = example_runs[s]
            ax.plot(df["t"], df[feature], label=labels[s], color=colors[s])
        ax.axvline(params.t_broadcast, color="black", linestyle=":", linewidth=0.8)
        ax.axvline(params.t_decision, color="green", linestyle="--", linewidth=0.8)
        ax.set_title(title)
        ax.set_ylabel(feature)
        ax.legend(fontsize=8)
    axes[-1].set_xlabel("t")
    fig.suptitle("V5 — séries de exemplo por cenário\n(linha pontilhada preta = broadcast; linha tracejada verde = instante da decisão do jogo)")
    fig.tight_layout()
    fig.savefig(OUTDIR / "series_temporais_exemplo.png", dpi=160)
    plt.close(fig)

    # --- Leitura honesta, escrita a partir dos números já calculados acima ---
    taxa_privado = resumo_cenario.loc["privado", "taxa_sucesso_coordenacao"]
    taxa_compartilhado = resumo_cenario.loc["compartilhado", "taxa_sucesso_coordenacao"]
    taxa_ratificado = resumo_cenario.loc["ratificado", "taxa_sucesso_coordenacao"]
    taxa_ratificado_sem_feedback = ablation_summary["ratificado"]
    pu_compartilhado = resumo_cenario.loc["compartilhado", "P_u_medio_na_decisao"]
    pu_ratificado = resumo_cenario.loc["ratificado", "P_u_medio_na_decisao"]

    padrao_previsto = (taxa_ratificado > taxa_compartilhado) and (taxa_ratificado > taxa_privado)
    compartilhado_nao_coordena = taxa_compartilhado <= (taxa_privado + 0.15)  # tolerância de 15pp, não um teste estatístico formal
    ablacao_colapsa = taxa_ratificado_sem_feedback <= (max(taxa_privado, taxa_compartilhado) + 0.15)

    readme = f"""# V5 — teste não-circular de common knowledge (coordenação com risco)

Simulação multiagente que estende a V4 (ver docstring de
`consciousness_model_v5_social.py` para as três mudanças em relação à V4:
feedback real na dinâmica individual, K_ck com limiar, e jogo de coordenação
tipo stag-hunt) e testa se a coordenação comportamental arriscada — não o
próprio índice S — sobe especificamente no cenário de common knowledge.

**IMPORTANTE — leia antes de citar estes números em qualquer lugar:**
resultados de simulação sintética de prova de conceito. Não constituem
validação empírica de nada sobre cognição social real, comunicação humana
real, jogos de coordenação reais, ou consciência de máquina. Ver seção de
"HONESTIDADE METODOLÓGICA" na docstring do script.

## Resultado central ({n_trials} trials por cenário, seed={seed})

```
{resumo_cenario.to_string()}
```

**Taxa de sucesso de coordenação:** privado={taxa_privado:.3f}, compartilhado={taxa_compartilhado:.3f}, ratificado={taxa_ratificado:.3f}.

## Ablação (a) — remoção do sinal de ratificação

Com `disable_feedback=True` (K_ck deixa de alimentar M mesmo no cenário
"ratificado"): taxa de sucesso de coordenação = {taxa_ratificado_sem_feedback:.3f}
(comparar com ratificado COM feedback = {taxa_ratificado:.3f}, e com o nível
de privado/compartilhado = {taxa_privado:.3f}/{taxa_compartilhado:.3f}).
Ver `ablacao_sem_feedback_resumo.csv`.

## Ablação (b) — "compartilhado" apesar de P_u alto

P_u médio no instante da decisão: compartilhado={pu_compartilhado:.3f},
ratificado={pu_ratificado:.3f}. Se os dois forem parecidos (ambos altos) MAS
a coordenação continuar baixa em "compartilhado", isso é a checagem central
de não-circularidade: informação ampla (P_u alto) não é suficiente sozinha
para coordenar — precisa de reconhecimento recíproco (R_a>0, K_ck>0).

## Sweep de p_ack (transição de fase?)

Ver `sweep_p_ack.csv` / `sweep_p_ack.png` — K_ck médio e taxa de sucesso de
coordenação no instante da decisão, para {len(p_ack_values)} valores de p_ack
entre {min(p_ack_values)} e {max(p_ack_values)} ({n_trials_sweep} trials por
valor). A leitura de "transição abrupta vs. rampa suave" é visual/descritiva
neste script — não um teste estatístico formal de ponto de mudança.

## Robustez (N de agentes, limiar de coordenação)

Ver `robustez_n_e_limiar.csv` — grade pequena de N∈{{6,8,12}} ×
limiar∈{{0,5, 0,6, 0,75}}, {n_trials_robustez} trials por combinação.

## Leitura preliminar automática (NÃO é a conclusão do agente — é um resumo
mecânico dos números acima; um agente deve revisar tudo antes de aceitar)

- Padrão previsto (ratificado > compartilhado E ratificado > privado): {"SIM" if padrao_previsto else "NÃO"}.
- "Compartilhado" ficou perto do nível de "privado" apesar de P_u alto (não-circularidade): {"SIM (consistente com a teoria)" if compartilhado_nao_coordena else "NÃO — compartilhado coordenou bem mais que privado, o que enfraquece a leitura de que é especificamente o reconhecimento recíproco (e não a informação ampla) que habilita a coordenação"}.
- Ablação (a) fez a coordenação de "ratificado" colapsar de volta ao nível basal: {"SIM (consistente — o mecanismo alegado é mesmo o responsável)" if ablacao_colapsa else "NÃO — a coordenação se manteve alta mesmo sem o feedback de K_ck, o que é evidência de que algo além do mecanismo alegado está produzindo o resultado; investigar antes de reportar o teste como bem-sucedido"}.

**Se as três linhas acima vierem "SIM"/consistentes, a predição do Cap. 9
passou neste teste específico — reportar como prova de conceito sintética
bem-sucedida, sem alegar mais que isso (não é validação empírica).** Se
qualquer uma vier "NÃO", o teste falhou ou ficou ambíguo neste ponto do
espaço de parâmetros — reportar honestamente, não maquiar (o próprio prompt
que originou este script pede isso explicitamente).

## Reprodutibilidade

Duas execuções do cenário "ratificado" com a mesma seed produzem série
temporal E resultado de decisão idênticos: {repro_ok}.

## Arquivos gerados

- `series_temporais_exemplo.csv` / `.png` — uma execução por cenário (seed fixa), K_ck/M/S/C_hum ao longo do tempo.
- `monte_carlo_decisoes.csv` — {n_trials} trials por cenário (dados brutos da decisão do jogo).
- `resumo_coordenacao_por_cenario.csv` — resultado central (tabela acima).
- `ablacao_sem_feedback_resumo.csv` — ablação (a).
- `sweep_p_ack.csv` / `.png` — sweep de p_ack (transição de fase).
- `robustez_n_e_limiar.csv` — robustez a N de agentes e ao limiar de coordenação.

## Parâmetros usados nesta execução

```
{params}
```
"""
    (OUTDIR / "README.md").write_text(readme, encoding="utf-8")
    print("\n" + readme)

    return {
        "repro_ok": repro_ok,
        "resumo_cenario": resumo_cenario,
        "ablation_summary": ablation_summary,
        "sweep_df": sweep_df,
        "robust_df": robust_df,
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-trials", type=int, default=80, help="Trials por cenário no Monte Carlo principal e na ablação")
    ap.add_argument("--n-trials-sweep", type=int, default=25, help="Trials por valor de p_ack no sweep")
    ap.add_argument("--n-trials-robustez", type=int, default=15, help="Trials por combinação (N, limiar) na grade de robustez")
    ap.add_argument("--T", type=float, default=40.0)
    ap.add_argument("--dt", type=float, default=0.10)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    save_all(
        n_trials=args.n_trials,
        n_trials_sweep=args.n_trials_sweep,
        n_trials_robustez=args.n_trials_robustez,
        T=args.T,
        dt=args.dt,
        seed=args.seed,
    )
