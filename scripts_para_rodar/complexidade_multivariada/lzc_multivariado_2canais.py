"""Teste de complexidade de Lempel-Ziv genuinamente MULTIVARIADA (2 canais), pedido pelo
parecer de neurociência (`pareceres_especialistas/neurociencia.md`, recomendação 3):

    "Testar um índice de complexidade genuinamente multivariado dos 2 canais antes de
    fechar a conclusão negativa sobre 'integração diferenciada'. A única tentativa
    multivariada até aqui (informação mútua gaussiana × entropia de permutação, em
    `integracao_diferenciada_1f.py`) tem desempenho pior que sincronia bruta. Um teste
    mais informativo seria calcular LZc sobre a sequência conjunta/concatenada dos 2
    canais binarizados (complexidade de Lempel-Ziv multivariada, no espírito de Casali
    et al. 2013 ou Schartner et al. 2015/2017 — antes de comprimir, e não depois de
    calcular LZc por canal e tirar a média), e reaplicar o mesmo pipeline de robustez já
    usado para o 1/f (bootstrap por sujeito, correção FDR, ajuste de 1/f treinado fora
    da amostra de teste)."

Diferença em relação a `integracao_diferenciada_1f.py` (que já existe neste projeto):
aquele script computa LZc e entropia de permutação POR CANAL e depois tira a média
(`lzc_mean_channels`) — o que nunca testa se há estrutura conjunta entre os 2 canais que
uma métrica por-canal, seguida de média, simplesmente não pode capturar. Este script
computa, ADICIONALMENTE, uma LZc verdadeiramente multivariada: os 2 canais são
binarizados cada um pela própria mediana (mesma convenção já usada no projeto) e depois
CONCATENADOS numa única sequência binária mais longa antes de comprimir — a mesma lógica
usada por Schartner et al. (2015, PLOS ONE) para "LZc multidimensional" em anestesia, e
próxima em espírito da compressão de padrão espaço-temporal do PCI de Casali et al.
(2013), embora sem a perturbação por TMS que define o PCI propriamente dito.

Pipeline de robustez (reaplicado integralmente, não simplificado):
  1. AUC W-vs-N3 ingênua (todas as épocas agrupadas) — bruta e residualizada por 1/f
     dentro da amostra (mesmo procedimento de `integracao_diferenciada_1f.py`).
  2. AUC W-vs-N3 por bootstrap de SUJEITO (não de época — reamostra sujeitos inteiros,
     preservando a unidade real de replicação), com IC95% e p-valor — mesma função de
     `scripts_para_rodar/estatistica/reforco_estatistico.py` (`cluster_bootstrap_auc`),
     copiada aqui para manter este script autocontido.
  3. AUC W-vs-N3 residualizada por 1/f FORA DA AMOSTRA: regressão metric~exponent_1f
     treinada em 4/5 dos sujeitos (K-fold por sujeito, não por época) e aplicada aos
     sujeitos do fold de teste — o "protocolo VNext" que o Cap. 11 do manuscrito já
     nomeia como o teste mais limpo ainda em aberto. Os resíduos out-of-sample de todos
     os folds são reunidos e re-testados com o mesmo bootstrap por sujeito do item 2.
  4. Correção de Benjamini-Hochberg (FDR) sobre todos os p-valores coletados.

Honestidade metodológica (mesma convenção do resto do projeto): este script SÓ CALCULA
E ESCREVE — a interpretação do resultado (se o índice multivariado sobrevive ou não ao
controle por 1/f) é feita separadamente, depois de rodar, e reportada com a mesma
disciplina do resto do Cap. 11 (resultado negativo é dado, não fracasso).

Uso:
    python lzc_multivariado_2canais.py --n-subjects 41 --data-dir <pasta_cache> [--n-boot 2000] [--n-folds 5]

    Rodada pequena de checagem antes da amostra cheia:
    python lzc_multivariado_2canais.py --n-subjects 3 --data-dir <pasta_cache>

Saídas (nesta pasta):
    lzc_multivariado_por_epoca.csv     - todas as métricas, por época
    auc_comparativo_multivariado.csv   - AUC (ingênua, bootstrap por sujeito, out-of-sample)
                                          para lzc_mean_channels (comparador) e lzc_multivariado
    resumo_lzc_multivariado.md         - relatório narrativo (a interpretar depois)
"""
from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import antropy as ant
import mne
import numpy as np
import pandas as pd
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

