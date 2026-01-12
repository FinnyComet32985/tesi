import os
import pandas as pd
import plotly.graph_objects as go

def plot_matchup_trend(sessions, tag, output_dir):
    """Genera un grafico interattivo del matchup (HTML) basato sulle sessioni."""
    
    all_battles = []
    stops_data = {
        'Quit': {'x': [], 'y': [], 'color': 'blue'},
        'Long': {'x': [], 'y': [], 'color': 'purple'},
        'Short': {'x': [], 'y': [], 'color': 'skyblue'}
    }
    
    seq_counter = 1
    
    for session in sessions:
        for battle in session['battles']:
            # Consideriamo solo battaglie con matchup valido per il grafico
            if battle['matchup'] is not None:
                b_data = battle.copy()
                b_data['seq_id'] = seq_counter
                b_data['color'] = 'green' if battle['win'] else 'red'
                
                # Info Tooltip
                trophies_info = ""
                if 'trophies_after' in battle:
                     trophies_info = f"Trofei: {battle.get('trophies_before', '?')} -> {battle['trophies_after']} ({battle.get('variation', 0):+})"
                
                b_data['ladder_info'] = trophies_info
                b_data['crowns_result'] = f"{battle['player_crowns']}-{battle['opponent_crowns']}"
                b_data['opponent'] = battle['opponent'] if battle['opponent'] else "N/A"
                
                all_battles.append(b_data)
                seq_counter += 1
        
        # Gestione linee di stop (Sessioni)
        # Disegniamo la linea tra l'ultima battaglia di questa sessione e la prima della prossima
        # Usiamo seq_counter - 0.5 come posizione approssimativa
        if session['stop_type'] != 'End' and all_battles:
            stop_type = session['stop_type']
            # Mappa i tipi di stop del v2 ai colori/nomi del grafico
            # v2 usa: 'Quit', 'Long', 'Short'
            if stop_type in stops_data:
                x_pos = seq_counter - 0.5
                stops_data[stop_type]['x'].extend([x_pos, x_pos, None])
                stops_data[stop_type]['y'].extend([0, 100, None])

    if not all_battles:
        return

    df = pd.DataFrame(all_battles)
    
    fig = go.Figure()

    # 1. Linea di tendenza generale (Sfondo)
    fig.add_trace(go.Scatter(
        x=df['seq_id'],
        y=df['matchup'],
        mode='lines',
        name='Trend Generale',
        line=dict(color='lightgray', width=1),
        hoverinfo='skip'
    ))

    # 2. Punti raggruppati per Game Mode
    modes = df['game_mode'].unique()
    for mode in modes:
        df_mode = df[df['game_mode'] == mode]
        
        fig.add_trace(go.Scatter(
            x=df_mode['seq_id'],
            y=df_mode['matchup'],
            mode='markers',
            name=mode,
            customdata=df_mode[['game_mode', 'crowns_result', 'opponent', 'ladder_info', 'timestamp']].values,
            hovertemplate=(
                "<b>Partita %{x}</b><br>" +
                "Matchup: %{y:.1f}%<br>" +
                "Modalità: %{customdata[0]}<br>" +
                "Risultato: %{customdata[1]}<br>" +
                "Avversario: %{customdata[2]}<br>" +
                "%{customdata[3]}<br>" +
                "Data: %{customdata[4]}<extra></extra>"
            ),
            marker=dict(size=8, color=df_mode['color'], line=dict(width=1, color='black'))
        ))

    # 3. Linee di Stop (Sessioni)
    for label, s_data in stops_data.items():
        if s_data['x']:
            fig.add_trace(go.Scatter(
                x=s_data['x'],
                y=s_data['y'],
                mode='lines',
                line=dict(color=s_data['color'], dash='dash', width=1),
                name=f"Stop: {label}",
                hoverinfo='skip'
            ))

    # Linea di equilibrio (50%)
    fig.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Equilibrio (50%)")

    fig.update_layout(
        title=f"Trend Matchup - Player: {tag}",
        xaxis_title="Sequenza Partite",
        yaxis_title="Matchup Win Rate (%)",
        template="plotly_white",
        hovermode="x unified"
    )

    # Salvataggio HTML
    graph_path = os.path.join(output_dir, f"matchup_graph_{tag}.html")
    fig.write_html(graph_path)
    print(f"Grafico salvato in: {graph_path}")