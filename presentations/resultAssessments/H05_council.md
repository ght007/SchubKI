# First technical assessment

> **Enquiry:** We have a liquid process that occasionally goes off specification. We suspect contamination, but we cannot yet name the contaminant or the affected quality variable. We would like you to recommend the best spectroscopy method and exact sensor configuration immediately. What information and first experiment should come before that decision?

**Quality checks:** 13/16 · **Sourced claims verified:** 3/3 · **Unsupported numbers:** 3

## 01. Decision Status
**Provisional assessment** · **Confidence:** insufficient (computed, not self-reported)

An exact method and sensor configuration cannot be finalized until the contaminant identity, its optical signature, and the quality variable to monitor are defined; we recommend Raman spectroscopy as the most promising starting point and outline the information and first experiment needed.

**The customer's own claims, tested first**
- **unverifiable**: "They want an exact recommendation of method and sensor configuration immediately.". An exact configuration cannot be justified before the target, sample optics, conditions and acceptance criteria are known; method selection depends on many factors and is decided by comparison on real samples. [S01 p.5] [S02 p.3]
- **unverifiable**: "They ask what information and first experiment should come before that decision.". The supplied material does not settle this; it needs to be tested. 

To raise confidence, answer: Is the sample clear, turbid or opaque, and does this change during the process? / What concentration range must be covered, and what is the smallest change that matters? / Which independent reference method (and its uncertainty) can provide calibration values?

## 02. Requirements stated
- Recommend best spectroscopy method for a liquid process with unknown contaminant
- Specify sensor configuration
- Identify prerequisite information and first experiment

## 03. Key unknowns
- Identity of the contaminant
- Optical behavior of the contaminant in the aqueous matrix
- Target quality variable to monitor
- Typical concentration level of the contaminant
- Matrix composition and variability

**Assumptions made**
- The contaminant is chemically distinct enough to produce a Raman‑active vibration or MIR absorption band.
- Process temperature and pressure are within the operating limits of standard Raman probes.
- Sufficient sample volume can be diverted for offline reference analysis.

## 04. Clarification questions
1. **What are the most critical quality attributes (e.g., purity, viscosity, color) that could be impacted by the suspected contamination?** _(high impact)_. Why: Knowing the quality variable defines the required sensitivity, selectivity, and whether a quantitative or classification model is needed.
2. **Do you have any prior analytical data (e.g., GC‑MS, HPLC) that hint at possible contaminant classes or functional groups?** _(high impact)_. Why: Even coarse chemical class information narrows the spectral region and probe type (Raman vs. MIR).
3. **What is the typical optical density or turbidity of the process liquid under normal operation?** _(medium impact)_. Why: Optical density determines whether transmission, ATR, or back‑scatter geometries are feasible.
4. **Are there constraints on probe installation (e.g., temperature, pressure, cleaning cycles) at the measurement point?** _(medium impact)_. Why: Installation constraints affect the choice between a local sensor (path C) and a central analyzer with fiber links.
5. **What acceptance criteria (e.g., false‑negative rate, detection limit) would satisfy process control?** _(low impact)_. Why: Criteria drive the required detection limit and thus influence method suitability.

## 05. Recommendation

### Raman (90° back‑scatter probe, liquid immersion) (primary)
- Raman is compatible with aqueous liquids and provides high selectivity for many organic contaminants. _(assumption)_
- A probe can be installed locally at the process point, matching the suggested Path C for lower installation cost. _(proposal)_
- _Applies if:_ Only if a representative set of off‑spec and in‑spec liquid samples can be collected for model building.

### MIR‑ATR (chalcogenide fiber, <50 µm path) (conditional)
- MIR provides well‑defined absorption peaks that can aid identification if the contaminant has strong IR bands. [S01 p.5] _(sourced)_
- Requires a specialty fiber; feasibility should be tested alongside Raman. _(proposal)_
- _Applies if:_ If Raman sensitivity proves insufficient after initial trials.

