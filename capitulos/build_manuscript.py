"""Reconstroi "Versao atual.md" (raiz do projeto) a partir dos arquivos
desta pasta, na ordem correta, separando cada um por "---".

Os arquivos em capitulos/ sao a fonte de verdade a partir de 2026-08-05.
Nao edite "Versao atual.md" diretamente - rode este script depois de
editar os arquivos de capitulo.

Uso: python capitulos/build_manuscript.py
"""
from pathlib import Path

HERE = Path(__file__).parent
OUTPUT = HERE.parent / "Versao atual.md"

ORDER = [
    "00_nota_metodologica.md",
    "01_introducao.md",
    "02_capitulo_01.md",
    "03_capitulo_02.md",
    "04_capitulo_03.md",
    "05_capitulo_04.md",
    "06_capitulo_05.md",
    "07_capitulo_06.md",
    "08_capitulo_07.md",
    "09_capitulo_08.md",
    "10_capitulo_09.md",
    "11_capitulo_10.md",
    "12_capitulo_11.md",
    "13_capitulo_12.md",
    "14_capitulo_13.md",
    "15_capitulo_14.md",
    "16_conclusao.md",
    "17_referencias.md",
]


def main():
    missing = [f for f in ORDER if not (HERE / f).exists()]
    if missing:
        raise FileNotFoundError(f"Arquivos de capitulo ausentes: {missing}")

    parts = []
    for fname in ORDER:
        content = (HERE / fname).read_text(encoding="utf-8").rstrip("\n")
        parts.append(content)

    full_text = "\n\n---\n\n".join(parts) + "\n"
    OUTPUT.write_text(full_text, encoding="utf-8")
    print(f"Reconstruido: {OUTPUT} ({len(full_text)} caracteres, {len(ORDER)} arquivos)")


if __name__ == "__main__":
    main()
