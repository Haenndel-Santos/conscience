#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
poder_vnext01.py — Analise de poder a priori para o PROTOCOLO_VNext_01, etapa 0.5/0.6.

ESTATUTO: codigo congelado antes da execucao. Escrito por agente; executado pelo autor.
Nenhum numero deste arquivo e resultado. Ele nao le dado de EEG e nao toca o dataset-alvo:
opera inteiramente sobre parametros de desenho e sobre desvios-padrao ja congelados em
`scripts_para_rodar/teste_calibrado/resultados_por_sujeito.csv`.

--------------------------------------------------------------------------------------
O QUE ESTE SCRIPT RESPONDE, E O QUE ELE DELIBERADAMENTE NAO FAZ
--------------------------------------------------------------------------------------

Ele separa DUAS perguntas que costumam ser fundidas numa frase enganosa do tipo
"o estudo tem 80% de poder":

  (1) PODER NO CENARIO DE REFERENCIA
      "Com dispersao igual a observada para a LZc residualizada (dp = 0,2346), qual e o
      poder?"

  (2) ROBUSTEZ A INCERTEZA DE DISPERSAO
      "Quanto essa conclusao muda dentro da faixa empirica pre-declarada de dispersoes
      plausiveis?"

A distincao importa porque a dispersao por participante da metrica NOVA (irreversibilidade
normalizada) e DESCONHECIDA. O dp de 0,2346 vem da LZc residualizada — mesma amostra de 36
participantes, mesmo teste, analise ja concluida — e por isso serve como cenario de
referencia legitimo. Ele NAO e uma estimativa da variabilidade da irreversibilidade, e
fixa-lo como se fosse transformaria uma analogia entre metricas numa premissa quantitativa.

O script, portanto, NUNCA procura "o dp que faz o poder passar de 80%". A faixa de
dispersoes e derivada mecanicamente dos dados ja congelados, ANTES de qualquer poder ser
calculado, pela regra da secao seguinte.

--------------------------------------------------------------------------------------
COMO A FAIXA DE DISPERSAO E OBTIDA (regra mecanica, pre-declarada)
--------------------------------------------------------------------------------------

Fonte: `teste_calibrado/resultados_por_sujeito.csv`, coluna `auc_dp` — o desvio-padrao das
AUCs por participante, ja calculado e congelado para cada metrica do projeto.

REGRA DE INCLUSAO: entram na faixa empirica todas as linhas cujo `auc_media` caia no
intervalo [AUC_MIN_REGIME, AUC_MAX_REGIME] = [0,35; 0,65].

Motivo, declarado antes de ver qualquer poder: quando a AUC media se aproxima de 0 ou de 1,
as AUCs por participante ficam comprimidas contra a fronteira e o desvio-padrao despenca por
artefato de limite, nao por a metrica ser mais estavel. As metricas BRUTAS do projeto ficam
em AUC ~0,99 (LZc, PE) ou ~0,14-0,20 (sincronia, MI, indice), com dp de 0,018 a 0,16. Usar
esses valores como cenarios de dispersao para uma metrica que se espera proxima do acaso
inflaria o poder aparente por construcao. A regra os exclui por criterio mecanico — posicao
no eixo da AUC — e nao por escolha caso a caso.

As linhas excluidas sao reportadas nominalmente na saida, com o dp que teriam contribuido,
para que a exclusao seja auditavel e nao silenciosa.

FALLBACK: se menos de MIN_CENARIOS_EMPIRICOS linhas sobreviverem a regra, ou se o CSV nao
for encontrado, o script usa a faixa mecanica pre-declarada de multiplicadores sobre o dp de
referencia — 0,5x / 0,75x / 1,0x / 1,25x / 1,5x sobre 0,2346, isto e, aproximadamente
0,1173 / 0,1760 / 0,2346 / 0,2933 / 0,3519. O fallback e igualmente pre-declarado: ele nao
depende de nada que so se saiba depois de rodar.

--------------------------------------------------------------------------------------
O TESTE SIMULADO E O TESTE REAL, NAO UM SUBSTITUTO ANALITICO
--------------------------------------------------------------------------------------

