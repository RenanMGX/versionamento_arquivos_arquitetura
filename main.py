from Entities.construcode import ConstruCode, crd
from Entities.files_manipulation import FilesManipulation
from Entities.functions import P
from Entities.dependencies.logs import Logs
from datetime import datetime 
from getpass import getuser
from typing import Literal, List
import sys
import traceback
from Entities.dependencies.config import Config
from Entities.dependencies.arguments import Arguments
import multiprocessing
import multiprocessing.context
import shutil
import os

def path_ambiente(param:str):
    if param == "qas":
        return Config()['path_ambiente']['qas']
    elif param == 'prd':
        #if input("Vc está executando em produção. continuar?[s/n] ").lower() == 's':
        return Config()['path_ambiente']['prd']
        #else:
        #    sys.exit()

class Execute:
    _path_ambiente = Config()['path_ambiente'][Config()['ambiente']['ambiente']]
    
    @staticmethod
    def start():
        files:FilesManipulation = FilesManipulation(Execute._path_ambiente, folder_teste=True)
        constru_code:ConstruCode = ConstruCode(file_manipulation=files)
        
        time_inicio:datetime = datetime.now()
        
        empreendimentos:list = constru_code.obter_empreendimentos()
        
        del files
        del constru_code
        
        print(empreendimentos, end=" <----------------------\n")
        
        if empreendimentos:
            tasks: List[multiprocessing.context.Process] = []
            
            for empre in empreendimentos:
                tasks.append(multiprocessing.Process(target=Execute.extract, args=([empre],)))
            
            for task in tasks:
                task.start()
            
            for task in tasks:
                task.close()
            
        else:
            Logs().register(status='Report', description="sem empreendimento encontrado")
            
        path = os.getcwd()
        for x in os.listdir(path):
            if "Download_Projects" in x:
                try:
                    shutil.rmtree(os.path.join(path, x))
                except:
                    pass
        
            
    @staticmethod
    def extract(empreendimento:list):
        files:FilesManipulation = FilesManipulation(Execute._path_ambiente, folder_teste=True)
        constru_code:ConstruCode = ConstruCode(file_manipulation=files, empreendimento=empreendimento[0])
        
        constru_code.extrair_projetos(empreendimento)
            
        Execute.versionar(files)
            
        print(P(f"Emprendimento {empreendimento} Finalizado!"))
        
        
    @staticmethod    
    def versionar(files:FilesManipulation = FilesManipulation(Config()['path_ambiente'][Config()['ambiente']['ambiente']], folder_teste=True)) -> None:
        for empreendimento in files.find_empreendimentos():
            empreendimento.versionar_arquivos()
            
    @staticmethod
    def verify():
        files:FilesManipulation = FilesManipulation(Execute._path_ambiente, folder_teste=True)
        constru_code:ConstruCode = ConstruCode(file_manipulation=files)
        
        constru_code.verificar_disciplinas()
    
    @staticmethod       
    def teste():
        files:FilesManipulation = FilesManipulation(Execute._path_ambiente, folder_teste=True)
        constru_code:ConstruCode = ConstruCode(file_manipulation=files)
        print(constru_code.obter_empreendimentos())
        
if __name__ == "__main__":
    multiprocessing.freeze_support()
    Arguments({
        "start": Execute.start,
        "verificar_disciplinas": Execute.verify,
        "versionar": Execute.versionar,
        "teste": Execute.teste
    })
    
    sys.exit()
    # log = Logs()
    # try:
    #     tempo_inicio:datetime = datetime.now()
    #     argv:List[str] = sys.argv
        
    #     if len(argv) <= 1:
    #         print(P("é necessario informar os argumentos para iniciar"))
    #         print(P("[start, verificar_disciplinas, versionar]"))
    #     else:
    #         execute:Execute = Execute()
            
    #         if argv[1].lower() == "start":
    #             execute.start()
    #             log.register(status='Concluido', description=f"o tempo de execução total script foi de {datetime.now() - tempo_inicio}")       
    #         elif argv[1].lower() == "verificar_disciplinas":
    #             execute.constru_code.verificar_disciplinas()
    #             print(P("disciplinas verificadas!"))
    #             log.register(status='Concluido', description=f"o tempo de execução total da verificação das disciplinas foi de {datetime.now() - tempo_inicio}")
    #         elif argv[1].lower() == "versionar":
    #             execute.versionar()
    #             print("arquivos versionados!")
    #             log.register(status='Concluido', description=f"o tempo de execução total do versionamento foi de {datetime.now() - tempo_inicio}")
    #         if argv[1].lower() == "teste":
    #             execute.teste()
    #             log.register(status='Concluido', description=f"o tempo de execução total script foi de {datetime.now() - tempo_inicio}")       
        
    # except Exception as error:
    #     log.register(status='Error', description="execução no main", exception=traceback.format_exc())
        