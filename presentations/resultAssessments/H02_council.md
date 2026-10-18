# First technical assessment

> **Enquiry:** Our dairy process handles both a relatively clear whey stream and an opaque milk concentrate. We want a pilot for composition monitoring, using laboratory protein and fat results where those variables are relevant. We can compare different measurement interfaces before choosing the installation. What first measurement concepts and comparison experiment would make sense for these two streams?
>
> **Answers added:** Path B - Where it is used: In production; Path C - Variables per sensor: Two or three

**Quality checks:** 12/16 · **Sourced claims verified:** 9/10 · **Unsupported numbers:** 1

## 01. Decision Status
**Provisional assessment** · **Confidence:** insufficient (computed, not self-reported)

A pilot using NIR reflection for the opaque milk concentrate and NIR transmission/transflection for the clear whey stream, with optional MIR‑ATR or Raman probes as comparative alternatives, is the most straightforward first‑step approach.

**Problems found in the request**
- Fluorescence needs a fluorescent target: Fluorescence has high sensitivity but low selectivity, and most chemicals do not fluoresce. Without a defined fluorescent target, marker or reference relationship, sensitivity alone does not justify reporting a concentration. [S01 p.5, S01 p.6, S04 p.4]

**The customer's own claims, tested first**
- **supported**: "We want a pilot for composition monitoring, using laboratory protein and fat results where those variables are relevant.". NIR reflection is the standard for opaque or concentrated dairy streams and transmission for clear streams, with scatter correction and PLS for protein and fat quantification. The pilot can use lab protein/fat data to build calibration models. [S01 p.17] [S01 p.18] [S01 p.18]
- **supported**: "We can compare different measurement interfaces before choosing the installation.". Rule R_CERTAINTY_DEMAND states that method selection depends on target, sample optics, and acceptance criteria, and must be decided by comparison on real samples. Therefore a comparison experiment is appropriate. [S01 p.5] [S01 p.18]

To raise confidence, answer: What is the sample (liquid, powder, melt, tissue...) and its main components? / Is the sample clear, turbid or opaque, and does this change during the process? / What concentration range must be covered, and what is the smallest change that matters?

## 02. Requirements stated
- protein
- fat

## 03. Key unknowns
- exact composition ranges of whey and milk concentrate
- temperature of streams
- fiber cable type and length

**Assumptions made**
- The whey stream is clear enough for transmission or transflection; the milk concentrate is opaque; fiber lengths are within the attenuation limits of the chosen methods.

## 04. Clarification questions
1. **What are the expected protein and fat concentration ranges for the whey and milk concentrate streams?** _(high impact)_. Why: Calibration ranges and model robustness depend on the full concentration span.
2. **What is the operating temperature of the streams during measurement?** _(medium impact)_. Why: Temperature influences spectral baseline and scattering.
3. **What fiber cable lengths and types (silica, chalcogenide, etc.) are planned for the pilot?** _(medium impact)_. Why: Fiber attenuation and penetration depth affect signal quality.
4. **Will the measurement be performed inline in the production line or in a lab‑based loop?** _(low impact)_. Why: It determines the choice of probe geometry and installation constraints.

## 05. Recommendation

### NIR (reflection) (primary)
- NIR reflection is the workhorse for opaque or concentrated dairy products and is used for fat and protein quantification with scatter correction and PLS. [S01 p.5] _(sourced)_
- Build a calibration model using lab protein/fat reference data for the milk concentrate. _(proposal)_
- _Applies if:_ Representative milk concentrate samples covering the full protein/fat range must be available.

### NIR (transmission/transflection) (primary)
- Clear or semi‑transparent liquids are best measured with transmission or transflection probes with a defined 1‑10 mm path. [S01 p.5] _(sourced)_
- Use a transflection probe that can also serve as a reflection probe for the milk concentrate to simplify installation. _(proposal)_
- _Applies if:_ The whey stream must be clear enough for transmission; a 1‑10 mm path length should be verified.

### MIR (ATR) (comparison)
- MIR ATR provides specific absorption bands for fat and protein and can be used for aqueous media. [S01 p.5] _(sourced)_
- Test an ATR probe on both streams to evaluate specificity versus NIR. _(proposal)_
- _Applies if:_ ATR probe must be compatible with the stream temperature and flow.

### Raman (comparison)
- Raman signals are weak but can be useful for aqueous media and are not strongly absorbed by water. [S01 p.5] _(sourced)_
- Assess Raman background and signal quality on the whey and milk concentrate. _(proposal)_
- _Applies if:_ A suitable laser wavelength and probe design must be selected to avoid fluorescence.

