"""Calibracao do teste de bootstrap por sujeito NO DESENHO DA ANESTESIA (propofol).

Por que este script existe: a analise de poder corrigida do sono
(`poder_estatistico_sono.py`, 2026-08-12) descobriu que o teste usado em todo o projeto
-- bootstrap por sujeito sobre a AUC agrupada por epoca, contra 0,5 -- rejeita ~28% das
vezes sob o nulo de sujeito, quando o nominal e 5%. Ou seja, e ANTICONSERVADOR, nao
conservador.

O motivo e estrutural: sob o nulo de sujeito (toda diferenca pareada = 0), a AUC
agrupada por epoca NAO e 0,5. Sujeitos diferem no nivel geral da metrica e contribuem
numeros desiguais de epocas em cada condicao, entao o pool acusa separacao mesmo sem
nenhum efeito intra-sujeito -- agregacao tipo Simpson. O teste compara essa AUC
agrupada contra 0,5, logo rejeita demais.

Isso importa diretamente para o resultado de anestesia de 2026-08-13
(`scripts_para_rodar/anestesia_1f/auc_comparativo_1f.csv`): LZc residualizada por 1/f
discrimina basal-vs-sedacao-moderada com AUC=0,829 e q=0,000. Esse q vem do MESMO teste.
Antes de trata-lo como significativo, e preciso saber qual e a taxa de erro tipo I do
teste NESTE desenho -- que e bem mais balanceado que o do sono (no sono, 8.923 epocas de
vigilia contra 3.972 de N3; aqui, ~755 contra ~751), e por isso pode ter inflacao bem
menor.

Metodo: impoe o nulo aos dados REAIS de propofol -- para cada sujeito, recentra as
epocas de basal e de sedacao moderada num mesmo nivel, zerando a diferenca pareada de
todo mundo, sem tocar na variancia intra-sujeito nem na heterogeneidade entre sujeitos.
Depois reamostra sujeitos com reposicao e roda o mesmo teste. A fracao de rejeicoes e a
taxa de erro tipo I empirica.

Uso:
    python calibracao_teste_anestesia.py [--n-boot 1000] [--n-sim 500]

Saida: `calibracao_erro_tipo1.md` nesta pasta.
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
ANESTESIA = HERE.parent / "anestesia_1f" / "propofol_1f_por_epoca.csv"
SONO = HERE.parent / "integracao_diferenciada" / "integracao_diferenciada_por_epoca.csv"


def fast_auc(y: np.ndarray, scores: np.ndarray) -> float | None:
    n_pos = int(y.sum())
    n_neg = y.size - n_pos
    if n_pos == 0 or n_neg == 0:
        return None
    ranks = stats.rankdata(scores)
    return float((ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def cluster_bootstrap_p(subj_scores, subj_y, n_boot, rng):
    n_subj = len(subj_scores)
    if n_subj < 4:
        return None
    boots = []
    for _ in range(n_boot):
        pick = rng.integers(0, n_subj, size=n_subj)
        auc = fast_auc(np.concatenate([subj_y[j] for j in pick]),
                       np.concatenate([subj_scores[j] for j in pick]))
        if auc is not None:
            boots.append(auc)
    if len(boots) < 50:
        return None
    boots = np.asarray(boots)
    return float(min(1.0, 2 * min(float(np.mean(boots <= 0.5)), float(np.mean(boots >= 0.5)))))


def wilson_ci(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    meio = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centro - meio), min(1.0, centro + meio))


def calibrar(df, subject_col, state_col, estado_a, estado_b, metric_col, cov_col,
             n_boot, n_sim, rng, rotulo):
    """Impoe o nulo de sujeito e mede a taxa de rejeicao."""
    sub = df[df[state_col].isin([estado_a, estado_b])].dropna(subset=[metric_col, cov_col]).copy()
    X = sub[cov_col].values.reshape(-1, 1)
    sub["resid"] = sub[metric_col].values - LinearRegression().fit(X, sub[metric_col].values).predict(X)

    subjects = [s for s in sub[subject_col].unique()
                if sub[(sub[subject_col] == s) & (sub[state_col] == estado_a)].shape[0] > 0
                and sub[(sub[subject_col] == s) & (sub[state_col] == estado_b)].shape[0] > 0]

    # impoe o nulo: recentra os dois estados de cada sujeito no mesmo nivel
    a_null, b_null = [], []
    n_a, n_b = [], []
    for s in subjects:
        a = sub[(sub[subject_col] == s) & (sub[state_col] == estado_a)]["resid"].values
        b = sub[(sub[subject_col] == s) & (sub[state_col] == estado_b)]["resid"].values
        centro = np.concatenate([a, b]).mean()
        a_null.append(a - a.mean() + centro)
        b_null.append(b - b.mean() + centro)
        n_a.append(a.size); n_b.append(b.size)

    n = len(subjects)
    sig = 0
    aucs = []
    t0 = time.time()
    for _ in range(n_sim):
        pick = rng.integers(0, n, size=n)
        subj_scores = [np.concatenate([a_null[j], b_null[j]]) for j in pick]
        subj_y = [np.concatenate([np.zeros(a_null[j].size, dtype=np.int8),
                                  np.ones(b_null[j].size, dtype=np.int8)]) for j in pick]
        auc = fast_auc(np.concatenate(subj_y), np.concatenate(subj_scores))
        if auc is not None:
            aucs.append(auc)
        p = cluster_bootstrap_p(subj_scores, subj_y, n_boot, rng)
        if p is not None and p < 0.05:
            sig += 1
    lo, hi = wilson_ci(sig, n_sim)
    dur = time.time() - t0
    print(f"{rotulo}: n={n} sujeitos | epocas {estado_a}={sum(n_a)} vs {estado_b}={sum(n_b)} "
          f"(razao {sum(n_a)/max(1,sum(n_b)):.2f}) | AUC sob o nulo = {np.mean(aucs):.4f} "
          f"| ERRO TIPO I = {sig/n_sim:.1%} [IC95 {lo:.1%}-{hi:.1%}]  ({dur:.0f}s)", flush=True)
    return {"desenho": rotulo, "n_sujeitos": n, "n_epocas_a": sum(n_a), "n_epocas_b": sum(n_b),
            "razao_epocas": sum(n_a) / max(1, sum(n_b)), "auc_media_sob_nulo": float(np.mean(aucs)),
            "erro_tipo1": sig / n_sim, "ic95_low": lo, "ic95_high": hi, "n_sim": n_sim, "n_boot": n_boot}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--n-sim", type=int, default=500)
    args = ap.parse_args()
    rng = np.random.default_rng(20260813)

    linhas = []
    print("=== Calibracao do teste sob o nulo de sujeito ===", flush=True)

    if ANESTESIA.exists():
        an = pd.read_csv(ANESTESIA)
        linhas.append(calibrar(an, "subject", "state", "basal", "sedacao_moderada",
                               "lzc", "exponent_1f", args.n_boot, args.n_sim, rng,
                               "ANESTESIA (propofol, basal vs moderada, LZc resid. 1/f)"))
    else:
        print(f"[aviso] {ANESTESIA} nao encontrado — pulando anestesia", flush=True)

    if SONO.exists():
        so = pd.read_csv(SONO)
        linhas.append(calibrar(so, "subject", "stage", "N3", "W",
                               "lzc", "exponent_1f", args.n_boot, args.n_sim, rng,
                               "SONO (Sleep-EDF, N3 vs W, LZc resid. 1/f)"))

    res = pd.DataFrame(linhas)
    md = f"""# Calibracao do teste de bootstrap por sujeito (erro tipo I empirico)

