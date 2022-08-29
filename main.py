# Aplicativo para apontamento de bags v2
#
# Nesta versão, o aplicativo não fará somente apontamento
# no banco de dados, mas sim no ERP como um todo.


# TODO: Verificar se é válido trocar configparser por JSON
import configparser
from datetime import datetime
import sys
from zeep import Client, xsd

from utils import Utils

class Apontamento:

    #Realizar as configurações iniciais e preparação da base para apontamento.
    def __init__(self):

        #Testa se o arquivo de configuração funciona
        try:
            Utils.get_config('sistema', 'enderp')
        except:
            sys.exit()

        self.enderp = Utils.get_config('sistema', 'enderp')
        self.prterp = Utils.get_config('sistema', 'prterp')
        self.enddtb = Utils.get_config('sistema', 'enddtb')
        self.prtdtb = Utils.get_config('sistema', 'prtdtb')
        self.codusu = Utils.get_config('sistema', 'codusu')
        self.senusu = Utils.get_config('sistema', 'senusu')
        self.codemp = Utils.get_config('apontamento', 'codemp')
        self.codfil = Utils.get_config('apontamento', 'codfil')
        self.codope = Utils.get_config('apontamento', 'codope')
        self.codori = Utils.get_config('apontamento', 'codori')
        self.numorp = Utils.get_config('apontamento', 'numorp')
        self.codetg = Utils.get_config('apontamento', 'codetg')
        self.seqrot = Utils.get_config('apontamento', 'seqrot')
        self.turtrb = Utils.get_config('apontamento', 'codemp')

        # Caso não encontra o arquivo, fallback para criar um novo arquivo limpo.
        # Detalhe, o aplicativo criará o arquivo, mas irá finalizar. Configure o arquivo e execute novamente.

    def loop(self):
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
    a = Apontamento()

    try:
        while(True):
            a.loop()
    except Exception as e:
        pass
    