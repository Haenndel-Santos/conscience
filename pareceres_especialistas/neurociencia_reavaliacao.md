# Reavaliação técnica — parecer de neurociência da consciência (segunda leitura)

**Manuscrito:** *Consciência como Regime Integrado* (`Versao atual.md`; fontes em `capitulos/`)
**Parecer original:** `pareceres_especialistas/neurociencia.md` (5 recomendações, priorizadas)
**Escopo desta reavaliação:** as respostas às 5 recomendações originais — com foco na recomendação 3 (teste computacional de complexidade multivariada), a única que exigia computação nova sobre dado real. Leitura e verificação apenas; nenhum arquivo do manuscrito foi editado.

---

## 1. Veredito geral atualizado

O programa empírico de EEG deste manuscrito está hoje mais completo e mais honesto do que na minha primeira leitura — não só porque as 5 recomendações foram endereçadas no texto, mas porque o *processo* usado para endereçar a mais exigente delas (recomendação 3) é, ele mesmo, uma demonstração da mesma ética que eu já havia identificado como o maior ponto forte do projeto. Ao tentar implementar o teste que pedi, o autor descobriu um bug real de seleção de canal (o canal de gatilho `Event marker` sendo tratado como um 3º canal EEG), obteve numa primeira correção um resultado preliminar que favorecia a teoria (AUC residual subindo de ~0,55 para ~0,70), **não o publicou**, investigou mais, encontrou que esse resultado favorável era ele mesmo produto de um segundo bug, corrigiu, e só então publicou o número final — que é negativo. Esse é exatamente o tipo de comportamento (escrutinar com mais rigor o resultado que confirma a própria hipótese do que o que a contraria) que a literatura de integridade científica identifica como o mais raro e mais difícil de praticar na prática, não só de professar. O teste em si, uma vez rodado, cumpre tecnicamente tudo que a recomendação 3 pedia — LZc genuinamente multivariada (concatenação binária, não média por canal), bootstrap por sujeito, validação cruzada por participante fora da amostra, correção FDR — e chega a um resultado negativo consistente em todas as quatro comparações testadas. As recomendações 1, 2, 4 e 5 foram incorporadas ao texto de forma literal e tecnicamente correta. Considero as 5 recomendações originais integralmente atendidas; os pontos que restam (seção 4 abaixo) são refinamentos, não lacunas de honestidade.

---

## 2. Recomendação por recomendação

| # | Recomendação original | Status | Comentário |
|---|---|---|---|
| 1 | Cap. 11 — explicitar na prosa a montagem de 2 canais (Fpz-Cz, Pz-Oz) e o teto de 8-16 canais/ROIs para medidas grafo-teóricas | **Atendida integralmente** | Inserida exatamente onde recomendei — na primeira menção da LZc por estágio de sono (`capitulos/12_capitulo_11.md`, §Sono, 1º parágrafo). O texto nomeia as duas derivações, afirma que são "calculadas de forma independente por canal" e cita o patamar de 8-16 canais/ROIs. Achado colateral notável: por causa do bug descrito abaixo, no momento em que escrevi o parecer original essa frase não era literalmente verdadeira (um 3º "canal" espúrio estava contaminando o cálculo) — só ficou 100% correta depois da correção que a própria recomendação 3 provocou. |
| 2 | Cap. 14 — citar Casali et al. (2013) e nomear a distinção perturbacional/observacional frente ao PCI | **Atendida, além do pedido** | Referência 99 (Casali et al. 2013) presente em `capitulos/17_referencias.md` e citada em `capitulos/15_capitulo_14.md`, seção IIT. A distinção não é só nomeada — é amarrada ao próprio episódio da anestesia (ritmo alfa posterior confundindo a complexidade sob propofol, Cap. 11), que é usado como ilustração concreta de por que o desenho perturbacional do PCI existe. Isso é mais do que as "duas a três frases" que eu havia pedido como mínimo. |
| 3 | Testar um índice de LZc genuinamente multivariado (concatenação, não média por canal) com o mesmo pipeline de robustez do controle 1/f, antes de fechar a conclusão sobre "integração diferenciada" | **Atendida com rigor real; resultado negativo** | Ver avaliação técnica detalhada na seção 3. Computação de fato executada (não hipotética), com bootstrap por sujeito, validação cruzada de 5 partições por sujeito fora da amostra, e correção FDR — os três elementos que eu havia pedido explicitamente. Resultado: AUC bruta praticamente idêntica ao comparador (0,9919 vs. 0,9919); residualizada fora da amostra, 0,549 [0,457–0,633] (multivariada) vs. 0,554 [0,455–0,639] (comparador) — nenhuma vantagem, nenhum dos dois sobrevive à FDR. |
| 4 | Adicionar Donoghue et al. (2020) e Colombo et al. (2019) ao Cap. 11 | **Atendida integralmente** | Referências 92 e 91 presentes em `capitulos/17_referencias.md`, citadas exatamente nos pontos certos do texto: Donoghue junto à menção do método FOOOF/specparam, Colombo junto à observação de que o confundidor espectral já era conhecido 5 anos antes de Höhn et al. (2024), no mesmo paradigma farmacológico. |
| 5 | Cap. 2 — adicionar Garfinkel et al. (2015) e Barrett & Simmons (2015), com Barrett & Simmons também no Cap. 10; evitar a associação acurácia-interoceptiva↔ansiedade | **Atendida integralmente, calibração respeitada** | Referências 64 (Garfinkel) e 62 (Barrett & Simmons) presentes; Barrett & Simmons aparece tanto no Cap. 2 quanto no Cap. 10 (`capitulos/11_capitulo_10.md`), fazendo exatamente a ponte para o FEP que recomendei. Busquei "ansiedade" em todo o Cap. 2 e não aparece — a única ocorrência do termo nos capítulos revisados é no Cap. 3, num contexto totalmente diferente (o regime sintético de ansiedade do modelo V3), não ligado a Garfinkel. Craig (2002, ref. 63) foi adicionado como extra, verificado de forma independente. |

