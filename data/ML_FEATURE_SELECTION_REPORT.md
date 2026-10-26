# SmartSilageAI (SIH26111) — Second-Stage ML Feature Selection & Data Leakage Report

**Project:** Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers  
**Challenge ID:** SIH26111 (Ministry of Fisheries, Animal Husbandry & Dairying)  
**Target Variable:** `fqi` (Fermentation Quality Index — Continuous Regression Target)  
**Dataset Reference:** `elab.all` sheet in `data/datasilage.xlsx` (1,496 rows × 52 columns)  
**Report Date:** 2026-10-08  
**Integrity Rules Followed:** Zero synthetic/fake data, zero arbitrary label binning, original Excel file untouched, zero model training executed.

---

## 1. Executive Summary & Problem Framing

In dairy science and on-farm feed management (SIH26111), predicting silage quality is fundamentally divided into two distinct temporal operational phases:

1. **Phase 1: Pre-Ensiling / Harvest-Time Forecasting (Primary ML Target):**
   - **The Farmer's Question:** *"I am chopping this green corn/sorghum today. Based on my forage's moisture and fiber traits, how will my choice of inoculant, packing delay, and storage method affect the final Fermentation Quality Index (`fqi`)?"*
   - **Data Horizon:** Only pre-ensiling variables (`.f`) and agronomic/management decisions (`delay`, `inhoculant`, `dose`, `method`, `maturity`) exist. **Zero post-ensiling variables exist yet.**
2. **Phase 2: Post-Ensiling / Pit-Opening Rapid Screening:**
   - **The Farmer's Question:** *"I opened my bunker silo 60 days later. Is this silage safe and high quality for my lactating dairy cows?"*
   - **Data Horizon:** The farmer can test on-farm field metrics (portable digital pH, Koster/microwave dry matter `dm.s`, probe temperature, visual/olfactory signs). However, **gas chromatography / HPLC fermentation acids (`lactic.ac.s`, `butyric.ac.s`, `acetic.ac.s`, `ammonia.s`) remain completely inaccessible on rural farms.**

### Why Post-Ensiling Fermentation Acids Constitute Severe Data Leakage
In the foundational literature establishing the `fqi` index (*Andrighetto et al., 2018, Anim Feed Sci Technol, 242:31–40*), Index $I_1$ (`fqi`) is formulated as an **algebraic composite of post-ensiling fermentation parameters**:
$$\text{FQI} = f\big(\text{pH}, \text{lactic acid}, \text{acetic acid}, \text{propionic acid}, \text{butyric acid}, \text{ethanol}, \text{ammonia-N}\big)$$

1. **Direct Mathematical Leakage:** Regressing `fqi` on `lactic.ac.s`, `acetic.ac.s`, `butyric.ac.s`, `propionic.ac.s`, `ammonia.s`, and `ethanol.s` gives an $R^2 > 0.83$ because the model merely learns the arithmetic equation used by the authors to generate `fqi`.
2. **Deployment Infeasibility:** An Indian dairy farmer with a smartphone cannot measure wet-chemistry chromatography acids in the cowshed. If the model relies on HPLC acids as features, the system is unusable in the field.

Therefore, to build a scientifically sound, leak-free, deployable AI model, **all post-ensiling laboratory fermentation acids must be strictly excluded from the feature matrix.**

---

## 2. Comprehensive 52-Column Feature Selection & Leakage Matrix

Below is the complete analysis of **every single column** present in the `elab.all` sheet:

