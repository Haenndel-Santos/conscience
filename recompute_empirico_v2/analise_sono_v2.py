"""Recompute empirico V2 - Sleep-EDF, amostra ampliada + segunda metrica.

Estende `recompute_empirico_sleepedf/analise_lzc_sleepedf.py` (nao o
sobrescreve - saidas ficam em pasta separada):

1. Amostra bem maior de sujeitos do Sleep-EDF Cassette (default: todos os
   validos ate --n-subjects, tipicamente ~40).
2. Segunda metrica INDEPENDENTE: entropia de permutacao normalizada
   (Bandt & Pompe, Physical Review Letters, 88, 174102, 2002 - verificada
   nesta sessao via busca web e via docstring/citacao da biblioteca
   antropy), calculada com `antropy.perm_entropy(order=3, normalize=True)`,
   ao lado da LZc ja usada na v1 (`antropy.lziv_complexity`).

Protocolo: _revisao_2026-08-05/confronto_empirico.md, Parte 4.

Uso:
    python analise_sono_v2.py --n-subjects 40 --data-dir <pasta_cache>
"""
from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import antropy as ant
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

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
STAGE_ORDER = ["W", "REM", "N1", "N2", "N3"]


def lzc_epoch(x: np.ndarray) -> float:
    b = (x >= np.median(x)).astype(np.uint8)
    return float(ant.lziv_complexity(b, normalize=True))


def pe_epoch(x: np.ndarray) -> float:
    return float(ant.perm_entropy(x, order=3, delay=1, normalize=True))


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
    # (gatilho/anotacao, nao sinal cerebral -- valores na faixa ~900-1000, escala
    # incompativel com EEG real) como tipo "eeg" em todo o Sleep-EDF Cassette. Sem este
    # filtro, ele entrava na media de lzc/pe junto dos 2 canais reais em 100% das
    # epocas de todos os sujeitos ja processados, distorcendo lzc e (por downstream)
    # qualquer analise que dependa dele. Restringe explicitamente ao whitelist dos 2
    # canais EEG reais deste dataset, independente do que infer_types rotulou.
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
    data = epochs.get_data()
    labels = epochs.events[:, 2]

    rows = []
    for i in range(data.shape[0]):
        stage = inv_event_id[labels[i]]
        lzc_per_ch = [lzc_epoch(data[i, ch, :]) for ch in range(data.shape[1])]
        pe_per_ch = [pe_epoch(data[i, ch, :]) for ch in range(data.shape[1])]
        rows.append({
            "subject": subject_id, "stage": stage,
            "lzc": float(np.mean(lzc_per_ch)),
            "pe": float(np.mean(pe_per_ch)),
        })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-subjects", type=int, default=41, help="Indice maximo (exclusivo) de sujeitos a tentar; alguns indices sao ausentes no dataset")
    ap.add_argument("--data-dir", type=str, required=True)
    args = ap.parse_args()

    subjects = list(range(args.n_subjects))
    paths = mne.datasets.sleep_physionet.age.fetch_data(
        subjects=subjects, recording=[1], path=args.data_dir, on_missing="warn"
    )
    fetched_subject_ids = [s for s in subjects if s not in (39, 68, 69, 78, 79)][: len(paths)]

    all_epochs = []
    processed, failed = [], []
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
        raise RuntimeError("Nenhum sujeito processado.")

    epochs_df = pd.concat(all_epochs, ignore_index=True)
    epochs_df.to_csv(HERE / "sleepedf_por_epoca.csv", index=False)

    by_stage = epochs_df.groupby("stage")[["lzc", "pe"]].agg(["mean", "std", "count"]).reindex(STAGE_ORDER)
    by_stage.to_csv(HERE / "sleepedf_por_estagio.csv")
    print("\n=== LZc e PE medios por estagio ===")
    print(by_stage)

    # Concordancia entre metricas: ordenacao (Spearman entre as medias por
    # estagio) e correlacao epoca-a-epoca.
    order_lzc = by_stage[("lzc", "mean")].rank(ascending=False)
    order_pe = by_stage[("pe", "mean")].rank(ascending=False)
    rank_corr = spearmanr(order_lzc, order_pe).statistic
    epoch_corr = spearmanr(epochs_df["lzc"], epochs_df["pe"]).statistic

    # AUC W-vs-N3 para as duas metricas
    sub = epochs_df[epochs_df["stage"].isin(["W", "N3"])]
    y = (sub["stage"] == "W").astype(int).values
    auc_lzc = roc_auc_score(y, sub["lzc"].values)
    auc_pe = roc_auc_score(y, sub["pe"].values)

    n_subjects_total = len(processed)
    summary_text = (
        f"=== Recompute empirico V2 - Sleep-EDF ampliado ===\n"
        f"Sujeitos solicitados: 0-{args.n_subjects - 1} | processados com sucesso: {n_subjects_total}\n"
        f"IDs processados: {processed}\n"
        f"Falhas: {failed if failed else 'nenhuma'}\n"
        f"Total de epocas: {len(epochs_df)}\n\n"
        f"Ordenacao por LZc (maior->menor): {list(by_stage[('lzc','mean')].sort_values(ascending=False).index)}\n"
        f"Ordenacao por PE  (maior->menor): {list(by_stage[('pe','mean')].sort_values(ascending=False).index)}\n"
        f"Correlacao de Spearman entre as ordenacoes por estagio: {rank_corr:.4f}\n"
        f"Correlacao de Spearman epoca-a-epoca (LZc vs PE, todas as epocas): {epoch_corr:.4f}\n\n"
        f"AUC W-vs-N3 (LZc): {auc_lzc:.4f}\n"
        f"AUC W-vs-N3 (PE):  {auc_pe:.4f}\n"
    )
    (HERE / "sleepedf_resumo.txt").write_text(summary_text, encoding="utf-8")
    print("\n" + summary_text)

    # Figura: LZc e PE por estagio, lado a lado
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for ax, metric, title in zip(axes, ["lzc", "pe"], ["Lempel-Ziv complexity (LZc)", "Entropia de permutação (PE, ordem 3)"]):
        box_data = [epochs_df.loc[epochs_df["stage"] == s, metric].dropna().values for s in STAGE_ORDER]
        ax.boxplot(box_data, tick_labels=STAGE_ORDER, showmeans=True)
        ax.set_title(title)
        ax.set_ylabel(metric.upper())
    fig.suptitle(f"Sleep-EDF ampliado (n={n_subjects_total} sujeitos, {len(epochs_df)} épocas) — LZc vs. entropia de permutação por estágio")
    fig.tight_layout()
    fig.savefig(HERE / "sleepedf_lzc_pe_por_estagio.png", dpi=160)
    plt.close(fig)

    return {"by_stage": by_stage, "rank_corr": rank_corr, "epoch_corr": epoch_corr, "auc_lzc": auc_lzc, "auc_pe": auc_pe, "n_subjects": n_subjects_total}


if __name__ == "__main__":
    main()
