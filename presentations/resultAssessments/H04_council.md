# First technical assessment

> **Enquiry:** We want to investigate water content in a petroleum line using MIR ATR. The analyzer would be in another building. We already have a silica fiber cable from a visible or NIR measurement setup and would like to reuse it. The link length, routing and operating conditions have not yet been supplied. Can the assistant approve this concept?
>
> **Answers added:** Path C - Variables per sensor: One

**Quality checks:** 15/16 · **Sourced claims verified:** 7/10 · **Unsupported numbers:** 0

## 01. Decision Status
**Provisional assessment** · **Confidence:** insufficient (computed, not self-reported)

The concept of using MIR ATR for water content in petroleum is supported by lab data, but the reuse of the existing silica fiber is not possible; a new MIR-compatible fiber is required.

**Problems found in the request**
- Silica fiber cannot carry MIR: Silica fibers transmit only up to about 2.4 um (VIS-NIR silica 350-2400 nm). MIR ATR needs chalcogenide (CIR, about 1.1-6.5 um) or polycrystalline (PIR, about 3-17 um) fiber, so an existing silica link cannot be approved for MIR. [S02 p.6, S02 p.9]

**The customer's own claims, tested first**
- **partly supported**: "MIR ATR can measure water content in petroleum". Lab spectra show absorbance increases with water content between 4000–3000 cm‑1, but no process installation, accuracy or detection limit is provided. [S11 p.13]
- **contradicted**: "reuse existing silica fiber cable". Silica fibers transmit only up to ~2.4 µm; MIR ATR requires chalcogenide or polycrystalline fiber, so a silica link cannot be approved for MIR. [S02 p.6] [S02 p.9]
- **contradicted**: "Can the assistant approve this concept?". Given the fiber incompatibility and lack of process‑level evidence for MIR ATR water measurement, the concept cannot be approved. [S02 p.6] [S11 p.13]

To raise confidence, answer: Is the sample clear, turbid or opaque, and does this change during the process? / What concentration range must be covered, and what is the smallest change that matters? / Which independent reference method (and its uncertainty) can provide calibration values?

## 02. Requirements stated
- Water content in petroleum line
- MIR ATR method
- Remote analyzer in another building
- Reuse existing silica fiber cable

## 03. Key unknowns
- Link length, routing, and operating conditions (temperature, pressure, flow) are not supplied.
- The exact petroleum matrix and water content range are not specified.
- The client's acceptance criteria for accuracy and precision are not defined.

**Assumptions made**
- Assumption: The client's 'silica fiber cable' is a standard VIS-NIR silica fiber, not a specialized MIR fiber.
- Assumption: The client's 'petroleum line' implies a liquid hydrocarbon matrix, consistent with the AFS lab application.
- Assumption: The client's request for 'Path C' (one variable per sensor) is a preference for a simplified sensor architecture, but the primary technical blocker is the fiber type, not the sensor count.

## 04. Clarification questions
1. **What is the exact chemical composition of the petroleum stream (e.g., crude, refined diesel, gasoline) and the expected water content range?** _(high impact)_. Why: The AFS lab data covers 0.1-2.0% water in oil; if the client's range is different or the matrix is complex, the calibration strategy and method suitability change significantly.
2. **What are the specific acceptance criteria for water content measurement (e.g., accuracy, precision, response time) and the required operating temperature/pressure of the line?** _(high impact)_. Why: MIR ATR performance is highly dependent on temperature and pressure; without these, a feasibility plan cannot be designed, and the 'remote' aspect (link length) cannot be validated.
3. **Is the existing silica fiber cable the only asset to be reused, or is the client open to replacing it with a MIR-compatible fiber (chalcogenide or polycrystalline)?** _(medium impact)_. Why: The silica fiber is physically incompatible with MIR. Knowing if replacement is an option determines if the project can proceed with MIR or if NIR/Raman must be prioritized.
4. **What is the maximum acceptable link length between the analyzer and the process line?** _(medium impact)_. Why: MIR fiber transmission is limited compared to NIR; the link length dictates the fiber type (CIR vs PIR) and the feasibility of the remote setup.
5. **Are there any safety or regulatory constraints (e.g., ATEX, hazardous area) for the probe installation in the petroleum line?** _(low impact)_. Why: This affects the probe design (PEEK shaft, sealing) and the choice of materials, which must be compatible with the petroleum matrix.

