# First technical assessment

> **Enquiry:** Our existing NIR pilot follows API concentration in one powder formulation at the tablet press feed frame. We are introducing a different API and excipient blend and would like to reuse the calibration. A colleague suggests adding Raman so that the old calibration will remain valid. What should our first technical assessment and experiment be?
>
> **Answers added:** Path B - Where it is used: In production; Path C - Variables per sensor: One

**Quality checks:** 15/16 · **Sourced claims verified:** 6/8 · **Unsupported numbers:** 0

## 01. Decision Status
**Provisional assessment** · **Confidence:** low (computed, not self-reported)

The existing NIR calibration cannot be directly reused for the new blend; a re‑validation of NIR and a feasibility test of a fused NIR‑Raman chemometric model are required.

**The customer's own claims, tested first**
- **unverifiable**: "Adding Raman will keep the old calibration valid". Adding a second method (for example Raman) does not make an existing single-method calibration valid. Data from different methods are not equivalent; a fused model needs synchronised data, fusion algorithms and its own calibration and validation. [S01 p.8] [S01 p.9]
- **unverifiable**: "Reuse existing NIR calibration for new API/excipient blend". NIR and other spectra need chemometric calibration models built and validated on the actual matrix. A new API or excipient blend changes the spectra, so an existing calibration must be re-validated and normally rebuilt; reuse is a hypothesis to test, not an assumption. [S01 p.10] [S01 p.5]

To raise confidence, answer: Is the sample clear, turbid or opaque, and does this change during the process? / What concentration range must be covered, and what is the smallest change that matters? / Which independent reference method (and its uncertainty) can provide calibration values?

## 02. Requirements stated
- Assess Raman’s impact on NIR calibration for new powder blend
- Test combined spectra and chemometric model transfer
- Target variable: API concentration in powder at tablet press feed frame
- Phase: pilot (powder)
- Existing asset: NIR pilot

## 03. Key unknowns
- Exact matrix composition of the new API/excipient blend
- Optical scattering and absorption behavior of the new blend in the NIR and Raman regions
- Concentration range of the API in the new blend

**Assumptions made**
- The new API/excipient blend remains a free‑flowing powder suitable for diffuse‑reflection NIR probing.
- A Raman probe with 785 nm excitation can be installed without major mechanical redesign.

## 04. Clarification questions
1. **What is the expected API concentration range in the new blend?** _(high impact)_. Why: Defines the calibration window and influences the number of calibration samples needed.
2. **Can you provide representative powder samples covering the full range of excipient variations you anticipate?** _(high impact)_. Why: Matrix variability drives the need for a robust chemometric model and affects transferability of the existing NIR calibration.
3. **What Raman excitation wavelength and probe geometry are available in your plant?** _(medium impact)_. Why: Raman signal strength and fluorescence background depend on excitation wavelength; the probe must be compatible with the feed‑frame environment.
4. **Do you have an independent reference assay (e.g., HPLC) for API concentration on the same samples?** _(medium impact)_. Why: Reference data are required for model validation and to quantify any improvement from adding Raman.
5. **Is the existing NIR probe fixed in the feed frame, and can a Raman probe be co‑located on the same shaft?** _(low impact)_. Why: Physical integration determines whether low‑level data fusion (synchronized spectra) is feasible.

## 05. Recommendation

### NIR (diffuse reflection) – re‑validation (primary)
- NIR is the proven method for powder blends in the tablet press feed frame and already deployed in the pilot. [S01 p.5] _(sourced)_
- Re‑validate the existing NIR calibration on the new blend using a representative calibration set and independent reference assays. _(proposal)_
- _Applies if:_ Only if a sufficient set of new‑blend samples covering the client‑agreed concentration range is available.

### Raman (785 nm contact probe) – feasibility test (conditional)
- Raman provides complementary chemical information and is supported for powder blends in the feed frame. [S01 p.5] _(sourced)_
- Test Raman alone to assess signal quality, fluorescence background, and linearity for the new API. _(proposal)_
- _Applies if:_ Requires a Raman probe compatible with the existing shaft and a fluorescence assessment.

### Fused NIR‑Raman (low‑level data fusion) – experimental comparison (comparison)
- Published work shows fused NIR‑Raman models can improve accuracy and robustness for API potency in the feed frame, but this is not a guarantee for a new formulation. [S01 p.15] _(sourced)_
- Build and compare three models (NIR only, Raman only, fused) on the same calibration set to quantify any benefit. _(proposal)_
- _Applies if:_ Requires synchronized acquisition of NIR and Raman spectra on each sample.

