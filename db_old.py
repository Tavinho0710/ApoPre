import sqlite3
import time
import threading
import pytds
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler


class Database:
	def insert_entry(self, codemp, codfil, codope, codori, numorp, codbar, cont, cel):
		datapo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		query = "select * from usu_tetiqbag where usu_numorp = '{0}' and usu_seqbar = {1}".format(numorp, cont)
		rs_sapiens = None
		rs_backup = self.sapiens_cursor.execute(query).fetchall()
		try:
			with pytds.connect(self.server, self.database, self.user, self.password, timeout=1, login_timeout=1) as conn:
				with conn.cursor() as cursor:
					rs_sapiens = cursor.execute(query).fetchall()
		except Exception as e:
			self.logger.error('Erro ao obter dados' + str(e) + type(e).__name__)
		
		if not rs_sapiens and not rs_backup:
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
			self.sapiens_cursor.execute(query)
			self.sapiens_conn.commit()
			return 1
		else:
			self.logger.warning('Já apontado: ' + str(rs_sapiens) + 'Backup: ' + str(rs_backup))
			return 0
	
	def get_qtdapo(self):
		return self.qtdapo
	
	def get_newop(self, op):
		query = "select numorp, qtdprv from e900cop where CodEmp = 1 AND CodOri = '04' AND NumOrp" \
		        "= {0}".format(op)
		rs = None
		try:
			with pytds.connect(self.server, self.database, self.user, self.password, timeout=2, login_timeout=2) as conn:
				with conn.cursor() as cursor:
					rs = cursor.execute(query).fetchone()
		except Exception as e:
			self.logger.error('Problema ao obter nova OP: ' + str(e))
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
				with pytds.connect(self.server, self.database, self.user, self.password, timeout=2, login_timeout=2) as conn:
					with conn.cursor() as cursor:
						qtde_fardo = list(cursor.execute(query).fetchone())
			except Exception as e:
				self.logger.error('Problema ao alterar OP: ' + str(e))
				return None, None, None
			return rs[0], int(rs[1]), int(qtde_fardo[0])
		else:
			self.logger.warning('Nenhuma OP encontrada')
			return None, None, None
				
	def sync_databases(self):
		sapiens_backup = sqlite3.connect('sapiens_backup.db')
		sapiens_backup_cursor = sapiens_backup.cursor()

		while True:
			time.sleep(3)
			query = 'select * from usu_tetiqbag where usu_sitapo = 0'
			rs = sapiens_backup_cursor.execute(query).fetchall()
			for r in rs:
				r = list(r)
				self.logger.debug('Sincronização: ' + str(r))
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
					with pytds.connect(self.server, self.database, self.user, self.password, timeout=3, login_timeout=3) as conn:
						with conn.cursor() as cursor:
								cursor.execute(query)
						conn.commit()	
					query = "update usu_tetiqbag " \
							"set usu_sitapo = 1 " \
							"where usu_codbar = '{0}'".format(r[5])
					sapiens_backup_cursor.execute(query)
					sapiens_backup.commit()

				except pytds.IntegrityError:
					self.logger.warning('Encontrada chave já apontada no banco de dados principal, verificar colisão:')
					self.logger.warning('Apontamento detectado: ' + str(r))
					query = "update usu_tetiqbag " \
							"set usu_sitapo = 2 " \
							"where usu_codbar = '{0}'".format(r[5])
					sapiens_backup_cursor.execute(query)
					sapiens_backup.commit()
				except Exception as e:
					self.logger.error('Problema ao sincronizar bases: ' + str(e) + type(e).__name__)

				query = 'select usu_seqbar from usu_tetiqbag where usu_numorp = {0}'.format(r[4])
				try:
					with pytds.connect(self.server, self.database, self.user, self.password, timeout=3, login_timeout=3) as conn:
						with conn.cursor() as cursor:
							self.qtdapo = len(cursor.execute(query).fetchall())
				except Exception as e:
					self.logger.error('Não é possível obter quantidade: ' + str(e) + type(e).__name__)
	
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
		self.sapiens_cursor.execute(query)
		self.sapiens_conn.commit()

	def __init__(self, server, database, user, password):		
		self.logger = logging.getLogger('BD')
		self.logger.setLevel('DEBUG')
		formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		handler = TimedRotatingFileHandler(
            'apontamento.log', when='d', interval=1, backupCount=30)
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)

		self.server = server
		self.database = database
		self.user = user
		self.password = password

		self.sapiens_conn = sqlite3.connect('sapiens_backup.db')
		self.sapiens_cursor = self.sapiens_conn.cursor()
		self.create_table()

		#Implementação pra puxar contagem total da OP aberta (já que tá fazendo teste de conexao)
		self.qtdapo = 0

		service_sync_database = threading.Thread(target=self.sync_databases)
		service_sync_database.start()