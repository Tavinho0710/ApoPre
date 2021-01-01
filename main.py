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
		logging.basicConfig(filename='apontamento.log', encoding='utf-8', level='DEBUG')
		logging.info('Inicializando')

		database = self.cp.get('sistema', 'database')
		user = self.cp.get('sistema', 'user')
		pwd = self.cp.get('sistema', 'password')

		logging.info('Incialização da base de dados')
		self.db = Database(database, user, pwd, mode)
		time.sleep(5)

		status = threading.Thread(target=self.status_t)
		status.start()

	def status_t(self):
		while True:
			self.lcd.write_line('Teste 1', 0, 0, 0)
			self.lcd.write_line('Teste 2', 1, 0, 0)
			self.lcd.write_line('Teste 3', 2, 0, 0)
			self.lcd.write_line('Teste 4', 3, 0, 0)
			time.sleep(3)


if __name__ == '__main__':
	Apontamento()
