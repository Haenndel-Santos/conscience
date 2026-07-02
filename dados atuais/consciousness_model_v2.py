
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

class ConsciousnessSystemV2:
    def __init__(self, regime: Regime, dt: float = 0.05, n_m: int = 6, n_b: int = 3, n_e: int = 3, seed: int = 0):
        self.regime = regime
        self.dt = dt
        self.n_m = n_m
        self.n_b = n_b
        self.n_e = n_e
        self.rng = np.random.default_rng(seed)

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

        self.w_mb = 0.35
        self.w_me = 0.20
        self.w_k = 0.20
        self.w_r = 0.25

    def _scaled_matrix(self, n: int, radius: float) -> np.ndarray:
        A = self.rng.normal(0, 1, (n, n))
        eig = np.linalg.eigvals(A)
        scale = radius / max(np.max(np.abs(eig)), 1e-8)
        return A * scale

    def _env(self, t: float) -> np.ndarray:
        base = np.array([
            np.sin(0.45 * t + 0.2),
            np.cos(0.18 * t + 1.1),
            np.sin(0.9 * t + 0.7)
        ])
        pulses = np.zeros(3)
        for center, amp, width in [(10, 0.8, 1.8), (25, 1.0, 1.5), (42, 0.7, 2.3)]:
            pulses += amp * np.exp(-0.5 * ((t - center) / width) ** 2)
        noise = self.rng.normal(0, self.regime.noise_scale, 3)
        return self.regime.env_gain * (base + 0.30 * pulses) + noise

    def _window(self, arr, n=24):
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
        Xn = Xc / Xstd
        Yn = Yc / Ystd
        corr = (Xn.T @ Yn) / max(X.shape[0] - 1, 1)
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
        den = np.sqrt((x0c**2).sum() * (x1c**2).sum())
        if den < 1e-8:
            return 0.0
        r = (x0c * x1c).sum() / den
        return float(abs(r))

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
        P_hist = np.array(self.psi_hist[-24:]) if len(self.psi_hist) else np.empty((0,))

        B = self._coupling(M_hist, B_hist) if M_hist.size and B_hist.size else 0.0
        ME = self._coupling(M_hist, E_hist) if M_hist.size and E_hist.size else 0.0
        K = self._complexity(M_hist) if M_hist.size else 0.0
        R = self._recursivity(P_hist) if len(P_hist) else 0.0

        Psi = self.regime.coherence_bias * (self.w_mb * B + self.w_me * ME + self.w_k * K + self.w_r * R)

        demand = self.regime.dissipation * (1.0 + 0.18 * np.mean(np.abs(self.m)) + 0.10 * np.mean(np.abs(self.b)))
        dE = self.regime.power_in - demand
        self.E = float(np.clip(self.E + self.dt * dE, 0.02, 2.0))
        Psi_eff = float((self.E / (self.E + 0.45)) * Psi)

        V, V_bio, V_soc = self._valuation()
        Q = float(sigmoid(2.7 * Psi_eff + 1.5 * self.M + 0.9 * V - 1.05))

        surprise = float(np.mean(np.abs(self.e)) / (1.0 + np.mean(np.abs(self.e))))
        dM = self.regime.mem_gain * (0.75 * Q + 0.25 * surprise) - self.regime.mem_decay * self.M
        self.M = float(np.clip(self.M + self.dt * dM, 0.0, 2.0))

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
        C_idx = float(np.clip(0.45 * Psi_eff + 0.20 * Q + 0.17 * M_cap + 0.18 * B, 0.0, 1.0))

        thresholds = [0.10, 0.22, 0.38, 0.56, 0.74]
        level = int(sum(C_idx >= th for th in thresholds))
        A = float(np.tanh(0.55 * np.mean(self.m) + 0.25 * np.mean(self.b) + 0.20 * Q))

        self.m_hist.append(self.m.copy())
        self.b_hist.append(self.b.copy())
        self.e_hist.append(self.e.copy())
        self.psi_hist.append(Psi_eff)

        return {
            "t": t, "E": self.E, "Psi": Psi, "Psi_eff": Psi_eff, "B": B, "ME": ME, "K": K, "R": R,
            "Q": Q, "M": self.M, "V": V, "V_bio": V_bio, "V_soc": V_soc, "C_idx": C_idx, "level": level,
            "A": A, "m_mean": float(np.mean(self.m)), "b_mean": float(np.mean(self.b))
        }

    def run(self, T: float = 50.0) -> pd.DataFrame:
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

def run_regimes(T=50.0, dt=0.05, seed=42):
    outputs = {}
    for i, (name, reg) in enumerate(default_regimes().items()):
        sys = ConsciousnessSystemV2(regime=reg, dt=dt, seed=seed + i)
        outputs[name] = sys.run(T=T)
    return outputs

def phase_map(T=20.0, dt=0.08, seed=100):
    coupling_vals = np.linspace(0.15, 1.10, 9)
    bio_vals = np.linspace(0.10, 0.75, 9)
    rows = []
    for i, cg in enumerate(coupling_vals):
        for j, bg in enumerate(bio_vals):
            reg = Regime("phase", 1.0, 0.05, float(cg), float(cg), 0.055, 0.046, 0.09, 0.045, float(bg), 0.20, 1.0, 0.10)
            sys = ConsciousnessSystemV2(regime=reg, dt=dt, seed=seed + i * 100 + j)
            df = sys.run(T=T)
            rows.append({"coupling": cg, "bio_gain": bg, "C_idx_mean": df["C_idx"].mean(), "Q_mean": df["Q"].mean(), "Psi_eff_mean": df["Psi_eff"].mean()})
    return pd.DataFrame(rows)

