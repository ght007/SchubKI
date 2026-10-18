# First technical assessment

> **Enquiry:** We already have a fluorescence spectrometer and would like to use it to report glucose concentration and viable biomass directly during fermentation. Our only justification is that fluorescence can be very sensitive. We have not identified a fluorescent target, marker or reference relationship. What should the assistant tell us?
>
> **Answers added:** Path B - Where it is used: Our R&D lab; Path C - Variables per sensor: Two or three

**Quality checks:** 15/16 · **Sourced claims verified:** 5/5 · **Unsupported numbers:** 0

## 01. Decision Status
**Provisional assessment** · **Confidence:** low (computed, not self-reported)

Fluorescence alone is not supported for direct glucose or viable biomass measurement; a multimodal approach with Raman and UV/Vis is recommended for testing.

**The customer's own claims, tested first**
- **unverifiable**: "fluorescence can be very sensitive". Turbidity / optical density correlates with cell density but does not by itself distinguish viable from non-viable cells. A viable-biomass claim needs a defined indicator and a viability reference method. [S01 p.16] [S01 p.17]
- **unverifiable**: "reuse existing fluorescence spectrometer for glucose and biomass measurement". NIR and other spectra need chemometric calibration models built and validated on the actual matrix. A new API or excipient blend changes the spectra, so an existing calibration must be re-validated and normally rebuilt; reuse is a hypothesis to test, not an assumption. [S01 p.10] [S01 p.5]

To raise confidence, answer: Is the sample clear, turbid or opaque, and does this change during the process? / What concentration range must be covered, and what is the smallest change that matters? / Which independent reference method (and its uncertainty) can provide calibration values?

## 02. Requirements stated
- glucose concentration
- viable biomass
- fluorescence spectrometer
- fermentation process
- R&D lab

## 03. Key unknowns
- Fluorescent target or marker for glucose/biomass
- Calibration relationship between fluorescence signal and glucose/biomass concentration
- Matrix composition and optical properties of fermentation broth
- Optical behavior (scattering, absorption) of fermentation broth

**Assumptions made**
- Assumption: The client's 'fluorescence spectrometer' is a standard benchtop or fiber-coupled instrument capable of measuring emission spectra, not just single-wavelength intensity.
- Assumption: The fermentation broth is optically clear enough for transmission or reflection measurements, or the client is prepared to use ATR or diffuse reflectance geometries if scattering is high.

## 04. Clarification questions
1. **What specific fluorescent species (e.g., NADH, tryptophan, riboflavin) do you intend to monitor, and do you have a reference method (e.g., HPLC, plate count) to correlate their fluorescence with glucose or biomass?** _(high impact)_. Why: Fluorescence is specific to certain molecules; without a defined target and reference, the signal cannot be interpreted as glucose or biomass concentration.
2. **Have you characterized the optical properties of your fermentation broth (turbidity, background fluorescence, scattering) at the wavelengths of interest?** _(high impact)_. Why: Turbidity and background fluorescence can obscure the signal from the target analyte, making direct measurement impossible without correction or a different method.
3. **What is the expected concentration range of glucose and biomass in your process, and what is the required accuracy/precision?** _(medium impact)_. Why: Fluorescence is sensitive but may lack the dynamic range or specificity for glucose (a non-fluorescent metabolite) and total biomass (a complex mixture) without chemometric modeling.
4. **Are you open to using a combination of methods (e.g., Raman for glucose, UV/Vis for biomass trend, fluorescence for cofactors) rather than relying solely on fluorescence?** _(medium impact)_. Why: No single spectral method is optimal for all bioprocess analytes; a multimodal approach is often more robust and accurate.

## 05. Recommendation

### Raman (primary)
- Raman spectroscopy is well-suited for direct detection of glucose in aqueous fermentation media. [S01 p.5] _(sourced)_
- Raman is particularly well-suited for aqueous environments due to low water absorbance. [S01 p.5] _(sourced)_
- A Raman probe should be tested on the client's fermentation broth to evaluate signal quality and background fluorescence interference. _(proposal)_
- _Applies if:_ Only if representative fermentation broth samples with reference assays for glucose and biomass are available.

