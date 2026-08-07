"""Frente E — Teste de calibração/identificabilidade do modelo V3.

REGRA DE GOVERNANÇA (`PLANO_ESTRATEGICO_cientifico.md` §0.1): este script foi
ESCRITO por um agente e NÃO foi executado por ele nos parâmetros reais. O
agente verificou sintaxe e rodou um teste de fumaça com parâmetros bem
reduzidos, só para confirmar que a lógica não quebra.

PERGUNTA QUE ESTE SCRIPT RESPONDE
----------------------------------
`PLANO_ESTRATEGICO_cientifico.md`, Frente E, pede: "tentar uma calibração:
constranger parâmetros do modelo para reproduzir a ordenação empírica de
LZc/PE observada no Sleep-EDF, e reportar se o modelo é um ajuste genuíno ou
uma tautologia."

Mapeamento honesto (única correspondência empírica inequívoca disponível):
`wake` (V3) ~ estágio W (Sleep-EDF); `deep_sleep` (V3) ~ estágio N3. Os
outros dois regimes do V3 (anxiety, reflex) não têm par empírico limpo nos
dados de sono já recompuados (não há um "estágio de ansiedade" no Sleep-EDF),
e por isso NÃO entram nesta calibração — usar N1/REM/N2 exigiria um
mapeamento adicional não fundamentado, que não vamos inventar aqui. O alvo
empírico é a discriminação W-vs-N3 real: AUC(LZc) = 0,9919 (Sleep-EDF, n=36,
ver `recompute_empirico_v2/RELATORIO_v2.md`). Como o confronto com o modelo
é sempre de ordenação/direção (nunca de unidades absolutas — `C_idx` não
está calibrado nas mesmas unidades de LZc/PE), o alvo de calibração aqui é o
AUC de C_idx entre wake e deep_sleep, não a magnitude bruta.

A PERGUNTA "GENUÍNO OU TAUTOLOGIA" OPERACIONALIZADA
-----------------------------------------------------
Reproduzir AUC alto não é, sozinho, evidência de nada — o teste real é: QUÃO
FÁCIL é reproduzir esse AUC alto variando os pesos livremente?
- Se uma fração GRANDE de combinações de pesos, sorteadas aleatoriamente
  dentro de limites amplos (0 a 2x o valor de referência de cada peso), já
  produz AUC alto (>=0,90 ou >=0,95), isso sustenta a leitura de que a
  separação wake/deep_sleep é quase garantida "por construção" — reproduzir
  o dado real não é uma restrição forte sobre o modelo, é algo que a
  arquitetura já faz para quase qualquer parametrização razoável.
- Se só uma região ESTREITA do espaço de parâmetros atinge AUC alto, isso é
  evidência de uma restrição mais genuína — o ajuste aos dados reais exige
  algo específico dos coeficientes, não é trivial.
- Adicionalmente, uma busca de otimização a partir de VÁRIOS pontos de
  partida aleatórios que converge para regiões muito diferentes do espaço de
  parâmetros (todas com AUC igualmente alto) é evidência de
  NÃO-IDENTIFICABILIDADE — há múltiplas soluções equivalentes, o que também
  enfraquece a leitura de "ajuste genuíno único".

Nenhuma dessas duas leituras é decidida por este script — ele só produz os
números; a interpretação (Leitura, no fim da saída) é um guia, não uma
conclusão pronta.

DEPENDÊNCIA DE OUTRO ARQUIVO DO PROJETO
----------------------------------------
Importa `consciousness_model_v3.py` de `dados atuais/` (mesma convenção de
`sensibilidade_v3.py` — ver docstring de lá para detalhes de path).

Uso:
    python calibracao_v3.py
    python calibracao_v3.py --n-samples 400 --n-starts 8   # mais preciso, mais lento
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
from sklearn.metrics import roc_auc_score

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "dados atuais"

PARAM_NAMES = ["w_mb", "w_me", "w_k", "w_r", "c_w_psi", "c_w_q", "c_w_m", "c_w_b"]
BASELINE = dict(
    w_mb=0.35, w_me=0.20, w_k=0.20, w_r=0.25,
    c_w_psi=0.45, c_w_q=0.20, c_w_m=0.17, c_w_b=0.18,
)
# Limites generosos: 0 a 2x o valor de referência de cada peso. A única
# restrição estrutural do modelo é não-negatividade (os pesos não precisam
# somar 1 — ver `ConsciousnessSystemV3.__init__`, eles multiplicam termos
# independentes de Ψ_eff/C_idx, não são uma partição de probabilidade).
BOUNDS = {k: (0.0, 2.0 * v) for k, v in BASELINE.items()}

EMPIRICAL_AUC_TARGET = 0.9919  # AUC W-vs-N3 real (LZc), Sleep-EDF n=36 — RELATORIO_v2.md, seção 2.


def _import_v3(model_dir):
    model_dir = Path(model_dir)
    if not (model_dir / "consciousness_model_v3.py").exists():
        raise FileNotFoundError(
            f"Não encontrei consciousness_model_v3.py em '{model_dir}'. "
            "Rode este script de dentro de scripts_para_rodar/robustez_modelo/, "
            "ou use --model-dir."
        )
    if str(model_dir) not in sys.path:
        sys.path.insert(0, str(model_dir))
    import consciousness_model_v3 as v3  # type: ignore
    return v3


def _params_to_kwargs(vec) -> dict:
    return {name: float(val) for name, val in zip(PARAM_NAMES, vec)}


def _sample_uniform(rng) -> np.ndarray:
    return np.array([rng.uniform(*BOUNDS[k]) for k in PARAM_NAMES])


def auc_wake_vs_deep_sleep(v3, weights, n_runs, T, dt, seed) -> float:
    """AUC binário wake-vs-deep_sleep, calculado diretamente (não via
    v3.roc_and_thresholds, que itera sobre 5 tasks pré-definidas — várias
    delas indefinidas quando só temos dados de 2 dos 4 regimes, o que só
    geraria UndefinedMetricWarning sem necessidade)."""
    rows = []
    regimes = v3.default_regimes()
    for r_idx, name in enumerate(["wake", "deep_sleep"]):
        reg = regimes[name]
        for run_id in range(n_runs):
            sistema = v3.ConsciousnessSystemV3(regime=reg, dt=dt, seed=seed + r_idx * 1000 + run_id, **weights)
            df = sistema.run(T=T)
            rows.append(v3.summarize_run(df, regime=name, run_id=run_id, variant="calibracao"))
    mc = pd.DataFrame(rows)
    y = (mc["regime"] == "wake").astype(int).values
    scores = mc["C_idx_mean"].values
    return float(roc_auc_score(y, scores))


def random_search(v3, n_samples, n_runs, T, dt, seed) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_samples):
        vec = _sample_uniform(rng)
        weights = _params_to_kwargs(vec)
        auc = auc_wake_vs_deep_sleep(v3, weights, n_runs, T, dt, seed + i)
        rows.append({**weights, "auc": auc})
    return pd.DataFrame(rows)


def coordinate_search_from_start(v3, start_weights, n_runs, T, dt, seed, n_sweeps=2, grid_points=5):
    """Busca de coordenadas simples e determinística: para cada parâmetro,
    testa um pequeno grid de valores mantendo os demais fixos, e mantém a
    mudança se o AUC melhorar. NÃO é uma otimização exaustiva — é uma busca
    local barata (evita depender de scipy.optimize, que pode não estar
    disponível no ambiente do autor)."""
    weights = dict(start_weights)
    best_auc = auc_wake_vs_deep_sleep(v3, weights, n_runs, T, dt, seed)
    for _ in range(n_sweeps):
        for name in PARAM_NAMES:
            lo, hi = BOUNDS[name]
            for cand in np.linspace(lo, hi, grid_points):
                trial = dict(weights)
                trial[name] = float(cand)
                auc = auc_wake_vs_deep_sleep(v3, trial, n_runs, T, dt, seed)
                if auc > best_auc:
                    best_auc = auc
                    weights = trial
    return weights, best_auc


def multi_start_optimization(v3, n_starts, n_runs, T, dt, seed) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 999)
    rows = []
    for start in range(n_starts):
        vec = _sample_uniform(rng)
        start_weights = _params_to_kwargs(vec)
        final_weights, best_auc = coordinate_search_from_start(
            v3, start_weights, n_runs, T, dt, seed=seed + start * 31
        )
        rows.append({**final_weights, "auc": best_auc, "start_id": start})
    return pd.DataFrame(rows)


def identifiability_report(random_df: pd.DataFrame, optim_df: pd.DataFrame) -> dict:
    frac_95 = float((random_df["auc"] >= 0.95).mean())
    frac_90 = float((random_df["auc"] >= 0.90).mean())
    frac_below_70 = float((random_df["auc"] < 0.70).mean())

    # espalhamento dos parâmetros entre as amostras aleatórias de MELHOR AUC
    # (top 10%): se o espalhamento for grande, muitas combinações diferentes
    # atingem AUC alto -> nao-identificavel / sustenta tautologia.
    top10 = random_df.sort_values("auc", ascending=False).head(max(1, len(random_df) // 10))
    spread_top10 = {p: float(top10[p].std()) for p in PARAM_NAMES}
    spread_full = {p: float(random_df[p].std()) for p in PARAM_NAMES}
    spread_ratio = {
        p: (spread_top10[p] / spread_full[p]) if spread_full[p] > 1e-9 else float("nan")
        for p in PARAM_NAMES
    }

    # dispersao entre os pontos de OTIMIZACAO final (multi-start): distancia
    # euclidiana media entre os vetores de parametros finais, normalizada
    # pela diagonal do espaco de busca.
    optim_vecs = optim_df[PARAM_NAMES].values
    diag = np.sqrt(sum((hi - lo) ** 2 for lo, hi in BOUNDS.values()))
    if len(optim_vecs) >= 2:
        dists = []
        for i in range(len(optim_vecs)):
            for j in range(i + 1, len(optim_vecs)):
                dists.append(np.linalg.norm(optim_vecs[i] - optim_vecs[j]))
        mean_dist_norm = float(np.mean(dists) / diag) if diag > 0 else float("nan")
    else:
        mean_dist_norm = float("nan")

    correls = {
        p: float(random_df[[p, "auc"]].corr(method="spearman").iloc[0, 1])
        for p in PARAM_NAMES
    }

    return {
        "fracao_amostras_auc_maior_igual_0_95": frac_95,
        "fracao_amostras_auc_maior_igual_0_90": frac_90,
        "fracao_amostras_auc_menor_0_70": frac_below_70,
        "espalhamento_relativo_top10pct_por_param": spread_ratio,
        "correlacao_spearman_param_x_auc": correls,
        "distancia_media_normalizada_entre_otimos_multistart": mean_dist_norm,
        "auc_medio_otimizacao_multistart": float(optim_df["auc"].mean()),
        "auc_minimo_otimizacao_multistart": float(optim_df["auc"].min()),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model-dir", default=str(DEFAULT_MODEL_DIR))
    ap.add_argument("--n-samples", type=int, default=200, help="Amostras aleatórias de pesos para a busca ampla")
    ap.add_argument("--n-starts", type=int, default=5, help="Pontos de partida para a busca de coordenadas (multi-start)")
    ap.add_argument("--n-runs", type=int, default=4, help="Runs por regime, por avaliação de AUC (Monte Carlo interno do V3)")
    ap.add_argument("--T", type=float, default=15.0)
    ap.add_argument("--dt", type=float, default=0.10)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--outdir", default=str(SCRIPT_DIR))
    args = ap.parse_args()

    v3 = _import_v3(args.model_dir)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"=== Busca aleatória ampla ({args.n_samples} amostras de pesos, limites 0 a 2x baseline) ===")
    random_df = random_search(v3, args.n_samples, args.n_runs, args.T, args.dt, args.seed)
    random_df.to_csv(outdir / "calibracao_busca_aleatoria.csv", index=False)
    print(random_df["auc"].describe())

    print(f"\n=== Otimização multi-start ({args.n_starts} pontos de partida, busca de coordenadas) ===")
    optim_df = multi_start_optimization(v3, args.n_starts, args.n_runs, args.T, args.dt, args.seed)
    optim_df.to_csv(outdir / "calibracao_otimizacao_multistart.csv", index=False)
    print(optim_df[PARAM_NAMES + ["auc"]].to_string(index=False))

    report = identifiability_report(random_df, optim_df)

    plt.figure(figsize=(7, 4.5))
    plt.hist(random_df["auc"], bins=25)
    plt.axvline(EMPIRICAL_AUC_TARGET, color="red", linestyle="--", label=f"AUC empírico real (LZc, W-vs-N3) = {EMPIRICAL_AUC_TARGET:.3f}")
    plt.xlabel("AUC (C_idx, wake vs deep_sleep) sob pesos sorteados aleatoriamente")
    plt.ylabel("contagem de amostras")
    plt.title("V3 — distribuição de AUC sob busca aleatória ampla de pesos")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(outdir / "calibracao_histograma_auc.png", dpi=160)
    plt.close()

    fig, axes = plt.subplots(2, 4, figsize=(18, 8))
    for ax, param in zip(axes.flat, PARAM_NAMES):
        ax.scatter(random_df[param], random_df["auc"], s=10, alpha=0.5)
        ax.set_title(f"{param} (rho={report['correlacao_spearman_param_x_auc'][param]:.2f})")
        ax.set_xlabel(param)
    axes[0, 0].set_ylabel("AUC")
    axes[1, 0].set_ylabel("AUC")
    fig.suptitle("V3 — AUC vs. cada peso individualmente (busca aleatória, identificabilidade visual)")
    fig.tight_layout()
    fig.savefig(outdir / "calibracao_identificabilidade.png", dpi=160)
    plt.close(fig)

    leitura = f"""