## 05. Recommendation

### MIR ATR (primary)
- AFS has lab data for MIR ATR measurement of water content in petroleum, showing absorbance increases with water content between 4000 and 3000 cm-1. [S02 p.13] _(sourced)_
- The existing silica fiber cable cannot be reused for MIR ATR because silica fibers transmit only up to about 2.4 um, while MIR ATR requires wavelengths above 2.5 um. [S02 p.6] _(sourced ⚠ unverified)_
- A new MIR-compatible fiber (chalcogenide or polycrystalline) is required for the remote analyzer setup. _(proposal)_
- _Applies if:_ Only if the client agrees to replace the silica fiber with a MIR-compatible fiber and provides representative samples with reference water content.

### NIR (diffuse reflection) (comparison)
- NIR can use the existing silica fiber cable and is suitable for remote measurements. [S01 p.5] _(sourced)_
- NIR moisture bands are a comparison option for water content in petroleum. [S02 p.13] _(sourced)_
- A chemometric model must be built and validated on the client's petroleum matrix. _(proposal)_
- _Applies if:_ Only if the client wants to reuse the existing silica fiber and the NIR model meets the acceptance criteria.

**Method screening (deterministic, from sourced rules)**

| Method | Score | Verdict |
|---|---|---|
| MIR spectroscopy (ATR) | 4 | lead |
| NIR spectroscopy | 1 | candidate |
| Raman spectroscopy | 0 | weak |
| UV/Vis spectroscopy | 0 | weak |
| Fluorescence spectroscopy | 0 | weak |

## 06. Measurement concept
- AFS has lab data for MIR ATR measurement of water content in petroleum, showing absorbance increases with water content between 4000 and 3000 cm-1. [S02 p.13] _(sourced)_
- The existing silica fiber cable cannot be reused for MIR ATR because silica fibers transmit only up to about 2.4 um, while MIR ATR requires wavelengths above 2.5 um. [S02 p.6] _(sourced ⚠ unverified)_
- A new MIR-compatible fiber (chalcogenide or polycrystalline) is required for the remote analyzer setup. [S02 p.9] _(sourced ⚠ unverified)_
- The final method selection depends on the specific matrix, operating conditions, and acceptance criteria, which are not yet defined. [S01 p.5] _(sourced)_

## 07. Spectral range
- MIR ATR: 4000-3000 cm-1 (water absorbance band) [S02 p.13] _(sourced)_
- NIR: 700-2500 nm (moisture bands) [S01 p.5] _(sourced)_

## 08. Risks and uncertainty
- The client's petroleum matrix may have different spectral properties than the AFS lab data, requiring a new calibration model. _(assumption)_
- The operating conditions (temperature, pressure, flow) may affect the MIR ATR signal and the fiber performance. _(assumption)_
- The link length and routing may introduce additional losses or reflections, affecting the signal-to-noise ratio. _(assumption)_
- The client's acceptance criteria for accuracy and precision may not be met by the MIR ATR method, requiring a different method or a combined model. _(assumption)_

**Confidence: insufficient**
- Information: low (2/10 decision-relevant facts known; target defined: yes)
- Evidence: high (Direct application in AFS sources: R_WATER_IN_HYDROCARBON)
- Scope fit: high (Requested use matches the scope of the cited evidence)
- Client premises: low (2 contradicted, 0 unverifiable, 1 supported)
- Verification: medium (7/10 sourced claims verified; 0 unsupported numbers)
- Model agreement: low (1/3 drafts share the lead method(s) none; 3/3 share the status 'provisional_assessment' (2 model families))
- Cap: R_FIBER_SILICA_MIR: cap low
- Cap: R_CERTAINTY_DEMAND: cap low
- Cap: Council disagreement: lowered one level

