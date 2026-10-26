# SmartSilageAI (SIH26111) — Controlled Domain-Robust Feature Experiment Report

**Project:** Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers  
**Challenge ID:** SIH26111 (Ministry of Fisheries, Animal Husbandry & Dairying)  
**Experiment:** Controlled Comparison of Baseline 14-Feature Set vs. Domain-Robust 11-Feature Set  
**Model Architecture:** `RandomForestRegressor(n_estimators=300, random_state=42)` (identical configuration)  
**Validation Strategy:** 5-Fold `GroupKFold` grouped strictly by `ref.trial` (Leave-One-Trial-Out)  
**Dataset Reference:** `elab.all` sheet in `data/datasilage.xlsx` (1,486 valid samples)  
**Date:** 2026-10-08  

---

## Executive Summary & Non-Production Statement

> [!WARNING]
> **Production Readiness Statement:**  
> **Neither model is production-ready.**  
> Although removing the unstable fiber features (`ndf.f`, `adf.f`, `lignin.f`) resulted in substantial improvements in out-of-trial generalization (reducing MAE by 1.29 points and reducing RMSE by 1.45 points), the overall average $R^2$ remains negative ($-0.747$). Deploying this model directly to commercial dairy farms is not yet justified without regional field calibration.

---

## 1. Experimental Setup & Hypotheses