**Method screening (deterministic, from sourced rules)**

| Method | Score | Verdict |
|---|---|---|
| NIR spectroscopy | 3 | lead |
| Raman spectroscopy | 2 | candidate |
| UV/Vis spectroscopy | 0 | weak |
| Fluorescence spectroscopy | 0 | weak |
| MIR spectroscopy (ATR) | -1 | weak |

## 06. Measurement concept
- Collect synchronized NIR diffuse‑reflection spectra and Raman spectra on representative powder samples, then build chemometric models (PLS) for API concentration using NIR alone, Raman alone, and fused NIR‑Raman data. _(proposal)_
- Validate each model against independent reference assays to quantify accuracy, robustness, and any benefit of the fused approach. _(proposal)_

## 07. Spectral range
- NIR diffuse‑reflection: client‑agreed range (broad overlapping bands). [S01 p.5] _(sourced)_
- Raman: Raman shift range typically client‑agreed; excitation wavelength 785 nm (as used in pharmaceutical feed‑frame probes). [S01 p.15] _(sourced)_

## 08. Risks and uncertainty
- Fluorescence background may mask Raman signals in organic powders. [S01 p.5] _(sourced)_
- Matrix change may render the existing NIR calibration inaccurate. [S01 p.5] _(sourced ⚠ unverified)_
- Adding Raman does not automatically preserve the validity of the original NIR model. [S01 p.5] _(sourced ⚠ unverified)_

**Confidence: low**
- Information: low (2/10 decision-relevant facts known; target defined: yes)
- Evidence: high (Direct application in AFS sources: R_PHARMA_BLEND)
- Scope fit: high (Requested use matches the scope of the cited evidence)
- Client premises: medium (0 contradicted, 2 unverifiable, 0 supported)
- Verification: medium (6/8 sourced claims verified; 0 unsupported numbers)
- Model agreement: high (3/3 drafts share the lead method(s) NIR; 3/3 share the status 'provisional_assessment' (2 model families))

## 09. Decision basis
- Client‑agreed accuracy and robustness criteria on independent reference data
- Demonstrated improvement (or lack thereof) of fused model over NIR‑only model

## 10. Sources
- **S01 p.5**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "NIR spectroscopy, with its relatively large penetration depth (up to several millimetres) even into dense solid samples due to low absorption and strong scattering, allows the use of ordinary glass for optics"
  - "the spectra of vibrational transitions in Raman and mid-IR spectroscopy carry complementary qualitative and quantitative information about the sample's composition."
  - "However, most chemicals do not exhibit this property."
  - "NIR and other spectra need chemometric calibration models built and validated on the actual matrix. A new API or excipient blend changes the spectra, so an existing calibration must be re‑validated and normally rebuilt" ⚠ unverified
- **S01 p.8**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "It is crucial that the spectral information obtained by different methods—Mid-IR, NIR, Raman, and fluorescence spectra—is collected from the same small, even pinpoint, area of the sample."
- **S01 p.9**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "The development of OMS begins with in-depth studies of the analyzed object using standard laboratory spectrometers."
- **S01 p.10**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "These immersion probes operate on the ATR principle but allow analysis at a significant distance from the spectrometer, without the need for sampling."
- **S01 p.15**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "By combining Raman and NIR, these models can predict API potency or coating thickness with higher accuracy and robustness than single‑method models."
  - "Raman spectrometer and Raman fiber probe for contact measurements with 785 nm excitation wavelength"

**Verifier warnings**
- risks[1]: unverified S01 p.5: quote not on page (49)
- risks[2]: unverified S01 p.5: quote not on page (49)

## 11. First feasibility experiment
**Samples**
- Representative powder batches covering the full API concentration range and expected excipient variations
**Reference measurements**
- Independent HPLC assay for API concentration on each calibration and validation sample
**Comparison**
- Model performance (RMSEP, bias) for NIR‑only, Raman‑only, and fused NIR‑Raman models
**Steps**
1. Prepare a calibration set (≈30–50 samples) spanning the API concentration range and matrix variability.
2. Acquire synchronized NIR diffuse‑reflection spectra and Raman spectra (785 nm) for each sample using the existing NIR probe and a compatible Raman probe.
3. Perform fluorescence/background assessment on Raman spectra; adjust acquisition parameters if needed.
4. Build three chemometric PLS models (NIR, Raman, fused) using standard preprocessing (scatter correction, baseline removal).
5. Validate each model against the independent HPLC reference set; compute RMSEP, bias, and robustness metrics.
6. Review results with the client; decide whether to adopt the existing NIR model, switch to a new NIR model, or implement a fused NIR‑Raman solution.

