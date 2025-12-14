import sqlite3



def open_connection(db_path):
    try: 
        CONNECTION = sqlite3.connect(db_path)
        CURSOR = CONNECTION.cursor()
        return CONNECTION, CURSOR
    except Exception as e:
        print(f"Error Message: {e}")
        return None