from Entities.construcode import ConstruCode, crd
from Entities.files_manipulation import FilesManipulation
from Entities.functions import P
from datetime import datetime 
from getpass import getuser
from typing import Literal, List
import sys

def path_ambiente(param:Literal["prd", "qas"]):
    if param == "qas":
        return f"C:\\Users\\{getuser()}\\Downloads"
    elif param == 'prd':
        if input("Vc está executando em produção. continuar?[s/n] ").lower() == 's':
            return r"\\server008\G\ARQ_PATRIMAR\Setores\dpt_tecnico\projetos_arquitetura\_ARQUITETURA"
        else:
            sys.exit()

class Execute:
    @property
    def files(self) -> FilesManipulation:
        return self.__files
    
    @property
    def constru_code(self) -> ConstruCode:
        return self.__constru_code
    
    def __init__(self, ambiente:Literal["prd", "qas"]) -> None:
        self.__files:FilesManipulation = FilesManipulation(path_ambiente(ambiente))
        self.__constru_code:ConstruCode = ConstruCode(file_manipulation=self.__files)
        
    def start(self):
        time_inicio:datetime = datetime.now()
        
        self.__constru_code.extrair_projetos()
        
        print(P("Finalizado!"))
        print(P(f"tempo de execução {datetime.now() - time_inicio}", color='white'))
        
        
    def versionar(self) -> None:
        for empreendimento in self.__files.find_empreendimentos():
            empreendimento.versionar_arquivos()
        
if __name__ == "__main__":
    argv:List[str] = sys.argv
    
    if len(argv) <= 1:
        print(P("é necessario informar os argumentos para iniciar"))
        print(P("[start, verificar_disciplinas, versionar]"))
    else:
        execute:Execute = Execute('qas')
        
        if argv[1].lower() == "start":
            execute.start()        
        elif argv[1].lower() == "verificar_disciplinas":
            execute.constru_code.verificar_disciplinas()
            print(P("disciplinas verificadas!"))
        elif argv[1].lower() == "versionar":
            execute.versionar()
            print("arquivos versionados!")