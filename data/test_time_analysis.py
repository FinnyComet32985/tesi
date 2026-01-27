import os
import statistics
from datetime import datetime
import pytz
from scipy.stats import kruskal, levene

COUNTRY_TZ_MAP = {
    'Italy': 'Europe/Rome', 'IT': 'Europe/Rome',
    'United States': 'America/New_York', 'US': 'America/New_York',
    'Germany': 'Europe/Berlin', 'DE': 'Europe/Berlin',
    'France': 'Europe/Paris', 'FR': 'Europe/Paris',
    'Spain': 'Europe/Madrid', 'ES': 'Europe/Madrid',
    'United Kingdom': 'Europe/London', 'GB': 'Europe/London', 'UK': 'Europe/London',
    'Russia': 'Europe/Moscow', 'RU': 'Europe/Moscow',
    'Japan': 'Asia/Tokyo', 'JP': 'Asia/Tokyo',
    'China': 'Asia/Shanghai', 'CN': 'Asia/Shanghai',
    'Brazil': 'America/Sao_Paulo', 'BR': 'America/Sao_Paulo',
    'Canada': 'America/Toronto', 'CA': 'America/Toronto',
    'Mexico': 'America/Mexico_City', 'MX': 'America/Mexico_City',
    'Korea, Republic of': 'Asia/Seoul', 'KR': 'Asia/Seoul',
    'Netherlands': 'Europe/Amsterdam', 'NL': 'Europe/Amsterdam'
}

def get_local_hour(timestamp_str, nationality):
    try:
        # Timestamp string is in Italian local time (from battlelog_v2)
        italy_tz = pytz.timezone('Europe/Rome')
        naive_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        italy_dt = italy_tz.localize(naive_dt)
        
        target_tz_name = COUNTRY_TZ_MAP.get(nationality, 'Europe/Rome')
        target_tz = pytz.timezone(target_tz_name)
        player_dt = italy_dt.astimezone(target_tz)
        return player_dt.hour
    except Exception:
        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').hour

