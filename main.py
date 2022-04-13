from codecs import xmlcharrefreplace_errors
from datetime import datetime
from pyexpat.model import XML_CQUANT_PLUS
from zeep import Client, xsd

def init():
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

    print(tipo)

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
    init()