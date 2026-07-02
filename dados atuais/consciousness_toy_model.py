
"""
Toy model for an embodied consciousness theory.

Implements:
- neural state m(t)
- bodily state b(t)
- environmental input e(t)
- memory trace M(t)
- energy availability E(t)
- integration proxy Psi(t)
- phenomenological potential Q(t)
- consciousness index C_idx(t)
- gradient level G(t)

Regimes:
- wake
- deep_sleep
- anxiety
- reflex

This is a deliberately simple, auditable prototype meant to test the
formal structure, not to claim biological completeness.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def sigmoid(x: float | np.ndarray) -> float | np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


@dataclass
class RegimeConfig:
    name: str
    # Environmental drive amplitude
    env_gain: float
    # Brain-body coupling
    brain_body_gain: float
    body_brain_gain: float
    # Memory consolidation and decay
    mem_gain: float
    mem_decay: float
    # Energy inflow and dissipation
    power_in: float
    dissipation: float
    # Valuation scaling
    social_gain: float
    bio_gain: float
    # Noise level
    noise_scale: float
    # Integration weights
    alpha: float = 0.30
    beta: float = 0.25
    gamma: float = 0.20
    delta: float = 0.25


class ConsciousnessSystem:
    """
    Minimal embodied consciousness simulator.

    State variables
    ---------------
    m : neural state vector, shape (n_m,)
    b : bodily state vector, shape (n_b,)
    e : environmental input vector, shape (n_e,)
    M : scalar memory trace
    E : scalar energy availability
    """

    def __init__(
        self,
        regime: RegimeConfig,
        n_m: int = 5,
        n_b: int = 3,
        n_e: int = 3,
        dt: float = 0.05,
        seed: int = 42,
    ) -> None:
        self.regime = regime
        self.n_m = n_m
        self.n_b = n_b
        self.n_e = n_e
        self.dt = dt
        self.rng = np.random.default_rng(seed)

        # State initialization
        self.m = self.rng.normal(0, 0.2, n_m)
        self.b = self.rng.normal(0, 0.2, n_b)
        self.e = np.zeros(n_e)
        self.M = 0.1
        self.E = 0.7

        # Fixed coupling matrices
        self.W_mm = self._stable_matrix(n_m, spectral_radius=0.85)
        self.W_mb = self.rng.normal(0, 0.35, (n_m, n_b))
        self.W_me = self.rng.normal(0, 0.40, (n_m, n_e))
        self.W_bm = self.rng.normal(0, 0.30, (n_b, n_m))
        self.W_bb = self._stable_matrix(n_b, spectral_radius=0.65)

        # Buffers for temporal metrics
        self.psi_hist = []
        self.m_hist = []
        self.b_hist = []

    def _stable_matrix(self, n: int, spectral_radius: float) -> np.ndarray:
        A = self.rng.normal(0, 1, (n, n))
        eigvals = np.linalg.eigvals(A)
        scale = spectral_radius / max(1e-8, np.max(np.abs(eigvals)))
        return A * scale

    def _environment(self, t: float) -> np.ndarray:
        # Multi-timescale signal
        base = np.array([
            math.sin(0.6 * t),
            math.cos(0.23 * t + 0.5),
            math.sin(1.1 * t + 1.2)
        ])
        pulses = np.zeros(3)
        # A few transient events to trigger state changes
        for center, amp, width in [(12, 1.2, 1.6), (26, 0.8, 1.2), (41, 1.0, 2.0)]:
            pulses += amp * np.exp(-0.5 * ((t - center) / width) ** 2)
        signal = self.regime.env_gain * (base + 0.35 * pulses)
        noise = self.rng.normal(0, self.regime.noise_scale, 3)
        return signal + noise

    def _mutual_info_proxy(self, x: np.ndarray, y: np.ndarray) -> float:
        """
        Lightweight bounded dependence proxy based on absolute correlation.
        Not true MI, but stable and auditable for a toy model.
        """
        x = np.asarray(x).ravel()
        y = np.asarray(y).ravel()
        if x.std() < 1e-8 or y.std() < 1e-8:
            return 0.0
        # use mean absolute pairwise correlation proxy
        vals = []
        for xi in np.atleast_2d(x).T:
            for yj in np.atleast_2d(y).T:
                r = np.corrcoef(xi.ravel(), yj.ravel())[0, 1] if len(xi.ravel()) > 1 else 0.0
                if np.isnan(r):
                    r = 0.0
                vals.append(abs(r))
        return float(np.mean(vals)) if vals else 0.0

    def _coupling_proxy(self, x_hist: np.ndarray, y_hist: np.ndarray) -> float:
        """
        Mean absolute lag-0 cross correlation across recent history.
        """
        if len(x_hist) < 4 or len(y_hist) < 4:
            return 0.0
        vals = []
        for i in range(x_hist.shape[1]):
            for j in range(y_hist.shape[1]):
                x = x_hist[:, i]
                y = y_hist[:, j]
                if x.std() < 1e-8 or y.std() < 1e-8:
                    vals.append(0.0)
                else:
                    r = np.corrcoef(x, y)[0, 1]
                    if np.isnan(r):
                        r = 0.0
                    vals.append(abs(r))
        return float(np.mean(vals)) if vals else 0.0

    def _complexity_proxy(self, m_hist: np.ndarray) -> float:
        """
        Complexity as balanced variability:
        higher for non-flat and non-saturated dynamics.
        """
        if len(m_hist) < 4:
            return 0.0
        var = np.mean(np.var(m_hist, axis=0))
        # bounded saturating map
        return float(var / (var + 1.0))

    def _recursivity_proxy(self, psi_hist: np.ndarray) -> float:
        """
        Recursivity / temporal coherence as lag-1 autocorrelation magnitude.
        """
        if len(psi_hist) < 5:
            return 0.0
        x = np.asarray(psi_hist)
        x0 = x[:-1]
        x1 = x[1:]
        if x0.std() < 1e-8 or x1.std() < 1e-8:
            return 0.0
        r = np.corrcoef(x0, x1)[0, 1]
        if np.isnan(r):
            return 0.0
        return float(abs(r))

    def _bio_valuation(self) -> float:
        # bodily salience grows with arousal and interoceptive magnitude
        mag = np.mean(np.abs(self.b))
        return float(self.regime.bio_gain * sigmoid(2.0 * mag - 0.5))

    def _social_valuation(self) -> float:
        # crude proxy: cortical association + memory amplify social weighting
        assoc = np.mean(np.abs(self.m[: min(2, len(self.m))]))
        return float(self.regime.social_gain * sigmoid(1.8 * assoc + 1.2 * self.M - 0.6))

    def _gradient_level(self, c_idx: float) -> int:
        thresholds = [0.12, 0.24, 0.40, 0.58, 0.76]
        level = 0
        for th in thresholds:
            if c_idx >= th:
                level += 1
        return level  # 0..5

    def step(self, t: float) -> dict:
        self.e = self._environment(t)

        # Recent windows for metrics
        m_hist = np.array(self.m_hist[-20:]) if self.m_hist else np.empty((0, self.n_m))
        b_hist = np.array(self.b_hist[-20:]) if self.b_hist else np.empty((0, self.n_b))
        psi_hist = np.array(self.psi_hist[-20:]) if self.psi_hist else np.empty((0,))

        # Component metrics for integration
        if len(m_hist) >= 4 and len(b_hist) >= 4:
            I_mb = self._coupling_proxy(m_hist, b_hist)
        else:
            I_mb = 0.0

        if len(m_hist) >= 4:
            # align window length with synthetic environment history proxy
            env_proxy = np.tile(self.e, (len(m_hist), 1))
            I_me = self._coupling_proxy(m_hist, env_proxy)
        else:
            I_me = 0.0

        K = self._complexity_proxy(m_hist) if len(m_hist) >= 4 else 0.0
        R = self._recursivity_proxy(psi_hist) if len(psi_hist) >= 5 else 0.0

        psi = (
            self.regime.alpha * I_mb
            + self.regime.beta * I_me
            + self.regime.gamma * K
            + self.regime.delta * R
        )

        # Energy dynamics
        dE = self.regime.power_in - self.regime.dissipation * (1.0 + 0.15 * np.mean(np.abs(self.m)))
        self.E = float(np.clip(self.E + self.dt * dE, 0.02, 2.0))
        psi_eff = float((self.E / (self.E + 0.5)) * psi)

        # Valuation terms
        V_bio = self._bio_valuation()
        V_soc = self._social_valuation()
        V = V_bio + V_soc

        # Qualia potential
        Q = float(sigmoid(2.4 * psi_eff + 1.4 * self.M + 1.1 * V - 1.1))

        # Coupling term used explicitly in consciousness index
        B = I_mb

        # Memory dynamics
        dM = self.regime.mem_gain * Q - self.regime.mem_decay * self.M
        self.M = float(np.clip(self.M + self.dt * dM, 0.0, 2.0))

        # Neural dynamics
        noise_m = self.rng.normal(0, self.regime.noise_scale, self.n_m)
        dm = (
            -0.55 * self.m
            + np.tanh(self.W_mm @ self.m)
            + self.regime.brain_body_gain * np.tanh(self.W_mb @ self.b)
            + np.tanh(self.W_me @ self.e)
            + 0.15 * Q
            + 0.08 * self.M
            + noise_m
        )
        self.m = self.m + self.dt * dm

        # Bodily dynamics
        noise_b = self.rng.normal(0, self.regime.noise_scale, self.n_b)
        db = (
            -0.65 * self.b
            + np.tanh(self.W_bb @ self.b)
            + self.regime.body_brain_gain * np.tanh(self.W_bm @ self.m)
            + 0.18 * Q
            + noise_b
        )
        self.b = self.b + self.dt * db

        # Consciousness index
        mem_cap = float(self.M / (self.M + 1.0))
        C_idx = float(np.clip(
            0.42 * psi_eff + 0.24 * Q + 0.18 * mem_cap + 0.16 * B, 0.0, 1.0
        ))
        level = self._gradient_level(C_idx)

        # Simple action index (not a focal claim, just a readout)
        A = float(np.tanh(0.6 * np.mean(self.m) + 0.3 * np.mean(self.b) + 0.2 * Q))

        # Update history after state update
        self.psi_hist.append(psi_eff)
        self.m_hist.append(self.m.copy())
        self.b_hist.append(self.b.copy())

        return {
            "t": t,
            "E": self.E,
            "Psi": psi,
            "Psi_eff": psi_eff,
            "Q": Q,
            "M": self.M,
            "B": B,
            "V_bio": V_bio,
            "V_soc": V_soc,
            "C_idx": C_idx,
            "level": level,
            "A": A,
            "m_mean": float(np.mean(self.m)),
            "b_mean": float(np.mean(self.b)),
            "m_norm": float(np.linalg.norm(self.m)),
            "b_norm": float(np.linalg.norm(self.b)),
            "e_mean": float(np.mean(self.e)),
        }

    def run(self, T: float = 60.0) -> pd.DataFrame:
        times = np.arange(0.0, T, self.dt)
        rows = [self.step(float(t)) for t in times]
        return pd.DataFrame(rows)


def default_regimes() -> dict[str, RegimeConfig]:
    return {
        "wake": RegimeConfig(
            name="wake",
            env_gain=1.0,
            brain_body_gain=0.95,
            body_brain_gain=0.85,
            mem_gain=0.10,
            mem_decay=0.04,
            power_in=0.055,
            dissipation=0.045,
            social_gain=0.25,
            bio_gain=0.35,
            noise_scale=0.05,
        ),
        "deep_sleep": RegimeConfig(
            name="deep_sleep",
            env_gain=0.25,
            brain_body_gain=0.45,
            body_brain_gain=0.40,
            mem_gain=0.03,
            mem_decay=0.06,
            power_in=0.045,
            dissipation=0.048,
            social_gain=0.05,
            bio_gain=0.15,
            noise_scale=0.02,
        ),
        "anxiety": RegimeConfig(
            name="anxiety",
            env_gain=1.15,
            brain_body_gain=1.10,
            body_brain_gain=1.20,
            mem_gain=0.12,
            mem_decay=0.03,
            power_in=0.060,
            dissipation=0.055,
            social_gain=0.35,
            bio_gain=0.55,
            noise_scale=0.07,
        ),
        "reflex": RegimeConfig(
            name="reflex",
            env_gain=1.05,
            brain_body_gain=0.22,
            body_brain_gain=0.18,
            mem_gain=0.01,
            mem_decay=0.08,
            power_in=0.040,
            dissipation=0.050,
            social_gain=0.00,
            bio_gain=0.18,
            noise_scale=0.03,
        ),
    }


def run_all_regimes(T: float = 60.0, dt: float = 0.05, seed: int = 42) -> dict[str, pd.DataFrame]:
    outputs = {}
    for i, (name, cfg) in enumerate(default_regimes().items()):
        system = ConsciousnessSystem(cfg, dt=dt, seed=seed + i)
        outputs[name] = system.run(T=T)
    return outputs


def save_outputs(outdir: str = ".", T: float = 60.0, dt: float = 0.05, seed: int = 42) -> dict[str, pd.DataFrame]:
    import os

    os.makedirs(outdir, exist_ok=True)
    outputs = run_all_regimes(T=T, dt=dt, seed=seed)
    summary_rows = []

    for name, df in outputs.items():
        df.to_csv(os.path.join(outdir, f"{name}_timeseries.csv"), index=False)

        summary_rows.append({
            "regime": name,
            "C_idx_mean": df["C_idx"].mean(),
            "C_idx_max": df["C_idx"].max(),
            "Psi_eff_mean": df["Psi_eff"].mean(),
            "Q_mean": df["Q"].mean(),
            "M_final": df["M"].iloc[-1],
            "B_mean": df["B"].mean(),
            "level_mode": int(df["level"].mode().iloc[0]),
        })

        plt.figure(figsize=(8, 4.5))
        plt.plot(df["t"], df["C_idx"], label="C_idx")
        plt.plot(df["t"], df["Psi_eff"], label="Psi_eff")
        plt.plot(df["t"], df["Q"], label="Q")
        plt.xlabel("Time")
        plt.ylabel("Index")
        plt.title(f"{name} regime: core indices")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"{name}_indices.png"), dpi=160)
        plt.close()

        plt.figure(figsize=(5, 5))
        plt.plot(df["m_mean"], df["b_mean"])
        plt.xlabel("mean neural state")
        plt.ylabel("mean bodily state")
        plt.title(f"{name} regime: brain-body phase loop")
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"{name}_phase.png"), dpi=160)
        plt.close()

    summary = pd.DataFrame(summary_rows).sort_values("C_idx_mean", ascending=False)
    summary.to_csv(os.path.join(outdir, "summary.csv"), index=False)

    plt.figure(figsize=(8, 4.5))
    plt.bar(summary["regime"], summary["C_idx_mean"])
    plt.ylabel("mean consciousness index")
    plt.title("Mean consciousness index by regime")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "regime_comparison.png"), dpi=160)
    plt.close()

    return outputs


if __name__ == "__main__":
    save_outputs(outdir="consciousness_outputs")
