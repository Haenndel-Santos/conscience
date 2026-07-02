
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


@dataclass
class Regime:
    name: str
    env_gain: float
    noise_scale: float
    brain_body_gain: float
    body_brain_gain: float
    power_in: float
    dissipation: float
    mem_gain: float
    mem_decay: float
    bio_gain: float
    social_gain: float
    coherence_bias: float = 1.0
    arousal_bias: float = 0.0


class ConsciousnessSystemV3:
    def __init__(
        self,
        regime: Regime,
        dt: float = 0.10,
        n_m: int = 6,
        n_b: int = 3,
        n_e: int = 3,
        seed: int = 0,
        w_mb: float = 0.35,
        w_me: float = 0.20,
        w_k: float = 0.20,
        w_r: float = 0.25,
        c_w_psi: float = 0.45,
        c_w_q: float = 0.20,
        c_w_m: float = 0.17,
        c_w_b: float = 0.18,
    ):
        self.regime = regime
        self.dt = dt
        self.n_m = n_m
        self.n_b = n_b
        self.n_e = n_e
        self.rng = np.random.default_rng(seed)

        self.w_mb = w_mb
        self.w_me = w_me
        self.w_k = w_k
        self.w_r = w_r
        self.c_w_psi = c_w_psi
        self.c_w_q = c_w_q
        self.c_w_m = c_w_m
        self.c_w_b = c_w_b

        self.m = self.rng.normal(0, 0.15, n_m)
        self.b = self.rng.normal(0, 0.15, n_b)
        self.e = np.zeros(n_e)
        self.M = 0.08
        self.E = 0.75

        self.W_mm = self._scaled_matrix(n_m, 0.82)
        self.W_mb = self.rng.normal(0, 0.28, (n_m, n_b))
        self.W_me = self.rng.normal(0, 0.32, (n_m, n_e))
        self.W_bm = self.rng.normal(0, 0.26, (n_b, n_m))
        self.W_bb = self._scaled_matrix(n_b, 0.68)

        self.m_hist = []
        self.b_hist = []
        self.e_hist = []
        self.psi_hist = []

    def _scaled_matrix(self, n: int, radius: float) -> np.ndarray:
        A = self.rng.normal(0, 1, (n, n))
        eig = np.linalg.eigvals(A)
        return A * (radius / max(np.max(np.abs(eig)), 1e-8))

    def _env(self, t: float) -> np.ndarray:
        base = np.array([
            np.sin(0.45 * t + 0.2),
            np.cos(0.18 * t + 1.1),
            np.sin(0.9 * t + 0.7),
        ])
        pulses = np.zeros(3)
        for center, amp, width in [(10, 0.8, 1.8), (25, 1.0, 1.5), (42, 0.7, 2.3)]:
            pulses += amp * np.exp(-0.5 * ((t - center) / width) ** 2)
        noise = self.rng.normal(0, self.regime.noise_scale, 3)
        return self.regime.env_gain * (base + 0.30 * pulses) + noise

    def _window(self, arr, n: int = 18):
        if len(arr) == 0:
            return np.empty((0,))
        return np.asarray(arr[-n:])

    def _coupling(self, X: np.ndarray, Y: np.ndarray) -> float:
        if len(X) < 5 or len(Y) < 5:
            return 0.0
        Xc = X - X.mean(axis=0, keepdims=True)
        Yc = Y - Y.mean(axis=0, keepdims=True)
        Xstd = Xc.std(axis=0, keepdims=True)
        Ystd = Yc.std(axis=0, keepdims=True)
        Xstd[Xstd < 1e-8] = 1.0
        Ystd[Ystd < 1e-8] = 1.0
        corr = ((Xc / Xstd).T @ (Yc / Ystd)) / max(X.shape[0] - 1, 1)
        return float(np.mean(np.abs(corr)))

    def _complexity(self, X: np.ndarray) -> float:
        if len(X) < 5:
            return 0.0
        var = np.mean(np.var(X, axis=0))
        return float(var / (var + 0.6))

    def _recursivity(self, x: np.ndarray) -> float:
        if len(x) < 6:
            return 0.0
        x0 = x[:-1]
        x1 = x[1:]
        x0c = x0 - x0.mean()
        x1c = x1 - x1.mean()
        den = np.sqrt((x0c ** 2).sum() * (x1c ** 2).sum())
        if den < 1e-8:
            return 0.0
        return float(abs((x0c * x1c).sum() / den))

    def _valuation(self) -> tuple[float, float, float]:
        body_mag = np.mean(np.abs(self.b)) + self.regime.arousal_bias
        v_bio = self.regime.bio_gain * sigmoid(2.1 * body_mag - 0.6)
        assoc = np.mean(np.abs(self.m[:2])) + 0.6 * self.M
        v_soc = self.regime.social_gain * sigmoid(1.8 * assoc - 0.5)
        return float(v_bio + v_soc), float(v_bio), float(v_soc)

    def step(self, t: float) -> dict:
        self.e = self._env(t)

        M_hist = self._window(self.m_hist)
        B_hist = self._window(self.b_hist)
        E_hist = self._window(self.e_hist)
        P_hist = np.array(self.psi_hist[-18:]) if len(self.psi_hist) else np.empty((0,))

        B = self._coupling(M_hist, B_hist) if M_hist.size and B_hist.size else 0.0
        ME = self._coupling(M_hist, E_hist) if M_hist.size and E_hist.size else 0.0
        K = self._complexity(M_hist) if M_hist.size else 0.0
        R = self._recursivity(P_hist) if len(P_hist) else 0.0

        Psi = self.regime.coherence_bias * (self.w_mb * B + self.w_me * ME + self.w_k * K + self.w_r * R)

        demand = self.regime.dissipation * (
            1.0 + 0.18 * np.mean(np.abs(self.m)) + 0.10 * np.mean(np.abs(self.b))
        )
        self.E = float(np.clip(self.E + self.dt * (self.regime.power_in - demand), 0.02, 2.0))
        Psi_eff = float((self.E / (self.E + 0.45)) * Psi)

        V, V_bio, V_soc = self._valuation()
        Q = float(sigmoid(2.7 * Psi_eff + 1.5 * self.M + 0.9 * V - 1.05))

        surprise = float(np.mean(np.abs(self.e)) / (1.0 + np.mean(np.abs(self.e))))
        self.M = float(
            np.clip(
                self.M + self.dt * (self.regime.mem_gain * (0.75 * Q + 0.25 * surprise) - self.regime.mem_decay * self.M),
                0.0,
                2.0,
            )
        )

        noise_m = self.rng.normal(0, self.regime.noise_scale, self.n_m)
        dm = (
            -0.52 * self.m
            + np.tanh(self.W_mm @ self.m)
            + self.regime.brain_body_gain * np.tanh(self.W_mb @ self.b)
            + np.tanh(self.W_me @ self.e)
            + 0.10 * Q
            + 0.06 * self.M
            + noise_m
        )
        noise_b = self.rng.normal(0, self.regime.noise_scale, self.n_b)
        db = (
            -0.60 * self.b
            + np.tanh(self.W_bb @ self.b)
            + self.regime.body_brain_gain * np.tanh(self.W_bm @ self.m)
            + 0.18 * Q
            + self.regime.arousal_bias * 0.05
            + noise_b
        )

        self.m = self.m + self.dt * dm
        self.b = self.b + self.dt * db

        M_cap = float(self.M / (self.M + 1.0))
        C_idx = float(
            np.clip(
                self.c_w_psi * Psi_eff + self.c_w_q * Q + self.c_w_m * M_cap + self.c_w_b * B,
                0.0,
                1.0,
            )
        )

        thresholds = [0.10, 0.22, 0.38, 0.56, 0.74]
        level = int(sum(C_idx >= th for th in thresholds))

        self.m_hist.append(self.m.copy())
        self.b_hist.append(self.b.copy())
        self.e_hist.append(self.e.copy())
        self.psi_hist.append(Psi_eff)

        return {
            "t": t, "E": self.E, "Psi_eff": Psi_eff, "B": B, "ME": ME, "K": K, "R": R,
            "Q": Q, "M": self.M, "C_idx": C_idx, "level": level
        }

    def run(self, T: float = 28.0) -> pd.DataFrame:
        rows = []
        for t in np.arange(0.0, T, self.dt):
            rows.append(self.step(float(t)))
        return pd.DataFrame(rows)


