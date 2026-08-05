# Confronto Empírico Inicial — dados públicos × modelo *Conscience*

Data: 2026-08-05 · Escopo: busca de bancos públicos + confronto das predições-chave do modelo com valores publicados. **Limitação desta sessão:** o acesso direto a repositórios de dados (PhysioNet/OpenNeuro) está bloqueado no ambiente, então este é um confronto por *literatura publicada* + mapa de datasets com protocolo de cálculo — não um recomputo sobre EEG bruto. As referências abaixo, quando entrarem no manuscrito, devem passar pela mesma verificação do Bloco A.

---

## Parte 1 — Predições do modelo confrontadas com evidência publicada

O modelo produz o índice 𝒞 e componentes (integração efetiva Ψ_eff, acoplamento B, complexidade K, recursividade R) e prevê uma **ordenação de regimes** e uma tese qualitativa (**integração diferenciada, não hipersincronia**). Confronto:

| Predição do modelo | Evidência empírica publicada | Veredito |
|---|---|---|
| Ordem vigília > sono profundo (𝒞/complexidade) | LZc em EEG: vigília 0,541 · REM 0,532 · N2 0,496 · **N3 0,451** (Front Hum Neurosci 2022). Queda vigília→NREM com Cohen's d>0,8 (Schartner 2015/2017). | ✅ **Confirmado** |
| REM ≈ vigília (alto 𝒞 interno, mesmo desacoplado do ambiente) — Cap. 11 | LZc REM (0,532) colado à vigília, muito acima de N3 (Front Hum Neurosci 2022). | ✅ **Confirmado** |
| Estados subintegrados (reflexo/anestesia) têm 𝒞 baixo | PCI: faixa consciente 0,44–0,67 vs inconsciente 0,12–0,31; cutoff validado PCI\*=0,31 (Casali 2013; Casarotto 2016). | ✅ **Confirmado** |
| **Integração diferenciada ≠ hipersincronia** (núcleo da teoria) | Crise epiléptica (hipersincronia) → **queda** de complexidade/entropia, discrimina perda de consciência (Sci Rep 2022). Burst-suppression (sincronia estereotipada) → PCI/LZc no piso (Casali 2013; Sarasso 2015). | ✅ **Confirmado (forte)** |
| Consciência ≠ mero arousal/responsividade | Ketamina: irresponsiva **mas** com experiência vívida → PCI alto (>0,31), agrupada com vigília (Sarasso 2015). | ✅ **Confirmado** |
| Estados de alta diferenciação podem exceder a vigília basal | Psicodélicos (LSD/psilocibina/ketamina) **aumentam** diversidade do sinal acima da vigília (Schartner & Carhart-Harris 2017). | ✅ Coerente com "integração diferenciada" |
| **Ansiedade = alta ativação/acoplamento + integração efetiva reduzida** | Ver Parte 2 — apoio **parcial e desigual**. | ⚠️ **Requer refinamento conceitual** |

**Conclusão da Parte 1:** o eixo central da teoria — a hierarquia vigília/REM > NREM profundo > anestesia, e a tese de que a consciência exige *integração diferenciada* (nem silêncio, nem hipersincronia) — está **fortemente alinhado com a evidência publicada**. Este é um resultado robusto: o modelo sintético reproduz uma ordenação que a literatura empírica sustenta de forma independente por múltiplas medidas (LZc, PCI, entropia).

## Parte 2 — O ponto que precisa de refinamento: a ansiedade

A predição sobre a ansiedade é a **mais frágil** e a evidência é honestamente **mista**:

- **Bem apoiado — flexibilidade/repertório reduzido:** TAG e pânico passam menos tempo no estado integrado e fazem menos transições (Xu et al. 2021); ansiedade/estresse/OCD transdiagnosticamente mostram menor flexibilidade neural, que a psicoterapia aumenta (Schiepek et al. 2021); estresse agudo reduz a variabilidade de transição, correlacionada com controle cognitivo (Wang et al. 2022, *PNAS*).
- **Bem apoiado — curva em U-invertido arousal × integração:** base neural moderna sólida via locus coeruleus–noradrenalina, com evidência causal e cross-species (Tong et al. 2025, *Nat Commun*); mecanismo pré-frontal estabelecido (Arnsten 2009, *Nat Rev Neurosci*); estreitamento atencional top-down sob estresse (Sänger et al. 2014).
- **Contrariado — "menos integração/acoplamento" em sentido literal:** sob estresse agudo a integração global **aumenta** (Wang et al. 2022); no PTSD a conectividade estática está **elevada**, com a *variabilidade temporal* reduzida (Jin et al. 2017). Ou seja: **rigidez de alto acoplamento**, não desacoplamento.
- **Misto — entropia/complexidade em TAG:** frequentemente **aumentada** no plano espacial/local (Fan et al. 2023; Wang et al. 2018), dependente da métrica.