### Fluorescence (conditional)
- Fluorescence spectroscopy is suitable for high-sensitivity detection of specific fluorescent cofactors. [S01 p.5] _(sourced)_
- Most chemicals, including glucose, do not fluoresce, so fluorescence cannot be used directly for glucose measurement. [S01 p.5] _(sourced)_
- The client's existing fluorescence spectrometer can be used to monitor fluorescent cofactors, but a calibration model must be built and validated on the client's specific fermentation broth. _(proposal)_
- _Applies if:_ Only if the client is interested in monitoring specific fluorescent cofactors (e.g., NADH, tryptophan) as indicators of metabolic state.

### UV/Vis (comparison)
- UV/Vis spectroscopy can be used for real-time biomass monitoring based on turbidity. [S01 p.5] _(sourced)_
- UV/Vis should be tested in parallel with fluorescence and Raman to provide a biomass trend that can be correlated with viable biomass reference measurements. _(proposal)_
- _Applies if:_ Only if the client is interested in a low-cost, robust tool for real-time biomass trend monitoring.

**Method screening (deterministic, from sourced rules)**

| Method | Score | Verdict |
|---|---|---|
| Raman spectroscopy | 4 | lead |
| NIR spectroscopy | 2 | candidate |
| MIR spectroscopy (ATR) | 1 | candidate |
| UV/Vis spectroscopy | 1 | candidate |
| Fluorescence spectroscopy | 1 | candidate |

## 06. Measurement concept
- Fluorescence spectroscopy is suitable for high-sensitivity detection of specific fluorescent cofactors like NADH, tryptophan, and riboflavin, but not for non-fluorescent metabolites like glucose. _(proposal)_
- Raman spectroscopy provides a molecular fingerprint for direct detection of specific metabolites like glucose, acetate, or lactate in aqueous environments. _(proposal)_
- UV/Vis spectroscopy can be used for real-time biomass monitoring because cell suspension turbidity correlates with cell density, but it does not distinguish viable from non-viable cells. _(proposal)_
- Test a multimodal approach combining Raman (for glucose), UV/Vis (for biomass trend), and fluorescence (for cofactors) to cover the full range of analytes and process variables. _(proposal)_

## 07. Spectral range
- Raman: Raman shift in cm-1, excitation laser in nm (e.g., 785 nm). _(proposal)_
- Fluorescence: Emission wavelength in nm, excitation wavelength in nm. _(proposal)_
- UV/Vis: Wavelength in nm (e.g., 600 nm for cell density). _(proposal)_

## 08. Risks and uncertainty
- Turbidity and background fluorescence in the fermentation broth may obscure the signal from the target analyte, making direct measurement impossible without correction or a different method. _(assumption)_
- Fluorescence is specific to certain molecules; without a defined target and reference, the signal cannot be interpreted as glucose or biomass concentration. _(assumption)_
- No single spectral method is optimal for all bioprocess analytes; a multimodal approach is often more robust and accurate. _(assumption)_

**Confidence: low**
- Information: low (2/10 decision-relevant facts known; target defined: yes)
- Evidence: high (Direct application in AFS sources: R_GLUCOSE_NOT_FLUORESCENT_TARGET, R_BIOPROCESS)
- Scope fit: high (Requested use matches the scope of the cited evidence)
- Client premises: medium (0 contradicted, 2 unverifiable, 0 supported)
- Verification: high (5/5 sourced claims verified; 0 unsupported numbers)
- Model agreement: medium (2/3 drafts share the lead method(s) RAMAN; 3/3 share the status 'provisional_assessment' (2 model families))

## 09. Decision basis
- Client-agreed accuracy/precision on independent validation samples
- Correlation coefficient (R²) between spectral signal and reference method (e.g., HPLC for glucose, plate count for biomass)
- Robustness to matrix variation (turbidity, pH, temperature)

