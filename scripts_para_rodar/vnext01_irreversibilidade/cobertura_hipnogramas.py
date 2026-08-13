#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cobertura_hipnogramas.py — Checagem Z12 do PROTOCOLO_VNext_01, etapa 0.3/0.4.

ESTATUTO: codigo congelado antes da execucao. Escrito por agente; executado pelo autor.
Nenhum numero deste arquivo e resultado.

--------------------------------------------------------------------------------------
A PERGUNTA
--------------------------------------------------------------------------------------

Os arquivos SC do Sleep-EDF Cassette sao gravacoes de ~20 h em atividade diurna normal. O
pipeline do projeto corta a ±30 min em torno do sono — convencao da literatura, nao limite
do dataset (`analise_sono_v2.py`, linhas 66-72):

    sleep_annots = [a for a in annot if a["description"] != "Sleep stage ?"]
    onset_first  = sleep_annots[1]["onset"]      # pula a PRIMEIRA anotacao pontuada
    onset_last   = sleep_annots[-2]["onset"]     # pula a ULTIMA
    crop_start   = max(0, onset_first - 30*60)
    crop_end     = onset_last + 30*60

Nunca foi verificado se os hipnogramas cobrem as 20 h. Se cobrirem, existe vigilia ATIVA
recuperavel sem trocar de dataset — o que ataca de uma vez a falha do proxy de EMG no REM e
a natureza do contraste W-vs-N3, hoje feito contra o periodo calmo em torno do sono.

Observacao de codigo, registrada como pista e nao como achado: o corte ancora em
`sleep_annots[1]` e `[-2]`, pulando a primeira e a ultima anotacao pontuada. Isso so faz
sentido se essas anotacoes forem blocos longos de vigilia. Este script mede se e o caso.

--------------------------------------------------------------------------------------
FILOSOFIA: DESCRITIVO E DETERMINISTICO
--------------------------------------------------------------------------------------

Este script NAO toma decisao cientifica nenhuma. Ele nao calcula metrica, nao filtra sinal,
nao rejeita epoca por artefato e nao decide se o braco W(ativo) sera executado. Ele apenas
CONTA, contra um criterio que ja estava fixado antes de ele existir, e reporta:

  - quantos participantes satisfazem cada requisito pre-declarado;
  - quais nao satisfazem, e por que, nominalmente;
  - o veredito mecanico do criterio de §3.2, aplicado sem margem de interpretacao.

O criterio (§3.2 do protocolo, fixado antes desta checagem):

    O braco W(ativo) so e executado se, em pelo menos 30 dos 36 participantes, existirem
    >= 30 epocas (15 min) anotadas como vigilia FORA da janela de +-30 min do corte atual.

ATENCAO A UMA RESSALVA QUE O PROPRIO CRITERIO CARREGA: o texto de §3.2 diz "apos rejeicao
de artefato". Este script mede a cobertura ANOTADA, sem rejeicao de artefato, porque
rejeicao de artefato exige carregar o sinal e aplicar um pipeline — o que faria dele um
script de analise, nao de contagem. A contagem aqui e, portanto, um LIMITE SUPERIOR do que
sobrara. O relatorio diz isso explicitamente, e o veredito e reportado como
`criterio_satisfeito_antes_de_artefato`. Se a margem for apertada, a decisao final exige a
passada de artefato; se nem o limite superior passar, a decisao ja esta tomada.

--------------------------------------------------------------------------------------
SAIDAS
--------------------------------------------------------------------------------------

  cobertura_hipnogramas.csv       uma linha por participante/registro (machine-readable)
  cobertura_hipnogramas_meta.json veredito, criterio, versoes, parametros
  cobertura_hipnogramas.md        relatorio humano

Uso:
    python cobertura_hipnogramas.py --data-dir <pasta_cache> --out-dir saida_vnext01

`--data-dir` e a pasta onde `mne.datasets.sleep_physionet` ja baixou os arquivos. O script
NAO baixa nada por conta propria a menos que --permitir-download seja passado.

