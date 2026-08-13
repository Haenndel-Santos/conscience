# Conscience

Interdisciplinary theoretical program treating consciousness as an **integrated
dynamic regime** — across neural, bodily, mnemonic, evaluative and environmental
signals — bodily situated, causally stratified, and extending to an
intersubjective dimension in the human case.

The manuscript and all documentation are written in **Portuguese**.

## Status

Advanced stage of **conceptual clarification**; early stage of **mechanistic
validation**. The V05 revision closed on 2026-08-11.

The honest summary of where this stands: the established contribution today is the
conceptual architecture and the testing apparatus — not a demonstrated empirical
signature of its own. Read `embasamento/registro_falsificabilidade.md` before
citing any result as confirmed.

### What is demonstrated

- **Sleep-stage discrimination is robust.** Lempel-Ziv complexity and permutation
  entropy separate wakefulness from N3 with AUC ≈ 0.99 (36 subjects, 39,086 epochs,
  two independent metrics agreeing perfectly on stage ordering).
- **The V3 model is implementable** and separates regimes analogous to waking,
  anxiety, deep sleep and reflex.

### What is *not* demonstrated

- **That those metrics measure differentiated integration.** After controlling for
  the aperiodic 1/f spectral exponent, discrimination collapses to AUC ≈ 0.55–0.58,
  with confidence intervals crossing chance and nothing surviving FDR correction.
  **How much that null tells us is itself limited:** at n=36 the design reaches 80%
  power only for Cohen's *dz* ≥ 0.47, while the observed effect is *dz* ≈ −0.10. The
  null is decisive against a large effect, not against a small real one. It also does
  not separate "complexity carries no signal beyond 1/f" from "1/f and complexity are
  two readings of one physiological change."
- **The anesthesia result.** The original dose-based prediction failed. Stratifying
  by behavioural responsiveness (13 responsive / 7 drowsy) explains the pattern
  plausibly but is post-hoc, same-dataset, and small — **exploratory, not confirmed**.
- **The intersubjective layer.** V5 models behavioural coordination in small
  synthetic groups. Its ablation shows the code realises the intended mechanism, but
  its parameters were calibrated to produce that threshold — internal verification,
  not independent corroboration of common knowledge or shared consciousness.
- **The animal, AI, trauma and evolution extensions** are bibliographically grounded
  but largely untested by this project.

## Structure

| Path | Contents |
|---|---|
| `capitulos/` | Manuscript source, chapter by chapter — the source of truth |
| `Versao atual.md` | Generated full draft (assembled from `capitulos/`) |
| `embasamento/` | Falsifiability registry, evidence maps, positioning against rival theories |
| `dados atuais/` | Simulation models V2–V5, output CSVs and figures |
| `recompute_empirico_sleepedf/`, `recompute_empirico_v2/` | Empirical EEG reanalyses and their reports |
| `scripts_para_rodar/` | Analysis scripts run locally by the author (require datasets not versioned here) |
| `pareceres_especialistas/` | Adversarial reviews — **AI-generated, not external peer review** |
| `CHECKLIST_pendencias.md` | Live working record of open and closed items |
| `docs/historico/` | Superseded agent briefs, kept for provenance |
| `.codex/` | Agent guidance and local skills |

`MAPA_TRABALHO_Conscience_V05.md` and `PLANO_ESTRATEGICO_cientifico.md` are
**concluded and preserved as historical records**, not active plans.

## Data

Datasets are **not versioned in this repository** and must be obtained separately:

- **Sleep-EDF** — fetched on demand by `mne.datasets.sleep_physionet`.
- **Propofol sedation** (Chennu et al. 2016, PLOS Comput Biol, DOI
  10.1371/journal.pcbi.1004669) — 3.44 GB, manual download from the Apollo/Cambridge
  repository, CC BY 2.0 UK.

Every analysis script takes the dataset location via a required `--data-dir` argument.

## Python environment

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
```

`requirements.txt` pins exact versions — the ones that produced the recorded results.
Version drift in MNE, specparam or scikit-learn can shift absolute values without
raising an error.

## AI assistance

This project was developed with substantial AI assistance: drafting, code, analysis
and the adversarial reviews in `pareceres_especialistas/`. All empirical analyses were
executed locally by the author against real data. Design decisions, scientific
judgements and final responsibility are the author's.

## License

Dual, by material type — see [`LICENSE`](LICENSE):

- **Code** (`.py`) — MIT.
- **Manuscript, documentation, figures and result tables** — CC BY 4.0.

The EEG datasets are **not** covered by either: they are not redistributed here and
carry their own terms. The propofol dataset is CC BY 2.0 UK and requires attribution
to Chennu et al. (2016).