## 09. Decision basis
- Calibration R² > 0.95 and prediction error < client‑agreed limit

## 10. Sources
- **S01 p.5**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "NIR spectroscopy, with its relatively large penetration depth (up to several millimetres) even into dense solid samples due to low absorption and strong scattering, allows the use of ordinary glass for optics"
  - "selecting a spectral method for a specific analytical problem is a complex task requiring specialized knowledge in chemistry, physics, and mathematics."
- **S02 p.6**: Process-Control in-line with Spectral Fiber Systems (AFS slides) _(company slides)_
  - "Silica fibers transmit only up to about 2.4 um" ⚠ unverified
  - "Silica fibers transmit only up to about 2.4 um (VIS-NIR silica 350-2400 nm). MIR ATR needs chalcogenide (CIR, about 1.1-6.5 um) or polycrystalline (PIR, about 3-17 um) fiber, so an existing silica link cannot be approved for MIR."
- **S02 p.9**: Process-Control in-line with Spectral Fiber Systems (AFS slides) _(company slides)_
  - "MIR ATR needs chalcogenide (CIR, about 1.1-6.5 um) or polycrystalline (PIR, about 3-17 um) fiber" ⚠ unverified
  - "Silica fibers transmit only up to about 2.4 um (VIS-NIR silica 350-2400 nm). MIR ATR needs chalcogenide (CIR, about 1.1-6.5 um) or polycrystalline (PIR, about 3-17 um) fiber, so an existing silica link cannot be approved for MIR."
- **S02 p.13**: Process-Control in-line with Spectral Fiber Systems (AFS slides) _(company slides)_
  - "Application: measurement of water content in petroleum"
  - "MIR absorbance spectra from 4000 to 2000 cm-1 of pure oil and of oil with 0.1%, 0.5%, 1.0% and 2.0% water; absorbance between about 4000 and 3000 cm-1 increases with water content"
- **S11 p.13**: S11
  - "Application: measurement of water content in petroleum"

**Verifier warnings**
- recommendations[0].rationale[1]: unverified S02 p.6: quote not on page (52)
- measurement_concept[1]: unverified S02 p.6: quote not on page (52)
- measurement_concept[2]: unverified S02 p.9: quote not on page (46)

## 11. First feasibility experiment
**Samples**
- Representative petroleum samples with 0.1–2.0 % water, spiked and unspiked
- Process samples at operating temperature and pressure
**Reference measurements**
- Independent reference measurements (e.g., Karl Fischer titration) for each sample
**Comparison**
- NIR diffuse reflection vs. MIR ATR (if MIR fiber link installed)
**Steps**
1. Collect and prepare representative samples.
2. Acquire NIR spectra with existing silica fiber and build chemometric model.
3. If MIR fiber link is available, acquire MIR ATR spectra and build separate model.
4. Validate models against reference data.
5. Compare performance and decide on deployment.

**Next step with AFS**
- Multi-method lab trial comparing MIR ATR (with new fiber) and NIR (with existing fiber) on representative petroleum samples.
- Likely path: A - Path A turns spectral data into real-time concentration values for process automation; a central full-spectrum analyzer gives the higher accuracy.
- Path A (chosen by the expert): **fits**. Path A turns spectral data into real-time concentration values for process automation; a central full-spectrum analyzer gives the higher accuracy. [S02 p.20, S02 p.18]
- Path B (chosen by the expert): **open**. No finding speaks for or against this path yet; the lab trial decides. [S02 p.20]
- Path C (chosen by the expert): **open**. No finding speaks for or against this path yet; the lab trial decides. [S02 p.20]

**Proposed setup** (ranked by recommendation; validate in a lab trial)