| # | Column Name | Meaning / Description | Category | Field Availability at Prediction Time | Decision | Exact Reason for Inclusion / Exclusion | Null % | Leakage Risk |
|:---:|:---|:---|:---|:---:|:---:|:---|:---:|:---:|
| 1 | `ref.trial` | Research trial grouping ID (1, 2.a.1.a, etc.) | Identifier | No | **EXCLUDE** | Administrative research trial ID. Including as a feature causes cross-trial memorization. *(Must be retained solely as a grouping key for GroupKFold validation).* | 0.00% | Medium (split leakage) |
| 2 | `ref.article` | Research article bibliography code | Identifier | No | **EXCLUDE** | Journal publication key; completely uninformative for agricultural silage quality. | 0.00% | Low |
| 3 | `fresh.id` | Fresh crop sample identifier string | Identifier | No | **EXCLUDE** | Sample ID tag (1,179 unique categories); would cause pure overfitting. | 0.00% | Low |
| 4 | `silage.id` | Ensiled silage sample identifier string | Identifier | No | **EXCLUDE** | Silage sample tag (1,121 unique categories); uninformative identifier. | 2.94% | Low |
| 5 | `year` | Trial calendar harvest year (2016–2022) | Management / Temporal | Yes | **EXCLUDE** | Feeding specific historical calendar years (`y2016`) as categorical features causes temporal overfitting and will not generalize to future calendar years (e.g. 2026). Better used as an out-of-time evaluation axis. | 0.00% | Medium |
| 6 | `method` | Storage containment type (`bags` vs `buckets`) | Management | Yes | **USE** | Silo type directly governs oxygen exclusion, wall permeation, and aerobic boundary conditions during ensiling. Farmers know their silo structure (bunker/pit vs bag). | 0.00% | Low |
| 7 | `inhoculant` | Bacterial additive applied (`c`=control, `he`=heterofermentative, `ho`=homofermentative) | Management | Yes | **USE** | Primary biological decision made by farmer. Determines whether lactic fermentation pathway is homolactic (rapid pH decline) or heterolactic (acetic acid for aerobic stability). | 0.00% | Low |
| 8 | `dose` | Inoculant application dosage (`none`, `h`=half, `s`=standard, `d`=double) | Management | Yes | **USE** | Governs microbial colony forming units (CFU/g) introduced into fresh biomass. Impute missing as `'none'`. | 2.41% | Low |
| 9 | `delay` | Packing delay between chopping and silo sealing (`D0`=0–4h, `D6`=6h, `D20`=20–24h) | Management | Yes | **USE** | Critical agronomic failure mode. Exposure to ambient air depletes fermentable sugars, increases temperature, and causes aerobic deterioration. Readily known by farmer. | 0.00% | Low |
| 10 | `hybrid` | Cultivar/hybrid seed code (39 unique hybrids) | Agronomic | Conditional | **EXCLUDE** | 39 high-cardinality research seed cultivars specific to European field trials. Will not generalize to Indian hybrid varieties (e.g., Advanta, Pioneer India) and causes high variance. | 4.75% | Low |
| 11 | `field` | Agronomic field fertility plot (`ifl`, `ifm`, `ifh`, `ifn`) | Agronomic | Conditional | **EXCLUDE** | Internal experimental field plot codes. Lacks standardized physical or chemical definition usable on commercial dairy farms. | 4.75% | Low |
| 12 | `fao.class` | FAO crop maturity class (`ea`=early ~200, `la`=late ~600–700) | Agronomic / Crop | Yes | **USE** | Early vs late maturity classes dictate vegetative period duration, grain-to-stover ratio, and whole-crop moisture curves. | 4.75% | Low |
| 13 | `maturity` | Harvest phenological stage (`eh`=1/3 milk line, `mh`=2/3 milk line, `lh`=late, `vlh`=very late) | Agronomic / Crop | Yes | **USE** | Universal farmer visual standard (kernel milk line in cob). Directly determines grain filling, moisture content, and starch density. Impute missing as `'Unknown'`. | 11.97% | Low |
| 14 | `subplot` | Research replicate plot block (`r1`, `r2`, `r3`, `r4`) | Identifier | No | **EXCLUDE** | Research field block replicate number; irrelevant to dairy farmer prediction. | 0.00% | Low |
| 15 | `density` | Categorical density class string (`denl`, `denh`) | Management | Yes | **EXCLUDE** | Too sparse: 96.79% missing values (only 48 rows recorded). Cannot be reliably used as a general feature. | 96.79% | Low |
| 16 | `type` | Aggregation type (`singular` vs `average` across bucket layers) | Experimental Protocol | No | **EXCLUDE** | Research lab data aggregation flag; irrelevant to farm feed testing. | 0.00% | Low |
| 17 | `dm.f` | Fresh forage dry matter content (%) | Fresh Nutrient | Yes | **USE** | The single most decisive biological parameter for ensiling. Determines whether fermentation is lactic or clostridial; measurable via Koster/microwave tester. | 1.47% | Low |
| 18 | `ash.f` | Fresh forage total ash (% DM) | Fresh Nutrient | Yes | **USE** | Measures soil contamination and mineral content; directly affects buffering capacity resisting acidification. | 1.47% | Low |
| 19 | `cp.f` | Fresh forage crude protein (% DM) | Fresh Nutrient | Yes | **USE** | Protein compounds act as biological buffers against organic acid accumulation; key nutritive parameter. | 1.47% | Low |
| 20 | `ee.f` | Fresh forage ether extract / crude fat (% DM) | Fresh Nutrient | Yes | **USE** | Baseline energy lipid fraction in standing forage; stable proximate input. | 1.47% | Low |
| 21 | `ndf.f` | Fresh Neutral Detergent Fiber (% DM) | Fresh Nutrient | Yes | **USE** | Total structural plant cell-wall fiber (hemicellulose + cellulose + lignin). Indicates vegetative maturity and silo compaction compressibility. | 2.27% | Low |
| 22 | `adf.f` | Fresh Acid Detergent Fiber (% DM) | Fresh Nutrient | Yes | **USE** | Less digestible lignocellulosic fraction; vital proximate indicator of forage maturity. | 1.60% | Low |
| 23 | `lignin.f` | Fresh Acid Detergent Lignin (% DM) | Fresh Nutrient | Yes | **USE** | Indigestible structural polymer; affects microbial access to plant sugars. | 1.47% | Low |
| 24 | `wsc.f` | Fresh Water-Soluble Carbohydrates (% DM) | Fresh Nutrient | Yes | **USE** | Primary metabolic fuel for lactic acid bacteria. Without adequate WSC, fermentation stalls and pH remains high. | 1.47% | Low |
| 25 | `starch.f` | Fresh grain starch content (% DM) | Fresh Nutrient | Yes | **USE** | Reflects kernel development and energy density of the whole maize plant. | 2.27% | Low |
| 26 | `Unnamed: 25` | Empty Excel sheet separator column | Formatting Artifact | No | **EXCLUDE** | 100.00% NaN; artifact of spreadsheet formatting. | 100.00% | Low |
| 27 | `dm.s` | Ensiled silage dry matter content (%) | Post-Ensiling | Conditional | **EXCLUDE** | Only measurable after fermentation is completed. Using it to forecast `fqi` at harvest violates temporal causality. | 0.67% | Medium (temporal leakage) |
| 28 | `ash.s` | Ensiled silage ash (% DM) | Post-Ensiling | No | **EXCLUDE** | Post-fermentation outcome variable; unavailable before ensiling. | 0.67% | Medium |
| 29 | `cp.s` | Ensiled silage crude protein (% DM) | Post-Ensiling | No | **EXCLUDE** | Post-fermentation outcome variable; unavailable before ensiling. | 0.67% | Medium |
| 30 | `ee.s` | Ensiled silage ether extract (% DM) | Post-Ensiling | No | **EXCLUDE** | Post-fermentation outcome variable. | 0.67% | Medium |
| 31 | `ndf.s` | Ensiled silage NDF (% DM) | Post-Ensiling | No | **EXCLUDE** | Post-fermentation outcome variable. | 0.67% | Medium |
| 32 | `adf.s` | Ensiled silage ADF (% DM) | Post-Ensiling | No | **EXCLUDE** | Post-fermentation outcome variable. | 0.67% | Medium |
| 33 | `lignin.s` | Ensiled silage lignin (% DM) | Post-Ensiling | No | **EXCLUDE** | Post-fermentation outcome AND severely missing (55.55% nulls). | 55.55% | Medium |
| 34 | `starch.s` | Ensiled silage starch (% DM) | Post-Ensiling | No | **EXCLUDE** | Post-fermentation outcome variable. | 0.74% | Medium |
| 35 | `wsc.s` | Residual unfermented sugars in silage (% DM) | Post-Ensiling | No | **EXCLUDE** | Post-fermentation outcome AND 45.12% missing. | 45.12% | Medium |
| 36 | `pH` | Silage pH post-fermentation | Post-Ensiling / Target Constituent | Conditional | **EXCLUDE** | Direct mathematical constituent in the Andrighetto et al. FQI formula ($r = -0.45$). Also post-fermentation metric. Feeding it creates formula leakage. | 0.87% | **High** |
| 37 | `ammonia.s` | Silage ammonia nitrogen ($NH_3\text{-}N / N_{\text{total}}$ %) | Post-Ensiling / Lab | No | **EXCLUDE** | Direct constituent penalized in FQI formula; requires laboratory Megazyme/Kjeldahl assay. | 0.67% | **High** |
| 38 | `glucose.s` | Silage residual glucose (% DM) | Post-Ensiling / Lab | No | **EXCLUDE** | HPLC laboratory metric; post-fermentation outcome; 15.31% missing. | 15.31% | Medium |
| 39 | `fructose.s` | Silage residual fructose (% DM) | Post-Ensiling / Lab | No | **EXCLUDE** | HPLC laboratory metric; post-fermentation outcome; 15.31% missing. | 15.31% | Medium |
| 40 | `mannithol.s` | Silage mannitol (% DM) | Post-Ensiling / Lab | No | **EXCLUDE** | Secondary fermentation product; post-fermentation HPLC metric. | 0.67% | Medium |
| 41 | `ethanol.s` | Silage ethanol (% DM) | Post-Ensiling / Lab | No | **EXCLUDE** | Direct constituent component in FQI formula (yeast fermentation indicator). | 0.67% | **High** |
| 42 | `lactic.ac.s` | Silage lactic acid (% DM) | Post-Ensiling / Lab | No | **EXCLUDE** | **Primary mathematical driver of FQI** ($r = +0.76$). Feeding it into ML is circular tautological leakage. Inaccessible to farmers on-farm. | 0.67% | **High** |
| 43 | `acetic.ac.s` | Silage acetic acid (% DM) | Post-Ensiling / Lab | No | **EXCLUDE** | Direct constituent term in FQI calculation; requires HPLC/GC chromatography. | 0.67% | **High** |
| 44 | `propionic.ac.s` | Silage propionic acid (% DM) | Post-Ensiling / Lab | No | **EXCLUDE** | Direct constituent term in FQI calculation. | 0.67% | **High** |
| 45 | `butyric.ac.s` | Silage butyric acid (% DM) | Post-Ensiling / Lab | No | **EXCLUDE** | Direct constituent term heavily penalized in FQI calculation (spoilage acid). | 0.67% | **High** |
| 46 | `dm.loss` | Dry matter loss during fermentation (%) | Derived / Outcome | No | **EXCLUDE** | Downstream loss outcome; only measurable at total silo cleanout. Feeding it creates temporal leakage. | 6.35% | High |
| 47 | `dm.ret` | Dry matter retention (%) | Derived / Outcome | No | **EXCLUDE** | Deterministic linear complement ($100 - \text{dm.loss}$). Post-fermentation outcome. | 6.35% | High |
| 48 | `fqi` | Fermentation Quality Index (continuous) | **TARGET VARIABLE** | No | **TARGET** | Proposed continuous target variable. Must NOT be an input feature. | 0.67% | Target |
| 49 | `porosity` | Silo packing porosity | Silo Physics | No | **EXCLUDE** | Highly missing (55.48%); unmeasurable on commercial dairy farms without specialized laboratory coring. | 55.48% | Low |
| 50 | `density.1` | Measured compaction density ($kg\text{ DM}/m^3$) | Management / Physics | Conditional | **EXCLUDE** | Highly missing (55.68% nulls; recorded only in bucket trials). Exclude from primary baseline. | 55.68% | Low |
| 51 | `ref.fresh` | Fresh spectrometer tag (`PoliSPECNIR`) | Metadata | No | **EXCLUDE** | Constant value across 100% of rows (zero variance); technical hardware tag. | 0.00% | Low |
| 52 | `ref.silage` | Silage spectrometer tag (`FOSS NIRSystem 5000` / `PoliSPECNIR`) | Metadata | No | **EXCLUDE** | Laboratory instrument tag; would introduce machine-specific bias. | 0.00% | Low |

