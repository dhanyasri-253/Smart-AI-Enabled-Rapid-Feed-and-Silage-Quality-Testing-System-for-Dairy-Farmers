"""
SmartSilageAI (SIH26111) — ML Model Benchmarking Script
Target: fqi (Fermentation Quality Index) Continuous Regression
Validation: GroupKFold (n_splits=5) grouped by ref.trial

Models Evaluated:
1. RandomForestRegressor (n_estimators=300, random_state=42)
2. HistGradientBoostingRegressor (random_state=42)
3. Ridge (random_state=42, with StandardScaler)

Integrity Rules:
- Preprocessing fitted strictly on training portion of each fold.
- No trial appears in both training and validation.
- Zero synthetic data used.
- Original datasilage.xlsx untouched.
"""

import os
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score


NUMERICAL_FEATURES: List[str] = [
    'dm.f', 'cp.f', 'ndf.f', 'adf.f', 'ash.f', 'wsc.f', 'starch.f', 'lignin.f'
]

CATEGORICAL_FEATURES: List[str] = [
    'method', 'inhoculant', 'dose', 'delay', 'fao.class', 'maturity'
]

TARGET_COLUMN: str = 'fqi'
GROUP_COLUMN: str = 'ref.trial'


def load_dataset(excel_path: str = 'dataset/datasilage.xlsx') -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Loads elab.all sheet and filters out rows with missing fqi target."""
    if not os.path.exists(excel_path):
        fallback = os.path.join(os.path.dirname(__file__), '..', 'data', 'datasilage.xlsx')
        if os.path.exists(fallback):
            excel_path = fallback
        else:
            raise FileNotFoundError(f"Cannot find dataset at {excel_path}")
            
    df = pd.read_excel(excel_path, sheet_name='elab.all')
    initial_count = len(df)
    
    # Filter only missing target rows
    df_clean = df[df[TARGET_COLUMN].notnull()].copy()
    cleaned_count = len(df_clean)
    
    X = df_clean[NUMERICAL_FEATURES + CATEGORICAL_FEATURES].copy()
    y = df_clean[TARGET_COLUMN].copy()
    groups = df_clean[GROUP_COLUMN].astype(str).copy()
    
    print(f"[Data Loading] Initial rows: {initial_count} | Cleaned rows (valid target): {cleaned_count}")
    return X, y, groups


def run_benchmark(excel_path: str = 'dataset/datasilage.xlsx') -> Dict:
    """Executes 5-fold GroupKFold cross-validation for RF, HGB, and Ridge."""
    X, y, groups = load_dataset(excel_path)
    
    unique_groups = groups.unique()
    n_groups = len(unique_groups)
    print(f"[Validation Strategy] GroupKFold with 5 folds across {n_groups} unique trials: {list(unique_groups)}")
    
    models = {
        'RandomForestRegressor': RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
        'HistGradientBoostingRegressor': HistGradientBoostingRegressor(random_state=42),
        'Ridge': Ridge(random_state=42)
    }
    
    # Storage for results
    fold_records = []
    summary_metrics = {m: {'mae': [], 'rmse': [], 'r2': []} for m in models}
    
    gkf = GroupKFold(n_splits=5)
    
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups=groups), 1):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        train_trials = list(groups.iloc[train_idx].unique())
        val_trials = list(groups.iloc[val_idx].unique())
        
        # Verify zero overlap between train and validation trials
        overlap = set(train_trials).intersection(set(val_trials))
        assert len(overlap) == 0, f"Leakage detected! Trials in both train and val: {overlap}"
        
        print(f"\n" + "=" * 70)
        print(f"FOLD {fold} / 5 | Validation Trial(s): {val_trials} | Val Size: {len(y_val)} | Train Size: {len(y_train)}")
        print(f"=" * 70)
        
        # 1. Fit preprocessing ONLY on training data
        num_imputer = SimpleImputer(strategy='median')
        cat_imputer_ohe = Pipeline([
            ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        preprocessor = ColumnTransformer([
            ('num', num_imputer, NUMERICAL_FEATURES),
            ('cat', cat_imputer_ohe, CATEGORICAL_FEATURES)
        ])
        
        X_train_proc = preprocessor.fit_transform(X_train)
        X_val_proc = preprocessor.transform(X_val)
        
        # Preprocessor with scaler for Ridge
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_proc)
        X_val_scaled = scaler.transform(X_val_proc)
        
        for name, model in models.items():
            if name == 'Ridge':
                model.fit(X_train_scaled, y_train)
                preds = model.predict(X_val_scaled)
            else:
                model.fit(X_train_proc, y_train)
                preds = model.predict(X_val_proc)
                
            mae = mean_absolute_error(y_val, preds)
            rmse = root_mean_squared_error(y_val, preds)
            r2 = r2_score(y_val, preds)
            
            summary_metrics[name]['mae'].append(mae)
            summary_metrics[name]['rmse'].append(rmse)
            summary_metrics[name]['r2'].append(r2)
            
            fold_records.append({
                'fold': fold,
                'val_trial': str(val_trials[0]),
                'val_samples': len(y_val),
                'train_samples': len(y_train),
                'model': name,
                'mae': mae,
                'rmse': rmse,
                'r2': r2
            })
            
            print(f"  {name:<30} | MAE: {mae:6.3f} | RMSE: {rmse:6.3f} | R2: {r2:7.3f}")
            
    df_results = pd.DataFrame(fold_records)
    
    print("\n" + "#" * 70)
    print("FINAL BENCHMARK SUMMARY (Mean +/- Std Across 5 Group Folds)")
    print("#" * 70)
    
    model_summaries = []
    for name, metrics in summary_metrics.items():
        mean_mae = np.mean(metrics['mae'])
        std_mae = np.std(metrics['mae'])
        mean_rmse = np.mean(metrics['rmse'])
        std_rmse = np.std(metrics['rmse'])
        mean_r2 = np.mean(metrics['r2'])
        std_r2 = np.std(metrics['r2'])
        
        model_summaries.append({
            'Model': name,
            'MAE Mean': mean_mae,
            'MAE Std': std_mae,
            'RMSE Mean': mean_rmse,
            'RMSE Std': std_rmse,
            'R2 Mean': mean_r2,
            'R2 Std': std_r2
        })
        print(f"Model: {name}")
        print(f"  MAE:  {mean_mae:6.3f} +/- {std_mae:5.3f}")
        print(f"  RMSE: {mean_rmse:6.3f} +/- {std_rmse:5.3f}")
        print(f"  R2:   {mean_r2:6.3f} +/- {std_r2:5.3f}")
        print("-" * 50)
        
    df_summary = pd.DataFrame(model_summaries)
    
    # Determine best model based on highest Mean R2 and lowest Mean RMSE/MAE
    best_model_row = df_summary.sort_values(by='RMSE Mean', ascending=True).iloc[0]
    best_model = best_model_row['Model']
    print(f"\n>>> BEST PERFORMING MODEL (Lowest Out-of-Trial RMSE): {best_model} <<<")
    
    return {
        'fold_results': df_results,
        'summary': df_summary,
        'best_model': best_model
    }


if __name__ == '__main__':
    run_benchmark(excel_path='dataset/datasilage.xlsx')
