#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
poder_vnext01.py — Analise de poder a priori para o PROTOCOLO_VNext_01, etapa 0.5/0.6.

ESTATUTO: codigo congelado antes da execucao. Escrito por agente; executado pelo autor.
Nenhum numero deste arquivo e resultado. Ele nao le dado de EEG e nao toca o dataset-alvo:
opera inteiramente sobre parametros de desenho e sobre desvios-padrao ja congelados em
`scripts_para_rodar/teste_calibrado/resultados_por_sujeito.csv`.

--------------------------------------------------------------------------------------
CORRECOES DE 2026-08-17, ANTES DO MERGE E ANTES DE QUALQUER EXECUCAO
--------------------------------------------------------------------------------------

Registradas em `embasamento/revisao_fase0_pre_merge.md` e na §16 do protocolo. Todas sao
anteriores a qualquer resultado, e nenhuma delas foi motivada por uma saida observada — o
script nunca rodou sobre nada.

  F1  A DECISAO ERA VACUA. `passa()` usava `.any()` sobre todos os efeitos >= 0,60, de modo
      que o maior efeito da grade (AUC=0,75) decidia, e os dois campos saiam True para
      qualquer dispersao. O portao de §10.3 e o poder no MENOR EFEITO DE INTERESSE de §6.4,
      e ele agora e avaliado numa ancora declarada (AUC_ANCORA_PODER), nao no melhor caso.

  F3  O GERADOR NAO ENTREGAVA O QUE A LINHA DECLARAVA. A truncagem por reamostragem de uma
      normal produzia media e dp realizados diferentes dos alvos (erros medidos de -11% a
      -24% no dp, e a celula rotulada AUC=0,60 simulava media 0,582). Pior: para boa parte
      da grade o par (media, dp) e INVIAVEL para qualquer normal truncada em [0,1] — o
      limite superior do dp de uma truncada tende a 0,2887 (o caso uniforme) quando a media
      e 0,5, e cai abaixo disso fora do centro. Trocado por uma Beta parametrizada em
      (media, dp), que vive em (0,1) por construcao, acerta os dois momentos em forma
      fechada e nao precisa de truncagem, reamostragem nem clip. Media e dp REALIZADOS
      passam a ser reportados em cada linha, para o CSV nao afirmar o que nao faz.

  F4  A FAIXA "EMPIRICA" ERA DEGENERADA. A regra de regime deixa passar 14 linhas, todas
      residualizadas, com dp em [0,2248; 0,2845] — 27% de amplitude, mais estreita que o
      proprio fallback pre-declarado (0,1173-0,3519). `robust_power_pass` era 13
      quase-repeticoes do cenario de referencia. A grade passa a ser a UNIAO das duas
      familias ja congeladas, sem numero novo. Custo: ~0,7 ms por replica, ~4 min de parede.

  F5/F6 em `cobertura_hipnogramas.py`.

  F2 SEGUE ABERTA, e e do autor. §6.4 fixa o menor efeito de interesse em AUC=0,55; §10.2
      deriva o limiar de suporte 0,60 do dz que JA da 80% de poder em n=36, isto e, 0,60 e
      aproximadamente o efeito minimo detectavel; e §10.3 exige 80% de poder no menor efeito
      de interesse. Os tres nao podem valer juntos. Este script nao resolve a tensao: ele a
      MEDE e a reporta em campos separados. AUC_ANCORA_PODER carrega hoje o valor que §10.3
      declara literalmente (0,55); mudar essa constante e emenda de protocolo e exige
      registro na §16, nao ajuste de codigo.

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

UNIAO COM A FAMILIA DE MULTIPLICADORES (correcao F4): a faixa varrida e a uniao das linhas
que sobrevivem a regra com a familia pre-declarada de multiplicadores sobre o dp de
referencia — 0,5x / 0,75x / 1,0x / 1,25x / 1,5x sobre 0,2346, isto e, aproximadamente
0,1173 / 0,1760 / 0,2346 / 0,2933 / 0,3519.