### NIR (transmission cuvette) (not recommended)
- NIR sensitivity at trace levels is limited for unknown contaminants. _(assumption)_

**Method screening (deterministic, from sourced rules)**

| Method | Score | Verdict |
|---|---|---|
| Raman spectroscopy | 1 | candidate |
| MIR spectroscopy (ATR) | 0 | weak |
| UV/Vis spectroscopy | 0 | weak |
| Fluorescence spectroscopy | 0 | weak |
| NIR spectroscopy | -1 | weak |

## 06. Measurement concept
- Raman spectroscopy with a 90° back‑scatter probe is well‑suited for aqueous liquids because water exhibits low Raman absorbance, providing high signal‑to‑noise for dissolved species. [S01 p.5] _(sourced)_
- If the contaminant has strong mid‑IR absorption, an ATR probe could capture well‑defined peaks, but requires a chalcogenide or polycrystalline fiber for MIR transmission. [S01 p.5] _(sourced)_
- NIR is less attractive for trace‑level detection because sensitivity drops below ~0.1 % for unknown species. _(assumption)_

## 07. Spectral range
- Raman: excitation typically 785 nm or 532 nm; Raman shift measured in cm⁻¹ covering 200–3500 cm⁻¹. _(proposal)_
- MIR‑ATR: 4000–650 cm⁻¹ (2500–15000 nm) using chalcogenide fiber. _(proposal)_

## 08. Risks and uncertainty
- If the contaminant does not have a strong Raman‑active vibration, detection may be limited. _(assumption)_
- ATR probe fouling in a process stream could degrade signal over time. _(assumption)_
- Raman signal can be weak for low‑concentration species; may require longer integration or higher laser power, raising safety considerations. _(assumption)_

**Confidence: insufficient**
- Information: insufficient (1/10 decision-relevant facts known; target defined: partial)
- Evidence: low (Only general method knowledge applies; no direct application example in the sources)
- Scope fit: high (Requested use matches the scope of the cited evidence)
- Client premises: medium (0 contradicted, 2 unverifiable, 0 supported)
- Verification: high (3/3 sourced claims verified; 3 unsupported numbers)
- Model agreement: low (1/2 drafts share the lead method(s) RAMAN; 1/2 share the status 'provisional_assessment' (2 model families))
- Cap: R_CERTAINTY_DEMAND: cap low

## 09. Decision basis
- Ability to detect the contaminant at the concentration observed in off‑spec samples (client‑agreed detection limit)
- Robustness of the probe under process temperature/pressure conditions
- Ease of integration at the measurement point (cost, cleaning, maintenance)

## 10. Sources
- **S01 p.5**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "strong absorption in the mid-IR region limits the corresponding spectral method to the analysis of very thin samples (usually less than 50 µm), but it opens up the possibility of using attenuated total reflectance (ATR)"
  - "the spectra of vibrational transitions in Raman and mid-IR spectroscopy carry complementary qualitative and quantitative information about the sample's composition."
  - "NIR spectroscopy, with its relatively large penetration depth (up to several millimetres) even into dense solid samples due to low absorption and strong scattering, allows the use of ordinary glass for optics"
- **S02 p.3**: Process-Control in-line with Spectral Fiber Systems (AFS slides) _(company slides)_
  - "Multi-Spectral Fiber Systems allow to test 4 spectroscopy methods in 0.3-16µm range"

## 11. First feasibility experiment
**Samples**
- In‑spec liquid from normal operation
- Off‑spec liquid collected during a deviation
- Spiked laboratory samples covering a range of plausible contaminants (e.g., organic solvents, salts, oils)
**Reference measurements**
- Independent laboratory analysis (e.g., GC‑MS or HPLC) to confirm presence/absence of contaminants in each sample
**Comparison**
- Raman probe vs. MIR‑ATR probe (if available) on identical samples
- Signal‑to‑noise and detection limit assessment for each method
**Steps**
1. Collect representative liquid samples (in‑spec, off‑spec, and spiked) and perform reference analysis.
2. Acquire Raman spectra with a standard 90° back‑scatter probe (785 nm laser) on all samples.
3. If possible, acquire MIR‑ATR spectra using a short‑path ATR probe on the same set.
4. Build preliminary chemometric classification models (e.g., PLS‑DA) for each method using the reference labels.
5. Evaluate detection limits, repeatability, and probe durability against client‑agreed criteria.
6. Decide on the final sensor configuration (Raman only or Raman + MIR) and proceed to pilot‑scale installation.

