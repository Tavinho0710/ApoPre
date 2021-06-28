# Controle de apontamento das unidades de acabamento
# Para a execução do código, é necessário a instalação das bibliotecas
# pyodbc, i2clcd
# Autor: Gustavo Niehues

import time
import configparser
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from lcd import Lcd
from db import Database


class Apontamento:
    def __init__(self):

        # Inicialização de logging
        logger = logging.getLogger('Apontamento Bag')
        logger.setLevel('DEBUG')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = TimedRotatingFileHandler(
            'apontamento.log', when='d', interval=1, backupCount=30)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self.lcd = Lcd(logger)
        self.cp = configparser.ConfigParser()

        try:
            self.cp.read('config.ini')
        except Exception as e:
            logger.error('Erro ao recuperar informações de configuração')
            self.lcd.write_line('Erro', 0, 1, )
            sys.exit()

        logger.info('Inicializando')

        server = self.cp.get('sistema', 'server')
        database = self.cp.get('sistema', 'database')
        user = self.cp.get('sistema', 'user')
        pwd = self.cp.get('sistema', 'password')

        logger.info('Incialização da base de dados')

        self.db = Database(logger, server, database, user, pwd)
        time.sleep(5)

        logger.info('Carregando dados de apontamento')

        self.codemp = int(self.cp.get('apontamento', 'codemp'))
        self.codfil = int(self.cp.get('apontamento', 'codfil'))
        self.codope = int(self.cp.get('apontamento', 'codope'))
        self.codori = self.cp.get('apontamento', 'codori')
        self.numorp = int(self.cp.get('apontamento', 'numorp'))
        self.qtdprv = int(self.cp.get('apontamento', 'qtdprv'))
        self.qtdfrd = int(self.cp.get('apontamento', 'qtdfrd'))
        self.numfrd = int(self.cp.get('apontamento', 'numfrd'))

        self.last_codbar = 0
        logger.info('Início da leitura do código de barras')

        try:
            while True:
                self.status()
                codbar: str = input()
                logger.info('Cod. Barras lido: {0}'.format(codbar))
                if (7 <= len(codbar) <= 11) and codbar[4].__eq__('-'):

                    if self.last_codbar == codbar:
                        self.lcd.write_line('Apontado', 0, 1, 1)
                        continue
                    try:
                        op, contcel = codbar.split('-')
                        cont, cel = int(
                            contcel[0:(len(contcel)-1)]), int(contcel[-1])
                        op = int(op)
                    except:
                        logger.info('Código invalido lido')
                        self.lcd.write_line('Nao reconhecido', 0, 1, 1)
                        continue
                        
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
                            self.lcd.write_line('Ja apontado', 0, 1, 2)
                        if result == 1:
                            self.last_codbar = codbar
                            self.lcd.write_line(
                                'Apontado: {0}'.format(codbar), 0, 1, 1)
                            logger.info('Apontado: {0}'.format(codbar))
                            if self.numfrd == self.qtdfrd:
                                self.numfrd = 1
                            else:
                                self.numfrd = self.numfrd + 1
                            self.config_update(
                                'apontamento', 'numfrd', self.numfrd)
                    else:
                        logger.warning(
                            'Tentativa de fazer apontamento com OP errada: ' + str(codbar))
                        self.lcd.write_line('OP nao confere', 0, 1, 2)
                elif len(codbar) == 24 and codbar[0:2].__eq__('04'):
                    nova_op = int(codbar[2:11])
                    if self.numorp != 0 and nova_op != self.numorp:
                        logger.warning(
                            'Não é possível iniciar nova OP sem finalizar a última')
                        self.lcd.write_line('OP nao fechada', 0, 1, 2)
                    elif self.numorp != 0 and nova_op == self.numorp:
                        logger.info('OP fechada: {0}'.format(self.numorp))
                        self.lcd.write_line('OP fechada', 0, 1, 2)
                        self.numorp = 0
                        self.qtdprv = 0
                        self.qtdfrd = 0
                        self.config_update(
                            'apontamento', 'numorp', self.numorp)
                        self.config_update(
                            'apontamento', 'qtdprv', self.qtdprv)
                        self.config_update(
                            'apontamento', 'qtdfrd', self.qtdfrd)
                    else:
                        op, qtdprv, fardo = self.db.get_newop(nova_op)
                        if op:
                            self.numorp = op
                            self.qtdfrd = fardo
                            self.qtdprv = qtdprv
                            self.numfrd = 0
                            logger.info('Dados de OP atualizados: OP - {0}, Qtde prev. - {1}, Qtde fardo - {2}'
                                        .format(op, fardo, qtdprv))
                            self.config_update('apontamento', 'numorp', op)
                            self.config_update('apontamento', 'qtdfrd', fardo)
                            self.config_update('apontamento', 'qtdprv', qtdprv)
                            self.config_update(
                                'apontamento', 'numfrd', self.numfrd)
                            self.lcd.write_line('Nova OP: ' + str(op), 0, 1, 2)
                        else:
                            self.lcd.write_line('Erro OP', 0, 1, 2)
                else:
                    self.lcd.write_line('Nao reconhecido', 0, 1, 2)
                self.status()
        except Exception as e:
            logger.exception('Erro fatal')

        self.lcd.write_line("Fim", 0, 0, 0)
        logger.error("Programa passou do While, verificar")

    def status(self):
        op = 'OP: {0}'.format(str(self.numorp))
        self.lcd.write_line(op, 0, 0, 0)
        self.lcd.write_line('Ult: {0}'.format(self.last_codbar), 1, 0, 0)
        if self.numfrd == self.qtdfrd and self.qtdfrd != 0:
            self.lcd.write_line(
                'Fardo: {0}/{1}!!!'.format(str(self.numfrd), str(self.qtdfrd)), 2, 0, 0)
        else:
            self.lcd.write_line(
                'Fardo: {0}/{1}'.format(str(self.numfrd), str(self.qtdfrd)), 2, 0, 0)
        self.lcd.write_line('Qtde: {0}/{1}'.format(self.db.get_qtdapo() if self.numorp != 0 else str(0),
                                                   self.qtdprv), 3, 0, 0)
        time.sleep(1)

    def config_update(self, section, config, value):
        self.cp.set(section, config, str(value))
        try:
            with open('config.ini', 'w') as configfile:
                self.cp.write(configfile)
        except Exception as e:
            self.lcd.write_line('Erro config', 0, 1, 999999)
            time.sleep(5)
            sys.exit()

if __name__ == '__main__':
    Apontamento()