## 10. Sources
- **S01 p.5**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "the spectra of vibrational transitions in Raman and mid-IR spectroscopy carry complementary qualitative and quantitative information about the sample's composition."
  - "However, most chemicals do not exhibit this property."
  - "the strong overlap of spectral signals in UV spectra complicates the analysis of real samples and makes the use of chemometric algorithms a necessary component"
  - "NIR spectroscopy, with its relatively large penetration depth (up to several millimetres) even into dense solid samples due to low absorption and strong scattering, allows the use of ordinary glass for optics"
- **S01 p.10**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "These immersion probes operate on the ATR principle but allow analysis at a significant distance from the spectrometer, without the need for sampling."
- **S01 p.16**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "where no single sensor is universally optimal for every analyte or condition."
- **S01 p.17**: Multispectral Laboratory of Optical Analysis Methods: purpose, methods, and applications (art photonics / MIR Photonics) _(overview)_
  - "Fig. 7. Spectral range for bioprocess monitoring with accessible variables."

## 11. First feasibility experiment
**Samples**
- Representative fermentation broth samples across the expected concentration range of glucose and biomass
- Samples with varying turbidity and background fluorescence to test robustness
- Blank samples (media without cells) to characterize background signal
**Reference measurements**
- HPLC or enzymatic assay for glucose concentration
- Plate count or dry weight for viable biomass
- UV/Vis absorbance at 600 nm for cell density trend
**Comparison**
- Fluorescence alone vs. Fluorescence + Raman vs. Fluorescence + UV/Vis
- Single-wavelength fluorescence vs. full-spectrum fluorescence with chemometrics
- Direct fluorescence measurement vs. fluorescence corrected for turbidity/background

**Next step with AFS**
- Multi-method lab trial comparing fluorescence, Raman, and UV/Vis on representative fermentation broth samples.
- Likely path: B - Path B gives a tailored set of spectrometers for R&D in the customer's own lab; testing several methods is what research needs.
- Path A (chosen by the expert): **open**. No finding speaks for or against this path yet; the lab trial decides. [S02 p.20]
- Path B (chosen by the expert): **fits**. Path B gives a tailored set of spectrometers for R&D in the customer's own lab. [S02 p.20]
- Path C (chosen by the expert): **conflicts**. Several variables at once need full-spectrum information; a few-wavelength sensor is designed for one specific control task. A full-spectrum analyzer gives higher accuracy. [S02 p.18, S02 p.20]

**If you proceed anyway with Path C** (Path C (customised spectral IoT sensor) is a poor fit here: Several variables at once need full-spectrum information; a few-wavelength sensor is designed for one specific control task. A full-spectrum analyzer gives higher accuracy.)
1. Run a lab trial with full-spectrum instruments on representative samples.
2. Select the most informative wavelengths and check that a few-band model reaches the client-agreed error on independent samples.
3. Build and test a prototype LED / filter sensor against the reference method before any volume order.
_Sources: S01 p.9, S03 p.14, S02 p.18_

**Proposed setup** (ranked by recommendation; validate in a lab trial)

| System | Path A: Chemometric model for process automation | Path B: Multi-spectral system for your R&D lab | Path C: Low-cost spectral sensors |
|---|---|---|---|
| 1. Raman (primary) | Models: glucose concentration calibration, viable biomass calibration → Process predictions | Lab system: RAMAN measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: RAMAN sensor, Process probe(s), Acquisition + control interface → Process monitoring |
| 2. UV/Vis (comparison) | Models: glucose concentration calibration, viable biomass calibration → Process predictions | Lab system: UVVIS measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: UVVIS sensor, Process probe(s), Acquisition + control interface → Process monitoring |
| 3. Fluorescence (conditional) | Models: glucose concentration calibration, viable biomass calibration → Process predictions | Lab system: FLUO measurement channel, Sample / probe, Acquisition + reference data → Spectra + reference values | Sensor system: FLUO sensor, Process probe(s), Acquisition + control interface → Process monitoring |

