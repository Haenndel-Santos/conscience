"""Varre TODOS os desenhos do registro de falsificabilidade e responde, para cada um:
o teste antigo era valido ali? e o que o teste calibrado diz do resultado?

Motivacao: a calibracao de 2026-08-13 mostrou que o `cluster_bootstrap_auc` usado no
projeto -- AUC agrupada sobre todas as epocas, comparada contra 0,5 -- tem erro tipo I de
100% no desenho do sono (epocas W:N3 = 2,25:1) e 5,5% no da anestesia (1,01:1). A causa e
agregacao tipo Simpson: sujeitos diferem no nivel geral da metrica e contribuem numeros
desiguais de epocas por condicao, entao a AUC do pool nao e 0,5 sob o nulo. O
DESEQUILIBRIO DE EPOCAS e o preditor. Falta checar os demais desenhos -- em especial o do
REM, cujas quatro comparacoes tem razoes entre 1,45:1 e 2,72:1.

Para cada desenho, reporta:
  - contagem de epocas e razao
  - AUC agrupada sob o nulo (permutacao de rotulos dentro do sujeito) -- o diagnostico
  - erro tipo I empirico do teste ANTIGO e do teste NOVO
  - o resultado REAL sob os dois testes

Uso:
    python varredura_desenhos.py [--n-cal 200] [--n-boot 500]

Saidas (nesta pasta): `varredura_desenhos.csv` e `.md`
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression

HERE = Path(__file__).parent
BASE = HERE.parent
REM = BASE / "rem_desacoplamento" / "rem_desacoplamento_por_epoca.csv"
SONO = BASE / "integracao_diferenciada" / "integracao_diferenciada_por_epoca.csv"
MULTI = BASE / "complexidade_multivariada" / "lzc_multivariado_por_epoca.csv"
ANEST = BASE / "anestesia_1f" / "propofol_1f_por_epoca.csv"


def fast_auc(y, scores):
    n_pos = int(y.sum())
    n_neg = y.size - n_pos
    if n_pos == 0 or n_neg == 0:
        return None
    r = stats.rankdata(scores)
    return float((r[y == 1].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - m), min(1.0, c + m)


def fatiar(df, subject_col, state_col, score_col, neg, pos, min_ep=3):
    sub = df[df[state_col].isin([neg, pos])].dropna(subset=[score_col])
    scores, n_neg = [], []
    for _, g in sub.groupby(subject_col):
        a = g[g[state_col] == neg][score_col].values
        b = g[g[state_col] == pos][score_col].values
        if a.size < min_ep or b.size < min_ep:
            continue
        scores.append(np.concatenate([a, b]))
        n_neg.append(a.size)
    return scores, n_neg


def montar(scores, n_neg):
    negs = [s[:k] for s, k in zip(scores, n_neg)]
    poss = [s[k:] for s, k in zip(scores, n_neg)]
    return negs, poss


def p_antigo(negs, poss, n_boot, rng):
    n = len(negs)
    ss = [np.concatenate([negs[j], poss[j]]) for j in range(n)]
    yy = [np.concatenate([np.zeros(negs[j].size, np.int8), np.ones(poss[j].size, np.int8)])
          for j in range(n)]
    boots = []
    for _ in range(n_boot):
        pick = rng.integers(0, n, size=n)
        a = fast_auc(np.concatenate([yy[j] for j in pick]), np.concatenate([ss[j] for j in pick]))
        if a is not None:
            boots.append(a)
    if len(boots) < 50:
        return None, None
    b = np.asarray(boots)
    p = float(min(1.0, 2 * min(float(np.mean(b <= 0.5)), float(np.mean(b >= 0.5)))))
    return p, float(np.mean(b))


def p_novo(negs, poss):
    aucs = []
    for ng, ps in zip(negs, poss):
        y = np.concatenate([np.zeros(ng.size, np.int8), np.ones(ps.size, np.int8)])
        a = fast_auc(y, np.concatenate([ng, ps]))
        if a is not None:
            aucs.append(a)
    aucs = np.asarray(aucs)
    if aucs.size < 5:
        return None, None
    d = aucs - 0.5
    if np.allclose(d, 0):
        return 1.0, 0.5
    p = float(stats.wilcoxon(d, alternative="two-sided", zero_method="wilcox").pvalue)
    return p, float(aucs.mean())


def avaliar(df, subject_col, state_col, score_col, neg, pos, rotulo, n_cal, n_boot, rng):
    scores, n_neg = fatiar(df, subject_col, state_col, score_col, neg, pos)
    if len(scores) < 5:
        print(f"  {rotulo}: sujeitos insuficientes, pulado", flush=True)
        return None
    n = len(scores)
    tot_neg = sum(n_neg)
    tot_pos = sum(s.size - k for s, k in zip(scores, n_neg))
    razao = max(tot_neg, tot_pos) / max(1, min(tot_neg, tot_pos))

    # resultado REAL
    negs, poss = montar(scores, n_neg)
    pa_real, auc_pool_real = p_antigo(negs, poss, max(n_boot, 1000), rng)
    pn_real, auc_suj_real = p_novo(negs, poss)

    # calibracao sob permutacao
    sig_a = sig_n = 0
    aucs_nulo = []
    t0 = time.time()
    for _ in range(n_cal):
        ng, ps = [], []
        for s, k in zip(scores, n_neg):
            p = rng.permutation(s.size)
            ng.append(s[p[:k]]); ps.append(s[p[k:]])
        y = np.concatenate([np.concatenate([np.zeros(ng[j].size, np.int8),
                                            np.ones(ps[j].size, np.int8)]) for j in range(n)])
        sc = np.concatenate([np.concatenate([ng[j], ps[j]]) for j in range(n)])
        a = fast_auc(y, sc)
        if a is not None:
            aucs_nulo.append(a)
        pa, _ = p_antigo(ng, ps, n_boot, rng)
        if pa is not None and pa < 0.05:
            sig_a += 1
        pn, _ = p_novo(ng, ps)
        if pn is not None and pn < 0.05:
            sig_n += 1

    ta, tn = sig_a / n_cal, sig_n / n_cal
    la, ha = wilson(sig_a, n_cal)
    ln, hn = wilson(sig_n, n_cal)
    veredito = "VALIDO" if ha <= 0.12 else ("SUSPEITO" if la <= 0.12 else "INVALIDO")
    print(f"  {rotulo}: n={n} | epocas {tot_neg}:{tot_pos} (razao {razao:.2f}) | "
          f"AUC agrup. sob nulo {np.mean(aucs_nulo):.4f}", flush=True)
    print(f"      teste ANTIGO -> erro tipo I {ta:.1%} [{la:.1%}-{ha:.1%}]  ** {veredito} **"
          f"   | resultado real: AUC agrup. {auc_pool_real:.3f}, p={pa_real:.3f}", flush=True)
    print(f"      teste NOVO   -> erro tipo I {tn:.1%} [{ln:.1%}-{hn:.1%}]"
          f"   | resultado real: AUC/sujeito {auc_suj_real:.3f}, p={pn_real:.4f}"
          f"   ({time.time()-t0:.0f}s)", flush=True)
    return {"desenho": rotulo, "n_sujeitos": n, "epocas_neg": tot_neg, "epocas_pos": tot_pos,
            "razao_epocas": razao, "auc_agrupada_sob_nulo": float(np.mean(aucs_nulo)),
            "erro_tipo1_antigo": ta, "antigo_ic_low": la, "antigo_ic_high": ha,
            "veredito_teste_antigo": veredito,
            "erro_tipo1_novo": tn, "novo_ic_low": ln, "novo_ic_high": hn,
            "resultado_auc_agrupada": auc_pool_real, "resultado_p_antigo": pa_real,
            "resultado_auc_por_sujeito": auc_suj_real, "resultado_p_novo": pn_real}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-cal", type=int, default=200)
    ap.add_argument("--n-boot", type=int, default=500)
    args = ap.parse_args()
    rng = np.random.default_rng(20260813)
    linhas = []

    print("=== REM (rem_desacoplamento) ===", flush=True)
    if REM.exists():
        rem = pd.read_csv(REM)
        # indice_desacoplamento: rank percentil dentro do sujeito, sobre a noite toda
        # (reproduz rem_complexidade_vs_emg.py:243-245 -- ranks calculados ANTES do filtro)
        rem["lzc_rank"] = rem.groupby("subject")["lzc"].rank(pct=True)
        rem["emg_rank"] = rem.groupby("subject")["emg_rms"].rank(pct=True)
        rem["indice_desacoplamento"] = rem["lzc_rank"] - rem["emg_rank"]
        for metrica in ["emg_rms", "eeg_emg_coherence", "indice_desacoplamento"]:
            for outro in ["W", "N1", "N2", "N3"]:
                r = avaliar(rem, "subject", "stage", metrica, outro, "REM",
                            f"REM vs {outro} — {metrica}", args.n_cal, args.n_boot, rng)
                if r:
                    linhas.append(r)

    print("\n=== Referencias ja calibradas ===", flush=True)
    if SONO.exists():
        so = pd.read_csv(SONO)
        so = so[so["stage"].isin(["W", "N3"])].dropna(subset=["lzc", "exponent_1f"]).copy()
        X = so["exponent_1f"].values.reshape(-1, 1)
        so["_s"] = so["lzc"].values - LinearRegression().fit(X, so["lzc"].values).predict(X)
        r = avaliar(so, "subject", "stage", "_s", "N3", "W", "SONO W vs N3 — LZc resid. 1/f",
                    args.n_cal, args.n_boot, rng)
        if r:
            linhas.append(r)
    if MULTI.exists():
        mu = pd.read_csv(MULTI)
        mu = mu[mu["stage"].isin(["W", "N3"])].dropna(subset=["lzc_multivariado", "exponent_1f"]).copy()
        X = mu["exponent_1f"].values.reshape(-1, 1)
        mu["_s"] = mu["lzc_multivariado"].values - LinearRegression().fit(X, mu["lzc_multivariado"].values).predict(X)
        r = avaliar(mu, "subject", "stage", "_s", "N3", "W", "SONO W vs N3 — LZc multivar. resid. 1/f",
                    args.n_cal, args.n_boot, rng)
        if r:
            linhas.append(r)
    if ANEST.exists():
        an = pd.read_csv(ANEST)
        an = an[an["state"].isin(["basal", "sedacao_moderada"])].dropna(subset=["lzc", "exponent_1f"]).copy()
        X = an["exponent_1f"].values.reshape(-1, 1)
        an["_s"] = an["lzc"].values - LinearRegression().fit(X, an["lzc"].values).predict(X)
        r = avaliar(an, "subject", "state", "_s", "basal", "sedacao_moderada",
                    "ANESTESIA basal vs moderada — LZc resid. 1/f", args.n_cal, args.n_boot, rng)
        if r:
            linhas.append(r)

    res = pd.DataFrame(linhas)
    res.to_csv(HERE / "varredura_desenhos.csv", index=False)

    invalidos = res[res["veredito_teste_antigo"] == "INVALIDO"]
    corr = res[["razao_epocas", "erro_tipo1_antigo"]].corr(method="spearman").iloc[0, 1]

    md = f"""# Varredura: o teste antigo era válido em cada desenho?

