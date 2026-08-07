"""Frente C — teste de "integracao diferenciada" com controle de inclinacao espectral (1/f).

Redefinicao de prioridade registrada em `embasamento/SINTESE_pilares.md` (2026-08-06,
achado #1): o resultado mais forte do projeto (ordenacao de LZc/entropia de permutacao
por estagio de sono) tem um confundidor parcial documentado no Bloco L do
`CHECKLIST_pendencias.md` — Hohn, Hahn, Lendner & Hoedlmoser (2024), eNeuro 11(3),
ENEURO.0259-23.2024, DOI 10.1523/ENEURO.0259-23.2024 (NAO "Bruzzone et al." — essa
citacao foi verificada como incorreta e corrigida no Bloco L). Em banda larga (1-45 Hz),
LZc e a inclinacao do espectro de potencia (1/f) "track highly similar information".

Este script:
  1. Recomputa LZc e entropia de permutacao (mesma definicao de
     `recompute_empirico_v2/analise_sono_v2.py`) por epoca de 30s, Sleep-EDF Cassette,
     canais Fpz-Cz e Pz-Oz — para garantir alinhamento perfeito de epocas com as
     metricas novas abaixo (nao faz merge com CSVs de rodadas anteriores).
  2. Calcula o expoente aperiodico (1/f slope) por canal/epoca via FOOOF/specparam,
     banda 1-40 Hz (o filtro do pipeline ja limita a 0.5-40 Hz; 1-40 Hz fica proximo
     da banda larga 1-45 Hz usada por Hohn et al. 2024, dentro do que os dados permitem).
  3. Opera a alegacao-assinatura da teoria (integracao ALTA e diferenciacao ALTA,
     nao hipersincronia) com um proxy de 2 canais, documentado explicitamente:
       - sincronia bruta (hipersincronia): coerencia espectral broadband entre os 2 canais
       - integracao: informacao mutua (aproximacao gaussiana) entre os 2 canais
       - diferenciacao: entropia de permutacao media dos 2 canais (riqueza da dinamica
         de cada canal isoladamente)
       - indice de integracao-diferenciada = integracao * diferenciacao (precisa das
         DUAS altas simultaneamente — distingue de hipersincronia pura, que so exige
         sincronia/integracao alta)
  4. Testa se LZc, PE e o indice de integracao-diferenciada discriminam W-vs-N3 MELHOR
     do que o 1/f slope sozinho, e se a discriminacao de cada metrica SOBREVIVE apos
     controlar pelo 1/f slope (residualizacao linear + AUC do residuo, e correlacao
     parcial de Spearman).

IMPORTANTE (honestidade metodologica, seguindo `.codex/PROJECT_RULES.md`):
  - O Sleep-EDF Cassette so tem 2 canais EEG (Fpz-Cz, Pz-Oz). Isso NAO permite medidas
    grafo-teoricas de integracao/segregacao multi-regiao (que exigiriam >=8-16 canais/
    ROIs). Os proxies de 2 canais acima sao uma simplificacao deliberada e documentada,
    nao uma analise de rede completa — nomeie assim no relatorio, nunca como "grafo-
    teorica" sem essa ressalva.
  - Resultado negativo/misto e dado, nao fracasso: se a discriminacao NAO sobreviver ao
    controle por 1/f, isso deve ser reportado com a mesma honestidade do resultado da
    anestesia (Bloco K).
  - Este script SO ESCREVE E CALCULA quando executado pelo AUTOR, localmente. O agente
    que o escreveu nao o executou (regra de governanca do PLANO_ESTRATEGICO_cientifico.md
    Sec.0.1) — fez apenas verificacao de sintaxe (compilacao, nao execucao).

Uso:
    python integracao_diferenciada_1f.py --n-subjects 40 --data-dir <pasta_cache>

    Para uma primeira rodada de checagem rapida (recomendado antes da amostra cheia):
    python integracao_diferenciada_1f.py --n-subjects 3 --data-dir <pasta_cache>

Saidas (nesta pasta):
    integracao_diferenciada_por_epoca.csv   - todas as metricas, por epoca
    integracao_diferenciada_por_estagio.csv - medias/desvios por estagio
    auc_comparativo.csv                     - AUC (W-vs-N3) de cada metrica, bruta e
                                               residualizada por 1/f slope
    correlacao_parcial.csv                  - correlacao de Spearman (metrica vs estagio
                                               ordinal), bruta e parcial controlando 1/f
    integracao_diferenciada_por_estagio.png - boxplots comparativos
    scatter_lzc_vs_1f.png                   - dispersao LZc x 1/f slope, colorido por estagio
    resumo_frente_c.md                      - relatorio narrativo (o agente interpreta depois)

Dependencias adicionais (alem de requirements.txt): mne, antropy, scipy, fooof (ou o
sucessor `specparam`) — ver README_como_rodar.md nesta pasta.
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
from scipy import signal
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score

try:
    from fooof import FOOOF
except ImportError:  # sucessor do pacote fooof, mesma API basica
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
STAGE_ORDER = ["W", "REM", "N1", "N2", "N3"]
# Ordinal usado para correlacoes (maior = mais proximo de vigilia plena; segue a
# predicao central da teoria W~REM>N2>N3, com N1 como transicao). Documentado aqui
# para nao ficar implicito no codigo.
STAGE_ORDINAL = {"N3": 0, "N2": 1, "N1": 2, "REM": 3, "W": 4}

FIT_FREQ_RANGE = (1.0, 40.0)  # proximo da banda larga 1-45 Hz de Hohn et al. 2024,
                                # limitado pelo filtro 0.5-40 Hz ja aplicado no pipeline
COHERENCE_BAND = (1.0, 40.0)


def lzc_epoch(x: np.ndarray) -> float:
    b = (x >= np.median(x)).astype(np.uint8)
    return float(ant.lziv_complexity(b, normalize=True))


def pe_epoch(x: np.ndarray) -> float:
    return float(ant.perm_entropy(x, order=3, delay=1, normalize=True))


def aperiodic_exponent(x: np.ndarray, sfreq: float) -> float | None:
    """Expoente aperiodico (1/f slope) via FOOOF/specparam, modo 'fixed'.

    Retorna None se o ajuste falhar (epoca curta demais, PSD degenerada, etc.) —
    o chamador deve tratar epocas com None descartando-as das metricas derivadas.
    """
    nperseg = min(len(x), int(sfreq * 4))
    if nperseg < int(sfreq * 2):
        return None
    freqs, psd = signal.welch(x, fs=sfreq, nperseg=nperseg, noverlap=nperseg // 2)
    try:
        fm = FOOOF(peak_width_limits=(1.0, 8.0), max_n_peaks=6, aperiodic_mode="fixed", verbose=False)
        fm.fit(freqs, psd, FIT_FREQ_RANGE)
        # aperiodic_params_ = [offset, exponent] no modo 'fixed'
        return float(fm.aperiodic_params_[1])
    except Exception:
        return None


def gaussian_mutual_information(x: np.ndarray, y: np.ndarray) -> float:
    """Informacao mutua aproximada assumindo (x, y) conjuntamente gaussianos:
    I(X;Y) = -0.5 * ln(1 - r^2). Aproximacao simples e padrao na literatura para
    um proxy rapido de integracao entre 2 sinais continuos; nao substitui uma
    estimativa de MI nao-parametrica, mas e adequada como indice comparativo
    dentro do mesmo dataset/pipeline.
    """
    if np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    r = float(np.corrcoef(x, y)[0, 1])
    r = max(min(r, 0.999999), -0.999999)
    return float(-0.5 * np.log(1.0 - r ** 2))


def broadband_coherence(x: np.ndarray, y: np.ndarray, sfreq: float) -> float:
    """Coerencia espectral media na banda COHERENCE_BAND — proxy de sincronia
    bruta/hipersincronia entre os 2 canais (nao distingue integracao de diferenciacao,
    de proposito: e o "outro lado" da tese que o indice combinado abaixo deve superar).
    """
    nperseg = min(len(x), int(sfreq * 4))
    if nperseg < int(sfreq * 2):
        return float("nan")
    freqs, cxy = signal.coherence(x, y, fs=sfreq, nperseg=nperseg, noverlap=nperseg // 2)
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
    if not eeg_picks:
        eeg_picks = [ch for ch in raw.ch_names if ("EEG" in ch) or ("Fpz-Cz" in ch) or ("Pz-Oz" in ch)]
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

    rows = []
    for i in range(data.shape[0]):
        stage = inv_event_id[labels[i]]

        lzc_per_ch = [lzc_epoch(data[i, ch, :]) for ch in range(n_ch)]
        pe_per_ch = [pe_epoch(data[i, ch, :]) for ch in range(n_ch)]
        exp_per_ch = [aperiodic_exponent(data[i, ch, :], sfreq) for ch in range(n_ch)]

        valid_exps = [e for e in exp_per_ch if e is not None]
        if not valid_exps:
            continue  # epoca sem ajuste 1/f valido em nenhum canal: descarta (documentar contagem no resumo)
        exponent_mean = float(np.mean(valid_exps))

        row = {
            "subject": subject_id,
            "stage": stage,
            "lzc": float(np.mean(lzc_per_ch)),
            "pe": float(np.mean(pe_per_ch)),
            "exponent_1f": exponent_mean,
            "exponent_1f_n_canais_validos": len(valid_exps),
        }

        if n_ch >= 2:
            x, y = data[i, 0, :], data[i, 1, :]
            row["sync_bruta"] = broadband_coherence(x, y, sfreq)
            row["integracao_mi"] = gaussian_mutual_information(x, y)
            row["diferenciacao_pe"] = float(np.mean(pe_per_ch))
            row["indice_integ_diferenciada"] = row["integracao_mi"] * row["diferenciacao_pe"]
        else:
            row["sync_bruta"] = float("nan")
            row["integracao_mi"] = float("nan")
            row["diferenciacao_pe"] = float("nan")
            row["indice_integ_diferenciada"] = float("nan")

        rows.append(row)
    return pd.DataFrame(rows)


def residualize(metric: np.ndarray, covariate: np.ndarray) -> np.ndarray:
    """Residuo de `metric` apos regressao linear simples sobre `covariate` (1/f slope).
    Usado para testar discriminacao "incremental" acima e alem do 1/f, conforme
    pedido em SINTESE_pilares.md (achado #1)."""
    X = covariate.reshape(-1, 1)
    reg = LinearRegression().fit(X, metric)
    pred = reg.predict(X)
    return metric - pred


def auc_w_vs_n3(df: pd.DataFrame, col: str) -> float | None:
    sub = df[df["stage"].isin(["W", "N3"])].dropna(subset=[col])
    if sub["stage"].nunique() < 2 or len(sub) < 4:
        return None
    y = (sub["stage"] == "W").astype(int).values
    return float(roc_auc_score(y, sub[col].values))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-subjects", type=int, default=41, help="Indice maximo (exclusivo) de sujeitos a tentar")
    ap.add_argument("--data-dir", type=str, required=True, help="Pasta de cache do mne.datasets (PHYSIONET_SLEEP_PATH)")
    args = ap.parse_args()

    subjects = list(range(args.n_subjects))
    paths = mne.datasets.sleep_physionet.age.fetch_data(
        subjects=subjects, recording=[1], path=args.data_dir, on_missing="warn"
    )
    # Sujeitos conhecidos como ausentes no dataset (mesma lista de analise_sono_v2.py)
    known_missing = {39, 68, 69, 78, 79}
    fetched_subject_ids = [s for s in subjects if s not in known_missing][: len(paths)]

    all_epochs, processed, failed = [], [], []
    for subj_id, (psg_path, hyp_path) in zip(fetched_subject_ids, paths):
        try:
            df = process_subject(psg_path, hyp_path, subj_id)
            all_epochs.append(df)
            processed.append(subj_id)
            print(f"[ok] sujeito {subj_id}: {len(df)} epocas com 1/f valido")
        except Exception as e:
            failed.append((subj_id, str(e)))
            print(f"[ERRO] sujeito {subj_id}: {e}")

    if not all_epochs:
        raise RuntimeError("Nenhum sujeito processado com sucesso.")

    epochs_df = pd.concat(all_epochs, ignore_index=True)
    epochs_df.to_csv(HERE / "integracao_diferenciada_por_epoca.csv", index=False)

    metric_cols = ["lzc", "pe", "exponent_1f", "sync_bruta", "integracao_mi", "diferenciacao_pe", "indice_integ_diferenciada"]
    by_stage = epochs_df.groupby("stage")[metric_cols].agg(["mean", "std", "count"]).reindex(STAGE_ORDER)
    by_stage.to_csv(HERE / "integracao_diferenciada_por_estagio.csv")
    print("\n=== Metricas medias por estagio ===")
    print(by_stage)

    # --- AUC W-vs-N3: bruta e residualizada por 1/f slope ---
    auc_rows = []
    covariate_full = epochs_df["exponent_1f"].values
    for col in ["lzc", "pe", "exponent_1f", "sync_bruta", "integracao_mi", "indice_integ_diferenciada"]:
        raw_auc = auc_w_vs_n3(epochs_df, col)
        if col == "exponent_1f":
            resid_auc = None  # nao faz sentido residualizar o proprio 1/f por ele mesmo
        else:
            sub = epochs_df.dropna(subset=[col, "exponent_1f"]).copy()
            if len(sub) >= 4:
                resid = residualize(sub[col].values, sub["exponent_1f"].values)
                tmp = pd.DataFrame({"stage": sub["stage"].values, "resid": resid})
                resid_auc = auc_w_vs_n3(tmp, "resid")
            else:
                resid_auc = None
        auc_rows.append({"metrica": col, "auc_w_vs_n3_bruta": raw_auc, "auc_w_vs_n3_residualizada_1f": resid_auc})
    auc_df = pd.DataFrame(auc_rows)
    auc_df.to_csv(HERE / "auc_comparativo.csv", index=False)
    print("\n=== AUC W-vs-N3 (bruta vs. residualizada por 1/f) ===")
    print(auc_df)

    # --- Correlacao de Spearman com o estagio (ordinal), bruta e parcial ---
    epochs_df["stage_ordinal"] = epochs_df["stage"].map(STAGE_ORDINAL)
    corr_rows = []
    for col in ["lzc", "pe", "sync_bruta", "integracao_mi", "indice_integ_diferenciada"]:
        sub = epochs_df.dropna(subset=[col, "exponent_1f", "stage_ordinal"])
        if len(sub) < 4:
            corr_rows.append({"metrica": col, "spearman_bruta": None, "spearman_parcial_1f": None})
            continue
        rho_raw = spearmanr(sub[col], sub["stage_ordinal"]).statistic
        resid_metric = residualize(sub[col].values, sub["exponent_1f"].values)
        resid_stage = residualize(sub["stage_ordinal"].values.astype(float), sub["exponent_1f"].values)
        rho_partial = spearmanr(resid_metric, resid_stage).statistic
        corr_rows.append({"metrica": col, "spearman_bruta": float(rho_raw), "spearman_parcial_1f": float(rho_partial)})
    corr_df = pd.DataFrame(corr_rows)
    corr_df.to_csv(HERE / "correlacao_parcial.csv", index=False)
    print("\n=== Correlacao de Spearman com estagio (bruta vs. parcial controlando 1/f) ===")
    print(corr_df)

    # --- Figuras ---
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    plot_cols = ["lzc", "pe", "exponent_1f", "sync_bruta", "integracao_mi", "indice_integ_diferenciada"]
    titles = ["LZc", "Entropia de permutação", "Expoente 1/f", "Sincronia bruta (coerência)", "Integração (MI gaussiana)", "Índice integração-diferenciada"]
    for ax, col, title in zip(axes.flat, plot_cols, titles):
        box_data = [epochs_df.loc[epochs_df["stage"] == s, col].dropna().values for s in STAGE_ORDER]
        ax.boxplot(box_data, tick_labels=STAGE_ORDER, showmeans=True)
        ax.set_title(title, fontsize=10)
    fig.suptitle(f"Frente C — métricas por estágio (n={len(processed)} sujeitos, {len(epochs_df)} épocas)")
    fig.tight_layout()
    fig.savefig(HERE / "integracao_diferenciada_por_estagio.png", dpi=160)
    plt.close(fig)

    fig2, ax2 = plt.subplots(figsize=(7, 6))
    for stage in STAGE_ORDER:
        sub = epochs_df[epochs_df["stage"] == stage]
        ax2.scatter(sub["exponent_1f"], sub["lzc"], s=6, alpha=0.4, label=stage)
    ax2.set_xlabel("Expoente 1/f (aperiodic exponent)")
    ax2.set_ylabel("LZc")
    ax2.set_title("LZc vs. inclinação espectral (1/f), por estágio")
    ax2.legend(markerscale=3)
    fig2.tight_layout()
    fig2.savefig(HERE / "scatter_lzc_vs_1f.png", dpi=160)
    plt.close(fig2)

    # --- Resumo narrativo ---
    resumo = f"""# Frente C — Resumo (gerado automaticamente, a interpretar por um agente depois)

Sujeitos solicitados: 0-{args.n_subjects - 1} | processados com sucesso: {len(processed)}
IDs processados: {processed}
Falhas: {failed if failed else 'nenhuma'}
Total de épocas com 1/f válido: {len(epochs_df)}

## AUC W-vs-N3 (bruta vs. residualizada por 1/f)
{auc_df.to_string(index=False)}

## Correlação de Spearman com estágio (bruta vs. parcial controlando 1/f)
{corr_df.to_string(index=False)}

## Leitura (preencher/revisar após rodar — não inventar conclusão aqui)
- Se `auc_w_vs_n3_residualizada_1f` de `lzc`/`pe`/`indice_integ_diferenciada` permanecer
  alta (próxima da bruta), a discriminação sobrevive ao controle por 1/f — reforça a
  leitura de "integração diferenciada", não apenas confundidor espectral.
- Se cair para perto de 0.5, o resultado é mais consistente com a hipótese do
  confundidor (Höhn et al. 2024) — reportar com a mesma honestidade do Bloco K
  (resultado negativo é dado, não fracasso).
- `sync_bruta` (hipersincronia) NÃO deveria discriminar tão bem quanto
  `indice_integ_diferenciada` — se discriminar igual ou melhor, isso enfraquece a
  alegação-assinatura da teoria (integração diferenciada > sincronia pura) e deve ser
  reportado como tal, não maquiado.

## Limitação metodológica (ver docstring do script)
Sleep-EDF Cassette só tem 2 canais EEG (Fpz-Cz, Pz-Oz). `integracao_mi`,
`diferenciacao_pe`, `sync_bruta` e `indice_integ_diferenciada` são proxies de 2 canais,
não medidas grafo-teóricas de rede multi-região. Reportar como tal.
"""
    (HERE / "resumo_frente_c.md").write_text(resumo, encoding="utf-8")
    print("\nProcessamento concluído. Saídas em:", HERE)


if __name__ == "__main__":
    main()
