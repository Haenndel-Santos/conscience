"""Teste diferencial do REM: complexidade EEG interna vs. desacoplamento cortico-muscular.

O Cap. 11 (secao Sonho) preve que, no REM, C(t) permanece alto em componentes internos
enquanto ME(t) -- acoplamento cerebro-ambiente -- cai, e ja nomeia isso como "predicao
diferencial que fica registrada como programa, nao como resultado ja obtido", porque
testa-la de verdade exige separar complexidade interna de acoplamento externo, nao so
medir complexidade agregada.

IMPORTANTE -- o que este script testa, e o que NAO testa: o Sleep-EDF Cassette nao tem
nenhum sensor de estimulo ambiental (nao ha paradigma de estimulacao auditiva ou
equivalente nestes dados) -- entao ME(t) no sentido literal (acoplamento cerebro-
AMBIENTE, responsividade a estimulo externo) nao pode ser testado com este dataset. O
que ESTA disponivel, e que este script de fato testa, e um proxy relacionado mas
distinto: acoplamento CORTICO-MUSCULAR (EEG-EMG), usando o canal 'submental' (EMG) ja
presente nos mesmos arquivos EDF. A atonia muscular do REM (supressao quase completa do
tono muscular, achado classico e bem estabelecido da polissonografia) e uma forma real
de desacoplamento entre o cerebro e a capacidade de agir sobre/no ambiente -- relacionada
ao que a teoria chama de externamente desacoplado, mas NAO iddentica a ME(t) tal como
definida no Cap. 13 (acoplamento cerebro-ambiente, nao cerebro-musculo). Reportar os
resultados como teste desse proxy especifico, nao como teste direto e completo da
predicao ME(t) do capitulo.

Este script:
  1. Reprocessa os mesmos arquivos do Sleep-EDF Cassette ja em cache (mesmo pipeline
     corrigido de `analise_sono_v2.py` -- 2 canais EEG reais, sem o canal 'Event marker'
     contaminado), agora tambem extraindo o canal EMG submental.
  2. Por epoca: LZc media dos 2 canais EEG (ja calculada em rodadas anteriores, recalculada
     aqui para alinhamento exato), amplitude RMS do EMG (marcador classico de atonia), e
     coerencia espectral EEG-EMG na banda 1-40 Hz (proxy de acoplamento cortico-muscular).
  3. Testa se REM tem o padrao previsto: LZc alta (ja confirmada em rodadas anteriores),
     RMS de EMG mais baixo que todos os outros estagios (atonia), e coerencia EEG-EMG mais
     baixa que vigilia -- com bootstrap por sujeito e correcao FDR sobre os testes
     coletados (mesma disciplina estatistica ja aplicada ao resto do projeto).
  4. Define um indice de "descaoplamento" = rank(LZc) - rank(RMS_EMG) por epoca, testando
     se REM tem o maior valor medio desse indice entre os 5 estagios -- e a
     operacionalizacao mais direta disponivel da predicao "internamente rico,
     externamente desacoplado".

Uso:
    python rem_complexidade_vs_emg.py --n-subjects 41 --data-dir <mesma pasta .cache_sleepedf ja usada>

Saidas (nesta pasta):
    rem_desacoplamento_por_epoca.csv   - LZc, RMS EMG, coerencia EEG-EMG, por epoca
    rem_desacoplamento_por_estagio.csv - medias por estagio
    testes_rem_desacoplamento.csv      - bootstrap por sujeito (REM vs. cada outro estagio)
                                          para RMS EMG, coerencia, e indice de desacoplamento
    resumo_rem_desacoplamento.md       - relatorio narrativo (a interpretar depois)
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
from sklearn.metrics import roc_auc_score

mne.set_log_level("ERROR")
warnings.filterwarnings("ignore")

HERE = Path(__file__).parent

ANNOTATION_TO_EVENT = {
    "Sleep stage W": 1, "Sleep stage 1": 2, "Sleep stage 2": 3,
    "Sleep stage 3": 4, "Sleep stage 4": 4, "Sleep stage R": 5,
}
EVENT_ID = {"W": 1, "N1": 2, "N2": 3, "N3": 4, "REM": 5}
STAGE_ORDER = ["W", "REM", "N1", "N2", "N3"]
COHERENCE_BAND = (1.0, 40.0)


def lzc_epoch(x: np.ndarray) -> float:
    b = (x >= np.median(x)).astype(np.uint8)
    return float(ant.lziv_complexity(b, normalize=True))


def emg_rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x ** 2)))


def eeg_emg_coherence(eeg: np.ndarray, emg: np.ndarray, sfreq: float) -> float:
    nperseg = min(len(eeg), int(sfreq * 4))
    if nperseg < int(sfreq * 2):
        return float("nan")
    freqs, cxy = signal.coherence(eeg, emg, fs=sfreq, nperseg=nperseg, noverlap=nperseg // 2)
    band = (freqs >= COHERENCE_BAND[0]) & (freqs <= COHERENCE_BAND[1])
    if not np.any(band):
        return float("nan")
    return float(np.mean(cxy[band]))


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
    eeg_picks = [ch for ch in eeg_picks if ch in ("Fpz-Cz", "Pz-Oz")]
    if not eeg_picks:
        eeg_picks = [ch for ch in raw.ch_names if ch in ("Fpz-Cz", "Pz-Oz")]
    emg_picks = [ch for ch in raw.ch_names if "submental" in ch.lower() or "emg" in ch.lower()]
    if not eeg_picks or not emg_picks:
        raise RuntimeError(f"Faltam canais em {psg_path}: eeg={eeg_picks}, emg={emg_picks}")

    all_picks = eeg_picks + emg_picks
    raw.pick(all_picks)
    raw.filter(0.5, 40.0, picks=eeg_picks, fir_design="firwin", verbose=False)
    # BUGFIX (2026-08-12): Sleep-EDF Cassette amostra a 100 Hz (Nyquist=50 Hz) -- a banda
    # EMG classica (ate ~100-500 Hz) nao cabe aqui. Usa a maior banda disponivel dentro do
    # limite (10-45 Hz) como proxy de atividade muscular; menos informativo que um registro
    # EMG dedicado de alta taxa de amostragem, mas ainda deve capturar tono muscular geral.
    nyquist = raw.info["sfreq"] / 2.0
    emg_high = min(45.0, nyquist - 1.0)
    raw.filter(10.0, emg_high, picks=emg_picks, fir_design="firwin", verbose=False,
               l_trans_bandwidth="auto", h_trans_bandwidth="auto")

    events, _ = mne.events_from_annotations(raw, event_id=ANNOTATION_TO_EVENT, chunk_duration=30.0, verbose=False)
    tmax = 30.0 - 1.0 / raw.info["sfreq"]
    epochs = mne.Epochs(raw=raw, events=events, event_id=EVENT_ID, tmin=0.0, tmax=tmax, baseline=None, preload=True, verbose=False)

    inv_event_id = {v: k for k, v in EVENT_ID.items()}
    data = epochs.get_data(picks=eeg_picks)
    emg_data = epochs.get_data(picks=emg_picks)[:, 0, :]
    labels = epochs.events[:, 2]
    sfreq = float(raw.info["sfreq"])

    rows = []
    for i in range(data.shape[0]):
        stage = inv_event_id[labels[i]]
        lzc_vals = [lzc_epoch(data[i, ch, :]) for ch in range(data.shape[1])]
        emg_x = emg_data[i, :]
        coh_vals = [eeg_emg_coherence(data[i, ch, :], emg_x, sfreq) for ch in range(data.shape[1])]
        rows.append({
            "subject": subject_id, "stage": stage,
            "lzc": float(np.mean(lzc_vals)),
            "emg_rms": emg_rms(emg_x),
            "eeg_emg_coherence": float(np.nanmean(coh_vals)),
        })
    return pd.DataFrame(rows)


def cluster_bootstrap_auc(df, subject_col, state_col, score_col, state_a, state_b, positive,
                           n_boot=2000, rng=None):
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
    ap.add_argument("--n-subjects", type=int, default=41)
    ap.add_argument("--data-dir", type=str, required=True)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    rng = np.random.default_rng(20260812)

    subjects = list(range(args.n_subjects))
    paths = mne.datasets.sleep_physionet.age.fetch_data(subjects=subjects, recording=[1], path=args.data_dir, on_missing="warn")
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
    epochs_df.to_csv(HERE / "rem_desacoplamento_por_epoca.csv", index=False)

    # indice de desacoplamento: rank percentual de LZc menos rank percentual de EMG RMS,
    # calculado dentro de cada sujeito (para nao deixar diferencas de escala entre sujeitos
    # dominarem o rank global)
    epochs_df["lzc_rank"] = epochs_df.groupby("subject")["lzc"].rank(pct=True)
    epochs_df["emg_rank"] = epochs_df.groupby("subject")["emg_rms"].rank(pct=True)
    epochs_df["indice_desacoplamento"] = epochs_df["lzc_rank"] - epochs_df["emg_rank"]

    by_stage = epochs_df.groupby("stage")[["lzc", "emg_rms", "eeg_emg_coherence", "indice_desacoplamento"]].agg(["mean", "std", "count"]).reindex(STAGE_ORDER)
    by_stage.to_csv(HERE / "rem_desacoplamento_por_estagio.csv")
    print("\n=== Médias por estágio ===")
    print(by_stage)

    print("\n=== Testes: REM vs. cada outro estágio, bootstrap por sujeito ===")
    test_rows = []
    for metric in ["emg_rms", "eeg_emg_coherence", "indice_desacoplamento"]:
        for other_stage in ["W", "N1", "N2", "N3"]:
            r = cluster_bootstrap_auc(epochs_df, "subject", "stage", metric, other_stage, "REM",
                                       positive="REM", n_boot=args.n_boot, rng=rng)
            if r:
                test_rows.append({"metrica": metric, "comparacao": f"REM vs {other_stage}",
                                   "auc": r["auc"], "ic95_low": r["ic95_low"], "ic95_high": r["ic95_high"],
                                   "p_valor_bootstrap": r["p_valor_bootstrap"], "n_sujeitos": r["n_sujeitos"]})
    test_df = pd.DataFrame(test_rows)
    test_df["p_valor_fdr_bh"] = benjamini_hochberg(test_df["p_valor_bootstrap"].values)
    test_df.to_csv(HERE / "testes_rem_desacoplamento.csv", index=False)
    print(test_df.to_string(index=False))

    resumo = f"""# REM: complexidade interna vs. desacoplamento cortico-muscular (gerado automaticamente)