**Implicação teórica (importante e favorável ao modelo):** a leitura defensável é que a ansiedade é **alta ativação + alto acoplamento corporal + integração rígida e pouco flexível** — não "menos integração" bruta. Isso **encaixa na arquitetura que o modelo já tem**: o índice separa o acoplamento **B** (que permanece alto na ansiedade) da integração efetiva **Ψ_eff**, que pondera complexidade **K** e recursividade **R** — isto é, a *diferenciação/flexibilidade*, que é justamente o que cai. A recomendação, portanto, é **definir explicitamente "integração efetiva" como integração diferenciada/flexível (não magnitude de conexão instantânea)**. Com essa definição, a predição passa de "especulativa" para "parcialmente apoiada", e o próprio modelo V3 já a expressa (regime de ansiedade: B alto, Ψ_eff menor que a vigília).

## Parte 3 — Mapa de bancos públicos (para o programa empírico)

| Dataset | Modalidade · estados | Acesso | Testa no modelo |
|---|---|---|---|
| **Sleep-EDF Expanded** | PSG, estágios W/REM/N1–N3 · 197 noites | **Aberto (ODC-BY), sem cadastro** · physionet.org/content/sleep-edfx | Complexidade (LZc/entropia) e recursividade por estágio — **vigília vs N3** |
| **NSRR / SHHS** | PSG + ECG/respiração/SpO₂ · milhares de sujeitos | Aberto mediante Data Access Request | Acoplamento **cérebro–corpo (B)** por estágio, em escala |
| **Cambridge Propofol EEG** (Chennu) | EEG 91 canais · basal→sedação→recuperação · 20 suj. | **Aberto (CC BY)** · repository.cam.ac.uk | Ψ_eff/K na transição consciência→inconsciência |
| **OpenNeuro ds006623** | fMRI · acordado→perda de responsividade→recuperação · 26 suj. | **Aberto (CC0)** | Integração efetiva com paradigma de consciência encoberta |
| **LEMON (MPI-Leipzig)** | EEG 62 ch + fisiologia contínua + MRI · 228 suj. | Download livre (checar DUA) | **B (cérebro–corpo)** em vigília; aproxima ativação |
| **COGITATE** | M-EEG/fMRI/iEEG · percepção consciente · vigília | Open-access via registro/DUA | Recursividade **R** / processamento recorrente (IIT×GNWT) |
| **OpenNeuro ds006072** | fMRI psilocibina vs metilfenidato · 7 suj. densos | **Aberto (CC BY-NC-ND)** | Desincronização/diferenciação em estado alterado |
| PCI / TMS-EEG (Casali/Sarasso) | TMS-EEG · vigília/sono/anestesia | **Não aberto** (sob solicitação; algoritmo público) | "Padrão-ouro" de Ψ_eff via perturbação |

Recurso "de ansiedade" de consciência **não existe** como dataset dedicado aberto; aproximar via LEMON (fisiologia/afeto) e dados de estresse agudo/dynamic-FC citados na Parte 2.

## Parte 4 — Protocolo recomendado para a primeira análise real (quando houver acesso a dados)

1. **Dataset:** Sleep-EDF Expanded (o mais acessível; hipnogramas prontos).
2. **Pré-processamento:** por época de 30 s, canal Fpz-Cz/Pz-Oz; filtro 0,5–40 Hz (MNE ou YASA).
3. **Métrica-alvo:** Lempel-Ziv complexity (LZc) por época, agregada por estágio (W, REM, N1, N2, N3) — proxy direto de K/𝒞.
4. **Teste da predição:** confirmar a ordenação W ≈ REM > N2 > N3 (esperado por Front Hum Neurosci 2022) e comparar a *forma* da queda com a ordenação do 𝒞 do modelo (wake > deep_sleep). Reportar AUC W-vs-N3 como no V3.
5. **Passo 2 (acoplamento B):** migrar para NSRR/SHHS e computar acoplamento EEG↔ECG/respiração por estágio.
6. **Calibração honesta:** o modelo não está em unidades de EEG; o confronto é de **ordenação e direção**, não de valores absolutos. Ajuste de escala deve ser reportado como calibração, não como validação circular.

## Limitações
- Confronto por literatura, não por recomputo (rede a repositórios bloqueada nesta sessão).
- Referências desta análise (Casali 2013, Sarasso 2015, Casarotto 2016, Schartner 2015/2017, Arnsten 2009, Xu 2021, Jin 2017, Wang 2022, Tong 2025, etc.) são reconhecidas na área, mas as de 2025 e a de LZc-por-estágio (Front Hum Neurosci 2022) devem ser **verificadas na prova** antes de entrar no manuscrito.
- Dados sintéticos do modelo ≠ validação empírica; este confronto estabelece **plausibilidade e direção**, e desenha o teste formal.