## Leitura (preencher/revisar após rodar — não inventar conclusão aqui)
- Fração de amostras aleatórias (limites amplos, 0 a 2x cada peso) com
  AUC>=0,95: {report['fracao_amostras_auc_maior_igual_0_95']:.1%}.
  AUC>=0,90: {report['fracao_amostras_auc_maior_igual_0_90']:.1%}.
  AUC<0,70: {report['fracao_amostras_auc_menor_0_70']:.1%}.
  - Se a fração com AUC alto for GRANDE (>50-70%), isso sustenta a leitura
    de que a separação wake/deep_sleep é quase garantida "por construção" —
    reproduzir o AUC real (0,992) não é uma restrição forte sobre o modelo.
  - Se a fração for PEQUENA, isso é evidência de uma restrição mais real.
- Distância média normalizada entre os ótimos finais da otimização
  multi-start: {report['distancia_media_normalizada_entre_otimos_multistart']:.3f}
  (0 = todos os pontos de partida convergem para o MESMO lugar; próximo de 1
  = convergem para lugares muito diferentes do espaço de busca).
  - Valor alto = não-identificabilidade: várias combinações de pesos bem
    diferentes dão o mesmo resultado, o que enfraquece a leitura de "ajuste
    genuíno único".
- Correlação de Spearman entre cada peso e o AUC (busca aleatória) indica
  quais pesos, se algum, realmente controlam a separação — pesos com
  |rho| baixo são pouco identificáveis a partir deste teste (o AUC não
  reage a eles).