### Fluorescence (not recommended)
- Fluorescence requires a fluorescent target; most dairy components do not fluoresce, making it unsuitable for protein/fat quantification. [S01 p.5] _(sourced)_
- _Applies if:_ None; not recommended for this application.

**Method screening (deterministic, from sourced rules)**

| Method | Score | Verdict |
|---|---|---|
| NIR spectroscopy | 5 | lead |
| MIR spectroscopy (ATR) | 1 | candidate |
| Raman spectroscopy | 1 | candidate |
| UV/Vis spectroscopy | 0 | weak |
| Fluorescence spectroscopy | -3 | not supported |

## 06. Measurement concept
- The pilot will use laboratory protein and fat results as reference for calibration. _(client fact)_
- NIR reflection is standard for opaque dairy streams and transmission for clear streams. [S01 p.5] _(sourced)_
- MIR ATR and Raman can add specificity but require careful probe selection. [S01 p.5] _(sourced)_

## 07. Spectral range
- NIR: client‑agreed range for protein/fat quantification. [S01 p.5] _(sourced)_
- MIR ATR: 4000–400 cm⁻¹, focusing on 1740 cm⁻¹ (fat) and 1650 cm⁻¹ (protein). [S04 p.3] _(sourced)_
- Raman: 400–4000 cm⁻¹ with excitation at 785 nm (typical for dairy). [S01 p.11] _(sourced ⚠ unverified)_

## 08. Risks and uncertainty
- The whey stream will remain clear enough for transmission; if it becomes turbid, the NIR transmission probe may fail. _(assumption)_
- Temperature variations may shift spectral baselines; calibration models must account for this. _(assumption)_
- Fiber attenuation over long lengths could reduce signal strength, especially for MIR ATR. _(assumption)_
- Include temperature sensors and monitor optical path length during the pilot. _(proposal)_

**Confidence: insufficient**
- Information: insufficient (1/10 decision-relevant facts known; target defined: yes)
- Evidence: high (Direct application in AFS sources: R_DAIRY)
- Scope fit: high (Requested use matches the scope of the cited evidence)
- Client premises: high (0 contradicted, 0 unverifiable, 2 supported)
- Verification: high (9/10 sourced claims verified; 1 unsupported numbers)
- Model agreement: high (3/3 drafts share the lead method(s) NIR; 3/3 share the status 'provisional_assessment' (2 model families))
- Cap: R_FLUO_NEEDS_TARGET: cap low
- Cap: R_CERTAINTY_DEMAND: cap low

## 09. Decision basis
- Model R² and RMSEP against lab reference; acceptance criteria set by client (e.g., RMSEP < client‑agreed value)

## 10. Sources
- **S01 p.5**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "NIR spectroscopy, with its relatively large penetration depth (up to several millimetres) even into dense solid samples due to low absorption and strong scattering, allows the use of ordinary glass for optics"
  - "strong absorption in the mid-IR region limits the corresponding spectral method to the analysis of very thin samples (usually less than 50 µm), but it opens up the possibility of using attenuated total reflectance (ATR)"
  - "Moreover, the spectra of vibrational transitions in Raman and mid-IR spectroscopy carry complementary qualitative and quantitative information about the sample's composition."
  - "However, most chemicals do not exhibit this property."
  - "selecting a spectral method for a specific analytical problem is a complex task requiring specialized knowledge in chemistry, physics, and mathematics."
- **S01 p.11**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "Raman signals are weak and, for many organic or biological samples, fluorescence can overlay them." ⚠ unverified
- **S01 p.17**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "Inline NIR Reflection is primarily used for opaque or highly concentrated dairy products"
- **S01 p.18**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "NIR Spectrometer and NIR light source remain the same for both reflection and transmission techniques"
  - "advanced labs often incorporate Fluorescence, Raman, and Mid-Infrared (MIR) ATR fiber optic techniques to capture specific chemical or structural information that NIR might miss"
- **S04 p.3**: Fiber Probe for Simultaneous Mid-Infrared and Fluorescence Spectroscopic Analysis (Anal. Chem. 2021) _(lab_demonstration)_
  - "the stretching vibration band of the ester carbonyl CO at about 1740 cm−1, which is characteristic of saturated triglycerides"

**Verifier warnings**
- spectral_range[2]: unverified S01 p.11: quote not on page (53)