---

## 3. In-Depth Analysis of Key Controversies & Nuances

### A. Why Post-Ensiling Fermentation Acids Are Leakage When Predicting FQI
In the scientific paper defining FQI (*Andrighetto et al., 2018*), Index $I_1$ was designed explicitly as an aggregate chemical index:
- It rewards higher lactic acid concentration (reflecting effective homolactic fermentation).
- It heavily penalizes butyric acid (clostridial protein breakdown and butyric fermentation).
- It adjusts for acetic acid, propionic acid, ethanol, and ammonia nitrogen ($NH_3\text{-}N$).
- An empirical regression on our exact 1,486 rows demonstrates that these chromatography acids and pH directly explain **82.8% of the variance** ($R^2 = 0.828$) of `fqi`.
- **Verdict:** If an ML model is given `lactic.ac.s`, `acetic.ac.s`, `butyric.ac.s`, etc., it simply memorizes the author's mathematical formula. It does not learn the biological conversion from forage to silage. Furthermore, no Indian dairy farmer has an HPLC machine in their barn.

### B. Why `dm.loss` and `dm.ret` Must Be Excluded
- `dm.loss` represents the percentage of dry biomass consumed by plant cell respiration, fermentation microbial metabolism, and gas/effluent losses.
- It is physically impossible to know `dm.loss` until the silo is completely fed out and re-weighed.
- Furthermore, `dm.ret` is an exact mathematical duplicate: $\text{dm.ret} = 100 - \text{dm.loss}$.
- Using either as an input feature is a severe temporal violation. Both must be excluded when predicting `fqi`. (Note: `dm.loss` could serve as a secondary prediction target in a future model, but never as an input feature).

