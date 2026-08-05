# V4 — prova de conceito da camada social (S(t) / C_hum(t))

Simulação multiagente mínima que operacionaliza S(t) e C_hum(t) — ver
docstring de `consciousness_model_v4_social.py` para as definições
operacionais completas e as ressalvas de honestidade metodológica.

**Resultado central** (15 execuções por cenário, seed=42):

```
              C_base_mean              S_mean           C_hum_mean           M_r_mean            P_u_mean            R_a_mean          
                     mean       std      mean       std       mean       std     mean       std      mean       std      mean       std
scenario                                                                                                                               
privado          0.611239  0.005423  0.000000  0.000000   0.611239  0.005423    0.000  0.000000  0.000000  0.000000  0.000000  0.000000
compartilhado    0.610530  0.005022  0.257306  0.002748   0.674856  0.005282    0.000  0.000000  0.771917  0.008245  0.000000  0.000000
ratificado       0.609150  0.006031  0.721352  0.027878   0.789488  0.007867    0.713  0.033273  0.759250  0.019952  0.691806  0.036577
```

**AUC "ratificado vs. privado"**:
- S(t): 1.0000
- C_hum(t): 1.0000
- C_base(t) (índice individual, sem camada social): 0.3911

C_base não discrimina os cenários (esperado — os agentes não sabem, em
seu estado interno, se estão ou não se comunicando); S(t) e C_hum(t)
discriminam fortemente, confirmando a predição qualitativa do Cap. 9
dentro desta operacionalização mínima.

**Reprodutibilidade por seed:** True (duas execuções do cenário
"ratificado" com seed=42 produzem series numericamente idênticas).

**IMPORTANTE — leia antes de citar estes números em qualquer lugar:**
resultados de simulação sintética de prova de conceito. S(t) é proxy
operacional de um processo social mínimo (broadcast + recepção
probabilística + reconhecimento recíproco probabilístico), não medida de
consciência intersubjetiva real. "Profundidade de mentalização recursiva"
aqui é um contador limitado a 2 níveis, não
uma simulação de crenças aninhadas. Não constitui validação empírica de
nada sobre cognição social real.

Arquivos:
- `series_temporais_exemplo.csv` — uma execução por cenário (seed=42), para a figura.
- `monte_carlo_runs.csv` — 15 execuções por cenário (dados brutos).
- `resumo_por_cenario.csv` — médias/desvios por cenário.
- `auc_ratificado_vs_privado.txt` — AUC de S, C_hum e C_base.
- `s_e_chum_por_cenario.png` — figura (C_base, S, C_hum ao longo do tempo, 3 cenários).