**Next step with AFS**
- Conduct a multi‑method lab trial (NIR + Raman) to generate calibration data and evaluate fused‑model performance before any production deployment.
- Likely path: A - Path A aligns with the goal of real‑time concentration monitoring for process automation; the lab trial provides the evidence needed to select the optimal model and hardware configuration.
- Path A (chosen by the expert): **fits**. Path A turns spectral data into real-time concentration values for process automation; a central full-spectrum analyzer gives the higher accuracy. [S02 p.20, S02 p.18]
- Path B (chosen by the expert): **conflicts**. Path B is a lab system for R&D; measuring in production is Path A (central analyzer) or Path C (sensors). [S02 p.20]
- Path C (chosen by the expert): **open**. No finding speaks for or against this path yet; the lab trial decides. [S02 p.20]

**If you proceed anyway with Path B** (Path B (customised multi-spectral system for R&D) is a poor fit here: Path B is a lab system for R&D; measuring in production is Path A (central analyzer) or Path C (sensors).)
1. Specify the lab kit from the methods short-listed in this assessment: spectrometers, fiber probes, software.
2. Run the method comparison on the customer's own samples in their lab.
3. Use the results as the basis for a later process solution (Path A or C).
_Sources: S02 p.20, S01 p.4_

**Proposed setup** (ranked by recommendation; validate in a lab trial)

| System | Path A: Chemometric model for process automation | Path B: Multi-spectral system for your R&D lab | Path C: Low-cost spectral sensors |
|---|---|---|---|
| 1. NIR (diffuse reflection) – re‑validation (primary) | Models: API concentration calibration → Process predictions | Lab system: NIR measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: NIR sensor, Process probe(s), Acquisition + control interface → Process monitoring |
| 2. Fused NIR‑Raman (low‑level data fusion) – experimental comparison (comparison) | Models: API concentration calibration → Process predictions | Lab system: NIR measurement channel, RAMAN measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: NIR sensor, RAMAN sensor, Process probe(s), Acquisition + control interface → Process monitoring |
| 3. Raman (785 nm contact probe) – feasibility test (conditional) | Models: API concentration calibration → Process predictions | Lab system: RAMAN measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: RAMAN sensor, Process probe(s), Acquisition + control interface → Process monitoring |

## Council
Winner: draft A; agreement 100% (3/3 drafts share the lead method(s) NIR; 3/3 share the status 'provisional_assessment')
- Draft A (openai/gpt-oss-120b): judge score 5.0, gate failures: G1 Sourced claims verified on the cited page, G2 No unsupported numbers
- Draft B (qwen/qwen3.8-27b): judge score 5.0, gate failures: G1 Sourced claims verified on the cited page, G2 No unsupported numbers
- Draft C (openai/gpt-oss-20b): judge score 4.0, gate failures: G2 No unsupported numbers

_Generated by the AFS assessment assistant (run 6909d89206, mode council, server default models; models used: openai/gpt-oss-120b, openai/gpt-oss-20b, openai/gpt-oss-20b -> rule fallback, qwen/qwen3.8-27b)._

---

# Appendix: how this assessment was made

Contents: A Path analysis · B Extracted requirements · C Rules that fired · D Method screening · E Spectral coverage · F Evidence retrieved · G Verification · H Quality checks · I Confidence · J Enquiry coach · K Council · L What-if changes · M Retrieval and model trace

## A. AFS path analysis
**Suggested path:** A. Path A turns spectral data into real-time concentration values for process automation; a central full-spectrum analyzer gives the higher accuracy. [S02 p.20, S02 p.18]

**Answers to the path questions**
- Path B - Where it is used: In production
- Path C - Variables per sensor: One

| Path | Requested by | Verdict | Reason | Sources |
|---|---|---|---|---|
| A | expert | fits | Path A turns spectral data into real-time concentration values for process automation; a central full-spectrum analyzer gives the higher accuracy. | S02 p.20, S02 p.18 |
| B | expert | conflicts | Path B is a lab system for R&D; measuring in production is Path A (central analyzer) or Path C (sensors). | S02 p.20 |
| C | expert | open | No finding speaks for or against this path yet; the lab trial decides. | S02 p.20 |

## B. Extracted requirements
**Summary:** Assess Raman’s impact on NIR calibration for new powder blend; test combined spectra and chemometric model transfer.

