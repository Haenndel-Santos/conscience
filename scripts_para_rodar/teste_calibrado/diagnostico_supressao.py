"""Por que o controle de 1/f esvazia o sono e amplifica a anestesia?

Produz os numeros da secao 2 de `embasamento/nota_estado_da_arte_1f.md`.

O Cap. 11 registrava esse contraste como "nitido, e permanece sem explicacao". Ele tem
explicacao, e ela esta na estrutura de correlacao entre tres coisas: a metrica (LZc), o
covariavel de controle (expoente aperiodico 1/f) e o estado.

  CONFUNDIMENTO/MEDIACAO -- o covariavel rastreia o estado tao bem quanto a metrica e e
  quase colinear com ela. Residualizar remove o sinal junto com o suposto confundidor.
  E o caso do sono.

  SUPRESSAO -- o covariavel quase nao rastreia o estado, mas segue fortemente acoplado a
  metrica. Removê-lo desmascara uma associacao que ja existia no dado bruto, sem que isso
  constitua teste de nada. E o caso da anestesia.

A distincao importa porque muda a leitura: "o efeito da anestesia sobreviveu ao controle
que matou o sono" so seria verdade se as duas operacoes fossem a mesma. Nao sao.

ATENCAO: isto diagnostica o PADRAO ESTATISTICO, nao resolve mediador-vs-confundidor, que
e questao causal e nao e decidivel com dado observacional (ver secao 3 da nota).

Uso:
    python diagnostico_supressao.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).parent
BASE = HERE.parent
ANESTESIA = BASE / "anestesia_1f" / "propofol_1f_por_epoca.csv"
SONO = BASE / "integracao_diferenciada" / "integracao_diferenciada_por_epoca.csv"


def analisar(csv: Path, state_col: str, neg: str, pos: str, metric: str, rotulo: str):
    if not csv.exists():
        print(f"[aviso] {csv} nao encontrado — pulando {rotulo}")
        return None
    df = pd.read_csv(csv)
    d = df[df[state_col].isin([neg, pos])].dropna(subset=[metric, "exponent_1f"]).copy()
    d["y"] = (d[state_col] == pos).astype(int)

    r_my = stats.spearmanr(d[metric], d["y"]).statistic           # metrica x estado
    r_ay = stats.spearmanr(d["exponent_1f"], d["y"]).statistic    # expoente x estado
    r_ma = stats.spearmanr(d[metric], d["exponent_1f"]).statistic # metrica x expoente
    produto = r_ay * r_ma

    # Supressao: o caminho indireto (estado -> expoente -> metrica) tem sinal OPOSTO ao da
    # associacao direta, entao o expoente mascarava parte dela. Confundimento/mediacao: o
    # caminho indireto tem o MESMO sinal, entao o expoente sustentava a associacao.
    if np.sign(produto) != np.sign(r_my) and abs(r_my) > 0.02:
        padrao = "SUPRESSAO — o expoente mascarava a associacao da metrica"
    else:
        padrao = "CONFUNDIMENTO/MEDIACAO — o expoente sustentava a associacao"

    print(f"\n=== {rotulo} ({neg} -> {pos}, {len(d)} epocas) ===")
    print(f"  metrica  x estado    rho = {r_my:+.3f}")
    print(f"  expoente x estado    rho = {r_ay:+.3f}   <- a coluna que decide")
    print(f"  metrica  x expoente  rho = {r_ma:+.3f}")
    print(f"  caminho indireto (expoente x estado)*(metrica x expoente) = {produto:+.3f}")
    print(f"  -> {padrao}")
    return {"desenho": rotulo, "n_epocas": len(d), "metrica_x_estado": r_my,
            "expoente_x_estado": r_ay, "metrica_x_expoente": r_ma,
            "caminho_indireto": produto, "padrao": padrao.split(" — ")[0]}


def main():
    print("=== Diagnostico: supressao ou confundimento? (Spearman, epoca a epoca) ===",
          flush=True)
    linhas = [r for r in (
        analisar(ANESTESIA, "state", "basal", "sedacao_moderada", "lzc",
                 "ANESTESIA — LZc"),
        analisar(SONO, "stage", "N3", "W", "lzc", "SONO — LZc"),
        analisar(SONO, "stage", "N3", "W", "pe", "SONO — PE"),
    ) if r is not None]

    if linhas:
        res = pd.DataFrame(linhas)
        res.to_csv(HERE / "diagnostico_supressao.csv", index=False)
        print(f"\nSaida: {HERE / 'diagnostico_supressao.csv'}")
        print("\nLeitura: a coluna `expoente_x_estado` e a que separa os dois casos. Onde o")
        print("expoente rastreia o estado, ele e explicacao rival genuina e o controle testa")
        print("algo. Onde nao rastreia, o controle so remove ruido correlacionado.")


if __name__ == "__main__":
    main()
