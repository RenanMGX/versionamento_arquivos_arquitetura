import xlwings as xw
from xlwings.main import Book
import re
from datetime import datetime
import os
from time import sleep

def fechar_excel(path:str):
    try:
        for apps in xw.apps:
            for open_app in apps.books:
                open_app:Book
                if open_app.name in path:
                    open_app.close()
                    if len(xw.apps) <= 0:
                        apps.kill()
                    return True
        return False
    except:
        return False
    
class P:
    @property
    def date(self) -> str:
        return datetime.now().strftime("[%d/%m/%Y - %H:%M:%S] ")
    def __init__(self, value: object) -> None:
        self.__value:object = value
        
    def __str__(self) -> str:
        return f"{self.date}{self.__value}"
    
def verificar_arquivos_download(path:str, *,timeout:int=60 * 15, wait:int=0) -> bool:
    if wait > 0:
        sleep(wait)
    if os.path.exists(path):
        for _ in range(timeout):
            exist:bool = False
            for file in os.listdir(path):
                if '.crdownload' in file:
                    exist = True
            if not exist:
                sleep(2)
                return True
            sleep(1)
        return False
    return False
    
if __name__ == "__main__":
    agora = datetime.now()
    verificar_arquivos_download(r'R:\Alterar Nomeclatura Projetos - Projetos Executivos\Download_Projects', wait=3)
    print(f"{datetime.now() - agora}")