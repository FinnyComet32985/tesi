from data_formatter import data_provider
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import open_connection, close_connection



def test1():


    return


def main():
    connection, cursor = open_connection("db/clash.db")


    data = data_provider()
    test1(data)

    close_connection()

if __name__ == "__main__":
    main()