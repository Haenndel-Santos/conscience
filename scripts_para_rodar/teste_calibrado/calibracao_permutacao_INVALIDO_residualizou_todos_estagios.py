"""Calibracao correta dos dois testes, por PERMUTACAO DE ROTULOS dentro de cada sujeito.

CORRIGE UM ERRO DA PRIMEIRA CALIBRACAO (2026-08-13, `calibracao_teste_anestesia.py`).
Aquela impunha o nulo recentrando as MEDIAS dos dois estados de cada sujeito. Isso esta
errado para um teste baseado em AUC: a AUC nao e funcao da media, e sim de dominancia
estocastica. Duas distribuicoes assimetricas com a mesma media podem ter AUC bem
diferente de 0,5 -- ou seja, aquele procedimento injetava um efeito real e o chamava de
nulo. Os numeros que ele produziu (61% no sono, 14% na anestesia) nao sao taxas de erro
tipo I validas e nao devem ser citados.

NULO CORRETO: permutar os rotulos de estado entre as epocas DE CADA SUJEITO, preservando
as contagens por estado. Isso destroi qualquer efeito de estado mantendo intacta a
distribuicao marginal de cada sujeito -- e a AUC passa a ter esperanca exatamente 0,5,
que e a hipotese que os dois testes afirmam estar avaliando.

Compara, sob esse mesmo nulo:
  (a) TESTE ANTIGO -- AUC agrupada sobre todas as epocas + bootstrap de sujeitos vs 0,5
  (b) TESTE NOVO   -- AUC dentro de cada sujeito + Wilcoxon dos postos sinalizados vs 0,5

Uso:
    python calibracao_permutacao.py [--n-cal 500] [--n-boot 1000]

Saidas (nesta pasta): `calibracao_permutacao.csv` e `.md`
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
SONO = BASE / "integracao_diferenciada" / "integracao_diferenciada_por_epoca.csv"
ANESTESIA = BASE / "anestesia_1f" / "propofol_1f_por_epoca.csv"


def fast_auc(y: np.ndarray, scores: np.ndarray) -> float | None:
    n_pos = int(y.sum())
    n_neg = y.size - n_pos
    if n_pos == 0 or n_neg == 0:
        return None
    ranks = stats.rankdata(scores)
    return float((ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - m), min(1.0, c + m)


def preparar_sujeitos(df, subject_col, state_col, score_col, estado_neg, estado_pos, min_ep=3):
    """Devolve, por sujeito, o vetor de scores e quantas epocas cabem a cada estado."""
    sub = df[df[state_col].isin([estado_neg, estado_pos])].dropna(subset=[score_col])
    scores, n_neg = [], []
    for _, g in sub.groupby(subject_col):
        a = g[g[state_col] == estado_neg][score_col].values
        b = g[g[state_col] == estado_pos][score_col].values
        if a.size < min_ep or b.size < min_ep:
            continue
        scores.append(np.concatenate([a, b]))
        n_neg.append(a.size)
    return scores, n_neg


def permutar(scores, n_neg, rng):
    """Permuta rotulos DENTRO de cada sujeito, preservando as contagens por estado."""
    negs, poss = [], []
    for s, k in zip(scores, n_neg):
        p = rng.permutation(s.size)
        negs.append(s[p[:k]])
        poss.append(s[p[k:]])
    return negs, poss


def p_teste_antigo(negs, poss, n_boot, rng):
    """AUC agrupada + bootstrap de sujeitos contra 0,5 (o teste em uso no projeto)."""
    n = len(negs)
    subj_scores = [np.concatenate([negs[j], poss[j]]) for j in range(n)]
    subj_y = [np.concatenate([np.zeros(negs[j].size, np.int8), np.ones(poss[j].size, np.int8)])
              for j in range(n)]
    boots = []
    for _ in range(n_boot):
        pick = rng.integers(0, n, size=n)
        a = fast_auc(np.concatenate([subj_y[j] for j in pick]),
                     np.concatenate([subj_scores[j] for j in pick]))
        if a is not None:
            boots.append(a)
    if len(boots) < 50:
        return None
    b = np.asarray(boots)
    return float(min(1.0, 2 * min(float(np.mean(b <= 0.5)), float(np.mean(b >= 0.5)))))


def p_teste_novo(negs, poss):
    """AUC por sujeito + Wilcoxon contra 0,5."""
    aucs = []
    for ng, ps in zip(negs, poss):
        y = np.concatenate([np.zeros(ng.size, np.int8), np.ones(ps.size, np.int8)])
        a = fast_auc(y, np.concatenate([ng, ps]))
        if a is not None:
            aucs.append(a)
    aucs = np.asarray(aucs)
    if aucs.size < 5:
        return None
    d = aucs - 0.5
    if np.allclose(d, 0):
        return 1.0
    return float(stats.wilcoxon(d, alternative="two-sided", zero_method="wilcox").pvalue)


def calibrar(df, subject_col, state_col, metric, cov, estado_neg, estado_pos,
             n_cal, n_boot, rng, rotulo):
    d = df.dropna(subset=[metric, cov]).copy()
    X = d[cov].values.reshape(-1, 1)
    d["_score"] = d[metric].values - LinearRegression().fit(X, d[metric].values).predict(X)
    scores, n_neg = preparar_sujeitos(d, subject_col, state_col, "_score", estado_neg, estado_pos)
    n = len(scores)

    sig_antigo = sig_novo = 0
    aucs_pooled = []
    t0 = time.time()
    for _ in range(n_cal):
        negs, poss = permutar(scores, n_neg, rng)
        y = np.concatenate([np.concatenate([np.zeros(negs[j].size, np.int8),
                                            np.ones(poss[j].size, np.int8)]) for j in range(n)])
        sc = np.concatenate([np.concatenate([negs[j], poss[j]]) for j in range(n)])
        a = fast_auc(y, sc)
        if a is not None:
            aucs_pooled.append(a)
        pa = p_teste_antigo(negs, poss, n_boot, rng)
        if pa is not None and pa < 0.05:
            sig_antigo += 1
        pn = p_teste_novo(negs, poss)
        if pn is not None and pn < 0.05:
            sig_novo += 1

    ta, tn = sig_antigo / n_cal, sig_novo / n_cal
    la, ha = wilson(sig_antigo, n_cal)
    ln, hn = wilson(sig_novo, n_cal)
    print(f"  {rotulo}: n={n} sujeitos | AUC agrupada sob o nulo = {np.mean(aucs_pooled):.4f}", flush=True)
    print(f"      ANTIGO (AUC agrupada + bootstrap): erro tipo I = {ta:.1%} [{la:.1%}-{ha:.1%}]", flush=True)
    print(f"      NOVO   (AUC por sujeito + Wilcoxon): erro tipo I = {tn:.1%} [{ln:.1%}-{hn:.1%}]"
          f"   ({time.time()-t0:.0f}s)", flush=True)
    return {"desenho": rotulo, "n_sujeitos": n,
            "auc_agrupada_sob_nulo": float(np.mean(aucs_pooled)),
            "erro_tipo1_antigo": ta, "antigo_ic_low": la, "antigo_ic_high": ha,
            "erro_tipo1_novo": tn, "novo_ic_low": ln, "novo_ic_high": hn,
            "n_cal": n_cal, "n_boot": n_boot}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-cal", type=int, default=500)
    ap.add_argument("--n-boot", type=int, default=1000)
    args = ap.parse_args()
    rng = np.random.default_rng(20260813)

    print("=== Calibracao por permutacao de rotulos dentro do sujeito (alfa nominal 0,05) ===",
          flush=True)
    linhas = []
    if ANESTESIA.exists():
        linhas.append(calibrar(pd.read_csv(ANESTESIA), "subject", "state", "lzc", "exponent_1f",
                               "basal", "sedacao_moderada", args.n_cal, args.n_boot, rng,
                               "ANESTESIA (basal vs moderada, LZc resid. 1/f)"))
    if SONO.exists():
        linhas.append(calibrar(pd.read_csv(SONO), "subject", "stage", "lzc", "exponent_1f",
                               "N3", "W", args.n_cal, args.n_boot, rng,
                               "SONO (N3 vs W, LZc resid. 1/f)"))

    res = pd.DataFrame(linhas)
    res.to_csv(HERE / "calibracao_permutacao.csv", index=False)

    md = f"""# Calibracao por permutacao — erro tipo I dos dois testes

