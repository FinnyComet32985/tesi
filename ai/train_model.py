
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder


from data_loader import load_data_for_ai

def train_and_evaluate():
    print("Caricamento dati...")
    df = load_data_for_ai()
    
    if df.empty:
        print("Nessun dato trovato.")
        return

    print(f"Totale righe: {len(df)}")
    
    # Preprocessing
    # Encode Nationality
    le_nat = LabelEncoder()
    df['nationality_encoded'] = le_nat.fit_transform(df['nationality'].fillna('Unknown'))
    
    # Encode Archetype
    le_arch = LabelEncoder()
    df['archetype_encoded'] = le_arch.fit_transform(df['archetype'].fillna('Unknown'))
    
    # Encode Player Tag
    le_player = LabelEncoder()
    df['player_tag_encoded'] = le_player.fit_transform(df['player_tag'])
    
    # Features
    features = [
        'hour', 'days_since_season', 'trophies', 'current_win', 'current_matchup', 
        'current_matchup_no_lvl', 'current_level_diff', 'streak', 
        'session_duration', 'battles_in_session', 'nationality_encoded',
        'deck_changed', 'elixir_leaked', 'archetype_encoded',
        'dist_goal', 'dist_pb', 'dist_avg_trophies', 'freq_opp_arch_10',
        'time_since_last', 'crown_diff', 'king_tower_level', 
        'avg_matchup_30', 'avg_matchup_60', 'avg_matchup_80', 'avg_matchup_100',
        'deck_matches_played', 'deck_win_rate_7d', 'global_win_rate',
        'matchup_trend_5', 'matchup_volatility_10', 'delta_equilibrium',
        'streak_violation', 'matchup_quality_decay', 'cumulative_matchup_error',
        'player_tag_encoded'
    ]
    # Add lagged features 1-30
    features.extend([f'prev_matchup_{i}' for i in range(1, 31)])
    
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
            # Se meno di 10 partite, usiamo tutto per training
            train_indices.extend(player_indices)
            
    train_df = df.loc[train_indices]
    test_df = df.loc[test_indices]
    
    print(f"Train set: {len(train_df)}, Test set: {len(test_df)}")
    
    X_train = train_df[features]
    y_train_win = train_df['target_win']
    y_train_mu = train_df['target_matchup']
    
    X_test = test_df[features]
    y_test_win = test_df['target_win']
    y_test_mu = test_df['target_matchup']
    
    # --- MODEL 1: Predict Outcome (Win/Loss) ---
    print("\n--- Addestramento Modello Outcome (Win/Loss) ---")
    clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    clf.fit(X_train, y_train_win)
    
    y_pred_win = clf.predict(X_test)
    acc = accuracy_score(y_test_win, y_pred_win)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test_win, y_pred_win))
    
    # Feature Importance Outcome
    importances = clf.feature_importances_
    indices = np.argsort(importances)[::-1]
    print("Feature Importance (Outcome):")
    for f in range(X_train.shape[1]):
        print(f"{f+1}. {features[indices[f]]} ({importances[indices[f]]:.4f})")

    # --- MODEL 2: Predict Next Matchup ---
    print("\n--- Addestramento Modello Matchup (Regression) ---")
    reg = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    reg.fit(X_train, y_train_mu)
    
    y_pred_mu = reg.predict(X_test)
    mae = mean_absolute_error(y_test_mu, y_pred_mu)
    r2 = r2_score(y_test_mu, y_pred_mu)
    
    print(f"MAE (Mean Absolute Error): {mae:.2f}%")
    print(f"R2 Score: {r2:.4f}")
    
    # Feature Importance Matchup
    importances_mu = reg.feature_importances_
    indices_mu = np.argsort(importances_mu)[::-1]
    print("Feature Importance (Matchup):")
    for f in range(X_train.shape[1]):
        print(f"{f+1}. {features[indices_mu[f]]} ({importances_mu[indices_mu[f]]:.4f})")

if __name__ == "__main__":
    train_and_evaluate()