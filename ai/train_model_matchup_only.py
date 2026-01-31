import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, classification_report
from data_loader import load_data_for_ai

def train_matchup_only():
    print("Caricamento dati (Matchup Only)...")
    df = load_data_for_ai()
    
    if df.empty:
        print("Nessun dato trovato.")
        return

    print(f"Totale righe: {len(df)}")
    
    # Features: Solo storia Matchup
    # current_matchup è l'ultimo giocato (lag 1 rispetto al target)
    features = [
        'current_matchup', 'current_win',
        'avg_matchup_20', 'avg_matchup_30', 'avg_matchup_40', 
        'avg_matchup_50', 'avg_matchup_80', 'avg_matchup_120', 'avg_matchup_150',
        'cumulative_matchup_error'
    ]
    
    # Aggiungiamo i singoli matchup passati (da -2 a -31)
    # prev_matchup_1 è il penultimo giocato, etc.
    features.extend([f'prev_matchup_{i}' for i in range(1, 31)] + [f'prev_win_{i}' for i in range(1, 31)])
    
    # Split Train/Test (Last 10 per player)
    df = df.sort_values(by=['player_tag', 'timestamp'])
    
    train_indices = []
    test_indices = []
    
    for tag in df['player_tag'].unique():
        player_indices = df[df['player_tag'] == tag].index
        if len(player_indices) > 10:
            train_indices.extend(player_indices[:-10])
            test_indices.extend(player_indices[-10:])
        else:
            train_indices.extend(player_indices)
            
    train_df = df.loc[train_indices]
    test_df = df.loc[test_indices]
    
    print(f"Train set: {len(train_df)}, Test set: {len(test_df)}")
    
    X_train = train_df[features]
    y_train_mu = train_df['target_matchup']
    y_train_win = train_df['target_win']
    
    X_test = test_df[features]
    y_test_mu = test_df['target_matchup']
    y_test_win = test_df['target_win']
    
    # --- MODEL 1: Predict Outcome (Win/Loss) ---
    print("\n--- Addestramento Modello Outcome (Solo Storia) ---")
    clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10, n_jobs=-1)
    clf.fit(X_train, y_train_win)
    
    y_pred_win = clf.predict(X_test)
    acc = accuracy_score(y_test_win, y_pred_win)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test_win, y_pred_win))
    
    importances_win = clf.feature_importances_
    indices_win = np.argsort(importances_win)[::-1]
    print("\nFeature Importance (Outcome Prediction):")
    for f in range(X_train.shape[1]):
        print(f"{f+1}. {features[indices_win[f]]} ({importances_win[indices_win[f]]:.4f})")

    # --- MODEL: Predict Next Matchup ---
    print("\n--- Addestramento Modello Matchup (Solo Storia) ---")
    reg = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10, n_jobs=-1)
    reg.fit(X_train, y_train_mu)
    
    y_pred_mu = reg.predict(X_test)
    mae = mean_absolute_error(y_test_mu, y_pred_mu)
    r2 = r2_score(y_test_mu, y_pred_mu)
    
    print(f"MAE (Mean Absolute Error): {mae:.2f}%")
    print(f"R2 Score: {r2:.4f}")
    
    # Feature Importance
    importances_mu = reg.feature_importances_
    indices_mu = np.argsort(importances_mu)[::-1]
    print("\nFeature Importance (Matchup Prediction):")
    for f in range(X_train.shape[1]):
        print(f"{f+1}. {features[indices_mu[f]]} ({importances_mu[indices_mu[f]]:.4f})")

if __name__ == "__main__":
    train_matchup_only()
