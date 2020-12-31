import threading
import time
import configparser
import logging
from lcd import Lcd
from db import Database


class Apontamento:
	def __init__(self):
		logging.info('Inicializando')
		logging.basicConfig(filename='apontamento.log', encoding='utf-8', level=logging.DEBUG)

		self.lcd = Lcd()
		self.cp = configparser.ConfigParser()

		self.cp.read('config.ini')
		database = self.cp.get('sistema', 'database')
		user = self.cp.get('sistema', 'user')
		pwd = self.cp.get('sistema', 'password')

		self.db = Database(database, user, pwd)
		time.sleep(5)

		status = threading.Thread(target=self.status_t)
		status.start()

	def status_t(self):
		while True:
			self.lcd.write_line('Teste 1', 0, 0, 0)
			self.lcd.write_line('Teste 2', 0, 0, 0)
			self.lcd.write_line('Teste 3', 0, 0, 0)
			self.lcd.write_line('Teste 4', 0, 0, 0)
			time.sleep(3)


if __name__ == '__main__':
	Apontamento()
