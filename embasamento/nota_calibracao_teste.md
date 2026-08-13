# Nota de correção — 2026-08-13

**Leia isto antes de interpretar qualquer resultado de "categoria 2".** Quatro coisas
mudaram entre 12/08 à noite e 13/08 de madrugada. Duas invalidam texto que já está na
árvore de trabalho, e uma **reverte o achado negativo central do Cap. 11**.

---

## 1. A rodada de anestesia já foi feita

`anestesia_controle_1f.py` rodou completo em 12/08, 23:02 → 13/08, 00:00 (58 min).
**80 de 80 arquivos `.set`, 3.082 épocas, 100% com 1/f válido, zero falhas.**

- Dataset em `D:\datasets\Sedation-RestingState` — foi retirado do scratchpad temporário
  de sessão onde estava (3,74 GB que uma limpeza de disco teria apagado), copiado e
  verificado por contagem, bytes e SHA256.
- Correção no script antes da rodada: `residualize_out_of_sample` estourava com grupos de
  menos de 2 sujeitos, porque a guarda do chamador conta **épocas** (`>=10`) enquanto o
  `KFold` particiona **sujeitos**. Inerte na amostra cheia; quebra qualquer rodada com
  `--max-subjects` pequeno.
- Validação: os números **brutos** reproduzem exatamente o Bloco O de 10/08 —
  responsive LZc 0,791 / PE 0,642, drowsy LZc 0,411 / PE 0,283.

### O achado

O controle por 1/f **não esvazia** o efeito da anestesia — amplifica. Com o teste
calibrado (AUC por sujeito), fora da amostra:

| grupo | n | LZc bruta | LZc resid. 1/f | p | q |
|---|---|---|---|---|---|
| todos | 20 | 0,702 | **0,885** [0,796–0,951] | 0,00019 | 0,0011 |
| responsive | 13 | 0,897 | **0,932** [0,872–0,979] | 0,00024 | 0,0011 |
| drowsy | 7 | 0,340 | 0,810 [0,595–0,952] | 0,031 | 0,070 |

A PE não acompanha em nenhum grupo (todos p≥0,22 após residualização).

**Três ressalvas que precisam entrar em qualquer leitura:**

1. **1/f aqui é provavelmente mediador, não confundidor.** O propofol causa tanto a
   mudança espectral quanto a de complexidade, e Colombo et al. (2019, ref. 91) mostra o
   expoente sozinho rastreando consciência neste mesmo paradigma. Residualizar um mediador
   remove o caminho causal da droga; o resíduo não é "o efeito purificado", é "o que a LZc
   faz ortogonalmente à assinatura espectral do propofol". **Não** é evidência de
   integração diferenciada.
2. **LZc e PE divergem.** O `RELATORIO_v2` estabelece a concordância entre métricas
   independentes como o indicador informal de robustez do projeto. Aqui elas divergem.
3. **A predição 1.4 perde seu mecanismo.** Ela está ✅ CONFIRMADA com base em "responsive
   sobe, drowsy desce". Sob o controle de 1/f os dois grupos vão na mesma direção
   paradoxal — o grupo drowsy inverte de sinal (0,340 → 0,812). Os números brutos
   replicam; o mecanismo proposto não sobrevive. Com n=7 e q=0,070, essa inversão é
   sugestiva, não estabelecida.

---

## 2. A análise de poder de 12/08 era inválida — e o texto dela está no manuscrito

O `poder_estatistico_sono.py` original **não reamostrava nada**: todas as `n_sim` réplicas
de um mesmo dz-alvo eram byte-idênticas. `sim_diffs` não dependia da variável do laço e as
épocas sintéticas eram recentralizações determinísticas, apesar de a docstring prometer
reamostragem com ruído. A única aleatoriedade entrava no bootstrap interno, então o
"poder" medido era ruído do teste, não variabilidade amostral entre estudos.

**O MDE de dz≈0,2 que saiu dali é inválido.** Saídas preservadas com sufixo
`_INVALIDO_replicas_identicas`. O Nível 1 (fórmula fechada) nunca foi afetado.

Números válidos, da rodada corrigida (n_sim=300, n_boot=1000): poder de 28,3% em dz=0,
52,7% em dz=0,1, 79,3% em dz=0,3. Fórmula fechada: 80% de poder exige dz ≥ 0,4669; efeito
observado dz = −0,0994.

**Ressalva importante:** essa curva de poder foi calculada com o teste antigo, que a seção
3 mostra ser inválido no desenho do sono. Ela descreve o poder de um teste que não deve
mais ser usado.

> **Resolvido (v3).** A curva foi refeita com o teste calibrado (n_sim=2000): 80% de poder
> exige dz entre 0,4 e 0,5, convergindo com a fórmula fechada para teste pareado
> (dz≥0,4669); no efeito observado (dz=−0,099) o poder é de **16,7%**, e em dz≥0,5 sobe
> para 91%. Os números da v2 acima (28,3% em dz=0, 52,7% em dz=0,1, 79,3% em dz=0,3)
> descrevem o teste descalibrado e **não devem ser citados**. A leitura que vale é a da
> v3, já incorporada a `registro_falsificabilidade.md` (entrada 1.2): o nulo é decisivo
> contra um mecanismo de efeito grande e não é informativo contra um efeito pequeno da
> magnitude do observado.

