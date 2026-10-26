# SmartSilageAI (SIH26111) — Final Candidate Model Report

**Project:** Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers  
**Challenge ID:** SIH26111 (Ministry of Fisheries, Animal Husbandry & Dairying)  
**Model Artifact:** [`dataset/fqi_model.joblib`](file:///c:/Users/Dhany/AIML_sih/dataset/fqi_model.joblib)  
**Model Type:** End-to-End Scikit-Learn Pipeline (`ColumnTransformer` + `RandomForestRegressor`)  
**Target Variable:** `fqi` (Fermentation Quality Index — Continuous Regression)  
**Date:** 2026-10-08  

---

## 1. Executive Summary & Non-Production Research Disclaimer

> [!CAUTION]
> **Scientific Integrity & Model Status Disclaimer:**  
> **This model is a RESEARCH PROTOTYPE and is NOT PRODUCTION-READY.**  
> - **Negative Out-of-Trial $R^2$:** Although this regularized 11-feature model achieved the lowest out-of-trial error among all tested candidates ($\text{MAE} = 9.506$, $\text{RMSE} = 11.541$), its average cross-trial coefficient of determination remained negative ($\mathbf{R^2 = -0.580 \pm 1.068}$) under rigorous 5-fold Leave-One-Trial-Out validation (`GroupKFold` on `ref.trial`).
> - **Biological Domain Shift:** The negative out-of-trial $R^2$ reflects genuine biological domain shifts between research trial campaigns (e.g. late-season harvest buffering shifts and micro-environmental variations).  
> - **Field Deployment Rule:** This model must **NOT** be deployed as an autonomous diagnostic authority on commercial dairy farms without prior local field calibration across Indian agro-climatic zones and Indian fodder cultivars.  
> - **Zero Synthetic Scores:** In compliance with scientific integrity rules, no artificial accuracy percentages, heuristic binning, or synthetic Good/Moderate/Poor classification labels were invented.

---

## 2. Dataset Information

* **Source File:** `elab.all` sheet in `data/datasilage.xlsx` (Mirror: `dataset/datasilage.xlsx`).
* **Original Excel Integrity:** The original Excel file was opened strictly in read-only mode and remains **100% untouched** (verified SHA-256 hash: `A90A5CCF1B1BA0084CBD0088BA3CDD14645308A2394E161FE7AD510B4266CDCD`).
* **Total Valid Samples:** Exactly **1,486 physical samples** (10 rows lacking ground-truth target `fqi` were excluded; zero rows were removed due to missing input features).
* **Zero Synthetic Data:** 100% of observations represent authentic physical and chemical observations from laboratory research trials conducted by the University of Padova.

---

## 3. Exact 11 Input Features & Target Definition

The model accepts raw data with the following **11 leak-free pre-ensiling and management features**:

### A. Fresh Nutritional / Chemical Traits (5 Continuous Numeric):
1. **`dm.f`**: Fresh Whole-Crop Dry Matter (%)
2. **`cp.f`**: Fresh Crude Protein (% DM)
3. **`ash.f`**: Fresh Total Ash (% DM)
4. **`wsc.f`**: Fresh Water-Soluble Carbohydrates (% DM)
5. **`starch.f`**: Fresh Starch Content (% DM)

*(Note: Collinear and trial-inconsistent fiber fractions `ndf.f`, `adf.f`, and `lignin.f` were permanently excluded based on the controlled feature experiment).*

### B. Harvest & Agronomic Management Decisions (6 Categorical):
6. **`method`**: Silo containment type (`bags` vs `buckets`)
7. **`inhoculant`**: Biological additive type (`c`=control/water, `he`=heterofermentative, `ho`=homofermentative)
8. **`dose`**: Inoculant application dosage (`none`, `h`=half, `s`=standard, `d`=double, `Unknown`)
9. **`delay`**: Chopping-to-sealing packing delay (`D0`=0–4h, `D6`=6h, `D20`=20–24h)
10. **`fao.class`**: FAO maturity class (`ea`=early ~200, `la`=late ~600–700, `Unknown`)
11. **`maturity`**: Kernel milk-line stage (`eh`=early 1/3, `mh`=mid 2/3, `lh`=late, `vlh`=very late, `Unknown`)

### C. Continuous Target Variable:
* **`fqi`**: Fermentation Quality Index (continuous numerical score, range: 11.66 – 84.57).

---

## 4. Preprocessing Architecture

The preprocessing stage is embedded directly into the saved Scikit-Learn `Pipeline` via a `ColumnTransformer`:
1. **Numerical Imputation:**  
   `SimpleImputer(strategy='median')` applied to the 5 numerical features.
2. **Categorical Imputation:**  
   `SimpleImputer(strategy='constant', fill_value='Unknown')` applied to the 6 categorical features (no default assumptions made for unrecorded entries).
3. **Categorical Encoding:**  
   `OneHotEncoder(handle_unknown='ignore', sparse_output=False)` produces 21 binary indicator columns.
4. **Feature Scaling:**  
   **No numerical scaling was applied.** Raw physical units (% DM, % CP, % Ash) are preserved directly for the tree-based estimator.

---

## 5. Exact Model Configuration

```python
RandomForestRegressor(
    n_estimators=500,
    max_depth=10,
    min_samples_leaf=3,
    max_features=0.8,
    random_state=42,
    n_jobs=-1
)
```

### Configuration Rationale:
* **Depth Cap (`max_depth=10`):** Prevents individual trees from memorizing trial-specific sampling quirks and noise.
* **Leaf Constraint (`min_samples_leaf=3`):** Smooths the leaf predictions, preventing isolated outlier splits.
* **Feature Subsampling (`max_features=0.8`):** Decorrelates the 500 trees by randomly selecting 80% of candidate features at each split, producing a more robust ensemble.

---

## 6. Validation Results (From Completed 5-Fold GroupKFold Experiment)

Validation was conducted using **5-Fold `GroupKFold` strictly grouped by `ref.trial`** (Leave-One-Trial-Out), with preprocessing fitted strictly on the training partition within every fold:

| Fold | Validation Trial ($N_{\text{val}}$ / $N_{\text{train}}$) | MAE | RMSE | $R^2$ | Validation Assessment |
|:---:|:---:|:---:|:---:|:---:|---|
| **Fold 1** | **Trial `1`** ($N=940$ / $N=546$) | 7.478 | 9.685 | -0.047 | Largest trial; near-zero $R^2$ despite small sample training |
| **Fold 2** | **Trial `2.a.1.a`** ($N=315$ / $N=1,171$) | **6.552** | **7.902** | **+0.479** | **Strongest generalization on unseen campaign** |
| **Fold 3** | **Trial `2.b`** ($N=87$ / $N=1,399$) | 14.402 | 16.957 | -2.626 | High grain/starch trial |
| **Fold 4** | **Trial `2.a.1.b`** ($N=84$ / $N=1,402$) | 13.900 | 16.826 | -0.421 | Late-season high-ash buffering shift |
| **Fold 5** | **Trial `2.a.2`** ($N=60$ / $N=1,426$) | **5.199** | **6.334** | -0.282 | Lowest absolute error; narrow trial variance |
| **SUMMARY** | **Mean ± Std Across Folds** | **9.506 ± 3.864** | **11.541 ± 4.496** | **-0.580 ± 1.068** | **Best configuration found** |

---

## 7. Final Model Refitting & Pipeline Artifact

### A. Final Refit on All 1,486 Valid Samples
Following standard machine learning protocol, after cross-validation proved this configuration superior to all alternatives:
- The complete pipeline (`ColumnTransformer` + `RandomForestRegressor`) was **refit on all 1,486 valid physical samples** in the dataset.
- Fitting on the entire dataset provides the final model with maximum biological diversity, combining bag and bucket trials, control and inoculated treatments, and multiple harvest seasons (2016–2022).

### B. Serialized Pipeline Artifact
* **Path:** [`dataset/fqi_model.joblib`](file:///c:/Users/Dhany/AIML_sih/dataset/fqi_model.joblib) (12.95 MB)
* **Direct Inference Support:** Raw data containing the 11 feature columns can be passed directly as a pandas DataFrame or dictionary to `pipeline.predict(X_raw)` without manual prior preprocessing.

---

## 8. Verification Checks

1. **File Existence:** [`dataset/fqi_model.joblib`](file:///c:/Users/Dhany/AIML_sih/dataset/fqi_model.joblib) exists and has size ~12.95 MB.
2. **Load Verification:** The joblib file loads cleanly as an instance of `sklearn.pipeline.Pipeline`.
3. **Inference Verification:** Evaluated on real dataset rows; produces valid continuous FQI predictions directly from raw feature inputs:
   - Sample 0 True FQI: 40.57 $\rightarrow$ Predicted FQI: 46.37
   - Sample 1 True FQI: 39.64 $\rightarrow$ Predicted FQI: 49.13
   - Sample 2 True FQI: 50.20 $\rightarrow$ Predicted FQI: 55.81
4. **Excel Integrity:** `data/datasilage.xlsx` and `dataset/datasilage.xlsx` remain completely untouched.
5. **No Premature Deployment:** No FastAPI endpoints were modified, and the model was not deployed to production.
