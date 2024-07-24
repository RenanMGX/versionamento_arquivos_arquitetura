import csv
import os
from typing import Literal
from datetime import datetime
import re
from .functions import fechar_excel
import traceback

class Logs:
    @property
    def path_folder(self) -> str:
        return self.__path_folder
    
    @property
    def name(self) -> str:
        return self.__name
    
    def __init__(self, *, name:str=' ', path_folder:str=os.path.join(os.getcwd(), 'Logs')) -> None:
        self.__path_folder:str = path_folder
        self.__name:str = name
        if not os.path.exists(self.path_folder):
            os.makedirs(self.path_folder)
            
    def register(self, *, status:Literal['Error', 'Concluido'],  description:str,exception:str=traceback.format_exc(), file:str="Logs_Operation.csv", date_format:str='%d/%m/%Y %H:%M:%S'):
        if not file.endswith('.csv'):
            file += '.csv'
        
        file_path:str = os.path.join(self.path_folder, file)
        
        exception = str(exception)
        exception = re.sub(r'\n', ' <br> ', exception)
        
        description = re.sub(r'\n', ' <br> ', description)
        
        exist:bool = os.path.exists(file_path)
        
        for _ in range(2):
            try:
                with open(file_path, 'a', encoding='utf-8', newline='') as _file:
                    csv_writer = csv.writer(_file, delimiter=';')
                    if not exist:
                        csv_writer.writerow(["Date", "Name", "Status", "Description", "Exception"])
                    csv_writer.writerow([datetime.now().strftime(date_format), self.name, status, description, exception])
                    return
            except PermissionError:
                fechar_excel(file)
            except Exception as error:
                raise error
                
        

if __name__ == "__main__":
    Logs().register(status='Concluido', description="Test")