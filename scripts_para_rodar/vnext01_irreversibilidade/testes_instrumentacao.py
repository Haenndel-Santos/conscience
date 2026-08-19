#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
testes_instrumentacao.py — Testes de CORRETUDE DE CODIGO da instrumentacao da Fase 0.

O que estes testes fazem: verificam invariantes de implementacao — que a reproducao do
teste primario bate com o original do projeto, que a regra mecanica de selecao de dispersao
seleciona o que deveria, que o poder se comporta monotonicamente, que a regra de suporte e
de fato conjuntiva, e que o gerador respeita o suporte [0,1] da AUC.

ACRESCENTADOS EM 2026-08-17 (correcao F8, e a razao dela): a revisao pre-merge encontrou dois
defeitos — um portao de decisao vacuo (F1) e um gerador que nao entregava os momentos
declarados (F3) — e nenhum dos dois foi pego por este arquivo. Nao por acaso: o portao era
funcao aninhada em `main()`, inalcancavel por teste, e a fidelidade do gerador nunca era
comparada com o alvo, so o suporte. As duas lacunas eram exatamente onde os defeitos estavam.
Os testes `teste_portao_ancora_no_efeito_declarado`, `teste_gerador_entrega_os_momentos_
declarados` e `teste_grade_de_dispersao_e_uniao` fecham as tres, e cada um fixa a propriedade
que o defeito violava — nao apenas o comportamento novo.

O que estes testes NAO fazem: nao produzem nenhum numero cientifico, nao tocam dado de EEG,
e nao substituem a execucao das etapas 0.4 e 0.6, que continuam sendo do autor.

Uso:
    python testes_instrumentacao.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))

import poder_vnext01 as pv  # noqa: E402

FALHAS: list[str] = []


def checa(cond: bool, nome: str, detalhe: str = "") -> None:
    if cond:
        print(f"  ok   {nome}")
    else:
        print(f"  FALHA {nome} {detalhe}")
        FALHAS.append(nome)


def teste_wilcoxon_identico_ao_original() -> None:
    """A reproducao do teste primario tem de bater com teste_uma_amostra, bit a bit.

    O original: stats.wilcoxon(aucs - 0.5, alternative="two-sided", zero_method="wilcox").
    Se alguem trocar por t-test ou por unilateral, este teste quebra — que e o ponto.
    """
    print("\nteste_wilcoxon_identico_ao_original")
    rng = np.random.default_rng(7)
    for _ in range(20):
        aucs = np.clip(rng.normal(0.55, 0.2, size=36), 1e-9, 1 - 1e-9)
        esperado = float(stats.wilcoxon(aucs - 0.5, alternative="two-sided",
                                        zero_method="wilcox").pvalue)
        obtido = pv.p_wilcoxon_contra_meio(aucs)
        if abs(esperado - obtido) > 1e-12:
            checa(False, "p identico ao original", f"({esperado} vs {obtido})")
            return
    checa(True, "p identico ao original em 20 amostras")

    # bilateral, nao unilateral: um efeito negativo forte tem de dar p pequeno tambem
    aucs_neg = np.full(36, 0.30)
    checa(pv.p_wilcoxon_contra_meio(aucs_neg) < 0.01,
          "bilateral: efeito negativo tambem rejeita")

    # degenerado
    checa(pv.p_wilcoxon_contra_meio(np.full(36, 0.5)) == 1.0,
          "todas as AUCs em 0,5 -> p = 1,0")


def teste_regra_suporte_e_conjuntiva() -> None:
    """SUPORTE exige as TRES condicoes. Cada uma sozinha nao basta."""
    print("\nteste_regra_suporte_e_conjuntiva")

    # AUC alta, p baixo, muitos acima de 0,5 -> passa
    aucs = np.full(36, 0.72)
    checa(pv.aplica_regra_suporte(aucs, 0.001) is True, "as tres condicoes -> True")

    # AUC abaixo do limiar, mas p significativo e todos acima de 0,5 -> NAO passa
    aucs = np.full(36, 0.58)
    checa(pv.aplica_regra_suporte(aucs, 0.001) is False,
          "AUC 0,58 com p=0,001 -> False (o caso que a revisao apontou)")

    # AUC alta e p alto -> nao passa
    aucs = np.full(36, 0.72)
    checa(pv.aplica_regra_suporte(aucs, 0.20) is False, "p nao significativo -> False")

    # AUC media alta puxada por poucos: 20 acima, 16 bem abaixo
    aucs = np.concatenate([np.full(20, 0.95), np.full(16, 0.15)])
    checa(pv.aplica_regra_suporte(aucs, 0.001) is False,
          "efeito carregado por poucos participantes -> False")


