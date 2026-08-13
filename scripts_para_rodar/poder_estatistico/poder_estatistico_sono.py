"""Analise de poder / efeito minimo detectavel (MDE) para o teste de discriminacao
W-vs-N3 residualizada por 1/f, dado n=36 sujeitos (Cap. 11, achado 1.2 do
`embasamento/registro_falsificabilidade.md`).

Por que este teste existe: "nao sobrevive a correcao FDR" pode significar duas coisas
muito diferentes -- (a) o efeito verdadeiro e proximo de zero, ou (b) o efeito existe mas
e pequeno demais para n=36 detectar. Este script calcula, a partir da estrutura de
variancia OBSERVADA nos dados reais, qual e o menor efeito verdadeiro que o desenho atual
detectaria com 80% de poder -- e onde o efeito ja observado fica em relacao a esse limiar.

--------------------------------------------------------------------------------------
HISTORICO DE CORRECOES -- leia antes de comparar com qualquer numero antigo
--------------------------------------------------------------------------------------
Esta e a TERCEIRA versao. As duas anteriores produziram numeros que nao devem ser citados:

  v1 (12/08): nao reamostrava nada. Todas as `n_sim` replicas de um mesmo dz-alvo eram
      byte-identicas -- `sim_diffs` nao dependia da variavel do laco e as epocas
      sinteticas eram recentralizacoes deterministicas. O "poder" medido era ruido do
      bootstrap interno, nao variabilidade amostral. Reportava MDE dz~0,2.
      Saidas: `*_INVALIDO_replicas_identicas.*`

  v2 (13/08): reamostragem corrigida, mas ainda media o poder do teste ANTIGO
      (`cluster_bootstrap_auc`: AUC agrupada por epoca + bootstrap de sujeitos), que a
      varredura por permutacao mostrou ser anticonservador neste desenho -- erro tipo I de
      10,5% [7,0-15,5] contra 5% nominal, porque as 8.923 epocas de W contra 3.972 de N3
      levam a AUC agrupada sob o nulo a 0,551 e o teste a compara contra 0,5. Uma curva de
      poder de um teste descalibrado nao descreve o poder de nada que se deva usar.
      Saidas: `*_teste_antigo_descalibrado.*`

  v3 (esta): mede o poder do TESTE CALIBRADO -- AUC calculada dentro de cada sujeito,
      seguida de Wilcoxon dessas AUCs contra 0,5 (ver
      `scripts_para_rodar/teste_calibrado/`). Erro tipo I empirico de 6,5% neste desenho
      pela varredura, e 7,2% pela linha dz=0 desta propria simulacao, contra 5% nominal.

O Nivel 1 (formula fechada) nunca foi afetado por nenhum dos dois bugs.

CONVENCAO IMPORTANTE: a residualizacao por 1/f e ajustada APENAS sobre as epocas de W e
N3, nao sobre os cinco estagios. E a convencao de `integracao_diferenciada_1f.py`.
Ajustar sobre todos os estagios muda o slope e produz residuos diferentes.
--------------------------------------------------------------------------------------

Metodo (dois niveis):
  1. Formula fechada de poder para teste pareado (Cohen's dz) ao nivel de sujeito --
     rapida, assume aproximacao normal, e mede um efeito de MEDIA.
  2. Monte Carlo: reamostra os 36 sujeitos com reposicao, reescala as diferencas pareadas
     reais para atingir cada dz-alvo (preservando a forma nao-normal da distribuicao) e
     roda o teste calibrado em cada replica.

Entrada: `scripts_para_rodar/integracao_diferenciada/integracao_diferenciada_por_epoca.csv`

Uso:
    python poder_estatistico_sono.py [--n-sim 2000]

Saidas (nesta pasta):
    poder_por_efeito.csv   - poder por dz-alvo, com IC de Wilson
    resumo_poder.md        - relatorio narrativo
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).parent
DATA_PATH = HERE.parent / "integracao_diferenciada" / "integracao_diferenciada_por_epoca.csv"


def fast_auc(y: np.ndarray, scores: np.ndarray) -> float | None:
    n_pos = int(y.sum())
    n_neg = y.size - n_pos
    if n_pos == 0 or n_neg == 0:
        return None
    ranks = stats.rankdata(scores)
    return float((ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def p_teste_calibrado(aucs: np.ndarray) -> float | None:
    """Wilcoxon dos postos sinalizados das AUCs por sujeito, contra 0,5."""
    if aucs.size < 5:
        return None
    d = aucs - 0.5
    if np.allclose(d, 0):
        return 1.0
    return float(stats.wilcoxon(d, alternative="two-sided", zero_method="wilcox").pvalue)


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    meio = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centro - meio), min(1.0, centro + meio))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-sim", type=int, default=2000, help="Replicas Monte Carlo por dz-alvo")
    args = ap.parse_args()
    rng = np.random.default_rng(20260813)
    alpha = 0.05

    print("=== Carregando dado real ja existente ===", flush=True)
    df = pd.read_csv(DATA_PATH)
    # convencao do projeto: filtrar o par de estados ANTES de residualizar
    wn3 = df[df["stage"].isin(["W", "N3"])].dropna(subset=["lzc", "exponent_1f"]).copy()
    X = wn3["exponent_1f"].values.reshape(-1, 1)
    wn3["resid"] = wn3["lzc"].values - LinearRegression().fit(X, wn3["lzc"].values).predict(X)

    per_subj = wn3.groupby(["subject", "stage"])["resid"].mean().unstack().dropna(subset=["W", "N3"])
    diffs = (per_subj["W"] - per_subj["N3"]).values
    n = len(diffs)
    mean_diff = float(np.mean(diffs))
    sd_diff = float(np.std(diffs, ddof=1))
    dz_obs = mean_diff / sd_diff
    print(f"n = {n} sujeitos | diferenca pareada media = {mean_diff:.5f} | DP = {sd_diff:.5f} "
          f"| Cohen's dz observado = {dz_obs:.4f}", flush=True)

    print("\n=== Nivel 1: formula fechada (teste pareado, aproximacao normal) ===", flush=True)
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    mde_fechada = {}
    for alvo in (0.80, 0.90):
        dz_min = (z_alpha + stats.norm.ppf(alvo)) / np.sqrt(n)
        mde_fechada[alvo] = dz_min
        print(f"  Poder {alvo*100:.0f}%: dz minimo detectavel = {dz_min:.4f} "
              f"({dz_min/abs(dz_obs):.2f}x o efeito observado)", flush=True)

    # --- pre-fatia por sujeito, uma unica vez ---
    subj_list = list(per_subj.index)
    n3_cent, w_cent, n3_center = [], [], []
    for s in subj_list:
        a = wn3[(wn3.subject == s) & (wn3.stage == "N3")]["resid"].values
        b = wn3[(wn3.subject == s) & (wn3.stage == "W")]["resid"].values
        n3_cent.append(a - a.mean())
        w_cent.append(b - b.mean())
        n3_center.append(float(per_subj.loc[s, "N3"]))
    n3_center = np.asarray(n3_center)
    diffs_std = (diffs - mean_diff) / sd_diff

    # AUC por sujeito OBSERVADA, para ancorar a leitura
    aucs_obs = []
    for j in range(n):
        a = n3_cent[j] + n3_center[j]
        b = w_cent[j] + n3_center[j] + diffs[j]
        y = np.concatenate([np.zeros(a.size, np.int8), np.ones(b.size, np.int8)])
        v = fast_auc(y, np.concatenate([a, b]))
        if v is not None:
            aucs_obs.append(v)
    aucs_obs = np.asarray(aucs_obs)
    print(f"\nAUC por sujeito OBSERVADA: media {aucs_obs.mean():.4f}, "
          f"{(aucs_obs > 0.5).mean():.0%} acima de 0,5, p={p_teste_calibrado(aucs_obs):.4f}", flush=True)

    print("\n=== Nivel 2: Monte Carlo com o TESTE CALIBRADO ===", flush=True)
    dz_targets = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.80, 1.00]
    results = []
    t0 = time.time()
    for dz in dz_targets:
        alvo = dz * sd_diff
        sig = 0
        aucs_med = []
        for _ in range(args.n_sim):
            pick = rng.integers(0, n, size=n)
            sim_diffs = diffs_std[pick] * sd_diff + alvo
            aucs = []
            for slot, j in enumerate(pick):
                a = n3_cent[j] + n3_center[j]
                b = w_cent[j] + n3_center[j] + sim_diffs[slot]
                y = np.concatenate([np.zeros(a.size, np.int8), np.ones(b.size, np.int8)])
                v = fast_auc(y, np.concatenate([a, b]))
                if v is not None:
                    aucs.append(v)
            aucs = np.asarray(aucs)
            aucs_med.append(aucs.mean())
            p = p_teste_calibrado(aucs)
            if p is not None and p < alpha:
                sig += 1
        poder = sig / args.n_sim
        lo, hi = wilson_ci(sig, args.n_sim)
        results.append({"dz_alvo": dz, "auc_por_sujeito_media": float(np.mean(aucs_med)),
                        "poder_estimado": poder, "poder_ic95_low": lo, "poder_ic95_high": hi,
                        "n_sim": args.n_sim})
        print(f"  dz={dz:.2f} -> AUC por sujeito {np.mean(aucs_med):.4f} | "
              f"poder={poder:.1%} [IC95 {lo:.1%}-{hi:.1%}]  ({time.time()-t0:.0f}s)", flush=True)

    res = pd.DataFrame(results)
    res.to_csv(HERE / "poder_por_efeito.csv", index=False)

    acima = res[res["poder_estimado"] >= 0.80]
    mde = acima["dz_alvo"].min() if not acima.empty else None
    erro_tipo1 = float(res.loc[res["dz_alvo"] == 0.0, "poder_estimado"].iloc[0])
    auc_pooled_obs = float(roc_auc_score((wn3["stage"] == "W").astype(int).values, wn3["resid"].values))

    resumo = f"""# Poder estatistico / efeito minimo detectavel — sono, n={n}

