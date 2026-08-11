"""Roda sensibilidade_v3.py e calibracao_v3.py com parametros maiores que
os defaults, para reforcar a precisao do resultado ja obtido com os
defaults (Bloco Q do CHECKLIST_pendencias.md).

Nao sobrescreve a rodada anterior: salva tudo em
'saida_parametros_maiores/' (pasta nova, dentro desta mesma pasta).

Escolha dos parametros (ver justificativa completa na conversa com o
agente): um aumento de ~4-9x no volume total de simulacao em relacao
aos defaults, escolhido para dar mais poder estatistico sem tornar o
tempo de execucao impraticavel para uma rodada unica.

Uso (de dentro desta pasta, com o venv do projeto ativo):
    python rodar_parametros_maiores.py

Tempo esperado: sensibilidade_v3.py deve terminar em poucos minutos;
calibracao_v3.py e a parte mais pesada e pode levar entre ~20 e ~60
minutos, dependendo da maquina. Os dois rodam em sequencia, nao em
paralelo, para nao competir por CPU e nao confundir qual saida e de
qual script se algo der errado no meio.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
OUTDIR = HERE / "saida_parametros_maiores"
OUTDIR.mkdir(exist_ok=True)

COMANDOS = [
    (
        "sensibilidade_v3.py (robustez) - parametros maiores",
        [
            sys.executable, str(HERE / "sensibilidade_v3.py"),
            "--n-runs", "15",
            "--n-trials", "20",
            "--T", "30",
            "--outdir", str(OUTDIR),
        ],
    ),
    (
        "calibracao_v3.py (identificabilidade) - parametros maiores",
        [
            sys.executable, str(HERE / "calibracao_v3.py"),
            "--n-samples", "500",
            "--n-starts", "8",
            "--n-runs", "6",
            "--T", "20",
            "--outdir", str(OUTDIR),
        ],
    ),
]


def main() -> None:
    for label, cmd in COMANDOS:
        print(f"\n=== Rodando: {label} ===")
        print(" ".join(cmd))
        resultado = subprocess.run(cmd, cwd=HERE)
        if resultado.returncode != 0:
            print(f"\nERRO: '{label}' terminou com codigo {resultado.returncode}. Parando aqui.")
            sys.exit(resultado.returncode)

    print(f"\nConcluido. Saidas em: {OUTDIR}")


if __name__ == "__main__":
    main()