**Next step with AFS**
- Perform a lab‑scale comparative trial of Raman and optional MIR‑ATR probes on representative process liquids to determine the most sensitive and robust configuration for on‑site sensor deployment.
- Likely path: C - Path C favours low‑cost local sensors; the trial will confirm which local probe meets the required detection performance.
- Path A (chosen by the expert): **open**. No finding speaks for or against this path yet; the lab trial decides. [S02 p.20]
- Path B (chosen by the expert): **open**. No finding speaks for or against this path yet; the lab trial decides. [S02 p.20]
- Path C (chosen by the expert): **fits**. Sensors installed at the measuring points give lower installation cost than a central analyzer with long fibers. [S02 p.18, S02 p.19]

**Proposed setup** (ranked by recommendation; validate in a lab trial)

| System | Path A: Chemometric model for process automation | Path B: Multi-spectral system for your R&D lab | Path C: Low-cost spectral sensors |
|---|---|---|---|
| 1. Raman (90° back‑scatter probe, liquid immersion) (primary) | Models: Target calibration → Process predictions | Lab system: RAMAN measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: RAMAN sensor, Process probe(s), Acquisition + control interface → Process monitoring |
| 2. MIR‑ATR (chalcogenide fiber, <50 µm path) (conditional) | Models: Target calibration → Process predictions | Lab system: MIR measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: MIR sensor, Process probe(s), Acquisition + control interface → Process monitoring |

## Council
Winner: draft A; agreement 50% (1/2 drafts share the lead method(s) RAMAN; 1/2 share the status 'provisional_assessment')
- Draft A (openai/gpt-oss-120b): judge score 4.67, gate failures: G1 Sourced claims verified on the cited page, G2 No unsupported numbers
- Draft B (qwen/qwen3.8-27b): judge score 0.0, gate failures: none
- Draft C (openai/gpt-oss-20b): judge score 4.33, gate failures: G1 Sourced claims verified on the cited page

_Generated by the AFS assessment assistant (run 9d2f822bd5, mode council, server default models; models used: openai/gpt-oss-120b, openai/gpt-oss-20b, openai/gpt-oss-20b -> rule fallback, qwen/qwen3.8-27b)._

---

# Appendix: how this assessment was made

Contents: A Path analysis · B Extracted requirements · C Rules that fired · D Method screening · E Spectral coverage · F Evidence retrieved · G Verification · H Quality checks · I Confidence · J Enquiry coach · K Council · L What-if changes · M Retrieval and model trace

## A. AFS path analysis
**Suggested path:** C. Sensors installed at the measuring points give lower installation cost than a central analyzer with long fibers. [S02 p.18, S02 p.19]

| Path | Requested by | Verdict | Reason | Sources |
|---|---|---|---|---|
| A | expert | open | No finding speaks for or against this path yet; the lab trial decides. | S02 p.20 |
| B | expert | open | No finding speaks for or against this path yet; the lab trial decides. | S02 p.20 |
| C | expert | fits | Sensors installed at the measuring points give lower installation cost than a central analyzer with long fibers. | S02 p.18, S02 p.19 |

## B. Extracted requirements
**Summary:** Liquid process occasionally off spec, contamination suspected but contaminant and quality variable unknown. Need recommendation of best spectroscopy method and sensor configuration, plus guidance on what information and first experiment to perform before deciding.