Gerado por `poder_estatistico_sono.py` (v3, teste calibrado) em {time.strftime('%Y-%m-%d %H:%M')}.
`--n-sim {args.n_sim}`, alfa = 0,05.

Pergunta: dado o desenho atual (n={n} sujeitos), qual e o menor efeito verdadeiro que este
projeto detectaria de forma confiavel (80% de poder)?

> **Terceira versao.** A v1 nao reamostrava nada (replicas identicas, MDE dz~0,2 invalido);
> a v2 media o poder do teste antigo, que rejeita 100% das vezes sob o nulo neste desenho.
> Numeros antigos preservados com sufixos `_INVALIDO_replicas_identicas` e
> `_teste_antigo_descalibrado`. **Nao cite nenhum dos dois.**

Teste avaliado aqui: AUC calculada dentro de cada sujeito, seguida de Wilcoxon dessas AUCs
contra 0,5 (`scripts_para_rodar/teste_calibrado/`).

## Efeito observado nos dados reais
- Diferenca pareada media = {mean_diff:.5f}, DP = {sd_diff:.5f}, **Cohen's dz = {dz_obs:.4f}**
- **AUC por sujeito = {aucs_obs.mean():.4f}**, com {(aucs_obs > 0.5).mean():.0%} dos sujeitos acima de 0,5
- AUC agrupada por epoca (ingenua, para referencia historica) = {auc_pooled_obs:.4f}