ANNOTATION_TO_EVENT = {
    "Sleep stage W": 1,
    "Sleep stage 1": 2,
    "Sleep stage 2": 3,
    "Sleep stage 3": 4,
    "Sleep stage 4": 4,
    "Sleep stage R": 5,
}
EVENT_ID = {"W": 1, "N1": 2, "N2": 3, "N3": 4, "REM": 5}
FIT_FREQ_RANGE = (1.0, 40.0)


def binarize(x: np.ndarray) -> np.ndarray:
    return (x >= np.median(x)).astype(np.uint8)


def lzc_from_binary(b: np.ndarray) -> float:
    """LZc normalizada (LZ76) de uma sequência binária já pronta — usa antropy
    internamente via a mesma rota que `ant.lziv_complexity`, mas aceita a sequência já
    binarizada em vez de recalcular a mediana (necessário para poder passar a
    concatenação dos 2 canais como uma única sequência)."""
    return float(ant.lziv_complexity(b, normalize=True))


def aperiodic_exponent(x: np.ndarray, sfreq: float) -> float | None:
    nperseg = min(len(x), int(sfreq * 4))
    if nperseg < int(sfreq * 2):
        return None
    freqs, psd = signal.welch(x, fs=sfreq, nperseg=nperseg, noverlap=nperseg // 2)
    try:
        fm = FOOOF(peak_width_limits=(1.0, 8.0), max_n_peaks=6, aperiodic_mode="fixed", verbose=False)
        fm.fit(freqs, psd, FIT_FREQ_RANGE)
        # API diverge entre os pacotes fooof (atributo `.aperiodic_params_`) e seu
        # sucessor specparam (metodo `.get_params(...)`) -- tenta os dois, nessa ordem.
        if hasattr(fm, "aperiodic_params_"):
            return float(fm.aperiodic_params_[1])
        return float(fm.get_params("aperiodic", "exponent"))
    except Exception:
        return None


def process_subject(psg_path: str, hyp_path: str, subject_id: int) -> pd.DataFrame:
    raw = mne.io.read_raw_edf(psg_path, stim_channel="marker", infer_types=True, preload=True)
    annot = mne.read_annotations(hyp_path)
    raw.set_annotations(annot, emit_warning=False)

    sleep_annots = [a for a in annot if a["description"] != "Sleep stage ?"]
    if len(sleep_annots) > 2:
        onset_first = sleep_annots[1]["onset"]
        onset_last = sleep_annots[-2]["onset"]
        crop_start = max(0, onset_first - 30 * 60)
        crop_end = onset_last + 30 * 60
        raw.crop(crop_start, min(crop_end, raw.times[-1]))

    ch_types = raw.get_channel_types()
    eeg_picks = [ch for ch, t in zip(raw.ch_names, ch_types) if t == "eeg"]
    # BUGFIX (2026-08-12): infer_types=True rotula erroneamente o canal 'Event marker'
    # como tipo "eeg" no Sleep-EDF Cassette (valores ~900-1000, nao EEG real). Este
    # script ja indexava explicitamente so data[:,0,:] e data[:,1,:] mais abaixo, entao
    # nao herdava o efeito numerico do bug -- mas dependia implicitamente da ordem dos
    # canais (o marcador ordenar por ultimo). Este filtro remove essa fragilidade.
    eeg_picks = [ch for ch in eeg_picks if ch in ("Fpz-Cz", "Pz-Oz")]
    if not eeg_picks:
        eeg_picks = [ch for ch in raw.ch_names if ch in ("Fpz-Cz", "Pz-Oz")]
    if not eeg_picks:
        raise RuntimeError(f"Nenhum canal EEG em {psg_path}")
    raw.pick(eeg_picks)
    raw.filter(0.5, 40.0, fir_design="firwin", verbose=False)

    events, _ = mne.events_from_annotations(raw, event_id=ANNOTATION_TO_EVENT, chunk_duration=30.0, verbose=False)
    tmax = 30.0 - 1.0 / raw.info["sfreq"]
    epochs = mne.Epochs(raw=raw, events=events, event_id=EVENT_ID, tmin=0.0, tmax=tmax, baseline=None, preload=True, verbose=False)

    inv_event_id = {v: k for k, v in EVENT_ID.items()}
    data = epochs.get_data()  # (n_epochs, n_channels, n_times)
    labels = epochs.events[:, 2]
    sfreq = float(raw.info["sfreq"])
    n_ch = data.shape[1]
    if n_ch < 2:
        raise RuntimeError(f"Sujeito {subject_id} tem só {n_ch} canal EEG; este script exige 2.")

    rows = []
    for i in range(data.shape[0]):
        stage = inv_event_id[labels[i]]
        ch0, ch1 = data[i, 0, :], data[i, 1, :]

        b0, b1 = binarize(ch0), binarize(ch1)
        lzc_ch0 = lzc_from_binary(b0)
        lzc_ch1 = lzc_from_binary(b1)
        lzc_concat = lzc_from_binary(np.concatenate([b0, b1]))

        exp0 = aperiodic_exponent(ch0, sfreq)
        exp1 = aperiodic_exponent(ch1, sfreq)
        valid_exps = [e for e in (exp0, exp1) if e is not None]
        if not valid_exps:
            continue
        exponent_mean = float(np.mean(valid_exps))

        rows.append({
            "subject": subject_id,
            "stage": stage,
            "lzc_mean_channels": float(np.mean([lzc_ch0, lzc_ch1])),
            "lzc_multivariado": lzc_concat,
            "exponent_1f": exponent_mean,
        })
    return pd.DataFrame(rows)


def residualize_insample(metric: np.ndarray, covariate: np.ndarray) -> np.ndarray:
    X = covariate.reshape(-1, 1)
    reg = LinearRegression().fit(X, metric)
    return metric - reg.predict(X)


def residualize_out_of_sample(df: pd.DataFrame, metric_col: str, covariate_col: str,
                               subject_col: str, n_folds: int, rng: np.random.Generator) -> pd.Series:
    """Regressao metric~covariate treinada por FOLD DE SUJEITOS (nao de epocas) e
    aplicada aos sujeitos do fold de teste -- evita que o ajuste "veja" os proprios
    dados que esta corrigindo (o "protocolo VNext" nomeado no Cap. 11).

    IMPORTANTE: `df` deve vir PRE-FILTRADO para as duas classes comparadas (W/N3) antes
    de chamar esta funcao -- ajustar a regressao com epocas de N1/N2/REM misturadas
    (como uma versao anterior deste script fazia por engano) produz um numero que nao e
    comparavel ao estimando ja estabelecido em `reforco_estatistico.py`, que residualiza
    so dentro do contraste sendo testado."""
    subjects = df[subject_col].unique()
    rng.shuffle(subjects)
    kf = KFold(n_splits=min(n_folds, len(subjects)), shuffle=False)
    resid = pd.Series(index=df.index, dtype=float)
    for train_idx, test_idx in kf.split(subjects):
        train_subjects = set(subjects[train_idx])
        test_subjects = set(subjects[test_idx])
        train_mask = df[subject_col].isin(train_subjects)
        test_mask = df[subject_col].isin(test_subjects)
        train_sub = df.loc[train_mask].dropna(subset=[metric_col, covariate_col])
        if len(train_sub) < 10:
            continue
        reg = LinearRegression().fit(train_sub[[covariate_col]].values, train_sub[metric_col].values)
        test_sub = df.loc[test_mask].dropna(subset=[metric_col, covariate_col])
        pred = reg.predict(test_sub[[covariate_col]].values)
        resid.loc[test_sub.index] = test_sub[metric_col].values - pred
    return resid


def cluster_bootstrap_auc(df, subject_col, state_col, score_col, state_a, state_b, positive,
                           n_boot=2000, rng=None):
    """Copiado de scripts_para_rodar/estatistica/reforco_estatistico.py para manter este
    script autocontido (mesma logica, mesma justificativa: bootstrap por SUJEITO, nao por
    epoca, porque epocas do mesmo sujeito sao correlacionadas -- pseudo-replicacao)."""
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
                "p_valor_bootstrap": None, "n_boot_validos": len(boots), "n_sujeitos": len(subjects)}
    boots = np.array(boots)
    ic_low, ic_high = np.percentile(boots, [2.5, 97.5])
    frac_below = float(np.mean(boots <= 0.5))
    frac_above = float(np.mean(boots >= 0.5))
    p_boot = float(min(1.0, 2 * min(frac_below, frac_above)))
    return {"auc": point, "ic95_low": float(ic_low), "ic95_high": float(ic_high),
            "p_valor_bootstrap": p_boot, "n_boot_validos": len(boots), "n_sujeitos": len(subjects)}


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


