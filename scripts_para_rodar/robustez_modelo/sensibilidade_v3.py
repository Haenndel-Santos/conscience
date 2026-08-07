"""Frente E — Análise de sensibilidade dos pesos do modelo V3.

REGRA DE GOVERNANÇA (`PLANO_ESTRATEGICO_cientifico.md` §0.1): este script foi
ESCRITO por um agente e NÃO foi executado por ele. O agente verificou apenas
sintaxe (`python -m py_compile`) e, à parte, rodou um teste de fumaça com
parâmetros reduzidos para confirmar que a lógica não quebra — os números
citados em READMEs/relatórios não vêm desse teste de fumaça, vêm da execução
real que o autor roda localmente.

OBJETIVO
--------
A crítica central ao modelo V3 (registrada em `PLANO_ESTRATEGICO_cientifico.md`,
diagnóstico, e em `dados atuais/README.md`) é que os regimes (wake, anxiety,
deep_sleep, reflex) se separam de forma limpa "por construção" — ou seja, os
parâmetros do modelo (os pesos que compõem Ψ_eff e C_idx) podem ter sido
implicitamente ajustados para produzir a separação desejada, o que tornaria a
separação uma tautologia, não uma descoberta.

Este script ataca essa crítica de um ângulo: ROBUSTEZ. Se a separação de
regimes (medida por AUC de C_idx entre pares de regimes) sobrevive a
perturbações GRANDES e simultâneas em todos os pesos, isso enfraquece a
crítica de tautologia (o resultado não depende de um ajuste fino específico).
Se a separação colapsa sob perturbações pequenas, isso a sustenta.

Duas análises:
1. Sensibilidade Monte Carlo: ruído multiplicativo aleatório simultâneo em
   TODOS os pesos ao mesmo tempo, em magnitudes crescentes, medindo como o
   AUC mediano (entre várias reamostragens de pesos) degrada.
2. Sensibilidade one-at-a-time (OAT): varia um peso por vez (os outros fixos
   no baseline), para identificar quais pesos, se algum, dominam a separação.

Este script NÃO decide se o modelo é válido — só mede robustez. A leitura
("Leitura", no fim de cada saída) é um guia de interpretação, não uma
conclusão pronta (mesma disciplina da Frente C/G).

DEPENDÊNCIA DE OUTRO ARQUIVO DO PROJETO
----------------------------------------
Este script IMPORTA `consciousness_model_v3.py` (não reimplementa a dinâmica
do modelo — seria um retrabalho enorme e arriscado reproduzir mal a EDO do
V3). Por padrão, localiza esse arquivo em `dados atuais/`, dois níveis acima
da pasta deste script (`scripts_para_rodar/robustez_modelo/`), assumindo a
estrutura de pastas padrão do projeto. Use `--model-dir` para apontar para
outro lugar se necessário.

Uso:
    python sensibilidade_v3.py
    python sensibilidade_v3.py --n-runs 10 --n-trials 15   # mais preciso, mais lento
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "dados atuais"

BASELINE_WEIGHTS = dict(
    w_mb=0.35, w_me=0.20, w_k=0.20, w_r=0.25,
    c_w_psi=0.45, c_w_q=0.20, c_w_m=0.17, c_w_b=0.18,
)
TASKS = [
    "wake_vs_deep_sleep", "wake_vs_reflex", "wake_vs_anxiety",
    "wake_vs_nonwake", "integrated_vs_low",
]


def _import_v3(model_dir):
    model_dir = Path(model_dir)
    if not (model_dir / "consciousness_model_v3.py").exists():
        raise FileNotFoundError(
            f"Não encontrei consciousness_model_v3.py em '{model_dir}'. "
            "Rode este script de dentro de scripts_para_rodar/robustez_modelo/ "
            "(layout padrão do projeto), ou use --model-dir para apontar para "
            "a pasta 'dados atuais' correta."
        )
    if str(model_dir) not in sys.path:
        sys.path.insert(0, str(model_dir))
    import consciousness_model_v3 as v3  # type: ignore
    return v3


def monte_carlo_with_weights(v3, weights: dict, n_runs: int, T: float, dt: float, seed: int) -> pd.DataFrame:
    """Réplica local de v3.monte_carlo(), mas aceitando pesos arbitrários.

    v3.monte_carlo() só aceita 'variants' pré-definidas (full/no_body/...),
    não pesos livres — por isso replicamos aqui o mesmo laço (regime x run),
    chamando ConsciousnessSystemV3 diretamente com os pesos perturbados.
    """
    rows = []
    for r_idx, (name, reg) in enumerate(v3.default_regimes().items()):
        for run_id in range(n_runs):
            sistema = v3.ConsciousnessSystemV3(
                regime=reg, dt=dt, seed=seed + r_idx * 1000 + run_id, **weights
            )
            df = sistema.run(T=T)
            rows.append(v3.summarize_run(df, regime=name, run_id=run_id, variant="perturbado"))
    return pd.DataFrame(rows)


def auc_for_weights(v3, weights, n_runs, T, dt, seed) -> dict:
    mc = monte_carlo_with_weights(v3, weights, n_runs, T, dt, seed)
    auc_df, _, _ = v3.roc_and_thresholds(mc, features=["C_idx_mean"])
    return auc_df.set_index("task")["auc"].to_dict()


def perturb_weights(rng, magnitude) -> dict:
    """Ruído multiplicativo uniforme em [1-magnitude, 1+magnitude] por peso,
    truncado em >=0 (pesos negativos não têm sentido no modelo)."""
    out = {}
    for k, v in BASELINE_WEIGHTS.items():
        factor = 1.0 + rng.uniform(-magnitude, magnitude)
        out[k] = max(0.0, v * factor)
    return out


def run_monte_carlo_sensitivity(v3, magnitudes, n_trials, n_runs, T, dt, seed) -> pd.DataFrame:
    rows = []
    rng = np.random.default_rng(seed)
    for magnitude in magnitudes:
        n_t = 1 if magnitude == 0.0 else n_trials
        for trial in range(n_t):
            weights = dict(BASELINE_WEIGHTS) if magnitude == 0.0 else perturb_weights(rng, magnitude)
            aucs = auc_for_weights(v3, weights, n_runs, T, dt, seed + trial * 17 + int(magnitude * 1000))
            for task, auc in aucs.items():
                rows.append({"magnitude": magnitude, "trial": trial, "task": task, "auc": auc, **weights})
    return pd.DataFrame(rows)


def run_oat_sensitivity(v3, multipliers, n_runs, T, dt, seed) -> pd.DataFrame:
    rows = []
    for param in BASELINE_WEIGHTS:
        for mult in multipliers:
            weights = dict(BASELINE_WEIGHTS)
            weights[param] = max(0.0, BASELINE_WEIGHTS[param] * mult)
            aucs = auc_for_weights(v3, weights, n_runs, T, dt, seed)
            for task, auc in aucs.items():
                rows.append({
                    "param": param, "multiplier": mult, "task": task, "auc": auc,
                    "value": weights[param],
                })
    return pd.DataFrame(rows)


def fragility_summary(mc_df: pd.DataFrame) -> pd.DataFrame:
    """Para cada task, a menor magnitude de perturbação cujo AUC mediano
    (entre as reamostragens de pesos daquela magnitude) já caiu abaixo de
    0,85 e abaixo de 0,70."""
    rows = []
    for task in TASKS:
        sub = mc_df[mc_df["task"] == task]
        med = sub.groupby("magnitude")["auc"].median().sort_index()
        thr85 = next((m for m, a in med.items() if a < 0.85), None)
        thr70 = next((m for m, a in med.items() if a < 0.70), None)
        rows.append({
            "task": task,
            "auc_baseline_mediana": float(med.iloc[0]) if len(med) else float("nan"),
            "primeira_magnitude_auc_abaixo_0_85": thr85,
            "primeira_magnitude_auc_abaixo_0_70": thr70,
        })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model-dir", default=str(DEFAULT_MODEL_DIR))
    ap.add_argument("--n-runs", type=int, default=6, help="Runs por regime, por sorteio de pesos (Monte Carlo interno do V3)")
    ap.add_argument("--n-trials", type=int, default=8, help="Sorteios de pesos aleatórios por magnitude de perturbação")
    ap.add_argument("--T", type=float, default=20.0)
    ap.add_argument("--dt", type=float, default=0.10)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--magnitudes", type=float, nargs="+", default=[0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0])
    ap.add_argument("--oat-multipliers", type=float, nargs="+", default=[0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0])
    ap.add_argument("--outdir", default=str(SCRIPT_DIR))
    args = ap.parse_args()

    v3 = _import_v3(args.model_dir)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print("=== Sensibilidade Monte Carlo (ruído multiplicativo simultâneo em todos os pesos) ===")
    mc_df = run_monte_carlo_sensitivity(v3, args.magnitudes, args.n_trials, args.n_runs, args.T, args.dt, args.seed)
    mc_df.to_csv(outdir / "sensibilidade_montecarlo.csv", index=False)

    frag = fragility_summary(mc_df)
    frag.to_csv(outdir / "sensibilidade_fragilidade_resumo.csv", index=False)
    print(frag.to_string(index=False))

    print("\n=== Sensibilidade one-at-a-time (um peso por vez, outros no baseline) ===")
    oat_df = run_oat_sensitivity(v3, args.oat_multipliers, args.n_runs, args.T, args.dt, args.seed)
    oat_df.to_csv(outdir / "sensibilidade_oat.csv", index=False)

    plt.figure(figsize=(9, 5.5))
    for task in TASKS:
        sub = mc_df[mc_df["task"] == task].groupby("magnitude")["auc"].agg(["median", "std"]).reset_index()
        plt.plot(sub["magnitude"], sub["median"], marker="o", label=task)
        plt.fill_between(
            sub["magnitude"],
            sub["median"] - sub["std"].fillna(0.0),
            sub["median"] + sub["std"].fillna(0.0),
            alpha=0.15,
        )
    plt.axhline(0.85, linestyle="--", color="gray", linewidth=1, label="AUC=0,85")
    plt.axhline(0.70, linestyle=":", color="gray", linewidth=1, label="AUC=0,70 (quase acaso)")
    plt.xlabel("magnitude da perturbação (ruído multiplicativo uniforme, simultâneo em todos os pesos)")
    plt.ylabel("AUC mediana (C_idx_mean)")
    plt.title("V3 — robustez da separação de regimes sob perturbação simultânea dos pesos")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(outdir / "sensibilidade_montecarlo.png", dpi=160)
    plt.close()

    fig, axes = plt.subplots(2, 4, figsize=(18, 8), sharey=True)
    params_list = list(BASELINE_WEIGHTS)
    for ax, param in zip(axes.flat, params_list):
        for task in TASKS:
            sub = oat_df[(oat_df["param"] == param) & (oat_df["task"] == task)]
            ax.plot(sub["multiplier"], sub["auc"], marker=".", label=task)
        ax.axvline(1.0, linestyle="--", color="black", linewidth=0.8)
        ax.set_title(f"{param} (baseline={BASELINE_WEIGHTS[param]:.2f})")
        ax.set_xlabel("multiplicador sobre o baseline")
    axes[0, 0].set_ylabel("AUC")
    axes[1, 0].set_ylabel("AUC")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=8)
    fig.suptitle("V3 — sensibilidade one-at-a-time por peso (outros pesos fixos no baseline)")
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    fig.savefig(outdir / "sensibilidade_oat.png", dpi=160)
    plt.close(fig)

    leitura = """
