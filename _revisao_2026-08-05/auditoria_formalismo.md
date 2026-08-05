# Auditoria de Formalismo — texto ↔ código

Data: 2026-08-05 · Fontes: `Versao atual.txt` (Cap. 9 e 13) e os scripts `consciousness_toy_model.py`, `consciousness_model_v2.py`, `consciousness_model_v3.py`.
Objetivo (regra do `formalism-and-model-guardian`): confirmar que cada símbolo do manuscrito tem estatuto claro, é de fato implementado, e não promete mais do que o texto sustenta.

## Veredito

O **núcleo do formalismo está fielmente implementado**: o estado X(t)=(m,b,e), a integração efetiva Ψ_eff, o proxy fenomenológico Q e o índice 𝒞 existem no código e seguem a estrutura das fórmulas do Cap. 13. Há, porém, **três lacunas que exigem disclosure honesto** e alguns pontos de padronização de versão. A mais importante à época desta auditoria: **a camada social S(t) / 𝒞_hum não era simulada em nenhum script** — era puramente conceitual (ver Nota 5, atualizada em 2026-08-05 com a chegada de `consciousness_model_v4_social.py`, que passa a oferecer uma prova de conceito mínima).

## Mapa símbolo → código → estatuto

| Símbolo (texto) | No código | O que é | Estatuto declarado | Situação |
|---|---|---|---|---|
| X(t)=(m,b,e) | `self.m`, `self.b`, `self.e` | estado neural, corporal, ambiente | variáveis de estado | ✅ implementado |
| B(t) | `B = _coupling(m_hist,b_hist)` | correlação cruzada média cérebro–corpo | proxy operacional | ✅ |
| ME(t) | `ME = _coupling(m_hist,e_hist)` | acoplamento cérebro–ambiente | proxy operacional | ✅ (toy: `I_me`) |
| K(t) | `K = _complexity(m_hist)` | complexidade (variabilidade balanceada) | proxy operacional | ✅ |
| R(t) | `R = _recursivity(psi_hist)` | recursividade (autocorrelação lag-1 de Ψ) | proxy operacional | ✅ |
| E(t) | `self.E` (power_in − dissipation) | disponibilidade de recurso metabólico/computacional | proxy (rebaixado no Cap.13) | ✅ coerente |
| Ψ_eff(t) | `Psi_eff = (E/(E+E0))·Psi` | integração efetiva | construto central | ✅ ver nota 1 |
| M(t) | `self.M` | traço de memória (consolidação/decaimento) | variável dinâmica | ✅ |
| V(t) | `V = V_bio + V_soc` | valoração corporal + social | proxy operacional | ✅ |
| Q(t) | `Q = σ(η1Ψ_eff+η2M+η3V − b)` | potencial fenomenológico (não qualia) | proxy explícito | ✅ ver nota 2 |
| 𝒞(t) | `C_idx` | índice de consciência | indicador de regime | ✅ ver nota 3 |
| G(t) / nível | `level` (0–5 por limiares) | posição no gradiente | leitura discreta | ✅ |
| **S(t)** | **— (ausente)** | camada social/intersubjetiva | provisório (Cap.9) | ⚠️ **não implementado** |
| **𝒞_hum(t)** | **— (ausente)** | índice humano = 𝒞 + w₅S | conceitual | ⚠️ **não implementado** |
| M_r, P_u, R_a | — (ausente) | mentalização recursiva, publicidade, ratificação | provisório | ⚠️ não implementado |

## Notas de discrepância (a resolver no texto ou no código)

**Nota 1 — Ψ_eff tem um fator a mais no código.** A fórmula do Cap. 13 é
`Ψ_eff = [E/(E+E₀)]·(α B + β ME + γ K + δ R)`.
O código multiplica ainda por `coherence_bias` (parâmetro por regime): `Psi = coherence_bias·(w_mb·B + w_me·ME + w_k·K + w_r·R)`. Esse `coherence_bias` (e o `arousal_bias`, que desloca a magnitude corporal) **não aparecem nas equações publicadas**. São botões que instanciam os regimes. → Ou explicitar esses parâmetros no formalismo, ou declará-los como "parâmetros de regime" fora do núcleo da equação. Correspondência de pesos: α↔w_mb, β↔w_me, γ↔w_k, δ↔w_r; E₀=0,45 (V2/V3) ou 0,5 (toy).