---

## 3. Avaliação técnica do teste da recomendação 3 (onde mais peso estatístico está em jogo)

Verifiquei diretamente o código (`scripts_para_rodar/complexidade_multivariada/lzc_multivariado_2canais.py`), os dados brutos (`lzc_multivariado_por_epoca.csv`, `auc_comparativo_multivariado.csv`) e o relatório (`resumo_lzc_multivariado.md`), e cruzei os números contra `embasamento/registro_falsificabilidade.md` (entrada 1.3b) e a prosa final em `capitulos/12_capitulo_11.md`/`Versao atual.md`. Os quatro artefatos são mutuamente consistentes até a 3ª/4ª casa decimal — não encontrei nenhum número que apareça diferente entre o script, o CSV, o registro de falseabilidade e a prosa do livro.

**O que foi bem feito, tecnicamente:**

- **Operacionalização multivariada correta.** `lzc_from_binary(np.concatenate([b0, b1]))` binariza cada canal pela própria mediana e concatena as duas sequências antes de comprimir — não calcula LZc por canal e tira a média. Isso é, de fato, a lógica de Schartner et al. (2015), corretamente citada (ref. 100), e é uma operacionalização diferente (e mais informativa sobre estrutura conjunta) do que a média por canal já usada no resto do projeto.
- **Bootstrap pela unidade certa.** `cluster_bootstrap_auc` reamostra sujeitos inteiros (n=36), não épocas — evita a pseudo-replicação que o próprio Cap. 11 já sinalizava como problema na estimativa ingênua. Reconferi a função linha a linha: o reamostreio é por sujeito, a AUC é recalculada em cada réplica, e IC95%/p-valor vêm dos percentis da distribuição bootstrap. Correto.
- **Validação fora da amostra pela unidade certa.** `residualize_out_of_sample` faz K-fold (5 partições) sobre a lista de *sujeitos*, não de épocas — o ajuste `metric ~ exponent_1f` é treinado só nos sujeitos de treino e aplicado aos sujeitos de teste, nunca vistos pelo ajuste. Isso é exatamente o "protocolo VNext" que o Cap. 11 já nomeava como teste mais limpo em aberto, agora implementado sem vazamento de informação entre treino e teste.
- **FDR calculado corretamente.** Reproduzi manualmente o procedimento de Benjamini-Hochberg sobre os 6 p-valores da tabela (2 brutos ≈0 + 4 residualizados entre 0,296 e 0,375) e confirmo que o valor final q=0,375 para as quatro comparações residualizadas é o que a fórmula padrão realmente produz — não há erro de implementação nem seleção pós-hoc do valor mais favorável.
- **A moldura do estimando certo é mantida.** O relatório segue a mesma disciplina já elogiada no parecer original: reporta a estimativa ingênua por época só para comparabilidade histórica, mas deixa explícito que é a estimativa por sujeito que "decide o resultado" — e é essa, não a mais favorável, que aparece na prosa do Cap. 11.

