"""Recompute empirico: complexidade de Lempel-Ziv (LZc) por estagio de sono.

Protocolo definido em `_revisao_2026-08-05/confronto_empirico.md` (Parte 4):

1. Dataset: Sleep-EDF Expanded, subset "sleep-cassette" (PhysioNet, ODC-BY,
   sem cadastro), baixado via `mne.datasets.sleep_physionet.age.fetch_data`.
2. Pre-processamento: epocas de 30 s, canais EEG Fpz-Cz e Pz-Oz, filtro
   passa-banda 0.5-40 Hz.
3. Metrica-alvo: Lempel-Ziv complexity (LZc) normalizada por epoca
   (binarizacao por mediana), agregada por estagio (W, REM, N1, N2, N3).
4. Teste da predicao: confirmar a ordenacao W ~ REM > N2 > N3 e reportar
   AUC W-vs-N3.
5. Comparar com a ordenacao do indice C(t) do modelo computacional
   (dados atuais/consciousness_model_v3.py): wake > anxiety > deep_sleep > reflex.

Uso:
    python analise_lzc_sleepedf.py --n-subjects 10 --data-dir <pasta_cache>

Saidas (nesta pasta):
    lzc_por_estagio.csv       - LZc medio/desvio por estagio, todas as epocas
    lzc_por_estagio_sujeito.csv - LZc medio por estagio, por sujeito
    lzc_por_estagio.png       - figura (boxplot LZc por estagio)
    auc_wake_vs_n3.txt        - AUC da tarefa W-vs-N3

IMPORTANTE (honestidade metodologica): este e um confronto de ORDENACAO/
DIRECAO entre o LZc empirico e o indice sintetico C(t) do modelo, nao uma
validacao de valores absolutos - as escalas nao sao comparaveis.
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
from sklearn.metrics import roc_auc_score

mne.set_log_level("ERROR")
warnings.filterwarnings("ignore")

HERE = Path(__file__).parent

# Mapeamento de anotacoes do Sleep-EDF (escore R&K) para eventos de 30 s.
# Estagios 3 e 4 sao fundidos em N3, seguindo a convencao AASM moderna
# (o proprio protocolo em confronto_empirico.md pede W/REM/N1/N2/N3).
ANNOTATION_TO_EVENT = {
    "Sleep stage W": 1,
    "Sleep stage 1": 2,
    "Sleep stage 2": 3,
    "Sleep stage 3": 4,
    "Sleep stage 4": 4,
    "Sleep stage R": 5,
}
EVENT_ID = {
    "W": 1,
    "N1": 2,
    "N2": 3,
    "N3": 4,
    "REM": 5,
}
STAGE_ORDER = ["W", "REM", "N1", "N2", "N3"]


def lzc_epoch(x: np.ndarray) -> float:
    """LZc normalizada de um vetor 1D, binarizado por mediana."""
    b = (x >= np.median(x)).astype(np.uint8)
    return float(ant.lziv_complexity(b, normalize=True))


def process_subject(psg_path: str, hyp_path: str, subject_id: int) -> pd.DataFrame:
    raw = mne.io.read_raw_edf(psg_path, stim_channel="marker", infer_types=True, preload=True)
    annot = mne.read_annotations(hyp_path)
    raw.set_annotations(annot, emit_warning=False)

    # Recorta 30 min de vigilia antes/depois do periodo de sono, seguindo a
    # pratica padrao do tutorial MNE para este dataset (evita horas de
    # gravacao diurna irrelevante dominando a classe "W").
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
        # Fallback: nomes conhecidos do Sleep-EDF quando infer_types nao rotula como eeg.
        eeg_picks = [ch for ch in raw.ch_names if ch in ("Fpz-Cz", "Pz-Oz")]
    if not eeg_picks:
        raise RuntimeError(f"Nenhum canal EEG encontrado em {psg_path}: {list(zip(raw.ch_names, ch_types))}")
    raw.pick(eeg_picks)
    raw.filter(0.5, 40.0, fir_design="firwin", verbose=False)

    events, _ = mne.events_from_annotations(
        raw, event_id=ANNOTATION_TO_EVENT, chunk_duration=30.0, verbose=False
    )
    tmax = 30.0 - 1.0 / raw.info["sfreq"]
    epochs = mne.Epochs(
        raw=raw, events=events, event_id=EVENT_ID, tmin=0.0, tmax=tmax,
        baseline=None, preload=True, verbose=False,
    )

    inv_event_id = {v: k for k, v in EVENT_ID.items()}
    data = epochs.get_data()  # (n_epochs, n_channels, n_times)
    labels = epochs.events[:, 2]

    rows = []
    for i in range(data.shape[0]):
        stage = inv_event_id[labels[i]]
        per_channel_lzc = [lzc_epoch(data[i, ch, :]) for ch in range(data.shape[1])]
        rows.append({
            "subject": subject_id,
            "stage": stage,
            "lzc_mean_channels": float(np.mean(per_channel_lzc)),
            **{f"lzc_{ch_name.replace(' ', '_')}": val for ch_name, val in zip(epochs.ch_names, per_channel_lzc)},
        })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-subjects", type=int, default=10)
    ap.add_argument("--data-dir", type=str, required=True, help="Pasta de cache do mne.datasets (PHYSIONET_SLEEP_PATH)")
    args = ap.parse_args()

    subjects = list(range(args.n_subjects))
    paths = mne.datasets.sleep_physionet.age.fetch_data(
        subjects=subjects, recording=[1], path=args.data_dir
    )

    all_epochs = []
    processed_subjects = []
    for subj_id, (psg_path, hyp_path) in zip(subjects, paths):
        try:
            df = process_subject(psg_path, hyp_path, subj_id)
            all_epochs.append(df)
            processed_subjects.append(subj_id)
            print(f"[ok] sujeito {subj_id}: {len(df)} epocas de 30s")
        except Exception as e:
            print(f"[ERRO] sujeito {subj_id}: {e}")

    if not all_epochs:
        raise RuntimeError("Nenhum sujeito processado com sucesso.")

    epochs_df = pd.concat(all_epochs, ignore_index=True)
    epochs_df.to_csv(HERE / "lzc_por_epoca.csv", index=False)

    # Agregacao por estagio (todas as epocas, todos os sujeitos)
    by_stage = epochs_df.groupby("stage")["lzc_mean_channels"].agg(["mean", "std", "count"]).reindex(STAGE_ORDER)
    by_stage.to_csv(HERE / "lzc_por_estagio.csv")
    print("\n=== LZc medio por estagio (todas as epocas) ===")
    print(by_stage)

    # Agregacao por estagio, por sujeito (para checar consistencia entre sujeitos)
    by_stage_subject = epochs_df.groupby(["subject", "stage"])["lzc_mean_channels"].mean().unstack()
    by_stage_subject = by_stage_subject.reindex(columns=STAGE_ORDER)
    by_stage_subject.to_csv(HERE / "lzc_por_estagio_sujeito.csv")

    # AUC W-vs-N3
    sub = epochs_df[epochs_df["stage"].isin(["W", "N3"])].copy()
    y = (sub["stage"] == "W").astype(int).values
    scores = sub["lzc_mean_channels"].values
    auc = roc_auc_score(y, scores)
    print(f"\nAUC (LZc) para W vs N3: {auc:.4f}")
    (HERE / "auc_wake_vs_n3.txt").write_text(
        f"AUC (LZc medio dos canais EEG) para W vs N3: {auc:.4f}\n"
        f"n_epocas W={int((sub['stage']=='W').sum())}, n_epocas N3={int((sub['stage']=='N3').sum())}\n"
        f"Sujeitos processados: {processed_subjects}\n",
        encoding="utf-8",
    )

    # Ordenacao observada vs predicao
    ordering = by_stage["mean"].sort_values(ascending=False)
    print("\nOrdenacao observada (maior -> menor LZc):", list(ordering.index))

    # Figura
    plt.figure(figsize=(8, 5))
    box_data = [epochs_df.loc[epochs_df["stage"] == s, "lzc_mean_channels"].dropna().values for s in STAGE_ORDER]
    plt.boxplot(box_data, tick_labels=STAGE_ORDER, showmeans=True)
    plt.ylabel("LZc normalizada (media dos canais EEG, por epoca de 30s)")
    plt.title(f"LZc por estagio de sono - Sleep-EDF Cassette (n={len(processed_subjects)} sujeitos)")
    plt.tight_layout()
    plt.savefig(HERE / "lzc_por_estagio.png", dpi=160)
    plt.close()

    print("\nProcessamento concluido. Saidas em:", HERE)


if __name__ == "__main__":
    main()