| Field | Value |
|---|---|
| target variables | API concentration |
| target defined | yes |
| matrix | unknown |
| phase | powder |
| optical behavior | unknown |
| aqueous | unknown |
| fluorescent target | unknown |
| heterogeneous | unknown |
| temperature | unknown |
| fouling risk | unknown |
| process context | pilot |
| analyzer remote | unknown |
| link length known | no |
| existing assets | NIR pilot |
| requested methods | NIR, RAMAN |
| reference method | unknown |
| concentration level | unknown |
| measurement points | unknown |
| preferred paths | - |

**Facts** (stated / inferred, with the words they come from)
- existing_assets: NIR pilot _(stated)_ — "existing NIR pilot follows API concentration in one powder formulation at the tablet press feed frame"
- target_variables: API concentration _(stated)_ — "introducing a different API and excipient blend and would like to reuse the calibration"
- requested_methods: Raman _(stated)_ — "colleague suggests adding Raman so that the old calibration will remain valid"

**Unknowns**
- matrix composition _(high impact)_: Affects spectral response and calibration transfer
- optical behavior _(high impact)_: Determines scattering and absorption characteristics
- concentration level _(high impact)_: Defines calibration range and sensitivity

**Client premises found**
- P1 (method claim): "Adding Raman will keep the old calibration valid"
- P2 (reuse claim): "Reuse existing NIR calibration for new API/excipient blend"

## C. Rules that fired (7)
| Severity | Rule | Finding | Sources |
|---|---|---|---|
| warn | R_CALIBRATION_MATRIX: Calibrations are matrix specific | NIR and other spectra need chemometric calibration models built and validated on the actual matrix. A new API or excipient blend changes the spectra, so an existing calibration must be re-validated and normally rebuilt; reuse is a hypothesis to test, not an assumption. | S01 p.10, S01 p.5, S03 p.14 |
| warn | R_ADD_METHOD_NOT_A_FIX: Adding a method does not keep a calibration valid | Adding a second method (for example Raman) does not make an existing single-method calibration valid. Data from different methods are not equivalent; a fused model needs synchronised data, fusion algorithms and its own calibration and validation. | S01 p.8, S01 p.9, S01 p.15 |
| info | R_RAMAN_FLUO_BACKGROUND: Raman fluorescence background risk | Raman signals are weak and, for many organic or biological samples, fluorescence can overlay them. Check background and signal quality on real samples; state excitation wavelength and Raman shift separately. | S01 p.11, S02 p.7 |
| info | R_POWDER: Powders favour NIR diffuse reflection; Raman as comparison | Powders: NIR diffuse reflection probe (scattering media, powder) and Raman probe (liquid, powder, solid) are the table-supported interfaces; NIR and Raman are the common in-line pharmaceutical pair. | S01 p.6, S01 p.14, S01 p.15 |
| info | R_PHARMA_BLEND: Pharmaceutical powder blends | Blend potency in a tablet press feed frame is supported for NIR reflection and Raman (785 nm contact probe); a fused NIR+Raman model is a hypothesis to test against single-method models. | S01 p.14, S01 p.15 |
| info | R_NO_REFERENCE: Reference method unknown | - | S01 p.5, S01 p.10 |
| info | R_PATH_PROCESS_MODEL: A production process with a target variable favours a chemometric model | - | S02 p.20, S02 p.18 |

## D. Method screening (deterministic)
| Method | Score | Verdict | Asked for by client | Contributions |
|---|---|---|---|---|
| NIR spectroscopy | 3 | lead | yes | +2 Powders favour NIR diffuse reflection; Raman as comparison [S01 p.6, S01 p.14] (R_POWDER); +1 Pharmaceutical powder blends [S01 p.14, S01 p.15] (R_PHARMA_BLEND) |
| Raman spectroscopy | 2 | candidate | yes | +1 Powders favour NIR diffuse reflection; Raman as comparison [S01 p.6, S01 p.14] (R_POWDER); +1 Pharmaceutical powder blends [S01 p.14, S01 p.15] (R_PHARMA_BLEND) |
| UV/Vis spectroscopy | 0 | weak | no | - |
| Fluorescence spectroscopy | 0 | weak | no | - |
| MIR spectroscopy (ATR) | -1 | weak | no | -1 Powders favour NIR diffuse reflection; Raman as comparison [S01 p.6, S01 p.14] (R_POWDER) |

