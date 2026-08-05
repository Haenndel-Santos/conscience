## Capítulo 13

### Esboço formal revisado

A estrutura formal básica pode ser mantida, com esclarecimentos importantes. As equações a seguir devem ser lidas como **esquemáticas**: expõem a lógica conceitual do modelo, enquanto a implementação computacional — na versão **V3** (`consciousness_model_v3.py`), adotada aqui como canônica em relação às versões toy e V2 — acrescenta parâmetros de regime, interceptos e uma transformação de saturação que a notação de corpo do texto omitia até esta revisão. Cada um deles é declarado explicitamente abaixo, para que nenhum proxy operacional seja lido como evidência.

O estado do sistema é:

$$
X(t)=\big(m(t),b(t),e(t)\big)
$$

onde $m(t)$ representa estados neurais, $b(t)$ estados corporais/interoceptivos e $e(t)$ o ambiente.

A integração efetiva é:

$$
\Psi_{\text{eff}}(t)=\frac{E(t)}{E(t)+E_0}\left(\alpha B(t)+\beta\, ME(t)+\gamma K(t)+\delta R(t)\right)
$$

Aqui, uma correção conceitual importante é necessária: $E(t)$ não deve ser tratado, neste estágio, como energia física fundamental plenamente especificada. Ele deve ser entendido mais modestamente como **disponibilidade funcional de recursos metabólicos/computacionais para sustentar integração recursiva**. Isso evita que a variável funcione como placeholder metafórico demais e, ao mesmo tempo, preserva sua importância no modelo.

Uma segunda correção, terminológica, é decisiva para não superestimar o que $\Psi_{\text{eff}}$ mede: **integração efetiva não é magnitude de acoplamento**. $B(t)$ e $ME(t)$ contribuem para $\Psi_{\text{eff}}$, mas são os termos que carregam diferenciação — $K(t)$, a complexidade, e $R(t)$, a recursividade — que distinguem um regime genuinamente integrado de um regime meramente acoplado. Essa distinção deixou de ser apenas conceitual quando confrontada com evidência publicada sobre ansiedade: sob estresse agudo, o acoplamento cérebro-corpo tende a permanecer alto ou mesmo aumentar, enquanto a flexibilidade de transição entre estados cai. A leitura correta de $\Psi_{\text{eff}}$ é, portanto, como **integração diferenciada e flexível** — a capacidade de manter subsistemas coordenados sem colapsá-los em rigidez —, não como intensidade bruta de conexão instantânea. É essa leitura que permite distinguir, no Cap. 3, a vigília integrada da ansiedade: ambas exibem $B(t)$ elevado, mas só a primeira sustenta $\Psi_{\text{eff}}$ alto.

Na implementação, $\Psi_{\text{eff}}$ carrega ainda um fator adicional, e a valoração corporal é deslocada por outro:

$$
\Psi(t) = \text{coherence\_bias} \cdot \big(w_{mb} B(t) + w_{me} ME(t) + w_k K(t) + w_r R(t)\big), \qquad \Psi_{\text{eff}}(t) = \frac{E(t)}{E(t)+E_0}\,\Psi(t)
$$

$\text{coherence\_bias}$ e $\text{arousal\_bias}$ não pertencem ao núcleo conceitual da equação: são **parâmetros de regime** que, junto aos ganhos de acoplamento e ruído, instanciam computacionalmente cada regime (vigília, ansiedade, sono profundo, reflexo) dentro da mesma arquitetura. Registrar essa distinção evita que um parâmetro de calibração do experimento seja confundido com uma variável teórica do modelo.

O proxy fenomenológico é:

$$
Q(t)=\sigma\big(\eta_1\Psi_{\text{eff}}(t)+\eta_2 M(t)+\eta_3 V(t) + \eta_0\big)
$$

em que $\eta_0$ é um intercepto necessário para que a sigmoide $\sigma$ opere na faixa correta de sensibilidade — negativo na implementação V3 ($\eta_0=-1{,}05$, com $\eta_1=2{,}7$, $\eta_2=1{,}5$, $\eta_3=0{,}9$), funcionando como um limiar mínimo abaixo do qual $Q$ permanece próximo de zero mesmo com $\Psi_{\text{eff}}$, $M$ e $V$ positivos.

E o índice global é:

$$
\mathcal{C}(t)=w_1\Psi_{\text{eff}}(t)+w_2Q(t)+w_3\mathcal{M}(t)+w_4B(t)
$$

onde $\mathcal{M}(t) = \dfrac{M(t)}{M(t)+1}$ é a **memória saturada**: uma transformação de $M(t)$ que comprime valores grandes de memória acumulada num intervalo limitado, evitando que um traço de memória muito longo domine o índice de forma desproporcional. $\mathcal{M}(t)$ não é o traço de memória bruto $M(t)$; o texto passa a distingui-los explicitamente por essa razão.

No caso humano, a teoria propõe:

$$
\mathcal{C}_{hum}(t)=w_1\Psi_{\text{eff}}(t)+w_2Q(t)+w_3\mathcal{M}(t)+w_4B(t)+w_5S(t)
$$

