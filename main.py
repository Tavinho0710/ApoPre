import threading
import time
import configparser
import logging
from lcd import Lcd
from db import Database


class Apontamento:
	def __init__(self):
		self.lcd = Lcd()
		self.cp = configparser.ConfigParser()
		
		self.cp.read('config.ini')
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
		
		self.codemp = self.cp.get('apontamento', 'codemp')
		self.codfil = self.cp.get('apontamento', 'codfil')
		self.codope = self.cp.get('apontamento', 'codope')
		self.codori = self.cp.get('apontamento', 'codori')
		self.numorp = self.cp.get('apontamento', 'numorp')
		self.qtdprv = self.cp.get('apontamento', 'qtdprv')
		self.qtdfrd = self.cp.get('apontamento', 'qtdfrd')
		
		status = threading.Thread(target=self.status_t)
		status.start()
		
		logging.info('Início da leitura do código de barras')
		
		while True:
			pass
	
	def status_t(self):
		while True:
			self.lcd.write_line('OP: '
			                    + self.numorp
			                    + ' '
			                    + '/'
			                    + ' '
			                    + 'Ult: 0', 0, 0, 0)
			self.lcd.write_line('Teste 2', 1, 0, 0)
			self.lcd.write_line('Teste 3', 2, 0, 0)
			self.lcd.write_line('C:'+('S' if self.db.get_status() else 'N'), 3, 0, 0)
			time.sleep(3)


if __name__ == '__main__':
	Apontamento()