## E. Spectral coverage (method range vs fiber transmission)
| Method | Method range | Fiber | Fiber range | Overlap | Covers |
|---|---|---|---|---|---|
| NIR | 0.78-2.5 µm | UV-VIS silica fiber (standard or Al/Cu-coated) | 0.18-1.2 µm | 0.78-1.2 µm | partial |
| NIR | 0.78-2.5 µm | VIS-NIR silica fiber (standard or Al/Cu-coated) | 0.35-2.4 µm | 0.78-2.4 µm | partial |
| NIR | 0.78-2.5 µm | Chalcogenide As-S IR fiber (CIR) | 1.1-6.5 µm | 1.1-2.5 µm | partial |
| NIR | 0.78-2.5 µm | Polycrystalline silver-halide IR fiber (PIR) | 3-17 µm | - | none |
| NIR | 0.78-2.5 µm | Hollow glass waveguide | 2-18 µm | 2-2.5 µm | partial |
| NIR | 0.78-2.5 µm | Indium fluoride fiber | 0.3-5.5 µm | 0.78-2.5 µm | full |
| NIR | 0.78-2.5 µm | Zirconium fluoride fiber | 0.3-4.5 µm | 0.78-2.5 µm | full |
| MIR | 2.5-25 µm | UV-VIS silica fiber (standard or Al/Cu-coated) | 0.18-1.2 µm | - | none |
| MIR | 2.5-25 µm | VIS-NIR silica fiber (standard or Al/Cu-coated) | 0.35-2.4 µm | - | none |
| MIR | 2.5-25 µm | Chalcogenide As-S IR fiber (CIR) | 1.1-6.5 µm | 2.5-6.5 µm | partial |
| MIR | 2.5-25 µm | Polycrystalline silver-halide IR fiber (PIR) | 3-17 µm | 3-17 µm | partial |
| MIR | 2.5-25 µm | Hollow glass waveguide | 2-18 µm | 2.5-18 µm | partial |
| MIR | 2.5-25 µm | Indium fluoride fiber | 0.3-5.5 µm | 2.5-5.5 µm | partial |
| MIR | 2.5-25 µm | Zirconium fluoride fiber | 0.3-4.5 µm | 2.5-4.5 µm | partial |
| RAMAN | 0.4-1.1 µm | UV-VIS silica fiber (standard or Al/Cu-coated) | 0.18-1.2 µm | 0.4-1.1 µm | full |
| RAMAN | 0.4-1.1 µm | VIS-NIR silica fiber (standard or Al/Cu-coated) | 0.35-2.4 µm | 0.4-1.1 µm | full |
| RAMAN | 0.4-1.1 µm | Chalcogenide As-S IR fiber (CIR) | 1.1-6.5 µm | - | none |
| RAMAN | 0.4-1.1 µm | Polycrystalline silver-halide IR fiber (PIR) | 3-17 µm | - | none |
| RAMAN | 0.4-1.1 µm | Hollow glass waveguide | 2-18 µm | - | none |
| RAMAN | 0.4-1.1 µm | Indium fluoride fiber | 0.3-5.5 µm | 0.4-1.1 µm | full |
| RAMAN | 0.4-1.1 µm | Zirconium fluoride fiber | 0.3-4.5 µm | 0.4-1.1 µm | full |
| UVVIS | 0.19-0.74 µm | UV-VIS silica fiber (standard or Al/Cu-coated) | 0.18-1.2 µm | 0.19-0.74 µm | full |
| UVVIS | 0.19-0.74 µm | VIS-NIR silica fiber (standard or Al/Cu-coated) | 0.35-2.4 µm | 0.35-0.74 µm | partial |
| UVVIS | 0.19-0.74 µm | Chalcogenide As-S IR fiber (CIR) | 1.1-6.5 µm | - | none |
| UVVIS | 0.19-0.74 µm | Polycrystalline silver-halide IR fiber (PIR) | 3-17 µm | - | none |
| UVVIS | 0.19-0.74 µm | Hollow glass waveguide | 2-18 µm | - | none |
| UVVIS | 0.19-0.74 µm | Indium fluoride fiber | 0.3-5.5 µm | 0.3-0.74 µm | partial |
| UVVIS | 0.19-0.74 µm | Zirconium fluoride fiber | 0.3-4.5 µm | 0.3-0.74 µm | partial |
| FLUO | 0.25-0.8 µm | UV-VIS silica fiber (standard or Al/Cu-coated) | 0.18-1.2 µm | 0.25-0.8 µm | full |
| FLUO | 0.25-0.8 µm | VIS-NIR silica fiber (standard or Al/Cu-coated) | 0.35-2.4 µm | 0.35-0.8 µm | partial |
| FLUO | 0.25-0.8 µm | Chalcogenide As-S IR fiber (CIR) | 1.1-6.5 µm | - | none |
| FLUO | 0.25-0.8 µm | Polycrystalline silver-halide IR fiber (PIR) | 3-17 µm | - | none |
| FLUO | 0.25-0.8 µm | Hollow glass waveguide | 2-18 µm | - | none |
| FLUO | 0.25-0.8 µm | Indium fluoride fiber | 0.3-5.5 µm | 0.3-0.8 µm | partial |
| FLUO | 0.25-0.8 µm | Zirconium fluoride fiber | 0.3-4.5 µm | 0.3-0.8 µm | partial |