### C. The `dm.s` (Silage Dry Matter) Dilemma: Pre-Ensiling vs. Post-Ensiling
- For a **Harvest-Time Forecasting Tool** (the primary goal of evaluating silage before making it), `dm.s` does not exist. Only `dm.f` (fresh forage dry matter) is known. Using `dm.s` would be predicting the future using future information.
- For an **Opened-Silo Rapid Field Screening Tool**, a farmer *can* measure moisture on opened silage using a microwave or Koster tester. However, in `elab.all`, `fqi` was designed to measure how well the fresh crop preserved into silage. 
- **Recommendation:** Keep `dm.s` strictly excluded from the baseline Harvest-to-FQI model. If a secondary "Opened-Silage Quality Evaluator" is later designed, `dm.s` can be included alongside field pH, but still strictly excluding chromatography acids.

### D. Missing Values: When to Impute vs. Exclude
- Columns must **NOT** be discarded simply because they contain missing values.
  - `maturity` has 11.97% missingness. However, kernel milk line maturity is one of the most vital biological traits governing whole-plant moisture and starch. It should be **kept** and missing rows imputed with an `'Unknown'` category.
  - `dose` has 2.41% missingness. Inoculant dosage directly impacts colony forming units; missing values should be imputed as `'none'`.
  - `dm.f`, `cp.f`, `ndf.f`, `adf.f`, `ash.f`, `wsc.f`, `starch.f` have between 1.47% and 2.27% missing values. These represent laboratory or NIRS proximate analysis missingness and should be retained using standard median or KNN imputation.