| System | Path A: Chemometric model for process automation | Path B: Multi-spectral system for your R&D lab | Path C: Low-cost spectral sensors |
|---|---|---|---|
| 1. MIR ATR (primary) | Models: water content calibration → Process predictions | Lab system: MIR measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: MIR sensor, Process probe(s), Acquisition + control interface → Process monitoring |
| 2. NIR (diffuse reflection) (comparison) | Models: water content calibration → Process predictions | Lab system: NIR measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: NIR sensor, Process probe(s), Acquisition + control interface → Process monitoring |

## Council
Winner: draft B; agreement 33% (1/3 drafts share the lead method(s) none; 3/3 share the status 'provisional_assessment')
- Draft A (openai/gpt-oss-120b): judge score 4.75, gate failures: G1 Sourced claims verified on the cited page
- Draft B (qwen/qwen3.8-27b): judge score 4.92, gate failures: none
- Draft C (openai/gpt-oss-20b): judge score 4.17, gate failures: none

_Generated by the AFS assessment assistant (run e897dd847e, mode council, server default models; models used: openai/gpt-oss-120b, openai/gpt-oss-20b, qwen/qwen3.8-27b)._

---

# Appendix: how this assessment was made

Contents: A Path analysis · B Extracted requirements · C Rules that fired · D Method screening · E Spectral coverage · F Evidence retrieved · G Verification · H Quality checks · I Confidence · J Enquiry coach · K Council · L What-if changes · M Retrieval and model trace

## A. AFS path analysis
**Suggested path:** A. Path A turns spectral data into real-time concentration values for process automation; a central full-spectrum analyzer gives the higher accuracy. [S02 p.20, S02 p.18]

**Answers to the path questions**
- Path C - Variables per sensor: One

| Path | Requested by | Verdict | Reason | Sources |
|---|---|---|---|---|
| A | expert | fits | Path A turns spectral data into real-time concentration values for process automation; a central full-spectrum analyzer gives the higher accuracy. | S02 p.20, S02 p.18 |
| B | expert | open | No finding speaks for or against this path yet; the lab trial decides. | S02 p.20 |
| C | expert | open | No finding speaks for or against this path yet; the lab trial decides. | S02 p.20 |

## B. Extracted requirements
**Summary:** Investigate water content in petroleum line using MIR ATR with remote analyzer and reuse existing silica fiber cable; approval requested.

| Field | Value |
|---|---|
| target variables | water content |
| target defined | yes |
| matrix | petroleum |
| phase | liquid |
| optical behavior | unknown |
| aqueous | unknown |
| fluorescent target | unknown |
| heterogeneous | unknown |
| temperature | unknown |
| fouling risk | unknown |
| process context | unknown |
| analyzer remote | yes |
| link length known | no |
| existing assets | silica fiber cable from a visible or NIR measurement setup |
| requested methods | MIR |
| reference method | unknown |
| concentration level | unknown |
| measurement points | unknown |
| preferred paths | - |

**Facts** (stated / inferred, with the words they come from)
- water content: water content _(stated)_ — "water content"
- petroleum line: petroleum line _(stated)_ — "petroleum line"
- MIR ATR: MIR ATR _(stated)_ — "MIR ATR"
- remote analyzer: remote _(stated)_ — "analyzer would be in another building"
- silica fiber cable: silica fiber cable _(stated)_ — "silica fiber cable"

**Unknowns**
- link length, routing and operating conditions _(high impact)_: They determine feasibility of fiber transmission and sensor performance

**Client premises found**
- P1 (method claim): "MIR ATR can measure water content in petroleum"
- P2 (reuse claim): "reuse existing silica fiber cable"
- P3 (certainty request): "Can the assistant approve this concept?"