**Absorption bands relevant to the targets**
- 1.3-2.2 µm (NIR): API [S02 p.18]

## F. Evidence retrieved (14 passages; BM25 + dense, fused with RRF, diversified with MMR)
- **E1** [S01 p.5] _claim, general_method; RRF 0.1187_: NIR spectroscopy, with its relatively large penetration depth (up to several millimetres) even into dense solid samples due to low absorption and strong scattering, allows the use of ordinary glass for optics
- **E2** [S01 p.5] _claim, general_method; RRF 0.025_: strong absorption in the mid-IR region limits the corresponding spectral method to the analysis of very thin samples (usually less than 50 µm), but it opens up the possibility of using attenuated total reflectance (ATR)
- **E3** [S01 p.5] _claim, general_method; RRF 0.0122_: the spectra of vibrational transitions in Raman and mid-IR spectroscopy carry complementary qualitative and quantitative information about the sample's composition.
- **E4** [S01 p.5] _claim, general_method; RRF 0.0_: the strong overlap of spectral signals in UV spectra complicates the analysis of real samples and makes the use of chemometric algorithms a necessary component
- **E5** [S01 p.5] _claim, general_method; RRF 0.0_: However, most chemicals do not exhibit this property.
- **E6** [S01 p.5] _claim, general_method; RRF 0.0676_: Mid-IR band spectra contain well-defined peaks (absorption bands), while NIR, UV, and fluorescence spectra contain broad, highly overlapping signals
- **E7** [S01 p.5] _claim, general_method; RRF 0.0398_: preliminary data preparation (preprocessing), construction, validation, and application of predictive models, specifically calibration or classification models.
- **E8** [S01 p.5] _claim, general_method; RRF 0.0_: selecting a spectral method for a specific analytical problem is a complex task requiring specialized knowledge in chemistry, physics, and mathematics.
- **E9** [S01 p.15] _chunk, overview; RRF 0.1669_: A multispectral NIRaman fiber probe has industrial grade design that combines NIR reflection and Raman optical techniques in a compact shaft that fits in a tablet press feed frame.
- **E10** [S01 p.15] _claim, literature_application; RRF 0.1633_: By combining Raman and NIR, these models can predict API potency or coating thickness with higher accuracy and robustness than single-method models.
- **E11** [S01 p.15] _chunk, overview; RRF 0.1476_: Evaluating the improvement of blend potency measurements in the feed frame of a rotary tablet press using combined NIR and Raman spectroscopy.
- **E12** [S01 p.12] _claim, general_method; RRF 0.1276_: dependence on concentration is linear over a wide range of intensities.
- **E13** [S01 p.15] _chunk, overview; RRF 0.1353_: Raman spectrometer and Raman fiber probe for contact measurements with 785 nm excitation wavelength During the experimental action, the probes are inserted directly into the process environment, such as the feed frame of a rotary tablet press.
- **E14** [S01 p.10] _claim, general_method; RRF 0.1234_: The broad absorption bands observed in this region overlap, suggesting the use of chemometrics for quantitative and qualitative analysis of spectral data.

## G. Verification (no AI: quotes, numbers, client facts)
Sourced claims verified: 6/8 · unsupported numbers: 0 · client facts not found in the enquiry: 0