- Conversely, columns like `Unnamed: 25` (100% null), `density` (96.79% null), `lignin.s` (55.55% null), and `density.1` (55.68% null) are excluded because their extreme sparsity would either force excessive synthetic imputation or drop over half the dataset.

### E. Temperature-Related Information
- In `elab.all`, there is no direct silage probe temperature column.
- Temperature tracking data (`event`, `time.event`, `cumulative.temperature`) is isolated in the separate sheet `elab.temp` (160 samples only).
- While silo temperature is very useful for detecting aerobic spoilage on real dairy farms, it is absent from the 1,496 rows of `elab.all`. Therefore, it cannot be an input feature in this master dataset.

---

## 4. Final Recommendations for the ML Pipeline

### A. Final Proposed Input Features (14 Features for Baseline Model)

The proposed 14 features represent a completely leak-free, deployable feature set available at harvest time:

#### 1. Fresh Nutritional / Proximate Features (8 continuous numeric features):
1. **`dm.f`**: Fresh Dry Matter (%)
2. **`cp.f`**: Fresh Crude Protein (% DM)
3. **`ndf.f`**: Fresh Neutral Detergent Fiber (% DM)
4. **`adf.f`**: Fresh Acid Detergent Fiber (% DM)
5. **`ash.f`**: Fresh Total Ash (% DM)
6. **`wsc.f`**: Fresh Water-Soluble Carbohydrates (% DM)
7. **`starch.f`**: Fresh Starch Content (% DM)
8. **`lignin.f`**: Fresh Acid Detergent Lignin (% DM)