def auc_naive(df: pd.DataFrame, col: str) -> float | None:
    sub = df[df["stage"].isin(["W", "N3"])].dropna(subset=[col])
    if sub["stage"].nunique() < 2 or len(sub) < 4:
        return None
    y = (sub["stage"] == "W").astype(int).values
    return float(roc_auc_score(y, sub[col].values))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-subjects", type=int, default=41)
    ap.add_argument("--data-dir", type=str, required=True)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--n-folds", type=int, default=5)
    args = ap.parse_args()
    rng = np.random.default_rng(20260811)

    subjects = list(range(args.n_subjects))
    paths = mne.datasets.sleep_physionet.age.fetch_data(
        subjects=subjects, recording=[1], path=args.data_dir, on_missing="warn"
    )
    known_missing = {39, 68, 69, 78, 79}
    fetched_subject_ids = [s for s in subjects if s not in known_missing][: len(paths)]

    all_epochs, processed, failed = [], [], []
    for subj_id, (psg_path, hyp_path) in zip(fetched_subject_ids, paths):
        try:
            df = process_subject(psg_path, hyp_path, subj_id)
            all_epochs.append(df)
            processed.append(subj_id)
            print(f"[ok] sujeito {subj_id}: {len(df)} epocas")
        except Exception as e:
            failed.append((subj_id, str(e)))
            print(f"[ERRO] sujeito {subj_id}: {e}")

    if not all_epochs:
        raise RuntimeError("Nenhum sujeito processado com sucesso.")

    epochs_df = pd.concat(all_epochs, ignore_index=True)
    epochs_df.to_csv(HERE / "lzc_multivariado_por_epoca.csv", index=False)
    print(f"\nTotal: {len(processed)} sujeitos, {len(epochs_df)} epocas com 1/f valido")

    results = []
    pvals_for_fdr = []

    for metric_col, metric_label in [("lzc_mean_channels", "LZc média por canal (comparador já existente)"),
                                      ("lzc_multivariado", "LZc multivariada (concatenação binária dos 2 canais)")]:
        # Ajuste da regressao metric~exponent_1f restrito a W/N3 (as duas classes
        # comparadas), mesma convencao ja estabelecida em reforco_estatistico.py -- usar
        # todas as 5 fases (como uma versao anterior deste script fazia) produz um
        # numero maior e NAO comparavel ao ja publicado no Cap. 11 e em
        # reforco_estatistico_resultados.csv.
        wn3 = epochs_df[epochs_df["stage"].isin(["N3", "W"])]

        # 1. AUC ingenua (epoca-pooled), bruta e residualizada in-sample
        auc_raw = auc_naive(epochs_df, metric_col)
        sub_resid = wn3.dropna(subset=[metric_col, "exponent_1f"]).copy()
        sub_resid["resid_insample"] = residualize_insample(sub_resid[metric_col].values, sub_resid["exponent_1f"].values)
        tmp = sub_resid.copy()
        tmp["_tmp"] = tmp["resid_insample"]
        auc_resid_insample_naive = auc_naive(tmp, "_tmp")

        # 2. Bootstrap por sujeito (bruta e residualizada in-sample)
        boot_raw = cluster_bootstrap_auc(epochs_df, "subject", "stage", metric_col, "N3", "W",
                                          positive="W", n_boot=args.n_boot, rng=rng)
        boot_resid_insample = cluster_bootstrap_auc(tmp, "subject", "stage", "_tmp", "N3", "W",
                                                      positive="W", n_boot=args.n_boot, rng=rng)

        # 3. Residualizacao OUT-OF-SAMPLE (K-fold por sujeito, so dentro de W/N3) + bootstrap por sujeito
        oos_resid = residualize_out_of_sample(wn3, metric_col, "exponent_1f", "subject",
                                               args.n_folds, rng)
        oos_df = wn3.copy()
        oos_df["_resid_oos"] = oos_resid
        oos_df = oos_df.dropna(subset=["_resid_oos"])
        boot_oos = cluster_bootstrap_auc(oos_df, "subject", "stage", "_resid_oos", "N3", "W",
                                          positive="W", n_boot=args.n_boot, rng=rng)

        for tipo, r, auc_naive_val in [
            ("bruta", boot_raw, auc_raw),
            ("residualizada_1f_in_sample", boot_resid_insample, auc_resid_insample_naive),
            (f"residualizada_1f_out_of_sample_{args.n_folds}fold", boot_oos, None),
        ]:
            row = {"metrica": metric_col, "descricao": metric_label, "tipo": tipo,
                   "auc_epoca_pooled_ingenua": auc_naive_val,
                   "auc_bootstrap_sujeito": r["auc"] if r else None,
                   "ic95_low": r["ic95_low"] if r else None,
                   "ic95_high": r["ic95_high"] if r else None,
                   "p_valor_bootstrap": r["p_valor_bootstrap"] if r else None,
                   "n_sujeitos": r["n_sujeitos"] if r else None}
            results.append(row)
            if r and r["p_valor_bootstrap"] is not None:
                pvals_for_fdr.append(r["p_valor_bootstrap"])

    results_df = pd.DataFrame(results)
    all_p = [r["p_valor_bootstrap"] for r in results]
    results_df["p_valor_fdr_bh"] = benjamini_hochberg(all_p)
    results_df.to_csv(HERE / "auc_comparativo_multivariado.csv", index=False)
    print("\n=== AUC comparativo (ingênua vs. bootstrap por sujeito vs. out-of-sample) ===")
    print(results_df.to_string(index=False))

    resumo = f"""# LZc multivariada (2 canais) — resumo (gerado automaticamente, a interpretar depois)

Recomendação 3 do parecer de neurociência (`pareceres_especialistas/neurociencia.md`):
testar um índice de complexidade genuinamente multivariado (concatenação binária dos
2 canais, não LZc por canal seguida de média) antes de fechar a conclusão negativa sobre
"integração diferenciada" no sono.

Sujeitos solicitados: 0-{args.n_subjects - 1} | processados com sucesso: {len(processed)}
IDs processados: {processed}
Falhas: {failed if failed else 'nenhuma'}
Total de épocas com 1/f válido: {len(epochs_df)}

## Tabela completa
{results_df.to_string(index=False)}

## Como ler

- **auc_epoca_pooled_ingenua**: trata cada época como observação independente — superestima
  a precisão (mesma ressalva já registrada no Cap. 11 para a análise original). Reportado
  só para comparabilidade com os relatórios anteriores do projeto.
- **auc_bootstrap_sujeito**: a estimativa correta para inferência — reamostra sujeitos
  inteiros (n={len(processed)}), não épocas. É esta, não a ingênua, que decide o resultado.
- **bruta**: LZc sem nenhum controle por 1/f.
- **residualizada_1f_in_sample**: mesmo procedimento já usado em `integracao_diferenciada_1f.py`
  (regressão metric~exponent_1f ajustada nos mesmos dados que está corrigindo).
- **residualizada_1f_out_of_sample_Nfold**: regressão treinada em sujeitos de treino e
  aplicada a sujeitos de teste nunca vistos pelo ajuste (K-fold por sujeito) — o teste mais
  limpo, e o que o Cap. 11 do manuscrito já nomeia como "protocolo VNext" ainda em aberto.

## Leitura (preencher/revisar após rodar — não inventar conclusão aqui)

- Se `lzc_multivariado` (bootstrap por sujeito, residualizada out-of-sample) tiver IC95%
  excluindo 0,5 e p_valor_fdr_bh < 0,05, a complexidade multivariada sobrevive ao controle
  por 1/f mesmo fora da amostra — evidência real de estrutura conjunta entre os 2 canais
  além do confundidor espectral, e o Cap. 11 deveria ser atualizado para refletir isso.
- Se cair para perto de 0,5 (como já aconteceu com `lzc_mean_channels` e com o índice de
  integração×diferenciação de `integracao_diferenciada_1f.py`), isso reforça — com um teste
  ainda mais rigoroso (multivariado de verdade, out-of-sample) — a leitura já registrada no
  Cap. 11: o achado bruto de complexidade por estágio de sono permanece robusto, mas não
  resiste, em nenhuma operacionalização tentada até agora, como evidência específica de
  integração diferenciada acima do confundidor espectral.
- Comparar `lzc_multivariado` bruto com `lzc_mean_channels` bruto: se a versão multivariada
  discriminar sensivelmente melhor mesmo antes do controle por 1/f, isso já seria um
  resultado interessante por si (capturar estrutura conjunta que a média por canal
  descarta), independente do que aconteça depois do controle.
"""
    (HERE / "resumo_lzc_multivariado.md").write_text(resumo, encoding="utf-8")
    print("\nProcessamento concluído. Saídas em:", HERE)


if __name__ == "__main__":
    main()