O motivo da uniao, declarado antes de qualquer poder ser calculado: as 14 linhas que a regra
admite sao TODAS residualizadas, agrupadas em dois blocos estreitos (~0,225-0,235, a familia
LZc, contada seis vezes entre `sono` e `sono-multi`; ~0,267-0,285, a familia
PE/sincronia/MI/indice), e a amplitude total e de 27%. Uma varredura confinada a esse
intervalo nao e teste de robustez: a dispersao da metrica NOVA e desconhecida e pode estar
fora dele pelos dois lados. A familia de multiplicadores era o fallback e e mais larga que o
caminho que a substituia — usar as duas nao introduz nenhum numero que nao estivesse ja
congelado, e nao depende de nada que so se saiba depois de rodar.

Se o CSV nao for encontrado ou sobrarem menos de MIN_CENARIOS_EMPIRICOS linhas, o script
roda apenas com a familia de multiplicadores, mas SOMENTE se `--permitir-fallback` for
passado explicitamente. Sem a flag ele para com erro, em vez de degradar silenciosamente com
um aviso em stderr que ninguem le.

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
DECISAO AUTOMATICA — ANCORADA NUM EFEITO DECLARADO, NAO NO MELHOR CASO
--------------------------------------------------------------------------------------

Todo campo de decisao e avaliado EM AUC_ANCORA_PODER, o menor efeito de interesse de §6.4,
que e o efeito que §10.3 nomeia no portao. Nao "em algum efeito da grade", nao "no melhor
caso". Como o poder cresce monotonicamente com o efeito, avaliar na ancora e a leitura mais
exigente compativel com o texto do protocolo, e a monotonia e verificada em tempo de execucao
em vez de assumida.

  reference_power_pass — PODER_ALVO satisfeito na ancora, no CENARIO DE REFERENCIA
                         (dp = 0,2346), sob a regra CONJUNTIVA de §6.1.
  robust_power_pass    — o mesmo, em TODA a faixa varrida.

E ao lado deles, porque uma decisao booleana esconde a informacao que interessa:

  poder_na_ancora_*       — o poder na ancora, sob os dois criterios, por dispersao.
  poder_no_suporte_*      — idem em AUC_SUPORTE (0,60), que NAO e o portao mas e o limiar que
                            a regra de suporte usa. Cuidado de leitura: como a regra compara
                            a AUC AMOSTRAL contra 0,60, o poder em AUC verdadeira = 0,60 e
                            <= 50% por construcao — a media amostral fica acima do limiar em
                            metade das replicas. Nao existe leitura desse campo que seja
                            simultaneamente 80% e ancorada em 0,60.
  mde_por_dispersao       — o menor efeito da grade que atinge PODER_ALVO. E a saida
                            metodologicamente informativa, e sobrevive a qualquer resolucao
                            de F2, porque nao depende de escolher uma ancora.

Se `reference_power_pass` passar e `robust_power_pass` nao, isso NAO e falha da simulacao. E
um resultado metodologico com conteudo proprio: a adequacao de n=36 depende de uma suposicao
ainda desconhecida sobre a dispersao da metrica nova, e o relatorio deve dize-lo nesses
termos. Se NENHUM dos dois passar, a leitura pre-declarada tambem existe e esta no fim de
`main()`: o portao de §10.3 nao e satisfeito neste n, e a decisao passa a ser de desenho
(F2), nao de simulacao.

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

# ANCORA DA DECISAO (correcao F1). §10.3: "nenhum braco confirmatorio e executado sem que a
# analise de poder mostre que ele detecta o MENOR EFEITO DE INTERESSE (§6.4) com pelo menos
# 80% de poder", e §6.4 fixa esse menor efeito de interesse em AUC = 0,55. Este e, portanto,
# o efeito que o portao do protocolo nomeia, lido literalmente.
#
# MUDAR ESTE VALOR E EMENDA DE PROTOCOLO, NAO AJUSTE DE CODIGO: exige registro na §16 com
# data e motivo, e — se feito depois de ver qualquer saida — rebaixa a analise afetada de
# confirmatoria a exploratoria pela regra de congelamento. A tensao entre §6.4, §10.2 e §10.3
# esta descrita no cabecalho (F2) e nao e resolvida aqui.
AUC_ANCORA_PODER = 0.55

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

