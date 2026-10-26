# SmartSilageAI (SIH26111) — Dataset Analysis Report: `datasilage.xlsx`

**Project:** Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers  
**Dataset File:** `data/datasilage.xlsx` (Mirror: `dataset/datasilage.xlsx`)  
**Analysis Date:** 2026-10-08  
**Dataset Source:** University of Padova / Andrighetto et al. (2018), Serva et al. (2021) experimental silage trials.

---

## 1. Sheet Overview & Selection

The workbook contains **4 sheets**:

| Sheet Name | Rows | Columns | Purpose / Description | Recommendation |
|---|---|---|---|---|
| `dictionary keys` | 54 | 3 | Metadata & scientific dictionary defining variables, units, literature citations (Andrighetto 2018, Serva 2021), and treatment keys. | **Reference Only** |
| `elab.all` | **1,496** | **52** | **Master dataset** containing all ensiling trials (2016–2022), bag and bucket methods, pre-ensiled forage proximate traits (`.f`), post-ensiled silage traits (`.s`), fermentation acids, DM loss, and Fermentation Quality Index (`fqi`). | **PRIMARY SHEET TO USE** |
| `elab.temp` | 160 | 19 | Subset experiment tracking thermal sensors and aerobic deterioration events over time (`event`, `time.event`, `cumulative.temperature`). | Specialized subset (Thermal/Aerobic stability only) |
| `elab.buckets` | 402 | 113 | Bucket-only experiment subdivided into vertical bucket strata/layers (`l.s`, `l.1`, `l.3`, `l.5`). Missing unified `fqi`. | Experimental subgroup (Exclude from main pipeline) |

**Conclusion:** **`elab.all`** is the main dataset sheet to use for model development.

---

## 2. Key Silage Quality Parameters Identified

Parameters in `elab.all` follow a clear scientific naming convention:
- **`.f` suffix:** Fresh forage characteristics (measured at harvest before ensiling).
- **`.s` suffix:** Silage characteristics (measured post-fermentation in ensiled feed).

| Quality Parameter | Dataset Column(s) | Role / Unit | Missing Count | Missing % |
|---|---|---|---|---|
| **pH** | `pH` | Fermentation acidity (pure number) | 13 | 0.87% |
| **Dry Matter** | `dm.f` (fresh), `dm.s` (silage) | Dry matter content (%) | 22 (fresh), 10 (silage) | 1.47%, 0.67% |
| **Crude Protein** | `cp.f` (fresh), `cp.s` (silage) | Crude protein (% DM) | 22 (fresh), 10 (silage) | 1.47%, 0.67% |
| **NDF (Neutral Detergent Fiber)** | `ndf.f` (fresh), `ndf.s` (silage) | Structural cell-wall fiber (% DM) | 34 (fresh), 10 (silage) | 2.27%, 0.67% |
| **ADF (Acid Detergent Fiber)** | `adf.f` (fresh), `adf.s` (silage) | Lignocellulose fiber (% DM) | 24 (fresh), 10 (silage) | 1.60%, 0.67% |
| **Ash** | `ash.f` (fresh), `ash.s` (silage) | Total mineral content (% DM) | 22 (fresh), 10 (silage) | 1.47%, 0.67% |
| **Lactic Acid** | `lactic.ac.s` | Primary desirable lactic acid (% DM) | 10 | 0.67% |
| **Acetic Acid** | `acetic.ac.s` | Fermentation acetic acid (% DM) | 10 | 0.67% |
| **Propionic Acid** | `propionic.ac.s` | Propionic acid (% DM) | 10 | 0.67% |
| **Butyric Acid** | `butyric.ac.s` | Clostridial spoilage marker (% DM) | 10 | 0.67% |
| **Dry Matter Loss / Retention** | `dm.loss`, `dm.ret` | Fermentation biomass loss (%) | 95 | 6.35% |
| **FQI** | `fqi` | Fermentation Quality Index (continuous) | 10 | 0.67% |

---

## 3. What Does `fqi` Represent?