**O episódio do bug, e por que ele pesa a favor do projeto, não contra:** o `CHECKLIST_pendencias.md` (entradas W12–W15) documenta uma sequência de dois bugs e duas correções que, na minha leitura, é o ponto mais forte de evidência processual deste parecer inteiro. Resumindo o que reconstruí a partir do changelog e dos diffs de `git`:

1. Um bug genuíno existia em 3 dos 6 scripts de recompute do sono: `infer_types=True` do MNE rotulava o canal `Event marker` (gatilho, não sinal cerebral) como tipo `"eeg"`, contaminando a média de LZc/PE/expoente-1/f em 100% das ~39 mil épocas já processadas.
2. Corrigido o bug, uma primeira rodada sugeriu que a discriminação residualizada por 1/f subia de ≈0,55 para ≈0,70 — um resultado que, se real, teria sido *favorável* à teoria (mais suporte a "integração diferenciada" sobrevivendo ao confundidor espectral). O autor **não aplicou esse número ao manuscrito** e reportou o achado antes de prosseguir.
3. Investigação adicional revelou que esse resultado de ≈0,70 era, ele mesmo, artefato de um segundo bug: a residualização fora da amostra do script novo estava sendo ajustada com as 5 fases do sono, não só W/N3 (a convenção já estabelecida no resto do projeto). Corrigido, o número caiu para ≈0,53 — consistente com o ≈0,55 já publicado.
4. A rodada final, com as duas correções aplicadas, é a que está reportada no Cap. 11 hoje: resultado negativo, robusto, e mais rigoroso do que qualquer teste anterior do projeto (é o único que usa validação cruzada por sujeito fora da amostra).

Um projeto disposto a aceitar sem escrutínio adicional um bug cuja correção "por acaso" favorece a própria tese seria um projeto com um problema sério de viés motivado. Este fez o oposto: tratou o resultado favorável com *mais* suspeita, não menos, até esgotar a explicação alternativa (um segundo erro de código) antes de aceitar o número. Isso é precisamente o padrão de comportamento que eu estava, no parecer original, elogiando como incomum no gênero — agora demonstrado sob pressão real, não apenas declarado como princípio.

---

## 4. Problemas novos identificados nesta reavaliação

Nenhum deles muda a leitura substantiva do resultado (negativo) nem constitui um problema de honestidade — são refinamentos técnicos que uma revisão de segunda camada deveria registrar:

