import sqlite3


class BancoDeDados:

    def __init__(self):
        self.connection = sqlite3.connect('db.sqlite3')
        self.cursor = self.connection.cursor()

    def criar_tabelas(self, sql):
        self.cursor.execute(sql)

    def inserir_registros(self, sql, params):
        self.cursor.execute(sql, params)
        self.connection.commit()

    def fechar_conexao(self):
        self.connection.close()