## Council
Winner: draft B; agreement 67% (2/3 drafts share the lead method(s) RAMAN; 3/3 share the status 'provisional_assessment')
- Draft A (openai/gpt-oss-120b): judge score 4.5, gate failures: G1 Sourced claims verified on the cited page, G2 No unsupported numbers
- Draft B (qwen/qwen3.8-27b): judge score 5.0, gate failures: G1 Sourced claims verified on the cited page, G2 No unsupported numbers
- Draft C (openai/gpt-oss-20b): judge score 3.75, gate failures: G1 Sourced claims verified on the cited page, G2 No unsupported numbers

_Generated by the AFS assessment assistant (run 12bd4ae4dd, mode council, server default models; models used: openai/gpt-oss-120b, openai/gpt-oss-20b, openai/gpt-oss-20b -> rule fallback, qwen/qwen3.8-27b)._

---

# Appendix: how this assessment was made

Contents: A Path analysis · B Extracted requirements · C Rules that fired · D Method screening · E Spectral coverage · F Evidence retrieved · G Verification · H Quality checks · I Confidence · J Enquiry coach · K Council · L What-if changes · M Retrieval and model trace

## A. AFS path analysis
**Suggested path:** B. Path B gives a tailored set of spectrometers for R&D in the customer's own lab. Path B gives the customer a tailored set of spectrometers for R&D in their own lab; testing several methods is what research needs. [S02 p.20, S02 p.20, S01 p.3]

**Answers to the path questions**
- Path B - Where it is used: Our R&D lab
- Path C - Variables per sensor: Two or three

| Path | Requested by | Verdict | Reason | Sources |
|---|---|---|---|---|
| A | expert | open | No finding speaks for or against this path yet; the lab trial decides. | S02 p.20 |
| B | expert | fits | Path B gives a tailored set of spectrometers for R&D in the customer's own lab. | S02 p.20 |
| C | expert | conflicts | Several variables at once need full-spectrum information; a few-wavelength sensor is designed for one specific control task. A full-spectrum analyzer gives higher accuracy. | S02 p.18, S02 p.20 |

## B. Extracted requirements
**Summary:** The client has a fluorescence spectrometer and wants to use it to measure glucose concentration and viable biomass during fermentation, claiming fluorescence is very sensitive but lacking a fluorescent target or calibration. They need guidance on feasibility and required data.

| Field | Value |
|---|---|
| target variables | glucose concentration, viable biomass |
| target defined | yes |
| matrix | unknown |
| phase | liquid |
| optical behavior | unknown |
| aqueous | yes |
| fluorescent target | yes |
| heterogeneous | unknown |
| temperature | unknown |
| fouling risk | unknown |
| process context | lab_research |
| analyzer remote | unknown |
| link length known | no |
| existing assets | fluorescence spectrometer |
| requested methods | FLUO |
| reference method | unknown |
| concentration level | unknown |
| measurement points | unknown |
| preferred paths | - |

**Facts** (stated / inferred, with the words they come from)
- existing_assets: fluorescence spectrometer _(stated)_ — "We already have a fluorescence spectrometer"
- target_variables: glucose concentration _(stated)_ — "glucose concentration and viable biomass"
- target_variables: viable biomass _(stated)_ — "glucose concentration and viable biomass"
- requested_methods: FLUO _(stated)_ — "fluorescence spectrometer"
- fluorescent_target: yes _(stated)_ — "fluorescence can be very sensitive"

**Unknowns**
- fluorescent target or marker for glucose/biomass _(high impact)_: Without a known fluorescent marker, calibration and sensitivity cannot be established
- calibration relationship between fluorescence signal and glucose/biomass concentration _(high impact)_: Required to convert signal to concentration
- matrix composition and optical properties of fermentation broth _(high impact)_: Affects fluorescence intensity and background
- optical behavior (scattering, absorption) of fermentation broth _(high impact)_: Impacts signal quality

**Client premises found**
- P1 (method claim): "fluorescence can be very sensitive"
- P2 (reuse claim): "reuse existing fluorescence spectrometer for glucose and biomass measurement"