def analyze_time_stats(players_sessions, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'battlelogs_v2')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'time_and_trophy_analysis_results.txt')

    print(f"\nGenerazione report Analisi Temporale e Trofei (Matchup, No-Lvl, Levels) in: {output_file}")

    time_slots = {0: "Notte (00-06)", 1: "Mattina (06-12)", 2: "Pomeriggio (12-18)", 3: "Sera (18-24)"}
    TROPHY_BUCKET_SIZE = 1000
    
    # Data structure: metric -> slot -> list of values
    metrics_data_time = {
        'Matchup (Reale)': {k: [] for k in time_slots},
        'Matchup (No-Lvl)': {k: [] for k in time_slots},
        'Level Diff': {k: [] for k in time_slots}
    }
    
    metrics_data_trophies = {
        'Matchup (Reale)': {},
        'Matchup (No-Lvl)': {},
        'Level Diff': {}
    }

    for p in players_sessions:
        nationality = p.get('nationality')
        for session in p['sessions']:
            for b in session['battles']:
                # Time Analysis
                if 'timestamp' in b:
                    h = get_local_hour(b['timestamp'], nationality)
                    slot = 0
                    if 6 <= h < 12: slot = 1
                    elif 12 <= h < 18: slot = 2
                    elif 18 <= h < 24: slot = 3
                    
                    if b.get('matchup') is not None:
                        metrics_data_time['Matchup (Reale)'][slot].append(b['matchup'])
                    
                    if b.get('matchup_no_lvl') is not None:
                        metrics_data_time['Matchup (No-Lvl)'][slot].append(b['matchup_no_lvl'])
                        
                    if b.get('level_diff') is not None:
                        metrics_data_time['Level Diff'][slot].append(b['level_diff'])
                
                # Trophy Analysis
                t = b.get('trophies_before')
                if t:
                    bucket = (t // TROPHY_BUCKET_SIZE) * TROPHY_BUCKET_SIZE
                    
                    if b.get('matchup') is not None:
                        if bucket not in metrics_data_trophies['Matchup (Reale)']: metrics_data_trophies['Matchup (Reale)'][bucket] = []
                        metrics_data_trophies['Matchup (Reale)'][bucket].append(b['matchup'])
                    
                    if b.get('matchup_no_lvl') is not None:
                        if bucket not in metrics_data_trophies['Matchup (No-Lvl)']: metrics_data_trophies['Matchup (No-Lvl)'][bucket] = []
                        metrics_data_trophies['Matchup (No-Lvl)'][bucket].append(b['matchup_no_lvl'])
                        
                    if b.get('level_diff') is not None:
                        if bucket not in metrics_data_trophies['Level Diff']: metrics_data_trophies['Level Diff'][bucket] = []
                        metrics_data_trophies['Level Diff'][bucket].append(b['level_diff'])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ANALISI CONFONDENTI: TEMPO E TROFEI\n")
        f.write("Obiettivo: Verificare se le condizioni di gioco variano significativamente in base all'orario o alla fascia di trofei.\n")
        f.write("="*100 + "\n\n")

        # --- TIME SECTION ---
        f.write("1. ANALISI TEMPORALE (Orario Locale)\n")
        f.write("-" * 100 + "\n")

        for metric_name, slots_data in metrics_data_time.items():
            f.write(f"--- METRICA: {metric_name} ---\n")
            f.write(f"{'Fascia Oraria':<20} | {'N':<8} | {'Mean':<10} | {'StdDev':<10} | {'Variance':<10}\n")
            f.write("-" * 70 + "\n")
            
            valid_samples = []
            
            for slot in sorted(time_slots.keys()):
                data = slots_data[slot]
                if not data:
                    f.write(f"{time_slots[slot]:<20} | {'0':<8} | {'-':<10} | {'-':<10} | {'-':<10}\n")
                    continue
                
                avg = statistics.mean(data)
                std = statistics.stdev(data) if len(data) > 1 else 0
                var = std ** 2
                
                f.write(f"{time_slots[slot]:<20} | {len(data):<8} | {avg:<10.2f} | {std:<10.2f} | {var:<10.2f}\n")
                valid_samples.append(data)
            
            f.write("-" * 70 + "\n")
            
            if len(valid_samples) > 1:
                try:
                    stat_k, p_k = kruskal(*valid_samples)
                    f.write(f"Kruskal-Wallis (Medie): p={p_k:.4f} -> {'SIGNIFICATIVO' if p_k < 0.05 else 'Non significativo'}\n")
                except Exception as e:
                    f.write(f"Kruskal-Wallis Error: {e}\n")
                    
                try:
                    stat_l, p_l = levene(*valid_samples)
                    f.write(f"Levene Test (Varianze): p={p_l:.4f} -> {'SIGNIFICATIVO' if p_l < 0.05 else 'Non significativo'}\n")
                except Exception as e:
                    f.write(f"Levene Test Error: {e}\n")
            else:
                f.write("Dati insufficienti per i test statistici.\n")
            
            f.write("\n")

        # --- TROPHY SECTION ---
        f.write("\n" + "="*100 + "\n")
        f.write("2. ANALISI PER FASCIA DI TROFEI\n")
        f.write(f"Bucket Size: {TROPHY_BUCKET_SIZE}\n")
        f.write("-" * 100 + "\n")

        for metric_name, buckets_data in metrics_data_trophies.items():
            f.write(f"--- METRICA: {metric_name} ---\n")
            f.write(f"{'Fascia Trofei':<20} | {'N':<8} | {'Mean':<10} | {'StdDev':<10} | {'Variance':<10}\n")
            f.write("-" * 70 + "\n")
            
            valid_samples = []
            sorted_buckets = sorted(buckets_data.keys())
            
            for bucket in sorted_buckets:
                data = buckets_data[bucket]
                if len(data) < 20: continue # Skip small buckets
                
                avg = statistics.mean(data)
                std = statistics.stdev(data) if len(data) > 1 else 0
                var = std ** 2
                
                label = f"{bucket}-{bucket+TROPHY_BUCKET_SIZE}"
                f.write(f"{label:<20} | {len(data):<8} | {avg:<10.2f} | {std:<10.2f} | {var:<10.2f}\n")
                valid_samples.append(data)
            
            f.write("-" * 70 + "\n")
            
            if len(valid_samples) > 1:
                try:
                    stat_k, p_k = kruskal(*valid_samples)
                    f.write(f"Kruskal-Wallis (Medie): p={p_k:.4f} -> {'SIGNIFICATIVO' if p_k < 0.05 else 'Non significativo'}\n")
                except Exception as e:
                    f.write(f"Kruskal-Wallis Error: {e}\n")
                    
                try:
                    stat_l, p_l = levene(*valid_samples)
                    f.write(f"Levene Test (Varianze): p={p_l:.4f} -> {'SIGNIFICATIVO' if p_l < 0.05 else 'Non significativo'}\n")
                except Exception as e:
                    f.write(f"Levene Test Error: {e}\n")
            else:
                f.write("Dati insufficienti per i test statistici.\n")
            
            f.write("\n")
            
        f.write("="*100 + "\n")