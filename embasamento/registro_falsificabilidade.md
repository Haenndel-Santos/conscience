# Registro de Falsificabilidade — Frente G

Documento vivo: toda predição citada no manuscrito (`capitulos/`) ou nos documentos de embasamento (Frentes A-D) aparece aqui com seu estatuto empírico atual. Gerado 2026-08-07, compilado a partir de `mapa_evidencias_pilares.md`, `SINTESE_pilares.md`, `posicionamento_teorias_rivais.md`, `nota_anestesia.md`, os 13 capítulos do manuscrito (`capitulos/`), e os resultados numéricos dos Blocos F/K/N/O do `CHECKLIST_pendencias.md`. Nenhuma predição nova foi inventada aqui — é uma compilação, não uma extensão da teoria.

## Legenda de estatuto

| Símbolo | Significado |
|---|---|
| ✅ CONFIRMADA | Dado empírico real do projeto sustenta a predição com discriminação clara. |
| ⚠️ PARCIAL | Sustentada com ressalva relevante, ou confirmada em parte, não na forma forte/original. |
| ❌ FALHOU | Teste real feito; o resultado não confirma a predição na forma testada. |
| ⏳ EM ANDAMENTO | Teste em execução; resultado preliminar existe mas não é conclusivo. |
| 🔬 SIMULAÇÃO APENAS | Só testado no modelo sintético (V3/V4); nenhum dado empírico real ainda — não é validação. |
| ⭕ NÃO TESTADA | Predição declarada no manuscrito, mas sem dado próprio do projeto (apoio, se houver, é só literatura externa). |
| 🗣️ FILOSÓFICA/NÃO OPERACIONALIZADA | Natureza conceitual; não há proxy quantitativo definido para testar diretamente. |

## Pilar 1 — Integração diferenciada (não hipersincronia)

| # | Predição | Operacionalização | Dado (fonte) | Estatuto |
|---|---|---|---|---|
| 1.1 | Estados de alta integração (vigília) discriminam de estados de baixa integração (sono profundo) via medidas de complexidade | AUC de LZc/PE entre estágios W e N3 (Sleep-EDF) | Bloco F/K: AUC W-vs-N3 LZc=0,992, PE=0,984; Spearman=1,0 na ordenação W>N1>REM>N2>N3 (n=36, 39.086 épocas) | ✅ CONFIRMADA |
| 1.2 | Essa discriminação sobrevive ao controle pela inclinação espectral 1/f — não é redutível ao confundidor de Höhn et al. (2024) | AUC residualizada por expoente 1/f (FOOOF/specparam) vs. AUC bruta, com IC 95% bootstrap por sujeito e correção FDR (Frente G) | Bloco N (Frente C, amostra completa, n=36): AUC cai de 0,992→0,550 (LZc) e 0,984→0,580 (PE) após residualização. IC 95% bootstrap inclui 0,5 nos dois casos (LZc: [0,458–0,633]; PE: [0,474–0,677]) e **nenhum dos dois sobrevive à correção FDR** (q=0,359 e q=0,183). Spearman colapsa de 0,683→−0,010 (LZc) e 0,737→0,085 (PE) ao controlar 1/f. O expoente 1/f sozinho já discrimina W-vs-N3 quase perfeitamente (AUC bruta=0,006, i.e., ~0,994 no sentido inverso) | ❌ FALHOU (na forma forte testada) |
| 1.3 | Um índice de integração×diferenciação (proxy de 2 canais: informação mútua × entropia de permutação) discrimina estágios de sono melhor que sincronia bruta pura | AUC do índice combinado vs. AUC da sincronia bruta, bruta e residualizada por 1/f, com IC 95%/FDR (Frente G) | Bloco N (n=36): bruta, `indice_integ_diferenciada` (AUC=0,218) não supera `sync_bruta` (AUC=0,148) — a sincronia pura discrimina de forma pelo menos tão extrema quanto o índice combinado. Residualizada por 1/f, os três ficam estatisticamente indistinguíveis do acaso e entre si: `sync_bruta`=0,456 [0,368–0,545], `integracao_mi`=0,531 [0,427–0,632], `indice_integ_diferenciada`=0,527 [0,423–0,627] — nenhum sobrevive à FDR (q entre 0,37 e 0,63). Não há evidência de que o índice combinado supere a sincronia bruta | ❌ FALHOU |
| 1.4 | A relação complexidade↔consciência é estado-dependente: "sedação moderada" nominal não prediz complexidade de forma confiável — depende de responsividade comportamental real, não de dose | AUC basal-vs-moderada, dose nominal vs. estratificado por responsividade reconstruída (IC de Wilson) | Bloco K: dose nominal deu AUC abaixo do acaso (LZc=0,33; PE=0,45). Bloco O: estratificado por responsividade, grupo responsivo mostrou aumento paradoxal (AUC=0,79 LZc, 0,64 PE) e grupo drowsy mostrou queda esperada (AUC=0,41 LZc, 0,28 PE) — replica Newman et al. (2026) | ✅ CONFIRMADA |
| 1.5 | Sistemas de alta conectividade formal sem corpo (Φ>0 no sentido da IIT) não são conscientes mesmo com integração alta | Nenhuma — é uma tese de demarcação filosófica, não uma medida quantitativa aplicável a um sistema real testado pelo projeto | Distinção vs. IIT em `posicionamento_teorias_rivais.md` | 🗣️ FILOSÓFICA/NÃO OPERACIONALIZADA |