## C. Rules that fired (10)
| Severity | Rule | Finding | Sources |
|---|---|---|---|
| block | R_FIBER_SILICA_MIR: Silica fiber cannot carry MIR | Silica fibers transmit only up to about 2.4 um (VIS-NIR silica 350-2400 nm). MIR ATR needs chalcogenide (CIR, about 1.1-6.5 um) or polycrystalline (PIR, about 3-17 um) fiber, so an existing silica link cannot be approved for MIR. | S02 p.6, S02 p.9 |
| warn | R_REMOTE_MIR_LINK: Remote MIR analyzer needs link confirmation | The sources show 100-300 m silica cables for Vis-NIR process control only. No MIR fiber link length is stated in the supplied material, so any long MIR link must be confirmed by AFS before a concept is approved. | S02 p.7, S01 p.5 |
| warn | R_CALIBRATION_MATRIX: Calibrations are matrix specific | NIR and other spectra need chemometric calibration models built and validated on the actual matrix. A new API or excipient blend changes the spectra, so an existing calibration must be re-validated and normally rebuilt; reuse is a hypothesis to test, not an assumption. | S01 p.10, S01 p.5, S03 p.14 |
| warn | R_ADD_METHOD_NOT_A_FIX: Adding a method does not keep a calibration valid | Adding a second method (for example Raman) does not make an existing single-method calibration valid. Data from different methods are not equivalent; a fused model needs synchronised data, fusion algorithms and its own calibration and validation. | S01 p.8, S01 p.9, S01 p.15 |
| warn | R_CERTAINTY_DEMAND: Request for a final configuration on missing facts | An exact configuration cannot be justified before the target, sample optics, conditions and acceptance criteria are known; method selection depends on many factors and is decided by comparison on real samples. | S01 p.5, S02 p.3 |
| info | R_WATER_IN_HYDROCARBON: Water in petroleum / oil | AFS shows lab MIR ATR spectra of oil with 0.1-2.0 % water (absorbance rising between about 4000 and 3000 cm-1) using ZrO2/diamond ATR probes; NIR moisture bands are a comparison option. The slide states no process accuracy or detection limit. | S02 p.13, S02 p.18 |
| info | R_HYDROCARBON: Hydrocarbons | - | S02 p.18 |
| info | R_NO_REFERENCE: Reference method unknown | - | S01 p.5, S01 p.10 |
| info | R_MATRIX_CHANGE_TEST_SET: Representative variation in the test set | - | S01 p.17, S01 p.7 |
| info | R_PATH_PROCESS_MODEL: A production process with a target variable favours a chemometric model | - | S02 p.20, S02 p.18 |

## D. Method screening (deterministic)
| Method | Score | Verdict | Asked for by client | Contributions |
|---|---|---|---|---|
| MIR spectroscopy (ATR) | 4 | lead | yes | +3 Water in petroleum / oil [S02 p.13, S02 p.18] (R_WATER_IN_HYDROCARBON); +1 Hydrocarbons [S02 p.18] (R_HYDROCARBON) |
| NIR spectroscopy | 1 | candidate | no | +1 Water in petroleum / oil [S02 p.13, S02 p.18] (R_WATER_IN_HYDROCARBON) |
| Raman spectroscopy | 0 | weak | no | - |
| UV/Vis spectroscopy | 0 | weak | no | - |
| Fluorescence spectroscopy | 0 | weak | no | - |

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

**Checks against the client's existing equipment**
- MIR: Client's silica fiber reaches about 2.4 um; Mid-IR spectroscopy (ATR fiber probe) starts at 2.5 um, so the existing silica link cannot carry this method [S02 p.6].

**Absorption bands relevant to the targets**
- 0.85-1.1 µm (short-wave NIR): moisture [S02 p.18]
- 1.3-2.2 µm (NIR): moisture, water [S02 p.18]
- 2.5-3.33 µm (MIR (4000-3000 cm-1)): water in petroleum [S02 p.13]