**Nota 2 — Q tem um intercepto omitido.** O texto escreve `Q = σ(η1Ψ_eff + η2M + η3V)`. O código usa `σ(2.7·Ψ_eff + 1.5·M + 0.9·V − 1.05)` — há um **termo constante −1,05** (e sigmoides de valoração com seus próprios interceptos). Sugestão: incluir o intercepto na fórmula do manuscrito (`… + η₀`) para fidelidade.

**Nota 3 — 𝓜 no índice 𝒞 é, na verdade, a memória saturada.** O Cap. 13 escreve `𝒞 = w₁Ψ_eff + w₂Q + w₃𝓜 + w₄B`. No código, o termo de memória é `M_cap = M/(M+1)` (transformação saturante), não M cru. → Escrever explicitamente que 𝓜 = M/(M+1). Pesos V2/V3: w₁=0,45 · w₂=0,20 · w₃=0,17 · w₄=0,18 (somam 1,0).

**Nota 4 — deriva de versões.** Os pesos e limiares mudam entre toy/V2/V3:
- Ψ_eff (toy): α,β,γ,δ = 0,30/0,25/0,20/0,25 · (V2/V3): 0,35/0,20/0,20/0,25.
- 𝒞 (toy): 0,42/0,24/0,18/0,16 · (V2/V3): 0,45/0,20/0,17/0,18.
- Limiares de nível (toy): [0,12·0,24·0,40·0,58·0,76] · (V2/V3): [0,10·0,22·0,38·0,56·0,74].
→ Declarar **qual versão é canônica** (recomendo V3) e citar sempre os pesos dessa versão no manuscrito.

**Nota 5 — atualização (2026-08-05, pós-V4): a camada social agora tem uma prova de conceito mínima.** O manuscrito apresenta `S(t)=λ₁M_r+λ₂P_u+λ₃R_a` e `𝒞_hum = 𝒞 + w₅S`. Até a V3, nenhum script implementava S, M_r, P_u ou R_a — o `V_soc` presente no código era apenas um peso de valoração social dentro de V, não a ratificação intersubjetiva do Cap. 9. Isso mudou parcialmente com `consciousness_model_v4_social.py`: uma simulação multiagente (N=6 agentes rodando a dinâmica individual do V3, sem alterá-la, comunicando-se por um canal público mínimo) que operacionaliza M_r, P_u e R_a como proxies provisórios e testa a predição de que S(t)/𝒞_hum crescem de um cenário privado para um publicamente ratificado, enquanto o índice individual de base (𝒞) permanece estável — confirmado com AUC=1,0 para S e 𝒞_hum, contra AUC≈0,46 (nível de acaso) para 𝒞 sozinho. → O texto deve continuar dizendo, de forma explícita, que essa é uma **simulação mínima de prova de conceito**, não uma medida de consciência intersubjetiva real: a "profundidade de mentalização recursiva" modelada é um contador de poucos níveis (0–2), não uma simulação de crenças aninhadas ou lógica epistêmica, e o resultado é direção/ordenação em dados sintéticos, não validação empírica sobre cognição social real.

## Recomendações (itens B3–B5)

1. Inserir no Cap. 13 **uma única tabela símbolo → definição operacional → estatuto** (como a acima), evitando que o leitor confunda proxy com evidência.
2. Corrigir as fórmulas para incluir interceptos e o fator de saturação da memória (notas 2 e 3), ou declarar que as equações são "esquemáticas".
3. Adotar V3 como versão canônica dos coeficientes e remover a ambiguidade de versões (nota 4).
4. Acrescentar uma frase padronizada onde os números aparecem: *"resultados de simulação sintética de prova de conceito; não constituem validação empírica"* (o projeto já diz isso na nota metodológica — replicar junto às tabelas).
5. Marcar S(t)/𝒞_hum como trabalho futuro de implementação, não como resultado existente.
