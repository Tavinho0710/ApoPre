import configparser
from datetime import datetime
from zeep import Client, xsd

def setup():
    config = configparser.ConfigParser()

    # Tenta ler o arquivo de configurações.
    try:
        with open('config.ini') as config_file:
            config.read_file(config_file)

    # Caso não encontra o arquivo, fallback para criar um novo arquivo limpo.
    # Detalhe, o aplicativo criará o arquivo, mas irá finalizar. Configure o arquivo e execute novamente.
    except IOError:
        print('Não rolou, criando um novo arquivo limpo')

        config['sistema'] = {
            'svrend': 'svr-erp2',
            'svrprt': '8079',
            'codusu': ' ',
            'senusu': ' '
        }

        config['apontamento'] = {
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
            config.write(config_file)
        exit()

def loop():
    pass

def apontar():
    cliente = Client('http://svr-erp2:8079/g5-senior-services/sapiens_Synccom_senior_g5_co_ger_sid?wsdl')
    tipo = cliente.get_type('ns0:sidExecutarIn')
    codusu = ''
    senusu = ''
    codemp = '1'
    codori = '04'
    codope = '50'
    numorp = '10142'
    codetg = '180'
    seqrot = '80'
    turtrb = '9'
    codcre = 'PR01F2'
    datmov = datetime.now().strftime('%d/%m/%Y')
    hormov = str(datetime.time(datetime.now()))
    qtdpro = '1000'
    requisicao = []
    requisicao.append('acao=SID.Prd.ApontarOps')
    requisicao.append('CodEmp=' + codemp)
    requisicao.append('CodOri=' + codori)
    requisicao.append('NumCad=' + codope)
    requisicao.append('NumOrp=' + numorp)
    requisicao.append('CodEtg=' + codetg)
    requisicao.append('SeqRot=' + seqrot)
    requisicao.append('TurTrb=' + turtrb)
    requisicao.append('CodCre=' + codcre)
    requisicao.append('DatMov=' + datmov)
    requisicao.append('HorMov=' + hormov)
    requisicao.append('QtdRe1=' + qtdpro)
    requisicao.append('QtdRe2=' + '0'   )
    requisicao.append('QtdRfg=' + '0'   )

    mensagem = tipo(SID=requisicao)
    resposta = cliente.service.Executar(codusu, senusu, 0, mensagem)
    print(resposta)

if __name__ == '__main__':
    setup()