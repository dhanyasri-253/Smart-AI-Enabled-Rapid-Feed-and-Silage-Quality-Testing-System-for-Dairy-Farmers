"""
SmartSilageAI (SIH26111) — Leak-Free Preprocessing Pipeline
Target: fqi (Fermentation Quality Index) Regression

This module implements the official, leak-free preprocessing pipeline
for the SIH26111 silage quality prediction models:
- RandomForestRegressor
- Ridge Regressor
- HistGradientBoostingRegressor

Rules:
1. Numerical features: Median imputation (unscaled by default).
2. Categorical features: Missing values replaced with 'Unknown' (no assumed defaults).
3. One-hot encoding with handle_unknown='ignore'.
4. Strict leakage prevention: Preprocessor is fitted ONLY on training data,
   then applied to validation/test sets.
5. Target 'fqi' is kept completely unchanged.
6. Zero synthetic data generated.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Tuple, List, Optional
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split


# Feature Definitions
NUMERICAL_FEATURES: List[str] = [
    'dm.f',      # Fresh Dry Matter (%)
    'cp.f',      # Fresh Crude Protein (% DM)
    'ndf.f',     # Fresh Neutral Detergent Fiber (% DM)
    'adf.f',     # Fresh Acid Detergent Fiber (% DM)
    'ash.f',     # Fresh Total Ash (% DM)
    'wsc.f',     # Fresh Water-Soluble Carbohydrates (% DM)
    'starch.f',  # Fresh Starch (% DM)
    'lignin.f'   # Fresh Acid Detergent Lignin (% DM)
]

CATEGORICAL_FEATURES: List[str] = [
    'method',     # Storage type: 'bags', 'buckets'
    'inhoculant', # Inoculant type: 'c', 'he', 'ho'
    'dose',       # Dosage: 'none', 's', 'd', 'h', 'Unknown'
    'delay',      # Packing delay: 'D0', 'D6', 'D20'
    'fao.class',  # Maturity class: 'ea', 'la', 'Unknown'
    'maturity'    # Phenological stage: 'eh', 'mh', 'lh', 'vlh', 'Unknown'
]

TARGET_COLUMN: str = 'fqi'


def build_preprocessor(scale_numeric: bool = False) -> ColumnTransformer:
    """
    Constructs an unfitted Scikit-Learn ColumnTransformer.
    
    Can be used directly or embedded in a full Pipeline (e.g. Pipeline([
        ('preprocessor', build_preprocessor()),
        ('regressor', RandomForestRegressor())
    ])) to ensure zero data leakage during cross-validation.
    
    Args:
        scale_numeric: If True, adds StandardScaler to the numerical pipeline.
                       Default is False (kept unscaled for tree models).
    Returns:
        Unfitted ColumnTransformer instance.
    """
    num_steps = [('imputer', SimpleImputer(strategy='median'))]
    if scale_numeric:
        num_steps.append(('scaler', StandardScaler()))
    
    num_pipeline = Pipeline(steps=num_steps)

    cat_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_pipeline, NUMERICAL_FEATURES),
            ('cat', cat_pipeline, CATEGORICAL_FEATURES)
        ],
        remainder='drop'
    )
    return preprocessor


def get_feature_names(fitted_preprocessor: ColumnTransformer) -> List[str]:
    """Extracts all output column names from a fitted ColumnTransformer."""
    cat_step = fitted_preprocessor.named_transformers_['cat'].named_steps['onehot']
    cat_names = list(cat_step.get_feature_names_out(CATEGORICAL_FEATURES))
    return NUMERICAL_FEATURES + cat_names


def load_raw_dataset(csv_path: str = 'dataset/fqi_ml_raw.csv') -> Tuple[pd.DataFrame, pd.Series]:
    """
    Loads dataset/fqi_ml_raw.csv and validates column completeness.
    
    Returns:
        X: Feature DataFrame (14 columns)
        y: Target Series (fqi, continuous)
    """
    if not os.path.exists(csv_path):
        # Fallback to data directory if dataset directory path is relative
        fallback_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'fqi_ml_raw.csv')
        if os.path.exists(fallback_path):
            csv_path = fallback_path
        else:
            raise FileNotFoundError(f"Cannot find raw dataset file at {csv_path}")

    df = pd.read_csv(csv_path)
    
    # Verify no rows have missing target
    if df[TARGET_COLUMN].isnull().any():
        raise ValueError(f"Target column '{TARGET_COLUMN}' contains missing values.")

    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES].copy()
    y = df[TARGET_COLUMN].copy()
    return X, y


def split_and_preprocess(
    csv_path: str = 'dataset/fqi_ml_raw.csv',
    test_size: float = 0.2,
    random_state: int = 42,
    scale_numeric: bool = False,
    save_artifacts: bool = True
) -> dict:
    """
    Executes leak-free preprocessing:
    1. Splits raw data into train and test sets BEFORE any transformation.
    2. Fits the ColumnTransformer strictly on X_train.
    3. Transforms X_train and X_test using the train-fitted transformer.
    4. Keeps y_train and y_test completely unchanged.
    5. Optionally saves processed artifacts.
    """
    X, y = load_raw_dataset(csv_path)
    raw_row_count = len(X)

    # 1. Split BEFORE fitting to prevent data leakage
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # 2. Build preprocessor and FIT ONLY on training split
    preprocessor = build_preprocessor(scale_numeric=scale_numeric)
    preprocessor.fit(X_train_raw)

    # 3. Transform both splits
    X_train_proc = preprocessor.transform(X_train_raw)
    X_test_proc = preprocessor.transform(X_test_raw)

    feature_names = get_feature_names(preprocessor)

    # Convert back to clean DataFrames with feature names
    df_X_train = pd.DataFrame(X_train_proc, columns=feature_names, index=X_train_raw.index)
    df_X_test = pd.DataFrame(X_test_proc, columns=feature_names, index=X_test_raw.index)

    output = {
        'raw_row_count': raw_row_count,
        'train_row_count': len(df_X_train),
        'test_row_count': len(df_X_test),
        'feature_count': len(feature_names),
        'feature_names': feature_names,
        'X_train': df_X_train,
        'X_test': df_X_test,
        'y_train': y_train,
        'y_test': y_test,
        'preprocessor': preprocessor
    }

    if save_artifacts:
        output_dir = os.path.dirname(os.path.abspath(csv_path))
        df_X_train.to_csv(os.path.join(output_dir, 'X_train_preprocessed.csv'), index=False)
        df_X_test.to_csv(os.path.join(output_dir, 'X_test_preprocessed.csv'), index=False)
        y_train.to_csv(os.path.join(output_dir, 'y_train.csv'), index=False)
        y_test.to_csv(os.path.join(output_dir, 'y_test.csv'), index=False)
        joblib.dump(preprocessor, os.path.join(output_dir, 'fqi_preprocessor.joblib'))
        print(f"[Preprocessing] Artifacts successfully saved to {output_dir}")

    return output


if __name__ == '__main__':
    print("=" * 60)
    print("SmartSilageAI (SIH26111) — Executing Leak-Free Preprocessor")
    print("=" * 60)
    
    result = split_and_preprocess(csv_path='dataset/fqi_ml_raw.csv', save_artifacts=True)
    
    print(f"Total Rows: {result['raw_row_count']}")
    print(f"Train Rows: {result['train_row_count']} (80%)")
    print(f"Test Rows:  {result['test_row_count']} (20%)")
    print(f"Transformed Features Count: {result['feature_count']}")
    print("\nPreprocessed Feature Columns:")
    for idx, f in enumerate(result['feature_names'], 1):
        print(f"  {idx:02d}. {f}")
    
    print("\nTarget 'fqi' Summary (Train):")
    print(result['y_train'].describe().round(3).to_string())
    print("\nTarget 'fqi' Summary (Test):")
    print(result['y_test'].describe().round(3).to_string())
    print("\n[SUCCESS] Preprocessing completed with ZERO synthetic data and ZERO leakage.")
