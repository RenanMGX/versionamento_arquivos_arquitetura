from typing import Dict
from getpass import getuser

default:Dict[str, Dict[str,object]] = {
    'credential': {
        'crd': 'ConstruCode'
    },
    'log': {
        'hostname': '127.0.0.1',
        'port': '8000',
        'token': ''
    },
    'path_ambiente': {
        'qas': f"C:\\Users\\{getuser()}\\Downloads",
        'prd': r"\\server008\G\ARQ_PATRIMAR\Setores\dpt_tecnico\projetos_arquitetura\_ARQUITETURA"
    }
}