def default_regimes():
    return {
        "wake": Regime("wake", 1.0, 0.045, 0.90, 0.82, 0.058, 0.043, 0.11, 0.040, 0.32, 0.24, 1.05, 0.00),
        "deep_sleep": Regime("deep_sleep", 0.22, 0.018, 0.40, 0.35, 0.042, 0.047, 0.028, 0.065, 0.14, 0.03, 0.70, -0.08),
        "anxiety": Regime("anxiety", 1.05, 0.085, 0.84, 1.08, 0.060, 0.053, 0.10, 0.042, 0.62, 0.30, 0.82, 0.45),
        "reflex": Regime("reflex", 1.00, 0.028, 0.18, 0.15, 0.040, 0.050, 0.010, 0.085, 0.18, 0.00, 0.55, 0.05),
    }

def model_variant_kwargs(variant: str) -> dict:
    if variant == "full":
        return {}
    if variant == "no_body":
        return {"w_mb": 0.0, "c_w_b": 0.0}
    if variant == "no_memory":
        return {"c_w_m": 0.0}
    if variant == "no_recursion":
        return {"w_r": 0.0}
    if variant == "neural_only":
        return {"w_mb": 0.0, "c_w_b": 0.0, "w_r": 0.0, "c_w_m": 0.0}
    raise ValueError(variant)