| Field | Value |
|---|---|
| target variables | - |
| target defined | partial |
| matrix | unknown |
| phase | liquid |
| optical behavior | unknown |
| aqueous | yes |
| fluorescent target | unknown |
| heterogeneous | unknown |
| temperature | unknown |
| fouling risk | unknown |
| process context | unknown |
| analyzer remote | unknown |
| link length known | no |
| existing assets | - |
| requested methods | - |
| reference method | unknown |
| concentration level | unknown |
| measurement points | unknown |
| preferred paths | - |

**Facts** (stated / inferred, with the words they come from)
- phase: liquid _(stated)_ — "liquid process"
- contamination_suspected: yes _(stated)_ — "suspect contamination"
- quality_variable_unknown: unknown _(stated)_ — "cannot yet name the contaminant or the affected quality variable"

**Unknowns**
- contaminant identity _(high impact)_: Determines suitable spectral range and detection limits
- quality variable to monitor _(high impact)_: Defines measurement objective and calibration strategy
- optical behavior of the liquid _(high impact)_: Affects choice of probe and fiber type
- concentration level of contaminant _(high impact)_: Influences sensitivity and detection limits
- matrix composition _(high impact)_: Affects spectral background and calibration

**Client premises found**
- P1 (certainty request): "They want an exact recommendation of method and sensor configuration immediately."
- P2 (other): "They ask what information and first experiment should come before that decision."

## C. Rules that fired (5)
| Severity | Rule | Finding | Sources |
|---|---|---|---|
| warn | R_CERTAINTY_DEMAND: Request for a final configuration on missing facts | An exact configuration cannot be justified before the target, sample optics, conditions and acceptance criteria are known; method selection depends on many factors and is decided by comparison on real samples. | S01 p.5, S02 p.3 |
| info | R_AQUEOUS: Water-rich media | Water absorbs strongly in the IR; Raman shows low water absorbance and suits aqueous media. MIR is used via ATR (very short path). | S01 p.16, S01 p.5 |
| info | R_TRACE: Trace levels challenge NIR | NIR may lack sensitivity for compounds below about 0.1 %; trace targets need a method with sufficient sensitivity and selectivity for the specific species. | S01 p.16 |
| info | R_NO_REFERENCE: Reference method unknown | - | S01 p.5, S01 p.10 |
| info | R_PATH_MANY_LOW_COST_POINTS: Many measuring points at low cost favour spectral sensors | - | S02 p.18, S02 p.19 |

## D. Method screening (deterministic)
| Method | Score | Verdict | Asked for by client | Contributions |
|---|---|---|---|---|
| Raman spectroscopy | 1 | candidate | no | +1 Water-rich media [S01 p.16, S01 p.5] (R_AQUEOUS) |
| MIR spectroscopy (ATR) | 0 | weak | no | - |
| UV/Vis spectroscopy | 0 | weak | no | - |
| Fluorescence spectroscopy | 0 | weak | no | - |
| NIR spectroscopy | -1 | weak | no | -1 Trace levels challenge NIR [S01 p.16] (R_TRACE) |

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