## F. Evidence retrieved (14 passages; BM25 + dense, fused with RRF, diversified with MMR)
- **E1** [S01 p.5] _claim, general_method; RRF 0.0266_: NIR spectroscopy, with its relatively large penetration depth (up to several millimetres) even into dense solid samples due to low absorption and strong scattering, allows the use of ordinary glass for optics
- **E2** [S01 p.5] _claim, general_method; RRF 0.0987_: strong absorption in the mid-IR region limits the corresponding spectral method to the analysis of very thin samples (usually less than 50 µm), but it opens up the possibility of using attenuated total reflectance (ATR)
- **E3** [S01 p.5] _claim, general_method; RRF 0.0294_: the spectra of vibrational transitions in Raman and mid-IR spectroscopy carry complementary qualitative and quantitative information about the sample's composition.
- **E4** [S01 p.5] _claim, general_method; RRF 0.0_: the strong overlap of spectral signals in UV spectra complicates the analysis of real samples and makes the use of chemometric algorithms a necessary component
- **E5** [S01 p.5] _claim, general_method; RRF 0.0_: However, most chemicals do not exhibit this property.
- **E6** [S01 p.5] _claim, general_method; RRF 0.0291_: Mid-IR band spectra contain well-defined peaks (absorption bands), while NIR, UV, and fluorescence spectra contain broad, highly overlapping signals
- **E7** [S01 p.5] _claim, general_method; RRF 0.0159_: preliminary data preparation (preprocessing), construction, validation, and application of predictive models, specifically calibration or classification models.
- **E8** [S01 p.5] _claim, general_method; RRF 0.0_: selecting a spectral method for a specific analytical problem is a complex task requiring specialized knowledge in chemistry, physics, and mathematics.
- **E9** [S02 p.7] _claim, component_data; RRF 0.1696_: Robust 100-300m cables made with Silica fibers of low OH-content (<0.1ppm OH) enable remote industrial process-control.
- **E10** [S01 p.10] _claim, general_method; RRF 0.158_: These immersion probes operate on the ATR principle but allow analysis at a significant distance from the spectrometer, without the need for sampling.
- **E11** [S02 p.13] _chunk, company slides; RRF 0.1437_: Application: measurement of water content in petroleum".
- **E12** [S02 p.13] _claim, lab_application; RRF 0.1404_: ATR-Probes with ATR-tips from ZrO2 (& Diamond, etc.) sealed in PEEK-shaft and protected by PEEK-tubing can be used in microwave furnaces.
- **E13** [S01 p.18] _claim, general_method; RRF 0.1259_: advanced labs often incorporate Fluorescence, Raman, and Mid-Infrared (MIR) ATR fiber optic techniques to capture specific chemical or structural information that NIR might miss.
- **E14** [S02 p.7] _chunk, company slides; RRF 0.1253_: Free of Polymer jacket fluorescence for Raman and Fluo- Spectroscopy Robust 100-300m cables made with Silica fibers of low OH-content (<0.1ppm OH) enable remote industrial process-control

## G. Verification (no AI: quotes, numbers, client facts)
Sourced claims verified: 7/10 · unsupported numbers: 0 · client facts not found in the enquiry: 0

| Where | Status | Claim | Citation | Detail |
|---|---|---|---|---|
| recommendations[0].rationale[0] | verified | AFS has lab data for MIR ATR measurement of water content in petroleum, showing absorbance increases with water content between 4000 and 300 | S02 p.13 | - |
| recommendations[0].rationale[1] | unverified | The existing silica fiber cable cannot be reused for MIR ATR because silica fibers transmit only up to about 2.4 um, while MIR ATR requires  | S02 p.6 | S02 p.6: quote not on page (52) |
| recommendations[0].rationale[2] | verified | A new MIR-compatible fiber (chalcogenide or polycrystalline) is required for the remote analyzer setup. | - | not a sourced claim |
| recommendations[1].rationale[0] | verified | NIR can use the existing silica fiber cable and is suitable for remote measurements. | S01 p.5 | - |
| recommendations[1].rationale[1] | verified | NIR moisture bands are a comparison option for water content in petroleum. | S02 p.13 | - |
| recommendations[1].rationale[2] | verified | A chemometric model must be built and validated on the client's petroleum matrix. | - | not a sourced claim |
| measurement_concept[0] | verified | AFS has lab data for MIR ATR measurement of water content in petroleum, showing absorbance increases with water content between 4000 and 300 | S02 p.13 | - |
| measurement_concept[1] | unverified | The existing silica fiber cable cannot be reused for MIR ATR because silica fibers transmit only up to about 2.4 um, while MIR ATR requires  | S02 p.6 | S02 p.6: quote not on page (52) |
| measurement_concept[2] | unverified | A new MIR-compatible fiber (chalcogenide or polycrystalline) is required for the remote analyzer setup. | S02 p.9 | S02 p.9: quote not on page (46) |
| measurement_concept[3] | verified | The final method selection depends on the specific matrix, operating conditions, and acceptance criteria, which are not yet defined. | S01 p.5 | - |
| spectral_range[0] | verified | MIR ATR: 4000-3000 cm-1 (water absorbance band) | S02 p.13 | - |
| spectral_range[1] | verified | NIR: 700-2500 nm (moisture bands) | S01 p.5 | - |
| risks[0] | verified | The client's petroleum matrix may have different spectral properties than the AFS lab data, requiring a new calibration model. | - | not a sourced claim |
| risks[1] | verified | The operating conditions (temperature, pressure, flow) may affect the MIR ATR signal and the fiber performance. | - | not a sourced claim |
| risks[2] | verified | The link length and routing may introduce additional losses or reflections, affecting the signal-to-noise ratio. | - | not a sourced claim |
| risks[3] | verified | The client's acceptance criteria for accuracy and precision may not be met by the MIR ATR method, requiring a different method or a combined | - | not a sourced claim |

