# SmartSilageAI (SIH26111) — Dataset Extraction & Preprocessing Preparation Report

**Project:** Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers  
**Challenge ID:** SIH26111 (Ministry of Fisheries, Animal Husbandry & Dairying)  
**Target Variable:** `fqi` (Fermentation Quality Index)  
**Extracted File:** [`dataset/fqi_ml_raw.csv`](file:///c:/Users/Dhany/AIML_sih/dataset/fqi_ml_raw.csv) (Mirror: [`data/fqi_ml_raw.csv`](file:///c:/Users/Dhany/AIML_sih/data/fqi_ml_raw.csv))  
**Report Date:** 2026-10-08  

---

## 1. Row Count & Filtering Summary

| Metric | Count | Details |
|---|---|---|
| **Original Row Count** | **1,496** | Extracted from `elab.all` sheet in `datasilage.xlsx` |
| **Rows Removed** | **10** | Rows with missing ground truth target (`fqi` is NaN) |
| **Final Cleaned Row Count** | **1,486** | Retained for ML pipeline inspection |
| **Input Feature Columns** | **14** | Pre-ensiling nutrient traits and management variables |
| **Target Column** | **1** | `fqi` (Continuous Fermentation Quality Index) |
| **Total Columns in CSV** | **15** | Only the 14 features plus `fqi` |

### Why Rows Were Removed:
- In supervised machine learning, training requires a valid ground truth target label. Exactly **10 rows** in `elab.all` lacked the target value (`fqi = NaN`).
- The removed row index positions in `elab.all` were: `[685, 774, 1404, 1405, 1406, 1407, 1408, 1409, 1410, 1411]`.
- **Zero other rows were removed.** Rows with missing input features were strictly preserved so that missingness can be transparently evaluated before any imputation or preprocessing.

---

## 2. Selected Columns & Schema

The raw dataset contains only the **14 selected leak-free input features** and the target **`fqi`**:

### A. Fresh Nutritional / Proximate Features (8 Continuous Numeric):
1. `dm.f` — Fresh Forage Dry Matter (%)
2. `cp.f` — Fresh Forage Crude Protein (% DM)
3. `ndf.f` — Fresh Neutral Detergent Fiber (% DM)
4. `adf.f` — Fresh Acid Detergent Fiber (% DM)
5. `ash.f` — Fresh Total Ash (% DM)
6. `wsc.f` — Fresh Water-Soluble Carbohydrates (% DM)
7. `starch.f` — Fresh Starch (% DM)
8. `lignin.f` — Fresh Acid Detergent Lignin (% DM)

### B. Agronomic & Management Decisions (6 Categorical):
9. `method` — Silo containment type (`bags` vs `buckets`)
10. `inhoculant` — Bacterial additive type (`c`, `he`, `ho`)
11. `dose` — Additive dosage rate (`none`, `h`, `s`, `d`)
12. `delay` — Packing delay duration (`D0`, `D6`, `D20`)
13. `fao.class` — Crop maturity class (`ea`, `la`)
14. `maturity` — Kernel milk-line stage (`eh`, `mh`, `lh`, `vlh`)

### C. Continuous Target Variable:
15. `fqi` — Fermentation Quality Index (continuous score: 11.66 to 84.57)

---

## 3. Missing-Value Audit (N = 1,486)

| Column Name | Role | Data Type | Non-Null Count | Null Count | Null % | Status / Observation |
|---|---|:---:|:---:|:---:|:---:|---|
| `dm.f` | Feature | float64 | 1,466 | 20 | 1.35% | Low missingness; pre-ensiling moisture |
| `cp.f` | Feature | float64 | 1,466 | 20 | 1.35% | Low missingness; pre-ensiling protein |
| `ndf.f` | Feature | float64 | 1,454 | 32 | 2.15% | Low missingness; pre-ensiling cell wall fiber |
| `adf.f` | Feature | float64 | 1,464 | 22 | 1.48% | Low missingness; pre-ensiling lignocellulose |
| `ash.f` | Feature | float64 | 1,466 | 20 | 1.35% | Low missingness; mineral buffering capacity |
| `wsc.f` | Feature | float64 | 1,466 | 20 | 1.35% | Low missingness; fermentable sugar substrate |
| `starch.f` | Feature | float64 | 1,454 | 32 | 2.15% | Low missingness; energy reserve |
| `lignin.f` | Feature | float64 | 1,466 | 20 | 1.35% | Low missingness; structural polymer |
| `method` | Feature | string | 1,486 | 0 | 0.00% | 100% complete |
| `inhoculant` | Feature | string | 1,486 | 0 | 0.00% | 100% complete |
| `dose` | Feature | string | 1,450 | 36 | 2.42% | Low missingness; inoculant dosage rate |
| `delay` | Feature | string | 1,486 | 0 | 0.00% | 100% complete |
| `fao.class` | Feature | string | 1,415 | 71 | 4.78% | Moderate missingness; early vs late class |
| `maturity` | Feature | string | 1,315 | 171 | 11.51% | Moderate missingness; kernel milk-line stage |
| `fqi` | **Target** | float64 | 1,486 | **0** | **0.00%** | **100% complete (Target)** |

---

## 4. Categorical Features Unique Values Audit

Below are the exact categorical distribution counts across the 1,486 valid rows:

### 1. `method` (Silo Storage Type)
- **Unique Values:** 2
- **Distribution:**
  - `bags`: 1,000 samples (67.29%)
  - `buckets`: 486 samples (32.71%)
  - `NaN`: 0 samples (0.00%)

### 2. `inhoculant` (Inoculant Treatment)
- **Unique Values:** 3
- **Distribution:**
  - `c` (Control / Pure water): 1,130 samples (76.04%)
  - `he` (Heterofermentative, e.g. *L. buchneri*): 253 samples (17.03%)
  - `ho` (Homofermentative, e.g. *L. plantarum*): 103 samples (6.93%)
  - `NaN`: 0 samples (0.00%)

### 3. `dose` (Inoculant Application Dosage)
- **Unique Values:** 4 (+ NaN)
- **Distribution:**
  - `none` (No additive applied): 1,118 samples (75.24%)
  - `s` (Standard recommended dose): 182 samples (12.25%)
  - `d` (Double standard dose): 75 samples (5.05%)
  - `h` (Half standard dose): 75 samples (5.05%)
  - `NaN` (Unrecorded): 36 samples (2.42%)

### 4. `delay` (Chopping-to-Sealing Packing Delay)
- **Unique Values:** 3
- **Distribution:**
  - `D0` (Immediate packing, 0–4 hours): 1,214 samples (81.70%)
  - `D6` (Delayed packing, 6 hours): 165 samples (11.10%)
  - `D20` (Long delayed packing, 20–24 hours): 107 samples (7.20%)
  - `NaN`: 0 samples (0.00%)

### 5. `fao.class` (Crop FAO Maturity Class)
- **Unique Values:** 2 (+ NaN)
- **Distribution:**
  - `la` (Late maturity, FAO 600–700): 959 samples (64.54%)
  - `ea` (Early maturity, FAO ~200): 456 samples (30.69%)
  - `NaN` (Unrecorded): 71 samples (4.78%)

### 6. `maturity` (Phenological Harvest Stage)
- **Unique Values:** 4 (+ NaN)
- **Distribution:**
  - `mh` (Mid-harvest, 2/3 milk line): 434 samples (29.21%)
  - `eh` (Early harvest, 1/3 milk line): 433 samples (29.14%)
  - `lh` (Late harvest, 5 days after 2/3 milk line): 403 samples (27.12%)
  - `vlh` (Very late harvest): 45 samples (3.03%)
  - `NaN` (Unrecorded): 171 samples (11.51%)

---

## 5. Strict Data Integrity & Boundary Confirmations

1. **No Synthetic or Fake Data:**
   - Zero rows or columns contain imputed, simulated, or fabricated numbers.
   - All 1,486 rows represent raw physical observations from experimental trials conducted by the University of Padova.
2. **Original Excel File Untouched:**
   - `data/datasilage.xlsx` and `dataset/datasilage.xlsx` were opened exclusively in read-only mode via pandas.
   - SHA-256 Hash verified: `A90A5CCF1B1BA0084CBD0088BA3CDD14645308A2394E161FE7AD510B4266CDCD` (identical to original).
3. **No Premature Transformation:**
   - Numerical values remain in their original units (% and pure scores). No normalization, standardization, or Box-Cox transformations have been applied.
   - Categorical values remain in their raw text codes (`bags`, `c`, `D0`, etc.). No one-hot or ordinal encoding has been performed.
4. **No Artificial Binning:**
   - `fqi` remains a continuous float. No artificial Good/Moderate/Poor labels have been created.
5. **No Model Training:**
   - No Scikit-Learn regression or classification model was trained or fitted.
