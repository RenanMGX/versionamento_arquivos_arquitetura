import os
from patrimar_dependencies.sharepointfolder import SharePointFolders
sharepoint_path = SharePointFolders(r'RPA - Dados\Configs\versionamento arquivos ConstruCode').value
if not sharepoint_path:
    raise FileExistsError(f"O caminho do Sharepoint '{sharepoint_path}' não foi encontrado!")
os.environ['json_folders_path'] = sharepoint_path

from Entities.construcode import ConstruCode
from Entities.files_manipulation import FilesManipulation
from Entities.functions import P
from datetime import datetime 
from getpass import getuser
from typing import Literal, List
import sys
import traceback
import multiprocessing
import multiprocessing.context
import shutil
from botcity.maestro import * #type: ignore
from patrimar_dependencies.screenshot import screenshot
from patrimar_dependencies.gemini_ia import ErrorIA
import traceback
from Entities.processos import Processos

# def path_ambiente(param:str):
#     if param == "qas":
#         return Config()['path_ambiente']['qas']
#     elif param == 'prd':
#         #if input("Vc está executando em produção. continuar?[s/n] ").lower() == 's':
#         return Config()['path_ambiente']['prd']
#         #else:
#         #    sys.exit()

class ExecuteAPP:
    #_path_ambiente = f'C:\\Users\\{os.getlogin()}\\Downloads'
    
    @staticmethod
    def start(*,email:str, password:str, path_ambiente:str, maestro:BotMaestroSDK|None=None, p:Processos=Processos(1)):
        files:FilesManipulation = FilesManipulation(path_ambiente, folder_teste=True)
        constru_code:ConstruCode = ConstruCode(file_manipulation=files, maestro=maestro, email=email, password=password)
        
        empreendimentos:list = constru_code.obter_empreendimentos()
        p.total = len(empreendimentos)
        
        del files
        del constru_code
        
        if empreendimentos:
            tasks: List[multiprocessing.context.Process] = []
            
            for empre in empreendimentos:
                tasks.append(multiprocessing.Process(target=ExecuteAPP.extract, args=([empre],email, password, path_ambiente, p, maestro)))
            
            for task in tasks:
                task.start()
            
            for task in tasks:
                task.join()
            
        else:
            if not maestro is None:
                maestro.alert(
                    task_id=maestro.get_execution().task_id,
                    title="Erro em ExecuteAPP.start()",
                    message="sem empreendimento encontrado",
                    alert_type=AlertType.INFO
                )
            
        path = os.getcwd()
        for x in os.listdir(path):
            if "Download_Projects" in x:
                try:
                    shutil.rmtree(os.path.join(path, x))
                except:
                    pass
            
    @staticmethod
    def extract(empreendimento:list, email:str, password:str, path_ambiente:str, p:Processos, maestro:BotMaestroSDK|None=None):
        try:
            files:FilesManipulation = FilesManipulation(path_ambiente, folder_teste=True, maestro=maestro)
            constru_code:ConstruCode = ConstruCode(file_manipulation=files, empreendimento=empreendimento[0], email=email, password=password, maestro=maestro)
            
            constru_code.extrair_projetos(empreendimento)
                
            ExecuteAPP.versionar(files)
                
            print(P(f"Emprendimento {empreendimento} Finalizado!"))
            p.add_processado()
        except Exception as error:
            print(traceback.format_exc())
            if maestro:
                ia_response = "Sem Resposta da IA"
                try:
                    token = maestro.get_credential(label="GeminiIA-Token-Default", key="token")
                    if isinstance(token, str):
                        ia_result = ErrorIA.error_message(
                            token=token,
                            message=traceback.format_exc()
                        )
                        ia_response = ia_result.replace("\n", " ")
                except Exception as e:
                    maestro.error(task_id=int(maestro.get_execution().task_id), exception=e)
                maestro.error(task_id=int(maestro.get_execution().task_id), exception=error, screenshot=screenshot(), tags={"IA Response": ia_response})
        
    @staticmethod    
    def versionar(files:FilesManipulation, folder_teste=True) -> None:
        for empreendimento in files.find_empreendimentos():
            empreendimento.versionar_arquivos()
            
    @staticmethod
    def verify(*, email:str, password:str, path_ambiente:str, maestro: BotMaestroSDK|None=None):
        files:FilesManipulation = FilesManipulation(path_ambiente, folder_teste=True)
        constru_code:ConstruCode = ConstruCode(file_manipulation=files, email=email, password=password, maestro=maestro)
        
        constru_code.verificar_disciplinas()
    
    @staticmethod       
    def teste(*, email:str, password:str, path_ambiente:str, maestro: BotMaestroSDK|None=None):
        files:FilesManipulation = FilesManipulation(path_ambiente, folder_teste=True)
        constru_code:ConstruCode = ConstruCode(file_manipulation=files, email=email, password=password, maestro=maestro)
        print(constru_code.teste())
    
        
if __name__ == "__main__":
    multiprocessing.freeze_support()
    x = {
        "start": ExecuteAPP.start,
        "verificar_disciplinas": ExecuteAPP.verify,
        "versionar": ExecuteAPP.versionar,
        "teste": ExecuteAPP.teste
    }
    
    from patrimar_dependencies.credenciais import Credential
    
    crd = Credential(
        path_raiz=SharePointFolders(r'RPA - Dados\CRD\.patrimar_rpa\credenciais').value,
        name_file="ConstruCode.json"
    ).load()
    
    ExecuteAPP.start(email=crd['email'], password=crd['password'], path_ambiente=f'C:\\Users\\{os.getlogin()}\\Downloads')
    