"""Aplica ao dataset de anestesia (propofol, Chennu et al. 2016) o mesmo padrao de rigor
ja estabelecido para o sono apos a correcao do bug de canal (ver
`scripts_para_rodar/complexidade_multivariada/` e `CHECKLIST_pendencias.md`, Bloco W):
controle pela inclinacao espectral 1/f, bootstrap por SUJEITO (nao por epoca), validacao
cruzada fora da amostra por sujeito, e correcao de Benjamini-Hochberg (FDR) sobre todos
os p-valores coletados.

Por que este teste existe: o confundidor 1/f (Hohn et al. 2024) que esvaziou o resultado
de sono (Cap. 11) NUNCA foi testado no dataset de anestesia deste projeto -- os scripts
originais (`analise_anestesia_propofol.py`, `reanalise_responsividade_propofol.py`)
calculam so LZc/PE, sem nenhum ajuste de expoente aperiodico. Isso e uma lacuna real: o
proprio Colombo et al. (2019, ja citado no Cap. 11, ref. 91) mostra que o expoente 1/f
SOZINHO ja rastreia presenca/ausencia de consciencia sob propofol, xenonio e cetamina --
exatamente o paradigma farmacologico deste dataset. Se a discriminacao basal-vs-sedacao
que o projeto ja relata (Bloco K/O) tambem for, em boa parte, uma assinatura espectral
simples, isso muda a leitura do "resultado positivo" ja escrito no Cap. 11 sobre
anestesia -- por isso vale testar antes de tratar aquele achado como mais solido do que
o do sono.

Este script:
  1. Reprocessa os mesmos arquivos .set ja usados por analise_anestesia_propofol.py e
     reanalise_responsividade_propofol.py (mesmo --data-dir, nada baixado de novo):
     LZc e PE por epoca (identico aos scripts anteriores, para comparabilidade), MAIS o
     expoente aperiodico 1/f por epoca (FOOOF/specparam, media entre os 91 canais reais
     deste dataset -- SEM o risco de contaminacao por canal espurio que afetou o sono,
     porque aqui os 91 canais ja vem curados pelos autores originais do dataset, sem
     nenhuma etapa de inferencia de tipo do MNE).
  2. Reconstroi a classificacao responsive/drowsy (mesma logica de
     reanalise_responsividade_propofol.py: IC de Wilson do hit-rate basal vs. moderada).
  3. Testa basal-vs-sedacao-moderada de tres formas, para cada agrupamento (todos os
     sujeitos; so responsive; so drowsy): bruta, residualizada por 1/f dentro da amostra,
     residualizada por 1/f fora da amostra (K-fold por sujeito, ajuste nunca treinado nos
     dados que esta corrigindo -- mesmo "protocolo VNext" agora aplicado ao sono).
  4. Bootstrap por SUJEITO (nao por epoca) para IC95%/p-valor de cada AUC, e correcao FDR
     de Benjamini-Hochberg sobre o conjunto completo de testes coletados.

IMPORTANTE (mesma disciplina do resto do projeto): este script so calcula quando
executado localmente pelo autor, com os arquivos .set reais -- nao ha atalho nem numero
hipotetico aqui. Resultado negativo (nao sobrevive ao controle) e informacao real sobre
os limites do achado de anestesia, tao valida quanto o resultado positivo ja escrito no
Cap. 11; resultado positivo (sobrevive) fortalece esse mesmo achado. Reportar o que sair,
sem escolher a leitura mais favoravel.

Uso:
    python anestesia_controle_1f.py --data-dir <pasta_Sedation-RestingState> [--max-subjects N] [--n-boot 2000] [--n-folds 5]

    Rodada pequena primeiro (recomendado, como nos scripts anteriores):
    python anestesia_controle_1f.py --data-dir <pasta> --max-subjects 3 --n-boot 200

Saidas (nesta pasta):
    propofol_1f_por_epoca.csv        - LZc, PE, expoente 1/f e grupo de responsividade, por epoca
    auc_comparativo_1f.csv           - AUC (bruta / residualizada dentro/fora da amostra),
                                        bootstrap por sujeito, para cada agrupamento e metrica
    responsividade_por_sujeito.csv   - mesma reconstrucao ja usada na Frente D
    resumo_anestesia_1f.md           - relatorio narrativo (a interpretar depois, nao aqui)
"""
from __future__ import annotations