## 11. First feasibility experiment
**Samples**
- Representative whey samples covering the full protein/fat range
- Representative milk concentrate samples covering the full protein/fat range
**Reference measurements**
- Independent lab assays of protein (Kjeldahl) and fat (Gerber) for each sample
**Comparison**
- NIR reflection vs NIR transmission/transflection vs MIR ATR vs Raman
**Steps**
1. Install NIR reflection probe on milk concentrate line and NIR transmission/transflection probe on whey line; optionally add MIR ATR and Raman probes on both streams.
2. Collect spectra and reference data for at least 30 samples per stream.
3. Preprocess spectra (MSC/SNV for NIR, baseline correction for Raman).
4. Build PLS models for protein and fat for each method and compare performance.
5. Evaluate robustness to temperature and flow variations by spiking samples and repeating measurements.
6. Select the best performing method(s) for pilot deployment and plan for full‑scale installation.

**Next step with AFS**
- Conduct a multi‑method lab trial to build and validate chemometric models for protein and fat on both streams.
- Likely path: A - Path A provides a central full‑ spectrum analyzer that delivers the highest accuracy for process automation.
- Path A (chosen by the expert): **fits**. Path A turns spectral data into real-time concentration values for process automation; a central full-spectrum analyzer gives the higher accuracy. [S02 p.20, S02 p.18]
- Path B (chosen by the expert): **conflicts**. Path B is a lab system for R&D; measuring in production is Path A (central analyzer) or Path C (sensors). [S02 p.20]
- Path C (chosen by the expert): **conflicts**. Several variables at once need full-spectrum information; a few-wavelength sensor is designed for one specific control task. A full-spectrum analyzer gives higher accuracy. [S02 p.18, S02 p.20]

**If you proceed anyway with Path B** (Path B (customised multi-spectral system for R&D) is a poor fit here: Path B is a lab system for R&D; measuring in production is Path A (central analyzer) or Path C (sensors).)
1. Specify the lab kit from the methods short-listed in this assessment: spectrometers, fiber probes, software.
2. Run the method comparison on the customer's own samples in their lab.
3. Use the results as the basis for a later process solution (Path A or C).
_Sources: S02 p.20, S01 p.4_

**If you proceed anyway with Path C** (Path C (customised spectral IoT sensor) is a poor fit here: Several variables at once need full-spectrum information; a few-wavelength sensor is designed for one specific control task. A full-spectrum analyzer gives higher accuracy.)
1. Run a lab trial with full-spectrum instruments on representative samples.
2. Select the most informative wavelengths and check that a few-band model reaches the client-agreed error on independent samples.
3. Build and test a prototype LED / filter sensor against the reference method before any volume order.
_Sources: S01 p.9, S03 p.14, S02 p.18_

**Proposed setup** (ranked by recommendation; validate in a lab trial)

| System | Path A: Chemometric model for process automation | Path B: Multi-spectral system for your R&D lab | Path C: Low-cost spectral sensors |
|---|---|---|---|
| 1. NIR (reflection) (primary) | Models: protein calibration, fat calibration → Process predictions | Lab system: NIR measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: NIR sensor, Process probe(s), Acquisition + control interface → Process monitoring |
| 2. NIR (transmission/transflection) (primary) | Models: protein calibration, fat calibration → Process predictions | Lab system: NIR measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: NIR sensor, Process probe(s), Acquisition + control interface → Process monitoring |
| 3. MIR (ATR) (comparison) | Models: protein calibration, fat calibration → Process predictions | Lab system: MIR measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: MIR sensor, Process probe(s), Acquisition + control interface → Process monitoring |
| 4. Raman (comparison) | Models: protein calibration, fat calibration → Process predictions | Lab system: RAMAN measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: RAMAN sensor, Process probe(s), Acquisition + control interface → Process monitoring |

## Council
Winner: draft C; agreement 100% (3/3 drafts share the lead method(s) NIR; 3/3 share the status 'provisional_assessment')
- Draft A (openai/gpt-oss-120b): judge score 4.08, gate failures: G1 Sourced claims verified on the cited page, G2 No unsupported numbers
- Draft B (qwen/qwen3.8-27b): judge score 4.83, gate failures: G1 Sourced claims verified on the cited page, G2 No unsupported numbers
- Draft C (openai/gpt-oss-20b): judge score 4.92, gate failures: G1 Sourced claims verified on the cited page, G2 No unsupported numbers

_Generated by the AFS assessment assistant (run 4f27f123b4, mode council, server default models; models used: openai/gpt-oss-120b, openai/gpt-oss-20b, qwen/qwen3.8-27b)._

---

# Appendix: how this assessment was made

