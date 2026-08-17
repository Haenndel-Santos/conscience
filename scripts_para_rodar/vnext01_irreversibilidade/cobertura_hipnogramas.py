#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cobertura_hipnogramas.py — Checagem Z12 do PROTOCOLO_VNext_01, etapa 0.3/0.4.

ESTATUTO: codigo congelado antes da execucao. Escrito por agente; executado pelo autor.
Nenhum numero deste arquivo e resultado.

--------------------------------------------------------------------------------------
CORRECOES DE 2026-08-17, ANTES DO MERGE E ANTES DE QUALQUER EXECUCAO
--------------------------------------------------------------------------------------

Registradas em `embasamento/revisao_fase0_pre_merge.md` e na §16 do protocolo.

  F5  O DENOMINADOR DE §3.2 NAO ERA IMPOSTO. A versao anterior contava sobre TODOS os pares
      PSG/hipnograma encontrados no cache — 39 — e comparava contra MIN_PARTICIPANTES=30, mas
      §3.2 diz "30 dos 36 participantes", e os 36 sao os que sobreviveram as exclusoes (3 sem
      N3, 2 indices ausentes do dataset). Os 3 sem N3 nao eram identificados nem removidos.
      Cenario concreto em que o veredito invertia: se os 3 sem N3 satisfizessem o minimo de
      vigilia e exatamente 30 dos 39 satisfizessem, o script imprimia SATISFEITO enquanto
      apenas 27 dos 36 analisados satisfaziam. Agora a coorte e derivada pela mesma regra de
      exclusao (ausencia de N3 anotado DENTRO da janela de corte, que e onde o pipeline
      epoca), a contagem e feita sobre ela, e se o tamanho derivado nao for exatamente
      N_PARTICIPANTES_ALVO o script REPORTA MAS NAO EMITE VEREDITO — porque nesse caso ele
      nao esta contando a coorte de §3.2, e um veredito seria sobre outra amostra.
      `--coorte` aceita uma lista explicita de registros, que tem precedencia sobre a
      derivacao, para o caso de a regra derivada nao reproduzir os 3 exatos.

  F6  A COBERTURA DO HIPNOGRAMA ERA VERDADEIRA POR CONSTRUCAO. O booleano usava a duracao
      ANOTADA total, que inclui `Sleep stage ?`; medido nestes arquivos, a anotacao `?` final
      estende o total a 24,00 h contra 21,8-23,4 h de sinal, de modo que o indicador seria
      verdadeiro mesmo num hipnograma que nao pontuasse nada. Passou a usar a duracao
      PONTUADA, que e a quantidade que responde a pergunta, e as duas saem no CSV.

  F9  `--permitir-download` era aceito e nunca usado, em nenhum caminho. Removido: o script
      nao baixa nada, e uma flag que promete comportamento inexistente e pior que nenhuma.

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
    python cobertura_hipnogramas.py --data-dir <pasta_cache> --out-dir saida --coorte os36.txt

`--data-dir` e a pasta onde `mne.datasets.sleep_physionet` ja baixou os arquivos. O script
NAO baixa nada, em nenhum caminho.

Codigos de saida: 0 = veredito emitido; 2 = erro de entrada; 3 = rodou, mas a coorte contada
nao tem o tamanho da coorte de §3.2 e nenhum veredito foi emitido (ver F5 acima).

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