#### 2. Harvest & Management Decision Features (6 categorical/ordinal features):
9. **`method`**: Silo containment type (`bags` vs `buckets`)
10. **`inhoculant`**: Bacterial additive type (`c` = control/water, `he` = heterofermentative, `ho` = homofermentative)
11. **`dose`**: Inoculant application rate (`none`, `h`, `s`, `d`)
12. **`delay`**: Packing delay time (`D0` = 0–4h, `D6` = 6h, `D20` = 20–24h)
13. **`fao.class`**: Maturity category (`ea` = early season, `la` = late season)
14. **`maturity`**: Kernel milk line stage (`eh` = early harvest 1/3, `mh` = mid harvest 2/3, `lh` = late harvest, `vlh` = very late harvest)

---

### B. Features Definitely Excluded (37 Columns)

1. **Identifiers & Technical Tags (8):** `ref.trial`, `ref.article`, `fresh.id`, `silage.id`, `subplot`, `type`, `ref.fresh`, `ref.silage`
2. **Formatting Artifacts (1):** `Unnamed: 25` (100% null)
3. **Severe Missingness > 50% (4):** `density` (96.8%), `lignin.s` (55.6%), `porosity` (55.5%), `density.1` (55.7%)
4. **Post-Ensiling Fermentation Acids & Target Constituents (7):** `lactic.ac.s`, `acetic.ac.s`, `propionic.ac.s`, `butyric.ac.s`, `ammonia.s`, `ethanol.s`, `pH` *(Direct formula leakage)*
5. **Post-Ensiling Laboratory Metabolites & Proximate Traits (12):** `dm.s`, `ash.s`, `cp.s`, `ee.s`, `ndf.s`, `adf.s`, `starch.s`, `wsc.s`, `glucose.s`, `fructose.s`, `mannithol.s`
6. **Downstream Losses & Mirrors (2):** `dm.loss`, `dm.ret`
7. **Confounding High-Cardinality Variables (3):** `year` (temporal confounder), `hybrid` (39 seed codes), `field` (internal plot codes)

---

### C. Proposed Target Variable: `fqi`

- **Name:** `fqi` (Fermentation Quality Index)
- **Role:** Ground truth continuous target.
- **Distribution:** Real continuous metric ranging from **11.66 to 84.57** (Mean: 52.40, Median: 52.76, Std: 10.72).
- **Handling:** Drop the 10 rows where `fqi` is missing, leaving **1,486 valid, real experimental samples**.

---

### D. Regression vs. Classification: Definite Recommendation

**RECOMMENDATION: CONTINUOUS REGRESSION**