## Pilar 2 — Corpo constitutivo / interocepção

| # | Predição | Operacionalização | Dado (fonte) | Estatuto |
|---|---|---|---|---|
| 2.1 | Manipulação corporal deveria alterar a *forma* da perspectiva consciente, não apenas sua intensidade | Não definida — `mapa_evidencias_pilares.md` recomenda isso como próximo passo falsificável, sem propor ainda a medida exata | — | ⭕ NÃO TESTADA |

## Cap. 3 — Stress, alostase e Princípio do Regime Ótimo de Ativação

| # | Predição | Operacionalização | Dado (fonte) | Estatuto |
|---|---|---|---|---|
| 3.1 | Ansiedade = acoplamento cérebro-corpo B(t) alto, mas integração efetiva Ψ_eff menor que na vigília plena | Simulação V3: Ψ_eff do regime "ansiedade" vs. regime "vigília" | `consciousness_model_v3.py` — simulação sintética de prova de conceito, nenhum dado EEG real de ansiedade processado pelo projeto | 🔬 SIMULAÇÃO APENAS |
| 3.2 | A relação consciência×ativação tem forma de ótimo intermediário (não escalada monotônica) | Mesma simulação V3, comparação entre os 4 regimes | Idem 3.1 | 🔬 SIMULAÇÃO APENAS |

## Pilar 5 / Cap. 9 — Common knowledge / camada social

| # | Predição | Operacionalização | Dado (fonte) | Estatuto |
|---|---|---|---|---|
| 5.1 | S(t) e C_hum(t) crescem de regime privado para publicamente ratificado, com o índice individual de base permanecendo estável | Simulação V4: agentes com canal público mínimo, M_r/P_u/R_a como proxies operacionais | `consciousness_model_v4_social.py` — confirmado **dentro da simulação**; revisão crítica (Bloco J, `revisao_critica_St_V4.md`) já apontou que a confirmação é quase-tautológica (AUC≈1,0 "por construção") | 🔬 SIMULAÇÃO APENAS (ressalva de circularidade já documentada) |
| 5.2 | Teste não-circular de coordenação social: a coordenação comportamental arriscada (jogo tipo stag-hunt) só tem sucesso no cenário de common knowledge (reconhecimento recíproco), não com mera informação compartilhada | Taxa de sucesso de coordenação por cenário (privado/compartilhado/ratificado), com feedback real do indicador de common knowledge (K_ck, limiar) sobre a dinâmica interna dos agentes, e duas ablações de controle | Frente F (V5), `dados atuais/consciousness_model_v5_social.py`, 80 trials/cenário: sucesso de coordenação privado=0,000, compartilhado=0,000 (apesar de P_u médio=1,0 na decisão — informação ampla não bastou), ratificado=0,913. Ablação (a) — sem o feedback de K_ck, "ratificado" colapsa para 0,000 (confirma que o mecanismo alegado é o responsável). Sweep de p_ack mostra uma faixa de transição real (não instantânea) entre p_ack≈0,004 e ≈0,08 (sucesso sobe de 0% a ~90-100%), com alguma queda não-monotônica no topo da faixa (p_ack=0,12/0,20 caem para 0,80) que é mais provavelmente ruído amostral (25 trials/ponto) do que um efeito real — não investigado a fundo | ✅ CONFIRMADA (prova de conceito sintética; ver ressalvas na tabela e na Frente F) |