1. **Só uma forma de "multivariado" foi testada.** A concatenação binária (bloco do canal 0 seguido do bloco do canal 1) é uma operacionalização legítima e fielmente atribuída a Schartner et al. (2015), mas é mecanicamente diferente de escaneamento intercalado amostra-a-amostra entre canais (mais próximo em espírito da construção da "palavra" espaço-temporal do PCI de Casali et al. 2013) — a concatenação em bloco captura menos diretamente sincronia entre os 2 canais no mesmo instante. Dada a convergência de *todas* as outras operacionalizações já tentadas no projeto (sincronia bruta, informação mútua, índice combinado, e agora a LZc concatenada) para o mesmo resultado nulo pós-1/f, é improvável que a versão intercalada mudasse a conclusão — mas não é logicamente garantido, e o script/docstring já é honesto ao dizer "no espírito de... embora sem a perturbação por TMS que define o PCI propriamente dito".
2. **Escopo da correção FDR não é global.** A correção de Benjamini-Hochberg é aplicada por bloco de análise (sono, dose de propofol, propofol por responsividade, cada um separadamente), não como uma única família cobrindo todo o programa empírico de EEG do livro. É uma prática defensável (corrigir dentro de uma família coerente de comparações, não entre datasets/perguntas diferentes), e reconferi à mão que isso não muda nenhuma conclusão do sono (os q-valores residualizados chegam a 0,375 tanto se agrupados com as comparações brutas quanto se isolados) — mas o manuscrito não justifica essa escolha de escopo em nenhum lugar que eu tenha encontrado.
3. **Largura do IC e poder estatístico não são discutidos explicitamente.** Os IC95% bootstrap por sujeito (~0,18 de largura, ex. [0,457–0,634]) são consistentes com n=36 sujeitos e comunicam corretamente "indistinguível do acaso" — a redação do Cap. 11 já usa essa formulação cautelosa, não "prova que não há integração". Ainda assim, uma frase explícita sobre o efeito mínimo detectável dado n=36 fortaleceria a seção para um leitor tecnicamente exigente; isso já valia no parecer original e continua valendo agora.
4. **O episódio do bug não aparece na prosa do Cap. 11 lida pelo leitor final.** Ele está documentado com extremo detalhe em `CHECKLIST_pendencias.md` e em `embasamento/registro_falsificabilidade.md` (nota ao final do documento), mas o texto que o leitor do livro efetivamente vê não menciona que um bug de seleção de canal foi encontrado e corrigido, nem que uma correção preliminar chegou a sugerir um resultado favorável antes de ser desmontada. Isso é uma escolha editorial defensável — seções de método de artigos publicados também não costumam narrar o processo de depuração —, mas dado quanto peso retórico este manuscrito já coloca em "mostrar o próprio trabalho" como virtude, uma nota de rodapé de uma frase seria consistente com esse compromisso, não uma correção de um erro.
5. **Modelo de ajuste 1/f usa modo "fixed", não "knee".** `aperiodic_mode="fixed"` no FOOOF/specparam não modela uma possível curvatura ("knee") no espectro, que é razoavelmente comum em EEG de sono de ondas lentas. Essa é uma escolha herdada do resto do projeto (não introduzida por este teste), então não é uma inconsistência nova — só registro que não foi testada a sensibilidade do resultado a essa escolha de modelagem.

---

## 5. O que ainda falta

- O teste multivariado intercalado (item 4.1) — baixa prioridade, resultado improvável de mudar.
- Qualquer medida grafo-teórica real de integração/segregação (exigiria um dataset com 8-16+ canais; Sleep-EDF Cassette não permite isso em princípio — já corretamente sinalizado como limite estrutural, não uma pendência de execução).
- O teste diferencial de REM que o próprio Cap. 11 já nomeia como "programa, não resultado" (separar complexidade interna de acoplamento ambiental $ME(t)$) — continua não operacionalizado.
- Uma frase sobre efeito mínimo detectável dado n=36 (item 4.3) — custo baixo, ainda não feito.
- Opcionalmente, uma nota de rodapé sobre o episódio do bug (item 4.4) — custo baixo, puramente uma questão de completude editorial, não de correção.
- A maioria das previsões distintivas do Cap. 14 frente às teorias rivais (dissociação sob cetamina, recorrência local em ensaios mascarados, assinatura da junção temporoparietal) seguem sem dado próprio do projeto — o próprio capítulo já rotula isso como "apostas declaradas, não resultados", o que é a leitura correta e não uma omissão.

---

## Anexo — verificação cruzada dos números centrais

| Métrica | Bruta (AUC) | Residualizada 1/f, dentro da amostra | Residualizada 1/f, fora da amostra (5-fold por sujeito) |
|---|---|---|---|
| `lzc_mean_channels` (comparador) | 0,9919 | 0,5504 [0,459–0,634] | 0,554 [0,455–0,639] |
| `lzc_multivariado` (novo, concatenação) | 0,9919 | 0,5454 [0,454–0,627] | 0,549 [0,457–0,633] |

Fontes cruzadas e conferidas mutuamente consistentes: `scripts_para_rodar/complexidade_multivariada/resumo_lzc_multivariado.md`, `.../auc_comparativo_multivariado.csv`, `embasamento/registro_falsificabilidade.md` (entrada 1.3b), `capitulos/12_capitulo_11.md` (§Sono, último parágrafo), `Versao atual.md` (linha correspondente). Nenhum dos quatro sobrevive à correção FDR (q=0,375 em todos).