def coupling_sweep(T=25.0, dt=0.08, seed=200):
    vals = np.linspace(0.10, 1.20, 12)
    rows = []
    for i, cg in enumerate(vals):
        reg = Regime("coupling_sweep", 1.0, 0.05, float(cg), float(cg), 0.055, 0.046, 0.09, 0.045, 0.30, 0.20, 1.0, 0.10)
        sys = ConsciousnessSystemV2(regime=reg, dt=dt, seed=seed + i)
        df = sys.run(T=T)
        rows.append({"coupling_gain": cg, "C_idx_mean": df["C_idx"].mean(), "Psi_eff_mean": df["Psi_eff"].mean(), "B_mean": df["B"].mean(), "Q_mean": df["Q"].mean()})
    return pd.DataFrame(rows)

def save_all(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    outputs = run_regimes()
    summary_rows = []

    for name, df in outputs.items():
        df.to_csv(outdir / f"{name}_timeseries.csv", index=False)
        summary_rows.append({
            "regime": name,
            "C_idx_mean": df["C_idx"].mean(),
            "C_idx_max": df["C_idx"].max(),
            "Psi_eff_mean": df["Psi_eff"].mean(),
            "B_mean": df["B"].mean(),
            "Q_mean": df["Q"].mean(),
            "M_final": df["M"].iloc[-1],
            "level_mode": int(df["level"].mode().iloc[0]),
        })

        plt.figure(figsize=(8, 4.5))
        plt.plot(df["t"], df["C_idx"], label="C_idx")
        plt.plot(df["t"], df["Psi_eff"], label="Psi_eff")
        plt.plot(df["t"], df["Q"], label="Q")
        plt.xlabel("Time")
        plt.ylabel("Index")
        plt.title(f"{name}: core indices")
        plt.legend()
        plt.tight_layout()
        plt.savefig(outdir / f"{name}_indices.png", dpi=160)
        plt.close()

        plt.figure(figsize=(8, 4.5))
        plt.plot(df["t"], df["B"], label="B")
        plt.plot(df["t"], df["M"], label="M")
        plt.plot(df["t"], df["E"], label="E")
        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.title(f"{name}: coupling, memory, energy")
        plt.legend()
        plt.tight_layout()
        plt.savefig(outdir / f"{name}_state_vars.png", dpi=160)
        plt.close()

        plt.figure(figsize=(5, 5))
        plt.plot(df["m_mean"], df["b_mean"])
        plt.xlabel("mean neural state")
        plt.ylabel("mean bodily state")
        plt.title(f"{name}: brain-body phase loop")
        plt.tight_layout()
        plt.savefig(outdir / f"{name}_phase.png", dpi=160)
        plt.close()

    summary = pd.DataFrame(summary_rows).sort_values("C_idx_mean", ascending=False)
    summary.to_csv(outdir / "summary.csv", index=False)

    sweep = coupling_sweep()
    sweep.to_csv(outdir / "coupling_sweep.csv", index=False)

    phase = phase_map()
    phase.to_csv(outdir / "phase_map.csv", index=False)

    plt.figure(figsize=(8, 4.5))
    plt.bar(summary["regime"], summary["C_idx_mean"])
    plt.ylabel("mean consciousness index")
    plt.title("V2: mean consciousness by regime")
    plt.tight_layout()
    plt.savefig(outdir / "regime_comparison.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.plot(sweep["coupling_gain"], sweep["C_idx_mean"], label="C_idx_mean")
    plt.plot(sweep["coupling_gain"], sweep["Psi_eff_mean"], label="Psi_eff_mean")
    plt.plot(sweep["coupling_gain"], sweep["Q_mean"], label="Q_mean")
    plt.xlabel("brain-body coupling gain")
    plt.ylabel("mean value")
    plt.title("V2: coupling sweep")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "coupling_sweep.png", dpi=160)
    plt.close()

    piv = phase.pivot(index="bio_gain", columns="coupling", values="C_idx_mean")
    plt.figure(figsize=(7, 5.5))
    plt.imshow(piv.values, origin="lower", aspect="auto",
               extent=[piv.columns.min(), piv.columns.max(), piv.index.min(), piv.index.max()])
    plt.colorbar(label="mean C_idx")
    plt.xlabel("coupling")
    plt.ylabel("bio_gain")
    plt.title("V2: phase map of mean consciousness index")
    plt.tight_layout()
    plt.savefig(outdir / "phase_map.png", dpi=160)
    plt.close()

    readme = """# Consciousness Model V2

Operational definitions:
- B(t): mean absolute brain-body cross-correlation in a rolling window.
- Psi(t): weighted sum of B(t), brain-environment coupling, complexity, and recursivity.
- M(t): dynamic memory trace with consolidation and decay.
- Q(t): phenomenological-potential proxy, not qualia itself.

Experiments:
- four-regime comparison
- coupling sweep
- phase map (coupling x bodily valuation)
"""
    (outdir / "README.md").write_text(readme, encoding="utf-8")

    return summary, sweep, phase