Gerado por `varredura_desenhos.py` em {time.strftime('%Y-%m-%d %H:%M')}.
`--n-cal {args.n_cal} --n-boot {args.n_boot}`, α nominal = 0,05.
Nulo imposto por **permutação de rótulos de estado dentro de cada sujeito**.

Veredito sobre o teste antigo: `VALIDO` se o topo do IC95 do erro tipo I ficar em ≤12%;
`INVALIDO` se nem o piso do IC chegar lá; `SUSPEITO` no meio.

## Resultado

{res.to_string(index=False)}

## Correlação entre desequilíbrio de épocas e inflação

Spearman(razão de épocas, erro tipo I do teste antigo) = **{corr:+.3f}**

## Desenhos em que o teste antigo é inválido

{invalidos[['desenho','razao_epocas','auc_agrupada_sob_nulo','erro_tipo1_antigo','resultado_p_antigo','resultado_auc_por_sujeito','resultado_p_novo']].to_string(index=False) if not invalidos.empty else 'Nenhum.'}

## Como ler
- `auc_agrupada_sob_nulo` é o diagnóstico direto: quanto mais longe de 0,5, mais o
  desequilíbrio de épocas está inflando a AUC do pool, e mais o teste antigo rejeita à toa.
- `resultado_p_antigo` só é interpretável nas linhas com veredito `VALIDO`.
- `resultado_p_novo` (AUC por sujeito + Wilcoxon) é interpretável em todas.
"""
    (HERE / "varredura_desenhos.md").write_text(md, encoding="utf-8")
    print(f"\nSaidas em: {HERE}", flush=True)


if __name__ == "__main__":
    main()
