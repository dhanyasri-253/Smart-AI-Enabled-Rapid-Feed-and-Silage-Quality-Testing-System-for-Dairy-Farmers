-- ====================================================================
-- SmartSilageAI - MySQL Database Schema
-- SIH26111: Smart AI-Enabled Rapid Feed and Silage Quality Testing System
-- Domain: Agriculture, FoodTech & Rural Development
-- Ministry of Fisheries, Animal Husbandry & Dairying
-- ====================================================================

CREATE DATABASE IF NOT EXISTS smartsilage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smartsilage;

-- 1. Farmers Table (Registered dairy farmers & field officers)
CREATE TABLE IF NOT EXISTS farmers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    mobile VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(120) NULL,
    location VARCHAR(150) NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Samples Table (Feed and Silage submissions)
CREATE TABLE IF NOT EXISTS samples (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sample_id VARCHAR(50) NOT NULL UNIQUE,
    farmer_id INT NOT NULL,
    sample_type VARCHAR(80) NOT NULL,
    sample_date DATE NOT NULL,
    
    -- Field-level accessible measurements
    ph FLOAT NULL COMMENT 'Silage pH measured via portable pH pen or test strip',
    moisture FLOAT NULL COMMENT 'Moisture percentage (estimated via squeeze test or hot air dryer)',
    temperature FLOAT NULL COMMENT 'Internal pit/bale temperature in Celsius',
    
    -- Optional Laboratory measurements (NIR or Wet Chemistry)
    crude_protein FLOAT NULL COMMENT 'Crude Protein % (Kjeldahl or Dumas method)',
    ndf FLOAT NULL COMMENT 'Neutral Detergent Fiber % (Van Soest method)',
    adf FLOAT NULL COMMENT 'Acid Detergent Fiber % (Van Soest method)',
    ash FLOAT NULL COMMENT 'Total mineral ash %',
    
    -- Visual & Sensory Field Indicators
    visual_odor VARCHAR(60) NULL COMMENT 'Aroma: Pleasant acidic, vinegar, rancid/butyric, musty/moldy',
    visual_color VARCHAR(60) NULL COMMENT 'Visual appearance: Olive green, golden brown, dark brown, moldy white/green',
    
    -- Media & Notes
    image_path VARCHAR(255) NULL COMMENT 'Stored relative image path for visual documentation',
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_sample_farmer FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE,
    INDEX idx_farmer_id (farmer_id),
    INDEX idx_sample_date (sample_date),
    INDEX idx_sample_type (sample_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Assessments Table (Preliminary screening & explainable outcomes)
CREATE TABLE IF NOT EXISTS assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sample_id INT NOT NULL,
    assessment_status VARCHAR(50) NOT NULL DEFAULT 'Completed',
    quality_category VARCHAR(80) NOT NULL DEFAULT 'Prototype — AI model pending validation',
    quality_score FLOAT NULL COMMENT 'Calculated preliminary index (0-100)',
    confidence VARCHAR(80) NULL DEFAULT 'Field Reference Screening (Pre-ML Validation)',
    model_version VARCHAR(100) NOT NULL DEFAULT 'Heuristic-v1.0 (ML Model Pending)',
    recommendation TEXT NOT NULL,
    parameter_breakdown JSON NULL COMMENT 'Explainable parameter analysis breakdown',
    lab_recommended BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_assessment_sample FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE,
    INDEX idx_sample_id (sample_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ====================================================================
-- SEED DATA FOR DEMO & TESTING
-- Password hash corresponds to 'farmer123'
-- ====================================================================
INSERT INTO farmers (id, name, mobile, email, location, password_hash)
VALUES 
(1, 'Ramesh Patel', '9876543210', 'ramesh.farmer@example.com', 'Anand, Gujarat', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918')
ON DUPLICATE KEY UPDATE id=id;

-- Sample 1: Good quality corn silage
INSERT INTO samples (id, sample_id, farmer_id, sample_type, sample_date, ph, moisture, temperature, crude_protein, ndf, adf, ash, visual_odor, visual_color, notes)
VALUES 
(1, 'SMP-2026-001', 1, 'Corn Silage', '2026-09-25', 3.9, 65.5, 25.0, 8.2, 44.0, 26.5, 4.8, 'Pleasant / Fruity Acidic', 'Olive Green / Light Brown', 'Bunker silo opened 4 weeks ago. Tightly packed.')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO assessments (sample_id, assessment_status, quality_category, quality_score, confidence, model_version, recommendation, lab_recommended)
VALUES 
(1, 'Completed', 'Acceptable Field Screening Range', 88.0, 'Field Reference Screening (Pre-ML Validation)', 'Heuristic-v1.0 (ML Model Pending)', 'Silage exhibits favorable lactic acid fermentation benchmarks (pH 3.9, optimal moisture ~65%). Safe for immediate feeding. Continue keeping face packed tightly to prevent secondary aerobic heating.', FALSE)
ON DUPLICATE KEY UPDATE id=id;

-- Sample 2: Aerobically deteriorating silage (High pH & heating)
INSERT INTO samples (id, sample_id, farmer_id, sample_type, sample_date, ph, moisture, temperature, crude_protein, ndf, adf, ash, visual_odor, visual_color, notes)
VALUES 
(2, 'SMP-2026-002', 1, 'Corn Silage', '2026-09-28', 5.2, 74.0, 41.5, 7.1, 52.0, 33.0, 6.2, 'Vinegar / Sharp Acetic', 'Dark Brown / Surface Mold', 'Top layer had rain ingress after plastic sheet tear.')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO assessments (sample_id, assessment_status, quality_category, quality_score, confidence, model_version, recommendation, lab_recommended)
VALUES 
(2, 'Completed', 'Caution — High Spoilage Risk', 42.0, 'Field Reference Screening (Pre-ML Validation)', 'Heuristic-v1.0 (ML Model Pending)', 'CRITICAL: Elevated internal temperature (41.5°C) and high pH (5.2) signify active aerobic deterioration and potential yeast/mold proliferation. Discard visibly heated/moldy surface layers. Do NOT feed to pregnant or lactating animals. Submit composite sample for wet chemistry mycotoxin testing.', TRUE)
ON DUPLICATE KEY UPDATE id=id;
