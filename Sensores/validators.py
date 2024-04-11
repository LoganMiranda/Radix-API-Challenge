from dateutil import parser


def valida_json(dados_sensor):
    try:
        equipmentId = dados_sensor["equipmentId"]
    except:
        raise Exception({"codigo":400, "mensagem": "chave 'equipmentId' nao esta no Json."})        
    
    try:
        timestamp = dados_sensor['timestamp']
    except:
        raise Exception({"codigo":400, "mensagem": "chave 'timestamp' nao esta no Json."})        
    
    try:
        value = dados_sensor["value"]
    except:
        raise Exception({"codigo":400, "mensagem": "chave 'value' nao esta no Json."})
    
    return equipmentId, timestamp, value   


def valida_arquivo(arquivo):
    try:
        arquivo = arquivo.decode('utf-8').splitlines()
        content_type = arquivo[2].split(':')
        if content_type[1] == ' text/csv':
            return arquivo
        else:
            raise Exception({"codigo": 400, "mensagem": 'Arquivo Nao é do tipo csv'})
    
    except:
        raise Exception({"codigo": 400, "mensagem": 'Nao foi possivel decodificar o arquivo. Nao é do tipo csv'})


def valida_equipmentId(equipmentId):
    try:
        if len(str(equipmentId)) > 8:
            raise Exception({"codigo": 400, "mensagem": f"{equipmentId} tem mais que 8 caracteres."})
        else:
            return

    except:
        raise Exception({"codigo": 400, "mensagem": f"{equipmentId} tem mais que 8 caracteres."})



def valida_timestamp(timestamp_recebido):
    try:
        timestamp = parser.parse(timestamp_recebido)
        
    except:
        raise Exception({"codigo": 400, "mensagem":f"'{timestamp_recebido}' nao esta no formato esperado(timestamp with timezone)."})
    
    return timestamp


def valida_value(value):
    try:
        value = float(value)
    
    except:
        raise Exception({"codigo": 400, "mensagem": f"value = '{value}' não é do tipo float."})
    
    return value