## Nivel 1 — formula fechada (nunca afetada pelos bugs)
80% de poder exigiria dz >= {mde_fechada[0.80]:.4f} ({mde_fechada[0.80]/abs(dz_obs):.1f}x o efeito observado).
90% de poder exigiria dz >= {mde_fechada[0.90]:.4f}.

## Nivel 2 — Monte Carlo com o teste calibrado

{res.to_string(index=False)}

**Erro tipo I empirico (linha dz=0): {erro_tipo1:.1%}** — compare com os 5% nominais. Este e
o controle de sanidade que a v2 reprovava (28,3% com o teste antigo sob este mesmo nulo, e
100% sob permutacao de rotulos).

**Efeito minimo detectavel (poder >=80%): dz ~ {mde if mde is not None else 'nao atingido na faixa testada'}.**

## Como ler
- Compare o MDE da simulacao com o da formula fechada ({mde_fechada[0.80]:.4f}). Proximos =
  o teste calibrado tem poder semelhante ao teste-t pareado; menor = e mais sensivel.
- O que decide a leitura do resultado nulo do Cap. 11 e onde o dz OBSERVADO ({dz_obs:.4f})
  cai em relacao ao MDE. Muito abaixo = o desenho nao tinha poder para distinguir "efeito
  pequeno real" de "efeito nulo", e o negativo e menos conclusivo do que parece.
- `dz` mede um efeito de MEDIA; o teste e de POSTOS. A coluna `auc_por_sujeito_media`
  mapeia um no outro, e e por ela que se deve comunicar tamanho de efeito.
- Isto usa a variancia REAL observada nos {n} sujeitos, incluindo os com poucas epocas de N3.
"""
    (HERE / "resumo_poder.md").write_text(resumo, encoding="utf-8")
    print(f"\nErro tipo I empirico: {erro_tipo1:.1%} | MDE (poder>=80%): dz~{mde}", flush=True)
    print("Processamento concluido. Saidas em:", HERE, flush=True)


if __name__ == "__main__":
    main()
