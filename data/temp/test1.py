from bs4 import Tag
from data_formatter import data_provider
import sys
import os
import pandas as pd
from scipy.stats import chi2_contingency, chi2

sys.path.append(os.path.join(os.path.dirname(__file__), '../../utils'))

from connection import open_connection, close_connection



def test1(data):
    """
    Esegue un test del chi-quadro per l'indipendenza tra streak e difficoltà del matchup.
    Stampa la tabella di contingenza e i risultati del test.
    """

    if not data:
        print("Dati non sufficienti per eseguire il test.")
        return

    # DataFrame per una facile manipolazione
    df = pd.DataFrame(data, columns=['Streak', 'Matchup'])

    # tabella di contingenza (osservazioni)
    contingency_table = pd.crosstab(df['Streak'], df['Matchup'])

    print("Tabella di Contingenza (Frequenze Osservate):")
    print(contingency_table)
    print("\n" + "="*40 + "\n")

    # test del chi-quadro
    chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)

    # Calcolo del valore critico (soglia teorica) per alpha=0.05
    prob = 0.95
    critical_value = chi2.ppf(prob, dof)

    print("Risultati del Test del Chi-Quadro:")
    print(f"  - Statistica Chi-Quadro Osservata: {chi2_stat:.4f}")
    print(f"  - Valore Critico (Teorico al 95%): {critical_value:.4f}")
    print(f"  - Gradi di Libertà (dof): {dof}")
    print(f"  - P-value: {p_value:.4f}")
    print("\nInterpretazione:")
    if chi2_stat >= critical_value:
        print(f"  - Poiché il Chi-Quadro ({chi2_stat:.4f}) >= Valore Critico ({critical_value:.4f}):")
        print("  - Rifiutiamo l'ipotesi nulla (Dipendenza significativa).")
        print("  - C'è una dipendenza statisticamente significativa tra la streak del giocatore e la difficoltà del matchup successivo.")
    else:
        print(f"  - Poiché il Chi-Quadro ({chi2_stat:.4f}) < Valore Critico ({critical_value:.4f}):")
        print("  - Non possiamo rifiutare l'ipotesi nulla (Indipendenza / Casualità).")
        print("  - Non c'è evidenza di una dipendenza tra la streak e la difficoltà del matchup.")

    print("\n" + "="*40 + "\n")
    return


def load_tags(cursor) -> list:
    """Carica i TAG dei giocatori dal database."""
    try:
        cursor.execute("SELECT player_tag FROM players")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Errore durante il caricamento dei tag: {e}")
        return []
    

def main():
    connection, cursor = open_connection("db/clash.db")

    tags = load_tags(cursor)
    

    for tag in tags:
        data = data_provider(cursor, tag)
        print("\n" + "="*40 + "\n")
        print(tag)
        print("\n" + "="*40 + "\n")
        test1(data)

    close_connection(connection)

if __name__ == "__main__":
    main()