## Pilar 6 — Automação inteligente / economia da consciência

| # | Predição | Operacionalização | Dado (fonte) | Estatuto |
|---|---|---|---|---|
| 6.1 | Recrutamento de consciência correlaciona com erro de previsão / novidade / conflito | Não operacionalizada nos dados do projeto | Apoio só em literatura externa (Botvinick et al. 2004; Clark 2013) | ⭕ NÃO TESTADA |

## Pilar 7 / Cap. 12 — Fronteira IA / corporificação

| # | Predição | Operacionalização | Dado (fonte) | Estatuto |
|---|---|---|---|---|
| 7.1 | LLMs puros não satisfazem as condições completas de consciência integrada (falta corpo, interocepção, alostase) | Nenhuma métrica quantitativa definida para aplicar a um LLM real | Cap. 12; apoio em Aru, Larkum & Shine (2023); Seth (2025) | 🗣️ FILOSÓFICA/NÃO OPERACIONALIZADA |
| 7.2 | Sistemas artificiais só se aproximam de consciência com incorporação robusta, interocepção, auto-manutenção e acoplamento dinâmico | Idem 7.1 — critério de demarcação gradiente recomendado por `SINTESE_pilares.md`, ainda não formalizado como medida | Cap. 12 | 🗣️ FILOSÓFICA/NÃO OPERACIONALIZADA |

## Pilar 8 — Hard problem

Debate filosófico por natureza (ver `mapa_evidencias_pilares.md`, Pilar 8); não gera predição empírica testável pelo projeto. Não incluído como entrada de teste.

## Cap. 11 — Testes de estresse da teoria (sonho, psicodélicos, animais, trauma)

| # | Predição | Operacionalização | Dado (fonte) | Estatuto |
|---|---|---|---|---|
| 11.1 | Sonho: no REM, complexidade interna permanece alta enquanto acoplamento cérebro-ambiente ME(t) cai — regime "internamente rico, externamente desacoplado" | LZc/PE agregados por estágio (não separam integração interna de acoplamento externo) | Bloco F/K: REM ficou **abaixo** da vigília tranquila em LZc agregado — não confirma nem refuta a predição específica, porque a métrica atual mede complexidade total, não a redistribuição interno/externo que a teoria de fato afirma. O próprio Cap. 11 já reconhece isso como "predição diferencial... registrada como programa, não como resultado já obtido" | ⚠️ PARCIAL / precisa de nova operacionalização |
| 11.2 | Psicodélicos aumentam certos componentes de complexidade/recursividade combinados com reconfiguração do regime | Não operacionalizada nos dados do projeto | Apoio só em literatura externa (REBUS, Carhart-Harris) | ⭕ NÃO TESTADA |
| 11.3 | Gradiente de consciência entre animais depende do grau de integração, não da posse de linguagem reflexiva | Não operacionalizada nos dados do projeto | Apoio só em literatura externa (Cambridge Declaration on Consciousness) | ⭕ NÃO TESTADA |
| 11.4 | Trauma = regime de captura por ameaça, rígido e potencialmente dissociado | Não operacionalizada nos dados do projeto | Apoio só em literatura externa (subtipo dissociativo do TEPT) | ⭕ NÃO TESTADA |