def teste_gerador_respeita_suporte() -> None:
    """AUC vive em [0,1]; o gerador nao pode devolver valor fora, nem NaN.

    O suporte e FECHADO de proposito. AUC = 1,0 e AUC = 0,0 sao valores legitimos de uma AUC —
    separacao perfeita em um dos dois sentidos — e a versao anterior os proibia por efeito
    colateral do `np.clip(x, 1e-9, 1-1e-9)` final, que existia para consertar a truncagem e
    nao por uma razao sobre a AUC. Com a Beta os valores de borda aparecem apenas quando um dos
    parametros e minusculo (media muito excentrica com dp grande), caso em que o ponto flutuante
    satura; sao poucos, sao validos, e nada a jusante quebra com eles.
    """
    print("\nteste_gerador_respeita_suporte")
    rng = np.random.default_rng(11)
    for media, dp in [(0.5, 0.20), (0.95, 0.15), (0.05, 0.15)]:
        x = pv.simula_aucs(rng, media, dp, 500)
        checa(bool(np.isfinite(x).all() and (x >= 0).all() and (x <= 1).all()),
              f"suporte respeitado (media={media}, dp={dp})")

    # e o suporte fechado nao envenena o teste primario
    x = np.concatenate([np.full(18, 1.0), np.full(18, 0.0)])
    checa(np.isfinite(pv.p_wilcoxon_contra_meio(x)),
          "AUCs exatamente em 0 e 1 nao quebram o Wilcoxon")


def teste_gerador_entrega_os_momentos_declarados() -> None:
    """O teste que faltava, e que deixou passar F3.

    O antecessor deste arquivo checava apenas que o gerador nao saia do suporte — o que era
    verdade por construcao, porque a versao anterior clipava no fim. Nada comparava media e dp
    REALIZADOS contra os alvos, e por isso ninguem viu que a celula rotulada AUC=0,60 simulava
    media 0,582 e dp 11% abaixo do pedido.
    """
    print("\nteste_gerador_entrega_os_momentos_declarados")
    rng = np.random.default_rng(2026)
    casos = [(0.50, 0.1173), (0.55, 0.2346), (0.60, 0.2346), (0.65, 0.2845),
             (0.75, 0.2346), (0.75, 0.3519), (0.50, 0.3519)]
    piores = (0.0, 0.0)
    for media, dp in casos:
        x = pv.simula_aucs(rng, media, dp, 200_000)
        e_m, e_d = abs(x.mean() - media), abs(x.std() - dp)
        piores = (max(piores[0], e_m), max(piores[1], e_d))
        if e_m > 0.005 or e_d > 0.005:
            checa(False, f"momentos realizados == alvos (media={media}, dp={dp})",
                  f"(erros {e_m:.4f}, {e_d:.4f})")
            return
    checa(True, f"momentos realizados == alvos em {len(casos)} celulas",
          f"(pior erro: media {piores[0]:.4f}, dp {piores[1]:.4f})")

    # a viabilidade e um limite universal do suporte, nao uma limitacao da Beta escolhida
    _, _, viavel = pv.parametros_beta(0.75, 0.44)
    checa(not viavel, "par com dp^2 >= media*(1-media) e marcado inviavel")
    _, _, viavel = pv.parametros_beta(0.75, 0.2845)
    checa(viavel, "par viavel e aceito")

    # e uma celula inviavel nao produz poder aproximado: produz NaN e a marca
    r = pv.poder_para(np.random.default_rng(1), 0.75, 0.44, 10)
    checa(r["alvo_viavel"] is False and np.isnan(r["poder_regra_suporte"]),
          "celula inviavel sai sem poder, nao com poder aproximado")