def summarize_run(df: pd.DataFrame, regime: str, run_id: int, variant: str) -> dict:
    return {
        "variant": variant,
        "regime": regime,
        "run_id": run_id,
        "C_idx_mean": df["C_idx"].mean(),
        "Psi_eff_mean": df["Psi_eff"].mean(),
        "B_mean": df["B"].mean(),
        "Q_mean": df["Q"].mean(),
        "K_mean": df["K"].mean(),
        "R_mean": df["R"].mean(),
        "M_final": df["M"].iloc[-1],
        "level_mode": int(df["level"].mode().iloc[0]),
    }

def monte_carlo(variant: str = "full", n_runs: int = 10, T: float = 28.0, dt: float = 0.10, seed: int = 42) -> pd.DataFrame:
    rows = []
    kwargs = model_variant_kwargs(variant)
    for r_idx, (name, reg) in enumerate(default_regimes().items()):
        for run_id in range(n_runs):
            sys = ConsciousnessSystemV3(regime=reg, dt=dt, seed=seed + r_idx * 1000 + run_id, **kwargs)
            df = sys.run(T=T)
            rows.append(summarize_run(df, regime=name, run_id=run_id, variant=variant))
    return pd.DataFrame(rows)

def build_binary_task(df: pd.DataFrame, task_name: str):
    if task_name == "wake_vs_deep_sleep":
        sub = df[df["regime"].isin(["wake", "deep_sleep"])].copy()
        y = (sub["regime"] == "wake").astype(int).values
    elif task_name == "wake_vs_reflex":
        sub = df[df["regime"].isin(["wake", "reflex"])].copy()
        y = (sub["regime"] == "wake").astype(int).values
    elif task_name == "wake_vs_anxiety":
        sub = df[df["regime"].isin(["wake", "anxiety"])].copy()
        y = (sub["regime"] == "wake").astype(int).values
    elif task_name == "wake_vs_nonwake":
        sub = df.copy()
        y = (sub["regime"] == "wake").astype(int).values
    elif task_name == "integrated_vs_low":
        sub = df.copy()
        y = sub["regime"].isin(["wake", "anxiety"]).astype(int).values
    else:
        raise ValueError(task_name)
    return sub, y

def youden_threshold(y_true: np.ndarray, scores: np.ndarray) -> dict:
    fpr, tpr, thr = roc_curve(y_true, scores)
    j = tpr - fpr
    idx = int(np.argmax(j))
    auc_val = float(roc_auc_score(y_true, scores))
    return {
        "threshold": float(thr[idx]),
        "sensitivity": float(tpr[idx]),
        "specificity": float(1.0 - fpr[idx]),
        "youden_j": float(j[idx]),
        "auc": auc_val,
        "fpr": fpr,
        "tpr": tpr,
    }

def roc_and_thresholds(df: pd.DataFrame, features=None):
    if features is None:
        features = ["C_idx_mean", "B_mean", "Psi_eff_mean", "Q_mean", "K_mean", "R_mean"]
    auc_rows, thr_rows, roc_curves = [], [], {}
    tasks = ["wake_vs_deep_sleep", "wake_vs_reflex", "wake_vs_anxiety", "wake_vs_nonwake", "integrated_vs_low"]
    for task in tasks:
        sub, y = build_binary_task(df, task)
        roc_curves[task] = {}
        for feat in features:
            res = youden_threshold(y, sub[feat].values)
            auc_rows.append({"task": task, "feature": feat, "auc": res["auc"]})
            thr_rows.append({"task": task, "feature": feat, "threshold": res["threshold"], "sensitivity": res["sensitivity"], "specificity": res["specificity"], "youden_j": res["youden_j"], "auc": res["auc"]})
            roc_curves[task][feat] = (res["fpr"], res["tpr"], res["auc"])
    return pd.DataFrame(auc_rows), pd.DataFrame(thr_rows), roc_curves