Based on the `dictionary keys` sheet:
> **Citation:** *Andrighetto I, Serva L, Gazziero M, Tenti S, Mirisola M, Garbin E, Contiero B, Grandis D, Marchesini G. 2018. Proposal and validation of new indexes to evaluate maize silage fermentative quality in lab-scale ensiling conditions through the use of a receiver operating characteristic analysis. Anim Feed Sci Technol. 242:31–40.*

- **`fqi`** stands for **Fermentation Quality Index** (specifically Index $I_1$ from the Andrighetto et al. 2018 study).
- It is a validated, continuous quantitative score (in this dataset ranging from **11.66 to 84.57**, with a mean of **52.40** and standard deviation of **10.72**).
- It evaluates the overall preservation success of ensiled forage by penalizing undesirable fermentation metabolites (butyric acid, high ammonia-N, high pH, excessive volatile fatty acids) and rewarding lactic acid dominance.

---

## 4. Data Leakage Risks & Mathematical Dependencies

### Critical Risk 1: FQI is Calculated Directly From Post-Ensiling Acids
- By definition in animal science literature (Andrighetto et al. 2018), Index $I_1$ (`fqi`) is an algebraic index formulated directly from:
  $$\text{FQI} = f(\text{pH}, \text{lactic acid}, \text{acetic acid}, \text{propionic acid}, \text{butyric acid}, \text{ammonia}, \text{ethanol})$$
- Linear regression confirms that these post-ensiled parameters alone explain over **82.8%** of the variance of `fqi` directly.
- **Leakage Warning:** If we set `fqi` as the ML target variable, we **MUST NOT** include `lactic.ac.s`, `acetic.ac.s`, `butyric.ac.s`, `propionic.ac.s`, `ammonia.s`, or `ethanol.s` as input features. Doing so would constitute direct mathematical leakage—the model would just memorize the formula rather than predicting true silage fermentation dynamics.

### Critical Risk 2: Field Usability vs. Wet Chemistry (SIH26111 Objective)
- The core SIH problem statement targets **dairy farmers in the field**. A dairy farmer cannot measure HPLC acids (lactic, butyric, propionic) or Kjeldahl ammonia on-farm.
- A legitimate ML model must use inputs available to the farmer:
  1. **Pre-ensiling harvest features:** Fresh forage traits (`dm.f`, `cp.f`, `ndf.f`, `adf.f`, `wsc.f`, `starch.f`) + harvest management (`delay`, `density`, `inoculant`, `maturity`).
  2. **Or On-farm ensiled screening:** Easy field measurements (`pH`, `dm.s` / moisture, temperature, visual signs) to screen quality or predict nutrition/losses without expensive lab chromatography.

### Critical Risk 3: Exact Complement Collinearity
- `dm.ret` is simply $100 - \text{dm.loss}$. Never use both in the same feature set.

### Critical Risk 4: Spurious Identifiers & Formatting Artifacts
- Columns like `Unnamed: 25` (100% null Excel blank column) must be removed.
- Trial identifiers (`ref.trial`, `ref.article`, `fresh.id`, `silage.id`, `ref.fresh`, `ref.silage`) must be excluded to prevent overfitting on specific research trials or spectrometers.

---

## 5. Column Categorization for ML

### Columns to Keep / Feature Candidates:
1. **Fresh Harvest Nutrients (Pre-ensiling):**
   - `dm.f` (Dry matter, fresh)
   - `cp.f` (Crude protein, fresh)
   - `ndf.f` (Neutral detergent fiber, fresh)
   - `adf.f` (Acid detergent fiber, fresh)
   - `ash.f` (Ash, fresh)
   - `wsc.f` (Water-soluble carbohydrates — key substrate for lactic bacteria)
   - `starch.f` (Starch content)
   - `lignin.f` (Lignin content)
2. **Crop & Ensiling Management Variables:**
   - `inoculant` / `inhoculant` (Control vs Heterofermentative vs Homofermentative)
   - `dose` (Inoculant dosage)
   - `delay` (Pre-packing delay: D0, D6, D20 hours)
   - `method` (Bags vs Buckets)
   - `fao.class` (Early vs Late crop maturity class)
   - `maturity` (Harvest stage: 1/3 milk line, 2/3 milk line, etc.)
   - `density` / `density.1` (Compaction density, where non-null)