| Where | Status | Claim | Citation | Detail |
|---|---|---|---|---|
| recommendations[0].rationale[0] | verified | NIR is the proven method for powder blends in the tablet press feed frame and already deployed in the pilot. | S01 p.5 | - |
| recommendations[0].rationale[1] | verified | Re‑validate the existing NIR calibration on the new blend using a representative calibration set and independent reference assays. | - | not a sourced claim |
| recommendations[1].rationale[0] | verified | Raman provides complementary chemical information and is supported for powder blends in the feed frame. | S01 p.5 | - |
| recommendations[1].rationale[1] | verified | Test Raman alone to assess signal quality, fluorescence background, and linearity for the new API. | - | not a sourced claim |
| recommendations[2].rationale[0] | verified | Published work shows fused NIR‑Raman models can improve accuracy and robustness for API potency in the feed frame, but this is not a guarant | S01 p.15 | - |
| recommendations[2].rationale[1] | verified | Build and compare three models (NIR only, Raman only, fused) on the same calibration set to quantify any benefit. | - | not a sourced claim |
| measurement_concept[0] | verified | Collect synchronized NIR diffuse‑reflection spectra and Raman spectra on representative powder samples, then build chemometric models (PLS)  | - | not a sourced claim |
| measurement_concept[1] | verified | Validate each model against independent reference assays to quantify accuracy, robustness, and any benefit of the fused approach. | - | not a sourced claim |
| spectral_range[0] | verified | NIR diffuse‑reflection: client‑agreed range (broad overlapping bands). | S01 p.5 | - |
| spectral_range[1] | verified | Raman: Raman shift range typically client‑agreed; excitation wavelength 785 nm (as used in pharmaceutical feed‑frame probes). | S01 p.15 | - |
| risks[0] | verified | Fluorescence background may mask Raman signals in organic powders. | S01 p.5 | - |
| risks[1] | unverified | Matrix change may render the existing NIR calibration inaccurate. | S01 p.5 | S01 p.5: quote not on page (49) |
| risks[2] | unverified | Adding Raman does not automatically preserve the validity of the original NIR model. | S01 p.5 | S01 p.5: quote not on page (49) |

**Numbers**
- recommendations[1]: 785 nm: supported
- spectral_range[1]: 785 nm: supported
- feasibility_plan.steps[1]: 785 nm: supported
- assumptions[1]: 785 nm: supported

## H. Quality checks
Passed 15/16 · one automatic repair round was used

| Check | Category | Status | Detail |
|---|---|---|---|
| S1 All required sections present | structure | pass | - |
| S2 3-6 questions, highest impact first | structure | pass | - |
| S3 Plan has samples, reference, comparison, decision basis | structure | pass | - |
| S4 Decision status consistent with rule findings | structure | pass | - |
| G1 Sourced claims verified on the cited page | grounding | warn | 6/8 verified; problems at risks[1], risks[2] |
| G2 No unsupported numbers | grounding | pass | - |
| G3 No invented client facts | grounding | pass | - |
| G4 Evidence used within its scope | grounding | pass | - |
| G5 Each recommendation has a sourced reason | grounding | pass | - |
| H1 No guarantee or readiness wording | honesty | pass | - |
| H2 Units: Raman shift in cm-1, excitation in nm | honesty | pass | - |
| H3 Fiber choice consistent with spectral coverage | honesty | pass | - |
| H4 Contradicted premises are stated plainly in the headline | honesty | pass | - |
| U1 Client-requested weak methods are addressed (why / why not) | usefulness | pass | - |
| U2 Feasibility plan is concrete | usefulness | pass | - |
| U3 Questions cover the high-impact unknowns | usefulness | pass | - |

**Repair notes**
- G1 fixed
- G2 fixed

## I. Confidence (computed from observable signals; the model never rates itself)
**Overall: low**
- Signal Information: low (0.20): 2/10 decision-relevant facts known; target defined: yes
- Signal Evidence: high (1.00): Direct application in AFS sources: R_PHARMA_BLEND
- Signal Scope fit: high (1.00): Requested use matches the scope of the cited evidence
- Signal Client premises: medium (0.67): 0 contradicted, 2 unverifiable, 0 supported
- Signal Verification: medium (0.75): 6/8 sourced claims verified; 0 unsupported numbers
- Signal Model agreement: high (1.00): 3/3 drafts share the lead method(s) NIR; 3/3 share the status 'provisional_assessment' (2 model families)
- NIR: low: lead, screening score 3
- RAMAN: insufficient: candidate, screening score 2
- UVVIS: insufficient: weak, screening score 0
- FLUO: insufficient: weak, screening score 0
- MIR: insufficient: weak, screening score -1
- To raise it, answer: Is the sample clear, turbid or opaque, and does this change during the process? / What concentration range must be covered, and what is the smallest change that matters? / Which independent reference method (and its uncertainty) can provide calibration values?

## J. Enquiry coach
Key facts present: 2/10

| Fact | Status | Impact | Question if missing |
|---|---|---|---|
| Optical behaviour (clear / turbid / opaque) | unknown | high | Is the sample clear, turbid or opaque, and does this change during the process? |
| Concentration range | unknown | high | What concentration range must be covered, and what is the smallest change that matters? |
| Reference method | unknown | high | Which independent reference method (and its uncertainty) can provide calibration values? |
| Process conditions at the probe | unknown | high | What temperature, pressure, flow, fouling and cleaning conditions apply at the probe? |
| Accuracy / acceptance criteria | unknown | medium | Which accuracy, bias or acceptance limits must the measurement meet? |
| Installation and fiber link | unknown | medium | Where can the probe be installed, and how far away will the analyzer be? |
| Response time / update rate | unknown | medium | How quickly must a change be detected (update rate, response time)? |
| Number of measuring points | unknown | low | How many measuring points or streams need monitoring? |
| Target variable / analyte | stated | high | - |
| Sample matrix and phase | inferred | high | What is the sample (liquid, powder, melt, tissue...) and its main components? |