def ablation_study(n_runs: int = 6, T: float = 22.0, dt: float = 0.10, seed: int = 500):
    rows = []
    for i, variant in enumerate(["full", "no_body", "no_memory", "no_recursion", "neural_only"]):
        df = monte_carlo(variant=variant, n_runs=n_runs, T=T, dt=dt, seed=seed + i * 100)
        auc_df, _, _ = roc_and_thresholds(df, features=["C_idx_mean"])
        auc_df = auc_df.rename(columns={"auc": "auc_cidx"})
        for _, r in auc_df.iterrows():
            rows.append({"variant": variant, "task": r["task"], "auc_cidx": r["auc_cidx"]})
    out = pd.DataFrame(rows)
    full_ref = out[out["variant"] == "full"][["task", "auc_cidx"]].rename(columns={"auc_cidx": "auc_full"})
    out = out.merge(full_ref, on="task", how="left")
    out["delta_auc"] = out["auc_full"] - out["auc_cidx"]
    return out

def coupling_saturation(n_runs: int = 5, T: float = 20.0, dt: float = 0.10, seed: int = 900):
    vals = np.linspace(0.10, 1.30, 13)
    rows = []
    for i, cg in enumerate(vals):
        c_vals = []
        for run_id in range(n_runs):
            reg = Regime("sweep", 1.0, 0.05, float(cg), float(cg), 0.055, 0.046, 0.09, 0.045, 0.30, 0.20, 1.0, 0.10)
            sys = ConsciousnessSystemV3(regime=reg, dt=dt, seed=seed + i * 100 + run_id)
            df = sys.run(T=T)
            c_vals.append(df["C_idx"].mean())
        rows.append({"coupling_gain": float(cg), "C_idx_mean": float(np.mean(c_vals)), "C_idx_sd": float(np.std(c_vals, ddof=1))})
    out = pd.DataFrame(rows)
    x = out["coupling_gain"].values
    y = out["C_idx_mean"].values
    dy = np.gradient(y, x)
    d2y = np.gradient(dy, x)
    out["dC_dB"] = dy
    out["d2C_dB2"] = d2y
    out["saturation_flag"] = out["d2C_dB2"] < 0
    return out

