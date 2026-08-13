"""Teste calibrado: AUC POR SUJEITO + teste de uma amostra contra 0,5.

Substitui o `cluster_bootstrap_auc` usado em todo o projeto, que a varredura de 2026-08-13
(`varredura_desenhos.py`) mostrou ser anticonservador em parte dos desenhos: erro tipo I
entre 0% e 100% conforme o caso, contra 5% nominal -- invalido em 3 dos 15 desenhos
testados, suspeito em 2, valido nos outros 10. Nenhuma conclusao ja registrada muda quando
refeita com o teste calibrado, mas os p-valores do teste antigo nao sao confiaveis onde
ele nao foi validado.

POR QUE O TESTE ANTIGO FALHA
    Ele agrupa todas as epocas de todos os sujeitos, calcula UMA AUC sobre esse pool, e
    reamostra sujeitos para obter o IC. O problema e o pool: sujeitos diferem no nivel
    geral da metrica e contribuem numeros desiguais de epocas em cada condicao, entao a
    AUC agrupada nao e 0,5 mesmo quando toda diferenca intra-sujeito e zero -- agregacao
    tipo Simpson. No Sleep-EDF (8.923 epocas de W contra 3.972 de N3, razao 2,25:1) a AUC
    sob o nulo e 0,567. O teste compara isso contra 0,5 e rejeita demais.

POR QUE ESTE RESOLVE
    Calcula a AUC DENTRO de cada sujeito (as epocas dele num estado contra as dele no
    outro) e depois testa a distribuicao dessas AUCs contra 0,5. Nao ha pool entre
    sujeitos, entao o desequilibrio de epocas deixa de importar por construcao: sob o
    nulo, a AUC de cada sujeito tem esperanca exatamente 0,5. Estimando preservado em
    AUC, entao as tabelas do manuscrito mudam de numero e de metodo, nao de unidade.

    Teste principal: Wilcoxon dos postos sinalizados (nao exige normalidade). O teste-t
    de uma amostra vai ao lado, como referencia.

    ATENCAO com n pequeno: com n=7 (grupo drowsy), o menor p bilateral que o Wilcoxon
    pode produzir e 2/2^7 = 0,0156. Significancia ali e possivel, mas granular.

A CALIBRACAO fica em `varredura_desenhos.py`, nesta mesma pasta -- ela impoe o nulo por
permutacao de rotulos dentro de cada sujeito e mede o erro tipo I dos DOIS testes em cada
desenho do registro. Resumo de 2026-08-13 (alfa nominal 0,05): o teste antigo vai de 0% a
100% conforme o desenho; o teste NOVO fica entre 2,0% e 8,5% em todos os 15.

O preditor do viés NAO e a razao de epocas -- `REM vs W emg_rms` (razao 1,45) e invalido e
`REM vs N1 emg_rms` (razao 1,89) e valido. O que produz o viés e a covariancia entre o
nivel geral de cada sujeito na metrica e o desequilibrio individual dele entre as duas
condicoes. Diagnostico direto: a coluna `auc_agrupada_sob_nulo` da varredura.

Uso:
    python teste_auc_por_sujeito.py [--n-folds 5]

Saidas (nesta pasta):
    resultados_por_sujeito.csv  - todas as comparacoes, com o numero antigo ao lado
    resumo_teste_calibrado.md   - relatorio narrativo
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold

HERE = Path(__file__).parent
BASE = HERE.parent
SONO_INTEG = BASE / "integracao_diferenciada" / "integracao_diferenciada_por_epoca.csv"
SONO_MULTI = BASE / "complexidade_multivariada" / "lzc_multivariado_por_epoca.csv"
ANESTESIA = BASE / "anestesia_1f" / "propofol_1f_por_epoca.csv"


# ----------------------------------------------------------------------------------
# nucleo
# ----------------------------------------------------------------------------------

def fast_auc(y: np.ndarray, scores: np.ndarray) -> float | None:
    n_pos = int(y.sum())
    n_neg = y.size - n_pos
    if n_pos == 0 or n_neg == 0:
        return None
    ranks = stats.rankdata(scores)
    return float((ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def auc_por_sujeito(df, subject_col, state_col, score_col, estado_neg, estado_pos,
                    min_epocas=3):
    """AUC calculada DENTRO de cada sujeito. Retorna (aucs, sujeitos, n_epocas)."""
    sub = df[df[state_col].isin([estado_neg, estado_pos])].dropna(subset=[score_col])
    aucs, sujeitos, n_epocas = [], [], []
    for s, g in sub.groupby(subject_col):
        neg = g[g[state_col] == estado_neg][score_col].values
        pos = g[g[state_col] == estado_pos][score_col].values
        if neg.size < min_epocas or pos.size < min_epocas:
            continue
        y = np.concatenate([np.zeros(neg.size, dtype=np.int8), np.ones(pos.size, dtype=np.int8)])
        a = fast_auc(y, np.concatenate([neg, pos]))
        if a is not None:
            aucs.append(a)
            sujeitos.append(s)
            n_epocas.append(neg.size + pos.size)
    return np.asarray(aucs), sujeitos, np.asarray(n_epocas)


def teste_uma_amostra(aucs: np.ndarray, rng, n_boot=10000):
    """Wilcoxon contra 0,5, com teste-t de referencia e IC bootstrap da media."""
    n = aucs.size
    if n < 5:
        return None
    d = aucs - 0.5
    if np.allclose(d, 0):
        p_w = 1.0
    else:
        p_w = float(stats.wilcoxon(d, alternative="two-sided", zero_method="wilcox").pvalue)
    p_t = float(stats.ttest_1samp(aucs, 0.5).pvalue)
    idx = rng.integers(0, n, size=(n_boot, n))
    medias = aucs[idx].mean(axis=1)
    lo, hi = np.percentile(medias, [2.5, 97.5])
    return {"n_sujeitos": int(n), "auc_media": float(aucs.mean()),
            "auc_mediana": float(np.median(aucs)), "auc_dp": float(aucs.std(ddof=1)),
            "ic95_low": float(lo), "ic95_high": float(hi),
            "p_wilcoxon": p_w, "p_ttest": p_t,
            "frac_sujeitos_acima_05": float(np.mean(aucs > 0.5))}


def benjamini_hochberg(p):
    p = np.asarray(p, dtype=float)
    ok = ~np.isnan(p)
    q = np.full(p.shape, np.nan)
    pv = p[ok]
    n = pv.size
    if n == 0:
        return q
    ordem = np.argsort(pv)
    ajust = np.empty(n)
    menor = 1.0
    for rank in range(n - 1, -1, -1):
        val = pv[ordem[rank]] * n / (rank + 1)
        menor = min(menor, val)
        ajust[ordem[rank]] = menor
    q[ok] = np.minimum(ajust, 1.0)
    return q


# ----------------------------------------------------------------------------------
# residualizacao por 1/f (mesmo esquema ja usado no projeto)
# ----------------------------------------------------------------------------------

def residualizar_in_sample(df, metric_col, cov_col):
    sub = df.dropna(subset=[metric_col, cov_col]).copy()
    X = sub[cov_col].values.reshape(-1, 1)
    sub["_score"] = sub[metric_col].values - LinearRegression().fit(X, sub[metric_col].values).predict(X)
    return sub


def residualizar_out_of_sample(df, metric_col, cov_col, subject_col, n_folds, rng):
    sub = df.dropna(subset=[metric_col, cov_col]).copy()
    subjects = sub[subject_col].unique().copy()
    if subjects.size < 2:
        sub["_score"] = np.nan
        return sub
    n_folds = max(2, min(n_folds, subjects.size))
    rng.shuffle(subjects)
    resid = pd.Series(index=sub.index, dtype=float)
    for tr, te in KFold(n_splits=n_folds, shuffle=False).split(subjects):
        treino = sub[sub[subject_col].isin(set(subjects[tr]))]
        teste = sub[sub[subject_col].isin(set(subjects[te]))]
        if len(treino) < 10 or teste.empty:
            continue
        reg = LinearRegression().fit(treino[[cov_col]].values, treino[metric_col].values)
        resid.loc[teste.index] = teste[metric_col].values - reg.predict(teste[[cov_col]].values)
    sub["_score"] = resid
    return sub


def preparar(df, metric_col, cov_col, subject_col, tipo, n_folds, rng):
    """Devolve o DataFrame com a coluna `_score` pronta para o tipo pedido."""
    if tipo == "bruta":
        out = df.dropna(subset=[metric_col]).copy()
        out["_score"] = out[metric_col].values
        return out
    if tipo == "resid_1f_in_sample":
        return residualizar_in_sample(df, metric_col, cov_col)
    if tipo == "resid_1f_out_of_sample":
        return residualizar_out_of_sample(df, metric_col, cov_col, subject_col, n_folds, rng)
    raise ValueError(tipo)


# A calibracao vive em `calibracao_permutacao.py`. A versao que existia aqui impunha o
# nulo recentrando medias, o que e invalido para AUC (ver docstring no topo).

# ----------------------------------------------------------------------------------

# p-valores do teste ANTIGO, para comparacao lado a lado (ja publicados no projeto)
ANTIGO = {
    ("sono", "todos", "lzc", "bruta"): (0.992, 0.000),
    ("sono", "todos", "lzc", "resid_1f_in_sample"): (0.550, 0.280),
    ("sono", "todos", "lzc", "resid_1f_out_of_sample"): (0.554, 0.280),
    ("sono", "todos", "pe", "bruta"): (0.984, 0.000),
    ("sono", "todos", "pe", "resid_1f_in_sample"): (0.580, 0.190),
    ("sono-multi", "todos", "lzc_multivariado", "bruta"): (0.992, 0.000),
    ("sono-multi", "todos", "lzc_multivariado", "resid_1f_out_of_sample"): (0.549, 0.375),
    ("anestesia", "todos", "lzc", "bruta"): (0.669, 0.004),
    ("anestesia", "todos", "lzc", "resid_1f_in_sample"): (0.832, 0.000),
    ("anestesia", "todos", "lzc", "resid_1f_out_of_sample"): (0.829, 0.000),
    ("anestesia", "todos", "pe", "bruta"): (0.547, 0.511),
    ("anestesia", "todos", "pe", "resid_1f_out_of_sample"): (0.610, 0.095),
    ("anestesia", "responsive", "lzc", "bruta"): (0.791, 0.000),
    ("anestesia", "responsive", "lzc", "resid_1f_out_of_sample"): (0.890, 0.000),
    ("anestesia", "drowsy", "lzc", "bruta"): (0.411, 0.049),
    ("anestesia", "drowsy", "lzc", "resid_1f_out_of_sample"): (0.742, 0.035),
    ("anestesia", "drowsy", "pe", "bruta"): (0.283, 0.020),
    ("anestesia", "drowsy", "pe", "resid_1f_out_of_sample"): (0.402, 0.413),
}

TIPOS = ["bruta", "resid_1f_in_sample", "resid_1f_out_of_sample"]


def rodar_bloco(nome, df, subject_col, state_col, estado_neg, estado_pos, metricas,
                grupos, n_folds, rng):
    linhas = []
    for grupo_nome, gdf in grupos:
        # IMPORTANTE: filtrar ao PAR de estados ANTES de residualizar. Essa e a convencao
        # do projeto (`integracao_diferenciada_1f.py` e `anestesia_controle_1f.py` ambos
        # fatiam o par e so entao ajustam a regressao). Residualizar sobre todos os
        # estagios muda o slope -- no sono, incluir N1/N2/REM produziu residuos
        # completamente diferentes e uma AUC por sujeito espuria de 0,65 contra os 0,49
        # reais. Nao alterar sem refazer a comparacao com os numeros publicados.
        gdf = gdf[gdf[state_col].isin([estado_neg, estado_pos])]
        for metrica in metricas:
            for tipo in TIPOS:
                prep = preparar(gdf, metrica, "exponent_1f", subject_col, tipo, n_folds, rng)
                prep = prep.dropna(subset=["_score"])
                if prep.empty:
                    continue
                aucs, _, n_ep = auc_por_sujeito(prep, subject_col, state_col, "_score",
                                                estado_neg, estado_pos)
                res = teste_uma_amostra(aucs, rng)
                if res is None:
                    continue
                antigo = ANTIGO.get((nome, grupo_nome, metrica, tipo))
                res.update({"bloco": nome, "grupo": grupo_nome, "metrica": metrica,
                            "tipo": tipo, "epocas_min": int(n_ep.min()),
                            "epocas_mediana": int(np.median(n_ep)),
                            "auc_antiga_pooled": antigo[0] if antigo else np.nan,
                            "p_antigo_bootstrap": antigo[1] if antigo else np.nan})
                linhas.append(res)
    df_out = pd.DataFrame(linhas)
    if not df_out.empty:
        df_out["q_fdr_bloco"] = benjamini_hochberg(df_out["p_wilcoxon"].values)
    return df_out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-folds", type=int, default=5)
    args = ap.parse_args()
    rng = np.random.default_rng(20260813)

    blocos = []

    # ---- Sono: integracao diferenciada (predicoes 1.2 e 1.3) ----
    if SONO_INTEG.exists():
        print("=== Sono: W vs N3 (integracao_diferenciada) ===", flush=True)
        so = pd.read_csv(SONO_INTEG)
        metricas = ["lzc", "pe", "sync_bruta", "integracao_mi", "indice_integ_diferenciada"]
        metricas = [m for m in metricas if m in so.columns]
        b = rodar_bloco("sono", so, "subject", "stage", "N3", "W", metricas,
                        [("todos", so)], args.n_folds, rng)
        blocos.append(b)
        print(b[["metrica", "tipo", "auc_media", "ic95_low", "ic95_high", "p_wilcoxon",
                 "q_fdr_bloco"]].to_string(index=False), flush=True)

    # ---- Sono: LZc multivariada (predicao 1.3b) ----
    if SONO_MULTI.exists():
        print("\n=== Sono: W vs N3 (complexidade multivariada) ===", flush=True)
        sm = pd.read_csv(SONO_MULTI)
        metricas = [m for m in ["lzc_mean_channels", "lzc_multivariado"] if m in sm.columns]
        b = rodar_bloco("sono-multi", sm, "subject", "stage", "N3", "W", metricas,
                        [("todos", sm)], args.n_folds, rng)
        blocos.append(b)
        print(b[["metrica", "tipo", "auc_media", "ic95_low", "ic95_high", "p_wilcoxon",
                 "q_fdr_bloco"]].to_string(index=False), flush=True)

    # ---- Anestesia: basal vs sedacao moderada (predicao 1.4 + controle 1/f) ----
    if ANESTESIA.exists():
        print("\n=== Anestesia: basal vs sedacao moderada ===", flush=True)
        an = pd.read_csv(ANESTESIA)
        grupos = [("todos", an),
                  ("responsive", an[an["grupo_responsividade"] == "responsive"]),
                  ("drowsy", an[an["grupo_responsividade"] == "drowsy"])]
        b = rodar_bloco("anestesia", an, "subject", "state", "basal", "sedacao_moderada",
                        ["lzc", "pe"], grupos, args.n_folds, rng)
        blocos.append(b)
        print(b[["grupo", "metrica", "tipo", "n_sujeitos", "auc_media", "ic95_low",
                 "ic95_high", "p_wilcoxon", "q_fdr_bloco"]].to_string(index=False), flush=True)

    res = pd.concat(blocos, ignore_index=True)
    colunas = ["bloco", "grupo", "metrica", "tipo", "n_sujeitos", "epocas_min",
               "epocas_mediana", "auc_media", "auc_mediana", "auc_dp", "ic95_low",
               "ic95_high", "frac_sujeitos_acima_05", "p_wilcoxon", "p_ttest",
               "q_fdr_bloco", "auc_antiga_pooled", "p_antigo_bootstrap"]
    res = res[[c for c in colunas if c in res.columns]]
    res.to_csv(HERE / "resultados_por_sujeito.csv", index=False)

    # ---- relatorio ----
    mudou = res.dropna(subset=["p_antigo_bootstrap"]).copy()
    mudou["antigo_signif"] = mudou["p_antigo_bootstrap"] < 0.05
    mudou["novo_signif"] = mudou["p_wilcoxon"] < 0.05
    divergentes = mudou[mudou["antigo_signif"] != mudou["novo_signif"]]

    md = f"""# Teste calibrado (AUC por sujeito) — resultados

