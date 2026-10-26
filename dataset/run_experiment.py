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

features_cat = ['method', 'inhoculant', 'dose', 'delay', 'fao.class', 'maturity']
baseline_num = ['dm.f', 'cp.f', 'ndf.f', 'adf.f', 'ash.f', 'wsc.f', 'starch.f', 'lignin.f']
experimental_num = ['dm.f', 'cp.f', 'ash.f', 'wsc.f', 'starch.f']

target = 'fqi'
y = df[target]
groups = df['ref.trial']

feature_sets = {
    'Baseline_14': (baseline_num, features_cat),
    'Experimental_11': (experimental_num, features_cat)
}

results = {fs: {'folds': [], 'mae': [], 'rmse': [], 'r2': []} for fs in feature_sets}

gkf = GroupKFold(n_splits=5)

for fold, (train_idx, val_idx) in enumerate(gkf.split(df, y, groups=groups), 1):
    val_trial = groups.iloc[val_idx].iloc[0]
    val_size = len(val_idx)
    train_size = len(train_idx)
    
    for fs_name, (num_cols, cat_cols) in feature_sets.items():
        X_train = df.iloc[train_idx][num_cols + cat_cols]
        X_val = df.iloc[val_idx][num_cols + cat_cols]
        y_train = y.iloc[train_idx]
        y_val = y.iloc[val_idx]
        
        preprocessor = ColumnTransformer([
            ('num', SimpleImputer(strategy='median'), num_cols),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
                ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
            ]), cat_cols)
        ])
        
        X_train_proc = preprocessor.fit_transform(X_train)
        X_val_proc = preprocessor.transform(X_val)
        
        rf = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
        rf.fit(X_train_proc, y_train)
        preds = rf.predict(X_val_proc)
        
        mae = mean_absolute_error(y_val, preds)
        rmse = root_mean_squared_error(y_val, preds)
        r2 = r2_score(y_val, preds)
        
        results[fs_name]['folds'].append({
            'fold': fold,
            'val_trial': val_trial,
            'val_size': val_size,
            'train_size': train_size,
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        })
        results[fs_name]['mae'].append(mae)
        results[fs_name]['rmse'].append(rmse)
        results[fs_name]['r2'].append(r2)

print('=== FOLD BY FOLD COMPARISON ===')
for f in range(5):
    b = results['Baseline_14']['folds'][f]
    e = results['Experimental_11']['folds'][f]
    print(f"Fold {b['fold']} (Val Trial: {b['val_trial']}, N_val={b['val_size']}, N_train={b['train_size']}):")
    print(f"  Baseline 14:     MAE={b['mae']:6.3f} | RMSE={b['rmse']:6.3f} | R2={b['r2']:7.3f}")
    print(f"  Experimental 11: MAE={e['mae']:6.3f} | RMSE={e['rmse']:6.3f} | R2={e['r2']:7.3f}")
    d_mae = e['mae'] - b['mae']
    d_rmse = e['rmse'] - b['rmse']
    d_r2 = e['r2'] - b['r2']
    print(f"  Delta (Exp - Base): dMAE={d_mae:+6.3f} | dRMSE={d_rmse:+6.3f} | dR2={d_r2:+7.3f}")
    print()

print('=== OVERALL SUMMARY (Mean +/- Std Across 5 Folds) ===')
for fs_name in feature_sets:
    maes = results[fs_name]['mae']
    rmses = results[fs_name]['rmse']
    r2s = results[fs_name]['r2']
    print(f"Feature Set: {fs_name}")
    print(f"  MAE:  {np.mean(maes):6.3f} +/- {np.std(maes):5.3f}")
    print(f"  RMSE: {np.mean(rmses):6.3f} +/- {np.std(rmses):5.3f}")
    print(f"  R2:   {np.mean(r2s):6.3f} +/- {np.std(r2s):5.3f}")
    print("-" * 50)
