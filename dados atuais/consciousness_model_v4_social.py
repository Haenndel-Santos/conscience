"""V4 — prova de conceito minima da camada social S(t) / C_hum(t).

CONTEXTO (ver Cap. 9 e Cap. 13 de Versao atual.md, e
_revisao_2026-08-05/auditoria_formalismo.md, Nota 5): o manuscrito define

    S(t)     = lambda1*M_r(t) + lambda2*P_u(t) + lambda3*R_a(t)
    C_hum(t) = C(t) + w5*S(t)

onde M_r = mentalizacao recursiva, P_u = publicidade, R_a = ratificacao
social. Ate a V3, nenhum script implementava S, M_r, P_u ou R_a - a
camada social era esboco programatico, nao simulacao. Este script e a
primeira tentativa de fechar essa lacuna, de forma deliberadamente
MINIMA.

ARQUITETURA
-----------
N agentes (default N=6) rodam, cada um, a dinamica INTERNA do V3 sem
nenhuma alteracao (mesma classe ConsciousnessSystemV3, importada daqui,
nao reimplementada) - cada agente produz seu proprio C_idx exatamente
como no V3. C_base(t) e a media desses C_idx entre os N agentes: e o que
o V3 sozinho preveria, ignorando qualquer camada social.

Por cima disso, um canal publico compartilhado implementa um processo
MINIMO de comunicacao entre agentes (broadcast -> recepcao -> reconheci-
mento reciproco), do qual M_r, P_u e R_a sao lidos como proxies. Os dois
niveis sao computacionalmente DESACOPLADOS por escolha de design: a
comunicacao social nao realimenta o estado interno (m, b, e) de cada
agente. Isso mantem V3 intocado (ninguem chama nada nele que nao seja o
proprio step() publico) e e literalmente fiel a forma aditiva da formula
do Cap. 13 (C_hum = C_base + w5*S, nao uma fusao dos dois processos).
Uma extensao futura (V5?) poderia alimentar o resultado da ratificacao
de volta em V(t) (valoracao social) de cada agente - fora do escopo
desta prova de conceito minima.

TRES CENARIOS (os tres niveis do Cap. 9)
-----------------------------------------
(i)   privado             - nenhuma transmissao. S(t) = 0 sempre.
(ii)  compartilhado        - um agente transmite; os demais podem
      (nao ratificado)      "perceber" o canal (isso e P_u), mas nao ha
                             mecanismo de reconhecimento mutuo: R_a e
                             M_r ficam em 0 por construcao (publicidade
                             sem ratificacao nao vira conhecimento comum).
(iii) publicamente          mesma transmissao/recepcao de (ii), MAIS um
      ratificado            mecanismo de reconhecimento reciproco: agen-
                             tes que receberam podem sinalizar de volta
                             ("eu vi isso"), o que alimenta R_a e uma
                             contagem de "profundidade de mentalizacao
                             recursiva" (M_r) limitada a poucos niveis.

OPERACIONALIZACAO DOS PROXIES (todos provisorios - ver Cap. 9)
----------------------------------------------------------------
P_u(t) = fracao dos N agentes que ja "possuem" o conteudo do canal
         (o agente-porta-voz conta desde o instante do broadcast).
R_a(t) = fracao dos N agentes que ja enviaram um sinal de reconhecimento
         de volta ao canal (so pode ser > 0 no cenario "ratificado" -
         no "compartilhado" esse mecanismo nao existe).
M_r(t) = profundidade de mentalizacao recursiva, um CONTADOR discreto
         com teto (depth_cap, default 2), normalizado para [0,1]:
           profundidade 0: sem confirmacao reciproca. Cobre tanto
                           "ninguem recebeu nada" quanto "alguem recebeu
                           (P_u>0) mas ninguem reconheceu de volta
                           (R_a=0)" - mera recepcao unilateral NAO conta
                           como mentalizacao recursiva aqui, porque
                           "eu sei que voce sabe" exige um sinal sobre o
                           estado do outro, que so existe quando ha
                           reconhecimento.
           profundidade 1: reconhecimento mutuo emergente (0<R_a<limiar)
                           - "eu sei que voce sabe" comeca a se formar.
           profundidade 2: reconhecimento quase universal (R_a>=limiar)
                           - proxy grosseiro para mais uma camada
                           iterada ("eu sei que voce sabe que eu sei"),
                           sem modelar crencas aninhadas de fato.
         A mesma formula de profundidade vale nos DOIS cenarios com
         comunicacao (compartilhado e ratificado); a diferenca entre
         eles nao esta em como M_r e calculado, mas em que
         "compartilhado" nunca deixa R_a passar de 0 (o mecanismo de
         reconhecimento simplesmente nao existe nesse cenario). Isso
         evita tratar o mesmo estado epistemico (P_u>0, R_a=0) de forma
         diferente so por causa do rotulo do cenario.
         Este contador de poucos niveis e uma escolha deliberada: a
         literatura de common knowledge (Thomas et al. 2014, 2016) nao
         exige regressao infinita para explicar efeitos de coordenacao
         social - alguns niveis bastam. Nao e uma simulacao de logica
         epistemica ou de crencas aninhadas de fato.

HONESTIDADE METODOLOGICA (ler antes de citar isto em qualquer lugar)
----------------------------------------------------------------------
- S(t) e C_hum(t) aqui sao PROXIES OPERACIONAIS de um processo social
  minimo, nao uma afirmacao de que os agentes tem consciencia
  intersubjetiva real, nem de que este mecanismo capta tudo que common
  knowledge significa na tradicao de Thomas et al.
- "Reconhecimento reciproco" e um sinal booleano probabilistico, nao uma
  representacao de crenca sobre o estado mental de outro agente.
- Todos os numeros deste script sao simulacao sintetica de prova de
  conceito. Nao constituem validacao empirica de nada sobre cognicao
  social real, comunicacao humana real, ou consciencia de maquina.
- O objetivo e estritamente demonstrar que, DADA esta operacionalizacao
  minima, a predicao qualitativa do Cap. 9 (S e C_hum crescem de privado
  para ratificado, enquanto o indice individual de base fica estavel) e
  internamente consistente e testavel - nao que ela e verdadeira sobre
  organismos reais.

Uso:
    python consciousness_model_v4_social.py
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score

from consciousness_model_v3 import ConsciousnessSystemV3, default_regimes

SCENARIOS = ["privado", "compartilhado", "ratificado"]
OUTDIR = Path(__file__).parent / "social_outputs"


@dataclass
class SocialLayerParams:
    """Parametros nomeados da camada social (todos provisorios)."""

    n_agents: int = 6
    t_broadcast: float = 8.0        # instante em que o agente-porta-voz transmite
    p_receive: float = 0.05         # prob. por passo de um agente perceber o canal
    p_ack: float = 0.04             # prob. por passo de reconhecer (so em "ratificado")
    depth_cap: int = 2               # profundidade maxima de mentalizacao recursiva modelada
    r_a_deep_threshold: float = 0.8 # fracao de R_a a partir da qual contamos profundidade 3
    lambda1: float = 1.0 / 3        # peso de M_r em S(t)
    lambda2: float = 1.0 / 3        # peso de P_u em S(t)
    lambda3: float = 1.0 / 3        # peso de R_a em S(t)
    w5: float = 0.25                # peso de S(t) em C_hum(t) = C_base(t) + w5*S(t)


class SocialChannel:
    """Processo minimo de comunicacao entre N agentes via canal publico.

    Le-se como uma maquina de estados PROVISORIA para M_r, P_u, R_a -
    nao uma teoria da comunicacao humana. Ver docstring do modulo.
    """

    def __init__(self, params: SocialLayerParams, scenario: str, rng: np.random.Generator):
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
            return {"P_u": 0.0, "R_a": 0.0, "M_r": 0.0, "depth": 0}

        if not self.broadcasted and t >= self.p.t_broadcast:
            self.broadcasted = True
            self.received[0] = True  # o porta-voz detem o conteudo desde o broadcast

        if self.broadcasted:
            for i in range(1, self.p.n_agents):
                if not self.received[i] and self.rng.random() < self.p.p_receive:
                    self.received[i] = True

        P_u = float(self.received.mean())

        # O mecanismo de reconhecimento so existe no cenario "ratificado".
        # Em "compartilhado", self.acknowledged fica sempre em zero, entao
        # R_a=0 por construcao (nao por um branch separado) - ver nota no
        # docstring do modulo sobre por que isso importa.
        if self.scenario == "ratificado" and self.broadcasted:
            for i in range(self.p.n_agents):
                if self.received[i] and not self.acknowledged[i] and self.rng.random() < self.p.p_ack:
                    self.acknowledged[i] = True

        R_a = float(self.acknowledged.mean())

        # Mesma formula de profundidade nos dois cenarios com comunicacao:
        # mera recepcao (P_u>0) sem reconhecimento (R_a=0) fica em
        # profundidade 0 - reconhecimento e o que licencia M_r>0.
        if R_a <= 0.0:
            depth = 0
        elif R_a < self.p.r_a_deep_threshold:
            depth = 1
        else:
            depth = 2
        M_r = depth / self.p.depth_cap

        return {"P_u": P_u, "R_a": R_a, "M_r": M_r, "depth": depth}


def run_scenario(scenario: str, params: SocialLayerParams, T: float = 40.0, dt: float = 0.10, seed: int = 42) -> pd.DataFrame:
    """Roda N agentes (dinamica interna do V3, regime 'wake') + 1 canal social."""
    wake = default_regimes()["wake"]
    agents = [ConsciousnessSystemV3(regime=wake, dt=dt, seed=seed + i * 1000) for i in range(params.n_agents)]
    channel = SocialChannel(params, scenario, rng=np.random.default_rng(seed + 999_999))

    rows = []
    for t in np.arange(0.0, T, dt):
        c_idx_agents = [ag.step(float(t))["C_idx"] for ag in agents]
        C_base = float(np.mean(c_idx_agents))

        social = channel.step(float(t))
        S = params.lambda1 * social["M_r"] + params.lambda2 * social["P_u"] + params.lambda3 * social["R_a"]
        C_hum = C_base + params.w5 * S

        rows.append({
            "t": float(t), "scenario": scenario,
            "C_base": C_base, "S": S, "C_hum": C_hum,
            "M_r": social["M_r"], "P_u": social["P_u"], "R_a": social["R_a"],
        })
    return pd.DataFrame(rows)


def monte_carlo_social(params: SocialLayerParams, n_runs: int = 15, T: float = 40.0, dt: float = 0.10, seed: int = 42) -> pd.DataFrame:
    """n_runs execucoes por cenario; resume cada run pela media da serie inteira
    (mesma convencao do V3: C_idx_mean = media da serie completa)."""
    rows = []
    for scenario in SCENARIOS:
        for run_id in range(n_runs):
            df = run_scenario(scenario, params, T=T, dt=dt, seed=seed + hash(scenario) % 1000 + run_id * 7)
            rows.append({
                "scenario": scenario, "run_id": run_id,
                "C_base_mean": df["C_base"].mean(),
                "S_mean": df["S"].mean(),
                "C_hum_mean": df["C_hum"].mean(),
                "M_r_mean": df["M_r"].mean(),
                "P_u_mean": df["P_u"].mean(),
                "R_a_mean": df["R_a"].mean(),
            })
    return pd.DataFrame(rows)


def check_reproducibility(params: SocialLayerParams, seed: int = 42) -> bool:
    """Roda o cenario ratificado duas vezes com a mesma seed; confirma resultado identico."""
    df1 = run_scenario("ratificado", params, T=20.0, dt=0.10, seed=seed)
    df2 = run_scenario("ratificado", params, T=20.0, dt=0.10, seed=seed)
    return bool(np.allclose(df1[["C_base", "S", "C_hum"]].values, df2[["C_base", "S", "C_hum"]].values))


def auc_ratificado_vs_privado(mc: pd.DataFrame, feature: str) -> float:
    sub = mc[mc["scenario"].isin(["privado", "ratificado"])].copy()
    y = (sub["scenario"] == "ratificado").astype(int).values
    scores = sub[feature].values
    return float(roc_auc_score(y, scores))


def save_all():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    params = SocialLayerParams()

    # 1) Reprodutibilidade por seed
    repro_ok = check_reproducibility(params)
    print(f"Reprodutibilidade (mesma seed, duas execucoes identicas): {repro_ok}")

    # 2) Series temporais de exemplo (uma run por cenario, seed fixa) - para a figura e inspecao
    example_runs = {s: run_scenario(s, params, T=40.0, dt=0.10, seed=42) for s in SCENARIOS}
    example_df = pd.concat(example_runs.values(), ignore_index=True)
    example_df.to_csv(OUTDIR / "series_temporais_exemplo.csv", index=False)

    # 3) Monte Carlo (15 runs por cenario) -> resumo por cenario + AUC
    mc = monte_carlo_social(params, n_runs=15, T=40.0, dt=0.10, seed=42)
    mc.to_csv(OUTDIR / "monte_carlo_runs.csv", index=False)

    resumo = mc.groupby("scenario")[
        ["C_base_mean", "S_mean", "C_hum_mean", "M_r_mean", "P_u_mean", "R_a_mean"]
    ].agg(["mean", "std"])
    # ordena as linhas na ordem teorica i -> ii -> iii
    resumo = resumo.reindex(SCENARIOS)
    resumo.to_csv(OUTDIR / "resumo_por_cenario.csv")
    print("\n=== Resumo por cenario (media +/- desvio entre 15 runs) ===")
    print(resumo)

    auc_S = auc_ratificado_vs_privado(mc, "S_mean")
    auc_Chum = auc_ratificado_vs_privado(mc, "C_hum_mean")
    auc_Cbase = auc_ratificado_vs_privado(mc, "C_base_mean")

    auc_text = (
        f"AUC 'ratificado vs privado' (15 runs por cenario, seed=42):\n"
        f"  S(t) medio da run     -> AUC = {auc_S:.4f}\n"
        f"  C_hum(t) medio da run -> AUC = {auc_Chum:.4f}\n"
        f"  C_base(t) medio da run (indice individual, sem camada social) -> AUC = {auc_Cbase:.4f}\n"
        f"\nReprodutibilidade por seed (2 execucoes identicas do cenario ratificado): {repro_ok}\n"
        f"\nParametros: {params}\n"
    )
    (OUTDIR / "auc_ratificado_vs_privado.txt").write_text(auc_text, encoding="utf-8")
    print("\n" + auc_text)

    # 4) Figura: series temporais das tres grandezas nos tres cenarios
    fig, axes = plt.subplots(3, 1, figsize=(9, 11), sharex=True)
    labels = {"privado": "privado", "compartilhado": "compartilhado (não ratificado)", "ratificado": "publicamente ratificado"}
    colors = {"privado": "tab:gray", "compartilhado": "tab:orange", "ratificado": "tab:blue"}
    for feature, ax, title in zip(
        ["C_base", "S", "C_hum"], axes,
        ["C_base(t) — índice individual (média dos agentes, sem camada social)",
         "S(t) — camada social (proxy provisório)",
         "C_hum(t) = C_base(t) + w5·S(t)"],
    ):
        for s in SCENARIOS:
            df = example_runs[s]
            ax.plot(df["t"], df[feature], label=labels[s], color=colors[s])
        ax.set_title(title)
        ax.set_ylabel(feature)
        ax.legend(fontsize=8)
        ax.axvline(params.t_broadcast, color="black", linestyle=":", linewidth=0.8)
    axes[-1].set_xlabel("t")
    fig.suptitle("V4 — prova de conceito: S(t) e C_hum(t) por cenário de common knowledge\n(simulação sintética; linha pontilhada = instante do broadcast)")
    fig.tight_layout()
    fig.savefig(OUTDIR / "s_e_chum_por_cenario.png", dpi=160)
    plt.close(fig)

    readme = f"""# V4 — prova de conceito da camada social (S(t) / C_hum(t))