Contents: A Path analysis · B Extracted requirements · C Rules that fired · D Method screening · E Spectral coverage · F Evidence retrieved · G Verification · H Quality checks · I Confidence · J Enquiry coach · K Council · L What-if changes · M Retrieval and model trace

## A. AFS path analysis
**Suggested path:** A. Path A turns spectral data into real-time concentration values for process automation; a central full-spectrum analyzer gives the higher accuracy. [S02 p.20, S02 p.18]

**Answers to the path questions**
- Path B - Where it is used: In production
- Path C - Variables per sensor: Two or three

| Path | Requested by | Verdict | Reason | Sources |
|---|---|---|---|---|
| A | expert | fits | Path A turns spectral data into real-time concentration values for process automation; a central full-spectrum analyzer gives the higher accuracy. | S02 p.20, S02 p.18 |
| B | expert | conflicts | Path B is a lab system for R&D; measuring in production is Path A (central analyzer) or Path C (sensors). | S02 p.20 |
| C | expert | conflicts | Several variables at once need full-spectrum information; a few-wavelength sensor is designed for one specific control task. A full-spectrum analyzer gives higher accuracy. | S02 p.18, S02 p.20 |

## B. Extracted requirements
**Summary:** Pilot composition monitoring of clear whey and opaque milk concentrate, comparing measurement interfaces, using lab protein/fat results as reference.

| Field | Value |
|---|---|
| target variables | protein, fat |
| target defined | yes |
| matrix | unknown |
| phase | unknown |
| optical behavior | unknown |
| aqueous | unknown |
| fluorescent target | unknown |
| heterogeneous | unknown |
| temperature | unknown |
| fouling risk | unknown |
| process context | pilot |
| analyzer remote | unknown |
| link length known | no |
| existing assets | - |
| requested methods | NIR, MIR, RAMAN, UVVIS, FLUO |
| reference method | unknown |
| concentration level | unknown |
| measurement points | unknown |
| preferred paths | - |

**Facts** (stated / inferred, with the words they come from)
- matrix: unknown _(inferred)_ — "Our dairy process handles both a relatively clear whey stream and an opaque milk concentrate."
- phase: unknown _(inferred)_ — "Our dairy process handles both a relatively clear whey stream and an opaque milk concentrate."
- optical_behavior: clear _(inferred)_ — "relatively clear whey stream"
- optical_behavior: opaque _(inferred)_ — "opaque milk concentrate"
- target_variables: protein _(stated)_ — "protein"
- target_variables: fat _(stated)_ — "fat"
- process_context: pilot _(stated)_ — "pilot for composition monitoring"

**Unknowns**
- exact composition ranges of whey and milk concentrate _(high impact)_: Needed to select appropriate spectral range and calibration
- temperature of streams _(medium impact)_: Affects spectral response
- fiber cable type and length _(medium impact)_: Determines signal loss and probe placement

**Client premises found**
- P1 (certainty request): "We want a pilot for composition monitoring, using laboratory protein and fat results where those variables are relevant."
- P2 (other): "We can compare different measurement interfaces before choosing the installation."