## Leitura (preencher/revisar após rodar — não inventar conclusão aqui)
- Se o AUC mediano permanecer alto (>0,85, idealmente >0,95) até magnitudes
  de perturbação grandes (>=0,5, ou seja +-50% de ruído simultâneo em TODOS
  os pesos ao mesmo tempo), a separação de regimes é robusta — não depende
  de um ajuste fino específico dos coeficientes, o que enfraquece a crítica
  de "separa só por construção".
- Se o AUC cair abaixo de 0,85 (ou 0,70) já em magnitudes pequenas (<0,2), a
  separação é frágil — sustenta a crítica de que os coeficientes precisam
  estar calibrados de forma bem específica para o modelo funcionar.
- A sensibilidade one-at-a-time mostra quais pesos, se algum, dominam a
  separação (curvas com queda íngreme perto do multiplicador 1,0) vs. quais
  são redundantes/pouco importantes (curvas quase planas ao longo de toda a
  faixa testada).
- Nenhuma dessas duas leituras, por si, resolve a questão de identificabilidade
  (se o AJUSTE dos pesos é necessário para bater com dados reais) — isso é
  testado separadamente em `calibracao_v3.py`.
"""
    (outdir / "resumo_sensibilidade.md").write_text(
        "# Frente E — Sensibilidade do modelo V3 (resumo, a interpretar por um agente depois)\n\n"
        f"Rodado com n_runs={args.n_runs}, n_trials={args.n_trials}, T={args.T}, "
        f"dt={args.dt}, seed={args.seed}.\n\n"
        "## Fragilidade por task (magnitude de perturbação em que o AUC mediano cai)\n\n"
        + frag.to_string(index=False)
        + "\n"
        + leitura,
        encoding="utf-8",
    )

    print(f"\nProcessamento concluído. Saídas em: {outdir}")


if __name__ == "__main__":
    main()
