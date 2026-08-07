"""Frente G — reforco estatistico (IC 95%, effect size, correcao para multiplas comparacoes)
dos resultados empiricos ja obtidos pelo projeto (Blocos F/K/N/O).

Contexto: os recomputes ja feitos (sono, propofol por dose nominal, propofol por
responsividade, integracao diferenciada com controle 1/f) reportam pontos estimados
(AUC, correlacao de Spearman) mas, ate agora, sem intervalo de confianca, sem effect
size padronizado e sem correcao para o fato de que muitas metricas/testes foram
comparados no mesmo conjunto de sujeitos. Isso e exatamente a lacuna que a Frente G
do plano estrategico pede para fechar ("reforco estatistico... dos resultados ja
obtidos", nao um novo experimento).

Este script:
  1. Le os CSVs por-epoca ja gerados pelos scripts anteriores (nao baixa nem recalcula
     LZc/PE/1f do zero).
  2. Para cada comparacao ja reportada (AUC de discriminacao entre dois estados/grupos,
     ou correlacao de Spearman), recalcula um INTERVALO DE CONFIANCA 95% via bootstrap
     por SUJEITO (nao por epoca) e um EFFECT SIZE padronizado.
  3. Ao final, aplica correcao de Benjamini-Hochberg (FDR) sobre TODOS os p-valores
     coletados (bootstrap ou analitico), porque varias metricas/comparacoes foram
     testadas no mesmo dataset em rodadas diferentes (Blocos F/K/N/O) e nunca foram
     corrigidas em conjunto.

Por que bootstrap por SUJEITO, nao por epoca (decisao metodologica central deste script):
  epocas do mesmo sujeito sao correlacionadas entre si (mesmo cerebro, mesmo estado
  fisiologico) — tratar cada epoca como observacao independente no bootstrap
  produziria um IC artificialmente estreito (pseudo-replicacao), inflando a aparencia
  de precisao. Reamostrar SUJEITOS inteiros (com todas as suas epocas) preserva a
  unidade real de replicacao do estudo (n=36 sujeitos no sono, n=20 no propofol).

IMPORTANTE (regra de governanca, `PLANO_ESTRATEGICO_cientifico.md` Sec.0.1, Frente G):
  este script SO CALCULA quando executado pelo AUTOR, localmente. O agente que o
  escreveu nao o executou -- fez apenas verificacao de sintaxe (compilacao).
  Os calculos aqui sao leves (bootstrap sobre CSVs pequenos ja existentes, nao
  processamento de EEG bruto), mas seguem a mesma disciplina dos scripts anteriores
  por consistencia e porque a especificacao da Frente G no plano diz explicitamente
  "scripts de IC/effect size; autor roda".

Uso:
    python reforco_estatistico.py --project-root <caminho_para_a_raiz_do_projeto> [--n-boot 2000]

    Por padrao, --project-root assume que este script esta em
    <raiz>/scripts_para_rodar/estatistica/ (isto e, dois niveis acima do arquivo).
    Se algum CSV de entrada nao existir (por exemplo, a Frente C n=41 ainda nao
    terminou), o script AVISA e pula essa secao, em vez de falhar -- rode de novo
    depois que o CSV faltante existir para completar a tabela.

Entradas esperadas (todas ja geradas por scripts anteriores, nenhuma nova):
    recompute_empirico_v2/sleepedf_por_epoca.csv          (Bloco F/K)
    recompute_empirico_v2/propofol_por_epoca.csv           (Bloco K, por dose nominal)
    scripts_para_rodar/anestesia_responsividade/propofol_responsividade_por_epoca.csv  (Bloco O)
    scripts_para_rodar/anestesia_responsividade/correlacao_basal_vs_mudanca.csv        (Bloco O)
    scripts_para_rodar/integracao_diferenciada/integracao_diferenciada_por_epoca.csv   (Bloco N, opcional)

Saidas (nesta pasta):
    reforco_estatistico_resultados.csv   - uma linha por teste: bloco, comparacao,
                                            metrica, estatistica, IC95, effect size,
                                            p-valor bruto, p-valor corrigido (FDR)
    resumo_reforco_estatistico.md        - narrativa (a interpretar depois)
"""
from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")