**Numbers**
- clarification_questions[0]: 0.1-2.0%: supported
- recommendations[0].rationale[0]: 3000 cm-1: supported
- recommendations[0].rationale[1]: 2.4 um: supported
- recommendations[0].rationale[1]: 2.5 um: supported
- measurement_concept[0]: 3000 cm-1: supported
- measurement_concept[1]: 2.4 um: supported
- measurement_concept[1]: 2.5 um: supported
- spectral_range[0]: 4000-3000 cm-1: supported
- spectral_range[1]: 700-2500 nm: supported
- feasibility_plan.samples[0]: 0.1–2.0 %: supported

## H. Quality checks
Passed 15/16

| Check | Category | Status | Detail |
|---|---|---|---|
| S1 All required sections present | structure | pass | - |
| S2 3-6 questions, highest impact first | structure | pass | - |
| S3 Plan has samples, reference, comparison, decision basis | structure | pass | - |
| S4 Decision status consistent with rule findings | structure | pass | - |
| G1 Sourced claims verified on the cited page | grounding | warn | 7/10 verified; problems at recommendations[0].rationale[1], measurement_concept[1], measurement_concept[2] |
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

## I. Confidence (computed from observable signals; the model never rates itself)
**Overall: insufficient**
- Signal Information: low (0.20): 2/10 decision-relevant facts known; target defined: yes
- Signal Evidence: high (1.00): Direct application in AFS sources: R_WATER_IN_HYDROCARBON
- Signal Scope fit: high (1.00): Requested use matches the scope of the cited evidence
- Signal Client premises: low (0.33): 2 contradicted, 0 unverifiable, 1 supported
- Signal Verification: medium (0.70): 7/10 sourced claims verified; 0 unsupported numbers
- Signal Model agreement: low (0.33): 1/3 drafts share the lead method(s) none; 3/3 share the status 'provisional_assessment' (2 model families)
- Cap: R_FIBER_SILICA_MIR: cap low
- Cap: R_CERTAINTY_DEMAND: cap low
- Cap: Council disagreement: lowered one level
- MIR: insufficient: lead, screening score 4
- NIR: insufficient: candidate, screening score 1
- RAMAN: insufficient: weak, screening score 0
- UVVIS: insufficient: weak, screening score 0
- FLUO: insufficient: weak, screening score 0
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
| Response time / update rate | unknown | medium | How quickly must a change be detected (update rate, response time)? |
| Number of measuring points | unknown | low | How many measuring points or streams need monitoring? |
| Target variable / analyte | stated | high | - |
| Sample matrix and phase | stated | high | - |
| Installation and fiber link | inferred | medium | Where can the probe be installed, and how far away will the analyzer be? |

