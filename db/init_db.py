import sqlite3

def init():
    # database creation
    connection = sqlite3.connect('./db/clash.db')

    # scheme creation
    schema = sql_read("./db/schema.sql")
    connection.executescript(schema)

    connection.commit()

    # card insert
    cards = sql_read("./db/cards.sql")
    connection.executescript(cards)

    connection.commit()

    # palyers insert 
    players = sql_read("./db/players.sql")
    connection.executescript(players)

    connection.commit()

    # closing the connection
    connection.close()


def sql_read(sql_file_path):
    with open(sql_file_path, 'r') as file:
            sql_script = file.read()
    return sql_script




if __name__ == "__main__":
    init()