Esta última equação exigia, até a versão V3, uma advertência que não podia ficar implícita: nem $S(t)$ nem $\mathcal{C}_{hum}(t)$ eram simulados em qualquer um dos três primeiros scripts do modelo (toy, V2, V3). Isso mudou de forma limitada com `consciousness_model_v4_social.py`: **$S(t)$ e $\mathcal{C}_{hum}(t)$ passam a ser minimamente simulados, como prova de conceito**. O V4 roda múltiplos agentes com a mesma dinâmica individual do V3 — sem alterá-la — comunicando-se por um canal público mínimo, do qual $M_r(t)$, $P_u(t)$ e $R_a(t)$ são lidos como proxies operacionais explícitos: publicidade como fração de agentes que receberam um conteúdo; ratificação como fração que sinalizou reconhecimento recíproco; mentalização recursiva como uma contagem de poucos níveis que só avança quando há reconhecimento — mera recepção unilateral não conta como "eu sei que você sabe". A simulação testa a predição de que $S(t)$ e $\mathcal{C}_{hum}(t)$ crescem de um regime privado para um publicamente ratificado enquanto o índice individual de base permanece estável, e essa predição se confirma dentro da operacionalização adotada. Isso continua sendo, é preciso repetir, **simulação sintética de prova de conceito**, não uma medida de consciência intersubjetiva real: o contador de mentalização recursiva do V4 não modela crenças aninhadas nem lógica epistêmica, e o mecanismo de reconhecimento é um sinal probabilístico, não uma representação do estado mental alheio. O que os scripts anteriores ao V4 chamavam de valoração social (componente $V_{soc}$ de $V(t)$) continua sendo apenas um peso de contexto social dentro da valoração — não a ratificação intersubjetiva descrita no Cap. 9, que só o V4 aproxima, e apenas de forma mínima.

É importante esclarecer, ainda, que $\mathcal{C}(t)$ não deve ser lido ingenuamente como “quanta consciência” um sistema tem em escala absoluta. Ele é melhor tratado como **indicador de posição do sistema em um espaço de regimes**. Em desenvolvimento futuro, isso pode mesmo evoluir de um índice escalar para um **espaço de fase vetorial**, no qual diferentes combinações de integração corporal, memória, valoração e common knowledge definiriam tipos distintos de estado consciente.

### Estatuto de cada variável e versão canônica

A tabela a seguir resume o estatuto de cada símbolo, para que nenhum proxy operacional seja confundido com evidência empírica:

| Símbolo | O que é | Estatuto |
|---|---|---|
| $X(t)=(m,b,e)$ | Estado neural, corporal e ambiental | Variáveis de estado |
| $B(t)$ | Acoplamento cérebro–corpo (correlação cruzada média) | Proxy operacional |
| $ME(t)$ | Acoplamento cérebro–ambiente | Proxy operacional |
| $K(t)$ | Complexidade (variabilidade balanceada) | Proxy operacional |
| $R(t)$ | Recursividade (autocorrelação de $\Psi_{\text{eff}}$) | Proxy operacional |
| $E(t)$ | Disponibilidade funcional de recurso metabólico/computacional | Proxy conceitual |
| $\Psi_{\text{eff}}(t)$ | Integração efetiva — diferenciada/flexível, não magnitude de acoplamento | Construto central |
| $M(t)$ | Traço de memória (consolidação/decaimento) | Variável dinâmica |
| $\mathcal{M}(t)=M(t)/(M(t)+1)$ | Memória saturada | Transformação operacional |
| $V(t)$ | Valoração corporal + social | Proxy operacional |
| $Q(t)$ | Potencial fenomenológico (proxy — não é qualia) | Proxy explícito |
| $\mathcal{C}(t)$ | Índice de consciência | Indicador de regime |
| $\text{coherence\_bias}$, $\text{arousal\_bias}$ | Ganho de coerência e deslocamento de ativação por regime | Parâmetros de regime (fora do núcleo conceitual) |
| $S(t)$ | Camada social (mentalização recursiva, publicidade, ratificação) | **Proxy operacional mínimo (V4, prova de conceito)** |
| $\mathcal{C}_{hum}(t)$ | Índice humano = $\mathcal{C}(t) + w_5 S(t)$ | **Proxy operacional mínimo (V4, prova de conceito)** |

A versão canônica dos coeficientes é a **V3**: $\alpha,\beta,\gamma,\delta = 0{,}35/0{,}20/0{,}20/0{,}25$ para $\Psi_{\text{eff}}$, e $w_1,w_2,w_3,w_4 = 0{,}45/0{,}20/0{,}17/0{,}18$ para $\mathcal{C}(t)$ — valores usados em toda comparação numérica deste manuscrito. As versões toy e V2 usam pesos ligeiramente diferentes e devem ser lidas como estágios anteriores do mesmo modelo, não como fontes alternativas de números.

Todos os números de simulação citados neste manuscrito — em figuras, tabelas e no texto — são **resultados de simulação sintética de prova de conceito; não constituem validação empírica**. Os regimes (vigília, ansiedade, sono profundo, reflexo) são definidos por parâmetros escolhidos pelo autor, de modo que a separação entre eles nas simulações reflete a coerência interna do modelo, não uma confirmação externa. O confronto com dados empíricos publicados — que já mostra alinhamento forte entre a ordenação vigília/REM > sono profundo > estados subintegrados e a literatura (ver Cap. 11) — é o passo necessário para qualquer alegação de validação.
