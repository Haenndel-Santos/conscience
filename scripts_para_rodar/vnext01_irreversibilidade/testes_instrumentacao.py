#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
testes_instrumentacao.py — Testes de CORRETUDE DE CODIGO da instrumentacao da Fase 0.

O que estes testes fazem: verificam invariantes de implementacao — que a reproducao do
teste primario bate com o original do projeto, que a regra mecanica de selecao de dispersao
seleciona o que deveria, que o poder se comporta monotonicamente, que a regra de suporte e
de fato conjuntiva, e que o gerador respeita o suporte [0,1] da AUC.

O que estes testes NAO fazem: nao produzem nenhum numero cientifico, nao tocam dado de EEG,
e nao substituem a execucao das etapas 0.4 e 0.6, que continuam sendo do autor.

Uso:
    python testes_instrumentacao.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
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
    """AUC vive em [0,1]; o gerador nao pode devolver valor fora."""
    print("\nteste_gerador_respeita_suporte")
    rng = np.random.default_rng(11)
    for media, dp in [(0.5, 0.35), (0.95, 0.30), (0.05, 0.30)]:
        x = pv.simula_aucs(rng, media, dp, 500)
        checa(bool((x > 0).all() and (x < 1).all()),
              f"suporte respeitado (media={media}, dp={dp})")


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

    if origem == "fallback":
        checa(len(inc) == len(pv.FALLBACK_MULTIPLICADORES),
              "fallback com o numero certo de cenarios")
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
                 "AUC_GRADE", "aplica_regra_suporte", "p_wilcoxon_contra_meio"}
    achados = sorted(nomes_referenciados(pv.carrega_faixa_dispersao) & proibidos)
    checa(not achados, "selecao de dispersao nao referencia nada de poder", f"achou {achados}")

    # e a reciproca: a grade de efeitos nao pode depender da dispersao observada
    checa(isinstance(pv.AUC_GRADE, tuple) and all(isinstance(x, float) for x in pv.AUC_GRADE),
          "grade de efeitos e constante literal, nao derivada dos dados")


def main() -> int:
    print("Testes de corretude da instrumentacao da Fase 0")
    print("(nao produzem numero cientifico; nao tocam dado de EEG)")
    teste_wilcoxon_identico_ao_original()
    teste_regra_suporte_e_conjuntiva()
    teste_gerador_respeita_suporte()
    teste_poder_monotono_no_efeito()
    teste_poder_decresce_com_dispersao()
    teste_regra_de_regime_seleciona_o_esperado()
    teste_nao_busca_dp_que_faz_passar()

    print("\n" + "=" * 70)
    if FALHAS:
        print(f"FALHAS ({len(FALHAS)}): {FALHAS}")
        return 1
    print("Todos os testes de corretude passaram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