- Se as correlações e o espalhamento relativo vierem todos como "nan", é
  porque o AUC saturou em um único valor (ex.: 1,0) em TODAS as amostras —
  ou seja, nem variou o suficiente para calcular uma correlação. Isso não é
  um erro do script: é, em si, o resultado mais extremo possível a favor da
  leitura "por construção" (qualquer combinação de pesos testada já satura
  a separação).
- Nenhuma dessas leituras substitui um teste estatístico formal — são
  descritivas, para orientar o agente que interpretar os números depois.
"""
    (outdir / "resumo_calibracao.md").write_text(
        "# Frente E — Calibração/identificabilidade do modelo V3 (resumo, a interpretar por um agente depois)\n\n"
        f"Rodado com n_samples={args.n_samples}, n_starts={args.n_starts}, n_runs={args.n_runs}, "
        f"T={args.T}, dt={args.dt}, seed={args.seed}.\n\n"
        f"Alvo empírico (referência, não um alvo de otimização direta — a otimização maximiza AUC, "
        f"não distância até este número): AUC real W-vs-N3 (LZc, Sleep-EDF n=36) = {EMPIRICAL_AUC_TARGET:.4f}.\n\n"
        "## Relatório de identificabilidade\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in report.items())
        + "\n"
        + leitura,
        encoding="utf-8",
    )

    print(f"\nProcessamento concluído. Saídas em: {outdir}")


if __name__ == "__main__":
    main()
