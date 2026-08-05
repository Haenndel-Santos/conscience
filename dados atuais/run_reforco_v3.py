"""Execucao reforcada do modelo V3 (n_runs=40, T=60), separada do baseline.

Reproduz o mesmo pipeline de `consciousness_model_v3.save_all`, mas com mais
execucoes por regime e series mais longas, para reduzir variancia da estimativa
sem sobrescrever os artefatos originais (gerados com n_runs=10, T=28). Saidas em
`reforco_outputs/`, na mesma pasta deste script.

Uso: python run_reforco_v3.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import consciousness_model_v3 as v3

N_RUNS = 40
T = 60.0
DT = 0.10
SEED = 42
OUTDIR = Path(__file__).parent / "reforco_outputs"


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    mc = v3.monte_carlo(n_runs=N_RUNS, T=T, dt=DT, seed=SEED)
    mc.to_csv(OUTDIR / "monte_carlo_runs.csv", index=False)

    regime_summary = mc.groupby("regime")[
        ["C_idx_mean", "Psi_eff_mean", "B_mean", "Q_mean", "K_mean", "R_mean", "M_final"]
    ].agg(["mean", "std"]).reset_index()
    regime_summary.to_csv(OUTDIR / "regime_summary.csv", index=False)

    cv_table = v3.coefficient_of_variation_by_regime(mc)
    cv_table.to_csv(OUTDIR / "cv_table.csv", index=False)

    auc_df, thr_df, roc_curves = v3.roc_and_thresholds(mc)
    auc_df.to_csv(OUTDIR / "auc_table.csv", index=False)
    thr_df.to_csv(OUTDIR / "thresholds_table.csv", index=False)

    winners = auc_df.sort_values(["task", "auc"], ascending=[True, False]).groupby("task").head(1)
    winners.to_csv(OUTDIR / "roc_winners.csv", index=False)

    rules = v3.falsifiable_rules(thr_df)
    rules.to_csv(OUTDIR / "falsifiable_rules.csv", index=False)

    # Comparacao direta com o baseline (n_runs=10, T=28), para deixar registrado
    # o efeito de reforcar a estimativa.
    baseline_mc = pd.read_csv(Path(__file__).parent / "monte_carlo_runs.csv")
    baseline_summary = baseline_mc.groupby("regime")["C_idx_mean"].agg(["mean", "std"])
    reinforced_summary = mc.groupby("regime")["C_idx_mean"].agg(["mean", "std"])
    comparison = baseline_summary.join(reinforced_summary, lsuffix="_baseline_n10_T28", rsuffix="_reforcado_n40_T60")
    comparison.to_csv(OUTDIR / "comparacao_baseline_vs_reforcado.csv")

    for feature in ["C_idx_mean", "B_mean", "Psi_eff_mean", "Q_mean"]:
        plt.figure(figsize=(8, 4.8))
        for regime in ["wake", "anxiety", "deep_sleep", "reflex"]:
            vals = mc.loc[mc["regime"] == regime, feature].values
            plt.hist(vals, bins=10, alpha=0.5, density=True, label=regime)
        plt.xlabel(feature)
        plt.ylabel("density")
        plt.title(f"V3 reforcado (n_runs={N_RUNS}, T={T}): {feature}")
        plt.legend()
        plt.tight_layout()
        plt.savefig(OUTDIR / f"dist_{feature}.png", dpi=160)
        plt.close()

    tasks = ["wake_vs_deep_sleep", "wake_vs_reflex", "wake_vs_anxiety", "wake_vs_nonwake", "integrated_vs_low"]
    features = ["C_idx_mean", "B_mean", "Psi_eff_mean", "Q_mean"]
    fig, axes = plt.subplots(len(tasks), 1, figsize=(7, 4.2 * len(tasks)))
    for ax, task in zip(axes, tasks):
        for feat in features:
            fpr, tpr, auc_val = roc_curves[task][feat]
            ax.plot(fpr, tpr, label=f"{feat} (AUC={auc_val:.3f})")
        ax.plot([0, 1], [0, 1], linestyle="--")
        ax.set_title(task)
        ax.set_xlabel("False positive rate")
        ax.set_ylabel("True positive rate")
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(OUTDIR / "roc_grid.png", dpi=160)
    plt.close()

    readme = f"""# V3 reforcado (n_runs={N_RUNS}, T={T}, dt={DT}, seed={SEED})

Execucao com mais repeticoes e series mais longas que o baseline
(n_runs=10, T=28), gerada para reduzir variancia da estimativa sem
sobrescrever os artefatos originais. Ver `comparacao_baseline_vs_reforcado.csv`
para o efeito direto sobre a media/desvio de C_idx por regime.

Resultados de simulacao sintetica de prova de conceito; nao constituem
validacao empirica (ver Cap. 13 do manuscrito).
"""
    (OUTDIR / "README.md").write_text(readme, encoding="utf-8")

    print(regime_summary)
    print()
    print("Comparacao baseline vs reforcado:")
    print(comparison)


if __name__ == "__main__":
    main()