# Tolerancia da checagem de fidelidade do gerador (correcao F3). A Beta acerta os momentos em
# forma fechada, entao o unico desvio esperado e o erro de amostragem — e por isso a tolerancia
# ESCALA com ele em vez de ser uma constante: uma folga fixa e frouxa demais com n_sim=2000 e
# apertada demais num smoke test, e nos dois casos mede a coisa errada. O criterio e o desvio em
# multiplos do erro-padrao da propria estatistica, com um piso absoluto para nao perseguir ruido
# numerico quando o dp e minusculo.
SIGMAS_FIDELIDADE = 5.0
PISO_FIDELIDADE = 0.002

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

def parametros_beta(auc_media: float, dp: float) -> tuple[float, float, bool]:
    """Parametros (a, b) da Beta com media `auc_media` e desvio-padrao `dp`.

    Por que Beta, e nao a normal truncada da versao anterior (correcao F3): a AUC por
    participante vive em (0,1), e a Beta vive nesse suporte POR CONSTRUCAO — sem truncagem,
    sem reamostragem, sem clip. O mapa (media, dp) -> (a, b) e fechado, de modo que os dois
    momentos alvo sao acertados exatamente em vez de aproximadamente:

        k = media*(1-media)/dp^2 - 1;   a = media*k;   b = (1-media)*k

    A versao anterior truncava uma normal por reamostragem e errava os dois momentos (media
    0,582 onde pedia 0,600; dp entre 11% e 24% abaixo do alvo). E o problema nao era de
    implementacao: o par (media, dp) e simplesmente INVIAVEL para uma normal truncada em boa
    parte da grade — o dp maximo de uma truncada em [0,1] tende a 0,2887 (o limite uniforme)
    quando a media e 0,5, e cai abaixo disso fora do centro, de modo que celulas como
    (0,75; 0,2845) nao existem naquela familia.

    A VIABILIDADE que resta e universal, nao um limite da Beta: nenhuma distribuicao em [0,1]
    com media m tem desvio-padrao >= sqrt(m*(1-m)) (o supremo e a distribuicao de dois pontos
    em 0 e 1). Celulas que violam isso sao marcadas inviaveis e nao produzem poder.

    Ressalva de forma, registrada porque momentos nao determinam a distribuicao e o Wilcoxon
    e sensivel a forma: com a e b > 1 a Beta e unimodal; abaixo disso vira U ou J. Na regiao
    que decide — a ancora (0,55; 0,2346) da a=1,92 e b=1,57 — ela e unimodal. Os cantos que
    ficam em forma de U sao cantos onde nenhuma familia seria gaussiana, porque o dp pedido
    esta perto do supremo teorico do suporte. A coluna `forma_unimodal` do CSV diz quais.
    """
    var = dp * dp
    limite = auc_media * (1.0 - auc_media)
    if not (0.0 < auc_media < 1.0) or var <= 0.0 or var >= limite:
        return float("nan"), float("nan"), False
    k = limite / var - 1.0
    return auc_media * k, (1.0 - auc_media) * k, True


def simula_aucs(rng, auc_media: float, dp: float, n: int) -> np.ndarray:
    """Uma amostra de n AUCs por participante, com media e dp exatamente os pedidos."""
    a, b, viavel = parametros_beta(auc_media, dp)
    if not viavel:
        raise ValueError(
            f"par (media={auc_media}, dp={dp}) inviavel em [0,1]: dp^2={dp * dp:.4f} >= "
            f"media*(1-media)={auc_media * (1 - auc_media):.4f}. Nenhuma distribuicao no "
            f"suporte da AUC tem esses dois momentos.")
    return rng.beta(a, b, size=n)