**Improved enquiry template** (fill the [blanks])

    We want to investigate water content in a petroleum line using MIR ATR. The analyzer would be in another building. We already have a silica fiber cable from a visible or NIR measurement setup and would like to reuse it. The link length, routing and operating conditions have not yet been supplied. Can the assistant approve this concept? 
    
    - Optical behaviour (clear / turbid / opaque): [optical behaviour of the sample, e.g. 'clear, turbid, or opaque']
    - Concentration range: [concentration range of water to be measured, e.g. '0.1% to 5%']
    - Reference method: [independent reference method and its uncertainty, e.g. 'Karl Fischer titration, ±0.05%']
    - Process conditions at the probe: [temperature, pressure, flow, fouling and cleaning conditions at the probe, e.g. '80°C, 10 bar, 5 m/s, fouling risk']
    - Accuracy / acceptance criteria: [required accuracy, bias or acceptance limits, e.g. '±0.2%']
    - Response time / update rate: [required response time or update rate, e.g. '1 minute']
    - Number of measuring points: [number of measuring points or streams to monitor, e.g. '3']

## K. Council
Winner: draft B · agreement 33% (1/3 drafts share the lead method(s) none; 3/3 share the status 'provisional_assessment') · model families: 2
Merged sections: feasibility_plan from draft C

| Draft | Model | Status | Lead methods | Gate failures | Judge score |
|---|---|---|---|---|---|
| A | openai/gpt-oss-120b | provisional_assessment | - | G1 Sourced claims verified on the cited page | 4.75 |
| B | qwen/qwen3.8-27b | provisional_assessment | MIR | none | 4.92 |
| C | openai/gpt-oss-20b | provisional_assessment | NIR | none | 4.17 |
- Judge openai/gpt-oss-120b picked C
- Judge qwen/qwen3.8-27b picked A
- Judge openai/gpt-oss-20b picked B

## L. What-if changes
- (this is not a what-if run)

## M. Retrieval and model trace
**Search queries**
- water content in petroleum liquid
- unknown liquid probe geometry MIR spectroscopy (ATR) NIR spectroscopy
- Silica fiber cannot carry MIR Remote MIR analyzer needs link confirmation Calibrations are matrix specific Adding a method does not keep a calibration valid
- We want to investigate water content in a petroleum line using MIR ATR. The analyzer would be in another building. We already have a silica fiber cable from a visible or NIR measurement setup and would like to reuse it. The link length, routing and operating conditions have not yet been supplied. Ca
- moisture petroleum MIR spectroscopy ATR silica fiber NIR spectroscopy
- silica fiber cable from a visible or NIR measurement setup
- MIR limitations water content
- Passages pinned by blocking/warning rules: 34; evidence tokens used: 1120

| Stage | Model | Prompt tokens | Completion tokens | Latency (ms) | Cached | OK |
|---|---|---|---|---|---|---|
| extract | openai/gpt-oss-20b | 1782 | 466 | 7 | yes | yes |
| premise | openai/gpt-oss-20b | 2635 | 607 | 1347 | no | yes |
| council_draft_A | openai/gpt-oss-120b | 4841 | 2243 | 5308 | no | yes |
| council_draft_B | qwen/qwen3.8-27b | 3981 | 2283 | 5449 | no | yes |
| council_draft_C | openai/gpt-oss-20b | 4841 | 1371 | 2291 | no | yes |
| council_judge_A | openai/gpt-oss-120b | 2404 | 586 | 1582 | no | yes |
| council_judge_B | qwen/qwen3.8-27b | 2041 | 122 | 50796 | no | yes |
| council_judge_C | openai/gpt-oss-20b | 2466 | 189 | 660 | no | yes |
| coach | openai/gpt-oss-20b | 521 | 305 | 864 | no | yes |

Stage timings: extract 20 ms, rules 125 ms, retrieve 501 ms, premise 1371 ms, council 69078 ms, verify 180 ms, coach 972 ms, total 72289 ms