### ⚠️ Texto a reescrever

Editados em 12/08 às 20:57 com o MDE inválido, **não devem ser commitados como estão**:
`capitulos/12_capitulo_11.md`, `embasamento/registro_falsificabilidade.md` (predição 1.2),
`Versao atual.md`.

---

## 3. O teste antigo é anticonservador em alguns desenhos — mas nenhuma conclusão muda

Varredura dos 15 desenhos usados no projeto
(`scripts_para_rodar/teste_calibrado/varredura_desenhos.md`). O nulo é imposto por
**permutação de rótulos de estado dentro de cada sujeito** — preserva a distribuição
marginal de cada um e força AUC=0,5 por construção. α nominal 0,05.

| desenho | razão | AUC sob nulo | tipo I antigo | veredito | p antigo | AUC/sujeito | p NOVO |
|---|---|---|---|---|---|---|---|
| REM vs W · emg_rms | 1,45 | 0,539 | **46,0%** | INVÁLIDO | 0,000 | 0,662 | <0,0001 |
| REM vs N1 · emg_rms | 1,89 | 0,511 | 0,0% | válido | 0,582 | 0,528 | 0,529 |
| REM vs N2 · emg_rms | 2,72 | 0,512 | 10,0% | suspeito | 0,274 | 0,505 | 0,994 |
| REM vs N3 · emg_rms | 1,55 | 0,506 | 0,0% | válido | 0,164 | 0,503 | 0,581 |
| REM vs W · coerência | 1,45 | 0,502 | 7,0% | válido | 0,000 | 0,545 | <0,0001 |
| REM vs N1 · coerência | 1,89 | 0,506 | 2,0% | válido | 0,000 | 0,538 | 0,0001 |
| REM vs N2 · coerência | 2,72 | 0,499 | 5,5% | válido | 0,028 | 0,518 | 0,0046 |
| REM vs N3 · coerência | 1,55 | 0,504 | 5,5% | válido | 0,000 | 0,512 | 0,032 |
| REM vs W · índice desac. | 1,45 | 0,495 | 0,0% | válido | 0,000 | 0,260 | <0,0001 |
| REM vs N1 · índice desac. | 1,89 | 0,508 | 0,5% | válido | 0,026 | 0,412 | 0,0044 |
| REM vs N2 · índice desac. | 2,72 | 0,509 | **18,0%** | INVÁLIDO | 0,000 | 0,660 | <0,0001 |
| REM vs N3 · índice desac. | 1,55 | 0,545 | **100,0%** | INVÁLIDO | 0,000 | 0,886 | <0,0001 |
| Sono W-N3 · LZc resid. | 2,25 | 0,551 | 10,5% | suspeito | 0,296 | 0,495 | 0,981 |
| Sono W-N3 · LZc multiv. | 2,25 | 0,547 | 6,0% | válido | 0,332 | 0,494 | 0,920 |
| Anestesia · LZc resid. | 1,01 | 0,499 | 3,0% | válido | 0,000 | 0,891 | 0,0002 |

> **Nota de leitura (acrescentada 2026-08-13).** A última linha traz **0,891**, que é o valor
> *dentro da amostra* (`resid_1f_in_sample`); o valor *fora da amostra* — o desenho mais
> rigoroso, e o que a seção 1 desta nota reporta — é **0,885** [0,796–0,951]. Os dois
> arredondam para o mesmo p (0,0002) e não mudam veredito algum, mas ao citar a anestesia
> use o de fora da amostra, para manter a mesma convenção do resto do projeto. Ambos em
> `scripts_para_rodar/teste_calibrado/resultados_por_sujeito.csv`.

**A conclusão que importa: nenhuma linha muda de veredito substantivo.** O teste antigo é
inválido em 3 dos 15 desenhos e suspeito em 2, mas nos três inválidos os efeitos reais são
grandes o bastante para sobreviverem ao teste calibrado — o `índice_desacoplamento`
REM-vs-N3, o caso mais extremo (100% de erro tipo I), tem AUC por sujeito de **0,886 com
p<0,0001**, mais forte que o número agrupado original. O teste novo é bem calibrado em
todos os desenhos (erro tipo I entre 2,0% e 8,5%).

**A razão de épocas NÃO é o preditor** — hipótese que esta nota afirmou numa versão
anterior e que a varredura refutou. Compare `REM vs W · emg_rms` (razão 1,45, inválido) com
`REM vs N1 · emg_rms` (razão 1,89, válido): a razão maior é a válida. O que produz o viés é
a **covariância entre o nível geral de cada sujeito na métrica e o desequilíbrio individual
dele entre as duas condições**. Se os sujeitos com EMG alto são justamente os que
contribuem proporcionalmente mais épocas de vigília, o pool inclina; se o desequilíbrio é
parelho entre sujeitos, não inclina, por maior que seja. A coluna que diagnostica é
`AUC sob nulo`, e ela só se obtém calibrando.