def poder_para(rng, auc_media: float, dp: float, n_sim: int) -> dict:
    """Poder sob os dois criterios, para um par (efeito, dispersao).

    Reporta tambem media e dp REALIZADOS sobre todas as replicas (correcao F3): a fidelidade
    do gerador passa a ser verificada em cada rodada em vez de afirmada no docstring.
    """
    a, b, viavel = parametros_beta(auc_media, dp)
    if not viavel:
        return {
            "poder_wilcoxon": float("nan"),
            "poder_regra_suporte": float("nan"),
            "media_realizada": float("nan"),
            "dp_realizado": float("nan"),
            "alvo_viavel": False,
            "forma_unimodal": False,
        }

    n_wil = 0
    n_regra = 0
    soma = 0.0
    soma_q = 0.0
    n_val = 0
    for _ in range(n_sim):
        aucs = simula_aucs(rng, auc_media, dp, N_PARTICIPANTES)
        soma += float(aucs.sum())
        soma_q += float(np.square(aucs).sum())
        n_val += aucs.size
        p = p_wilcoxon_contra_meio(aucs)
        if p < ALFA:
            n_wil += 1
            # a regra so pode passar se o teste passou; avaliada mesmo assim por clareza
        if aplica_regra_suporte(aucs, p):
            n_regra += 1

    media_real = soma / n_val
    dp_real = float(np.sqrt(max(soma_q / n_val - media_real ** 2, 0.0)))
    return {
        "poder_wilcoxon": n_wil / n_sim,
        "poder_regra_suporte": n_regra / n_sim,
        "media_realizada": media_real,
        "dp_realizado": dp_real,
        "alvo_viavel": True,
        "forma_unimodal": bool(a > 1.0 and b > 1.0),
    }


# ======================================================================================
# FAIXA DE DISPERSAO
# ======================================================================================

