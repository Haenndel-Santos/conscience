"""Recompute empirico V2 - extremo de anestesia (propofol, Cambridge/Chennu).

Dataset: "Brain connectivity during propofol sedation" (Chennu, O'Connor,
Adapa, Menon, Bekinschtein - PLOS Computational Biology, 2016,
DOI 10.1371/journal.pcbi.1004669 - verificado nesta sessao via busca web).
Dados abertos (CC BY 2.0 UK): repository.cam.ac.uk/handle/1810/252736.

20 sujeitos saudaveis, EEG de 91 canais (250 Hz), 4 estados por sujeito:
basal, sedacao leve, sedacao moderada, recuperacao (~7 min cada, ja
pre-segmentados pelos autores originais em epocas de ~10s, artefato
removido, referenciado a media dos canais). O mapeamento arquivo->estado
vem de `datainfo.mat` (coluna 2 = codigo de estado 1-4, verificado nesta
sessao: 20 sujeitos x 4 estados = 80 arquivos .set, um de cada codigo por
sujeito, sem excecao).

Metricas: LZc (Lempel-Ziv, antropy.lziv_complexity) e entropia de
permutacao (Bandt & Pompe 2002, antropy.perm_entropy, ordem 3), as mesmas
duas metricas de `analise_sono_v2.py`, calculadas por canal e por epoca
"pre-fabricada" (~10s), depois medias entre os 91 canais.

Uso:
    python analise_anestesia_propofol.py --data-dir <pasta_extraida> [--max-subjects N]
"""
from __future__ import annotations

import argparse
import re
import warnings
from pathlib import Path

import antropy as ant
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd
from pymatreader import read_mat
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

mne.set_log_level("ERROR")
warnings.filterwarnings("ignore")

HERE = Path(__file__).parent

STATE_LABELS = {1: "basal", 2: "sedacao_leve", 3: "sedacao_moderada", 4: "recuperacao"}
STATE_ORDER = ["basal", "sedacao_leve", "sedacao_moderada", "recuperacao"]


def lzc_epoch(x: np.ndarray) -> float:
    b = (x >= np.median(x)).astype(np.uint8)
    return float(ant.lziv_complexity(b, normalize=True))


def load_state_map(data_dir: Path) -> dict[str, str]:
    """filename (sem extensao) -> label de estado, a partir de datainfo.mat."""
    mat_path = data_dir / "datainfo.mat"
    d = read_mat(str(mat_path))
    mapping = {}
    for row in d["datainfo"]:
        fname, code = row[0], int(row[1])
        mapping[fname] = STATE_LABELS[code]
    return mapping