## C. Rules that fired (11)
| Severity | Rule | Finding | Sources |
|---|---|---|---|
| warn | R_CALIBRATION_MATRIX: Calibrations are matrix specific | NIR and other spectra need chemometric calibration models built and validated on the actual matrix. A new API or excipient blend changes the spectra, so an existing calibration must be re-validated and normally rebuilt; reuse is a hypothesis to test, not an assumption. | S01 p.10, S01 p.5, S03 p.14 |
| warn | R_ADD_METHOD_NOT_A_FIX: Adding a method does not keep a calibration valid | Adding a second method (for example Raman) does not make an existing single-method calibration valid. Data from different methods are not equivalent; a fused model needs synchronised data, fusion algorithms and its own calibration and validation. | S01 p.8, S01 p.9, S01 p.15 |
| warn | R_OD_NOT_VIABILITY: Optical density is not viable biomass | Turbidity / optical density correlates with cell density but does not by itself distinguish viable from non-viable cells. A viable-biomass claim needs a defined indicator and a viability reference method. | S01 p.16, S01 p.17 |
| info | R_GLUCOSE_NOT_FLUORESCENT_TARGET: Glucose is reached by vibrational methods | In the AFS material glucose and similar metabolites are associated with Raman, NIR and MIR, not with fluorescence. | S01 p.16, S01 p.17, S02 p.18 |
| info | R_RAMAN_FLUO_BACKGROUND: Raman fluorescence background risk | Raman signals are weak and, for many organic or biological samples, fluorescence can overlay them. Check background and signal quality on real samples; state excitation wavelength and Raman shift separately. | S01 p.11, S02 p.7 |
| info | R_AQUEOUS: Water-rich media | Water absorbs strongly in the IR; Raman shows low water absorbance and suits aqueous media. MIR is used via ATR (very short path). | S01 p.16, S01 p.5 |
| info | R_BIOPROCESS: Bioprocess monitoring | No single sensor is optimal for every bioprocess analyte: UV/Vis turbidity for biomass trends, Raman for metabolites in aqueous media, NIR for major components (mM), fluorescence for fluorescent cofactors (NADH, tryptophan, riboflavin). | S01 p.16, S01 p.17, S01 p.7 |
| info | R_NO_REFERENCE: Reference method unknown | - | S01 p.5, S01 p.10 |
| info | R_MATRIX_CHANGE_TEST_SET: Representative variation in the test set | - | S01 p.17, S01 p.7 |
| info | R_PATH_RD_LAB: R&D or exploratory lab work favours a multi-spectral lab system | - | S02 p.20, S01 p.3 |
| info | R_PATH_SEVERAL_VARIABLES: Several variables in one stream need full spectra | - | S02 p.18, S02 p.20 |

## D. Method screening (deterministic)
| Method | Score | Verdict | Asked for by client | Contributions |
|---|---|---|---|---|
| Raman spectroscopy | 4 | lead | no | +2 Glucose is reached by vibrational methods [S01 p.16, S01 p.17] (R_GLUCOSE_NOT_FLUORESCENT_TARGET); +1 Water-rich media [S01 p.16, S01 p.5] (R_AQUEOUS); +1 Bioprocess monitoring [S01 p.16, S01 p.17] (R_BIOPROCESS) |
| NIR spectroscopy | 2 | candidate | no | +1 Glucose is reached by vibrational methods [S01 p.16, S01 p.17] (R_GLUCOSE_NOT_FLUORESCENT_TARGET); +1 Bioprocess monitoring [S01 p.16, S01 p.17] (R_BIOPROCESS) |
| MIR spectroscopy (ATR) | 1 | candidate | no | +1 Glucose is reached by vibrational methods [S01 p.16, S01 p.17] (R_GLUCOSE_NOT_FLUORESCENT_TARGET) |
| UV/Vis spectroscopy | 1 | candidate | no | +1 Bioprocess monitoring [S01 p.16, S01 p.17] (R_BIOPROCESS) |
| Fluorescence spectroscopy | 1 | candidate | yes | +1 Bioprocess monitoring [S01 p.16, S01 p.17] (R_BIOPROCESS) |

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
- 6-10.5 µm (MIR fingerprint): glucose [S02 p.18]