# Estagios que o pipeline mapeia para N3 (`analise_sono_v2.py::ANNOTATION_TO_EVENT`). A
# exclusao que leva 39 -> 36 e "sem epocas de N3", e e reproduzida aqui sobre anotacao, para
# que a contagem de §3.2 caia sobre a coorte de §3.2 e nao sobre o cache inteiro (F5).
DESC_N3 = ("Sleep stage 3", "Sleep stage 4")


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
    n3_dentro_s = 0.0
    for onset, dur, desc in todas:
        ini, fim = onset, onset + dur
        if desc in DESC_N3:
            n3_dentro_s += max(0.0, min(fim, crop_end) - max(ini, crop_start))
            continue
        if desc != DESC_W:
            continue
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
        "n3_dentro_do_corte_s": n3_dentro_s,
        "epocas_n3_dentro": int(n3_dentro_s // DURACAO_EPOCA_S),
        # Reproduz a exclusao 39 -> 36 sobre anotacao (F5): sem N3 dentro do corte, o registro
        # nao entra na amostra de n=36 e nao pode contar para o criterio de §3.2.
        "tem_n3_no_corte": bool(n3_dentro_s > 0.0),
        # F6: a pergunta e se o hipnograma PONTUA o registro, e `duracao_anotada_total_s`
        # inclui `Sleep stage ?`, que sozinho pode cobrir mais que o proprio sinal. As duas
        # saem no CSV; o booleano usa a pontuada, que e a que responde.
        "hipnograma_pontua_registro": bool(
            linha["duracao_pontuada_total_s"] >= 0.95 * dur_total_s),
        "fracao_do_registro_pontuada": (
            linha["duracao_pontuada_total_s"] / dur_total_s if dur_total_s else np.nan),
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
    ap.add_argument("--coorte", type=str, default=None,
                    help="arquivo de texto com um nome de registro PSG por linha, delimitando "
                         "a coorte de 36 de §3.2. Tem precedencia sobre a derivacao automatica "
                         "pela ausencia de N3. Use se a regra derivada nao reproduzir "
                         "exatamente os 3 registros excluidos do projeto.")
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

    lidos = df[df["erro"] == ""] if "erro" in df.columns else df

    # ---- coorte de §3.2: os 36, nao o cache inteiro (correcao F5) ----
    if args.coorte:
        nomes = {ln.strip() for ln in Path(args.coorte).read_text(encoding="utf-8").splitlines()
                 if ln.strip() and not ln.strip().startswith("#")}
        ok = lidos[lidos["psg"].isin(nomes)].copy()
        origem_coorte = f"lista explicita ({args.coorte})"
        fora_da_coorte = lidos[~lidos["psg"].isin(nomes)].copy()
    else:
        ok = lidos[lidos.get("tem_n3_no_corte", False).astype(bool)].copy() \
            if "tem_n3_no_corte" in lidos.columns else lidos.copy()
        origem_coorte = "derivada: registros com N3 anotado dentro da janela de corte"
        fora_da_coorte = lidos[~lidos.get("tem_n3_no_corte", False).astype(bool)].copy() \
            if "tem_n3_no_corte" in lidos.columns else pd.DataFrame()

    coorte_confere = bool(len(ok) == N_PARTICIPANTES_ALVO)
    n_satisfazem = int(ok.get("satisfaz_min_epocas_w_fora", pd.Series(dtype=bool)).sum())

    # O veredito so e emitido se a coorte contada FOR a coorte de §3.2. Contar 30 de 39 e
    # responder a outra pergunta, e nao ha leitura em que isso seja conservador.
    criterio = bool(n_satisfazem >= MIN_PARTICIPANTES) if coorte_confere else None

    nao_satisfazem = ok[~ok.get("satisfaz_min_epocas_w_fora", False).astype(bool)] \
        if "satisfaz_min_epocas_w_fora" in ok.columns else pd.DataFrame()

    meta = {
        "criterio_secao_3_2": {
            "min_epocas_w_fora_do_corte": MIN_EPOCAS_W_FORA,
            "min_participantes": MIN_PARTICIPANTES,
            "n_participantes_alvo": N_PARTICIPANTES_ALVO,
        },
        "n_registros_encontrados": int(len(df)),
        "n_registros_com_erro": int((df["erro"] != "").sum()) if "erro" in df.columns else 0,
        "coorte": {
            "origem": origem_coorte,
            "n": int(len(ok)),
            "confere_com_n_alvo": coorte_confere,
            "registros": ok["psg"].tolist() if "psg" in ok.columns else [],
            "fora_da_coorte": (fora_da_coorte["psg"].tolist()
                               if "psg" in fora_da_coorte.columns else []),
        },
        "n_satisfazem_min_epocas": n_satisfazem,
        "criterio_satisfeito_antes_de_artefato": criterio,
        "veredito_emitido": coorte_confere,
        "ressalva": ("Contagem sobre anotacao, SEM rejeicao de artefato. E um LIMITE SUPERIOR "
                     "do que restara apos a passada de artefato exigida por §3.2."),
        "ressalva_coorte": (
            "O criterio de §3.2 e sobre os 36 participantes que sobreviveram as exclusoes do "
            "projeto. Se a coorte derivada aqui nao tiver exatamente esse tamanho, nenhum "
            "veredito e emitido: passe --coorte com a lista dos 36."),
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
    pont_med = ok["fracao_do_registro_pontuada"].median() if "fracao_do_registro_pontuada" in ok.columns else float("nan")
    pontua = int(ok.get("hipnograma_pontua_registro", pd.Series(dtype=bool)).sum())

    if criterio is None:
        veredito = (f"**NAO EMITIDO** — a coorte contada tem {len(ok)} registros, e o criterio "
                    f"de §3.2 e sobre {N_PARTICIPANTES_ALVO}")
    else:
        veredito = f"**{'SATISFEITO' if criterio else 'NAO SATISFEITO'}**"

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
        "## Coorte contada",
        "",
        f"- Registros encontrados no cache: **{len(df)}** (com erro: {meta['n_registros_com_erro']})",
        f"- Coorte de §3.2: **{len(ok)}** registros — origem: {origem_coorte}",
        f"- Confere com os {N_PARTICIPANTES_ALVO} do projeto: "
        f"**{'sim' if coorte_confere else 'NAO'}**",
        "",
        "## Resultado",
        "",
        f"- Satisfazem o minimo de epocas, dentro da coorte: **{n_satisfazem}** de {len(ok)}",
        f"- Criterio de §3.2 (antes de artefato): {veredito}",
        "",
        f"- Duracao mediana do registro: **{dur_med:.1f} h**",
        f"- Fracao mediana do registro efetivamente usada pelo corte atual: **{usada_med:.1%}**",
        f"- Fracao mediana do registro **pontuada** pelo hipnograma: **{pont_med:.1%}**",
        f"- Registros cujo hipnograma pontua >=95% do sinal: **{pontua}** de {len(ok)}",
        "",
    ]
    if not coorte_confere:
        md += [
            "> ⚠️ **Nenhum veredito foi emitido.** A coorte derivada aqui nao tem o tamanho da",
            f"> coorte de §3.2 ({len(ok)} contra {N_PARTICIPANTES_ALVO}). Contar 30 de um",
            "> denominador diferente responde a outra pergunta, e nao ha leitura em que isso",
            "> seja conservador: passe `--coorte` com a lista dos 36 registros do projeto e",
            "> rode de novo.",
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
    print(f"Coorte contada: {len(ok)} ({origem_coorte})")
    print(f"Satisfazem o minimo: {n_satisfazem} / {len(ok)}")
    if criterio is None:
        print(f"Criterio §3.2: VEREDITO NAO EMITIDO — a coorte tem {len(ok)} registros, e o "
              f"criterio e sobre {N_PARTICIPANTES_ALVO}. Passe --coorte com a lista dos 36.")
    else:
        print(f"Criterio §3.2 (antes de artefato): "
              f"{'SATISFEITO' if criterio else 'NAO SATISFEITO'}")
    print("=" * 78)
    print(f"\nSaidas em {out}/")
    return 0 if criterio is not None else 3


if __name__ == "__main__":
    raise SystemExit(main())