Cada replica Monte Carlo reproduz o teste primario ja pre-declarado, e nao uma aproximacao
normal conveniente:

  - AUC por participante como unidade (n = N_PARTICIPANTES);
  - Wilcoxon dos postos sinalizados contra 0,5, BILATERAL, `zero_method="wilcox"`,
    identico a `teste_calibrado/teste_auc_por_sujeito.py::teste_uma_amostra`;
  - alfa nominal 0,05.

E reporta o poder sob DOIS criterios, porque a regra de decisao de §6.1 do protocolo e
CONJUNTIVA e nao se reduz a "p < 0,05":

  poder_wilcoxon      — apenas p < 0,05 (o teste isolado);
  poder_regra_suporte — as tres condicoes de SUPORTE simultaneamente:
                        AUC media >= 0,60  E  p < 0,05  E  >= 25 dos 36 acima de 0,5.

O segundo e o operativo. Um desenho pode ter poder alto no primeiro e baixo no segundo, e
relatar so o primeiro seria otimista de um modo que o protocolo nao autoriza.

--------------------------------------------------------------------------------------
DECISAO AUTOMATICA (dois campos, nao um PASS/FAIL)
--------------------------------------------------------------------------------------

  reference_power_pass — o criterio de poder congelado (PODER_ALVO) e satisfeito NO CENARIO
                         DE REFERENCIA (dp = 0,2346).
  robust_power_pass    — o criterio e satisfeito em TODA a faixa empirica pre-declarada.

Se apenas o primeiro passar, isso NAO e falha da simulacao. E um resultado metodologico com
conteudo proprio: a adequacao de n=36 depende de uma suposicao ainda desconhecida sobre a
dispersao da metrica nova, e o relatorio deve dize-lo nesses termos.

--------------------------------------------------------------------------------------
REPRODUTIBILIDADE
--------------------------------------------------------------------------------------

Semente explicita (--seed, default SEED_PADRAO) registrada na saida. Alem disso, o script
repete a estimativa com SEMENTES_VERIFICACAO sementes independentes e reporta a dispersao
entre elas, para demonstrar que o ruido de Monte Carlo nao esta determinando a conclusao
perto do limiar de 80%. Se a faixa entre sementes cruzar PODER_ALVO, o campo
`mc_ruido_cruza_alvo` fica True e o relatorio adverte que n_sim precisa subir.

Uso:
    python poder_vnext01.py --n-sim 2000 --out-dir saida_vnext01

Dependencias: numpy, pandas, scipy (versoes de requirements.txt).
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# ======================================================================================
# CONSTANTES DE DESENHO — todas pre-declaradas. Nenhuma e ajustavel apos ver resultado.
# ======================================================================================

N_PARTICIPANTES = 36          # amostra real do Sleep-EDF apos exclusoes (§3.2 do protocolo)
ALFA = 0.05                   # alfa nominal do teste primario
PODER_ALVO = 0.80             # criterio de poder congelado
AUC_SUPORTE = 0.60            # §6.1 SUPORTE, condicao 1
MIN_SUJEITOS_ACIMA = 25       # §6.1 SUPORTE, condicao 3 (de 36)
DP_REFERENCIA = 0.2346        # LZc residualizada fora da amostra, resultados_por_sujeito.csv

# Regra mecanica de selecao da faixa empirica de dispersao (ver docstring)
AUC_MIN_REGIME = 0.35
AUC_MAX_REGIME = 0.65
MIN_CENARIOS_EMPIRICOS = 3    # abaixo disso, cai no fallback

# Fallback pre-declarado: multiplicadores sobre DP_REFERENCIA
FALLBACK_MULTIPLICADORES = (0.5, 0.75, 1.0, 1.25, 1.5)

# Grade de efeitos: AUC media verdadeira sob a alternativa
AUC_GRADE = (0.50, 0.52, 0.55, 0.58, 0.60, 0.62, 0.65, 0.70, 0.75)

SEED_PADRAO = 20260813
SEMENTES_VERIFICACAO = (20260813, 71, 1729, 424242, 98765)