Recomendação: adotar o teste calibrado daqui em diante e reportá-lo. Nenhum resultado já
registrado precisa de retratação.

> **Duas calibrações anteriores desta nota estavam erradas; nenhum dos números delas deve
> ser citado.**
> (a) A primeira impunha o nulo recentrando as *médias* dos dois estados, e reportava 61%
> (sono) e 14% (anestesia). AUC não é função da média, e sim de dominância estocástica: com
> distribuições assimétricas, médias iguais dão AUC ≠ 0,5 — o procedimento injetava efeito
> real e o chamava de nulo. Arquivos `_INVALIDO_nulo_por_media`.
> (b) A segunda usava permutação (correto) mas residualizava por 1/f sobre **os cinco
> estágios** antes de filtrar o par, contra a convenção do projeto. Reportava 100% para o
> sono; o valor correto é 10,5%. Arquivos `_INVALIDO_residualizou_todos_estagios`.
> As duas falhas são da mesma família: **conferir sempre sobre que amostra a residualização
> foi ajustada, e que nulo exatamente está sendo imposto.**

---

## 4. Com o teste calibrado, a predição 1.2 continua falhando — e mais claramente

O teste novo — AUC calculada **dentro** de cada sujeito, depois Wilcoxon dessas AUCs
contra 0,5 — não agrupa épocas entre sujeitos, então o desequilíbrio deixa de importar
por construção.

Sono, W vs N3, n=36 (`scripts_para_rodar/teste_calibrado/resultados_por_sujeito.csv`):

| métrica | bruta | resid. 1/f (fora da amostra) | p | q |
|---|---|---|---|---|
| LZc | 0,991 | **0,500** [0,425–0,577] | 0,96 | 0,98 |
| LZc multivariada | 0,991 | 0,494 [0,422–0,567] | 0,93 | 0,99 |
| PE | 0,991 | 0,547 [0,456–0,635] | 0,30 | 0,51 |
| sincronia bruta | 0,140 | 0,450 [0,363–0,537] | 0,28 | 0,51 |
| integração (MI) | 0,180 | 0,493 [0,405–0,583] | 0,92 | 0,98 |
| índice integração×diferenciação | 0,201 | 0,484 [0,395–0,572] | 0,81 | 0,98 |

**O teste calibrado torna o nulo mais limpo, não mais fraco.** O teste antigo dava AUC
agrupada de 0,554 com p=0,28; o calibrado dá 0,500 com p=0,96 — praticamente o acaso
exato. As predições 1.2, 1.3 e 1.3b permanecem ❌ FALHOU, agora por um teste válido.

A discriminação **bruta** (0,991) segue intacta e esmagadora. O que não sobrevive continua
sendo a leitura mecanística, exatamente como o Cap. 11 já diz. A diferença é que agora
essa conclusão se apoia num teste calibrado em vez de num que rejeita 100% das vezes sob
o nulo.

> **⚠️ Armadilha metodológica, documentada porque custou uma conclusão errada.**
> Uma versão anterior deste script residualizava por 1/f sobre **os cinco estágios** e só
> depois filtrava W e N3. Isso muda o slope da regressão e produziu uma AUC por sujeito
> espúria de 0,648 (p<0,001), que parecia reverter a predição 1.2. A convenção do projeto
> — em `integracao_diferenciada_1f.py` e em `anestesia_controle_1f.py` — é **filtrar o par
> de estados primeiro e só então residualizar**. O sinal de alerta que expôs o erro: a AUC
> por sujeito dizia 0,648 (W acima de N3) enquanto o dz observado dizia −0,099 (W abaixo
> de N3). Refeita pela convenção correta, a AUC por sujeito é 0,495 e correlaciona +0,986
> com a diferença de médias — sem contradição. Qualquer reanálise futura precisa checar
> sobre que amostra a residualização foi ajustada.

---

## Arquivos

| Caminho | O quê |
|---|---|
| `scripts_para_rodar/teste_calibrado/resultados_por_sujeito.csv` | Todas as comparações, teste novo, com o número antigo ao lado |
| `scripts_para_rodar/teste_calibrado/calibracao_permutacao.md` | Calibração dos dois testes |
| `scripts_para_rodar/anestesia_1f/auc_comparativo_1f.csv` | Anestesia, teste antigo (válido naquele desenho) |
| `scripts_para_rodar/poder_estatistico/poder_por_efeito.csv` | Poder, versão corrigida |
| `*_INVALIDO_replicas_identicas.*` | Poder, versão inválida |
| `*_INVALIDO_nulo_por_media.*` | Calibração inválida (nulo pela média) |