## Frente B — Predições distintivas frente a teorias rivais

| # | Predição (vs. rival) | Operacionalização | Dado (fonte) | Estatuto |
|---|---|---|---|---|
| B.1 | vs. IIT: a relação complexidade-consciência é estado-dependente, não uma generalização monotônica via Φ/PCI entre modalidades de perda de consciência | Ver 1.4 acima | Bloco K + Bloco O | ⚠️ PARCIAL (já tem dado próprio, mesmo teste de 1.4) |
| B.2 | vs. GNWT: conteúdo consciente pode ser decodificável em córtex posterior sem "ignição" pré-frontal robusta | Nenhuma no projeto; apoio indireto externo | COGITATE Consortium (2025, *Nature*) — não testou a teoria Conscience, testou IIT/GNWT diretamente | ⭕ NÃO TESTADA PELO PROJETO |
| B.3 | vs. FEP/Active Inference: LZc/PE e conectividade top-down (DCM) devem se dissociar sob cetamina | Nenhum dado de cetamina no projeto | `posicionamento_teorias_rivais.md` | ⭕ NÃO TESTADA |
| B.4 | vs. HOT: experiência acompanha o regime de complexidade de 1ª ordem, independente do estado funcional do dlPFC | Nenhuma no projeto; apoio indireto externo | Raccah et al. (2021) | ⭕ NÃO TESTADA PELO PROJETO |
| B.5 | vs. RPT: complexidade de rede ampla (não recorrência local) deve despencar em trials mascarados/não relatados | Nenhum dado de masking no projeto | `posicionamento_teorias_rivais.md` | ⭕ NÃO TESTADA |
| B.6 | vs. AST: assinatura de complexidade global (já fragilizada no propofol agregado) vs. assinatura localizada em TPJ — teste real ainda em aberto | Nenhuma no projeto | `posicionamento_teorias_rivais.md` | ⭕ NÃO TESTADA / teste ainda não decidido |

## Modelo formal (V3/V4) — Cap. 13

| # | Predição | Operacionalização | Dado (fonte) | Estatuto |
|---|---|---|---|---|
| M.1 | O modelo V3 separa regimes (vigília, ansiedade, sono profundo, reflexo) por combinações distintas de parâmetros | Simulação, parâmetros de regime fixados pelo autor | `consciousness_model_v3.py` — separação limpa, mas **por construção**: os regimes são definidos pelos parâmetros escolhidos, não descobertos a partir de dados | 🔬 SIMULAÇÃO APENAS (ressalva de tautologia — motivo da Frente E, ainda não escrita) |
| M.2 | S(t)/C_hum(t) sobe de regime privado para publicamente ratificado mantendo o índice individual estável | Ver 5.1 | `consciousness_model_v4_social.py` | 🔬 SIMULAÇÃO APENAS (mesma ressalva de circularidade) |

## Frente D — Reanálise de anestesia por responsividade (Bloco O)

| # | Predição | Operacionalização | Dado (fonte) | Estatuto |
|---|---|---|---|---|
| D.1 | Sob sedação moderada, subgrupo responsivo mostra aumento *paradoxal* de LZc/PE; subgrupo não-responsivo mostra a queda esperada (replicando Newman et al. 2026) | AUC basal-vs-moderada, separado por grupo de responsividade reconstruída | Bloco O: responsive AUC=0,791 (LZc) / 0,642 (PE); drowsy AUC=0,411 (LZc) / 0,283 (PE), n=20 (13 responsive/7 drowsy) | ✅ CONFIRMADA |
| D.2 | Complexidade basal correlaciona negativamente com a mudança de complexidade sob sedação moderada | Spearman ρ, complexidade basal × delta, por sujeito | Bloco O: PE ρ=−0,749, p=0,0001 (significativo); LZc ρ=−0,340, p=0,143 (não significativo) — mesma direção, força desigual entre métricas | ⚠️ PARCIAL |