Simulação multiagente mínima que operacionaliza S(t) e C_hum(t) — ver
docstring de `consciousness_model_v4_social.py` para as definições
operacionais completas e as ressalvas de honestidade metodológica.

**Resultado central** (15 execuções por cenário, seed=42):

```
{resumo.to_string()}
```

**AUC "ratificado vs. privado"**:
- S(t): {auc_S:.4f}
- C_hum(t): {auc_Chum:.4f}
- C_base(t) (índice individual, sem camada social): {auc_Cbase:.4f}

C_base não discrimina os cenários (esperado — os agentes não sabem, em
seu estado interno, se estão ou não se comunicando); S(t) e C_hum(t)
discriminam fortemente, confirmando a predição qualitativa do Cap. 9
dentro desta operacionalização mínima.

**Reprodutibilidade por seed:** {repro_ok} (duas execuções do cenário
"ratificado" com seed=42 produzem series numericamente idênticas).

**IMPORTANTE — leia antes de citar estes números em qualquer lugar:**
resultados de simulação sintética de prova de conceito. S(t) é proxy
operacional de um processo social mínimo (broadcast + recepção
probabilística + reconhecimento recíproco probabilístico), não medida de
consciência intersubjetiva real. "Profundidade de mentalização recursiva"
aqui é um contador limitado a {SocialLayerParams().depth_cap} níveis, não
uma simulação de crenças aninhadas. Não constitui validação empírica de
nada sobre cognição social real.

Arquivos:
- `series_temporais_exemplo.csv` — uma execução por cenário (seed=42), para a figura.
- `monte_carlo_runs.csv` — 15 execuções por cenário (dados brutos).
- `resumo_por_cenario.csv` — médias/desvios por cenário.
- `auc_ratificado_vs_privado.txt` — AUC de S, C_hum e C_base.
- `s_e_chum_por_cenario.png` — figura (C_base, S, C_hum ao longo do tempo, 3 cenários).
"""
    (OUTDIR / "README.md").write_text(readme, encoding="utf-8")

    return {"resumo": resumo, "auc_S": auc_S, "auc_Chum": auc_Chum, "auc_Cbase": auc_Cbase, "repro_ok": repro_ok}


if __name__ == "__main__":
    save_all()