Gerado por `teste_auc_por_sujeito.py` em {time.strftime('%Y-%m-%d %H:%M')}.
`--n-folds {args.n_folds}`.

Substitui o `cluster_bootstrap_auc` (AUC agrupada por época + bootstrap de sujeitos) no
desenho do sono, onde o desequilíbrio de épocas (2,25:1) o torna inválido.

## Calibração (de `calibracao_permutacao.py`, permutação de rótulos dentro do sujeito)

| desenho | AUC agrupada sob o nulo | teste ANTIGO | teste NOVO |
|---|---|---|---|
| Anestesia (épocas 1,01:1) | 0,4972 | 5,5% [3,1–9,6%] | 4,0% [2,0–7,7%] |
| Sono (épocas 2,25:1) | 0,5828 | **100,0%** [98,1–100%] | 7,0% [4,2–11,4%] |

O teste antigo é válido no desenho balanceado da anestesia e inválido no do sono.
O teste novo é calibrado nos dois.

## Resultados

{res.to_string(index=False)}

## Onde a conclusão mudou em relação ao teste antigo

{divergentes[['bloco','grupo','metrica','tipo','auc_antiga_pooled','p_antigo_bootstrap','auc_media','p_wilcoxon']].to_string(index=False) if not divergentes.empty else 'Nenhuma divergência de significância a alfa=0,05.'}

## Como ler
- `auc_media` é a média das AUCs **calculadas dentro de cada sujeito** — não é
  comparável em valor absoluto com `auc_antiga_pooled`, que agrupava épocas de todos os
  sujeitos. A AUC por sujeito é tipicamente mais próxima de 0,5, porque não incorpora a
  separação entre sujeitos. A comparação que importa é de **significância**, não de valor.
- `frac_sujeitos_acima_05` mostra a consistência do efeito entre sujeitos: um efeito real
  aparece na maioria dos sujeitos, não só na média.
- `epocas_min` sinaliza sujeitos com poucas épocas, cuja AUC individual é ruidosa.
- `q_fdr_bloco` é Benjamini-Hochberg dentro de cada bloco, como os scripts originais faziam.
"""
    (HERE / "resumo_teste_calibrado.md").write_text(md, encoding="utf-8")
    print(f"\nSaidas em: {HERE}", flush=True)


if __name__ == "__main__":
    main()
