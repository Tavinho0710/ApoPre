import logging
import sqlite3
import threading
import pyodbc


class Database:
	def insert_entry(self):
		pass

	def get_status(self):
		if self.conexao:
			return True
		else:
			return False
		
	def service_t(self):
		self.start_db()
		while True:
			if self.conexao:
				pass
			else:
				self.start_db()
				
	def start_db(self):
		try:
			conn = pyodbc.connect(
				'DSN={0};UID={1};PWD={2}'.format(self.database, self.user, self.password), timeout=1)
			cursor = conn.cursor()
			cursor.execute('Select * from usu_tetiqbag')
			logging.info('Banco de dados iniciado')
			self.conexao = conn
		except Exception as e:
			logging.error('Falha na conexão com o banco de dados. ' + str(e))
			self.conexao = None
	
	def __init__(self, database, user, password):
		self.database = database
		self.user = user
		self.password = password
		self.conexao = None
		
		service = threading.Thread(target=self.service_t)
		service.start()