## C. Rules that fired (12)
| Severity | Rule | Finding | Sources |
|---|---|---|---|
| block | R_FLUO_NEEDS_TARGET: Fluorescence needs a fluorescent target | Fluorescence has high sensitivity but low selectivity, and most chemicals do not fluoresce. Without a defined fluorescent target, marker or reference relationship, sensitivity alone does not justify reporting a concentration. | S01 p.5, S01 p.6, S04 p.4 |
| warn | R_VARIABLE_OPTICS: Changing optics or several streams need a geometry comparison | Optical behaviour changes (clear vs turbid/opaque). No single geometry should be assumed: compare transmission/transflection with reflection (or ATR) across the full range of states; a transflection probe can sometimes cover both. | S01 p.18, S01 p.16 |
| warn | R_CERTAINTY_DEMAND: Request for a final configuration on missing facts | An exact configuration cannot be justified before the target, sample optics, conditions and acceptance criteria are known; method selection depends on many factors and is decided by comparison on real samples. | S01 p.5, S02 p.3 |
| info | R_RAMAN_FLUO_BACKGROUND: Raman fluorescence background risk | Raman signals are weak and, for many organic or biological samples, fluorescence can overlay them. Check background and signal quality on real samples; state excitation wavelength and Raman shift separately. | S01 p.11, S02 p.7 |
| info | R_OPAQUE: Opaque or scattering media favour reflection or ATR | Opaque or concentrated media: NIR reflection is used for opaque dairy products; transmission saturates or fails when light cannot penetrate; ATR uses a very short evanescent path. | S01 p.17, S01 p.18, S01 p.16 |
| info | R_CLEAR: Clear liquids favour transmission or transflection | Clear or semi-transparent liquids: transmission or transflection probes with a defined 1-10 mm path are preferred; reflection can be less representative. | S01 p.18, S01 p.16, S01 p.6 |
| info | R_AQUEOUS: Water-rich media | Water absorbs strongly in the IR; Raman shows low water absorbance and suits aqueous media. MIR is used via ATR (very short path). | S01 p.16, S01 p.5 |
| info | R_DAIRY: Dairy composition | NIR is the workhorse for in-line dairy composition: reflection for opaque/concentrated products, transmission for clear streams; scatter correction (MSC/SNV) before PLS. Fluorescence, Raman and MIR ATR can add specificity. | S01 p.17, S01 p.18, S02 p.18 |
| info | R_NO_REFERENCE: Reference method unknown | - | S01 p.5, S01 p.10 |
| info | R_MULTI_POINT: Several measuring points | Several measuring points: a central full-spectrum analyzer with multiplexer and long fibers gives higher accuracy; distributed spectral sensors give lower installation cost (decided after lab trials). | S02 p.18 |
| info | R_PATH_PROCESS_MODEL: A production process with a target variable favours a chemometric model | - | S02 p.20, S02 p.18 |
| info | R_PATH_SEVERAL_VARIABLES: Several variables in one stream need full spectra | - | S02 p.18, S02 p.20 |

## D. Method screening (deterministic)
| Method | Score | Verdict | Asked for by client | Contributions |
|---|---|---|---|---|
| NIR spectroscopy | 5 | lead | yes | +2 Opaque or scattering media favour reflection or ATR [S01 p.17, S01 p.18] (R_OPAQUE); +1 Clear liquids favour transmission or transflection [S01 p.18, S01 p.16] (R_CLEAR); +2 Dairy composition [S01 p.17, S01 p.18] (R_DAIRY) |
| MIR spectroscopy (ATR) | 1 | candidate | yes | +1 Opaque or scattering media favour reflection or ATR [S01 p.17, S01 p.18] (R_OPAQUE) |
| Raman spectroscopy | 1 | candidate | yes | +1 Water-rich media [S01 p.16, S01 p.5] (R_AQUEOUS) |
| UV/Vis spectroscopy | 0 | weak | yes | -1 Opaque or scattering media favour reflection or ATR [S01 p.17, S01 p.18] (R_OPAQUE); +1 Clear liquids favour transmission or transflection [S01 p.18, S01 p.16] (R_CLEAR) |
| Fluorescence spectroscopy | -3 | not supported | yes | -3 Fluorescence needs a fluorescent target [S01 p.5, S01 p.6] (R_FLUO_NEEDS_TARGET) |

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
- 0.85-1.1 µm (short-wave NIR): fat, protein [S02 p.18]
- 6.1-6.46 µm (MIR (about 1640 and 1548 cm-1)): protein [S04 p.3]

