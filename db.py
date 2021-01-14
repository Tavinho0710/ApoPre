import logging
import sqlite3
import time
import threading
import pyodbc
from datetime import datetime


class Database:
	def insert_entry(self, codemp, codfil, codope, codori, numorp, codbar, cont, cel):
		datapo = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
		query = "select * from usu_tetiqbag where usu_codbar = '{0}'".format(codbar)
		if self.get_status():
			rs = self.conexao_cursor.execute(query)
			if rs:
				print(rs)
			
	def get_status(self):
		if self.conexao:
			return True
		else:
			return False
		
	def service_t(self):
		self.local = sqlite3.connect('sapiens_backup.db', check_same_thread=False)
		self.local_cursor = self.local.cursor()
		self.create_table()
		self.start_db()
		while True:
			if self.conexao:
				pass
			else:
				time.sleep(3)
				self.start_db()
				
	def start_db(self):
		try:
			conn = pyodbc.connect(
				'DSN={0};UID={1};PWD={2}'.format(self.database, self.user, self.password), timeout=1)
			cursor = conn.cursor()
			cursor.execute('Select * from usu_tetiqbag')
			logging.info('Banco de dados iniciado')
			self.conexao = conn
			self.conexao_cursor = conn.cursor()
			
		except Exception as e:
			logging.error('Falha na conexão com o banco de dados. ' + str(e))
			self.conexao = None
	
	def create_table(self):
		query = """
					CREATE TABLE IF NOT EXISTS usu_tetiqbag (
					usu_codemp INT,
					usu_codfil INT,
					usu_codope INT,
					usu_codori TEXT,
					usu_numorp INT,
					usu_codbar TEXT,
					usu_seqbar INT,
					usu_datapo TEXT,
					usu_celapo INT,
					usu_sitapo INT
					);"""
		self.local_cursor.execute(query)
		self.local.commit()
	
	def __init__(self, database, user, password):
		self.database = database
		self.user = user
		self.password = password
		self.conexao = None
		
		self.conexao_cursor = None
		
		self.local = None
		self.local_cursor = None
		
		service = threading.Thread(target=self.service_t)
		service.start()