### A. Background & Motivation
In our diagnostic analysis ([`dataset/ML_GENERALIZATION_ANALYSIS.md`](file:///c:/Users/Dhany/AIML_sih/dataset/ML_GENERALIZATION_ANALYSIS.md)), cross-trial correlations revealed that plant fiber fractions (`ndf.f`, `adf.f`, and `lignin.f`) exhibited **severe correlation sign inversions** across different research trials:
* In Trial `2.a.1.a`, ADF correlated positively with FQI ($r = +0.81$).
* In Trial `2.b`, ADF correlated negatively with FQI ($r = -0.40$).

### B. Hypothesis
Removing these 3 unstable, contradictory fiber features will prevent decision trees from memorizing trial-specific fiber thresholds, thereby forcing the ensemble to rely on universally consistent biochemical drivers (`dm.f`, `cp.f`, `ash.f`, `wsc.f`, `starch.f`, and management variables), which should improve out-of-trial generalization.

### C. Feature Sets Under Comparison:
1. **Baseline 14-Feature Set:**  
   `dm.f`, `cp.f`, `ndf.f`, `adf.f`, `ash.f`, `wsc.f`, `starch.f`, `lignin.f`, `method`, `inhoculant`, `dose`, `delay`, `fao.class`, `maturity`
2. **Experimental 11-Feature Set (Removed: `ndf.f`, `adf.f`, `lignin.f`):**  
   `dm.f`, `cp.f`, `ash.f`, `wsc.f`, `starch.f`, `method`, `inhoculant`, `dose`, `delay`, `fao.class`, `maturity`

### D. Controlled Evaluation Rules:
* Identical model: `RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)`.
* Identical cross-validation: `GroupKFold(n_splits=5)` grouped on `ref.trial`.
* Identical preprocessing: Median imputation for numeric, constant `'Unknown'` for categorical, `OneHotEncoder(handle_unknown='ignore')` fitted strictly on `X_train` inside each fold.
* Zero hyperparameter tuning.

---

## 2. Fold-by-Fold Comparison

| Fold | Validation Trial ($N_{\text{val}}$ / $N_{\text{train}}$) | Metric | Baseline (14 Features) | Experimental (11 Features) | Delta ($\Delta = \text{Exp} - \text{Base}$) | Impact |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Fold 1** | **Trial `1`**<br>($N_{\text{val}}=940$, $N_{\text{train}}=546$) | **MAE**<br>**RMSE**<br>**$R^2$** | 8.333<br>10.915<br>-0.330 | **7.808**<br>**10.178**<br>**-0.156** | **-0.525**<br>**-0.737**<br>**+0.174** | ✅ **Improved** |
| **Fold 2** | **Trial `2.a.1.a`**<br>($N_{\text{val}}=315$, $N_{\text{train}}=1,171$) | **MAE**<br>**RMSE**<br>**$R^2$** | 6.922<br>8.412<br>+0.409 | **6.844**<br>**8.136**<br>**+0.447** | **-0.079**<br>**-0.276**<br>**+0.038** | ✅ **Improved** |
| **Fold 3** | **Trial `2.b`**<br>($N_{\text{val}}=87$, $N_{\text{train}}=1,399$) | **MAE**<br>**RMSE**<br>**$R^2$** | **14.257**<br>**17.096**<br>**-2.686** | 15.033<br>18.027<br>-3.099 | +0.776<br>+0.932<br>-0.413 | ⚠️ Slightly Degraded |
| **Fold 4** | **Trial `2.a.1.b`**<br>($N_{\text{val}}=84$, $N_{\text{train}}=1,402$) | **MAE**<br>**RMSE**<br>**$R^2$** | 17.883<br>21.568<br>-1.335 | **14.831**<br>**17.943**<br>**-0.616** | **-3.052**<br>**-3.625**<br>**+0.719** | ✅ **Substantially Improved** |
| **Fold 5** | **Trial `2.a.2`**<br>($N_{\text{val}}=60$, $N_{\text{train}}=1,426$) | **MAE**<br>**RMSE**<br>**$R^2$** | 8.581<br>9.931<br>-2.152 | **5.014**<br>**6.411**<br>**-0.314** | **-3.567**<br>**-3.521**<br>**+1.839** | ✅ **Dramatically Improved** |

---

## 3. Overall Benchmark Comparison Across All 5 Folds

| Metric | Baseline (14 Features) | Experimental (11 Features) | Net Absolute Change | Percentage Improvement |
|---|:---:|:---:|:---:|:---:|
| **Mean MAE** | 11.195 ± 4.180 | **9.906 ± 4.201** | **-1.289** | **11.5% Error Reduction** |
| **Mean RMSE** | 13.584 ± 4.966 | **12.139 ± 4.920** | **-1.445** | **10.6% Error Reduction** |
| **Mean $R^2$** | -1.219 ± 1.138 | **-0.747 ± 1.226** | **+0.472** | **38.7% Relative Improvement** |

---

## 4. Scientific Findings & Interpretation

### A. Did Removing `ndf.f`, `adf.f`, and `lignin.f` Improve or Worsen Generalization?
**It substantially IMPROVED out-of-trial generalization across almost every dimension:**
1. **Consistency Across Folds:** In **4 out of 5 folds (80% of folds)**, the 11-feature model achieved lower error and higher $R^2$:
   - In Fold 5 (Trial `2.a.2`), MAE dropped dramatically from **8.58** to **5.01** (a 41.6% error drop).
   - In Fold 4 (Trial `2.a.1.b`), MAE dropped from **17.88** to **14.83** (a 3.05-point error reduction).
   - In Fold 1 (Trial `1`, the largest trial with 940 samples), MAE decreased from **8.33** to **7.81**.
   - In Fold 2 (Trial `2.a.1.a`, the main out-of-trial validation set with 315 samples), $R^2$ rose from **+0.409** to **+0.447**.
2. **Mean Error Threshold:** For the first time, average out-of-trial MAE dropped below 10 points (**9.91 points**).
3. **Only Fold 3 Degraded Slightly:** In Fold 3 (Trial `2.b`, 87 samples), MAE increased slightly from 14.26 to 15.03 (+0.78 points). As observed in our correlation analysis, Trial `2.b` was an outlier trial where starch had an atypical positive correlation with FQI.

### B. Biological & Statistical Explanation
* **Removal of Conflicting Decision Boundaries:** When `ndf.f` and `adf.f` were present, trees made split decisions based on fiber thresholds that were valid only for specific trials. Because fiber fractions reverse their relationship with FQI between trials (due to differing harvest heights and grain-to-stover ratios), those trees made severe prediction errors on unseen trials.
* **Emphasis on Universal Bio-Chemical Drivers:** With the collinear and unstable fiber features removed, the Random Forest relied on universally reliable indicators:
  - `dm.f` (dry matter — consistently negative correlation with FQI across all trials).
  - `cp.f` and `ash.f` (protein and mineral buffering capacity).
  - `wsc.f` (water-soluble carbohydrates — primary microbial fuel).
  - `starch.f` (grain development).
  - Management decisions (`method`, `inhoculant`, `dose`, `delay`, `maturity`).

---

## 5. Recommendation on Which Feature Set to Retain

### **OFFICIAL RECOMMENDATION: RETAIN THE 11-FEATURE EXPERIMENTAL SET**

The **11-Feature Set** (`dm.f`, `cp.f`, `ash.f`, `wsc.f`, `starch.f`, `method`, `inhoculant`, `dose`, `delay`, `fao.class`, `maturity`) should be retained as the new primary feature baseline for all future modeling and tuning for the following reasons:
1. **Demonstrated Empirical Superiority:** Lower average MAE (9.91 vs 11.20) and lower RMSE (12.14 vs 13.58) across out-of-trial splits.
2. **Simpler, More Parsimonious Model:** Eliminates 3 laboratory fiber parameters (`ndf.f`, `adf.f`, `lignin.f`), reducing collinearity and feature noise.
3. **On-Farm Practicality (SIH26111):** Measuring fewer laboratory proximate fiber traits reduces input friction for field extension workers and farmers while achieving better out-of-trial transferability.

---

## 6. Strict Verification Confirmations

1. **Original Excel File Untouched:** SHA-256 hash `A90A5CCF...` verified identical.
2. **Existing Baseline Report Intact:** [`dataset/ML_MODEL_BENCHMARK_REPORT.md`](file:///c:/Users/Dhany/AIML_sih/dataset/ML_MODEL_BENCHMARK_REPORT.md) was preserved and not overwritten.
3. **Zero Synthetic / Fake Data:** All evaluations performed on authentic laboratory observations.
4. **No Premature Deployment:** Model remains in experimental benchmarking mode.