Dependencias: numpy, pandas, mne (versoes de requirements.txt).
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ======================================================================================
# CONSTANTES — pre-declaradas, iguais as do pipeline atual e as de §3.2
# ======================================================================================

JANELA_CORTE_S = 30 * 60      # ±30 min, identico a analise_sono_v2.py
DURACAO_EPOCA_S = 30.0        # epoca do projeto
MIN_EPOCAS_W_FORA = 30        # §3.2: >= 30 epocas (15 min)
MIN_PARTICIPANTES = 30        # §3.2: em >= 30 dos 36 participantes
N_PARTICIPANTES_ALVO = 36

DESC_IGNORAR = "Sleep stage ?"
DESC_W = "Sleep stage W"


def carrega_anotacoes(hyp_path: Path):
    import mne
    return mne.read_annotations(str(hyp_path))


def analisa_registro(psg_path: Path, hyp_path: Path) -> dict:
    """Conta cobertura de um registro. Puramente descritivo."""
    import mne

    raw = mne.io.read_raw_edf(str(psg_path), preload=False, verbose="ERROR")
    dur_total_s = float(raw.times[-1])
    sfreq = float(raw.info["sfreq"])

    annot = carrega_anotacoes(hyp_path)
    todas = [(float(a["onset"]), float(a["duration"]), str(a["description"])) for a in annot]
    pontuadas = [a for a in todas if a[2] != DESC_IGNORAR]

    linha = {
        "psg": psg_path.name,
        "hipnograma": hyp_path.name,
        "sfreq_hz": sfreq,
        "duracao_registro_s": dur_total_s,
        "duracao_registro_h": dur_total_s / 3600.0,
        "n_anotacoes_totais": len(todas),
        "n_anotacoes_pontuadas": len(pontuadas),
        "duracao_anotada_total_s": float(sum(d for _, d, _ in todas)),
        "duracao_pontuada_total_s": float(sum(d for _, d, _ in pontuadas)),
        "erro": "",
    }

    if len(pontuadas) <= 2:
        linha["erro"] = "menos de 3 anotacoes pontuadas; corte do pipeline nao se aplica"
        return linha

    # Reproduz EXATAMENTE o corte de analise_sono_v2.py
    onset_first = pontuadas[1][0]
    onset_last = pontuadas[-2][0]
    crop_start = max(0.0, onset_first - JANELA_CORTE_S)
    crop_end = min(onset_last + JANELA_CORTE_S, dur_total_s)

    linha.update({
        "onset_primeira_pontuada_s": pontuadas[0][0],
        "duracao_primeira_pontuada_s": pontuadas[0][1],
        "desc_primeira_pontuada": pontuadas[0][2],
        "onset_ultima_pontuada_s": pontuadas[-1][0],
        "duracao_ultima_pontuada_s": pontuadas[-1][1],
        "desc_ultima_pontuada": pontuadas[-1][2],
        "crop_start_s": crop_start,
        "crop_end_s": crop_end,
        "duracao_apos_corte_s": crop_end - crop_start,
        "duracao_apos_corte_h": (crop_end - crop_start) / 3600.0,
        "fracao_do_registro_usada": (crop_end - crop_start) / dur_total_s if dur_total_s else np.nan,
    })

    # Vigilia FORA da janela de corte
    w_fora_s = 0.0
    w_antes_s = 0.0
    w_depois_s = 0.0
    w_dentro_s = 0.0
    for onset, dur, desc in todas:
        if desc != DESC_W:
            continue
        ini, fim = onset, onset + dur
        dentro = max(0.0, min(fim, crop_end) - max(ini, crop_start))
        w_dentro_s += dentro
        antes = max(0.0, min(fim, crop_start) - ini)
        depois = max(0.0, fim - max(ini, crop_end))
        w_antes_s += antes
        w_depois_s += depois
    w_fora_s = w_antes_s + w_depois_s

    linha.update({
        "w_dentro_do_corte_s": w_dentro_s,
        "w_fora_do_corte_s": w_fora_s,
        "w_fora_antes_s": w_antes_s,
        "w_fora_depois_s": w_depois_s,
        "epocas_w_fora": int(w_fora_s // DURACAO_EPOCA_S),
        "epocas_w_dentro": int(w_dentro_s // DURACAO_EPOCA_S),
        "hipnograma_cobre_registro": bool(
            linha["duracao_anotada_total_s"] >= 0.95 * dur_total_s),
    })
    linha["satisfaz_min_epocas_w_fora"] = bool(
        linha["epocas_w_fora"] >= MIN_EPOCAS_W_FORA)
    return linha


def encontra_pares(data_dir: Path) -> list[tuple[Path, Path]]:
    """Pareia PSG e Hypnogram pelo prefixo de sujeito/noite (SC4ssNE)."""
    psgs = sorted(data_dir.rglob("*PSG.edf"))
    hyps = sorted(data_dir.rglob("*Hypnogram.edf"))
    idx = {}
    for h in hyps:
        m = re.match(r"(S[CT]4?\d+[A-Z]?)", h.name)
        if m:
            idx.setdefault(m.group(1)[:6], []).append(h)
    pares = []
    for p in psgs:
        m = re.match(r"(S[CT]4?\d+[A-Z]?)", p.name)
        if not m:
            continue
        cand = idx.get(m.group(1)[:6], [])
        if cand:
            pares.append((p, cand[0]))
    return pares


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Checagem Z12: cobertura dos hipnogramas do Sleep-EDF. Descritivo.")
    ap.add_argument("--data-dir", type=str, required=True,
                    help="pasta onde os arquivos do Sleep-EDF ja estao em cache")
    ap.add_argument("--out-dir", type=str, required=True)
    ap.add_argument("--permitir-download", action="store_true",
                    help="autoriza mne.datasets a baixar o que faltar (default: nao)")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    if not data_dir.exists():
        print(f"[erro] --data-dir nao existe: {data_dir}", file=sys.stderr)
        return 2

    pares = encontra_pares(data_dir)
    if not pares:
        print(f"[erro] nenhum par PSG/Hypnogram encontrado em {data_dir}.\n"
              f"       Este script nao baixa dados por padrao.", file=sys.stderr)
        return 2

    print(f"{len(pares)} pares PSG/Hypnogram encontrados em {data_dir}\n")

    linhas = []
    for i, (psg, hyp) in enumerate(pares, 1):
        try:
            linha = analisa_registro(psg, hyp)
        except Exception as exc:  # registro corrompido nao derruba a passada inteira
            linha = {"psg": psg.name, "hipnograma": hyp.name, "erro": f"{type(exc).__name__}: {exc}"}
        linhas.append(linha)
        print(f"[{i}/{len(pares)}] {psg.name}: "
              f"{linha.get('duracao_registro_h', float('nan')):.1f} h, "
              f"epocas W fora do corte = {linha.get('epocas_w_fora', 'erro')}", flush=True)

    df = pd.DataFrame(linhas)
    df.to_csv(out / "cobertura_hipnogramas.csv", index=False)

    ok = df[df["erro"] == ""] if "erro" in df.columns else df
    n_satisfazem = int(ok.get("satisfaz_min_epocas_w_fora", pd.Series(dtype=bool)).sum())
    criterio = bool(n_satisfazem >= MIN_PARTICIPANTES)

    nao_satisfazem = ok[~ok.get("satisfaz_min_epocas_w_fora", False).astype(bool)] \
        if "satisfaz_min_epocas_w_fora" in ok.columns else pd.DataFrame()

    meta = {
        "criterio_secao_3_2": {
            "min_epocas_w_fora_do_corte": MIN_EPOCAS_W_FORA,
            "min_participantes": MIN_PARTICIPANTES,
            "n_participantes_alvo": N_PARTICIPANTES_ALVO,
        },
        "n_registros_analisados": int(len(df)),
        "n_registros_com_erro": int((df["erro"] != "").sum()) if "erro" in df.columns else 0,
        "n_satisfazem_min_epocas": n_satisfazem,
        "criterio_satisfeito_antes_de_artefato": criterio,
        "ressalva": ("Contagem sobre anotacao, SEM rejeicao de artefato. E um LIMITE SUPERIOR "
                     "do que restara apos a passada de artefato exigida por §3.2."),
        "janela_corte_s": JANELA_CORTE_S,
        "duracao_epoca_s": DURACAO_EPOCA_S,
        "versoes": {"python": platform.python_version(), "numpy": np.__version__,
                    "pandas": pd.__version__},
    }
    try:
        import mne
        meta["versoes"]["mne"] = mne.__version__
    except Exception:
        pass
    (out / "cobertura_hipnogramas_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    dur_med = ok["duracao_registro_h"].median() if "duracao_registro_h" in ok.columns else float("nan")
    usada_med = ok["fracao_do_registro_usada"].median() if "fracao_do_registro_usada" in ok.columns else float("nan")
    cobre = int(ok.get("hipnograma_cobre_registro", pd.Series(dtype=bool)).sum())

    md = [
        "# Cobertura dos hipnogramas do Sleep-EDF — checagem Z12",
        "",
        "> Saida de `cobertura_hipnogramas.py`. **Descritivo**: nenhuma decisao cientifica",
        "> foi tomada por este script. A contagem e sobre anotacao, **sem rejeicao de**",
        "> **artefato**, e portanto e um limite superior do que restara.",
        "",
        "## Criterio, fixado em §3.2 antes desta checagem",
        "",
        f"O braco W(ativo) so e executado se, em pelo menos **{MIN_PARTICIPANTES} dos "
        f"{N_PARTICIPANTES_ALVO} participantes**, existirem **>= {MIN_EPOCAS_W_FORA} epocas** "
        f"anotadas como vigilia fora da janela de +-30 min do corte atual.",
        "",
        "## Resultado",
        "",
        f"- Registros analisados: **{len(df)}** (com erro: {meta['n_registros_com_erro']})",
        f"- Satisfazem o minimo de epocas: **{n_satisfazem}**",
        f"- Criterio de §3.2 (antes de artefato): **{'SATISFEITO' if criterio else 'NAO SATISFEITO'}**",
        "",
        f"- Duracao mediana do registro: **{dur_med:.1f} h**",
        f"- Fracao mediana do registro efetivamente usada pelo corte atual: **{usada_med:.1%}**",
        f"- Registros cujo hipnograma cobre >=95% do sinal: **{cobre}** de {len(ok)}",
        "",
    ]
    if not nao_satisfazem.empty:
        md += ["## Registros que NAO satisfazem, nominalmente", "",
               "| registro | epocas W fora | duracao (h) |", "|---|---|---|"]
        for _, r in nao_satisfazem.iterrows():
            md.append(f"| {r.get('psg','?')} | {r.get('epocas_w_fora','?')} | "
                      f"{r.get('duracao_registro_h', float('nan')):.1f} |")
        md.append("")
    md += [
        "## Como ler este resultado",
        "",
        "Se o criterio **nao** foi satisfeito nem neste limite superior, a decisao ja esta",
        "tomada: o braco W(ativo) nao e executado, e o contraste primario W(calmo) vs N3",
        "segue como esta — que e o desenho pre-declarado de qualquer forma.",
        "",
        "Se foi satisfeito com margem folgada, o braco W(ativo) fica autorizado, ainda",
        "sujeito aos controles de deriva de §14.3 (hora do dia, impedancia, EMG), que sao",
        "confundidores alinhados ao contraste e nao desaparecem por haver dado disponivel.",
        "",
        "Se foi satisfeito por margem apertada, a passada de rejeicao de artefato e",
        "obrigatoria antes da decisao, porque esta contagem a ignora por construcao.",
    ]
    (out / "cobertura_hipnogramas.md").write_text("\n".join(md), encoding="utf-8")

    print("\n" + "=" * 78)
    print(f"Satisfazem o minimo: {n_satisfazem} / {len(ok)}")
    print(f"Criterio §3.2 (antes de artefato): {'SATISFEITO' if criterio else 'NAO SATISFEITO'}")
    print("=" * 78)
    print(f"\nSaidas em {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