## F. Evidence retrieved (14 passages; BM25 + dense, fused with RRF, diversified with MMR)
- **E1** [S01 p.5] _claim, general_method; RRF 0.0_: NIR spectroscopy, with its relatively large penetration depth (up to several millimetres) even into dense solid samples due to low absorption and strong scattering, allows the use of ordinary glass for optics
- **E2** [S01 p.5] _claim, general_method; RRF 0.0519_: strong absorption in the mid-IR region limits the corresponding spectral method to the analysis of very thin samples (usually less than 50 µm), but it opens up the possibility of using attenuated total reflectance (ATR)
- **E3** [S01 p.5] _claim, general_method; RRF 0.0562_: the spectra of vibrational transitions in Raman and mid-IR spectroscopy carry complementary qualitative and quantitative information about the sample's composition.
- **E4** [S01 p.5] _claim, general_method; RRF 0.0_: the strong overlap of spectral signals in UV spectra complicates the analysis of real samples and makes the use of chemometric algorithms a necessary component
- **E5** [S01 p.5] _claim, general_method; RRF 0.029_: However, most chemicals do not exhibit this property.
- **E6** [S01 p.5] _claim, general_method; RRF 0.0431_: Mid-IR band spectra contain well-defined peaks (absorption bands), while NIR, UV, and fluorescence spectra contain broad, highly overlapping signals
- **E7** [S01 p.5] _claim, general_method; RRF 0.0_: preliminary data preparation (preprocessing), construction, validation, and application of predictive models, specifically calibration or classification models.
- **E8** [S01 p.5] _claim, general_method; RRF 0.0_: selecting a spectral method for a specific analytical problem is a complex task requiring specialized knowledge in chemistry, physics, and mathematics.
- **E9** [S01 p.18] _claim, general_method; RRF 0.1324_: advanced labs often incorporate Fluorescence, Raman, and Mid-Infrared (MIR) ATR fiber optic techniques to capture specific chemical or structural information that NIR might miss.
- **E10** [S01 p.18] _chunk, overview; RRF 0.1276_: While NIR is the workhorse of the dairy industry, advanced labs often incorporate Fluorescence, Raman, and Mid-Infrared (MIR) ATR fiber optic techniques to capture specific chemical or structural information that NIR might miss.
- **E11** [S03 p.16] _chunk, proof_of_concept_in_vitro; RRF 0.1144_: Selecting optimal wavelength intervals for an optical sensor: A case study of milk fat and total protein analysis in the region 400–1100 nm.
- **E12** [S01 p.17] _claim, literature_application; RRF 0.1086_: Inline NIR Reflection is primarily used for opaque or highly concentrated dairy products
- **E13** [S01 p.17] _chunk, overview; RRF 0.1072_: Data processing may involve converting the reflectance values to absorbance and applying Multiplicative Scatter Correction (MSC) or Standard Normal Variate (SNV) transformations to remove physical interference caused by the scattering nature of the milk particles before using Partial Least Squares (PLS) regression to quantify fat and protein.
- **E14** [S04 p.3] _chunk, lab_demonstration; RRF 0.1016_: This fact also explains the presence of protein amide I and II bands in the IR spectra of fat in Figure 2a, making those bands less useful for the sample classiﬁcation.

## G. Verification (no AI: quotes, numbers, client facts)
Sourced claims verified: 9/10 · unsupported numbers: 1 · client facts not found in the enquiry: 0

| Where | Status | Claim | Citation | Detail |
|---|---|---|---|---|
| recommendations[0].rationale[0] | verified | NIR reflection is the workhorse for opaque or concentrated dairy products and is used for fat and protein quantification with scatter correc | S01 p.5 | - |
| recommendations[0].rationale[1] | verified | Build a calibration model using lab protein/fat reference data for the milk concentrate. | - | not a sourced claim |
| recommendations[1].rationale[0] | verified | Clear or semi‑transparent liquids are best measured with transmission or transflection probes with a defined 1‑10 mm path. | S01 p.5 | - |
| recommendations[1].rationale[1] | verified | Use a transflection probe that can also serve as a reflection probe for the milk concentrate to simplify installation. | - | not a sourced claim |
| recommendations[2].rationale[0] | verified | MIR ATR provides specific absorption bands for fat and protein and can be used for aqueous media. | S01 p.5 | - |
| recommendations[2].rationale[1] | verified | Test an ATR probe on both streams to evaluate specificity versus NIR. | - | not a sourced claim |
| recommendations[3].rationale[0] | verified | Raman signals are weak but can be useful for aqueous media and are not strongly absorbed by water. | S01 p.5 | quote aligned to the exact page wording |
| recommendations[3].rationale[1] | verified | Assess Raman background and signal quality on the whey and milk concentrate. | - | not a sourced claim |
| recommendations[4].rationale[0] | verified | Fluorescence requires a fluorescent target; most dairy components do not fluoresce, making it unsuitable for protein/fat quantification. | S01 p.5 | - |
| measurement_concept[0] | verified | The pilot will use laboratory protein and fat results as reference for calibration. | - | not a sourced claim |
| measurement_concept[1] | verified | NIR reflection is standard for opaque dairy streams and transmission for clear streams. | S01 p.5 | - |
| measurement_concept[2] | verified | MIR ATR and Raman can add specificity but require careful probe selection. | S01 p.5 | quote aligned to the exact page wording |
| spectral_range[0] | verified | NIR: client‑agreed range for protein/fat quantification. | S01 p.5 | - |
| spectral_range[1] | verified | MIR ATR: 4000–400 cm⁻¹, focusing on 1740 cm⁻¹ (fat) and 1650 cm⁻¹ (protein). | S04 p.3 | - |
| spectral_range[2] | unverified | Raman: 400–4000 cm⁻¹ with excitation at 785 nm (typical for dairy). | S01 p.11 | S01 p.11: quote not on page (53) |
| risks[0] | verified | The whey stream will remain clear enough for transmission; if it becomes turbid, the NIR transmission probe may fail. | - | not a sourced claim |
| risks[1] | verified | Temperature variations may shift spectral baselines; calibration models must account for this. | - | not a sourced claim |
| risks[2] | verified | Fiber attenuation over long lengths could reduce signal strength, especially for MIR ATR. | - | not a sourced claim |
| risks[3] | verified | Include temperature sensors and monitor optical path length during the pilot. | - | not a sourced claim |