## F. Evidence retrieved (14 passages; BM25 + dense, fused with RRF, diversified with MMR)
- **E1** [S01 p.5] _claim, general_method; RRF 0.0139_: NIR spectroscopy, with its relatively large penetration depth (up to several millimetres) even into dense solid samples due to low absorption and strong scattering, allows the use of ordinary glass for optics
- **E2** [S01 p.5] _claim, general_method; RRF 0.0_: strong absorption in the mid-IR region limits the corresponding spectral method to the analysis of very thin samples (usually less than 50 µm), but it opens up the possibility of using attenuated total reflectance (ATR)
- **E3** [S01 p.5] _claim, general_method; RRF 0.0285_: the spectra of vibrational transitions in Raman and mid-IR spectroscopy carry complementary qualitative and quantitative information about the sample's composition.
- **E4** [S01 p.5] _claim, general_method; RRF 0.0285_: the strong overlap of spectral signals in UV spectra complicates the analysis of real samples and makes the use of chemometric algorithms a necessary component
- **E5** [S01 p.5] _claim, general_method; RRF 0.0_: However, most chemicals do not exhibit this property.
- **E6** [S01 p.5] _claim, general_method; RRF 0.0_: Mid-IR band spectra contain well-defined peaks (absorption bands), while NIR, UV, and fluorescence spectra contain broad, highly overlapping signals
- **E7** [S01 p.5] _claim, general_method; RRF 0.0_: preliminary data preparation (preprocessing), construction, validation, and application of predictive models, specifically calibration or classification models.
- **E8** [S01 p.5] _claim, general_method; RRF 0.0_: selecting a spectral method for a specific analytical problem is a complex task requiring specialized knowledge in chemistry, physics, and mathematics.
- **E9** [S01 p.3] _claim, general_method; RRF 0.0793_: The ability to test various optical spectroscopy approaches is crucial for solving complex analytical problems, such as analyzing natural and industrial samples of incompletely known composition, in order to select the most suitable method or combination of methods.
- **E10** [S01 p.6] _chunk, overview; RRF 0.0611_: (emission) liquid 2-5 mm average high high Raman-probe liquid, powder, solid 4 UV/Visibl e spectrosc opy cuvette absorption liquid 1-5 mm high low low ATR probe 0.1-1 mu low avera ge Diffuse reflection- probe diffuse reflection solid, pill 1-5 mm low low Transmission or transflection probe Transmiss…
- **E11** [S01 p.18] _claim, general_method; RRF 0.0593_: it fails when the milk becomes too "thick" or fat-rich, as the light cannot penetrate the sample.
- **E12** [S04 p.1] _chunk, lab_demonstration; RRF 0.0579_: Technical evaluation of the probe has conﬁrmed its output signal quality that was comparable to that of respective probes for single methods.
- **E13** [S01 p.16] _claim, general_method; RRF 0.0557_: For highly transparent liquids with low optical density, UV-Transmission or Transflection probes are ideal
- **E14** [S01 p.6] _chunk, overview; RRF 0.056_: 6 Table 1. Comparative characteristics of spectral methods and measurement techniques. №Method Measurement method Physical phenomenon Sample Type Optical path, depth Sensitiv ity Selectivit y Cost 1 IR spectrosc opy ATR- platform absorption liquid,paste, soft 1-6 mu average high high ATR probe* cuve…

## G. Verification (no AI: quotes, numbers, client facts)
Sourced claims verified: 3/3 · unsupported numbers: 3 · client facts not found in the enquiry: 0

| Where | Status | Claim | Citation | Detail |
|---|---|---|---|---|
| recommendations[0].rationale[0] | verified | Raman is compatible with aqueous liquids and provides high selectivity for many organic contaminants. | - | not a sourced claim |
| recommendations[0].rationale[1] | verified | A probe can be installed locally at the process point, matching the suggested Path C for lower installation cost. | - | not a sourced claim |
| recommendations[1].rationale[0] | verified | MIR provides well‑defined absorption peaks that can aid identification if the contaminant has strong IR bands. | S01 p.5 | - |
| recommendations[1].rationale[1] | verified | Requires a specialty fiber; feasibility should be tested alongside Raman. | - | not a sourced claim |
| recommendations[2].rationale[0] | verified | NIR sensitivity at trace levels is limited for unknown contaminants. | - | not a sourced claim |
| measurement_concept[0] | verified | Raman spectroscopy with a 90° back‑scatter probe is well‑suited for aqueous liquids because water exhibits low Raman absorbance, providing h | S01 p.5 | - |
| measurement_concept[1] | verified | If the contaminant has strong mid‑IR absorption, an ATR probe could capture well‑defined peaks, but requires a chalcogenide or polycrystalli | S01 p.5 | - |
| measurement_concept[2] | verified | NIR is less attractive for trace‑level detection because sensitivity drops below ~0.1 % for unknown species. | - | not a sourced claim |
| spectral_range[0] | verified | Raman: excitation typically 785 nm or 532 nm; Raman shift measured in cm⁻¹ covering 200–3500 cm⁻¹. | - | not a sourced claim |
| spectral_range[1] | verified | MIR‑ATR: 4000–650 cm⁻¹ (2500–15000 nm) using chalcogenide fiber. | - | not a sourced claim |
| risks[0] | verified | If the contaminant does not have a strong Raman‑active vibration, detection may be limited. | - | not a sourced claim |
| risks[1] | verified | ATR probe fouling in a process stream could degrade signal over time. | - | not a sourced claim |
| risks[2] | verified | Raman signal can be weak for low‑concentration species; may require longer integration or higher laser power, raising safety considerations. | - | not a sourced claim |

