"""Frente D — reanalise da anestesia (propofol) estratificada por responsividade real,
nao apenas por dose/estado nominal.

Contexto (ver `embasamento/nota_anestesia.md` para a leitura completa da literatura):
o recompute V2 (`recompute_empirico_v2/analise_anestesia_propofol.py`) encontrou um
resultado NEGATIVO/misto: a predicao de que a complexidade (LZc, entropia de permutacao)
cairia com a profundidade da sedacao NAO se confirmou — "basal" teve a MENOR
complexidade das 4 condicoes, e a AUC basal-vs-sedacao-moderada ficou abaixo do acaso
(LZc=0,33; PE=0,45). O proprio artigo do dataset (Chennu, O'Connor, Adapa, Menon,
Bekinschtein 2016, PLOS Comp Biol, DOI 10.1371/journal.pcbi.1004669) tem como achado
central que a RESPONSIVIDADE COMPORTAMENTAL se dissocia da dose nominal de propofol —
alguns sujeitos permanecem responsivos em sedacao "moderada", outros ficam nao-
responsivos ja em sedacao "leve". Um estudo mais recente que reanalisou ESTE MESMO
dataset — Newman, Maschke, Mashour & Blain-Moraes (2026), British Journal of
Anaesthesia 137(2):525-534, DOI 10.1016/j.bja.2026.03.082 — encontrou que sujeitos que
permanecem responsivos sob sedacao moderada mostram um aumento PARADOXAL de
complexidade tipo Lempel-Ziv, enquanto sujeitos que ficam nao-responsivos mostram o
padrao esperado (queda de complexidade). Isso e uma explicacao candidata forte e ja
publicada (nao inventada nesta sessao) para o resultado negativo/misto do projeto:
se a amostra e uma MISTURA de dois subgrupos com respostas opostas, a media do grupo
inteiro pode nao mostrar tendencia clara nem consistencia entre metricas — exatamente
o que foi observado.

Este script:
  1. Le `datainfo.mat` (mesmo arquivo ja usado por `analise_anestesia_propofol.py`,
     agora extraindo TODAS as 5 colunas, nao so a coluna de estado): nome do arquivo,
     codigo de sedacao (1-4), concentracao plasmatica de propofol (ug/L), tempo de
     reacao medio (ms) e numero de respostas corretas (de 40) na tarefa auditiva de
     duas escolhas usada pelos autores do dataset original.
  2. Calcula hit_rate = respostas_corretas / 40 por sujeito/estado (variavel continua
     de responsividade).
  3. Reconstroi (aproximadamente — ver ressalva abaixo) a classificacao binaria
     "responsive" / "drowsy" por sujeito, comparando o intervalo de confianca de
     Wilson (95%) do hit rate no basal vs. na sedacao moderada, seguindo a descricao
     do metodo em Chennu et al. (2016) Methods/"Behavioural data analysis". Nao ha
     garantia de reproduzir exatamente os 7 "drowsy"/13 "responsive" relatados pelos
     autores (o tipo exato de intervalo de confianca usado por eles nao e detalhado
     no artigo) — tratar como reconstrucao aproximada, documentada como tal no resumo.
  4. Recalcula LZc e entropia de permutacao por epoca (mesma definicao de
     `analise_anestesia_propofol.py`, para alinhamento exato).
  5. Reestratifica a comparacao "basal vs. sedacao moderada" por grupo de
     responsividade (responsive vs. drowsy), replicando diretamente a logica de
     Newman et al. (2026) neste mesmo dataset: testa se o aumento paradoxal de LZc
     esta concentrado no subgrupo "responsive" e a queda esperada no subgrupo "drowsy".
  6. Testa a correlacao entre a complexidade basal de cada sujeito e a MUDANCA de
     complexidade sob sedacao moderada (replicando, com LZc/PE em vez da complexidade
     estatistica Tipo II usada por Newman et al., o espirito do r=-0,88 relatado por
     eles — SEM prometer reproduzir esse numero, que era para uma metrica diferente).

IMPORTANTE (honestidade metodologica):
  - A classificacao "responsive"/"drowsy" reconstruida aqui e uma APROXIMACAO do
    metodo original, nao uma reproducao garantida. Reportar isso explicitamente.
  - Se a reestratificacao NAO mostrar o padrao de Newman et al. (2026) neste projeto,
    isso e um resultado negativo tao valido quanto qualquer outro — reportar com a
    mesma honestidade do Bloco K, nao maquiar.
  - Este script SO ESCREVE E CALCULA quando executado pelo AUTOR, localmente. O agente
    que o escreveu nao o executou (regra de governanca do PLANO_ESTRATEGICO_cientifico.md
    Sec.0.1) — fez apenas verificacao de sintaxe (compilacao, nao execucao).
  - A estrutura de `datainfo.mat` (5 colunas) foi confirmada via documentacao oficial
    do FieldTrip Toolbox e da pagina do repositorio Apollo/Cambridge, NAO por inspecao
    direta do arquivo binario (que so existe dentro do zip de 3,44 GB, nao baixado por
    este agente). Se a leitura via `pymatreader.read_mat` retornar uma estrutura
    diferente da esperada (nomes de campo diferentes, menos/mais colunas), o script
    imprime a estrutura bruta encontrada em vez de falhar silenciosamente — confira
    a saida do terminal na primeira rodada.

Uso:
    python reanalise_responsividade_propofol.py --data-dir <pasta_extraida> [--max-subjects N]

    (mesma pasta "Sedation-RestingState" extraida ja usada por
    `analise_anestesia_propofol.py` — reaproveita os mesmos arquivos .set e o mesmo
    datainfo.mat, nao baixa nada de novo)

Saidas (nesta pasta):
    responsividade_por_sujeito.csv       - hit_rate, IC de Wilson, classificacao
                                            responsive/drowsy reconstruida, por sujeito
    propofol_responsividade_por_epoca.csv - LZc/PE por epoca, com grupo de responsividade
    comparacao_por_grupo.csv             - medias/AUC de LZc/PE por estado, separado por
                                            grupo responsive vs. drowsy (o teste central)
    correlacao_basal_vs_mudanca.csv      - complexidade basal x mudanca sob sedacao
                                            moderada, por sujeito
    comparacao_por_grupo.png             - figura comparativa
    resumo_frente_d.md                   - relatorio narrativo (a interpretar depois)
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
N_TRIALS_TASK = 40  # total de tentativas na tarefa auditiva de 2 escolhas (Chennu et al. 2016, Methods)


def lzc_epoch(x: np.ndarray) -> float:
    b = (x >= np.median(x)).astype(np.uint8)
    return float(ant.lziv_complexity(b, normalize=True))


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confianca de Wilson (95% por padrao) para uma proporcao binomial.
    Escolha documentada: o artigo original (Chennu et al. 2016) nao especifica o tipo
    exato de IC usado — Wilson e uma escolha padrao e robusta para n pequeno (n=40
    aqui), mas isso significa que a classificacao reconstruida abaixo e uma
    aproximacao, nao uma reproducao garantida do rotulo original dos autores."""
    if n == 0:
        return (0.0, 1.0)
    phat = successes / n
    denom = 1 + z ** 2 / n
    center = (phat + z ** 2 / (2 * n)) / denom
    margin = (z * np.sqrt((phat * (1 - phat) + z ** 2 / (4 * n)) / n)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def load_datainfo(data_dir: Path) -> pd.DataFrame:
    """Le datainfo.mat com as 5 colunas documentadas (filename, sedation, concentration,
    reactiontime, correctresponses). Se a estrutura vier diferente do esperado, imprime
    o formato bruto em vez de falhar silenciosamente — ver docstring do modulo."""
    mat_path = data_dir / "datainfo.mat"
    d = read_mat(str(mat_path))
    raw_table = d["datainfo"]

    rows = []
    for i, row in enumerate(raw_table):
        try:
            filename = row[0]
            sedation_code = int(row[1])
            concentration = float(row[2]) if len(row) > 2 else float("nan")
            reactiontime = float(row[3]) if len(row) > 3 else float("nan")
            correct = float(row[4]) if len(row) > 4 else float("nan")
        except (IndexError, TypeError, ValueError) as e:
            print(f"[AVISO] linha {i} de datainfo.mat em formato inesperado ({e}); linha bruta: {row}")
            continue
        rows.append({
            "filename": filename,
            "state": STATE_LABELS.get(sedation_code, f"desconhecido_{sedation_code}"),
            "concentration_ug_l": concentration,
            "reactiontime_ms": reactiontime,
            "correctresponses": correct,
        })
    df = pd.DataFrame(rows)
    if df.empty or df["correctresponses"].isna().all():
        print("\n[AVISO IMPORTANTE] Não foi possível extrair colunas 3-5 (concentração/tempo de "
              "reação/respostas corretas) de datainfo.mat no formato esperado. Estrutura bruta da "
              "primeira linha, para diagnóstico manual:")
        print(raw_table[0] if len(raw_table) else "tabela vazia")
        print("Prosseguindo apenas com a coluna de estado (código de sedação) já usada em "
              "analise_anestesia_propofol.py; a estratificação por responsividade não será possível.\n")
    return df


def classify_responsiveness(datainfo: pd.DataFrame) -> pd.DataFrame:
    """Reconstroi hit_rate e a classificacao responsive/drowsy por sujeito, comparando
    o IC de Wilson do hit rate no basal vs. na sedacao moderada (metodo aproximado —
    ver docstring)."""
    datainfo = datainfo.copy()
    datainfo["subject"] = datainfo["filename"].apply(lambda f: re.match(r"(\d+)", str(f)).group(1))
    datainfo["hit_rate"] = datainfo["correctresponses"] / N_TRIALS_TASK

    rows = []
    for subject, sub in datainfo.groupby("subject"):
        basal = sub[sub["state"] == "basal"]
        moderada = sub[sub["state"] == "sedacao_moderada"]
        if basal.empty or moderada.empty or basal["correctresponses"].isna().any() or moderada["correctresponses"].isna().any():
            rows.append({"subject": subject, "hit_rate_basal": None, "hit_rate_moderada": None, "grupo_responsividade": "indeterminado"})
            continue
        n_basal = int(basal["correctresponses"].iloc[0])
        n_mod = int(moderada["correctresponses"].iloc[0])
        ci_basal = wilson_ci(n_basal, N_TRIALS_TASK)
        ci_mod = wilson_ci(n_mod, N_TRIALS_TASK)
        # "drowsy" se o IC da sedacao moderada for mais baixo e nao sobreposto ao do basal
        non_overlapping_lower = ci_mod[1] < ci_basal[0]
        grupo = "drowsy" if non_overlapping_lower else "responsive"
        rows.append({
            "subject": subject,
            "hit_rate_basal": n_basal / N_TRIALS_TASK,
            "hit_rate_moderada": n_mod / N_TRIALS_TASK,
            "ci_wilson_basal": ci_basal,
            "ci_wilson_moderada": ci_mod,
            "grupo_responsividade": grupo,
        })
    return pd.DataFrame(rows)


def process_file(set_path: Path, subject_id: str, state: str) -> pd.DataFrame:
    """Identico a analise_anestesia_propofol.py — mantido separado (nao importado)
    para este script ficar autocontido e nao depender de um caminho relativo fragil
    ate o outro script."""
    epochs = mne.io.read_epochs_eeglab(str(set_path), verbose=False)
    data = epochs.get_data()
    n_epochs, n_channels, n_times = data.shape

    pe_per_epoch_channel = np.zeros((n_epochs, n_channels))
    for ch in range(n_channels):
        pe_per_epoch_channel[:, ch] = ant.perm_entropy(data[:, ch, :], order=3, normalize=True)
    pe_per_epoch = pe_per_epoch_channel.mean(axis=1)

    lzc_per_epoch = np.zeros(n_epochs)
    for e in range(n_epochs):
        lzc_vals = [lzc_epoch(data[e, ch, :]) for ch in range(n_channels)]
        lzc_per_epoch[e] = float(np.mean(lzc_vals))

    return pd.DataFrame({
        "subject": subject_id, "state": state,
        "epoch": np.arange(n_epochs),
        "lzc": lzc_per_epoch, "pe": pe_per_epoch,
    })


def auc_between(df: pd.DataFrame, col: str, state_a: str, state_b: str, positive: str) -> float | None:
    sub = df[df["state"].isin([state_a, state_b])].dropna(subset=[col])
    if sub["state"].nunique() < 2 or len(sub) < 4:
        return None
    y = (sub["state"] == positive).astype(int).values
    return float(roc_auc_score(y, sub[col].values))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=str, required=True, help="Pasta 'Sedation-RestingState' extraida (mesma do analise_anestesia_propofol.py)")
    ap.add_argument("--max-subjects", type=int, default=None, help="Limitar numero de sujeitos (para teste rapido)")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)

    print("=== Passo 1: lendo datainfo.mat (5 colunas) ===")
    datainfo = load_datainfo(data_dir)
    if datainfo.empty:
        raise RuntimeError("datainfo.mat não pôde ser lido — verifique --data-dir.")

    print("\n=== Passo 2: reconstruindo classificação responsive/drowsy (aproximada) ===")
    resp_df = classify_responsiveness(datainfo)
    resp_df.to_csv(HERE / "responsividade_por_sujeito.csv", index=False)
    print(resp_df[["subject", "hit_rate_basal", "hit_rate_moderada", "grupo_responsividade"]])
    n_drowsy = (resp_df["grupo_responsividade"] == "drowsy").sum()
    n_responsive = (resp_df["grupo_responsividade"] == "responsive").sum()
    print(f"\nClassificação reconstruída: {n_responsive} 'responsive', {n_drowsy} 'drowsy' "
          f"(Chennu et al. 2016 relatam 13/7 no artigo original — não é garantido bater exatamente).")

    print("\n=== Passo 3: processando EEG (LZc/PE por época), como em analise_anestesia_propofol.py ===")
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
            print(f"[AVISO] sem estado mapeado para {stem}, pulando")
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
    grupo_map = dict(zip(resp_df["subject"], resp_df["grupo_responsividade"]))
    epochs_df["grupo_responsividade"] = epochs_df["subject"].map(grupo_map).fillna("indeterminado")
    epochs_df.to_csv(HERE / "propofol_responsividade_por_epoca.csv", index=False)

    print("\n=== Passo 4: comparação basal vs. sedação moderada, por grupo de responsividade ===")
    comp_rows = []
    for grupo in ["responsive", "drowsy"]:
        sub_grupo = epochs_df[epochs_df["grupo_responsividade"] == grupo]
        by_state = sub_grupo.groupby("state")[["lzc", "pe"]].mean().reindex(STATE_ORDER)
        auc_lzc = auc_between(sub_grupo, "lzc", "basal", "sedacao_moderada", positive="sedacao_moderada")
        auc_pe = auc_between(sub_grupo, "pe", "basal", "sedacao_moderada", positive="sedacao_moderada")
        n_subj_grupo = sub_grupo["subject"].nunique()
        comp_rows.append({
            "grupo": grupo, "n_sujeitos": n_subj_grupo,
            "lzc_basal": by_state.loc["basal", "lzc"] if "basal" in by_state.index else None,
            "lzc_sedacao_moderada": by_state.loc["sedacao_moderada", "lzc"] if "sedacao_moderada" in by_state.index else None,
            "pe_basal": by_state.loc["basal", "pe"] if "basal" in by_state.index else None,
            "pe_sedacao_moderada": by_state.loc["sedacao_moderada", "pe"] if "sedacao_moderada" in by_state.index else None,
            "auc_lzc_basal_vs_moderada_positivo_moderada": auc_lzc,
            "auc_pe_basal_vs_moderada_positivo_moderada": auc_pe,
        })
    comp_df = pd.DataFrame(comp_rows)
    comp_df.to_csv(HERE / "comparacao_por_grupo.csv", index=False)
    print(comp_df)
    print("\nLeitura (Newman et al. 2026, mesmo dataset): esperado 'responsive' mostrar LZc MAIOR na "
          "sedação moderada que no basal (aumento paradoxal, AUC>0.5 favorecendo moderada); 'drowsy' "
          "mostrar o padrão oposto (queda, AUC<0.5). Confira se os números acima seguem esse padrão — "
          "não assuma, leia o resultado real.")

    print("\n=== Passo 5: complexidade basal x mudança sob sedação moderada, por sujeito ===")
    per_subj = epochs_df.groupby(["subject", "state"])[["lzc", "pe"]].mean().unstack()
    corr_rows = []
    if ("lzc", "basal") in per_subj.columns and ("lzc", "sedacao_moderada") in per_subj.columns:
        basal_lzc = per_subj[("lzc", "basal")]
        delta_lzc = per_subj[("lzc", "sedacao_moderada")] - basal_lzc
        valid = basal_lzc.notna() & delta_lzc.notna()
        if valid.sum() >= 4:
            rho, p = spearmanr(basal_lzc[valid], delta_lzc[valid])
            corr_rows.append({"metrica": "lzc", "spearman_basal_vs_delta": float(rho), "p_valor": float(p), "n": int(valid.sum())})
    if ("pe", "basal") in per_subj.columns and ("pe", "sedacao_moderada") in per_subj.columns:
        basal_pe = per_subj[("pe", "basal")]
        delta_pe = per_subj[("pe", "sedacao_moderada")] - basal_pe
        valid = basal_pe.notna() & delta_pe.notna()
        if valid.sum() >= 4:
            rho, p = spearmanr(basal_pe[valid], delta_pe[valid])
            corr_rows.append({"metrica": "pe", "spearman_basal_vs_delta": float(rho), "p_valor": float(p), "n": int(valid.sum())})
    corr_df = pd.DataFrame(corr_rows)
    corr_df.to_csv(HERE / "correlacao_basal_vs_mudanca.csv", index=False)
    print(corr_df)
    print("\nNota: Newman et al. (2026) relatam r=-0.88 para uma métrica DIFERENTE (complexidade "
          "estatística Tipo II) — o teste acima é análogo, não uma tentativa de reproduzir esse número "
          "específico com LZc/PE (Tipo I).")

    # --- Figura ---
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, metric, title in zip(axes, ["lzc", "pe"], ["LZc", "Entropia de permutação"]):
        for grupo, marker in [("responsive", "o"), ("drowsy", "s")]:
            sub_grupo = epochs_df[epochs_df["grupo_responsividade"] == grupo]
            means = sub_grupo.groupby("state")[metric].mean().reindex(STATE_ORDER)
            ax.plot(STATE_ORDER, means.values, marker=marker, label=grupo)
        ax.set_title(title)
        ax.set_xticklabels(["basal", "leve", "moderada", "recup."])
        ax.legend()
    fig.suptitle("Frente D — complexidade por estado, estratificado por responsividade reconstruída")
    fig.tight_layout()
    fig.savefig(HERE / "comparacao_por_grupo.png", dpi=160)
    plt.close(fig)

    # --- Resumo narrativo ---
    resumo = f"""# Frente D — Resumo (gerado automaticamente, a interpretar por um agente depois)

Sujeitos com dados de responsividade: {len(resp_df)} ({n_responsive} 'responsive', {n_drowsy} 'drowsy',
reconstrução aproximada via IC de Wilson — Chennu et al. 2016 relatam 13/7 no artigo original)
Arquivos EEG processados: {len(subjects_seen)} sujeitos, {len(epochs_df)} épocas
Falhas: {failed if failed else 'nenhuma'}

## Comparação por grupo de responsividade (o teste central desta reanálise)
{comp_df.to_string(index=False)}

## Correlação complexidade basal x mudança sob sedação moderada
{corr_df.to_string(index=False)}

## Leitura (preencher/revisar após rodar — não inventar conclusão aqui)
- Se o grupo 'responsive' mostrar LZc/PE MAIOR na sedação moderada que no basal (AUC
  favorecendo moderada) e o grupo 'drowsy' mostrar o padrão oposto, isso REPLICA o
  achado de Newman et al. (2026, BJA, mesmo dataset) e explica por que a análise
  agregada original (`analise_anestesia_propofol.py`) deu um resultado negativo/misto:
  os dois subgrupos se cancelam na média.
- Se não replicar, é um resultado negativo igualmente válido — reportar com a mesma
  honestidade do Bloco K, sem forçar a leitura.
- Lembrar: a classificação responsive/drowsy aqui é uma RECONSTRUÇÃO aproximada do
  método de Chennu et al. (2016), não os rótulos originais exatos dos autores — o
  número de sujeitos em cada grupo pode diferir ligeiramente de 13/7.

## Limitação metodológica
Ver docstring do script: estrutura de `datainfo.mat` confirmada via documentação do
FieldTrip Toolbox, não por inspeção direta do binário. Se a leitura falhar ou vier
incompleta, o script imprime a estrutura bruta no início da execução — confira o log.
"""
    (HERE / "resumo_frente_d.md").write_text(resumo, encoding="utf-8")
    print("\nProcessamento concluído. Saídas em:", HERE)


if __name__ == "__main__":
    main()
