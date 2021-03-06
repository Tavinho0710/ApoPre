from collections import deque
import time
import threading
import logging
from logging.handlers import TimedRotatingFileHandler
import i2clcd


class Lcd:

    # Se type=1, apaga o visor inteiro pra mostrar a mensagem
    def write_line(self, text, line, type, duration):
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
                self.logger.error("Erro LCD: " + e)

    def __init__(self, ):
        self.logger = logging.getLogger('LCD')
        self.logger.setLevel('DEBUG')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = TimedRotatingFileHandler(
            'apontamento.log', when='d', interval=1, backupCount=30)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.fila_espera = deque()
        self.lcd = i2clcd.i2clcd(i2c_bus=1, i2c_addr=0x27, lcd_width=20)
        self.lcd.init()
        self.lcd.print_line('Inicializando', line=0)
        self.lcd.print_line('Aguarde', line=1)
        time.sleep(3)
        fila = threading.Thread(target=self.fila_t)
        fila.start()
