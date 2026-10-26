# Models Directory — SmartSilageAI (SIH26111)

## Current Status
- **Model Status**: `Not yet trained (Pending validated dataset)`
- **Model Version**: `N/A`
- **Validation Status**: `Pending scientific trial with ICAR / NDRI benchmarks`
- **Expected Artifact**: `models/model.joblib`

## Architecture for Future Integration

When a scientifically validated training dataset is acquired from accredited Indian dairy institutions (such as ICAR-National Dairy Research Institute or State Agricultural Universities):

1. **Pretrained Model Storage**:
   Trained scikit-learn or XGBoost pipeline models will be exported to this directory as `model.joblib`.

2. **Model Metadata (`model_metadata.json`)**:
   Will include:
   - `model_type`: e.g., `RandomForestClassifier` or `XGBoostClassifier`
   - `training_date`: Timestamp of training
   - `dataset_source`: Name of accredited research facility / cooperative
   - `accuracy_f1_score`: Verified test performance metrics
   - `feature_names`: `['ph', 'moisture', 'temperature', 'crude_protein', 'ndf', 'adf', 'ash']`
   - `target_classes`: `['Acceptable', 'Needs Attention', 'High Spoilage Risk']`

3. **Fallback Mechanism**:
   The application's `backend/ml/model_loader.py` verifies the integrity of `models/model.joblib`. If the model is absent or not yet validated, the system automatically falls back to the transparent, explainable ICAR/NDRI field reference heuristic engine, clearly alerting the farmer: **"Prototype — AI model pending validation"**.
