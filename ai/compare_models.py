import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
from data_loader import load_data_for_ai

def train_and_compare():
    print("Caricamento dati per confronto modelli...")
    df = load_data_for_ai()
    
    if df.empty:
        print("Nessun dato trovato.")
        return

    # --- PREPARAZIONE DATI ---
    # Ordiniamo per garantire la sequenzialità
    df = df.sort_values(by=['player_tag', 'timestamp'])

    # Creiamo il target per i livelli (Livello del prossimo avversario)
    # data_loader ci dà già target_matchup, ma dobbiamo calcolare target_level_diff
    # Shiftiamo indietro di 1 per prendere il valore della prossima riga
    df['target_level_diff'] = df.groupby('player_tag')['current_level_diff'].shift(-1)

    # Rimuoviamo le righe dove non abbiamo il target (l'ultima partita di ogni giocatore)
    df = df.dropna(subset=['target_matchup', 'target_level_diff'])

    print(f"Totale righe valide: {len(df)}")

    # --- FEATURE ENGINEERING (Fattori Intrinseci) ---
    # 1. Livello Atteso per Fascia Trofei (Structural Paywall)
    # Calcoliamo il level_diff medio per ogni fascia di 500 trofei
    df['trophy_bucket'] = (df['trophies'] // 500) * 500
    avg_lvl_map = df.groupby('trophy_bucket')['current_level_diff'].mean().to_dict()
    df['expected_level_diff'] = df['trophy_bucket'].map(avg_lvl_map)

    # 2. Encoding Archetipo (Il sistema sa che mazzo usi?)
    le = LabelEncoder()
    df['archetype_encoded'] = le.fit_transform(df['archetype'].astype(str))

    # --- DEFINIZIONE FEATURE ---
    
    # MODELLO A: "Ufficiale" (Supercell)
    # Ipotesi: Il matchmaking dipende solo da Trofei, Livello Torre e chi è online (Orario)
    features_official = [
        'trophies', 
        'king_tower_level', 
        'hour'  # Proxy per il pool di giocatori online
    ]

    # MODELLO B: "Intrinseco" (Deck & Level Aware - NO MEMORIA)
    # Ipotesi: Il sistema bilancia in base al mazzo che usi e ai livelli della fascia, ma NON guarda il passato.
    features_intrinsic = features_official + [
        'archetype_encoded',    # Che mazzo sto usando?
        'deck_avg_elixir_leaked', # Skill specifica col mazzo (Avg Elixir Leaked)
        'expected_level_diff',  # Qual è lo svantaggio livelli medio a questi trofei?
        'days_since_season'     # Progressione stagionale
    ]

    # MODELLO C: "Comportamentale" (Ipotesi Rigged/EOMM - CON MEMORIA)
    # Ipotesi: Il sistema reagisce all'esito delle partite precedenti (Streak, Tilt, Pity)
    features_behavioral = features_intrinsic + [
        'current_win',          # Ho vinto o perso l'ultima?
        'current_matchup',      # Era un counter?
        'streak',               # Sono in serie positiva/negativa?
        'crown_diff'            # Ho vinto di misura o stravinto? (Qualità esito)
    ]

    # Split Train/Test (Ultimi 10 match per player come test set)
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

    # Funzione helper per addestrare e valutare
    def evaluate_model(name, features, target_col, y_train, y_test):
        print(f"\n--- {name} [{target_col}] ---")
        print(f"Features: {features}")
        
        X_train = train_df[features].fillna(0)
        X_test = test_df[features].fillna(0)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10, n_jobs=-1)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"R2 Score: {r2:.5f}")
        print(f"MAE:      {mae:.4f}")
        return r2

    # --- CONFRONTO 1: PREDIZIONE MATCHUP (Deck Rigging) ---
    print("\n" + "="*60)
    print("CONFRONTO 1: PREDIZIONE PROSSIMO MATCHUP (Deck)")
    print("="*60)
    
    y_train_mu = train_df['target_matchup']
    y_test_mu = test_df['target_matchup']

    r2_official_mu = evaluate_model("Modello A (Ufficiale)", features_official, 'target_matchup', y_train_mu, y_test_mu)
    r2_intrinsic_mu = evaluate_model("Modello B (Intrinseco)", features_intrinsic, 'target_matchup', y_train_mu, y_test_mu)
    r2_behavioral_mu = evaluate_model("Modello C (Comportamentale)", features_behavioral, 'target_matchup', y_train_mu, y_test_mu)

    # --- CONFRONTO 2: PREDIZIONE LIVELLI (Paywall/Punishment) ---
    print("\n" + "="*60)
    print("CONFRONTO 2: PREDIZIONE PROSSIMO LEVEL DIFF (Livelli)")
    print("="*60)

    y_train_lvl = train_df['target_level_diff']
    y_test_lvl = test_df['target_level_diff']

    r2_official_lvl = evaluate_model("Modello A (Ufficiale)", features_official, 'target_level_diff', y_train_lvl, y_test_lvl)
    r2_intrinsic_lvl = evaluate_model("Modello B (Intrinseco)", features_intrinsic, 'target_level_diff', y_train_lvl, y_test_lvl)
    r2_behavioral_lvl = evaluate_model("Modello C (Comportamentale)", features_behavioral, 'target_level_diff', y_train_lvl, y_test_lvl)

    # --- CONCLUSIONI ---
    print("\n" + "="*60)
    print("RISULTATI FINALI E INTERPRETAZIONE")
    print("="*60)
    
    def interpret(r2_a, r2_b, r2_c, metric):
        print(f"\nMETRICA: {metric}")
        print(f"R2 Modello A (Base):       {r2_a:.5f}")
        print(f"R2 Modello B (Intrinseco): {r2_b:.5f}")
        print(f"R2 Modello C (Memoria):    {r2_c:.5f}")
        
        # Analisi Delta
        delta_intrinsic = r2_b - r2_a
        delta_behavioral = r2_c - r2_b
        
        print(f"\nIMPATTO FATTORI:")
        print(f"1. Deck & Livelli (B - A): {delta_intrinsic:+.5f}")
        print(f"2. Storia Recente (C - B): {delta_behavioral:+.5f}")
        
        if delta_behavioral > 0.02:
            print("\n>> CONCLUSIONE: C'è evidenza di MEMORIA (EOMM).")
            print("   Sapere se hai vinto/perso l'ultima partita migliora la predizione del futuro.")
        elif delta_intrinsic > 0.05:
            print("\n>> CONCLUSIONE: Il sistema è DECK-AWARE ma non necessariamente RIGGED.")
            print("   Il matchmaking guarda il tuo mazzo, ma non la tua streak recente.")
        else:
            print("\n>> CONCLUSIONE: Il sistema sembra CASUALE/BASATO SU TROFEI.")
            
    interpret(r2_official_mu, r2_intrinsic_mu, r2_behavioral_mu, "Next Matchup (Deck)")
    interpret(r2_official_lvl, r2_intrinsic_lvl, r2_behavioral_lvl, "Next Level Diff (Levels)")

if __name__ == "__main__":
    train_and_compare()