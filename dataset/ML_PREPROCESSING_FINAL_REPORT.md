# SmartSilageAI (SIH26111) — Final ML Preprocessing Report

**Project:** Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers  
**Challenge ID:** SIH26111 (Ministry of Fisheries, Animal Husbandry & Dairying)  
**Target Variable:** `fqi` (Fermentation Quality Index — Continuous Regression)  
**Input Data File:** [`dataset/fqi_ml_raw.csv`](file:///c:/Users/Dhany/AIML_sih/dataset/fqi_ml_raw.csv)  
**Pipeline Code:** [`dataset/fqi_preprocessing.py`](file:///c:/Users/Dhany/AIML_sih/dataset/fqi_preprocessing.py)  
**Report Date:** 2026-10-08  

---

## 1. Row Counts & Data Integrity Summary

| Metric | Count | Details |
|---|:---:|---|
| **Input Raw Rows (`fqi_ml_raw.csv`)** | **1,486** | All samples with valid ground-truth `fqi` |
| **Additional Rows Removed** | **0** | Zero rows were removed during preprocessing |
| **Final Preprocessed Rows** | **1,486** | 100% of rows preserved across splits |
| **Training Split (80%)** | **1,188** | Fitted strictly on `X_train` |
| **Testing / Validation Split (20%)** | **298** | Transformed using train-fitted preprocessor |
| **Output Feature Dimensions** | **29** | 8 numerical + 21 one-hot encoded categories |

---

## 2. Feature Definitions & Categorization

### A. Numerical Feature Columns (8 Features):
1. **`dm.f`**: Fresh Whole-Crop Dry Matter (%)
2. **`cp.f`**: Fresh Crude Protein (% DM)
3. **`ndf.f`**: Fresh Neutral Detergent Fiber (% DM)
4. **`adf.f`**: Fresh Acid Detergent Fiber (% DM)
5. **`ash.f`**: Fresh Total Ash (% DM)
6. **`wsc.f`**: Fresh Water-Soluble Carbohydrates (% DM)
7. **`starch.f`**: Fresh Starch (% DM)
8. **`lignin.f`**: Fresh Acid Detergent Lignin (% DM)

### B. Categorical Feature Columns (6 Features):
1. **`method`**: Silo containment type (`bags` vs `buckets`)
2. **`inhoculant`**: Bacterial additive applied (`c`=control, `he`=heterofermentative, `ho`=homofermentative)
3. **`dose`**: Inoculant application dosage (`none`, `h`=half, `s`=standard, `d`=double, `Unknown`)
4. **`delay`**: Chopping-to-sealing delay duration (`D0`=0–4h, `D6`=6h, `D20`=20–24h)
5. **`fao.class`**: FAO crop maturity class (`ea`=early ~200, `la`=late ~600–700, `Unknown`)
6. **`maturity`**: Kernel milk-line stage (`eh`=early 1/3, `mh`=mid 2/3, `lh`=late, `vlh`=very late, `Unknown`)

### C. Continuous Target Variable:
* **`fqi`**: Fermentation Quality Index (continuous numerical score, 11.66 to 84.57)

---

## 3. Missing Values Before Preprocessing ($N = 1,486$)

| Feature | Data Type | Null Count | Null % | Imputation Strategy Applied |
|---|:---:|:---:|:---:|---|
| `dm.f` | float64 | 20 | 1.35% | Median Imputation (fitted on train split) |
| `cp.f` | float64 | 20 | 1.35% | Median Imputation (fitted on train split) |
| `ndf.f` | float64 | 32 | 2.15% | Median Imputation (fitted on train split) |
| `adf.f` | float64 | 22 | 1.48% | Median Imputation (fitted on train split) |
| `ash.f` | float64 | 20 | 1.35% | Median Imputation (fitted on train split) |
| `wsc.f` | float64 | 20 | 1.35% | Median Imputation (fitted on train split) |
| `starch.f` | float64 | 32 | 2.15% | Median Imputation (fitted on train split) |
| `lignin.f` | float64 | 20 | 1.35% | Median Imputation (fitted on train split) |
| `method` | string | 0 | 0.00% | None needed (100% complete) |
| `inhoculant` | string | 0 | 0.00% | None needed (100% complete) |
| `dose` | string | 36 | 2.42% | Constant Imputation: `'Unknown'` (no default assumed) |
| `delay` | string | 0 | 0.00% | None needed (100% complete) |
| `fao.class` | string | 71 | 4.78% | Constant Imputation: `'Unknown'` |
| `maturity` | string | 171 | 11.51% | Constant Imputation: `'Unknown'` |
| **`fqi` (Target)** | float64 | **0** | **0.00%** | **Target 100% complete; untouched** |

---

## 4. Imputation, Encoding & Scaling Decisions

### A. Numerical Imputation:
* **Method:** `SimpleImputer(strategy='median')`
* **Leakage Control:** The median values were calculated **strictly from `X_train`** (1,188 rows) and applied without recomputing to `X_test` (298 rows).

### B. Categorical Imputation:
* **Method:** `SimpleImputer(strategy='constant', fill_value='Unknown')`
* **Rule Adherence:** No heuristic assumption was made (e.g. missing `dose` was NOT assumed to mean `'none'`). Unrecorded values are explicitly represented as an `'Unknown'` category to allow the models to capture unobserved data patterns neutrally.

### C. Categorical Encoding:
* **Method:** `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`
* **Generated Dimensions:** 21 binary indicator columns:
  * `method` (2): `method_bags`, `method_buckets`
  * `inhoculant` (3): `inhoculant_c`, `inhoculant_he`, `inhoculant_ho`
  * `dose` (5): `dose_Unknown`, `dose_d`, `dose_h`, `dose_none`, `dose_s`
  * `delay` (3): `delay_D0`, `delay_D20`, `delay_D6`
  * `fao.class` (3): `fao.class_Unknown`, `fao.class_ea`, `fao.class_la`
  * `maturity` (5): `maturity_Unknown`, `maturity_eh`, `maturity_lh`, `maturity_mh`, `maturity_vlh`
* **Total Feature Vector:** $8 \text{ (numerical)} + 21 \text{ (one-hot)} = \mathbf{29} \text{ features}$.

### D. Scaling & Normalization:
* **Was Numerical Scaling Used?** **NO.**
* **Rationale:** 
  1. Primary tree-based benchmark models (`RandomForestRegressor`, `HistGradientBoostingRegressor`) are invariant to monotonic scale transformations; keeping raw physical units preserves interpretability (e.g. % DM, % CP).
  2. For linear regularized models (`Ridge`), feature scaling can be attached as a dedicated `StandardScaler()` step inside its specific training pipeline without altering the base dataset.

---

## 5. Strict Verification & Data Protection Confirmations

1. **Target `fqi` Untouched:**
   - The continuous numerical target `fqi` was separated prior to feature transformation.
   - Zero scaling, clipping, binning, or modifications were applied to `y_train` or `y_test`.
   - Train Target: $N = 1,188$, Mean = $52.55 \pm 10.78$, Min = $11.66$, Max = $84.57$.
   - Test Target: $N = 298$, Mean = $51.84 \pm 10.45$, Min = $25.24$, Max = $83.30$.
2. **Zero Synthetic / Fake Data Created:**
   - No synthetic oversampling, SMOTE, or fabricated observations were introduced. All values originate from the 1,486 real laboratory trials.
3. **Original Excel File Intact:**
   - `datasilage.xlsx` (in both `data/` and `dataset/`) remains completely untouched.
   - Verified SHA-256 Hash: `A90A5CCF1B1BA0084CBD0088BA3CDD14645308A2394E161FE7AD510B4266CDCD`.
4. **Leak-Free Preprocessing Artifacts Generated:**
   - [`dataset/X_train_preprocessed.csv`](file:///c:/Users/Dhany/AIML_sih/dataset/X_train_preprocessed.csv) (1,188 rows × 29 features)
   - [`dataset/X_test_preprocessed.csv`](file:///c:/Users/Dhany/AIML_sih/dataset/X_test_preprocessed.csv) (298 rows × 29 features)
   - [`dataset/y_train.csv`](file:///c:/Users/Dhany/AIML_sih/dataset/y_train.csv) (1,188 rows)
   - [`dataset/y_test.csv`](file:///c:/Users/Dhany/AIML_sih/dataset/y_test.csv) (298 rows)
   - [`dataset/fqi_preprocessor.joblib`](file:///c:/Users/Dhany/AIML_sih/dataset/fqi_preprocessor.joblib) (Fitted Scikit-Learn transformer)
5. **No Model Training:**
   - Zero models have been trained. The preprocessing stage is complete and frozen for inspection.