* **Reason 1 (Zero Artificial Labels):** Rule 9 explicitly states: *"Do NOT create artificial Good/Moderate/Poor labels."* Training a classifier would require inventing arbitrary numerical cutoffs (e.g. FQI > 60 = Good) which introduces subjective classification boundary noise.
* **Reason 2 (Preserves Variance & Precision):** Silage quality is a biological continuum. A sample at FQI 59.9 is virtually identical to 60.1, but a classifier treats them as different classes.
* **Reason 3 (Flexible Advisory Thresholds in UI):** The ML model predicts the exact continuous `fqi` score. The frontend UI can then display both the precise estimated score and scientific advisory guidance (e.g. ICAR-NDRI or Andrighetto score bands) without compromising model mathematics.

---

### E. Recommended Preprocessing Pipeline

1. **Target Row Filtering:**
   - Drop the 10 rows with missing `fqi` (yielding $N = 1,486$ clean samples).
2. **Numerical Features (`dm.f`, `cp.f`, `ndf.f`, `adf.f`, `ash.f`, `wsc.f`, `starch.f`, `lignin.f`):**
   - Apply `SimpleImputer(strategy='median')` to handle the < 2.3% missing values without creating synthetic patterns.
   - For linear/regularized models, apply `StandardScaler()`. For tree-based models, scaling is optional.
3. **Categorical Features (`method`, `inhoculant`, `dose`, `delay`, `fao.class`, `maturity`):**
   - Fill missing categorical entries with `'Unknown'` or `'none'` (for `dose`).
   - Encode using `OneHotEncoder(handle_unknown='ignore', sparse_output=False)` inside a Scikit-Learn `ColumnTransformer`.

---

### F. Recommended Train/Test Splitting Strategy

A standard random `train_test_split(test_size=0.2)` is **HIGHLY RISKY** for this dataset because repeated samples from the same harvest batch, field plot, and micro-trial are present across rows. Random splitting would allow identical subplots and trials to appear in both train and test sets, causing optimistic performance estimates.

#### Recommended Cross-Validation Protocol:
1. **GroupKFold (Grouped by `ref.trial`):**
   - There are 5 distinct trial series (`ref.trial`).
   - Grouping on `ref.trial` ensures entire trial clusters remain unseen during training, evaluating true out-of-trial transferability.
2. **Temporal / Out-of-Year Validation:**
   - Alternatively, train on older experimental years (`y2016`, `y2017`, `y2018`, `y2019`) and test on subsequent years (`y2020`, `y2021`, `y2022`). This mirrors real-world deployment where a model trained on past seasons predicts future harvest seasons.

---

### G. Suitability of Random Forest as a Benchmark Model

**VERDICT: YES, HIGHLY APPROPRIATE AS A BENCHMARK MODEL**

Random Forest Regressor (`RandomForestRegressor`) is an ideal candidate for this task for several concrete reasons:
1. **Non-Linear Biological Interactions:** Fermentation quality is governed by non-linear interactions (e.g., packing delay is catastrophic when moisture is high, but less severe at lower moisture). Decision trees capture these interaction thresholds naturally without manual polynomial feature engineering.
2. **Robustness to Extreme Values:** Unlike ordinary least squares (OLS), tree ensembles are insensitive to biological outliers in proximate fiber or ash.
3. **Mixed Data Types:** Seamlessly integrates continuous chemical fractions with one-hot encoded agronomic management flags.
4. **Feature Importance Interpretability:** Provides MDI (Mean Decrease in Impurity) and Permutation Feature Importance, enabling dairy nutritionists to verify whether the model is learning sound biological rules (e.g., verifying that high WSC and homofermentative inoculants promote FQI, while long packing delay degrades FQI).
5. **Ensemble Benchmarking Plan:** Random Forest should be benchmarked alongside:
   - Baseline 1: Regularized Linear Model (`Ridge` / `ElasticNet`)
   - Baseline 2: Random Forest (`RandomForestRegressor`)
   - Baseline 3: Gradient Boosted Trees (`HistGradientBoostingRegressor` / `LightGBM`)
