# Poder estatístico / efeito mínimo detectável — sono, n=36 (gerado automaticamente)

Pergunta: dado o desenho atual (n=36 sujeitos, bootstrap por sujeito, alfa=0,05), qual é
o menor efeito verdadeiro (Cohen's dz pareado, e seu AUC equivalente) que este projeto
conseguiria detectar de forma confiável (80% de poder)?

Dado usado: `integracao_diferenciada_por_epoca.csv` (LZc residualizado por 1/f dentro da
amostra, W vs N3, 36 sujeitos com os dois estágios).

Efeito observado nos dados reais: diferença pareada média = -0.00502, DP = 0.05055,
Cohen's dz = -0.0994, AUC observada (ingênua, época-pooled) = 0.5504.

## Fórmula fechada (nível 1)
80% de poder exigiria dz ≥ 0.4669.
90% de poder exigiria dz ≥ 0.5403.

## Simulação Monte Carlo (nível 2, reescalando a distribuição real não-normal)
 dz_alvo  auc_equivalente_media  poder_estimado  n_sim
     0.0               0.570078           0.000    500
     0.1               0.589528           0.272    500
     0.2               0.608725           1.000    500
     0.3               0.627527           1.000    500
     0.4               0.645901           1.000    500
     0.5               0.663825           1.000    500
     0.6               0.681271           1.000    500
     0.8               0.714684           1.000    500
     1.0               0.745824           1.000    500

**Efeito mínimo detectável (poder ≥80%) pela simulação: dz ≈ 0.2.**

## Como ler (preencher/revisar depois — não inventar conclusão aqui)
- Se o dz observado nos dados reais (-0.0994) estiver MUITO abaixo do MDE
  (dz≈0.2), isso significa que mesmo um
  efeito real, mas pequeno, teria sido detectável por este desenho — reforça a leitura
  de que o resultado nulo é informativo (efeito verdadeiro é provavelmente próximo de
  zero, não apenas "não detectado por falta de poder").
- Se o dz observado estivesse PRÓXIMO do MDE, a leitura mudaria: o desenho atual teria
  poder limitado para distinguir "efeito pequeno real" de "efeito nulo", e o resultado
  negativo seria menos conclusivo do que o texto atual do Cap. 11 sugere.
- Isto usa a variância REAL observada nos 36 sujeitos (não uma suposição teórica), então
  reflete a heterogeneidade real do dado, incluindo os sujeitos com poucas épocas de N3.