import argparse
import re
import warnings
from pathlib import Path

import antropy as ant
import mne
import numpy as np
import pandas as pd
from pymatreader import read_mat
from scipy import signal
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold

try:
    from fooof import FOOOF
except ImportError:
    from specparam import SpectralModel as FOOOF

mne.set_log_level("ERROR")
warnings.filterwarnings("ignore")

HERE = Path(__file__).parent

STATE_LABELS = {1: "basal", 2: "sedacao_leve", 3: "sedacao_moderada", 4: "recuperacao"}
N_TRIALS_TASK = 40
FIT_FREQ_RANGE = (1.0, 40.0)


def lzc_epoch(x: np.ndarray) -> float:
    b = (x >= np.median(x)).astype(np.uint8)
    return float(ant.lziv_complexity(b, normalize=True))


def aperiodic_exponent(x: np.ndarray, sfreq: float) -> float | None:
    nperseg = min(len(x), int(sfreq * 4))
    if nperseg < int(sfreq * 2):
        return None
    freqs, psd = signal.welch(x, fs=sfreq, nperseg=nperseg, noverlap=nperseg // 2)
    try:
        fm = FOOOF(peak_width_limits=(1.0, 8.0), max_n_peaks=6, aperiodic_mode="fixed", verbose=False)
        fm.fit(freqs, psd, FIT_FREQ_RANGE)
        if hasattr(fm, "aperiodic_params_"):
            return float(fm.aperiodic_params_[1])
        return float(fm.get_params("aperiodic", "exponent"))
    except Exception:
        return None


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    phat = successes / n
    denom = 1 + z ** 2 / n
    center = (phat + z ** 2 / (2 * n)) / denom
    margin = (z * np.sqrt((phat * (1 - phat) + z ** 2 / (4 * n)) / n)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def load_datainfo(data_dir: Path) -> pd.DataFrame:
    mat_path = data_dir / "datainfo.mat"
    d = read_mat(str(mat_path))
    raw_table = d["datainfo"]
    rows = []
    for i, row in enumerate(raw_table):
        try:
            filename = row[0]
            sedation_code = int(row[1])
            correct = float(row[4]) if len(row) > 4 else float("nan")
        except (IndexError, TypeError, ValueError) as e:
            print(f"[AVISO] linha {i} de datainfo.mat em formato inesperado ({e})")
            continue
        rows.append({"filename": filename, "state": STATE_LABELS.get(sedation_code, f"desconhecido_{sedation_code}"),
                      "correctresponses": correct})
    return pd.DataFrame(rows)


def classify_responsiveness(datainfo: pd.DataFrame) -> pd.DataFrame:
    datainfo = datainfo.copy()
    datainfo["subject"] = datainfo["filename"].apply(lambda f: re.match(r"(\d+)", str(f)).group(1))
    rows = []
    for subject, sub in datainfo.groupby("subject"):
        basal = sub[sub["state"] == "basal"]
        moderada = sub[sub["state"] == "sedacao_moderada"]
        if basal.empty or moderada.empty or basal["correctresponses"].isna().any() or moderada["correctresponses"].isna().any():
            rows.append({"subject": subject, "grupo_responsividade": "indeterminado"})
            continue
        n_basal = int(basal["correctresponses"].iloc[0])
        n_mod = int(moderada["correctresponses"].iloc[0])
        ci_basal = wilson_ci(n_basal, N_TRIALS_TASK)
        ci_mod = wilson_ci(n_mod, N_TRIALS_TASK)
        grupo = "drowsy" if ci_mod[1] < ci_basal[0] else "responsive"
        rows.append({"subject": subject, "grupo_responsividade": grupo})
    return pd.DataFrame(rows)


def process_file(set_path: Path, subject_id: str, state: str) -> pd.DataFrame:
    epochs = mne.io.read_epochs_eeglab(str(set_path), verbose=False)
    data = epochs.get_data()
    n_epochs, n_channels, n_times = data.shape
    sfreq = float(epochs.info["sfreq"])

    pe_per_epoch_channel = np.zeros((n_epochs, n_channels))
    for ch in range(n_channels):
        pe_per_epoch_channel[:, ch] = ant.perm_entropy(data[:, ch, :], order=3, normalize=True)
    pe_per_epoch = pe_per_epoch_channel.mean(axis=1)

    lzc_per_epoch = np.zeros(n_epochs)
    exponent_per_epoch = np.full(n_epochs, np.nan)
    for e in range(n_epochs):
        lzc_vals = [lzc_epoch(data[e, ch, :]) for ch in range(n_channels)]
        lzc_per_epoch[e] = float(np.mean(lzc_vals))
        exp_vals = [aperiodic_exponent(data[e, ch, :], sfreq) for ch in range(n_channels)]
        exp_valid = [v for v in exp_vals if v is not None]
        if exp_valid:
            exponent_per_epoch[e] = float(np.mean(exp_valid))

    return pd.DataFrame({
        "subject": subject_id, "state": state, "epoch": np.arange(n_epochs),
        "lzc": lzc_per_epoch, "pe": pe_per_epoch, "exponent_1f": exponent_per_epoch,
    })


def residualize_insample(metric: np.ndarray, covariate: np.ndarray) -> np.ndarray:
    X = covariate.reshape(-1, 1)
    reg = LinearRegression().fit(X, metric)
    return metric - reg.predict(X)


def residualize_out_of_sample(df: pd.DataFrame, metric_col: str, covariate_col: str,
                               subject_col: str, n_folds: int, rng: np.random.Generator) -> pd.Series:
    subjects = df[subject_col].unique()
    resid = pd.Series(index=df.index, dtype=float)
    if len(subjects) < 2:
        # O KFold aqui particiona SUJEITOS, nao epocas -- com menos de 2 sujeitos nao
        # existe particao fora da amostra possivel. A guarda do chamador checa numero de
        # epocas (>=10), que passa mesmo com 1 sujeito, entao a protecao tem de ser aqui.
        # Devolve NaN (o chamador descarta via dropna) em vez de estourar. Inerte na
        # amostra cheia, onde os grupos tem 20/13/7 sujeitos.
        return resid
    n_folds = max(2, min(n_folds, len(subjects)))
    rng.shuffle(subjects)
    kf = KFold(n_splits=n_folds, shuffle=False)
    for train_idx, test_idx in kf.split(subjects):
        train_subjects = set(subjects[train_idx])
        test_subjects = set(subjects[test_idx])
        train_sub = df.loc[df[subject_col].isin(train_subjects)].dropna(subset=[metric_col, covariate_col])
        if len(train_sub) < 10:
            continue
        reg = LinearRegression().fit(train_sub[[covariate_col]].values, train_sub[metric_col].values)
        test_sub = df.loc[df[subject_col].isin(test_subjects)].dropna(subset=[metric_col, covariate_col])
        if test_sub.empty:
            continue
        pred = reg.predict(test_sub[[covariate_col]].values)
        resid.loc[test_sub.index] = test_sub[metric_col].values - pred
    return resid


def cluster_bootstrap_auc(df, subject_col, state_col, score_col, state_a, state_b, positive,
                           n_boot=2000, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    sub = df[df[state_col].isin([state_a, state_b])].dropna(subset=[score_col])
    subjects = sub[subject_col].unique()
    if len(subjects) < 4:
        return {"auc": None, "ic95_low": None, "ic95_high": None, "p_valor_bootstrap": None, "n_sujeitos": len(subjects)}
    y_full = (sub[state_col] == positive).astype(int).values
    if len(set(y_full)) < 2:
        return {"auc": None, "ic95_low": None, "ic95_high": None, "p_valor_bootstrap": None, "n_sujeitos": len(subjects)}
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
    if len(boots) < 100:
        return {"auc": point, "ic95_low": None, "ic95_high": None, "p_valor_bootstrap": None, "n_sujeitos": len(subjects)}
    boots = np.array(boots)
    ic_low, ic_high = np.percentile(boots, [2.5, 97.5])
    frac_below = float(np.mean(boots <= 0.5))
    frac_above = float(np.mean(boots >= 0.5))
    p_boot = float(min(1.0, 2 * min(frac_below, frac_above)))
    return {"auc": point, "ic95_low": float(ic_low), "ic95_high": float(ic_high),
            "p_valor_bootstrap": p_boot, "n_sujeitos": len(subjects)}


def benjamini_hochberg(pvals):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=str, required=True)
    ap.add_argument("--max-subjects", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--n-folds", type=int, default=5)
    args = ap.parse_args()
    rng = np.random.default_rng(20260812)
    data_dir = Path(args.data_dir)

    print("=== Passo 1: datainfo.mat + classificação responsive/drowsy ===")
    datainfo = load_datainfo(data_dir)
    if datainfo.empty:
        raise RuntimeError("datainfo.mat não pôde ser lido — verifique --data-dir.")
    resp_df = classify_responsiveness(datainfo)
    resp_df.to_csv(HERE / "responsividade_por_sujeito.csv", index=False)
    grupo_map = dict(zip(resp_df["subject"], resp_df["grupo_responsividade"]))
    n_resp = (resp_df["grupo_responsividade"] == "responsive").sum()
    n_drow = (resp_df["grupo_responsividade"] == "drowsy").sum()
    print(f"Classificação: {n_resp} responsive, {n_drow} drowsy")

    print("\n=== Passo 2: processando EEG (LZc, PE, expoente 1/f por época, 91 canais) ===")
    set_files = sorted(data_dir.glob("*.set"))
    if not set_files:
        raise RuntimeError(f"Nenhum .set encontrado em {data_dir}")
    state_map = dict(zip(datainfo["filename"], datainfo["state"]))
    subjects_seen, all_rows, failed = [], [], []
    for f in set_files:
        stem = f.stem
        subject_id = re.match(r"(\d+)", stem).group(1)
        if args.max_subjects is not None and subject_id not in subjects_seen and len(subjects_seen) >= args.max_subjects:
            continue
        if subject_id not in subjects_seen:
            subjects_seen.append(subject_id)
        state = state_map.get(stem)
        if state is None:
            continue
        try:
            df = process_file(f, subject_id, state)
            all_rows.append(df)
            print(f"[ok] sujeito {subject_id} / {state}: {len(df)} épocas ({f.name})")
        except Exception as e:
            failed.append((f.name, str(e)))
            print(f"[ERRO] {f.name}: {e}")

    if not all_rows:
        raise RuntimeError("Nenhum arquivo processado com sucesso.")
    epochs_df = pd.concat(all_rows, ignore_index=True)
    epochs_df["grupo_responsividade"] = epochs_df["subject"].map(grupo_map).fillna("indeterminado")
    epochs_df.to_csv(HERE / "propofol_1f_por_epoca.csv", index=False)
    print(f"\nTotal: {len(subjects_seen)} sujeitos, {len(epochs_df)} épocas "
          f"({epochs_df['exponent_1f'].notna().sum()} com 1/f válido). Falhas: {failed if failed else 'nenhuma'}")

    print("\n=== Passo 3: AUC basal-vs-moderada — bruta / residualizada dentro e fora da amostra ===")
    results = []
    groups = [("todos", epochs_df), ("responsive", epochs_df[epochs_df["grupo_responsividade"] == "responsive"]),
              ("drowsy", epochs_df[epochs_df["grupo_responsividade"] == "drowsy"])]
    for grupo_nome, grupo_df in groups:
        bm = grupo_df[grupo_df["state"].isin(["basal", "sedacao_moderada"])]
        for metric in ["lzc", "pe"]:
            boot_raw = cluster_bootstrap_auc(bm, "subject", "state", metric, "basal", "sedacao_moderada",
                                              positive="sedacao_moderada", n_boot=args.n_boot, rng=rng)
            sub_resid = bm.dropna(subset=[metric, "exponent_1f"]).copy()
            resid_in = residualize_insample(sub_resid[metric].values, sub_resid["exponent_1f"].values) if len(sub_resid) >= 10 else None
            if resid_in is not None:
                sub_resid["_tmp"] = resid_in
                boot_in = cluster_bootstrap_auc(sub_resid, "subject", "state", "_tmp", "basal", "sedacao_moderada",
                                                 positive="sedacao_moderada", n_boot=args.n_boot, rng=rng)
            else:
                boot_in = {"auc": None, "ic95_low": None, "ic95_high": None, "p_valor_bootstrap": None, "n_sujeitos": 0}
            oos_resid = residualize_out_of_sample(sub_resid, metric, "exponent_1f", "subject", args.n_folds, rng) if len(sub_resid) >= 10 else pd.Series(dtype=float)
            oos_df = sub_resid.copy()
            oos_df["_resid_oos"] = oos_resid
            oos_df = oos_df.dropna(subset=["_resid_oos"])
            boot_oos = cluster_bootstrap_auc(oos_df, "subject", "state", "_resid_oos", "basal", "sedacao_moderada",
                                              positive="sedacao_moderada", n_boot=args.n_boot, rng=rng) if len(oos_df) >= 10 else {"auc": None, "ic95_low": None, "ic95_high": None, "p_valor_bootstrap": None, "n_sujeitos": 0}
            for tipo, r in [("bruta", boot_raw), ("residualizada_1f_in_sample", boot_in), (f"residualizada_1f_out_of_sample_{args.n_folds}fold", boot_oos)]:
                results.append({"grupo": grupo_nome, "metrica": metric, "tipo": tipo,
                                 "auc": r["auc"], "ic95_low": r["ic95_low"], "ic95_high": r["ic95_high"],
                                 "p_valor_bootstrap": r["p_valor_bootstrap"], "n_sujeitos": r["n_sujeitos"]})

    results_df = pd.DataFrame(results)
    results_df["p_valor_fdr_bh"] = benjamini_hochberg(results_df["p_valor_bootstrap"].values)
    results_df.to_csv(HERE / "auc_comparativo_1f.csv", index=False)
    print(results_df.to_string(index=False))

    resumo = f"""# Controle por 1/f — anestesia (propofol) — resumo (gerado automaticamente, a interpretar depois)

Pergunta: o resultado de anestesia já escrito no Cap. 11 (responsividade explica o
padrão "paradoxal") sobrevive ao mesmo controle por inclinação espectral 1/f que
esvaziou o resultado equivalente do sono?

Sujeitos: {len(subjects_seen)} ({n_resp} responsive, {n_drow} drowsy). Falhas: {failed if failed else 'nenhuma'}.

## Tabela completa
{results_df.to_string(index=False)}

## Como ler
- **bruta**: LZc/PE sem nenhum controle por 1/f — deve reproduzir, aproximadamente, os
  números já publicados em `comparacao_por_grupo.csv` (Bloco O) para responsive/drowsy.
- **residualizada_1f_in_sample / out_of_sample**: mesmo padrão agora aplicado ao sono —
  fora da amostra é o teste mais rigoroso (ajuste nunca treinado nos dados que corrige).
- Comparar "todos" com "responsive"/"drowsy": se o padrão paradoxal (responsive) e o
  padrão esperado (drowsy) sobreviverem à residualização, o achado de anestesia é mais
  robusto que o de sono. Se ambos colapsarem para ~0,5 como o sono colapsou, a leitura
  precisa mudar: o "resultado positivo" da anestesia seria, ele também, majoritariamente
  uma assinatura espectral (Colombo et al. 2019 já mostrou isso ser plausível neste
  mesmo paradigma farmacológico).

## Não inventar conclusão aqui — reportar o número real, qualquer que seja.
"""
    (HERE / "resumo_anestesia_1f.md").write_text(resumo, encoding="utf-8")
    print("\nProcessamento concluído. Saídas em:", HERE)


if __name__ == "__main__":
    main()