## Resumo quantitativo

- Confirmadas (✅): 4 (1.1, 1.4, D.1, 5.2)
- Parciais (⚠️): 3 (11.1, D.2, B.1)
- Falhou (❌): 2 (1.2, 1.3)
- Em andamento (⏳): 0
- Simulação apenas (🔬): 5 (3.1, 3.2, 5.1, M.1, M.2)
- Não testadas (⭕): 10 (2.1, 6.1, 11.2, 11.3, 11.4, B.2, B.3, B.4, B.5, B.6)
- Filosóficas/não operacionalizadas (🗣️): 3 (1.5, 7.1, 7.2)
- Total de entradas no registro: 27

**Leitura honesta (atualizada 2026-08-07, com resultado final das Frentes C/G/F):** o núcleo empírico mais forte do projeto (1.1 — LZc/PE discriminam W-vs-N3 com AUC~0,99, confirmado com duas métricas independentes em 36 sujeitos, robusto a bootstrap/FDR) **permanece válido como descrição do dado bruto**, mas o teste de robustez que este registro sinalizava como pendente (1.2/1.3, controle pela inclinação espectral 1/f) **concluiu de forma negativa para a teoria**: ao residualizar por 1/f, a discriminação de LZc/PE cai para perto do acaso (AUC≈0,55-0,58, IC 95% cruzando 0,5, nenhum sobrevivendo à correção FDR) e a correlação com o estágio do sono colapsa de ~0,68-0,74 para ~0. O expoente 1/f isolado quase discrimina W-vs-N3 sozinho (AUC bruta≈0,994 em módulo). Isso é consistente com o confundidor descrito por Höhn et al. (2024) explicando a maior parte — não necessariamente toda — da discriminação bruta observada em 1.1. Adicionalmente, a alegação-assinatura da teoria (1.3 — integração diferenciada > sincronia bruta pura) também não se sustentou: bruta, o índice combinado não supera a sincronia pura em magnitude de discriminação, e residualizada, os dois ficam estatisticamente indistinguíveis do acaso e um do outro. Isso não invalida o achado 1.1 como observação empírica (a discriminação bruta é real e robusta), mas remove o suporte que 1.2/1.3 dariam à interpretação causal/mecanística proposta pela teoria (integração diferenciada, não confundidor espectral). Do lado social, a Frente F (V5) deu um resultado positivo específico: 5.2 passou no teste não-circular — a coordenação comportamental arriscada só teve sucesso no cenário de common knowledge (91,3% vs. 0% nos outros dois), sobreviveu à ablação de controle (remover o feedback do indicador de common knowledge colapsa a coordenação de volta a 0%), e "compartilhado" não coordenou apesar de informação tão ampla quanto "ratificado" — a checagem central de não-circularidade. É, junto com D.1, um dos dois achados novos e limpos desta rodada — mas continua sendo simulação sintética de prova de conceito, não validação empírica sobre cognição social real. A maior parte das predições específicas de cada pilar (corpo, IA, animais, psicodélicos, trauma, quase todas as distintivas vs. rivais) **ainda não tem dado próprio do projeto** — são predições declaradas, não testes feitos. Isso não é fraqueza escondida: é exatamente o que este registro existe para deixar visível — inclusive quando o resultado, como em 1.2/1.3, é negativo para a própria teoria.

## Manutenção

Este documento deve ser atualizado sempre que: (a) um Bloco novo do `CHECKLIST_pendencias.md` mudar o estatuto de uma predição já listada aqui; (b) o manuscrito (`capitulos/`) ganhar uma predição nova; (c) a Frente E for rodada (atualizar M.1 — ainda pendente, ver Bloco Q do CHECKLIST). (1.2/1.3 refletem o resultado final da Frente C, n=36, com reforço estatístico da Frente G — bootstrap por sujeito + FDR — aplicado em 2026-08-07; 5.2 reflete o resultado da Frente F/V5, aplicado em 2026-08-07.)