Gerado por `calibracao_permutacao.py` em {time.strftime('%Y-%m-%d %H:%M')}.
`--n-cal {args.n_cal} --n-boot {args.n_boot}`, alfa nominal = 0,05.

## Metodo

O nulo e imposto **permutando os rotulos de estado entre as epocas de cada sujeito**,
preservando as contagens por estado. Isso destroi qualquer efeito de estado mantendo a
distribuicao marginal de cada sujeito intacta, e faz a AUC ter esperanca exatamente 0,5 —
que e a hipotese que os dois testes afirmam avaliar.

> **Corrige a calibracao anterior.** `calibracao_teste_anestesia.py` impunha o nulo
> recentrando as *medias* dos dois estados. AUC nao e funcao da media, e sim de dominancia
> estocastica: com distribuicoes assimetricas, medias iguais nao implicam AUC=0,5. Aquele
> procedimento injetava efeito real e o chamava de nulo. Os numeros dele (61% e 14%) nao
> sao taxas de erro tipo I validas.

## Resultado

{res.to_string(index=False)}

## Como ler
- Um teste calibrado rejeita ~5% das vezes sob este nulo. Acima disso e anticonservador
  (rejeita demais, produz falsos positivos); bem abaixo e conservador (perde poder).
- `auc_agrupada_sob_nulo` diagnostica a agregacao tipo Simpson: se ficar acima de 0,5 mesmo
  com os rotulos permutados dentro de cada sujeito, o desequilibrio de epocas entre estados
  esta inflando a AUC do pool, e qualquer teste que compare essa AUC contra 0,5 herda o viés.
- A comparacao entre as duas linhas de erro tipo I e o que decide qual teste usar.
"""
    (HERE / "calibracao_permutacao.md").write_text(md, encoding="utf-8")
    print(f"\nSaidas em: {HERE}", flush=True)


if __name__ == "__main__":
    main()