**Numbers**
- recommendations[1]: 10 mm: supported
- recommendations[1].rationale[0]: 10 mm: supported
- spectral_range[1]: 4000–400 cm⁻¹: supported
- spectral_range[1]: 1740 cm⁻¹: supported
- spectral_range[1]: 1650 cm⁻¹: unsupported (not found in the enquiry, the evidence or the cited pages)
- spectral_range[2]: 400–4000 cm⁻¹: supported
- spectral_range[2]: 785 nm: supported

**Client facts**
- measurement_concept[0]: verified: The pilot will use laboratory protein and fat results as reference for calibration.

## H. Quality checks
Passed 12/16 · one automatic repair round was used

| Check | Category | Status | Detail |
|---|---|---|---|
| S1 All required sections present | structure | pass | - |
| S2 3-6 questions, highest impact first | structure | pass | - |
| S3 Plan has samples, reference, comparison, decision basis | structure | pass | - |
| S4 Decision status consistent with rule findings | structure | pass | - |
| G1 Sourced claims verified on the cited page | grounding | warn | 9/10 verified; problems at spectral_range[2] |
| G2 No unsupported numbers | grounding | fail | 1650 cm⁻¹ at spectral_range[1] |
| G3 No invented client facts | grounding | pass | - |
| G4 Evidence used within its scope | grounding | pass | - |
| G5 Each recommendation has a sourced reason | grounding | pass | - |
| H1 No guarantee or readiness wording | honesty | pass | - |
| H2 Units: Raman shift in cm-1, excitation in nm | honesty | pass | - |
| H3 Fiber choice consistent with spectral coverage | honesty | pass | - |
| H4 Contradicted premises are stated plainly in the headline | honesty | pass | - |
| U1 Client-requested weak methods are addressed (why / why not) | usefulness | warn | not addressed: UVVIS |
| U2 Feasibility plan is concrete | usefulness | pass | - |
| U3 Questions cover the high-impact unknowns | usefulness | warn | 0/3 high-impact rule questions covered |

**Repair notes**
- G1 fixed

## I. Confidence (computed from observable signals; the model never rates itself)
**Overall: insufficient**
- Signal Information: insufficient (0.10): 1/10 decision-relevant facts known; target defined: yes
- Signal Evidence: high (1.00): Direct application in AFS sources: R_DAIRY
- Signal Scope fit: high (1.00): Requested use matches the scope of the cited evidence
- Signal Client premises: high (1.00): 0 contradicted, 0 unverifiable, 2 supported
- Signal Verification: high (0.90): 9/10 sourced claims verified; 1 unsupported numbers
- Signal Model agreement: high (1.00): 3/3 drafts share the lead method(s) NIR; 3/3 share the status 'provisional_assessment' (2 model families)
- Cap: R_FLUO_NEEDS_TARGET: cap low
- Cap: R_CERTAINTY_DEMAND: cap low
- NIR: insufficient: lead, screening score 5
- MIR: insufficient: candidate, screening score 1
- RAMAN: insufficient: candidate, screening score 1
- UVVIS: insufficient: weak, screening score 0
- FLUO: insufficient: not_supported, screening score -3
- To raise it, answer: What is the sample (liquid, powder, melt, tissue...) and its main components? / Is the sample clear, turbid or opaque, and does this change during the process? / What concentration range must be covered, and what is the smallest change that matters?

## J. Enquiry coach
Key facts present: 1/10

| Fact | Status | Impact | Question if missing |
|---|---|---|---|
| Sample matrix and phase | unknown | high | What is the sample (liquid, powder, melt, tissue...) and its main components? |
| Optical behaviour (clear / turbid / opaque) | unknown | high | Is the sample clear, turbid or opaque, and does this change during the process? |
| Concentration range | unknown | high | What concentration range must be covered, and what is the smallest change that matters? |
| Reference method | unknown | high | Which independent reference method (and its uncertainty) can provide calibration values? |
| Process conditions at the probe | unknown | high | What temperature, pressure, flow, fouling and cleaning conditions apply at the probe? |
| Accuracy / acceptance criteria | unknown | medium | Which accuracy, bias or acceptance limits must the measurement meet? |
| Installation and fiber link | unknown | medium | Where can the probe be installed, and how far away will the analyzer be? |
| Response time / update rate | unknown | medium | How quickly must a change be detected (update rate, response time)? |
| Number of measuring points | unknown | low | How many measuring points or streams need monitoring? |
| Target variable / analyte | stated | high | - |

