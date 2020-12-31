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
		self.db = Database()
		time.sleep(5)


if __name__ == '__main__':
	Apontamento()