def falsifiable_rules(thr_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    targets = [("wake_vs_deep_sleep", "C_idx_mean"), ("wake_vs_reflex", "B_mean"), ("wake_vs_anxiety", "Psi_eff_mean"), ("integrated_vs_low", "C_idx_mean")]
    for task, feat in targets:
        sub = thr_df[(thr_df["task"] == task) & (thr_df["feature"] == feat)].sort_values("auc", ascending=False)
        if len(sub) == 0:
            continue
        r = sub.iloc[0]
        if task == "wake_vs_deep_sleep":
            rule = f"If {feat} < {r['threshold']:.3f}, predict non-wake / low-integration state."
        elif task == "wake_vs_reflex":
            rule = f"If {feat} < {r['threshold']:.3f}, predict reflex-like subintegrated regime."
        elif task == "wake_vs_anxiety":
            rule = f"If {feat} < {r['threshold']:.3f} while arousal remains high, predict anxiety rather than integrated wakefulness."
        else:
            rule = f"If {feat} >= {r['threshold']:.3f}, predict integrated-like regime over low regime."
        rows.append({"task": task, "feature": feat, "threshold": float(r["threshold"]), "auc": float(r["auc"]), "rule": rule})
    return pd.DataFrame(rows)

def coefficient_of_variation_by_regime(df: pd.DataFrame, feature: str = "C_idx_mean") -> pd.DataFrame:
    grp = df.groupby("regime")[feature].agg(["mean", "std"]).reset_index()
    grp["cv_pct"] = 100.0 * grp["std"] / grp["mean"]
    return grp

def save_all(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    mc = monte_carlo()
    mc.to_csv(outdir / "monte_carlo_runs.csv", index=False)

    regime_summary = mc.groupby("regime")[["C_idx_mean", "Psi_eff_mean", "B_mean", "Q_mean", "K_mean", "R_mean", "M_final"]].agg(["mean", "std"]).reset_index()
    regime_summary.to_csv(outdir / "regime_summary.csv", index=False)

    cv_table = coefficient_of_variation_by_regime(mc)
    cv_table.to_csv(outdir / "cv_table.csv", index=False)

    auc_df, thr_df, roc_curves = roc_and_thresholds(mc)
    auc_df.to_csv(outdir / "auc_table.csv", index=False)
    thr_df.to_csv(outdir / "thresholds_table.csv", index=False)

    ablation = ablation_study()
    ablation.to_csv(outdir / "ablation_table.csv", index=False)

    sat = coupling_saturation()
    sat.to_csv(outdir / "saturation_table.csv", index=False)

    rules = falsifiable_rules(thr_df)
    rules.to_csv(outdir / "falsifiable_rules.csv", index=False)

    winners = auc_df.sort_values(["task", "auc"], ascending=[True, False]).groupby("task").head(1)
    winners.to_csv(outdir / "roc_winners.csv", index=False)

    for feature in ["C_idx_mean", "B_mean", "Psi_eff_mean", "Q_mean"]:
        plt.figure(figsize=(8, 4.8))
        for regime in ["wake", "anxiety", "deep_sleep", "reflex"]:
            vals = mc.loc[mc["regime"] == regime, feature].values
            plt.hist(vals, bins=8, alpha=0.5, density=True, label=regime)
        plt.xlabel(feature); plt.ylabel("density"); plt.title(f"V3 distributions: {feature}")
        plt.legend(); plt.tight_layout()
        plt.savefig(outdir / f"dist_{feature}.png", dpi=160)
        plt.close()

    tasks = ["wake_vs_deep_sleep", "wake_vs_reflex", "wake_vs_anxiety", "wake_vs_nonwake", "integrated_vs_low"]
    features = ["C_idx_mean", "B_mean", "Psi_eff_mean", "Q_mean"]
    fig, axes = plt.subplots(len(tasks), 1, figsize=(7, 4.2 * len(tasks)))
    for ax, task in zip(axes, tasks):
        for feat in features:
            fpr, tpr, auc_val = roc_curves[task][feat]
            ax.plot(fpr, tpr, label=f"{feat} (AUC={auc_val:.3f})")
        ax.plot([0, 1], [0, 1], linestyle="--")
        ax.set_title(task); ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(outdir / "roc_grid.png", dpi=160)
    plt.close()

    plt.figure(figsize=(10, 5))
    tasks_short = ["wake_vs_deep_sleep", "wake_vs_reflex", "wake_vs_anxiety", "integrated_vs_low"]
    for i, task in enumerate(tasks_short):
        sub = ablation[ablation["task"] == task]
        x = np.arange(len(sub)) + i * (len(sub) + 1)
        plt.bar(x, sub["auc_cidx"], label=task)
    plt.ylabel("AUC (C_idx)"); plt.title("V3 ablation performance by task"); plt.legend(); plt.xticks([])
    plt.tight_layout()
    plt.savefig(outdir / "ablation_performance.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 4.8))
    plt.plot(sat["coupling_gain"], sat["C_idx_mean"], label="mean C_idx")
    plt.fill_between(sat["coupling_gain"], sat["C_idx_mean"] - sat["C_idx_sd"], sat["C_idx_mean"] + sat["C_idx_sd"], alpha=0.25, label="±1 sd")
    plt.xlabel("brain-body coupling gain"); plt.ylabel("mean C_idx"); plt.title("V3 saturation curve"); plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "saturation_curve.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 4.8))
    plt.plot(sat["coupling_gain"], sat["d2C_dB2"], label="second derivative")
    plt.axhline(0, linestyle="--")
    plt.xlabel("brain-body coupling gain"); plt.ylabel("d²C/dB²"); plt.title("V3 saturation curvature test"); plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "saturation_curvature.png", dpi=160)
    plt.close()

    readme = """# Consciousness Model V3

Focus:
- thresholds
- ROC comparison
- ablation tests
- falsifiable rules
- saturation analysis

Note:
- This execution uses lighter defaults for speed.
- Increase n_runs and T later for stronger estimates.
"""
    (outdir / "README.md").write_text(readme, encoding="utf-8")

    return {"mc": mc, "regime_summary": regime_summary, "cv_table": cv_table, "auc_df": auc_df, "thr_df": thr_df, "ablation": ablation, "sat": sat, "rules": rules, "winners": winners}
