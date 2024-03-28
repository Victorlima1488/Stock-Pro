import sqlite3
from sqlite3 import Error

def conexao_do_banco():
    db_file = 'app/database/database.db'
    
    try:
        conn = sqlite3.connect(db_file)
    except Error as er:
        print(er)
    return conn