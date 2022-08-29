import configparser
from distutils.command.config import config
from logging import exception

class Utils:

    def __init__(self):
        self.cp = configparser.ConfigParser()

    def get_config(self, section, key):

        # Tenta ler o arquivo de configurações.
        try:
            with open('config.ini') as config_file:
                self.cp.read_file(config_file)
            return self.cp.get(section, key)

        # Caso não encontra o arquivo, fallback para criar um novo arquivo limpo.
        # Detalhe, o aplicativo criará o arquivo, mas irá finalizar. Configure o arquivo e execute novamente.
        except IOError:
            print('Config não encontrada, criando um novo arquivo limpo')

            self.cp['sistema'] = {
                'enderp': 'svr-erp2',
                'prterp': '8079',
                'enddtb': 'svr-dberp',
                'prtdtb': '1433',
                'codusu': ' ',
                'senusu': ' '
            }

            self.cp['apontamento'] = {
                'codemp': '1',
                'codfil': ' ',
                'codope': ' ',
                'codori': ' ',
                'numorp': ' ',
                'codetg': ' ',
                'seqrot': ' ',
                'turtrb': ' ',
                'codcre': ' '
            }
            with open('config.ini', 'w') as config_file:
                self.cp.write(config_file)
            raise Exception('Problema ao ler arquivo de configuração, criando novo')


        except configparser.NoSectionError:
            raise Exception('Seção não encontrada')