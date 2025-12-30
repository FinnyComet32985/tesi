from data_formatter import data_provider
import sys
import os
import pandas as pd
from scipy.stats import chi2_contingency

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
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)

    print("Risultati del Test del Chi-Quadro:")
    print(f"  - Statistica Chi-Quadro: {chi2:.4f}")
    print(f"  - Gradi di Libertà (dof): {dof}")
    print(f"  - P-value: {p_value:.4f}")
    print("\nInterpretazione:")
    if p_value < 0.05:
        print("  - Il p-value è < 0.05. Rifiutiamo l'ipotesi nulla.")
        print("  - C'è una dipendenza statisticamente significativa tra la streak del giocatore e la difficoltà del matchup successivo.")
    else:
        print("  - Il p-value è >= 0.05. Non possiamo rifiutare l'ipotesi nulla.")
        print("  - Non c'è evidenza di una dipendenza tra la streak e la difficoltà del matchup.")

    return


def main():
    connection, cursor = open_connection("db/clash.db")

    # tag di test
    PLAYER_TAG_TO_TEST = "YU889LRR0" # ragnar
    #PLAYER_TAG_TO_TEST = "RP9GVG9" # max
    #PLAYER_TAG_TO_TEST = "QJU20YUL" # blas

    data = data_provider(cursor, PLAYER_TAG_TO_TEST)
    test1(data)

    close_connection(connection)

if __name__ == "__main__":
    main()