def process_file(set_path: Path, subject_id: str, state: str) -> pd.DataFrame:
    epochs = mne.io.read_epochs_eeglab(str(set_path), verbose=False)
    data = epochs.get_data()  # (n_epochs, n_channels, n_times)
    n_epochs, n_channels, n_times = data.shape

    # PE: caminho vetorizado do antropy p/ ordem 3 aceita (n_epochs, n_times)
    # de uma vez por canal - muito mais rapido que looping epoca a epoca.
    pe_per_epoch_channel = np.zeros((n_epochs, n_channels))
    for ch in range(n_channels):
        pe_per_epoch_channel[:, ch] = ant.perm_entropy(data[:, ch, :], order=3, normalize=True)
    pe_per_epoch = pe_per_epoch_channel.mean(axis=1)

    # LZc: sem caminho vetorizado no antropy - looping epoca x canal.
    lzc_per_epoch = np.zeros(n_epochs)
    for e in range(n_epochs):
        lzc_vals = [lzc_epoch(data[e, ch, :]) for ch in range(n_channels)]
        lzc_per_epoch[e] = float(np.mean(lzc_vals))

    return pd.DataFrame({
        "subject": subject_id, "state": state,
        "epoch": np.arange(n_epochs),
        "lzc": lzc_per_epoch, "pe": pe_per_epoch,
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=str, required=True, help="Pasta 'Sedation-RestingState' extraida")
    ap.add_argument("--max-subjects", type=int, default=None, help="Limitar numero de sujeitos (para teste rapido)")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    state_map = load_state_map(data_dir)

    set_files = sorted(data_dir.glob("*.set"))
    if not set_files:
        raise RuntimeError(f"Nenhum .set encontrado em {data_dir}")

    subjects_seen = []
    all_rows = []
    failed = []
    for f in set_files:
        stem = f.stem
        subject_id = re.match(r"(\d+)", stem).group(1)
        if args.max_subjects is not None and subject_id not in subjects_seen and len(subjects_seen) >= args.max_subjects:
            continue
        if subject_id not in subjects_seen:
            subjects_seen.append(subject_id)
        state = state_map.get(stem)
        if state is None:
            print(f"[AVISO] sem estado mapeado para {stem}, pulando")
            continue
        try:
            df = process_file(f, subject_id, state)
            all_rows.append(df)
            print(f"[ok] sujeito {subject_id} / {state}: {len(df)} epocas ({f.name})")
        except Exception as e:
            failed.append((f.name, str(e)))
            print(f"[ERRO] {f.name}: {e}")

    if not all_rows:
        raise RuntimeError("Nenhum arquivo processado com sucesso.")

    epochs_df = pd.concat(all_rows, ignore_index=True)
    epochs_df.to_csv(HERE / "propofol_por_epoca.csv", index=False)

    by_state = epochs_df.groupby("state")[["lzc", "pe"]].agg(["mean", "std", "count"]).reindex(STATE_ORDER)
    by_state.to_csv(HERE / "propofol_por_estado.csv")
    print("\n=== LZc e PE medios por estado (propofol) ===")
    print(by_state)

    order_lzc = by_state[("lzc", "mean")].rank(ascending=False)
    order_pe = by_state[("pe", "mean")].rank(ascending=False)
    rank_corr = spearmanr(order_lzc, order_pe).statistic

    sub = epochs_df[epochs_df["state"].isin(["basal", "sedacao_moderada"])]
    y = (sub["state"] == "basal").astype(int).values
    auc_lzc = roc_auc_score(y, sub["lzc"].values)
    auc_pe = roc_auc_score(y, sub["pe"].values)

    n_subjects = epochs_df["subject"].nunique()
    summary = (
        f"=== Recompute empirico V2 - Propofol (Cambridge/Chennu) ===\n"
        f"Sujeitos processados: {n_subjects} (de 20 no dataset)\n"
        f"Arquivos com falha: {failed if failed else 'nenhum'}\n"
        f"Total de epocas: {len(epochs_df)}\n\n"
        f"Ordenacao por LZc (maior->menor): {list(by_state[('lzc','mean')].sort_values(ascending=False).index)}\n"
        f"Ordenacao por PE  (maior->menor): {list(by_state[('pe','mean')].sort_values(ascending=False).index)}\n"
        f"Correlacao de Spearman entre ordenacoes por estado: {rank_corr:.4f}\n\n"
        f"AUC basal-vs-sedacao_moderada (LZc): {auc_lzc:.4f}\n"
        f"AUC basal-vs-sedacao_moderada (PE):  {auc_pe:.4f}\n"
    )
    (HERE / "propofol_resumo.txt").write_text(summary, encoding="utf-8")
    print("\n" + summary)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for ax, metric, title in zip(axes, ["lzc", "pe"], ["LZc", "Entropia de permutação (ordem 3)"]):
        box_data = [epochs_df.loc[epochs_df["state"] == s, metric].dropna().values for s in STATE_ORDER]
        ax.boxplot(box_data, tick_labels=["basal", "leve", "moderada", "recup."], showmeans=True)
        ax.set_title(title)
    fig.suptitle(f"Sedação por propofol (n={n_subjects} sujeitos, {len(epochs_df)} épocas) — complexidade por estado")
    fig.tight_layout()
    fig.savefig(HERE / "propofol_lzc_pe_por_estado.png", dpi=160)
    plt.close(fig)

    return {"by_state": by_state, "rank_corr": rank_corr, "auc_lzc": auc_lzc, "auc_pe": auc_pe, "n_subjects": n_subjects}


if __name__ == "__main__":
    main()
