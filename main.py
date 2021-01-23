import threading
import time
import configparser
import logging
import sys
from datetime import datetime
from lcd2 import Lcd
from db import Database


class Apontamento:
	def __init__(self):
		self.lcd = Lcd()
		self.cp = configparser.ConfigParser()
		try:
			self.cp.read('config.ini')
		except Exception as e:
			logging.error('' + str(e) + ' ' + str((datetime.now().strftime('%d/%m/%Y %H:%M:%S'))))
			logging.error('Erro na leitura/gravação do arquivo de config')
			sys.exit()
		mode = int(self.cp.get('modo', 'modo'))
		logging.basicConfig(filename='apontamento.log',
		                    level=mode,
		                    format='%(asctime)s %(levelname)s %(message)s',
		                    datefmt='%d/%m/%Y %H:%M:%S')
		
		logging.info('Inicializando')
		
		database = self.cp.get('sistema', 'database')
		user = self.cp.get('sistema', 'user')
		pwd = self.cp.get('sistema', 'password')
		
		logging.info('Incialização da base de dados')
		
		self.db = Database(database, user, pwd)
		time.sleep(5)
		
		logging.info('Carregando dados de apontamento')
		
		self.codemp = int(self.cp.get('apontamento', 'codemp'))
		self.codfil = int(self.cp.get('apontamento', 'codfil'))
		self.codope = int(self.cp.get('apontamento', 'codope'))
		self.codori = self.cp.get('apontamento', 'codori')
		self.numorp = int(self.cp.get('apontamento', 'numorp'))
		self.qtdprv = int(self.cp.get('apontamento', 'qtdprv'))
		self.qtdfrd = int(self.cp.get('apontamento', 'qtdfrd'))
		
		self.last_codbar = 0
		
		status = threading.Thread(target=self.status_t)
		status.start()
		
		logging.info('Início da leitura do código de barras')
		
		while True:
			codbar: str = input()
			logging.debug('Cod. Barras lido: {0}'.format(codbar))
			if len(codbar) == 10:
				op, contcel = codbar.split('-')
				cont, cel = int(contcel[0:4]), int(contcel[-1])
				op = int(op)
				
				if self.numorp == op:
					result = self.db.insert_entry(self.codemp,
					                              self.codfil,
					                              self.codope,
					                              self.codori,
					                              self.numorp,
					                              codbar,
					                              cont,
					                              cel)
					if result == 0:
						self.lcd.write_line('Já apontado', 0, 1, 2)
					if result == 1:
						self.last_codbar = codbar
			elif len(codbar) == 24:
				nova_op = int(codbar[2:11])
			else:
				self.lcd.write_line('Não reconhecido', 0, 1, 2)
	
	def status_t(self):
		while True:
			self.lcd.write_line('OP: ' + str(self.numorp), 0, 0, 0)
			self.lcd.write_line('Ult: {0}'.format(self.last_codbar), 1, 0, 0)
			self.lcd.write_line('Teste 3', 2, 0, 0)
			self.lcd.write_line('C:' + ('S' if self.db.get_status() else 'N'), 3, 0, 0)
			time.sleep(3)


if __name__ == '__main__':
	Apontamento()
