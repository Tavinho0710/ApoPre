import threading
import time
import configparser
import logging
from lcd import Lcd
# from db import Database


class Apontamento:
	def __init__(self):
		logging.info('Inicializando')
		logging.basicConfig(filename='apontamento.log', )
		print('Inicializando')
		self.lcd = Lcd()
		time.sleep(5)
		# self.db = Database()


if __name__ == '__main__':
	Apontamento()
