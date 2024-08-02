import xlwings as xw
from xlwings.main import Book
import re
from datetime import datetime
import os
from time import sleep
import json
from typing import Dict

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
        for key, value in kwargs.items():
            self.__param[key] = value
        self.__save()
        self.__load()        
        return self
    
    def reload(self):
        self.__load()
        return self
    
    def delete(self, *args:str):
        for key in args:
            try:
                del self.param[key]
            except:
                continue
        self.__save()
        self.__load()
        
        return self
    
    def __save(self) -> None:
        with open(self.file_path, 'w', encoding='utf-8')as _file:
            json.dump(self.param, _file)
            
    def __load(self) -> None:
        with open(self.file_path, 'r', encoding='utf-8')as _file:
            self.__param = json.load(_file)
        
            
        

    
if __name__ == "__main__":
    bot = Config()
    
    print(bot.param['falhou'])
    