CSV_DP = Path(__file__).resolve().parent.parent / "teste_calibrado" / "resultados_por_sujeito.csv"


# ======================================================================================
# TESTE PRIMARIO — copia fiel de teste_calibrado/teste_auc_por_sujeito.py
# ======================================================================================

def p_wilcoxon_contra_meio(aucs: np.ndarray) -> float:
    """Wilcoxon bilateral das AUCs por participante contra 0,5.

    Identico ao teste primario ja pre-declarado (teste_uma_amostra). Nao substituir por
    aproximacao normal nem por t-test: o poder tem de ser o poder DESTE teste.
    """
    d = aucs - 0.5
    if np.allclose(d, 0):
        return 1.0
    return float(stats.wilcoxon(d, alternative="two-sided", zero_method="wilcox").pvalue)


def aplica_regra_suporte(aucs: np.ndarray, p: float) -> bool:
    """As tres condicoes CONJUNTAS de SUPORTE (§6.1 do protocolo)."""
    return bool(
        aucs.mean() >= AUC_SUPORTE
        and p < ALFA
        and int(np.sum(aucs > 0.5)) >= MIN_SUJEITOS_ACIMA
    )


# ======================================================================================
# GERACAO DAS REPLICAS
# ======================================================================================

def simula_aucs(rng, auc_media: float, dp: float, n: int) -> np.ndarray:
    """Uma amostra de n AUCs por participante, media `auc_media` e desvio `dp`.

    AUC vive em [0,1], entao uma normal truncada e mais honesta que uma normal livre — que
    produziria AUCs fora do suporte. O truncamento e feito por reamostragem dos valores
    fora do intervalo, preservando media e dispersao alvo tao proximo quanto o suporte
    permite. Em dispersoes altas com media proxima de 0,5 o efeito e pequeno; perto das
    bordas ele comprime, que e exatamente o fenomeno real que a regra AUC_MIN/MAX_REGIME
    identifica nos dados congelados.
    """
    out = rng.normal(auc_media, dp, size=n)
    for _ in range(64):
        fora = (out <= 0.0) | (out >= 1.0)
        if not fora.any():
            break
        out[fora] = rng.normal(auc_media, dp, size=int(fora.sum()))
    return np.clip(out, 1e-9, 1 - 1e-9)


def poder_para(rng, auc_media: float, dp: float, n_sim: int) -> dict:
    """Poder sob os dois criterios, para um par (efeito, dispersao)."""
    n_wil = 0
    n_regra = 0
    for _ in range(n_sim):
        aucs = simula_aucs(rng, auc_media, dp, N_PARTICIPANTES)
        p = p_wilcoxon_contra_meio(aucs)
        if p < ALFA:
            n_wil += 1
            # a regra so pode passar se o teste passou; avaliada mesmo assim por clareza
        if aplica_regra_suporte(aucs, p):
            n_regra += 1
    return {
        "poder_wilcoxon": n_wil / n_sim,
        "poder_regra_suporte": n_regra / n_sim,
    }


# ======================================================================================
# FAIXA EMPIRICA DE DISPERSAO
# ======================================================================================