**Numbers**
- recommendations[1]: 50 µm: supported
- measurement_concept[2]: 0.1 %: supported
- spectral_range[0]: 785 nm: supported
- spectral_range[0]: 532 nm: unsupported (not found in the enquiry, the evidence or the cited pages)
- spectral_range[0]: 200–3500 cm⁻¹: unsupported (not found in the enquiry, the evidence or the cited pages)
- spectral_range[1]: 4000–650 cm⁻¹: unsupported (not found in the enquiry, the evidence or the cited pages)
- spectral_range[1]: 2500–15000 nm: supported
- feasibility_plan.steps[1]: 785 nm: supported

## H. Quality checks
Passed 13/16 · one automatic repair round was used

| Check | Category | Status | Detail |
|---|---|---|---|
| S1 All required sections present | structure | pass | - |
| S2 3-6 questions, highest impact first | structure | pass | - |
| S3 Plan has samples, reference, comparison, decision basis | structure | pass | - |
| S4 Decision status consistent with rule findings | structure | pass | - |
| G1 Sourced claims verified on the cited page | grounding | pass | - |
| G2 No unsupported numbers | grounding | fail | 532 nm at spectral_range[0]; 200–3500 cm⁻¹ at spectral_range[0]; 4000–650 cm⁻¹ at spectral_range[1] |
| G3 No invented client facts | grounding | pass | - |
| G4 Evidence used within its scope | grounding | pass | - |
| G5 Each recommendation has a sourced reason | grounding | fail | no sourced rationale: Raman (90° back‑scatter probe, liquid immersion) |
| H1 No guarantee or readiness wording | honesty | pass | - |
| H2 Units: Raman shift in cm-1, excitation in nm | honesty | pass | - |
| H3 Fiber choice consistent with spectral coverage | honesty | pass | - |
| H4 Contradicted premises are stated plainly in the headline | honesty | pass | - |
| U1 Client-requested weak methods are addressed (why / why not) | usefulness | pass | - |
| U2 Feasibility plan is concrete | usefulness | pass | - |
| U3 Questions cover the high-impact unknowns | usefulness | warn | 0/1 high-impact rule questions covered |

**Repair notes**
- G1 fixed

## I. Confidence (computed from observable signals; the model never rates itself)
**Overall: insufficient**
- Signal Information: insufficient (0.10): 1/10 decision-relevant facts known; target defined: partial
- Signal Evidence: low (0.33): Only general method knowledge applies; no direct application example in the sources
- Signal Scope fit: high (1.00): Requested use matches the scope of the cited evidence
- Signal Client premises: medium (0.67): 0 contradicted, 2 unverifiable, 0 supported
- Signal Verification: high (1.00): 3/3 sourced claims verified; 3 unsupported numbers
- Signal Model agreement: low (0.50): 1/2 drafts share the lead method(s) RAMAN; 1/2 share the status 'provisional_assessment' (2 model families)
- Cap: R_CERTAINTY_DEMAND: cap low
- RAMAN: insufficient: candidate, screening score 1
- MIR: insufficient: weak, screening score 0
- UVVIS: insufficient: weak, screening score 0
- FLUO: insufficient: weak, screening score 0
- NIR: insufficient: weak, screening score -1
- To raise it, answer: Is the sample clear, turbid or opaque, and does this change during the process? / What concentration range must be covered, and what is the smallest change that matters? / Which independent reference method (and its uncertainty) can provide calibration values?