def teste_portao_ancora_no_efeito_declarado() -> None:
    """O teste que faltava para F1: a decisao nao pode ser vacua.

    `passa()` era funcao aninhada em `main()` e portanto inalcancavel por teste — a unica parte
    do script sem cobertura era a que carregava a decisao. Agora e `avalia_portao`, no nivel do
    modulo, e este teste fixa a propriedade que o defeito violava: um poder alto num efeito
    GRANDE nao pode fazer o portao passar quando o poder na ANCORA e baixo.
    """
    print("\nteste_portao_ancora_no_efeito_declarado")

    grade = pd.DataFrame({
        "auc_media_verdadeira": [0.55, 0.60, 0.70, 0.75],
        "poder_regra_suporte": [0.04, 0.23, 0.93, 0.99],
        "poder_wilcoxon": [0.20, 0.63, 0.99, 1.00],
    })
    r = pv.avalia_portao(grade, auc_ancora=0.55)
    checa(r["passa"] is False,
          "poder alto em AUC=0,75 NAO faz o portao passar (o defeito F1)",
          f"(poder na ancora {r['poder_na_ancora']})")
    checa(abs(r["poder_na_ancora"] - 0.20) < 1e-12, "le o poder na celula da ancora")
    checa(r["monotonia_ok"] is True, "monotonia reconhecida quando o poder cresce")

    # F2: o portao le o TESTE PRIMARIO, nao a regra de classificacao. As duas colunas desta
    # grade sao deliberadamente diferentes, para que trocar o criterio quebre este teste.
    checa(r["criterio"] == pv.CRITERIO_PORTAO_A == "poder_wilcoxon",
          "o portao A e o poder do Wilcoxon, nao a regra conjuntiva (F2)",
          f"(criterio={r['criterio']})")
    checa(abs(pv.avalia_portao(grade, auc_ancora=0.55,
                               criterio="poder_regra_suporte")["poder_na_ancora"] - 0.04) < 1e-12,
          "a caracteristica operacional da regra segue calculavel, em campo proprio")

    forte = grade.copy()
    forte["poder_wilcoxon"] = [0.85, 0.90, 0.95, 0.99]
    checa(pv.avalia_portao(forte, auc_ancora=0.55)["passa"] is True,
          "portao passa quando o poder na ancora atinge o alvo")

    # ancora fora da grade nao pode passar por omissao
    r = pv.avalia_portao(grade, auc_ancora=0.52)
    checa(r["passa"] is False and np.isnan(r["poder_na_ancora"]),
          "ancora ausente da grade -> NaN e nao passa")

    # e a monotonia e verificada, nao assumida
    quebrada = grade.copy()
    quebrada["poder_wilcoxon"] = [0.85, 0.90, 0.40, 0.99]
    checa(pv.avalia_portao(quebrada, auc_ancora=0.55)["monotonia_ok"] is False,
          "queda grande de poder com efeito crescente e detectada")

    checa(pv.AUC_ANCORA_PODER in pv.AUC_GRADE,
          "a ancora declarada esta na grade que o script simula")


