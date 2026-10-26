# SmartSilageAI — SIH26111
### Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers

> **Ministry:** Ministry of Fisheries, Animal Husbandry & Dairying  
> **Domain:** Agriculture, FoodTech & Rural Development  
> **Challenge ID:** SIH26111  
> **Evaluation Mode:** Prototype Screening Mode (Transparent Scientific Integration)

---

> [!IMPORTANT]
> **Scientific Integrity & Model Status Disclaimer:**  
> **"The current prototype does not contain a validated trained ML model. The ML pipeline is designed for integration after obtaining and validating an appropriate feed/silage quality dataset."**  
> We do NOT claim that this preliminary on-farm screening replaces certified laboratory wet-chemistry testing unless scientifically calibrated and validated with ICAR-NDRI benchmarks.

---

## Table of Contents
1. [SIH Problem Statement](#1-sih-problem-statement)
2. [Problem Background](#2-problem-background)
3. [Existing Challenge](#3-existing-challenge)
4. [Proposed Solution](#4-proposed-solution)
5. [Target Users](#5-target-users)
6. [User Workflow](#6-user-workflow)
7. [System Architecture](#7-system-architecture)
8. [Technology Stack](#8-technology-stack)
9. [Database Design](#9-database-design)
10. [AI/ML Approach](#10-aiml-approach)
11. [Dataset Requirements](#11-dataset-requirements)
12. [Feasibility](#12-feasibility)
13. [Sustainability](#13-sustainability)
14. [Expected Impact](#14-expected-impact)
15. [Scalability](#15-scalability)
16. [Current Limitations](#16-current-limitations)
17. [Future Improvements](#17-future-improvements)
18. [Installation Instructions](#18-installation-instructions)
19. [How to Run Frontend & Backend](#19-how-to-run-frontend--backend)
20. [How to Run FastAPI Services](#20-how-to-run-fastapi-services)
21. [How to Configure MySQL](#21-how-to-configure-mysql)

---

## 1. SIH Problem Statement
**SIH26111: Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers**

Dairy cattle productivity in India relies heavily on nutritional quality and fermentation stability of preserved fodder (silage) and concentrate feed rations. Poor silage management, secondary aerobic deterioration, and clostridial fermentation lead to severe milk yield loss, reproductive disorders, and health risks from mycotoxins (e.g. Aflatoxin M1 in milk). 

This system provides a practical, low-barrier, mobile-first screening tool for dairy farmers to assess feed quality rapidly on the farm.

---

## 2. Problem Background
India is the world's largest milk producer, yet average per-animal daily milk production remains constrained by variable fodder nutrition. Ensiling green fodder (corn, sorghum, hybrid napier) during surplus seasons is expanding rapidly across dairy states (Gujarat, Punjab, Haryana, Maharashtra, Karnataka, Tamil Nadu). 

However, ensiling is a biological process requiring strict anaerobic compaction. If air enters or moisture is improperly balanced, ensiled crops ferment into foul, butyric, or mold-contaminated material that can poison cattle.

---

## 3. Existing Challenge
1. **Slow Laboratory Turnaround:** Traditional proximate wet-chemistry analysis (Kjeldahl for Crude Protein, Van Soest fiber extraction) requires 3 to 7 days and travel to district research centers.
2. **High Testing Costs:** Commercial laboratory testing costs ₹1,500 – ₹4,000 per sample, which is unaffordable for smallholders with 2–5 cows.
3. **Delayed Detection of Spoilage:** By the time a farmer notices reduced feed intake or sudden milk drops, toxic spoilage has already impacted the herd.
4. **Unrealistic AI Claims in Tech Prototypes:** Many software projects claim that an ordinary mobile camera alone can calculate chemical parameters (protein, pH, NDF) from photos. In dairy science, camera pixels cannot substitute for chemical reagents without calibrated NIR spectrophotometry.

---

## 4. Proposed Solution
**SmartSilageAI** bridges this gap by providing **Rapid Preliminary On-Farm Screening**:
- Captures field-accessible indicators:
  - **pH** (using low-cost pocket digital pen or indicator strips, < ₹300)
  - **Moisture % / Dry Matter** (using hand-squeeze test or hot-air drying)
  - **Internal Temperature** (using a stainless probe thermometer to detect aerobic spoilage)
  - **Sensory Observations** (clean lactic aroma vs. vinegar/acetic vs. foul butyric odor; olive color vs. dark heat caramelization)
- Validates measurements against **ICAR-NDRI dairy science guidelines**.
- Delivers **Explainable AI Indicators**: Highlights exactly *why* a parameter is alarming (e.g., pH 5.2 triggers clostridial warning; temperature > 38°C flags air leaks).
- Provides practical farm actions (e.g., bunker face management, discarding top mold, adjusting compaction).
- Clearly advises the farmer when to send a composite sample for **certified laboratory wet-chemistry testing**.

---

## 5. Target Users
* **Primary Users:** Smallholder & commercial dairy farmers (simple vernacular interface, large touch buttons, visual units).
* **Secondary Users:**
  - Dairy Cooperatives (Amul, Nandini, Aavin, OMFED milk collection societies).
  - Livestock Extension & Krishi Vigyan Kendra (KVK) field officers.
  - Veterinary practitioners conducting nutritional diagnostic visits.
  - Commercial silage bag & baled fodder suppliers.
  - Certified fodder testing laboratories.

---

## 6. User Workflow

```
Dairy Farmer / Extension Worker
             │
             ▼
    Login / Register (Mobile #)
             │
             ▼
    Create Feed / Silage Sample
             │
  ┌──────────┴──────────────────────────┐
  ▼                                     ▼
Field Measurements              Sensory & Image Record
• pH (pocket pen/strips)        • Aroma (lactic/butyric/acetic)
• Moisture % (squeeze test)     • Appearance (olive/mold/dark)
• Internal Temperature (°C)     • Optional bunker photo
  │                                     │
  └──────────┬──────────────────────────┘
             ▼
  System Validation & Heuristic Screening
  (Transparent ML integration pipeline)
             │
             ▼
  Explainable Rapid Assessment Dossier
  • Preliminary Status (Acceptable / Caution / High Risk)
  • Parameter-by-Parameter Scientific Explanation
  • Immediate Farm Bunker Actions
  • Certified Lab Referral Advice (if alarming)
             │
             ▼
  Archived in Historical Trends Database
```

---

## 7. System Architecture

```
[ Frontend: HTML5 / CSS3 / Vanilla JS ]
   │ (REST API calls with JWT / Bearer Token)
   ▼
[ FastAPI Backend (Python) ]
   ├── Authentication & User Service
   ├── Sample Validation & Media Manager (/uploads)
   ├── Explainable Heuristic Rule Engine (ICAR/NDRI Standards)
   └── ML Integration Layer (backend/ml/)
         ├── model_loader.py (Detects models/model.joblib)
         ├── preprocessing.py (Feature vectors & boundary bounds)
         └── predictor.py (Inference engine + heuristic fallback)
   │
   ▼
[ Database Layer ]
   ├── Primary: MySQL (Structured schema: farmers, samples, assessments)
   └── Zero-Setup Fallback: SQLite (smartsilage.db for instant local testing)
```

---

## 8. Technology Stack
* **Frontend:** HTML5, Modern Vanilla CSS (Agricultural design system, mobile responsive), Vanilla JavaScript (No heavy NPM build steps required).
* **Backend:** Python 3.10+, FastAPI, Uvicorn ASGI server.
* **Database:** MySQL 8.0+ (with SQLAlchemy ORM and PyMySQL driver) + automatic local SQLite fallback for out-of-the-box evaluation.
* **AI/ML Layer:** Scikit-learn, Joblib, NumPy (pre-configured pipeline architecture ready to load `models/model.joblib`).

---

## 9. Database Design

```sql
-- 1. Farmers
CREATE TABLE farmers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    mobile VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(120),
    location VARCHAR(150),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Samples
CREATE TABLE samples (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sample_id VARCHAR(50) NOT NULL UNIQUE,
    farmer_id INT NOT NULL,
    sample_type VARCHAR(80) NOT NULL,
    sample_date DATE NOT NULL,
    ph FLOAT,
    moisture FLOAT,
    temperature FLOAT,
    crude_protein FLOAT,
    ndf FLOAT,
    adf FLOAT,
    ash FLOAT,
    visual_odor VARCHAR(60),
    visual_color VARCHAR(60),
    image_path VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
);

-- 3. Assessments
CREATE TABLE assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sample_id INT NOT NULL UNIQUE,
    assessment_status VARCHAR(50) DEFAULT 'Completed',
    quality_category VARCHAR(80) DEFAULT 'Prototype — AI model pending validation',
    quality_score FLOAT,
    confidence VARCHAR(80),
    model_version VARCHAR(100),
    recommendation TEXT NOT NULL,
    parameter_breakdown JSON,
    lab_recommended BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE
);
```

---

## 10. AI/ML Approach

### Why We Refuse Fake AI Models
Fabricating a synthetic CSV of random numbers and claiming "97% AI accuracy" is unscientific and dangerous to dairy livestock. 

### The ML Integration Pipeline
1. **Preprocessing (`backend/ml/preprocessing.py`):**
   Validates physical boundaries (e.g. pH 2.5–12.0, moisture 10–90%, temp 0–75°C). Imputes missing laboratory features (CP, NDF) using agronomic medians while retaining explicit field-vs-lab metadata flags.
2. **Model Loader (`backend/ml/model_loader.py`):**
   Dynamically looks for `models/model.joblib`. If absent, gracefully runs the transparent ICAR-NDRI reference engine and marks predictions: **"Prototype — AI model pending validation"**.
3. **Predictor (`backend/ml/predictor.py`):**
   When `model.joblib` is supplied after dataset trials, it invokes `model.predict()`. Until then, it evaluates Flieg's Fermentation Index heuristics:
   $$\text{Score} = 90 - (25 \times N_{\text{severe}}) - (12 \times N_{\text{concerning}})$$

---

## 11. Dataset Requirements
To train the production model, field samples will be paired with certified proximate wet-chemistry analysis in collaboration with state agricultural universities:

| Parameter | Method | Typical Target (Corn Silage) | Equipment |
|---|---|---|---|
| pH | Electrode / Test Strip | 3.7 – 4.2 | Portable pH meter |
| Moisture % | Gravimetric drying | 60% – 70% | Koster tester / Hot-air oven |
| Temperature | Thermistor probe | < 32°C | Digital soil/compost spear |
| Crude Protein (CP) | Kjeldahl ($N \times 6.25$) | 7.5% – 9.5% | Laboratory Kjeldahl unit |
| NDF % | Van Soest neutral detergent | 38% – 48% | Fibertec analyzer |
| ADF % | Van Soest acid detergent | 24% – 30% | Fibertec analyzer |

---

## 12. Feasibility
- **Zero Expensive Hardware:** Dairy farmers only need their existing smartphone and low-cost field tools (pH strips at ₹150 per pack, pocket thermometer at ₹250).
- **Lightweight Backend:** FastAPI runs with minimal memory footprint (< 100MB RAM) on edge Raspberry Pi devices, local cooperative dairy PCs, or cloud servers.
- **Low Connectivity Support:** Local database storage allows offline field recordings by extension workers that sync when network signal is restored.

---

## 13. Sustainability
- **Prevents Massive Feed Wastage:** Identifying aerobic heating within the first 48 hours allows farmers to remove the top 10 cm and reseal the silo, saving the remaining 20 tonnes of feed.
- **Protects Animal Health:** Prevents ketosis, rumen acidosis, and mycotoxicosis from feeding spoiled butyric silage.
- **Resource Conservation:** Optimizes land and water invested in green forage cultivation by preventing storage degradation.

---

## 14. Expected Impact
1. **Economic:** Saves estimated ₹15,000 to ₹40,000 per dairy farm per season by reducing fodder spoiling and preventing veterinary treatment expenses for digestive disorders.
2. **Milk Quality:** Minimizes Aflatoxin contamination in milk, elevating cooperative milk collection standards.
3. **Capacity Building:** Educates rural farmers on anaerobic compaction principles through actionable tips.

---

## 15. Scalability
1. **Multilingual Interface:** Localization for Hindi, Gujarati, Tamil, Marathi, Punjabi, and Kannada.
2. **IoT In-Silo Probes:** Direct Bluetooth/LoRaWAN telemetry from temperature spears embedded inside silage bunkers.
3. **Computer Vision Mold Classifier:** Transfer-learning MobileNet model to classify visual surface mycelium.
4. **Union-Level Dashboard:** Aggregate view for District Milk Unions (Amul, NDDB) to monitor forage reserves across talukas.

---

## 16. Current Limitations
- Current prototype operates on **ICAR-NDRI scientific reference rules** because a finalized, certified Indian dataset is not yet collected.
- Mobile phone cameras cannot read chemical properties (protein, fiber, pH) directly from pixels alone.
- Physical laboratory confirmation remains necessary for suspected mycotoxin cases.

---

## 17. Future Improvements
- Train supervised gradient boosted trees (LightGBM/XGBoost) once 2,000+ split-sample laboratory pairs are gathered across Indian agro-climatic zones.
- Add voice-assisted regional language audio prompts for illiterate farmers.
- Integrate automated SMS/WhatsApp alerts to local veterinary extension officers if severe spoilage is detected.

---

## 18. Installation Instructions

### Prerequisites
- Python 3.10+ installed on your computer.
- Git (optional).

### Step 1: Clone or Navigate to the Project
```powershell
cd c:\Users\Dhany\AIML_sih
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

---

## 19. How to Run Frontend & Backend

Because the FastAPI backend automatically serves the frontend static files, you can run the **entire application with one single command**:

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Now open your web browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 20. How to Run FastAPI Services & FQI Prediction API

### Starting the Server
```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Interactive Documentation & Diagnostics
- **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Technical Reference:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Technical / Jury Diagnostic Status:** [http://127.0.0.1:8000/api/admin/status](http://127.0.0.1:8000/api/admin/status)

### FQI Prediction Endpoint: `POST /predict`
The prediction endpoint evaluates pre-ensiling forage characteristics and management choices using the frozen 11-feature Random Forest pipeline (`dataset/fqi_model.joblib`).

#### Request Fields (Exactly 11 Input Features):
| Field | Type | Description |
|---|---|---|
| `dm.f` | float | Fresh Whole-Crop Dry Matter (%) |
| `cp.f` | float | Fresh Crude Protein (% DM) |
| `ash.f` | float | Fresh Total Ash (% DM) |
| `wsc.f` | float | Fresh Water-Soluble Carbohydrates (% DM) |
| `starch.f` | float | Fresh Starch Content (% DM) |
| `method` | string | Silo containment type (e.g. `'bags'`, `'buckets'`) |
| `inhoculant` | string | Biological additive applied (e.g. `'c'`, `'he'`, `'ho'`) |
| `dose` | string | Inoculant dosage applied (e.g. `'none'`, `'s'`, `'h'`, `'d'`, `'Unknown'`) |
| `delay` | string | Packing delay duration (e.g. `'D0'`, `'D6'`, `'D20'`) |
| `fao.class` | string | FAO crop maturity class (e.g. `'ea'`, `'la'`, `'Unknown'`) |
| `maturity` | string | Kernel milk-line stage (e.g. `'eh'`, `'mh'`, `'lh'`, `'vlh'`, `'Unknown'`) |

#### Example Request:
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "dm.f": 34.5,
       "cp.f": 8.2,
       "ash.f": 3.8,
       "wsc.f": 8.5,
       "starch.f": 30.2,
       "method": "bags",
       "inhoculant": "c",
       "dose": "none",
       "delay": "D0",
       "fao.class": "la",
       "maturity": "mh"
     }'
```

#### Example Response:
```json
{
  "predicted_fqi": 49.43
}
```
*(Note: FQI is a continuous score from 11.66 to 84.57. This model is a research prototype).*

---

## 21. How to Configure MySQL

### Option A: Out-of-the-Box Zero-Setup (Automatic SQLite Fallback)
If you don't have MySQL credentials set up right away, you don't need to do anything! The backend automatically falls back to local SQLite (`smartsilage.db`) and seeds realistic demo data so you can test immediately.

### Option B: Connecting to your MySQL Server
1. Ensure your MySQL server is running (Port 3306).
2. Open your MySQL client (MySQL Workbench, HeidiSQL, or MySQL CLI) and run:
   ```sql
   SOURCE c:/Users/Dhany/AIML_sih/database/schema.sql;
   ```
   *(Or simply copy-paste the contents of `database/schema.sql` into MySQL Workbench and execute).*
3. Open `.env` in the project root and specify your MySQL credentials:
   ```env
   DB_TYPE=mysql
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=smartsilage
   ```
4. Restart the server:
   ```powershell
   python -m uvicorn backend.main:app --reload
   ```
   The backend will log:
   `[SmartSilageAI] Connected successfully to MySQL Database: 'smartsilage'`

---

### Demo Mode Quick Credentials (For Evaluators & Testing)
- **Mobile Number:** `9876543210`
- **Password:** `farmer123`
- *(Or simply click the **"One-Click Demo Login"** button on the login page!)*