## J. Enquiry coach
Key facts present: 1/10

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
| Target variable / analyte | inferred | high | Which variable or analyte must be measured, and which changes must be distinguished? |
| Sample matrix and phase | inferred | high | What is the sample (liquid, powder, melt, tissue...) and its main components? |

**Improved enquiry template** (fill the [blanks])

    We have a liquid process that occasionally goes off specification. We suspect contamination, but we cannot yet name the contaminant or the affected quality variable. We would like you to recommend the best spectroscopy method and exact sensor configuration immediately. What information and first experiment should come before that decision? 
    
    - Optical behaviour (clear / turbid / opaque): [optical behaviour, e.g. 'clear, turbid, or opaque, and does this change during the process?']
    - Concentration range: [concentration range, e.g. 'x to y %', and what is the smallest change that matters?]
    - Reference method: [reference method and its uncertainty, e.g. 'GC-MS with 0.5% uncertainty']
    - Process conditions at the probe: [temperature, pressure, flow, fouling and cleaning conditions at the probe]
    - Accuracy / acceptance criteria: [accuracy, bias or acceptance limits that must be met]
    - Installation and fiber link: [probe installation location and distance to analyzer]
    - Response time / update rate: [required update rate or response time]
    - Number of measuring points: [number of measuring points or streams to monitor]

## K. Council
Winner: draft A · agreement 50% (1/2 drafts share the lead method(s) RAMAN; 1/2 share the status 'provisional_assessment') · model families: 2

| Draft | Model | Status | Lead methods | Gate failures | Judge score |
|---|---|---|---|---|---|
| A | openai/gpt-oss-120b | provisional_assessment | RAMAN | G1 Sourced claims verified on the cited page, G2 No unsupported numbers | 4.67 |
| B | qwen/qwen3.8-27b | error: model failed | - | none | 0.0 |
| C | openai/gpt-oss-20b | insufficient_information | - | G1 Sourced claims verified on the cited page | 4.33 |
- Judge openai/gpt-oss-120b picked C
- Judge openai/gpt-oss-20b picked A

## L. What-if changes
- (this is not a what-if run)

## M. Retrieval and model trace
**Search queries**
- composition in unknown liquid
- unknown liquid probe geometry Raman spectroscopy
- Request for a final configuration on missing facts Water-rich media Trace levels challenge NIR Reference method unknown
- We have a liquid process that occasionally goes off specification. We suspect contamination, but we cannot yet name the contaminant or the affected quality variable. We would like you to recommend the best spectroscopy method and exact sensor configuration immediately. What information and first exp
- Passages pinned by blocking/warning rules: 9; evidence tokens used: 1320

| Stage | Model | Prompt tokens | Completion tokens | Latency (ms) | Cached | OK |
|---|---|---|---|---|---|---|
| extract | openai/gpt-oss-20b | 1725 | 546 | 0 | yes | yes |
| premise | openai/gpt-oss-20b -> rule fallback | 0 | 0 | 1798 | no | no: 1 validation error for PremiseCheckOut verdicts.1   Input should be an object [t |
| council_draft_A | openai/gpt-oss-120b | 4537 | 2388 | 5601 | no | yes |
| council_draft_B | qwen/qwen3.8-27b | 0 | 0 | 64393 | no | no: qwen/qwen3.8-27b: retries exhausted |
| council_draft_C | openai/gpt-oss-20b | 4537 | 967 | 1495 | no | yes |
| council_judge_A | openai/gpt-oss-120b | 1332 | 234 | 837 | no | yes |
| council_judge_C | openai/gpt-oss-20b | 1523 | 226 | 608 | no | yes |
| repair | openai/gpt-oss-20b | 4008 | 1859 | 27961 | no | yes |
| coach | openai/gpt-oss-20b | 534 | 272 | 10434 | no | yes |

Stage timings: extract 7 ms, rules 52 ms, retrieve 186 ms, premise 1809 ms, council 74120 ms, verify 28086 ms, coach 10448 ms, total 114725 ms