HERE = Path(__file__).parent


# ---------------------------------------------------------------------------
# Utilitarios estatisticos
# ---------------------------------------------------------------------------

def cluster_bootstrap_auc(df, subject_col, state_col, score_col, state_a, state_b, positive,
                           n_boot=2000, rng=None):
    """AUC (positive vs a outra) discriminando por score_col, com IC 95% e p-valor via
    bootstrap por SUJEITO (reamostra sujeitos inteiros, nao epocas isoladas)."""
    if rng is None:
        rng = np.random.default_rng()
    sub = df[df[state_col].isin([state_a, state_b])].dropna(subset=[score_col])
    subjects = sub[subject_col].unique()
    if len(subjects) < 4:
        return None
    y_full = (sub[state_col] == positive).astype(int).values
    if len(set(y_full)) < 2:
        return None
    point = float(roc_auc_score(y_full, sub[score_col].values))

    by_subject = {s: sub[sub[subject_col] == s] for s in subjects}
    boots = []
    for _ in range(n_boot):
        resampled = rng.choice(subjects, size=len(subjects), replace=True)
        boot_df = pd.concat([by_subject[s] for s in resampled], ignore_index=True)
        y = (boot_df[state_col] == positive).astype(int).values
        if len(set(y)) < 2:
            continue
        try:
            boots.append(roc_auc_score(y, boot_df[score_col].values))
        except ValueError:
            continue
    if len(boots) < 200:
        return {"auc": point, "ic95_low": None, "ic95_high": None,
                "effect_size_rank_biserial": 2 * point - 1,
                "p_valor_bootstrap": None, "n_boot_validos": len(boots), "n_sujeitos": len(subjects)}
    boots = np.array(boots)
    ic_low, ic_high = np.percentile(boots, [2.5, 97.5])
    # p-valor bootstrap bicaudal para H0: AUC = 0.5
    frac_below = float(np.mean(boots <= 0.5))
    frac_above = float(np.mean(boots >= 0.5))
    p_boot = float(min(1.0, 2 * min(frac_below, frac_above)))
    return {
        "auc": point, "ic95_low": float(ic_low), "ic95_high": float(ic_high),
        "effect_size_rank_biserial": float(2 * point - 1),
        "p_valor_bootstrap": p_boot, "n_boot_validos": len(boots), "n_sujeitos": len(subjects),
    }


def paired_cohens_d(df, subject_col, state_col, score_col, state_a, state_b):
    """Cohen's d PAREADO sobre medias por sujeito (state_b - state_a), evitando tratar
    cada epoca como observacao independente (pseudo-replicacao)."""
    per_subj = (df[df[state_col].isin([state_a, state_b])]
                .groupby([subject_col, state_col])[score_col].mean().unstack())
    if state_a not in per_subj.columns or state_b not in per_subj.columns:
        return None
    diffs = (per_subj[state_b] - per_subj[state_a]).dropna()
    if len(diffs) < 4 or diffs.std(ddof=1) == 0:
        return None
    d = float(diffs.mean() / diffs.std(ddof=1))
    return {"cohens_d_pareado": d, "n_sujeitos": int(len(diffs)), "media_diferenca": float(diffs.mean())}


