# SmartSilageAI (SIH26111) — Random Forest Hyperparameter Tuning Report

**Project:** Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers  
**Challenge ID:** SIH26111 (Ministry of Fisheries, Animal Husbandry & Dairying)  
**Experiment:** Controlled Hyperparameter Tuning for the 11-Feature Random Forest Model  
**Validation Strategy:** 5-Fold `GroupKFold` grouped strictly by `ref.trial` (Leave-One-Trial-Out)  
**Dataset Reference:** `elab.all` sheet in `data/datasilage.xlsx` (1,486 valid samples)  
**Execution Script:** [`dataset/run_tuning_experiment.py`](file:///c:/Users/Dhany/AIML_sih/dataset/run_tuning_experiment.py)  
**Date:** 2026-10-08  

---

## Executive Summary & Non-Production Statement

> [!CAUTION]
> **Definitive Production-Readiness Warning:**  
> **The model is STILL NOT production-ready.**  
> Although hyperparameter regularization produced consistent reductions in prediction error (reducing MAE from 9.91 to 9.51 and RMSE from 12.14 to 11.54), **the overall out-of-trial $R^2$ remains negative ($-0.580 \pm 1.068$)**.  
> Regularizing trees mitigates variance and smooths regression boundaries, but it cannot bridge fundamental agronomic domain shifts between research trials (such as late-season buffering shifts). Deploying this model in commercial dairy settings without localized field calibration remains premature.

---

## 1. Feature Set & Target Definition

* **Selected Feature Set (11 Domain-Robust Features):**
  * **Nutritional Traits (5 Continuous):** `dm.f`, `cp.f`, `ash.f`, `wsc.f`, `starch.f`
  * **Management Traits (6 Categorical):** `method`, `inhoculant`, `dose`, `delay`, `fao.class`, `maturity`
* **Target Variable:** `fqi` (Continuous Fermentation Quality Index, Range: 11.66 – 84.57)
* **Validation Scheme:** 5-fold `GroupKFold` on `ref.trial`. No trial appears in both training and validation within any fold.
* **Preprocessing:** Fitted strictly on `X_train` inside each fold (median imputation for numeric, constant `'Unknown'` for categorical, `OneHotEncoder(handle_unknown='ignore')`).

---

## 2. Tested Hyperparameter Configurations

| Configuration | `n_estimators` | `max_depth` | `min_samples_leaf` | `max_features` | Rationale / Objective |
|---|:---:|:---:|:---:|:---:|---|
| **1. Baseline** | 300 | `None` (Full) | 1 | 1.0 (All) | Existing unconstrained tree benchmark from robust feature experiment. |
| **2. Conservative** | 500 | `None` (Full) | 2 | 1.0 (All) | Slightly larger ensemble; prunes single-sample isolated leaves. |
| **3. Regularized** | 500 | 15 | 2 | 0.8 (Subsample) | Restricts tree depth to 15; decorrelates trees via 80% feature subsampling. |
| **4. More Regularized** | 500 | 10 | 3 | 0.8 (Subsample) | Stronger depth cap (10) and leaf size (3) to prevent memorization of trial-specific quirks. |

---

## 3. Fold-by-Fold Detailed Results

### Fold 1: Validation Trial `1` ($N_{\text{val}} = 940$, $N_{\text{train}} = 546$)
| Configuration | MAE | RMSE | $R^2$ |
|---|:---:|:---:|:---:|
| 1. Baseline | 7.808 | 10.178 | -0.156 |
| 2. Conservative | 7.733 | 10.021 | -0.121 |
| 3. Regularized | **7.409** | **9.575** | **-0.023** |
| 4. More Regularized | 7.478 | 9.685 | -0.047 |

---

### Fold 2: Validation Trial `2.a.1.a` ($N_{\text{val}} = 315$, $N_{\text{train}} = 1,171$)
| Configuration | MAE | RMSE | $R^2$ |
|---|:---:|:---:|:---:|
| 1. Baseline | 6.844 | 8.136 | +0.447 |
| 2. Conservative | 6.596 | 7.905 | +0.478 |
| 3. Regularized | 6.598 | 7.904 | +0.478 |
| **4. More Regularized** | **6.552** | **7.902** | **+0.479** |

---

### Fold 3: Validation Trial `2.b` ($N_{\text{val}} = 87$, $N_{\text{train}} = 1,399$)
| Configuration | MAE | RMSE | $R^2$ |
|---|:---:|:---:|:---:|
| 1. Baseline | 15.033 | 18.027 | -3.099 |
| 2. Conservative | 14.815 | 17.719 | -2.960 |
| 3. Regularized | 14.753 | 17.217 | -2.739 |
| **4. More Regularized** | **14.402** | **16.957** | **-2.626** |

---

### Fold 4: Validation Trial `2.a.1.b` ($N_{\text{val}} = 84$, $N_{\text{train}} = 1,402$)
| Configuration | MAE | RMSE | $R^2$ |
|---|:---:|:---:|:---:|
| 1. Baseline | 14.831 | 17.943 | -0.616 |
| 2. Conservative | 14.662 | 17.800 | -0.591 |
| 3. Regularized | 14.079 | 17.068 | -0.463 |
| **4. More Regularized** | **13.900** | **16.826** | **-0.421** |

---

### Fold 5: Validation Trial `2.a.2` ($N_{\text{val}} = 60$, $N_{\text{train}} = 1,426$)
| Configuration | MAE | RMSE | $R^2$ |
|---|:---:|:---:|:---:|
| **1. Baseline** | **5.014** | 6.411 | -0.314 |
| 2. Conservative | 5.077 | 6.405 | -0.311 |
| 3. Regularized | 5.566 | 6.678 | -0.426 |
| 4. More Regularized | 5.199 | **6.334** | **-0.282** |

---

## 4. Overall Benchmark Comparison Across All 5 Folds (Mean ± Std)

| Configuration | MAE (Mean ± Std) | RMSE (Mean ± Std) | $R^2$ (Mean ± Std) | Rank |
|---|:---:|:---:|:---:|:---:|
| **4. More Regularized** (`depth=10`, `leaf=3`, `feat=0.8`) | **9.506 ± 3.864** | **11.541 ± 4.496** | **-0.580 ± 1.068** | 🏆 **1st (Best)** |
| **3. Regularized** (`depth=15`, `leaf=2`, `feat=0.8`) | 9.681 ± 3.916 | 11.689 ± 4.548 | -0.634 ± 1.106 | 🥈 2nd |
| **2. Conservative** (`depth=None`, `leaf=2`, `feat=1.0`) | 9.776 ± 4.139 | 11.970 ± 4.865 | -0.701 ± 1.183 | 🥉 3rd |
| **1. 11-Feature Baseline** (`depth=None`, `leaf=1`, `feat=1.0`) | 9.906 ± 4.201 | 12.139 ± 4.920 | -0.747 ± 1.226 | 4th |

---

## 5. Comparison With 11-Feature Baseline & Scientific Findings

### A. Net Change From Baseline to Best Configuration (Config 4):
* **MAE Improvement:** **$-0.400$ points** (from 9.906 down to **9.506**).
* **RMSE Improvement:** **$-0.598$ points** (from 12.139 down to **11.541**).
* **$R^2$ Improvement:** **$+0.167$ points** (from $-0.747$ up to **$-0.580$**).

### B. Did Hyperparameter Tuning Actually Improve Generalization?
**YES, tuning produced modest, monotonic improvements:**
1. **Reduced Overfitting on Complex Folds:**
   - In Fold 4 (Trial `2.a.1.b`), MAE dropped from **14.83** to **13.90** (almost a full point reduction).
   - In Fold 3 (Trial `2.b`), MAE dropped from **15.03** to **14.40**.
   - In Fold 2 (Trial `2.a.1.a`, the main 315-sample validation trial), $R^2$ improved from **+0.447** to **+0.479**, and MAE dropped to **6.55**.
2. **Why Regularization Helped:**
   - Restricting `max_depth` to 10 and requiring `min_samples_leaf` $\ge 3$ prevents trees from creating hyper-specific terminal leaves that capture trial-specific sampling artifacts.
   - Setting `max_features = 0.8` injects tree diversity by forcing trees to find alternative splits rather than repeatedly splitting on the same dominant features.

### C. Critical Warning on Negative $R^2$:
* Despite the steady improvement, **mean out-of-trial $R^2$ remains negative ($-0.580$)**.
* **Why tuning cannot fix negative $R^2$ entirely:**  
  Hyperparameter tuning smooths decision surfaces, but it cannot eliminate physical domain shifts. When Trial `2.a.1.b` has an average FQI that is 16 points lower than the training data due to late-season harvest buffering, a regularized model still cannot predict that systematic shift without trial-level or seasonal calibration data.

---

## 6. Official Configuration Recommendation

### **BEST CONFIGURATION: Configuration 4 (More Regularized)**
* **Parameters:** `n_estimators=500`, `max_depth=10`, `min_samples_leaf=3`, `max_features=0.8`, `random_state=42`.
* **Verdict:** Retain Configuration 4 as the optimized model weights for subsequent analysis.
* **Non-Deployment Rule:** Do not deploy to production. Model evaluation must clearly state that cross-trial biological variance limits purely supervised out-of-trial $R^2$.

---

## 7. Integrity & Constraint Confirmations

1. **Original Excel File Untouched:** SHA-256 hash `A90A5CCF1B1BA0084CBD0088BA3CDD14645308A2394E161FE7AD510B4266CDCD` confirmed identical.
2. **Existing Reports Intact:** All previous reports ([`ML_MODEL_BENCHMARK_REPORT.md`](file:///c:/Users/Dhany/AIML_sih/dataset/ML_MODEL_BENCHMARK_REPORT.md) and [`ML_ROBUST_FEATURE_EXPERIMENT.md`](file:///c:/Users/Dhany/AIML_sih/dataset/ML_ROBUST_FEATURE_EXPERIMENT.md)) remain untouched.
3. **Zero Synthetic Data / Fake Labels:** 100% authentic laboratory experimental observations.
4. **No Deployment:** Model remains strictly in experimental benchmarking mode.