Gerado por `calibracao_teste_anestesia.py` em {time.strftime('%Y-%m-%d %H:%M')}.
`--n-boot {args.n_boot} --n-sim {args.n_sim}`, alfa nominal = 0,05.

O nulo e imposto aos dados REAIS: para cada sujeito, os dois estados sao recentrados num
mesmo nivel, zerando toda diferenca pareada. Variancia intra-sujeito e heterogeneidade
entre sujeitos ficam intactas. Sujeitos sao reamostrados com reposicao a cada replica.
Sob um teste calibrado, a fracao de rejeicoes deveria ficar em ~5%.

{res.to_string(index=False)}

## Como ler
- **erro_tipo1 >> 0,05** significa que o teste rejeita demais: os p-valores e q-valores
  produzidos por ele NAO estao calibrados, e resultados "significativos" obtidos com ele
  precisam ser reavaliados.
- **auc_media_sob_nulo** e o diagnostico da causa: se estiver bem acima de 0,5 mesmo com
  toda diferenca pareada zerada, a inflacao vem da agregacao por epoca (sujeitos com
  niveis diferentes e contagens desiguais de epocas em cada condicao), nao do bootstrap.
- **razao_epocas** proxima de 1 indica desenho balanceado, que tende a sofrer menos.
- Um resultado NEGATIVO obtido com um teste anticonservador fica MAIS forte, nao mais
  fraco: o teste rejeita facil e ainda assim nao rejeitou.
"""
    (HERE / "calibracao_erro_tipo1.md").write_text(md, encoding="utf-8")
    res.to_csv(HERE / "calibracao_erro_tipo1.csv", index=False)
    print("\nSaidas:", HERE / "calibracao_erro_tipo1.md", flush=True)


if __name__ == "__main__":
    main()
