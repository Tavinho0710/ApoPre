from collections import deque
import time, threading, logging
import i2clcd


class Lcd:

	# Se type=1, apaga o visor inteiro pra mostrar a mensagem
	def write_line(self,text, line, type, duration):
		self.fila_espera.append([text, line, type, duration])

	# def write_line(self, text, line, type, duration):
		# self.lcd.print_line(text, line)
		# print(text, line, type, duration)

	def fila_t(self):
		while True:
			try:
				if self.fila_espera:
					text, line, type, duration = self.fila_espera.popleft()
					print(text, line, type, duration)
					if type == 1:
						self.lcd.clear()
					self.lcd.print_line(text, line)
					time.sleep(duration)
			except Exception as e:
				logging.error("Erro LCD: " + e)

	def __init__(self):
		self.fila_espera = deque()
		self.lcd = i2clcd.i2clcd(i2c_bus=1, i2c_addr=0x27, lcd_width=20)
		self.lcd.init()
		self.lcd.print_line('Inicializando', line=0)
		self.lcd.print_line('Aguarde', line=1)
		time.sleep(3)
		fila = threading.Thread(target=self.fila_t)
		fila.start()