3. **Post-Ensiled Field Screening Metrics (Only if evaluating opened silage):**
   - `pH`
   - `dm.s` (Post-fermentation DM / Moisture)
   - `cp.s`, `ndf.s`, `adf.s`, `ash.s` (Proximate NIRS profile)

### Columns to Exclude:
- `Unnamed: 25` (100% NaN)
- `ref.trial`, `ref.article`, `fresh.id`, `silage.id` (Database IDs / trial IDs)
- `ref.fresh`, `ref.silage` (Spectrometer model tags)
- `dm.ret` (Duplicate mirror of `dm.loss`)
- `lignin.s`, `wsc.s`, `porosity`, `density.1` (High missingness > 45-55%, unless specifically imputed)
- `lactic.ac.s`, `acetic.ac.s`, `propionic.ac.s`, `butyric.ac.s`, `ethanol.s`, `ammonia.s` (Post-ensiled fermentation acids — exclude if predicting `fqi` to avoid leakage!)

---

## 6. Missing-Value Analysis & Strategy

In `elab.all`:
- **Core Nutrients & Acids:** Very high data completeness (< 2% missing).
  - `fqi`: Only 10 missing rows (0.67%).
  - `dm.f`, `cp.f`, `ndf.f`, `adf.f`, `ash.f`: Only 22–34 missing rows (1.4% – 2.3%).
  - Rows with missing targets can simply be dropped.
- **High-Missing Columns (>40% missing):**
  - `density` (96.79% missing) — string column, sparsely recorded; `density.1` numeric has 55.68% missing.
  - `lignin.s` (55.55% missing).
  - `porosity` (55.48% missing).
  - `wsc.s` (45.12% missing).
  - These columns should either be dropped from the primary feature baseline or handled with dedicated iterative/KNN imputation.
- **Categorical Columns with Missingness:**
  - `maturity` (11.97% missing), `hybrid` (4.75% missing), `fao.class` (4.75% missing).
  - Strategy: Impute with `'Unknown'` category before one-hot/ordinal encoding.

---

## 7. Possible ML Target Variables

1. **Target Option 1: Fermentation Quality Index (`fqi`) — Continuous Regression**
   - Real, scientifically validated target in the dataset.
   - Predicts fermentation quality score directly without synthetic binning.
   - Requires excluding post-ensiled acids from input features to maintain scientific validity.
2. **Target Option 2: Fermentation Dry Matter Loss (`dm.loss`) — Continuous Regression**
   - Crucial economic parameter for dairy farmers: represents feed shrinkage and nutrient loss during storage.
3. **Target Option 3: Post-Ensiled pH (`pH`) — Continuous Regression**
   - Predictable from fresh forage buffering capacity (`dm.f`, `wsc.f`, `cp.f`) and management delay/inoculants.

---

## 8. Recommended Next Steps for ML Pipeline

1. **Clean & Parse Features:**
   - Drop uninformative ID columns (`ref.trial`, `fresh.id`, `silage.id`, `Unnamed: 25`).
   - Parse categorical variables cleanly (`inoculant`, `delay`, `dose`, `fao.class`, `maturity`).
2. **Handle Missing Values Without Data Fabrication:**
   - Drop the 10 rows lacking the target variable (`fqi`).
   - Use median imputation or KNN imputation for minor missing numeric features (< 2.5%).
   - Encode missing categoricals as `'missing'`.
3. **Define Leakage-Safe Feature Sets:**
   - **Feature Set A (Pre-Ensiling Harvest Predictor):** Uses only fresh crop parameters (`.f`) and management conditions (`inoculant`, `delay`, `density`) to predict outcome `fqi` or `dm.loss`.
   - **Feature Set B (Rapid Field Silage Quality Estimator):** Uses farmer-accessible metrics (`pH`, moisture/`dm.s`, basic proximate NIR metrics) without HPLC acids.
4. **Train & Benchmark Real Regression Models:**
   - Train real Scikit-Learn models (Ridge, ElasticNet, GradientBoostingRegressor, RandomForestRegressor).
   - Evaluate with nested Cross-Validation ($R^2$, MAE, RMSE).
   - Export models and connect them to the FastAPI inference engine (`assessment_service.py`).