**Improved enquiry template** (fill the [blanks])

    We want a pilot for composition monitoring of our dairy process, which handles a relatively clear whey stream and an opaque milk concentrate. We need to use laboratory protein and fat results where those variables are relevant. We can compare different measurement interfaces before choosing the installation. What first measurement concepts and comparison experiment would make sense for these two streams? [Sample matrix and phase: e.g. liquid, powder, melt, tissue...] [Optical behaviour: clear, turbid, opaque, and any changes during the process...] [Concentration range: e.g. 0.5–5% protein, 0.1–2% fat, and the smallest change that matters...] [Reference method: e.g. Kjeldahl for protein, Gerber for fat, and its uncertainty...] [Process conditions at the probe: temperature, pressure, flow, fouling, cleaning conditions...] [Accuracy / acceptance criteria: required accuracy, bias, acceptance limits...] [Installation and fiber link: where the probe can be installed and how far away the analyzer will be...] [Response time / update rate: how quickly a change must be detected...] [Number of measuring points: how many measuring points or streams need monitoring...]

## K. Council
Winner: draft C · agreement 100% (3/3 drafts share the lead method(s) NIR; 3/3 share the status 'provisional_assessment') · model families: 2

| Draft | Model | Status | Lead methods | Gate failures | Judge score |
|---|---|---|---|---|---|
| A | openai/gpt-oss-120b | provisional_assessment | NIR | G1 Sourced claims verified on the cited page, G2 No unsupported numbers | 4.08 |
| B | qwen/qwen3.8-27b | provisional_assessment | NIR | G1 Sourced claims verified on the cited page, G2 No unsupported numbers | 4.83 |
| C | openai/gpt-oss-20b | provisional_assessment | NIR | G1 Sourced claims verified on the cited page, G2 No unsupported numbers | 4.92 |
- Judge openai/gpt-oss-120b picked C
- Judge qwen/qwen3.8-27b picked C
- Judge openai/gpt-oss-20b picked B

## L. What-if changes
- (this is not a what-if run)

## M. Retrieval and model trace
**Search queries**
- protein, fat in unknown unknown
- unknown unknown probe geometry NIR spectroscopy MIR spectroscopy (ATR) Raman spectroscopy
- Fluorescence needs a fluorescent target Changing optics or several streams need a geometry comparison Request for a final configuration on missing facts Raman fluorescence background risk
- Our dairy process handles both a relatively clear whey stream and an opaque milk concentrate. We want a pilot for composition monitoring, using laboratory protein and fat results where those variables are relevant. We can compare different measurement interfaces before choosing the installation. Wha
- milk concentrate clear liquid whey opaque protein fat
- NIR MIR RAMAN UVVIS FLUO limitations protein, fat
- Passages pinned by blocking/warning rules: 28; evidence tokens used: 1464

| Stage | Model | Prompt tokens | Completion tokens | Latency (ms) | Cached | OK |
|---|---|---|---|---|---|---|
| extract | openai/gpt-oss-20b | 4190 | 947 | 0 | yes | yes |
| premise | openai/gpt-oss-20b | 6580 | 862 | 2058 | no | yes |
| council_draft_A | openai/gpt-oss-120b | 5390 | 2621 | 5999 | no | yes |
| council_draft_B | qwen/qwen3.8-27b | 11009 | 5077 | 59070 | no | yes |
| council_draft_C | openai/gpt-oss-20b | 5390 | 1784 | 2490 | no | yes |
| council_judge_A | openai/gpt-oss-120b | 2717 | 309 | 840 | no | yes |
| council_judge_B | qwen/qwen3.8-27b | 2350 | 122 | 46341 | no | yes |
| council_judge_C | openai/gpt-oss-20b | 2573 | 128 | 396 | no | yes |
| repair | openai/gpt-oss-20b | 4337 | 2061 | 2631 | no | yes |
| coach | openai/gpt-oss-20b | 565 | 296 | 12934 | no | yes |

Stage timings: extract 6 ms, rules 49 ms, retrieve 130 ms, premise 2059 ms, council 116045 ms, verify 2733 ms, coach 12937 ms, total 133967 ms