def carrega_faixa_dispersao(csv_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Aplica a regra mecanica e devolve (incluidas, excluidas, origem).

    `origem` e "empirica" ou "fallback". A decisao e tomada aqui, ANTES de qualquer poder
    ser calculado, e nao depende de nenhum resultado.
    """
    if not csv_path.exists():
        print(f"[aviso] {csv_path} nao encontrado — usando o fallback pre-declarado.",
              file=sys.stderr)
        return _fallback(), pd.DataFrame(), "fallback"

    df = pd.read_csv(csv_path)
    faltando = {"bloco", "metrica", "tipo", "auc_media", "auc_dp"} - set(df.columns)
    if faltando:
        print(f"[aviso] colunas ausentes em {csv_path.name}: {sorted(faltando)} — fallback.",
              file=sys.stderr)
        return _fallback(), pd.DataFrame(), "fallback"

    df = df[df["bloco"].astype(str).str.startswith("sono")].copy()
    df["rotulo"] = df["bloco"].astype(str) + " / " + df["metrica"].astype(str) + " / " + df["tipo"].astype(str)

    no_regime = df["auc_media"].between(AUC_MIN_REGIME, AUC_MAX_REGIME)
    incluidas = df[no_regime][["rotulo", "auc_media", "auc_dp"]].copy()
    excluidas = df[~no_regime][["rotulo", "auc_media", "auc_dp"]].copy()

    if len(incluidas) < MIN_CENARIOS_EMPIRICOS:
        print(f"[aviso] apenas {len(incluidas)} cenarios sobreviveram a regra de regime "
              f"(minimo {MIN_CENARIOS_EMPIRICOS}) — usando o fallback pre-declarado.",
              file=sys.stderr)
        return _fallback(), excluidas, "fallback"

    incluidas = incluidas.sort_values("auc_dp").reset_index(drop=True)
    return incluidas, excluidas.sort_values("auc_dp").reset_index(drop=True), "empirica"


def _fallback() -> pd.DataFrame:
    return pd.DataFrame({
        "rotulo": [f"fallback {m:g}x DP_REFERENCIA" for m in FALLBACK_MULTIPLICADORES],
        "auc_media": [np.nan] * len(FALLBACK_MULTIPLICADORES),
        "auc_dp": [round(m * DP_REFERENCIA, 4) for m in FALLBACK_MULTIPLICADORES],
    })


# ======================================================================================
# MAIN
# ======================================================================================

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Poder a priori do VNext-01 (etapa 0.5/0.6). Nao le dado de EEG.")
    ap.add_argument("--n-sim", type=int, default=2000,
                    help="replicas Monte Carlo por celula. O protocolo fixa 2000; valores "
                         "menores sao permitidos SOMENTE para smoke test e ficam marcados "
                         "como tal na saida.")
    ap.add_argument("--out-dir", type=str, required=True)
    ap.add_argument("--seed", type=int, default=SEED_PADRAO)
    ap.add_argument("--pular-verificacao-sementes", action="store_true",
                    help="pula a checagem multi-semente (apenas para smoke test rapido)")
    args = ap.parse_args()

    if args.n_sim < 2000:
        print(f"[AVISO] n_sim={args.n_sim} < 2000. O protocolo (§10.3) fixa 2000. "
              f"Esta rodada sera marcada como SMOKE TEST e nao pode fechar a etapa 0.6.",
              file=sys.stderr)

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    incluidas, excluidas, origem = carrega_faixa_dispersao(CSV_DP)
    dps = [float(x) for x in incluidas["auc_dp"].tolist()]
    if DP_REFERENCIA not in dps:
        dps.append(DP_REFERENCIA)
    dps = sorted(set(round(d, 4) for d in dps))

    print(f"Origem da faixa de dispersao: {origem}")
    print(f"Cenarios de dispersao ({len(dps)}): {dps}")
    print(f"Referencia (LZc residualizada): {DP_REFERENCIA}")
    if not excluidas.empty:
        print(f"\nExcluidas pela regra de regime AUC in [{AUC_MIN_REGIME}; {AUC_MAX_REGIME}] "
              f"— nao entram na faixa, listadas para auditoria:")
        print(excluidas.to_string(index=False))
    print()

    rng = np.random.default_rng(args.seed)
    linhas = []
    for dp in dps:
        for auc in AUC_GRADE:
            r = poder_para(rng, auc, dp, args.n_sim)
            linhas.append({
                "dp_auc_por_participante": dp,
                "eh_referencia": bool(abs(dp - DP_REFERENCIA) < 1e-9),
                "auc_media_verdadeira": auc,
                "n_participantes": N_PARTICIPANTES,
                "n_sim": args.n_sim,
                **r,
            })
            print(f"  dp={dp:.4f}  AUC={auc:.2f}  "
                  f"poder_wilcoxon={r['poder_wilcoxon']:.3f}  "
                  f"poder_regra={r['poder_regra_suporte']:.3f}", flush=True)

    df = pd.DataFrame(linhas)
    df.to_csv(out / "poder_vnext01.csv", index=False)

    # ---- decisao: os dois campos, no criterio operativo (regra de suporte) ----
    def passa(sub: pd.DataFrame) -> bool:
        alvo = sub[sub["auc_media_verdadeira"] >= AUC_SUPORTE]
        return bool(not alvo.empty and (alvo["poder_regra_suporte"] >= PODER_ALVO).any())

    ref = df[df["eh_referencia"]]
    reference_power_pass = passa(ref)
    robust_power_pass = all(passa(df[df["dp_auc_por_participante"] == dp]) for dp in dps)

    # menor AUC detectavel com PODER_ALVO, por dispersao
    mde = {}
    for dp in dps:
        sub = df[(df["dp_auc_por_participante"] == dp) &
                 (df["poder_regra_suporte"] >= PODER_ALVO)]
        mde[dp] = float(sub["auc_media_verdadeira"].min()) if not sub.empty else None

    # ---- ruido de Monte Carlo: mesmas celulas, sementes independentes ----
    mc = {}
    if not args.pular_verificacao_sementes:
        alvo_auc = AUC_SUPORTE
        vals = []
        for s in SEMENTES_VERIFICACAO:
            r = poder_para(np.random.default_rng(s), alvo_auc, DP_REFERENCIA, args.n_sim)
            vals.append(r["poder_regra_suporte"])
        lo, hi = min(vals), max(vals)
        mc = {
            "celula": f"AUC={alvo_auc}, dp={DP_REFERENCIA}",
            "sementes": list(SEMENTES_VERIFICACAO),
            "poderes": vals,
            "min": lo, "max": hi, "amplitude": hi - lo,
            "cruza_alvo": bool(lo < PODER_ALVO <= hi),
        }
        print(f"\nRuido de Monte Carlo na celula de referencia: {vals} "
              f"(amplitude {hi - lo:.3f})")
        if mc["cruza_alvo"]:
            print(f"[AVISO] a faixa entre sementes cruza {PODER_ALVO}. "
                  f"n_sim precisa subir antes de a conclusao ser usada.", file=sys.stderr)

    meta = {
        "estatuto": "SMOKE TEST" if args.n_sim < 2000 else "rodada valida para a etapa 0.6",
        "origem_faixa_dispersao": origem,
        "cenarios_dp": dps,
        "dp_referencia": DP_REFERENCIA,
        "excluidas_pela_regra_de_regime": excluidas.to_dict(orient="records"),
        "regra_de_regime": {"auc_min": AUC_MIN_REGIME, "auc_max": AUC_MAX_REGIME},
        "teste": "Wilcoxon bilateral contra 0,5, zero_method=wilcox, alfa=0,05",
        "regra_suporte": {"auc_min": AUC_SUPORTE, "alfa": ALFA,
                          "min_sujeitos_acima_05": MIN_SUJEITOS_ACIMA,
                          "n_participantes": N_PARTICIPANTES},
        "poder_alvo": PODER_ALVO,
        "n_sim": args.n_sim,
        "seed": args.seed,
        "reference_power_pass": reference_power_pass,
        "robust_power_pass": robust_power_pass,
        "mde_por_dispersao": mde,
        "mc_ruido": mc,
        "versoes": {"python": platform.python_version(),
                    "numpy": np.__version__, "pandas": pd.__version__,
                    "scipy": stats.__name__ and __import__("scipy").__version__},
    }
    (out / "poder_vnext01_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 78)
    print(f"reference_power_pass = {reference_power_pass}")
    print(f"robust_power_pass    = {robust_power_pass}")
    print("=" * 78)
    if reference_power_pass and not robust_power_pass:
        print(
            "\nLeitura pre-declarada deste caso: nao e falha da simulacao. E um resultado\n"
            "metodologico — a adequacao de n=36 depende de uma suposicao ainda desconhecida\n"
            "sobre a dispersao da irreversibilidade por participante. Qualquer relatorio deve\n"
            "dizer 'tem poder suficiente SE a metrica nova tiver dispersao proxima a da LZc\n"
            "residualizada', nunca 'o estudo tem 80% de poder'."
        )
    print(f"\nSaidas: {out / 'poder_vnext01.csv'}\n         {out / 'poder_vnext01_meta.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
