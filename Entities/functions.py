import xlwings as xw
from xlwings.main import Book
import re
from datetime import datetime
import os
from time import sleep
import json
from typing import Dict, Literal
import unicodedata
from colorama import Fore

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
    
    @property
    def color(self) -> str:
        if self.__color == 'white':
            return Fore.WHITE
        elif self.__color == 'blue':
            return Fore.BLUE
        elif self.__color == 'green':
            return Fore.GREEN
        elif self.__color == 'red':
            return Fore.RED
        elif self.__color =='cyan':
            return Fore.CYAN
        elif self.__color == 'yellow':
            return Fore.YELLOW
        elif self.__color == 'magenta':
            return Fore.MAGENTA
        else:
            return Fore.RESET
    
    def __init__(self, value: str, *, color:Literal['white', 'red', 'blue', 'green', 'cyan', 'yellow', 'magenta', 'nenhum'] = "nenhum") -> None:
        self.__value:str = value
        self.__color:str = color
        
    def __str__(self) -> str:
        return f"{self.date}{self.color + self.__value + Fore.RESET}"
    
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
                sleep(3)
                return True
            sleep(1)
        return False
    return False

def tratar_nome_arquivo(nome:str) -> str:
    return re.sub(r'[|\\/:*?"<>]', "-", nome)

class Config:
    @property
    def file_path(self) -> str:
        return self.__file_path
    
    @property
    def param(self) -> dict:
        return self.__param
    
    
    def __init__(self, *, file_path:str=os.path.join(os.getcwd(), 'Entities\\config.json')) -> None:
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        for _ in range(2):
            try:
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                    break
            except FileNotFoundError:
                file_path = os.path.join(os.getcwd(), file_path)
                sleep(1)
        
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as _file:
                json.dump({}, _file)
        
        self.__file_path:str = file_path
        
        with open(self.file_path, 'r', encoding='utf-8') as _file:
            self.__param:dict = json.load(_file)
            
    def add(self, **kwargs):
        self.__load()
        for key, value in kwargs.items():
            self.__param[key] = value
        self.__save()
        self.__load()
        print(P(f"no arquivo de config '{kwargs}' foi adicionado"))   
        return self
    
    def reload(self):
        self.__load()
        return self
    
    def delete(self, *args:str):
        self.__load()
        for key in args:
            try:
                del self.param[key]
            except:
                continue
        self.__save()
        self.__load()
        print(P(f"no arquivo de config '{args}' foi deletado"))        
        return self
    
    def __save(self) -> None:
        with open(self.file_path, 'w', encoding='utf-8')as _file:
            json.dump(self.param, _file)
            
    def __load(self) -> None:
        with open(self.file_path, 'r', encoding='utf-8')as _file:
            self.__param = json.load(_file)
        
            
def remover_acentos(texto):
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    
if __name__ == "__main__":
    bot = Config()
    
    print(bot.param['falhou'])
    