def carrega_faixa_dispersao(csv_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Aplica a regra mecanica e devolve (empiricas, excluidas, origem).

    `origem` e "empirica" ou "indisponivel". A decisao e tomada aqui, ANTES de qualquer poder
    ser calculado, e nao depende de nenhum resultado. A uniao com a familia de multiplicadores
    (correcao F4) e feita por `monta_grade_dispersao`, nao aqui — esta funcao continua sem
    referenciar nada relacionado a poder, e ha um teste de bytecode que verifica isso.
    """
    if not csv_path.exists():
        print(f"[aviso] {csv_path} nao encontrado.", file=sys.stderr)
        return pd.DataFrame(), pd.DataFrame(), "indisponivel"

    df = pd.read_csv(csv_path)
    faltando = {"bloco", "metrica", "tipo", "auc_media", "auc_dp"} - set(df.columns)
    if faltando:
        print(f"[aviso] colunas ausentes em {csv_path.name}: {sorted(faltando)}.",
              file=sys.stderr)
        return pd.DataFrame(), pd.DataFrame(), "indisponivel"

    df = df[df["bloco"].astype(str).str.startswith("sono")].copy()
    df["rotulo"] = df["bloco"].astype(str) + " / " + df["metrica"].astype(str) + " / " + df["tipo"].astype(str)

    no_regime = df["auc_media"].between(AUC_MIN_REGIME, AUC_MAX_REGIME)
    incluidas = df[no_regime][["rotulo", "auc_media", "auc_dp"]].copy()
    excluidas = df[~no_regime][["rotulo", "auc_media", "auc_dp"]].copy()

    if len(incluidas) < MIN_CENARIOS_EMPIRICOS:
        print(f"[aviso] apenas {len(incluidas)} cenarios sobreviveram a regra de regime "
              f"(minimo {MIN_CENARIOS_EMPIRICOS}).", file=sys.stderr)
        return pd.DataFrame(), excluidas, "indisponivel"

    incluidas = incluidas.sort_values("auc_dp").reset_index(drop=True)
    return incluidas, excluidas.sort_values("auc_dp").reset_index(drop=True), "empirica"


def familia_multiplicadores() -> pd.DataFrame:
    """A familia pre-declarada de multiplicadores sobre DP_REFERENCIA."""
    return pd.DataFrame({
        "rotulo": [f"{m:g}x DP_REFERENCIA" for m in FALLBACK_MULTIPLICADORES],
        "auc_media": [np.nan] * len(FALLBACK_MULTIPLICADORES),
        "auc_dp": [round(m * DP_REFERENCIA, 4) for m in FALLBACK_MULTIPLICADORES],
    })


def monta_grade_dispersao(empiricas: pd.DataFrame) -> tuple[list[float], pd.DataFrame]:
    """Uniao da faixa empirica com a familia de multiplicadores (correcao F4).

    Devolve (dps ordenados e deduplicados, tabela de procedencia). Nenhum numero e inventado
    aqui: a faixa empirica sai do CSV congelado pela regra de regime, e os multiplicadores
    estavam ja pre-declarados como fallback. DP_REFERENCIA entra sempre, porque e o cenario de
    referencia e o ancoramento de §10.2.
    """
    partes = [familia_multiplicadores()]
    if not empiricas.empty:
        partes.insert(0, empiricas[["rotulo", "auc_media", "auc_dp"]])
    proc = pd.concat(partes, ignore_index=True)
    proc["auc_dp"] = proc["auc_dp"].round(4)

    dps = sorted(set(proc["auc_dp"].tolist()) | {round(DP_REFERENCIA, 4)})
    return [float(d) for d in dps], proc.sort_values("auc_dp").reset_index(drop=True)


# ======================================================================================
# PORTAO DE DECISAO — nivel de modulo, para ser testavel (correcao F8)
# ======================================================================================

def poder_no_efeito(sub: pd.DataFrame, auc: float, criterio: str) -> float:
    """O poder numa celula de efeito exata. NaN se o efeito nao esta na grade."""
    linha = sub[np.isclose(sub["auc_media_verdadeira"], auc)]
    if linha.empty:
        return float("nan")
    return float(linha[criterio].iloc[0])


def avalia_portao(sub: pd.DataFrame, auc_ancora: float = AUC_ANCORA_PODER,
                  criterio: str = "poder_regra_suporte") -> dict:
    """O portao de §10.3, avaliado NA ANCORA declarada (correcao F1).

    O defeito que esta funcao substitui usava `.any()` sobre todos os efeitos >= AUC_SUPORTE,
    de modo que o maior efeito da grade decidia e o resultado era True por construcao. Aqui o
    poder e lido na celula da ancora, e mais nada.

    `monotonia_ok` verifica, em vez de assumir, que o poder nao cai quando o efeito cresce
    acima da ancora — que e a premissa que torna "avaliar na ancora" equivalente a "avaliar no
    pior caso de interesse". Se ela falhar, ha ruido de Monte Carlo demais ou bug, e o
    relatorio avisa.
    """
    poder = poder_no_efeito(sub, auc_ancora, criterio)
    acima = sub[sub["auc_media_verdadeira"] >= auc_ancora].sort_values("auc_media_verdadeira")
    vals = acima[criterio].tolist()
    finitos = [v for v in vals if np.isfinite(v)]
    return {
        "auc_ancora": auc_ancora,
        "criterio": criterio,
        "poder_na_ancora": poder,
        "passa": bool(np.isfinite(poder) and poder >= PODER_ALVO),
        "monotonia_ok": bool(
            len(finitos) < 2
            or all(b >= a - 0.05 for a, b in zip(finitos, finitos[1:]))),
    }


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
    ap.add_argument("--permitir-fallback", action="store_true",
                    help="autoriza rodar SEM a faixa empirica, apenas com a familia de "
                         "multiplicadores, se o CSV congelado nao estiver disponivel. Sem esta "
                         "flag o script para, em vez de degradar em silencio.")
    args = ap.parse_args()

    if args.n_sim < 2000:
        print(f"[AVISO] n_sim={args.n_sim} < 2000. O protocolo (§10.3) fixa 2000. "
              f"Esta rodada sera marcada como SMOKE TEST e nao pode fechar a etapa 0.6.",
              file=sys.stderr)

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    if AUC_ANCORA_PODER not in AUC_GRADE:
        print(f"[erro] AUC_ANCORA_PODER={AUC_ANCORA_PODER} nao esta em AUC_GRADE. O portao "
              f"nao pode ser avaliado num efeito que a grade nao simula.", file=sys.stderr)
        return 2

    empiricas, excluidas, origem = carrega_faixa_dispersao(CSV_DP)
    if origem == "indisponivel" and not args.permitir_fallback:
        print("[erro] a faixa empirica de dispersao nao pode ser derivada do CSV congelado "
              "(ver avisos acima). Rodar apenas com a familia de multiplicadores e um caminho "
              "DEGRADADO e precisa ser pedido explicitamente com --permitir-fallback, para "
              "que nao aconteca em silencio.", file=sys.stderr)
        return 2

    dps, procedencia = monta_grade_dispersao(empiricas)

    print(f"Origem da faixa empirica: {origem}")
    print(f"Cenarios de dispersao ({len(dps)}), uniao empirica + multiplicadores: {dps}")
    print(f"Referencia (LZc residualizada): {DP_REFERENCIA}")
    print(f"Ancora da decisao (§6.4 via §10.3): AUC = {AUC_ANCORA_PODER}")
    print(f"\nProcedencia de cada cenario de dispersao:")
    print(procedencia.to_string(index=False))
    if not excluidas.empty:
        print(f"\nExcluidas pela regra de regime AUC in [{AUC_MIN_REGIME}; {AUC_MAX_REGIME}] "
              f"— nao entram na faixa empirica, listadas para auditoria:")
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
                "eh_ancora": bool(abs(auc - AUC_ANCORA_PODER) < 1e-9),
                "auc_media_verdadeira": auc,
                "n_participantes": N_PARTICIPANTES,
                "n_sim": args.n_sim,
                **r,
            })
            if r["alvo_viavel"]:
                print(f"  dp={dp:.4f}  AUC={auc:.2f}  "
                      f"poder_wilcoxon={r['poder_wilcoxon']:.3f}  "
                      f"poder_regra={r['poder_regra_suporte']:.3f}  "
                      f"(realizado: media={r['media_realizada']:.4f}, "
                      f"dp={r['dp_realizado']:.4f})", flush=True)
            else:
                print(f"  dp={dp:.4f}  AUC={auc:.2f}  INVIAVEL em [0,1] — celula sem poder",
                      flush=True)

    df = pd.DataFrame(linhas)
    df.to_csv(out / "poder_vnext01.csv", index=False)

    # ---- fidelidade do gerador: verificada, nao afirmada (correcao F3) ----
    viaveis = df[df["alvo_viavel"]].copy()
    n_amostras = args.n_sim * N_PARTICIPANTES
    # erro-padrao da media amostral e (aproximadamente) do desvio-padrao amostral
    se_media = viaveis["dp_auc_por_participante"] / np.sqrt(n_amostras)
    se_dp = viaveis["dp_auc_por_participante"] / np.sqrt(2 * n_amostras)
    tol_media = np.maximum(SIGMAS_FIDELIDADE * se_media, PISO_FIDELIDADE)
    tol_dp = np.maximum(SIGMAS_FIDELIDADE * se_dp, PISO_FIDELIDADE)
    desvio_media = (viaveis["media_realizada"] - viaveis["auc_media_verdadeira"]).abs()
    desvio_dp = (viaveis["dp_realizado"] - viaveis["dp_auc_por_participante"]).abs()
    fora = (desvio_media > tol_media) | (desvio_dp > tol_dp)

    erro_media = float(desvio_media.max())
    erro_dp = float(desvio_dp.max())
    z_media = float((desvio_media / se_media).max())
    z_dp = float((desvio_dp / se_dp).max())
    fidelidade_ok = bool(not fora.any())
    n_inviaveis = int((~df["alvo_viavel"]).sum())
    n_nao_unimodais = int((viaveis["forma_unimodal"] == False).sum())  # noqa: E712

    print(f"\nFidelidade do gerador: desvio maximo na media {erro_media:.4f} ({z_media:.1f} "
          f"erros-padrao), no dp {erro_dp:.4f} ({z_dp:.1f} erros-padrao); limite "
          f"{SIGMAS_FIDELIDADE:g} erros-padrao")
    if not fidelidade_ok:
        print(f"[AVISO] o gerador nao esta entregando os momentos declarados em "
              f"{int(fora.sum())} celulas, alem do que o erro de amostragem explica. A grade "
              f"estaria rotulada com parametros que nao simula, e nenhuma linha deve ser usada.",
              file=sys.stderr)
    if n_inviaveis:
        print(f"[nota] {n_inviaveis} celulas inviaveis em [0,1] (dp^2 >= media*(1-media)); "
              f"saem sem poder, nao com poder aproximado.")
    if n_nao_unimodais:
        print(f"[nota] {n_nao_unimodais} celulas viaveis tem Beta em forma de U ou J "
              f"(a<=1 ou b<=1): momentos certos, forma extrema. Ver `forma_unimodal` no CSV.")

    # ---- decisao: ancorada no menor efeito de interesse (correcao F1) ----
    ref = df[df["eh_referencia"]]
    portao_ref = avalia_portao(ref)
    reference_power_pass = portao_ref["passa"]

    portoes_por_dp = {dp: avalia_portao(df[df["dp_auc_por_participante"] == dp]) for dp in dps}
    robust_power_pass = all(p["passa"] for p in portoes_por_dp.values())
    monotonia_ok = all(p["monotonia_ok"] for p in portoes_por_dp.values())
    if not monotonia_ok:
        print("[AVISO] o poder nao cresce monotonicamente com o efeito em alguma dispersao. "
              "Isso invalida a leitura de 'avaliar na ancora e o pior caso de interesse': "
              "ha ruido de Monte Carlo demais, ou bug.", file=sys.stderr)

    # poder na ancora e no limiar de suporte, sob os dois criterios, por dispersao
    def por_dp(auc: float, criterio: str) -> dict:
        return {dp: poder_no_efeito(df[df["dp_auc_por_participante"] == dp], auc, criterio)
                for dp in dps}

    poder_na_ancora = {
        "regra_suporte": por_dp(AUC_ANCORA_PODER, "poder_regra_suporte"),
        "wilcoxon": por_dp(AUC_ANCORA_PODER, "poder_wilcoxon"),
    }
    poder_no_suporte = {
        "regra_suporte": por_dp(AUC_SUPORTE, "poder_regra_suporte"),
        "wilcoxon": por_dp(AUC_SUPORTE, "poder_wilcoxon"),
    }

    # menor AUC detectavel com PODER_ALVO, por dispersao
    mde = {}
    for dp in dps:
        sub = df[(df["dp_auc_por_participante"] == dp) &
                 (df["poder_regra_suporte"] >= PODER_ALVO)]
        mde[dp] = float(sub["auc_media_verdadeira"].min()) if not sub.empty else None

    # ---- ruido de Monte Carlo: mesmas celulas, sementes independentes ----
    mc = {}
    if not args.pular_verificacao_sementes:
        alvo_auc = AUC_ANCORA_PODER   # a celula que decide, nao AUC_SUPORTE (correcao F1)
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
        print(f"\nRuido de Monte Carlo na celula da ancora: {vals} "
              f"(amplitude {hi - lo:.3f})")
        if mc["cruza_alvo"]:
            print(f"[AVISO] a faixa entre sementes cruza {PODER_ALVO}. "
                  f"n_sim precisa subir antes de a conclusao ser usada.", file=sys.stderr)

    meta = {
        "estatuto": "SMOKE TEST" if args.n_sim < 2000 else "rodada valida para a etapa 0.6",
        "origem_faixa_dispersao": origem,
        "faixa_dispersao": "uniao da faixa empirica com a familia de multiplicadores (F4)",
        "cenarios_dp": dps,
        "procedencia_cenarios_dp": procedencia.to_dict(orient="records"),
        "dp_referencia": DP_REFERENCIA,
        "excluidas_pela_regra_de_regime": excluidas.to_dict(orient="records"),
        "regra_de_regime": {"auc_min": AUC_MIN_REGIME, "auc_max": AUC_MAX_REGIME},
        "teste": "Wilcoxon bilateral contra 0,5, zero_method=wilcox, alfa=0,05",
        "gerador": "Beta parametrizada em (media, dp); suporte (0,1) por construcao (F3)",
        "regra_suporte": {"auc_min": AUC_SUPORTE, "alfa": ALFA,
                          "min_sujeitos_acima_05": MIN_SUJEITOS_ACIMA,
                          "n_participantes": N_PARTICIPANTES},
        "poder_alvo": PODER_ALVO,
        "n_sim": args.n_sim,
        "seed": args.seed,
        # ---- o portao, e o efeito em que ele foi avaliado ----
        "ancora_da_decisao": {
            "auc": AUC_ANCORA_PODER,
            "origem": "menor efeito de interesse de §6.4, que §10.3 nomeia no portao",
            "criterio": "poder_regra_suporte (a regra conjuntiva de §6.1)",
        },
        "reference_power_pass": reference_power_pass,
        "robust_power_pass": robust_power_pass,
        "portao_na_referencia": portao_ref,
        "portao_por_dispersao": {str(k): v for k, v in portoes_por_dp.items()},
        "monotonia_do_poder_ok": monotonia_ok,
        # ---- o que uma decisao booleana esconde ----
        "poder_na_ancora": {k: {str(dp): v for dp, v in d.items()}
                            for k, d in poder_na_ancora.items()},
        "poder_no_limiar_de_suporte": {k: {str(dp): v for dp, v in d.items()}
                                       for k, d in poder_no_suporte.items()},
        "mde_por_dispersao": {str(k): v for k, v in mde.items()},
        # ---- fidelidade do gerador, verificada nesta rodada ----
        "fidelidade_gerador": {
            "desvio_max_media": erro_media,
            "desvio_max_dp": erro_dp,
            "desvio_max_media_em_erros_padrao": z_media,
            "desvio_max_dp_em_erros_padrao": z_dp,
            "limite_em_erros_padrao": SIGMAS_FIDELIDADE,
            "piso_absoluto": PISO_FIDELIDADE,
            "celulas_fora_do_limite": int(fora.sum()),
            "ok": fidelidade_ok,
            "celulas_inviaveis": n_inviaveis,
            "celulas_beta_nao_unimodal": n_nao_unimodais,
        },
        "mc_ruido": mc,
        "correcoes_aplicadas": ["F1 ancora da decisao", "F3 gerador Beta e momentos"
                                " realizados", "F4 uniao das faixas de dispersao"],
        "f2_em_aberto": ("§6.4 (interesse 0,55), §10.2 (0,60 ~ MDE) e §10.3 (80% no menor "
                         "efeito de interesse) nao podem valer juntos em n=36. Decisao de "
                         "desenho do autor, a registrar na §16."),
        "versoes": {"python": platform.python_version(),
                    "numpy": np.__version__, "pandas": pd.__version__,
                    "scipy": __import__("scipy").__version__},
    }
    (out / "poder_vnext01_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    p_anc = portao_ref["poder_na_ancora"]
    p_sup = poder_no_suporte["regra_suporte"].get(round(DP_REFERENCIA, 4), float("nan"))
    print("\n" + "=" * 78)
    print(f"Portao de §10.3, avaliado em AUC = {AUC_ANCORA_PODER} (menor efeito de interesse):")
    print(f"  poder na ancora, cenario de referencia (dp={DP_REFERENCIA}): {p_anc:.3f}")
    print(f"  poder no limiar de suporte AUC={AUC_SUPORTE}, mesmo cenario:  {p_sup:.3f}")
    print(f"  MDE no cenario de referencia: {mde.get(round(DP_REFERENCIA, 4))}")
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
    elif not reference_power_pass:
        print(
            "\nLeitura pre-declarada deste caso: o portao de §10.3 NAO e satisfeito neste n,\n"
            "nem no cenario de dispersao mais favoravel entre os congelados. Isso nao e falha\n"
            "da simulacao nem resultado sobre a teoria — e a constatacao de que o desenho, como\n"
            "esta, nao tem poder para o menor efeito que o proprio protocolo declara de\n"
            "interesse. A decisao que se segue e de DESENHO (F2: reformular o portao, rebaixar o\n"
            "braco a estimativa com IC pre-declarado, ou aceitar e registrar a subpotencia), e\n"
            "precisa ser tomada e registrada na §16 ANTES da Fase 1. O que nao pode acontecer e\n"
            "esta saida ser lida como 'a irreversibilidade nao funciona': ela nao e sobre a\n"
            "metrica, e sobre o n.\n"
            "Consulte `mde_por_dispersao`: e o objeto que sobrevive a qualquer resolucao de F2."
        )
    print(f"\nSaidas: {out / 'poder_vnext01.csv'}\n         {out / 'poder_vnext01_meta.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