## F. Evidence retrieved (14 passages; BM25 + dense, fused with RRF, diversified with MMR)
- **E1** [S01 p.5] _claim, general_method; RRF 0.0_: NIR spectroscopy, with its relatively large penetration depth (up to several millimetres) even into dense solid samples due to low absorption and strong scattering, allows the use of ordinary glass for optics
- **E2** [S01 p.5] _claim, general_method; RRF 0.012_: strong absorption in the mid-IR region limits the corresponding spectral method to the analysis of very thin samples (usually less than 50 µm), but it opens up the possibility of using attenuated total reflectance (ATR)
- **E3** [S01 p.5] _claim, general_method; RRF 0.013_: the spectra of vibrational transitions in Raman and mid-IR spectroscopy carry complementary qualitative and quantitative information about the sample's composition.
- **E4** [S01 p.5] _claim, general_method; RRF 0.0_: the strong overlap of spectral signals in UV spectra complicates the analysis of real samples and makes the use of chemometric algorithms a necessary component
- **E5** [S01 p.5] _claim, general_method; RRF 0.0701_: However, most chemicals do not exhibit this property.
- **E6** [S01 p.5] _claim, general_method; RRF 0.0265_: Mid-IR band spectra contain well-defined peaks (absorption bands), while NIR, UV, and fluorescence spectra contain broad, highly overlapping signals
- **E7** [S01 p.5] _claim, general_method; RRF 0.0164_: preliminary data preparation (preprocessing), construction, validation, and application of predictive models, specifically calibration or classification models.
- **E8** [S01 p.5] _claim, general_method; RRF 0.0_: selecting a spectral method for a specific analytical problem is a complex task requiring specialized knowledge in chemistry, physics, and mathematics.
- **E9** [S01 p.16] _chunk, overview; RRF 0.1689_: While UV/Vis tracks growth, Raman spectroscopy can be used in the same reactor to provide a "molecular fingerprint" for direct detection of specific metabolites like glucose, acetate, or lactate.
- **E10** [S01 p.17] _claim, literature_overview; RRF 0.1531_: Fig. 7. Spectral range for bioprocess monitoring with accessible variables.
- **E11** [S01 p.7] _claim, literature_application; RRF 0.1528_: the combination of NIR spectroscopy with fluorescence spectroscopy demonstrated the possibility of more accurately determining the biomass content during yeast fermentation
- **E12** [S01 p.16] _chunk, overview; RRF 0.1542_: While UV/Vis tracks growth, Raman spectroscopy can be used in the same reactor to provide a "molecular fingerprint" for direct detection of specific metabolites like glucose, acetate, or lactate.
- **E13** [S01 p.16] _claim, general_method; RRF 0.1482_: UV/Vis spectroscopy can be deployed as a low-cost, robust tool for real-time biomass monitoring, as cell suspension turbidity correlates well with cell density.
- **E14** [S01 p.16] _claim, general_method; RRF 0.1255_: direct detection of specific metabolites like glucose, acetate, or lactate.

## G. Verification (no AI: quotes, numbers, client facts)
Sourced claims verified: 5/5 · unsupported numbers: 0 · client facts not found in the enquiry: 0

