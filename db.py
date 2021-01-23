import logging
import sqlite3
import time
import threading
import pyodbc
from datetime import datetime


class Database:
	def insert_entry(self, codemp, codfil, codope, codori, numorp, codbar, cont, cel):
		datapo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		query = "select * from usu_tetiqbag where usu_codbar = '{0}'".format(codbar)
		rs = None
		if self.get_status():
			rs = self.conexao_cursor.execute(query).fetchall()
			if rs:
				print(rs)
			else:
				rs = None
		else:
			rs = self.local_cursor.execute(query).fetchall()
			if rs:
				print(rs)
			else:
				rs = None
		if rs is None:
			query = """insert into usu_tetiqbag
			(usu_codemp ,
			usu_codfil ,
			usu_codope ,
			usu_codori ,
			usu_numorp ,
			usu_codbar ,
			usu_seqbar ,
			usu_datapo ,
			usu_celapo ,
			usu_sitapo)
			values ({0}, {1}, {2}, '{3}', {4}, '{5}', {6}, '{7}', {8}, {9})
			""".format(codemp, codfil, codope, codori, numorp, codbar, cont, datapo, cel, 0)
			self.local_cursor.execute(query)
			self.local.commit()
			return 1
		else:
			return 0
	
	def get_status(self):
		if self.conexao:
			return False
		else:
			return False
	
	def service_t(self):
		self.local = sqlite3.connect('sapiens_backup.db', check_same_thread=False)
		self.local_cursor = self.local.cursor()
		self.create_table()
		self.start_db()
		while True:
			if self.conexao:
				time.sleep(1)
				query = 'select * from usu_tetiqbag where usu_sitapo = 0'
				rs = self.local_cursor.execute(query).fetchall()
				for r in rs:
					r = list(r)
					logging.debug(str(r[0])
					              + str(r[1])
					              + str(r[2])
					              + r[3]
					              + str(r[4])
					              + r[5]
					              + str(r[6])
					              + r[7]
					              + str(r[8]))
					query = """insert into usu_tetiqbag
								(usu_codemp,
								usu_codfil,
								usu_codope,
								usu_codori,
								usu_numorp,
								usu_codbar,
								usu_seqbar,
								usu_datapo,
								usu_celapo)
								values ({0}, {1}, {2}, '{3}', {4}, '{5}', {6}, convert(datetime,'{7}',103), {8})
								""".format(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8])
					try:
						self.conexao_cursor.execute(query)
						self.conexao.commit()
						query = "update table usu_tetiqbag " \
						        "set usu_sitapo = 1 " \
						        "where usu_codbar = '{0}'".format(r[5])
						self.local_cursor.execute(query)
						self.local.commit()
					
					except pyodbc.IntegrityError:
						query = "select * from usu_tetiqbag where usu_codbar = '{}'".format(r[5])
						rs = self.conexao.execute(query).fetchall()
						logging.warning('Encontrada chave já apontada no banco de dados principal, verificar colisão:')
						logging.warning('Apontamento original: ' + str(rs[0]))
						logging.warning('Apontamento detectado: ' + str(r))
					except Exception as e:
						logging.error('Problema ao sincronizar bases: ' + str(e) + type(e).__name__)
						self.conexao = None
			else:
				time.sleep(2)
				self.start_db()
	
	def start_db(self):
		try:
			conn = pyodbc.connect(
				'DSN={0};UID={1};PWD={2}'.format(self.database, self.user, self.password), timeout=1)
			conn.timeout = 1
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