ATENÇÃO: este script testa acoplamento EEG-EMG (cortico-muscular), um proxy relacionado
mas DISTINTO de ME(t) tal como definida no Cap. 13 (acoplamento cérebro-AMBIENTE). O
Sleep-EDF Cassette não tem sensor de estímulo ambiental — ME(t) literal não é testável
com este dataset. Ler os resultados abaixo como teste desse proxy específico (atonia
muscular durante REM), não como confirmação direta da predição ME(t) do capítulo.

Sujeitos: {len(processed)} processados, {len(epochs_df)} épocas. Falhas: {failed if failed else 'nenhuma'}.

## Médias por estágio
{by_stage.to_string()}

## Testes (REM vs. cada outro estágio, bootstrap por sujeito, FDR)
{test_df.to_string(index=False)}

## Como ler (preencher depois — não inventar conclusão aqui)
- Se `emg_rms` for menor em REM que em W/N1/N2/N3 (AUC<0,5 favorecendo REM como "menor"),
  isso replica a atonia muscular do REM — achado clássico e esperado da polissonografia,
  não uma novidade teórica por si, mas a base sobre a qual o índice de desacoplamento
  é construído.
- O teste mais diretamente relevante à predição do Cap. 11 é `indice_desacoplamento`: se
  for consistentemente MAIOR em REM que nos outros 4 estágios (LZc alta relativa + EMG
  baixo relativo, dentro do mesmo sujeito), isso é evidência a favor da leitura
  "internamente rico, externamente desacoplado" — na forma operacionalizável disponível
  com este dataset (cortico-muscular, não cortico-ambiental).
- Se REM não se distinguir dos outros estágios nesse índice, é um resultado negativo
  válido para esta operacionalização específica — não decide a predição ME(t) original,
  que continua exigindo um dataset com estímulo ambiental registrado para ser testada
  de verdade.
"""
    (HERE / "resumo_rem_desacoplamento.md").write_text(resumo, encoding="utf-8")
    print("\nProcessamento concluído. Saídas em:", HERE)


if __name__ == "__main__":
    main()
