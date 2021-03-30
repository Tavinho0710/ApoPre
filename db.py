import logging
import sqlite3
import time
import threading
import pyodbc
from datetime import datetime


class Database:
	def insert_entry(self, codemp, codfil, codope, codori, numorp, codbar, cont, cel):
		datapo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		query = "select * from usu_tetiqbag where usu_numorp = '{0}' and usu_seqbar = {1}".format(numorp, cont)
		rs = None
		try:
			with self.lock:
				rs = self.conexao_cursor.execute(query).fetchall()
		except Exception as e:
			logging.error('Erro ao obter dados' + str(e) + type(e).__name__)
			rs = self.local_insert.execute(query).fetchall()
		if not rs:
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
			self.local_insert_cursor.execute(query)
			self.local_insert.commit()
			return 1
		else:
			logging.warning('Já apontado: ' + str(rs))
			return 0
	
	def get_status(self):
		if self.conexao:
			return True
		else:
			return False
	
	def get_qtdapo(self):
		return self.qtdapo
	
	def get_duplicado(self):
		query = 'select * from usu_tetiqbag where usu_sitapo = 2'
		rs = []
		try:
			rs = self.local_check.execute(query).fetchone()
		except Exception as e:
			logging.exception('Problema' + str(e))
		if rs:
			return True
		else:
			return False
	
	def get_newop(self, op):
		query = "SELECT numorp, qtdprv FROM e900cop WHERE CodEmp = 1 AND CodOri = '04' AND NumOrp" \
		        "= {0}".format(op)
		rs = None
		try:
			with self.lock:
				rs = self.conexao_cursor.execute(query).fetchone()
		except Exception as e:
			logging.error('Problema ao obter nova OP: ' + str(e))
			self.conexao = None
			return None, None, None
		if rs:
			query = """
					SELECT QtdEmb FROM e900qdo, e075der
					where e900qdo.CodEmp = e075der.CodEmp
					and e900qdo.CodPro = e075der.CodPro
					and e900qdo.CodDer = e075der.CodDer
					and e900qdo.CodEmp = 1
					and e900qdo.CodOri = '04'
					and e900qdo.NumOrp = {0}
					""".format(op)
			try:
				with self.lock:
					qtde_fardo = list(self.conexao_cursor.execute(query).fetchone())
					
			except Exception as e:
				logging.error('Problema ao alterar OP: ' + str(e))
				self.conexao = None
				return None, None, None
			return rs[0], int(rs[1]), int(qtde_fardo[0])
		else:
			logging.warning('Nenhuma OP encontrada')
			return None, None, None
				
	def service_t(self):
		self.local = sqlite3.connect('sapiens_backup.db', check_same_thread=False)
		self.local_cursor = self.local.cursor()
		
		self.local_insert = sqlite3.connect('sapiens_backup.db', check_same_thread=False)
		self.local_insert_cursor = self.local_insert.cursor()
		
		self.local_check = sqlite3.connect('sapiens_backup.db', check_same_thread=False)
		self.local_check_cursor = self.local_check.cursor()
		
		self.create_table()
		self.start_db()
		while True:
			try:
				if self.conexao:
					time.sleep(1)
					query = 'select * from usu_tetiqbag where usu_sitapo = 0'
					rs = self.local_cursor.execute(query).fetchall()
					for r in rs:
						r = list(r)
						logging.debug('Sincronização: ' + str(r))
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
							query = "update usu_tetiqbag " \
							        "set usu_sitapo = 1 " \
							        "where usu_codbar = '{0}'".format(r[5])
							self.local_cursor.execute(query)
							self.local.commit()
						except pyodbc.IntegrityError:
							query = "select * from usu_tetiqbag where usu_numorp = {0} and usu_seqbar = {1}".format(r[4], r[6])
							rs = self.conexao.execute(query).fetchall()
							logging.warning('Encontrada chave já apontada no banco de dados principal, verificar colisão:')
							logging.warning('Apontamento original: ' + str(rs[0]))
							logging.warning('Apontamento detectado: ' + str(r))
							query = "update usu_tetiqbag " \
							        "set usu_sitapo = 2 " \
							        "where usu_codbar = '{0}'".format(r[5])
							self.local_cursor.execute(query)
							self.local.commit()
						except Exception as e:
							logging.error('Problema ao sincronizar bases: ' + str(e) + type(e).__name__)
							self.conexao = None
						query = 'select usu_seqbar from usu_tetiqbag where usu_numorp = {0}'.format(r[4])
						try:
							self.qtdapo = len(self.conexao_cursor.execute(query).fetchall())
						except Exception as e:
							logging.error('Não é possível obter quantidade: ' + str(e) + type(e).__name__)
							self.conexao = None
				else:
					time.sleep(2)
					self.start_db()
			except Exception as e:
				logging.error('Erro: ' + str(e) + type(e).__name__)
	
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
		self.lock = threading.Lock()
		
		self.database = database
		self.user = user
		self.password = password
		self.conexao = None
		
		self.conexao_cursor = None
		
		self.local = None
		self.local_cursor = None
		
		self.local_insert = None
		self.local_insert_cursor = None
		
		self.local_check = None
		self.local_check_cursor = None
		
		#Implementação pra puxar contagem total da OP aberta (já que tá fazendo teste de conexao)
		self.qtdapo = 0
		
		service = threading.Thread(target=self.service_t)
		service.start()