**Improved enquiry template** (fill the [blanks])

    Our existing NIR pilot follows API concentration in one powder formulation at the tablet press feed frame. We are introducing a different API and excipient blend and would like to reuse the calibration. A colleague suggests adding Raman so that the old calibration will remain valid. What should our first technical assessment and experiment be? Optical behaviour (clear / turbid / opaque): [optical behaviour, e.g. 'clear, turbid, or opaque'] Concentration range: [concentration range, e.g. '0.5–5%'] Reference method: [reference method and its uncertainty, e.g. 'HPLC, ±0.1%'] Process conditions at the probe: [temperature, pressure, flow, fouling and cleaning conditions, e.g. '25°C, 1 bar, 10 mL/min, no fouling'] Accuracy / acceptance criteria: [accuracy, bias or acceptance limits, e.g. '±0.5%'] Installation and fiber link: [probe installation location and distance to analyzer, e.g. 'near feed frame, 2 m'] Response time / update rate: [required update rate or response time, e.g. '1 s'] Number of measuring points: [number of measuring points or streams, e.g. '1']

## K. Council
Winner: draft A · agreement 100% (3/3 drafts share the lead method(s) NIR; 3/3 share the status 'provisional_assessment') · model families: 2

| Draft | Model | Status | Lead methods | Gate failures | Judge score |
|---|---|---|---|---|---|
| A | openai/gpt-oss-120b | provisional_assessment | NIR | G1 Sourced claims verified on the cited page, G2 No unsupported numbers | 5.0 |
| B | qwen/qwen3.8-27b | provisional_assessment | NIR | G1 Sourced claims verified on the cited page, G2 No unsupported numbers | 5.0 |
| C | openai/gpt-oss-20b | provisional_assessment | NIR | G2 No unsupported numbers | 4.0 |
- Judge openai/gpt-oss-120b picked B
- Judge qwen/qwen3.8-27b picked A
- Judge openai/gpt-oss-20b picked B

## L. What-if changes
- (this is not a what-if run)

## M. Retrieval and model trace
**Search queries**
- API concentration in unknown powder
- unknown powder probe geometry NIR spectroscopy Raman spectroscopy
- Calibrations are matrix specific Adding a method does not keep a calibration valid Raman fluorescence background risk Powders favour NIR diffuse reflection; Raman as comparison
- Our existing NIR pilot follows API concentration in one powder formulation at the tablet press feed frame. We are introducing a different API and excipient blend and would like to reuse the calibration. A colleague suggests adding Raman so that the old calibration will remain valid. What should our
- NIR spectroscopy API powder feed frame calibration Raman spectroscopy
- NIR pilot
- NIR RAMAN limitations API concentration
- Passages pinned by blocking/warning rules: 29; evidence tokens used: 1293

| Stage | Model | Prompt tokens | Completion tokens | Latency (ms) | Cached | OK |
|---|---|---|---|---|---|---|
| extract | openai/gpt-oss-20b | 1787 | 956 | 0 | yes | yes |
| premise | openai/gpt-oss-20b -> rule fallback | 0 | 0 | 1328 | no | no: 1 validation error for PremiseCheckOut verdicts.1   Input should be an object [t |
| council_draft_A | openai/gpt-oss-120b | 4727 | 2362 | 5348 | no | yes |
| council_draft_B | qwen/qwen3.8-27b | 3820 | 1507 | 8069 | no | yes |
| council_draft_C | openai/gpt-oss-20b | 4750 | 1408 | 74557 | no | yes |
| council_judge_A | openai/gpt-oss-120b | 2098 | 328 | 1135 | no | yes |
| council_judge_B | qwen/qwen3.8-27b | 2023 | 122 | 586 | no | yes |
| council_judge_C | openai/gpt-oss-20b | 2298 | 229 | 16146 | no | yes |
| repair | openai/gpt-oss-20b | 4137 | 1926 | 41222 | no | yes |
| coach | openai/gpt-oss-20b | 539 | 286 | 0 | yes | yes |

Stage timings: extract 5 ms, rules 13 ms, retrieve 165 ms, premise 1331 ms, council 106066 ms, verify 41347 ms, coach 2 ms, total 148940 ms