def teste_portao_b_equivalencia() -> None:
    """F8: o portao de nulo informativo mede o que §6.1 declara, e nao passa em n=36.

    Tres propriedades sao fixadas aqui. A primeira e de CORRETUDE: TOST a alfa e o IC de
    (1 - 2*alfa), e nao o de (1 - alfa) — trocar um pelo outro e o erro classico de
    equivalencia, e mudaria o n necessario de ~190 para ~232. A segunda e a inacessibilidade
    em si, que e a razao de F8 existir. A terceira e que o portao ATINGE o alvo com n
    suficiente, para que "nao passa" seja um fato sobre o n e nao um bug que reprova sempre.
    """
    print("\nteste_portao_b_equivalencia")

    checa(pv.EQ_MARGEM_INF == 0.45 and pv.EQ_MARGEM_SUP == 0.55,
          "as margens sao as de §6.1 e §6.4, inalteradas")

    # TOST a 0,05 <=> IC 90%. Uma amostra cuja semi-amplitude de IC 90% cabe nas margens mas a
    # de IC 95% nao cabe tem de ser aceita — e o que distingue as duas formulacoes.
    n = 36
    meia_90 = float(stats.t.ppf(0.95, n - 1)) / np.sqrt(n)
    alvo_dp = 0.049 / meia_90          # semi-amplitude de IC 90% = 0,049 < 0,05
    x = np.full(n, 0.50)
    x[: n // 2] += alvo_dp
    x[n // 2:] -= alvo_dp
    x = 0.50 + (x - x.mean())
    aceita_90 = pv.testa_equivalencia(x)
    meia_real_95 = float(stats.t.ppf(0.975, n - 1)) * float(x.std(ddof=1)) / np.sqrt(n)
    checa(aceita_90 and meia_real_95 > 0.05,
          "TOST a 0,05 usa o IC 90%, nao o 95% (o erro classico de equivalencia)",
          f"(semi-IC95={meia_real_95:.4f})")

    # uma amostra visivelmente dispersa nao pode ser declarada equivalente
    rng = np.random.default_rng(11)
    checa(pv.testa_equivalencia(np.clip(rng.normal(0.5, 0.30, n), 1e-9, 1 - 1e-9)) is False,
          "dispersao larga NAO e declarada equivalente")

    # F8: inacessivel em n=36 na dispersao de referencia, mesmo sob o nulo exato
    p36 = pv.poder_equivalencia(np.random.default_rng(5), pv.DP_REFERENCIA, 400)
    checa(p36 < 0.05,
          "P(EQUIVALENCIA | nulo exato) e ~0 em n=36 na dispersao de referencia (F8)",
          f"(p={p36:.4f})")

    # e o portao nao e um teste que reprova sempre: com n suficiente ele atinge o alvo
    p_grande = pv.poder_equivalencia(np.random.default_rng(5), pv.DP_REFERENCIA, 400, n=260)
    checa(p_grande >= pv.PODER_ALVO,
          "com n suficiente o portao B atinge o alvo — nao reprova por construcao",
          f"(n=260 -> p={p_grande:.3f})")


def teste_grade_de_dispersao_e_uniao() -> None:
    """F4: a grade varrida contem as duas familias, e nenhuma sobrepoe a outra."""
    print("\nteste_grade_de_dispersao_e_uniao")
    empiricas, _, origem = pv.carrega_faixa_dispersao(pv.CSV_DP)
    dps, proc = pv.monta_grade_dispersao(empiricas)

    mult = [round(m * pv.DP_REFERENCIA, 4) for m in pv.FALLBACK_MULTIPLICADORES]
    checa(all(m in dps for m in mult), "a familia de multiplicadores esta na grade")
    checa(round(pv.DP_REFERENCIA, 4) in dps, "o cenario de referencia esta na grade")
    checa(dps == sorted(set(dps)), "grade ordenada e sem duplicatas")

    if origem == "empirica":
        emp = [round(float(x), 4) for x in empiricas["auc_dp"]]
        checa(all(e in dps for e in emp), "todas as dispersoes empiricas estao na grade")
        checa(min(dps) < min(emp) and max(dps) > max(emp),
              "a uniao e estritamente mais larga que a faixa empirica sozinha",
              f"(empirica [{min(emp)}; {max(emp)}] -> uniao [{min(dps)}; {max(dps)}])")
        checa(len(proc) == len(empiricas) + len(pv.FALLBACK_MULTIPLICADORES),
              "a procedencia de cada cenario e rastreavel")
    else:
        print("  (CSV congelado indisponivel; uniao com a faixa empirica nao testada aqui)")


def teste_poder_monotono_no_efeito() -> None:
    """Poder tem de crescer com o efeito, fixada a dispersao. Se nao crescer, ha bug."""
    print("\nteste_poder_monotono_no_efeito")
    rng = np.random.default_rng(3)
    p_baixo = pv.poder_para(rng, 0.50, 0.23, 300)["poder_wilcoxon"]
    p_alto = pv.poder_para(rng, 0.75, 0.23, 300)["poder_wilcoxon"]
    checa(p_alto > p_baixo, "poder cresce com o efeito", f"({p_baixo:.3f} -> {p_alto:.3f})")

    # sob o nulo exato, o poder e o erro tipo I: tem de ficar perto de alfa
    checa(abs(p_baixo - pv.ALFA) < 0.05,
          "sob AUC=0,5 o poder aproxima alfa", f"({p_baixo:.3f} vs {pv.ALFA})")


def teste_poder_decresce_com_dispersao() -> None:
    """Fixado o efeito, mais dispersao -> menos poder. E a premissa da varredura inteira."""
    print("\nteste_poder_decresce_com_dispersao")
    rng = np.random.default_rng(5)
    p_apertado = pv.poder_para(rng, 0.62, 0.15, 300)["poder_wilcoxon"]
    p_largo = pv.poder_para(rng, 0.62, 0.35, 300)["poder_wilcoxon"]
    checa(p_apertado > p_largo, "poder cai com a dispersao",
          f"({p_apertado:.3f} -> {p_largo:.3f})")


def teste_regra_de_regime_seleciona_o_esperado() -> None:
    """A regra mecanica tem de excluir as metricas comprimidas contra a fronteira."""
    print("\nteste_regra_de_regime_seleciona_o_esperado")
    inc, exc, origem = pv.carrega_faixa_dispersao(pv.CSV_DP)

    if origem == "indisponivel":
        checa(inc.empty, "faixa empirica vazia quando o CSV nao esta disponivel")
        checa(len(pv.familia_multiplicadores()) == len(pv.FALLBACK_MULTIPLICADORES),
              "familia de multiplicadores com o numero certo de cenarios")
        print("  (CSV congelado indisponivel; regra empirica nao testada nesta maquina)")
        return

    checa(len(inc) >= pv.MIN_CENARIOS_EMPIRICOS, "faixa empirica com cenarios suficientes")
    checa(bool(inc["auc_media"].between(pv.AUC_MIN_REGIME, pv.AUC_MAX_REGIME).all()),
          "todas as incluidas estao no regime declarado")
    if not exc.empty:
        checa(bool((~exc["auc_media"].between(pv.AUC_MIN_REGIME, pv.AUC_MAX_REGIME)).all()),
              "todas as excluidas estao fora do regime")
        checa(bool(exc["auc_dp"].min() < inc["auc_dp"].min()),
              "as excluidas tem dp menor — o artefato de fronteira que a regra existe para barrar")

    # o dp de referencia tem de estar dentro ou muito perto da faixa empirica
    checa(bool(inc["auc_dp"].min() <= pv.DP_REFERENCIA <= inc["auc_dp"].max()),
          "dp de referencia dentro da faixa empirica")


def teste_nao_busca_dp_que_faz_passar() -> None:
    """Guarda contra a tentacao explicitamente proibida no protocolo.

    A faixa de dispersao tem de ser determinada ANTES e independentemente do poder.

    A checagem e feita sobre os NOMES QUE O BYTECODE REFERENCIA (`co_names`), nao sobre o
    texto-fonte: procurar a string "poder" no fonte da falso-positivo, porque o proprio
    docstring da funcao explica que ela nao consulta poder. Guarda que quebra por causa de
    prosa e guarda que sera desligada na primeira vez que incomodar.
    """
    print("\nteste_nao_busca_dp_que_faz_passar")

    def nomes_referenciados(fn) -> set[str]:
        code = fn.__code__
        nomes = set(code.co_names) | set(code.co_varnames)
        for const in code.co_consts:
            if hasattr(const, "co_names"):  # funcoes aninhadas
                nomes |= set(const.co_names) | set(const.co_varnames)
        return nomes

    proibidos = {"PODER_ALVO", "poder_para", "poder_wilcoxon", "poder_regra_suporte",
                 "AUC_GRADE", "aplica_regra_suporte", "p_wilcoxon_contra_meio",
                 "avalia_portao", "poder_no_efeito", "AUC_ANCORA_PODER"}
    achados = sorted(nomes_referenciados(pv.carrega_faixa_dispersao) & proibidos)
    checa(not achados, "selecao de dispersao nao referencia nada de poder", f"achou {achados}")

    # a uniao das faixas (F4) tambem nao pode consultar poder — e o mesmo risco, um passo depois
    achados = sorted(nomes_referenciados(pv.monta_grade_dispersao) & proibidos)
    checa(not achados, "uniao das faixas de dispersao nao referencia nada de poder",
          f"achou {achados}")

    # e a reciproca: a grade de efeitos nao pode depender da dispersao observada
    checa(isinstance(pv.AUC_GRADE, tuple) and all(isinstance(x, float) for x in pv.AUC_GRADE),
          "grade de efeitos e constante literal, nao derivada dos dados")


def main() -> int:
    print("Testes de corretude da instrumentacao da Fase 0")
    print("(nao produzem numero cientifico; nao tocam dado de EEG)")
    teste_wilcoxon_identico_ao_original()
    teste_regra_suporte_e_conjuntiva()
    teste_gerador_respeita_suporte()
    teste_gerador_entrega_os_momentos_declarados()
    teste_poder_monotono_no_efeito()
    teste_poder_decresce_com_dispersao()
    teste_regra_de_regime_seleciona_o_esperado()
    teste_grade_de_dispersao_e_uniao()
    teste_portao_ancora_no_efeito_declarado()
    teste_portao_b_equivalencia()
    teste_nao_busca_dp_que_faz_passar()

    print("\n" + "=" * 70)
    if FALHAS:
        print(f"FALHAS ({len(FALHAS)}): {FALHAS}")
        return 1
    print("Todos os testes de corretude passaram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
