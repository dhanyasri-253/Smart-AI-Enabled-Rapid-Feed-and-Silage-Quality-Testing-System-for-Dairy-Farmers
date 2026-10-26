# SmartSilageAI (SIH26111) — Split Validation & Trial Leakage Report

**Project:** Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers  
**Challenge ID:** SIH26111 (Ministry of Fisheries, Animal Husbandry & Dairying)  
**Investigation:** Validation of Train/Test Splitting Strategy & Intra-Trial Data Leakage  
**Dataset Reference:** `elab.all` sheet in `data/datasilage.xlsx` / [`dataset/fqi_ml_raw.csv`](file:///c:/Users/Dhany/AIML_sih/dataset/fqi_ml_raw.csv)  
**Date:** 2026-10-08  

---

## 1. Executive Summary & Core Findings

| Question / Parameter | Result / Finding | Status / Risk |
|---|---|:---:|
| **Does `ref.trial` exist in `elab.all`?** | **YES** (Column 1 of the sheet) | Verified |
| **Number of unique `ref.trial` values** | **5 unique trials** (`1`, `2.a.1.a`, `2.a.1.b`, `2.a.2`, `2.b`) | Verified |
| **Do the same trials appear in both train and test?** | **YES. 100% of trials appear in BOTH sets.** | ⚠️ **Severe Intra-Trial Overlap** |
| **Number of overlapping trials** | **5 out of 5 trials (100% overlap)** | ⚠️ **Complete Overlap** |
| **Is the random 80/20 split scientifically appropriate?** | **NO. It causes pseudo-replication and optimistic bias.** | ❌ **Flawed for Real Deployment** |
| **Recommended Strategy** | **GroupKFold / GroupShuffleSplit using `ref.trial`** *(with Temporal Split as complementary benchmark)* | ✅ **Scientifically Valid** |

---

## 2. Detailed Trial Distribution Analysis

In the 1,486 valid samples of `elab.all`, the 5 unique trials represent distinct research campaigns with specific harvest methodologies, storage structures, and years:

| Trial ID (`ref.trial`) | Sample Count | Share (%) | Harvest Years | Silo Method | Experimental Context |
|:---:|:---:|:---:|:---:|:---:|---|
| **`1`** | **940** | **63.26%** | 2016, 2017, 2018, 2019 | `bags` | Primary long-term multi-year bag ensiling trial |
| **`2.a.1.a`** | **315** | **21.20%** | 2019, 2020 | `buckets` | Lab-scale bucket compaction trial (Series 1a) |
| **`2.b`** | **87** | **5.85%** | 2018, 2019 | `buckets` | Secondary bucket trial (inoculant variations) |
| **`2.a.1.b`** | **84** | **5.65%** | 2021, 2022 | `buckets` | Late-season bucket trial (Series 1b) |
| **`2.a.2`** | **60** | **4.04%** | 2019 | `bags` | 2019 focused bag ensiling replicate trial |
| **TOTAL** | **1,486** | **100.00%** | **2016–2022** | **Mixed** | |

---

## 3. Train vs. Test Trial Overlap Audit (Current Random 80/20 Split)

When a standard random split (`test_size=0.2, random_state=42`) is applied to `fqi_ml_raw.csv`, the resulting distribution per trial across the train (1,188 samples) and test (298 samples) splits is:

| Trial ID (`ref.trial`) | Total Samples | Train Set (80%) | Test Set (20%) | Train Share (%) | Test Share (%) | Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `1` | 940 | 750 | 190 | 79.8% | 20.2% | **OVERLAPPING** |
| `2.a.1.a` | 315 | 260 | 55 | 82.5% | 17.5% | **OVERLAPPING** |
| `2.a.1.b` | 84 | 62 | 22 | 73.8% | 26.2% | **OVERLAPPING** |
| `2.a.2` | 60 | 50 | 10 | 83.3% | 16.7% | **OVERLAPPING** |
| `2.b` | 87 | 66 | 21 | 75.9% | 24.1% | **OVERLAPPING** |
| **OVERLAPPING TRIALS** | **5 / 5** | **100% of Trials** | **100% of Trials** | — | — | **5 overlapping** |

### What This Means:
Every single experimental trial is split ~80% into the training partition and ~20% into the testing partition. **There is not a single unseen trial in the test set.**

---

## 4. Why the Current Random 80/20 Split is Scientifically Inappropriate

In agricultural and biological machine learning, random splitting across clustered data causes severe **pseudo-replication** and **shortcut learning**:

1. **Intra-Trial Confounding & Shared Environmental Noise:**
   Samples originating from the same trial share unrecorded cluster-level environmental conditions (e.g. ambient harvest humidity, chopper blade sharpness, specific field microbial baseline, specific micro-plot soil characteristics). When a random split is used, these shared cluster characteristics appear on both sides of the split.
2. **Artificial Optimism (Inflated Test Scores):**
   The model does not need to learn true generalizable biochemical rules connecting fresh forage traits to `fqi`. Instead, it can exploit subtle correlational fingerprints shared among sister samples from the same trial. This makes validation metrics ($R^2$, MAE, RMSE) look artificially strong on paper.
3. **Mismatch with Real-World Farm Deployment (SIH26111 Goal):**
   When an Indian dairy farmer in Gujarat or Punjab uses the SmartSilageAI mobile application, their silo pit is a **completely new, unseen farm and trial**. A model validated only on seen trials cannot prove whether it will generalize to an entirely new farm environment.

---

## 5. Splitting Strategy Comparison & Recommendation

### Comparison of Options:

| Strategy | Description | Strengths | Limitations |
|---|---|---|---|
| **A. GroupKFold / GroupShuffleSplit (using `ref.trial`)** | Entire trials are assigned strictly to train OR test. No trial is ever split. | **Completely eliminates trial leakage.** Measures true out-of-trial generalization to new silo series. | Group sizes are imbalanced (Trial 1 = 63.3%). Standard 5-fold GroupKFold yields one large test fold (63.3%) and four small test folds (~4–21%). GroupShuffleSplit handles this smoothly. |
| **B. Temporal Split (Train on 2016–2019, Test on 2020–2022)** | Splits chronologically: past seasons train the model; future seasons test the model. | Perfectly simulates real agricultural deployment. Eliminates future look-ahead bias. | The test set (2020–2022) comprises 219 samples (14.7%), all of which happen to be bucket trials (`2.a.1.a` and `2.a.1.b`). |
| **C. Current Random 80/20 Split** | Standard uniform random sampling across all rows. | Maximizes sample diversity in train and test. Statistically balanced. | **Suffers from 100% trial overlap.** Prone to intra-trial pseudo-replication and over-optimistic evaluation. |

---

## 6. Official Recommendation

### Primary Recommendation: **GroupKFold / GroupShuffleSplit using `ref.trial`**

* **Why:** It directly solves the problem statement by ensuring that **no trial appears in both training and evaluation sets**.
* **How to Execute in ML Pipeline:**
  1. **Option 1 (`GroupShuffleSplit`):** Hold out 1 or 2 entire trial series (e.g. Trial `2.a.1.a` with 315 samples = 21.2% test share) exclusively as the unseen test benchmark, while training on the remaining trials (`1`, `2.b`, `2.a.1.b`, `2.a.2` = 1,171 samples = 78.8%).
  2. **Option 2 (`GroupKFold(n_splits=5)` Cross-Validation):** Evaluate all models across the 5 trial groups so that every trial serves as an unseen out-of-trial test fold.
* **Secondary / Reporting Recommendation:**
  In the final model evaluation report, report both:
  - **In-Distribution Random Split Benchmark:** For baseline comparison.
  - **Out-of-Trial Grouped Benchmark (GroupKFold):** As the definitive scientific metric proving real-world transferability to new dairy farms.

---

## 7. Confirmation of Constraints
- Zero models were trained.
- `datasilage.xlsx` was opened strictly in read-only mode and remains 100% untouched.
- No synthetic or fake data was created.
- Existing preprocessed CSV files remain unchanged.