| Where | Status | Claim | Citation | Detail |
|---|---|---|---|---|
| recommendations[0].rationale[0] | verified | Raman spectroscopy is well-suited for direct detection of glucose in aqueous fermentation media. | S01 p.5 | - |
| recommendations[0].rationale[1] | verified | Raman is particularly well-suited for aqueous environments due to low water absorbance. | S01 p.5 | - |
| recommendations[0].rationale[2] | verified | A Raman probe should be tested on the client's fermentation broth to evaluate signal quality and background fluorescence interference. | - | not a sourced claim |
| recommendations[1].rationale[0] | verified | Fluorescence spectroscopy is suitable for high-sensitivity detection of specific fluorescent cofactors. | S01 p.5 | - |
| recommendations[1].rationale[1] | verified | Most chemicals, including glucose, do not fluoresce, so fluorescence cannot be used directly for glucose measurement. | S01 p.5 | - |
| recommendations[1].rationale[2] | verified | The client's existing fluorescence spectrometer can be used to monitor fluorescent cofactors, but a calibration model must be built and vali | - | not a sourced claim |
| recommendations[2].rationale[0] | verified | UV/Vis spectroscopy can be used for real-time biomass monitoring based on turbidity. | S01 p.5 | - |
| recommendations[2].rationale[1] | verified | UV/Vis should be tested in parallel with fluorescence and Raman to provide a biomass trend that can be correlated with viable biomass refere | - | not a sourced claim |
| measurement_concept[0] | verified | Fluorescence spectroscopy is suitable for high-sensitivity detection of specific fluorescent cofactors like NADH, tryptophan, and riboflavin | - | not a sourced claim |
| measurement_concept[1] | verified | Raman spectroscopy provides a molecular fingerprint for direct detection of specific metabolites like glucose, acetate, or lactate in aqueou | - | not a sourced claim |
| measurement_concept[2] | verified | UV/Vis spectroscopy can be used for real-time biomass monitoring because cell suspension turbidity correlates with cell density, but it does | - | not a sourced claim |
| measurement_concept[3] | verified | Test a multimodal approach combining Raman (for glucose), UV/Vis (for biomass trend), and fluorescence (for cofactors) to cover the full ran | - | not a sourced claim |
| spectral_range[0] | verified | Raman: Raman shift in cm-1, excitation laser in nm (e.g., 785 nm). | - | not a sourced claim |
| spectral_range[1] | verified | Fluorescence: Emission wavelength in nm, excitation wavelength in nm. | - | not a sourced claim |
| spectral_range[2] | verified | UV/Vis: Wavelength in nm (e.g., 600 nm for cell density). | - | not a sourced claim |
| risks[0] | verified | Turbidity and background fluorescence in the fermentation broth may obscure the signal from the target analyte, making direct measurement im | - | not a sourced claim |
| risks[1] | verified | Fluorescence is specific to certain molecules; without a defined target and reference, the signal cannot be interpreted as glucose or biomas | - | not a sourced claim |
| risks[2] | verified | No single spectral method is optimal for all bioprocess analytes; a multimodal approach is often more robust and accurate. | - | not a sourced claim |

**Numbers**
- spectral_range[0]: 785 nm: supported
- spectral_range[2]: 600 nm: supported
- feasibility_plan.reference[2]: 600 nm: supported

## H. Quality checks
Passed 15/16 · one automatic repair round was used

| Check | Category | Status | Detail |
|---|---|---|---|
| S1 All required sections present | structure | pass | - |
| S2 3-6 questions, highest impact first | structure | pass | - |
| S3 Plan has samples, reference, comparison, decision basis | structure | pass | - |
| S4 Decision status consistent with rule findings | structure | pass | - |
| G1 Sourced claims verified on the cited page | grounding | pass | - |
| G2 No unsupported numbers | grounding | pass | - |
| G3 No invented client facts | grounding | pass | - |
| G4 Evidence used within its scope | grounding | pass | - |
| G5 Each recommendation has a sourced reason | grounding | pass | - |
| H1 No guarantee or readiness wording | honesty | pass | - |
| H2 Units: Raman shift in cm-1, excitation in nm | honesty | warn | Raman shift given in nm at spectral_range[0] |
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
- Signal Evidence: high (1.00): Direct application in AFS sources: R_GLUCOSE_NOT_FLUORESCENT_TARGET, R_BIOPROCESS
- Signal Scope fit: high (1.00): Requested use matches the scope of the cited evidence
- Signal Client premises: medium (0.67): 0 contradicted, 2 unverifiable, 0 supported
- Signal Verification: high (1.00): 5/5 sourced claims verified; 0 unsupported numbers
- Signal Model agreement: medium (0.67): 2/3 drafts share the lead method(s) RAMAN; 3/3 share the status 'provisional_assessment' (2 model families)
- RAMAN: low: lead, screening score 4
- NIR: insufficient: candidate, screening score 2
- MIR: insufficient: candidate, screening score 1
- UVVIS: insufficient: candidate, screening score 1
- FLUO: insufficient: candidate, screening score 1
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

    We already have a fluorescence spectrometer and would like to use it to report glucose concentration and viable biomass directly during fermentation. Our only justification is that fluorescence can be very sensitive. We have not identified a fluorescent target, marker or reference relationship. What should the assistant tell us? 
    
    [Optical behaviour (clear / turbid / opaque): Is the sample clear, turbid or opaque, and does this change during the process?]
    [Concentration range: What concentration range must be covered, and what is the smallest change that matters?]
    [Reference method: Which independent reference method (and its uncertainty) can provide calibration values?]
    [Process conditions at the probe: What temperature, pressure, flow, fouling and cleaning conditions apply at the probe?]
    [Accuracy / acceptance criteria: Which accuracy, bias or acceptance limits must the measurement meet?]
    [Installation and fiber link: Where can the probe be installed, and how far away will the analyzer be?]
    [Response time / update rate: How quickly must a change be detected (update rate, response time)?]
    [Number of measuring points: How many measuring points or streams need monitoring?]