def cluster_bootstrap_spearman(per_subject_x, per_subject_y, n_boot=2000, rng=None):
    """IC 95% via bootstrap por sujeito para uma correlacao de Spearman ja calculada a
    nivel de sujeito (usa os proprios valores por sujeito, nao epocas)."""
    if rng is None:
        rng = np.random.default_rng()
    x = np.asarray(per_subject_x)
    y = np.asarray(per_subject_y)
    valid = ~(np.isnan(x) | np.isnan(y))
    x, y = x[valid], y[valid]
    n = len(x)
    if n < 4:
        return None
    rho_point, _ = spearmanr(x, y)
    boots = []
    idx = np.arange(n)
    for _ in range(n_boot):
        resampled = rng.choice(idx, size=n, replace=True)
        if len(set(resampled)) < 3:
            continue
        rho, _ = spearmanr(x[resampled], y[resampled])
        if not np.isnan(rho):
            boots.append(rho)
    if len(boots) < 200:
        return {"rho": float(rho_point), "ic95_low": None, "ic95_high": None, "n_sujeitos": n}
    ic_low, ic_high = np.percentile(boots, [2.5, 97.5])
    return {"rho": float(rho_point), "ic95_low": float(ic_low), "ic95_high": float(ic_high), "n_sujeitos": n}


def residualize(y, confound):
    """Residuos de uma regressao linear simples y ~ confound (mesma logica descrita em
    integracao_diferenciada_1f.py: remove a parte de y explicada linearmente pelo
    confundidor, ex. o expoente 1/f)."""
    y = np.asarray(y, dtype=float)
    c = np.asarray(confound, dtype=float)
    valid = ~(np.isnan(y) | np.isnan(c))
    if valid.sum() < 4:
        return np.full_like(y, np.nan)
    coeffs = np.polyfit(c[valid], y[valid], deg=1)
    pred = np.polyval(coeffs, c)
    resid = y - pred
    resid[~valid] = np.nan
    return resid


