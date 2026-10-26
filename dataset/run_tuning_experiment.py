import os
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

excel_path = 'dataset/datasilage.xlsx'
df = pd.read_excel(excel_path, sheet_name='elab.all')
df = df[df['fqi'].notnull()].copy()
df['ref.trial'] = df['ref.trial'].astype(str)

features_num = ['dm.f', 'cp.f', 'ash.f', 'wsc.f', 'starch.f']
features_cat = ['method', 'inhoculant', 'dose', 'delay', 'fao.class', 'maturity']
target = 'fqi'

X = df[features_num + features_cat]
y = df[target]
groups = df['ref.trial']

configs = {
    '1_Baseline': {
        'n_estimators': 300,
        'max_depth': None,
        'min_samples_leaf': 1,
        'max_features': 1.0,
        'random_state': 42
    },
    '2_Conservative': {
        'n_estimators': 500,
        'max_depth': None,
        'min_samples_leaf': 2,
        'max_features': 1.0,
        'random_state': 42
    },
    '3_Regularized': {
        'n_estimators': 500,
        'max_depth': 15,
        'min_samples_leaf': 2,
        'max_features': 0.8,
        'random_state': 42
    },
    '4_More_Regularized': {
        'n_estimators': 500,
        'max_depth': 10,
        'min_samples_leaf': 3,
        'max_features': 0.8,
        'random_state': 42
    }
}

results = {c: {'folds': [], 'mae': [], 'rmse': [], 'r2': []} for c in configs}

gkf = GroupKFold(n_splits=5)

for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups=groups), 1):
    val_trial = groups.iloc[val_idx].iloc[0]
    val_size = len(val_idx)
    train_size = len(train_idx)
    
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
    
    # Preprocessing strictly on train
    num_imputer = SimpleImputer(strategy='median')
    cat_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
        ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer([
        ('num', num_imputer, features_num),
        ('cat', cat_pipeline, features_cat)
    ])
    
    X_train_proc = preprocessor.fit_transform(X_train)
    X_val_proc = preprocessor.transform(X_val)
    
    print(f"\n=== FOLD {fold} (Val Trial: {val_trial}, N_val={val_size}, N_train={train_size}) ===")
    
    for cfg_name, params in configs.items():
        rf = RandomForestRegressor(**params, n_jobs=-1)
        rf.fit(X_train_proc, y_train)
        preds = rf.predict(X_val_proc)
        
        mae = mean_absolute_error(y_val, preds)
        rmse = root_mean_squared_error(y_val, preds)
        r2 = r2_score(y_val, preds)
        
        results[cfg_name]['folds'].append({
            'fold': fold,
            'val_trial': val_trial,
            'val_size': val_size,
            'train_size': train_size,
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        })
        results[cfg_name]['mae'].append(mae)
        results[cfg_name]['rmse'].append(rmse)
        results[cfg_name]['r2'].append(r2)
        
        print(f"  {cfg_name:<20} | MAE: {mae:6.3f} | RMSE: {rmse:6.3f} | R2: {r2:7.3f}")

print("\n" + "=" * 70)
print("HYPERPARAMETER TUNING SUMMARY (Mean +/- Std Across 5 Folds)")
print("=" * 70)

for cfg_name, data in results.items():
    maes = data['mae']
    rmses = data['rmse']
    r2s = data['r2']
    print(f"Configuration: {cfg_name}")
    print(f"  MAE:  {np.mean(maes):6.3f} +/- {np.std(maes):5.3f}")
    print(f"  RMSE: {np.mean(rmses):6.3f} +/- {np.std(rmses):5.3f}")
    print(f"  R2:   {np.mean(r2s):6.3f} +/- {np.std(r2s):5.3f}")
    print("-" * 50)