## K. Council
Winner: draft B · agreement 67% (2/3 drafts share the lead method(s) RAMAN; 3/3 share the status 'provisional_assessment') · model families: 2

| Draft | Model | Status | Lead methods | Gate failures | Judge score |
|---|---|---|---|---|---|
| A | openai/gpt-oss-120b | provisional_assessment | RAMAN | G1 Sourced claims verified on the cited page, G2 No unsupported numbers | 4.5 |
| B | qwen/qwen3.8-27b | provisional_assessment | RAMAN | G1 Sourced claims verified on the cited page, G2 No unsupported numbers | 5.0 |
| C | openai/gpt-oss-20b | provisional_assessment | NIR | G1 Sourced claims verified on the cited page, G2 No unsupported numbers | 3.75 |
- Judge openai/gpt-oss-120b picked B
- Judge qwen/qwen3.8-27b picked A
- Judge openai/gpt-oss-20b picked B

## L. What-if changes
- (this is not a what-if run)

## M. Retrieval and model trace
**Search queries**
- glucose concentration, viable biomass in unknown liquid
- unknown liquid probe geometry Raman spectroscopy NIR spectroscopy MIR spectroscopy (ATR)
- Calibrations are matrix specific Adding a method does not keep a calibration valid Optical density is not viable biomass Glucose is reached by vibrational methods
- We already have a fluorescence spectrometer and would like to use it to report glucose concentration and viable biomass directly during fermentation. Our only justification is that fluorescence can be very sensitive. We have not identified a fluorescent target, marker or reference relationship. What
- fluorescence spectroscopy glucose biomass fermentation
- fluorescence spectrometer
- FLUO limitations glucose concentration, viable biomass
- Passages pinned by blocking/warning rules: 40; evidence tokens used: 1217

| Stage | Model | Prompt tokens | Completion tokens | Latency (ms) | Cached | OK |
|---|---|---|---|---|---|---|
| extract | openai/gpt-oss-20b | 1761 | 750 | 0 | yes | yes |
| premise | openai/gpt-oss-20b -> rule fallback | 0 | 0 | 1942 | no | no: 1 validation error for PremiseCheckOut verdicts.1   Input should be an object [t |
| council_draft_A | openai/gpt-oss-120b | 4967 | 2695 | 6202 | no | yes |
| council_draft_B | qwen/qwen3.8-27b | 4089 | 2377 | 5311 | no | yes |
| council_draft_C | openai/gpt-oss-20b | 11279 | 2657 | 84832 | no | yes |
| council_judge_A | openai/gpt-oss-120b | 2478 | 436 | 1109 | no | yes |
| council_judge_B | qwen/qwen3.8-27b | 2284 | 122 | 549 | no | yes |
| council_judge_C | openai/gpt-oss-20b | 2459 | 129 | 24521 | no | yes |
| repair | openai/gpt-oss-20b | 4276 | 2101 | 39510 | no | yes |
| coach | openai/gpt-oss-20b | 533 | 268 | 12254 | no | yes |

Stage timings: extract 7 ms, rules 16 ms, retrieve 160 ms, premise 1951 ms, council 122631 ms, verify 39536 ms, coach 12262 ms, total 176572 ms

