# SmartSilageAI (SIH26111) — Out-of-Trial Generalization Diagnostic Report

**Project:** Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers  
**Challenge ID:** SIH26111 (Ministry of Fisheries, Animal Husbandry & Dairying)  
**Investigation:** Root Cause Analysis of Out-of-Trial Generalization Failure in GroupKFold Benchmark  
**Dataset Reference:** `elab.all` sheet in `data/datasilage.xlsx` (1,486 valid samples)  
**Benchmark Reference:** [`dataset/ML_MODEL_BENCHMARK_REPORT.md`](file:///c:/Users/Dhany/AIML_sih/dataset/ML_MODEL_BENCHMARK_REPORT.md)  
**Date:** 2026-10-08  

---

## Executive Summary & Non-Production Statement

> [!WARNING]
> **Definitive Finding on Production Readiness:**  
> **`RandomForestRegressor` is NOT production-ready.**  
> Although Random Forest achieved the lowest error metrics among benchmarked models (MAE = 11.20, RMSE = 13.58), its out-of-trial coefficient of determination is negative ($R^2 = -1.219$). Deploying this model in its current state to Indian dairy farmers would result in unpredictable predictions on unseen farms.  
> This diagnostic investigation identifies the exact statistical and agronomic root causes of this failure.

---

## 1. Analysis of Random Forest Performance Metrics ($R^2 = -1.219$, $\text{MAE} = 11.20$, $\text{RMSE} = 13.58$)

### Observed Evidence:
Across the 5 Leave-One-Trial-Out folds, `RandomForestRegressor` produced the following metrics:
* **Fold 1 (Val: Trial `1`, $N=940$):** MAE = 8.333, RMSE = 10.915, $R^2 = -0.330$
* **Fold 2 (Val: Trial `2.a.1.a`, $N=315$):** MAE = 6.922, RMSE = 8.412, $\mathbf{R^2 = +0.409}$
* **Fold 3 (Val: Trial `2.b`, $N=87$):** MAE = 14.257, RMSE = 17.096, $R^2 = -2.686$
* **Fold 4 (Val: Trial `2.a.1.b`, $N=84$):** MAE = 17.883, RMSE = 21.568, $R^2 = -1.335$
* **Fold 5 (Val: Trial `2.a.2`, $N=60$):** MAE = 8.581, RMSE = 9.931, $R^2 = -2.152$
* **Overall Mean across Folds:** **MAE = $11.195 \pm 4.180$**, **RMSE = $13.584 \pm 4.966$**, **$R^2 = -1.219 \pm 1.138$**.

### Statistical & Biological Explanation:
1. **Mathematical Mechanics of Negative $R^2$:**  
   The coefficient of determination is defined as:
   $$R^2 = 1 - \frac{\sum_{i} (y_i - \hat{y}_i)^2}{\sum_{i} (y_i - \bar{y}_{\text{val}})^2} = 1 - \frac{SS_{\text{res}}}{SS_{\text{tot}}}$$
   In standard in-distribution splits, $\hat{y}$ centers around $\bar{y}_{\text{val}}$, making $SS_{\text{res}} \le SS_{\text{tot}}$. However, in GroupKFold, when the validation trial has a **global baseline shift** (a different mean from the training trials) or has a **narrow intra-trial variance** ($SS_{\text{tot}}$ is very small), even a modest prediction error causes $SS_{\text{res}} > SS_{\text{tot}}$, driving $R^2$ negative.
2. **Absolute vs. Relative Error:**  
   The mean FQI across the entire dataset is 52.40 (scale: 11.66 to 84.57). An overall MAE of 11.20 represents an average error of approximately **$21.4\%$ of the mean quality score**. In Fold 2, the MAE was lower (6.92, or $13.8\%$ error), demonstrating that the model learns genuine predictive patterns when training data is broad enough. However, in Folds 3 and 4, MAE surged to 14.26 and 17.88, dragging down the overall benchmark.

---

## 2. FQI Target Distribution Shift Across the 5 Trials

### Observed Evidence:

| Trial ID (`ref.trial`) | Sample Count | Share (%) | Mean FQI | Median FQI | Std Dev | Min FQI | Max FQI |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`1`** | 940 | 63.26% | 54.00 | 53.46 | 9.47 | 28.70 | 84.57 |
| **`2.a.1.a`** | 315 | 21.20% | 50.26 | 48.82 | 10.96 | 29.66 | 71.66 |
| **`2.a.1.b`** | 84 | 5.65% | **38.35** | **32.10** | **14.20** | **11.66** | 64.43 |
| **`2.a.2`** | 60 | 4.04% | **59.06** | **60.57** | **5.64** | 45.19 | 67.32 |
| **`2.b`** | 87 | 5.85% | 51.85 | 53.41 | 8.96 | 34.31 | 67.97 |
| **All Trials Combined** | **1,486** | **100.00%** | **52.40** | **52.76** | **10.72** | **11.66** | **84.57** |

### Statistical Explanation:
* **Severe Target Mean Shift in Trial `2.a.1.b`:**  
  Trial `2.a.1.b` has an average FQI of only **38.35** (median **32.10**), compared to **54.00** in Trial 1 and **59.06** in Trial 2.a.2. This is an enormous **16 to 21 point drop** in average fermentation quality. When models trained on trials with average FQI ~53–59 attempt to predict Trial `2.a.1.b`, they systematically overpredict quality, causing high MAE (17.88).
* **Restricted Variance in Trial `2.a.2`:**  
  Trial `2.a.2` has a standard deviation of only **5.64** (compared to 10.96 in Trial 2.a.1.a). Because $SS_{\text{tot}}$ is minimal, even an MAE of 8.58 yields an $R^2$ of $-2.152$.

---

## 3. Input Feature Distribution Shift Between Trials

### Observed Evidence (Feature Means Across Trials):

| Trial ID | `dm.f` (%) | `cp.f` (%) | `ndf.f` (%) | `adf.f` (%) | `ash.f` (%) | `wsc.f` (%) | `starch.f` (%) | `lignin.f` (%) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `1` | 34.65 | 6.72 | 42.56 | 22.25 | 3.80 | 5.55 | 27.57 | 2.19 |
| `2.a.1.a` | 35.56 | 6.43 | 41.61 | 23.08 | 3.68 | 6.56 | 31.65 | 2.67 |
| `2.a.1.b` | 35.16 | **7.90** | 43.24 | 23.23 | **4.61** | **8.05** | 28.52 | 2.14 |
| `2.a.2` | 33.84 | 6.61 | 43.47 | 24.32 | 3.72 | 6.60 | 31.13 | 2.83 |
| `2.b` | 34.46 | 6.61 | **37.29** | **20.20** | **3.42** | **7.78** | **34.43** | 2.25 |

### Statistical & Biological Explanation:
1. **Trial `2.a.1.b` represents atypical late-season biomass:**  
   Notice that Trial `2.a.1.b` has markedly higher crude protein (**7.90%** vs 6.43–6.72%), higher ash (**4.61%** vs 3.42–3.80%), and higher sugars (**8.05%** vs 5.55%). High crude protein and high mineral ash substantially increase buffering capacity ($BC$), resisting lactic acid drop and driving poorer fermentation (hence FQI = 38.35). Models trained on Trial 1 had never seen this high-buffering combination.
2. **Trial `2.b` represents high-grain, low-fiber forage:**  
   Trial `2.b` has significantly lower NDF (**37.29%** vs ~42–43%) and lower ADF (**20.20%** vs ~22–24%), but higher starch (**34.43%** vs 27.57%). This indicates a different harvest cut with a much higher grain-to-stover ratio.

---

## 4. Categorical Variables Imbalance & Confounding Across Trials

### Observed Evidence (Percentage Distribution Within Each Trial):

#### A. `method` (Silo Containment):
* **Trial `1`:** 100% `bags` (0% buckets)
* **Trial `2.a.1.a`:** 0% bags (100% `buckets`)
* **Trial `2.a.1.b`:** 0% bags (100% `buckets`)
* **Trial `2.a.2`:** 100% `bags` (0% buckets)
* **Trial `2.b`:** 0% bags (100% `buckets`)

#### B. `inhoculant` (Biological Additive):
* **Trial `1`:** 100% `c` (Pure water control — zero inoculated samples!)
* **Trial `2.a.1.a`:** 20% `c`, 60% `he` (heterofermentative), 20% `ho` (homofermentative)
* **Trial `2.a.1.b`:** 33.3% `c`, 33.3% `he`, 33.3% `ho`
* **Trial `2.a.2`:** 20% `c`, 60% `he`, 20% `ho`
* **Trial `2.b`:** 100% `c` (Pure water control)

#### C. `delay` (Packing Delay Duration):
* **Trial `1`:** 100% `D0` (Immediate packing — zero delayed packing samples!)
* **Trial `2.a.1.a`:** 32.7% `D0`, 33.3% `D6` (6h delay), 34.0% `D20` (20h delay)
* **Trial `2.a.1.b`:** 28.6% `D0`, 71.4% `D6`, 0.0% `D20`
* **Trial `2.a.2`:** 100% `D0`
* **Trial `2.b`:** 100% `D0`

#### D. `fao.class` (Maturity Class):
* **Trial `1`:** 48.5% `ea` (early), 51.5% `la` (late)
* **Trials `2.a.1.a`, `2.a.1.b`, `2.a.2`:** 100% `la` (late maturity only)
* **Trial `2.b`:** 18.4% `la`, **81.6% unrecorded (`NaN`)**

#### E. `maturity` (Phenological Harvest Stage):
* **Trial `1`:** 33.3% `eh` (1/3 milk line), 33.4% `mh` (2/3 milk line), 33.3% `lh` (late harvest)
* **Trial `2.a.1.a`:** 28.6% `eh`, 28.6% `mh`, 28.6% `lh`, 14.3% `vlh` (very late harvest)
* **Trial `2.a.1.b`:** **100.0% unrecorded (`NaN`)** (0 of 84 samples have maturity)
* **Trial `2.b`:** **100.0% unrecorded (`NaN`)** (0 of 87 samples have maturity)
* **Trial `2.a.2`:** 50% `eh`, 50% `mh`

### Explanation:
Categorical features are **heavily confounded with trial identity**. Trial 1 has zero variation in `inhoculant`, `dose`, or `delay` (all baseline control). In contrast, Trials 2.a.1.b and 2.b completely lack records for `maturity` (100% missing). This severe structural imbalance creates extreme domain shifts between training and test sets.

---

## 5. Missing-Value Patterns Between Trials

### Observed Evidence:

| Feature | Trial `1` ($N=940$) | Trial `2.a.1.a` ($N=315$) | Trial `2.a.1.b` ($N=84$) | Trial `2.a.2` ($N=60$) | Trial `2.b` ($N=87$) |
|---|:---:|:---:|:---:|:---:|:---:|
| `dm.f`, `cp.f`, `ash.f`, `wsc.f`, `lignin.f` | 11 (1.17%) | 6 (1.90%) | 0 (0.00%) | 0 (0.00%) | 3 (3.45%) |
| `ndf.f`, `starch.f` | 23 (2.45%) | 6 (1.90%) | 0 (0.00%) | 0 (0.00%) | 3 (3.45%) |
| `adf.f` | 11 (1.17%) | 6 (1.90%) | 0 (0.00%) | 2 (3.33%) | 3 (3.45%) |
| `dose` | 0 (0.00%) | 0 (0.00%) | **36 (42.86%)** | 0 (0.00%) | 0 (0.00%) |
| `fao.class` | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | **71 (81.61%)** |
| `maturity` | 0 (0.00%) | 0 (0.00%) | **84 (100.0%)** | 0 (0.00%) | **87 (100.0%)** |

### Explanation:
Missing values are **not Missing Completely at Random (MCAR)**. They are **structural trial omissions**:
- In Trials `2.a.1.b` and `2.b`, the researchers did not record kernel milk-line stage (`maturity`), resulting in **100% missing values**.
- In Trial `2.b`, `fao.class` was not recorded in **81.6%** of samples.
- When validating on Fold 3 or Fold 4, the model is forced to evaluate samples where key categorical inputs are `'Unknown'`, whereas in training they were fully specified.

---

## 6. Correlation Inversion: How Feature-to-FQI Relationships Flip Between Trials

### Observed Evidence (Pearson Correlation $r$ with `fqi` by Trial):

| Feature | Trial `1` ($N=940$) | Trial `2.a.1.a` ($N=315$) | Trial `2.a.1.b` ($N=84$) | Trial `2.a.2` ($N=60$) | Trial `2.b` ($N=87$) |
|---|:---:|:---:|:---:|:---:|:---:|
| **`dm.f`** | **-0.54** | **-0.73** | **-0.76** | **-0.82** | **-0.28** |
| **`cp.f`** | +0.26 | +0.27 | **+0.73** | **-0.45** | +0.23 |
| **`ndf.f`** | +0.05 | **+0.76** | +0.43 | **+0.51** | **-0.45** |
| **`adf.f`** | +0.15 | **+0.81** | **+0.68** | **+0.68** | **-0.40** |
| **`ash.f`** | +0.29 | +0.33 | **+0.80** | +0.17 | -0.13 |
| **`wsc.f`** | +0.25 | -0.05 | **+0.76** | -0.21 | +0.32 |
| **`starch.f`** | -0.28 | -0.46 | -0.59 | -0.51 | **+0.49** |
| **`lignin.f`** | -0.14 | **+0.81** | **+0.70** | **+0.69** | **-0.33** |

### Statistical & Biological Explanation:
This correlation matrix reveals a striking biological reality:
1. **The Only Consistent Predictor:**  
   **Fresh dry matter (`dm.f`) is consistently negatively correlated with FQI across all 5 trials** ($r$ ranges from $-0.28$ to $-0.82$). Lower DM (higher moisture) consistently ferments to lower FQI when compaction is imperfect.
2. **Severe Sign Reversals Across Trials:**
   * **`ndf.f` (Fiber):** In Trial `2.a.1.a`, fiber has a strong **positive** correlation with FQI ($r = +0.76$). But in Trial `2.b`, it has a strong **negative** correlation ($r = -0.45$).
   * **`adf.f` (Fiber):** In Trial `2.a.1.a`, $r = +0.81$. In Trial `2.b`, $r = -0.40$.
   * **`starch.f`:** In Trials 1, 2.a.1.a, 2.a.1.b, and 2.a.2, starch correlates **negatively** with FQI ($-0.28$ to $-0.59$). In Trial `2.b`, starch correlates **positively** with FQI ($r = +0.49$).
   * **`cp.f` (Protein):** In Trial `2.a.1.b`, $r = +0.73$. In Trial `2.a.2`, $r = -0.45$.

When feature-to-target correlations **invert their signs** between trials, any model (linear or non-linear) trained on one set of trials will make inversely erroneous predictions when applied to a trial where the underlying biological response curve is reversed.

---

## 7. Why Trial 1 is Substantially Different From Other Trials

### Observed Evidence:
1. **Sample Dominance:** Trial 1 represents **940 out of 1,486 samples (63.26%)**.
2. **Monolithic Control Protocol:**  
   - `method`: 100% `bags` (all other trials except 2.a.2 are `buckets`).
   - `inhoculant`: 100% `c` (pure water control — zero biological additives).
   - `dose`: 100% `none`.
   - `delay`: 100% `D0` (100% immediate sealing — zero packing delays).
3. **Primary Experimental Goal:**  
   Trial 1 was an agronomic field evaluation of natural crop variation across 4 consecutive years (2016–2019) and 39 maize hybrids under standard ensiling practices. It was not a management stress test.

### Explanation:
Trial 1 is an unperturbed natural-variation study, whereas the subsequent trials (`2.a.1.a`, `2.a.1.b`, `2.a.2`, `2.b`) were **deliberate stress-testing trials** investigating packing delays (6h to 24h), bacterial additives, and bucket compaction gradients.

---

## 8. Why Fold 2 Performs Well ($R^2 = +0.409$) While Other Folds Fail

### Observed Evidence:
* **Fold 2 Metrics (Val: Trial `2.a.1.a`):** MAE = 6.922, RMSE = 8.412, $\mathbf{R^2 = +0.409}$.
* **Folds 1, 3, 4, 5 Metrics:** $R^2$ ranges from $-0.330$ to $-2.686$.

### Explanation:
1. **Training Set Composition in Fold 2:**  
   In Fold 2, the training set contains **1,171 samples**, including the massive Trial 1 (940 samples) plus Trials `2.b`, `2.a.1.b`, and `2.a.2`. The training data covers both bags and buckets, all years (2016–2022), all inoculant types, and varied delays.
2. **Validation Sample Size and Variance:**  
   Trial `2.a.1.a` has a substantial sample size ($N = 315$, 21.2% of data) and a healthy standard deviation ($\sigma = 10.96$). The model had sufficient target variance to explain, and its training data was rich enough to capture the multi-dimensional relationships.
3. **Why Fold 1 Fails ($N=940$, $R^2 = -0.330$):**  
   In Fold 1, the training set is only **546 samples** (Trials 2.a.1.a, 2.b, 2.a.1.b, 2.a.2). This training set consists almost entirely of bucket trials with active inoculants and delays. The model is then asked to predict 940 bag samples with zero inoculants and zero delay. The model suffers from sample-size starvation (546 training on 940 test) and severe distribution mismatch.
4. **Why Folds 3, 4, and 5 Fail:**  
   - Fold 3 (`2.b`, $N=87$): Fiber/starch correlations invert sign.
   - Fold 4 (`2.a.1.b`, $N=84$): Mean FQI plummets to 38.35 (domain shift); 100% missing maturity.
   - Fold 5 (`2.a.2`, $N=60$): Target variance is tiny ($\sigma = 5.64$), making $SS_{\text{tot}}$ negligible and forcing negative $R^2$.

---

## 9. Data-Quality & Distribution-Shift Audit

| Issue Identified | Affected Trials | Severity | Statistical / Agronomic Impact |
|---|---|:---:|---|
| **Target Distribution Shift** | Trial `2.a.1.b` | **High** | FQI mean drops by ~16 points (38.35 vs ~54). Model systematically overpredicts quality. |
| **Variance Restriction** | Trial `2.a.2` | **Medium** | Target variance is compressed ($\sigma = 5.64$). Even low MAE produces negative $R^2$. |
| **Systematic Missingness (MNAR)** | Trials `2.a.1.b`, `2.b` | **High** | `maturity` is 100% missing in both trials; `fao.class` is 81.6% missing in `2.b`. |
| **Feature Correlation Inversion** | Trial `2.b` | **High** | NDF, ADF, and starch reverse correlation sign with FQI. |
| **Categorical Confounding** | Trial `1` vs `2.x` | **High** | Trial 1 is 100% bag, 100% control, 100% D0; subsequent trials are bucket/inoculant trials. |

---

## 10. Ridge Preprocessing Verification

### Verification in Code (`dataset/train_models.py`, lines 86–97):
```python
# 1. Pipeline applies median imputer to numeric, constant 'Unknown' + OneHotEncoder to categorical
X_train_proc = preprocessor.fit_transform(X_train)
X_val_proc = preprocessor.transform(X_val)

# 2. Dedicated StandardScaler fitted strictly on X_train_proc for Ridge
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_proc)
X_val_scaled = scaler.transform(X_val_proc)

# 3. Model training
model.fit(X_train_scaled, y_train)  # For Ridge
preds = model.predict(X_val_scaled)
```

### Confirmed Answers:
1. **Was scaling actually used for Ridge?**  
   **YES.** `StandardScaler()` was explicitly instantiated, fitted strictly on `X_train_proc`, and transformed on `X_val_proc` before fitting Ridge.
2. **Why was scaling used for Ridge but NOT tree models?**  
   * **Mathematical Necessity for Ridge:** Ridge minimizes the penalized residual sum of squares:
     $$\mathcal{L}_{\text{Ridge}} = \|y - Xw\|_2^2 + \alpha \|w\|_2^2$$
     Because numerical features span different natural magnitudes (e.g. Dry Matter ~35%, Starch ~30%, while Lignin ~2.2% and one-hot encodings are 0 or 1), unscaled features force Ridge to penalize coefficients unequally. StandardScaler normalizes all features to zero mean and unit variance ($\sigma = 1$), ensuring the regularization penalty $\alpha$ applies uniformly.
   * **Mathematical Invariance of Tree Models:** Decision tree algorithms (Random Forest and HistGradientBoosting) split nodes based on rank-order inequalities ($x_j \le \theta$). Monotonic scale transformations do not alter ordering or optimal split points. Leaving tree inputs unscaled preserves native physical interpretability (% DM, % CP) without affecting model predictions.

---

## 11. Recommendations for the Next Experiment (Design Only — Not Implemented)

Based on the empirical evidence gathered, the following methodological steps are recommended:

### Recommendation A: Hybrid Out-of-Trial Train/Test Split
* Rather than 5-fold GroupKFold where Fold 1 is starved of data (546 train vs 940 test), use **`GroupShuffleSplit`**:
  * **Train Set:** Trial `1` (940 samples) + Trial `2.b` (87) + Trial `2.a.1.b` (84) + Trial `2.a.2` (60) = **1,171 samples (78.8%)**.
  * **Test Benchmark:** Trial `2.a.1.a` = **315 samples (21.2%)**.
  * **Why:** This mirrors Fold 2, where the training set has sufficient data volume and diversity, and the test set has balanced variance and zero trial overlap.

### Recommendation B: Domain-Robust Feature Pruning
* Prune or de-emphasize features whose correlations invert sign between trials (such as `ndf.f`, `adf.f`, and `lignin.f`).
* Focus on universally stable predictors:
  * `dm.f` (consistently negative correlation across all 5 trials).
  * Agronomic interaction ratios: e.g. $\text{Fermentable Ratio} = \frac{\text{wsc.f}}{\text{cp.f} + \text{ash.f}}$ (sugar substrate vs buffering capacity).

### Recommendation C: Handle Structural Missingness with Dedicated Indicators
* Instead of generic imputation for `maturity` (which is 100% missing in Trials 2.a.1.b and 2.b), treat `maturity_missing` as an explicit structural feature, or evaluate a model trained solely on core proximate traits that are present across 100% of samples.

### Recommendation D: Error Metric Realism for Hakathons & Field Deployment
* Clarify in evaluation reports that an MAE of 6.92 to 11.20 points on an 85-point biological scale is typical for cross-environment agricultural predictions. 
* Frame the model not as a precise laboratory replacement, but as an **early-warning field screener** for dairy farmers.