def benjamini_hochberg(pvals):
    """Correcao de Benjamini-Hochberg (FDR) -- escolhida em vez de Bonferroni por ser
    menos conservadora quando os testes nao sao todos independentes (varias metricas
    calculadas no mesmo conjunto de sujeitos, em rodadas/blocos diferentes)."""
    pvals = np.asarray(pvals, dtype=float)
    n = len(pvals)
    valid = ~np.isnan(pvals)
    q = np.full(n, np.nan)
    if valid.sum() == 0:
        return q
    idx_valid = np.where(valid)[0]
    p_valid = pvals[idx_valid]
    order = np.argsort(p_valid)
    ranked = p_valid[order]
    m = len(ranked)
    raw_q = ranked * m / (np.arange(m) + 1)
    raw_q = np.minimum.accumulate(raw_q[::-1])[::-1]
    raw_q = np.clip(raw_q, 0, 1)
    q_valid = np.empty(m)
    q_valid[order] = raw_q
    q[idx_valid] = q_valid
    return q


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", type=str, default=str(HERE.parent.parent),
                     help="Raiz do projeto (pasta que contem recompute_empirico_v2/, scripts_para_rodar/, etc.)")
    ap.add_argument("--n-boot", type=int, default=2000, help="Numero de reamostragens bootstrap")
    args = ap.parse_args()
    root = Path(args.project_root)
    rng = np.random.default_rng(12345)

    resultados = []  # lista de dicts, uma linha por teste

    # --- Bloco F/K: Sleep-EDF, W vs N3 ---
    sleep_path = root / "recompute_empirico_v2" / "sleepedf_por_epoca.csv"
    if sleep_path.exists():
        print(f"=== Lendo {sleep_path} ===")
        sleep_df = pd.read_csv(sleep_path)
        for metrica in ["lzc", "pe"]:
            r = cluster_bootstrap_auc(sleep_df, "subject", "stage", metrica, "N3", "W", positive="W",
                                       n_boot=args.n_boot, rng=rng)
            d = paired_cohens_d(sleep_df, "subject", "stage", metrica, "N3", "W")
            if r:
                resultados.append({"bloco": "F/K", "comparacao": "sono: W vs N3", "metrica": metrica,
                                    "tipo": "AUC", "estatistica": r["auc"],
                                    "ic95_low": r["ic95_low"], "ic95_high": r["ic95_high"],
                                    "effect_size": r["effect_size_rank_biserial"],
                                    "effect_size_tipo": "rank-biserial (2*AUC-1)",
                                    "p_valor": r["p_valor_bootstrap"], "n_sujeitos": r["n_sujeitos"]})
            if d:
                resultados.append({"bloco": "F/K", "comparacao": "sono: W vs N3", "metrica": metrica,
                                    "tipo": "Cohen's d pareado", "estatistica": d["cohens_d_pareado"],
                                    "ic95_low": None, "ic95_high": None,
                                    "effect_size": d["cohens_d_pareado"], "effect_size_tipo": "Cohen's d pareado",
                                    "p_valor": None, "n_sujeitos": d["n_sujeitos"]})
    else:
        print(f"[AVISO] não encontrei {sleep_path} — pulando reforço estatístico do sono. "
              f"Rode de novo depois de gerar esse CSV (Bloco F/K).")

    # --- Bloco K: Propofol por dose nominal, basal vs sedação moderada ---
    prop_path = root / "recompute_empirico_v2" / "propofol_por_epoca.csv"
    if prop_path.exists():
        print(f"=== Lendo {prop_path} ===")
        prop_df = pd.read_csv(prop_path)
        for metrica in ["lzc", "pe"]:
            # positive="basal" (nao "sedacao_moderada") para bater exatamente com a convencao
            # ja usada em analise_anestesia_propofol.py (Bloco K) -- la, AUC<0.5 significa
            # "moderada teve complexidade MAIOR que basal" (o resultado negativo original).
            # A Frente D (Bloco O, abaixo) usa a convencao OPOSTA (positive="sedacao_moderada"),
            # de proposito, para casar com "aumento paradoxal" de Newman et al. (2026) — as duas
            # convivem no projeto; cada secao deste script respeita a convencao da sua fonte.
            r = cluster_bootstrap_auc(prop_df, "subject", "state", metrica, "basal", "sedacao_moderada",
                                       positive="basal", n_boot=args.n_boot, rng=rng)
            if r:
                resultados.append({"bloco": "K", "comparacao": "propofol (dose nominal): basal vs moderada",
                                    "metrica": metrica, "tipo": "AUC", "estatistica": r["auc"],
                                    "ic95_low": r["ic95_low"], "ic95_high": r["ic95_high"],
                                    "effect_size": r["effect_size_rank_biserial"],
                                    "effect_size_tipo": "rank-biserial (2*AUC-1)",
                                    "p_valor": r["p_valor_bootstrap"], "n_sujeitos": r["n_sujeitos"]})
    else:
        print(f"[AVISO] não encontrei {prop_path} — pulando reforço estatístico do propofol por dose nominal (Bloco K).")

    # --- Bloco O: Propofol por responsividade (Frente D) ---
    frente_d_dir = root / "scripts_para_rodar" / "anestesia_responsividade"
    fd_epocas_path = frente_d_dir / "propofol_responsividade_por_epoca.csv"
    if fd_epocas_path.exists():
        print(f"=== Lendo {fd_epocas_path} ===")
        fd_df = pd.read_csv(fd_epocas_path)
        for grupo in ["responsive", "drowsy"]:
            sub_grupo = fd_df[fd_df["grupo_responsividade"] == grupo]
            for metrica in ["lzc", "pe"]:
                r = cluster_bootstrap_auc(sub_grupo, "subject", "state", metrica, "basal", "sedacao_moderada",
                                           positive="sedacao_moderada", n_boot=args.n_boot, rng=rng)
                if r:
                    resultados.append({"bloco": "O", "comparacao": f"propofol (responsividade): basal vs moderada, grupo {grupo}",
                                        "metrica": metrica, "tipo": "AUC", "estatistica": r["auc"],
                                        "ic95_low": r["ic95_low"], "ic95_high": r["ic95_high"],
                                        "effect_size": r["effect_size_rank_biserial"],
                                        "effect_size_tipo": "rank-biserial (2*AUC-1)",
                                        "p_valor": r["p_valor_bootstrap"], "n_sujeitos": r["n_sujeitos"]})

        # correlação basal x mudança, com IC (recalculada a partir dos dados por época)
        per_subj = fd_df.groupby(["subject", "state"])[["lzc", "pe"]].mean().unstack()
        for metrica in ["lzc", "pe"]:
            if (metrica, "basal") in per_subj.columns and (metrica, "sedacao_moderada") in per_subj.columns:
                basal = per_subj[(metrica, "basal")]
                delta = per_subj[(metrica, "sedacao_moderada")] - basal
                r = cluster_bootstrap_spearman(basal.values, delta.values, n_boot=args.n_boot, rng=rng)
                if r:
                    _, p_analitico = spearmanr(basal.dropna(), delta.dropna()) if len(basal.dropna()) >= 4 else (None, None)
                    resultados.append({"bloco": "O", "comparacao": "propofol: complexidade basal x mudança sob sedação moderada",
                                        "metrica": metrica, "tipo": "Spearman rho", "estatistica": r["rho"],
                                        "ic95_low": r["ic95_low"], "ic95_high": r["ic95_high"],
                                        "effect_size": r["rho"], "effect_size_tipo": "rho (Spearman)",
                                        "p_valor": p_analitico, "n_sujeitos": r["n_sujeitos"]})
    else:
        print(f"[AVISO] não encontrei {fd_epocas_path} — pulando reforço estatístico da Frente D (Bloco O).")

    # --- Bloco N: Integração diferenciada com controle 1/f (Frente C) ---
    frente_c_dir = root / "scripts_para_rodar" / "integracao_diferenciada"
    fc_epocas_path = frente_c_dir / "integracao_diferenciada_por_epoca.csv"
    if fc_epocas_path.exists():
        print(f"=== Lendo {fc_epocas_path} ===")
        fc_df = pd.read_csv(fc_epocas_path)
        metricas_fc = ["lzc", "pe", "sync_bruta", "integracao_mi", "indice_integ_diferenciada"]
        for metrica in metricas_fc:
            if metrica not in fc_df.columns:
                continue
            # bruta
            r = cluster_bootstrap_auc(fc_df, "subject", "stage", metrica, "N3", "W", positive="W",
                                       n_boot=args.n_boot, rng=rng)
            if r:
                resultados.append({"bloco": "N", "comparacao": "sono (Frente C): W vs N3, bruta",
                                    "metrica": metrica, "tipo": "AUC", "estatistica": r["auc"],
                                    "ic95_low": r["ic95_low"], "ic95_high": r["ic95_high"],
                                    "effect_size": r["effect_size_rank_biserial"],
                                    "effect_size_tipo": "rank-biserial (2*AUC-1)",
                                    "p_valor": r["p_valor_bootstrap"], "n_sujeitos": r["n_sujeitos"]})
            # residualizada por 1/f (recalculada aqui, mesma lógica do script da Frente C)
            if "exponent_1f" in fc_df.columns:
                tmp = fc_df[fc_df["stage"].isin(["N3", "W"])].dropna(subset=[metrica, "exponent_1f"]).copy()
                tmp["resid"] = residualize(tmp[metrica].values, tmp["exponent_1f"].values)
                tmp = tmp.dropna(subset=["resid"])
                r_resid = cluster_bootstrap_auc(tmp, "subject", "stage", "resid", "N3", "W", positive="W",
                                                 n_boot=args.n_boot, rng=rng)
                if r_resid:
                    resultados.append({"bloco": "N", "comparacao": "sono (Frente C): W vs N3, residualizada por 1/f",
                                        "metrica": metrica, "tipo": "AUC", "estatistica": r_resid["auc"],
                                        "ic95_low": r_resid["ic95_low"], "ic95_high": r_resid["ic95_high"],
                                        "effect_size": r_resid["effect_size_rank_biserial"],
                                        "effect_size_tipo": "rank-biserial (2*AUC-1)",
                                        "p_valor": r_resid["p_valor_bootstrap"], "n_sujeitos": r_resid["n_sujeitos"]})
    else:
        print(f"[AVISO] não encontrei {fc_epocas_path} — pulando reforço estatístico da Frente C (Bloco N). "
              f"Isso é esperado se a amostra completa (--n-subjects 41) ainda não terminou de rodar; "
              f"rode este script de novo depois.")

    if not resultados:
        raise RuntimeError("Nenhum CSV de entrada encontrado — nada para calcular. Confira --project-root.")

    resultados_df = pd.DataFrame(resultados)
    resultados_df["p_valor_fdr_bh"] = benjamini_hochberg(resultados_df["p_valor"].values)
    resultados_df.to_csv(HERE / "reforco_estatistico_resultados.csv", index=False)
    print("\n=== Tabela final (reforco_estatistico_resultados.csv) ===")
    print(resultados_df.to_string(index=False))

    n_testes_com_p = resultados_df["p_valor"].notna().sum()
    n_sobrevivem_fdr = (resultados_df["p_valor_fdr_bh"] < 0.05).sum()
    resumo = f"""# Frente G — Resumo do reforço estatístico (gerado automaticamente, a interpretar depois)

Total de comparações calculadas: {len(resultados_df)}
Comparações com p-valor associado (bootstrap ou analítico): {n_testes_com_p}
Sobrevivem à correção de Benjamini-Hochberg (FDR, q<0.05): {n_sobrevivem_fdr}

## Como ler a tabela

- **estatistica**: valor pontual (AUC, Spearman rho, ou Cohen's d) já reportado nos Blocos F/K/N/O.
- **ic95_low / ic95_high**: intervalo de confiança 95%, via bootstrap por SUJEITO (não por época —
  ver docstring do script para a justificativa: bootstrap por época daria IC artificialmente estreito).
- **effect_size**: para AUC, a correlação rank-biserial (2·AUC−1, varia de −1 a 1, 0 = sem discriminação);
  para Spearman, o próprio rho; para Cohen's d, o próprio d (pareado, sobre médias por sujeito).
- **p_valor**: bootstrap (para AUC) ou analítico já reportado (para Spearman).
- **p_valor_fdr_bh**: p-valor corrigido por Benjamini-Hochberg (FDR) considerando TODOS os testes
  desta tabela em conjunto — é este valor, não o p_valor bruto, que deveria ser citado no manuscrito
  ao afirmar significância, porque múltiplas métricas/comparações foram testadas no mesmo conjunto
  de sujeitos ao longo dos Blocos F/K/N/O.

## Leitura (preencher depois de rodar — não inventar conclusão aqui)
- Onde o IC95 do AUC exclui 0,5 (ou o IC95 do rho exclui 0), e o p_valor_fdr_bh < 0,05, o resultado
  é robusto a essa correção.
- Onde o IC95 é largo e cruza 0,5/0 (comum com n pequeno, ex. o grupo "drowsy" da Frente D com n=7),
  isso deve ser reportado como incerteza real, não escondido atrás do ponto estimado.
- Comparar esta tabela com os relatórios narrativos originais (RELATORIO_v2.md, resumo_frente_c.md,
  resumo_frente_d.md) — nenhuma conclusão qualitativa deveria mudar, mas a precisão declarada muda.
"""
    (HERE / "resumo_reforco_estatistico.md").write_text(resumo, encoding="utf-8")
    print(f"\nComparações com p-valor: {n_testes_com_p} | sobrevivem FDR q<0.05: {n_sobrevivem_fdr}")
    print("Processamento concluído. Saídas em:", HERE)


if __name__ == "__main__":
    main()
