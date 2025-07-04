import os
import json
from typing import Dict

def ler_disciplinas(file_path:str= os.path.join(os.environ['json_folders_path'], 'disciplinas.json')):
    with open(file_path, 'r', encoding='utf-8')as _file:
        return json.load(_file)


CODIGO_DISCIPLINA = ler_disciplinas


ETAPA_PROJETOS:dict = {
    "EI": "00-ESTUDO INICIAL / PRELIMINAR",
    "AP": "01-ANTEPROJETO",
    "PE": "02-PROJETO EXECUTIVO",
    "PP": "03-PROJETO PRÉ-EXECUTIVO",
    "PL": "04-PROJETO LEGAL COMPLETO",
    "LS": "05-PROJETO LEGAL SIMPLIFICADO",
    "MP": "06-MASTERPLAN",
    "EM": "07-ESTUDO DE MASSA",
    "AB": "08-AS BUILT",
    "MD": "09-MEMORIAL DESCRITIVO",
    "LM": "10-LISTA DE MATERIAIS"
}

SUB_PASTAS = {
#\XXXX-ARQUITETURA    
"ARQL": f"XXXX-ARQUITETURA",

#\XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO
"DETL": f"XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO", "LOCP": f"XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO",
"COLR": f"XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO", "FACE": f"XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO",
"FAER": f"XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO", 
            
#\XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO\\XXXX-ESQUADRIAS
"PCES": f"XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO\\XXXX-ESQUADRIAS",
            
#\XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO\\XXXX-ESQUADRIAS\\XXXX-PROJETO TECNICO-CESQ
"CESQ": f"XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO\\XXXX-ESQUADRIAS\\XXXX-PROJETO TECNICO",
            
#\XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO\\XXXX-EXECUTIVOS
"EXAP": f"XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO\\XXXX-EXECUTIVOS", "EXEG": f"XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO\\XXXX-EXECUTIVOS",
"EXAC": f"XXXX-ARQUITETURA\\XXXX-PROJETO EXECUTIVO\\XXXX-EXECUTIVOS",


#\XXXX-INSTALAÇÕES
"AQUE": f"XXXX-INSTALAÇÕES", "CLEX": f"XXXX-INSTALAÇÕES", "DREN": f"XXXX-INSTALAÇÕES", "ELET": f"XXXX-INSTALAÇÕES", "IESG": f"XXXX-INSTALAÇÕES", "HIDR": f"XXXX-INSTALAÇÕES",
"INCE": f"XXXX-INSTALAÇÕES", "PISC": f"XXXX-INSTALAÇÕES", "PRES": f"XXXX-INSTALAÇÕES", "SPDA": f"XXXX-INSTALAÇÕES", "AUTO":  f"XXXX-INSTALAÇÕES", "CLIM": f"XXXX-INSTALAÇÕES",
"EENE": f"XXXX-INSTALAÇÕES", "IGAS": f"XXXX-INSTALAÇÕES", "TELE": f"XXXX-INSTALAÇÕES", "SGAS": f"XXXX-INSTALAÇÕES",
}
