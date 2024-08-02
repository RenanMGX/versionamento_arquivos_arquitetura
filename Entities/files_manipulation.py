import os
import re
from .dictionary.dictionary import CODIGO_DISCIPLINA, ETAPA_PROJETOS, SUB_PASTAS
from typing import List, Dict
import shutil
from .functions import tratar_nome_arquivo, P
from Entities.logs import Logs


class EmpreendimentoFolder:
    @property
    def caminhos(self) -> List[str]:
        return self.__value
    
    @property
    def arquivos(self) -> List[str]:
        return [os.path.basename(path) for path in self.__value]
    
    @property
    def base_path(self):
        return self.__base_path
    
    @property
    def emp_folder(self) -> str:
        return self.__emp_folder
    
    @property
    def pattern(self) -> str:
        return r'[A-z]{1}[0-9]{3}-[\D\d]+-R[0-9]+'
    
    @property
    def centro(self) -> str:
        emp_folder:str = os.path.basename(self.emp_folder)
        centro = re.search(r'[A-z]{1}[0-9]{3}', emp_folder)
        if not centro is None:
            return centro.group()
        raise Exception(f"centro de custo não foi identificado do caminho {emp_folder}")
    
    @property
    def logs(self):
        return self.__logs
    
    
    def __init__(self, *, emp_folder:str, base_path:str) -> None:
        """Metodo construtor ele ira listar os arquivos dentro da pasta

        Args:
            emp_folder (str): caminho da pasta do empreendimento
            base_path (str): caminho base da classe mae

        Raises:
            FileNotFoundError: caso não encontre o arquivo
        """
        self.__base_path:str = base_path
        self.__emp_folder:str = emp_folder
        
        if (self.__emp_folder.endswith("\\")) or (self.__emp_folder.endswith("/")):
            self.__emp_folder = self.__emp_folder[0:-1]
            
        if not os.path.exists(self.__emp_folder):
            raise FileNotFoundError(f"Caminho não encontrado! -> {self.__emp_folder}")       
        
        self.__value:List[str] = self.__list_files(self.__emp_folder)
        
        self.__logs:Logs = Logs(name="EmpreendimentoFolder")
        
    def __str__(self) -> str:
        return self.__emp_folder
    
    def __list_files(self, folder:str) -> list:
        """lista os arquivos dentro da pasta informada

        Args:
            folder (str): pasta para procurar os arquivos

        Returns:
            list: lista de arquivos encontrados
        """
        caminhos:list = []
        for paths, folders, files in os.walk(folder):
            for file in files:
                #if (file.endswith('.pdf')) or (file.endswith(".dwg")):
                if re.findall(self.pattern, file, re.IGNORECASE):
                    caminhos.append(os.path.join(paths, file))
        return caminhos
    
    def __preparar_caminho(self, path:str) -> str:
        """prepar o caminho para copiar o arquivo

        Args:
            path (str): pasta base para preparação

        Returns:
            str: caminho da pasta Projetos preparada
        """
        emp_folder:str = os.path.join(path, (os.path.join(os.path.basename(os.path.dirname(self.emp_folder)), os.path.basename(self.emp_folder))))
        
        #import pdb; pdb.set_trace()
        #emp_folder = os.path.join(emp_folder, f"{self.centro}-PROJETOS")
        return emp_folder
    
    def __identificar_caminho_final(self, *, arquivo_original:str, target:str, **kargs):
        target = self.__preparar_caminho(target)

        codigos_arquivos_procurar:re.Match|None = re.search(self.pattern, arquivo_original)
        if not codigos_arquivos_procurar is None:
            codigos_arquivos:list = str(codigos_arquivos_procurar.group()).split('-')
            codigo_disciplina_arquivo = codigos_arquivos[2]
            codigo_etapa_arquivo = codigos_arquivos[3]
        else:
            raise Exception(f"Arquivo não encontrado '{arquivo_original}'")
        
        
        target = self.__montar_caminhos_disciplina(target=target, codigo=codigo_disciplina_arquivo, **kargs)
        
        target = self.__montar_caminhos_etapa_projeto(target=target, codigo=codigo_etapa_arquivo)
        
        if not os.path.exists(target):
            os.makedirs(target)
           
        return os.path.join(target, os.path.basename(arquivo_original))
    
    def __montar_caminhos_disciplina(self, *, target:str, codigo:str, **kargs) -> str:
        codigo = codigo.upper()
        
        SELECTED_CODIGO_DISCIPLINA:dict
        
        CODIGO_DISCIPLINA_HERDADO:Dict[str,Dict[str,str]] = CODIGO_DISCIPLINA()
        
        for key,value in CODIGO_DISCIPLINA_HERDADO.items():
            if self.centro.upper() in key.upper():
                SELECTED_CODIGO_DISCIPLINA = value
        
        try:
            disciplina = SELECTED_CODIGO_DISCIPLINA[codigo]
            try:
                disciplina = os.path.join(target, f"{SUB_PASTAS[codigo]}\\XXXX-{disciplina}".upper())
            except:
                disciplina = os.path.join(target, f"XXXX-{disciplina}".upper())
        except:
            disciplina = os.path.join(target, f"** Não Identificado **\\{self.centro}-{codigo}".upper())
            
        return disciplina.replace("XXXX", self.centro)
    
    def __montar_caminhos_etapa_projeto(self, *, target:str, codigo:str):
        codigo = codigo.upper()
        
        etapa:str
        try:
            etapa = ETAPA_PROJETOS[codigo]
            etapa = os.path.join(target, etapa.upper())
        except:
            etapa = os.path.join(target, f"** Não Identificado **\\--{codigo}--".upper())
        
        return etapa
        
    
    def file_exist(self, _file:str) -> bool:
        """verifica se o arquivo existe na pasta

        Args:
            _file (str): arquivo

        Returns:
            bool: Verdadeiro se o arquivo existir Falso se não existir
        """
        result = [file for file in self.arquivos if re.search(_file, file, re.IGNORECASE)]
        if result:
            return True
        return False
    
    def get_caminho(self, value:str) -> str:
        """encontra o caminho completo do arquivo caso encontre

        Args:
            value (str): arquivo

        Returns:
            str: caso encontre retorne o caminho completo do arquivo
        """
        for path in self.caminhos:
            if value in path:
                return path
        return "None"
    
    def copy_file_to(self, *, original_file:str, target:str="", **kargs):
        if target == "":
            target = self.base_path
        
        caminho_para_salvar = self.__identificar_caminho_final(arquivo_original=original_file, target=target, **kargs)
        
        if not os.path.exists(os.path.dirname(caminho_para_salvar)):
            os.makedirs(os.path.dirname(caminho_para_salvar))
        
        shutil.copy2(original_file, caminho_para_salvar)
        #print(P(f"arquivo salvo no caminho {caminho_para_salvar}"))
        self.logs.register(status='Concluido', description=f"Arquivo salvo no caminho {caminho_para_salvar}",exception=None)
        
    

class FilesManipulation:
    @property
    def base_path(self):
        path = self.__base_path
        if (path.endswith("\\")) or (path.endswith("/")):
            path = path[0:-1]
        if not os.path.exists(path):
            raise FileNotFoundError(f"Caminho não encontrado! -> {path}")
        return path
    
    def __init__(self, base_path:str) -> None:
        self.__base_path:str = base_path
   
    def __str__(self) -> str:
        return self.base_path
    
    def find_empreendimento(self, centro_custo:str, primeiro:bool=True) -> EmpreendimentoFolder:
        for _ in range(2):
            for folders in os.listdir(self.base_path):
                folders = os.path.join(self.base_path, folders)
                if os.path.isdir(folders):
                    for folder in os.listdir(folders):
                        result = re.search(centro_custo, folder, re.IGNORECASE)
                        if not result is None:
                            folder = os.path.join(folders, folder)
                            if os.path.isdir(folder):
                                return EmpreendimentoFolder(emp_folder=folder, base_path=self.base_path)
                
            new_path = os.path.join(self.base_path, f"## Não Encontrados ##\\{centro_custo}")
            if not os.path.exists(new_path):
                os.makedirs(new_path.upper())
            
        # for folders in os.listdir(self.base_path):
        #     folders = os.path.join(self.base_path, folders)
        #     if os.path.isdir(folders):
        #         result = re.search(centro_custo, folders, re.IGNORECASE)
        #         if not result is None:
        #             folder = os.path.join(self.base_path, folders)
        #             return EmpreendimentoFolder(emp_folder=folder, base_path=self.base_path)
                

        raise FileNotFoundError(f"Pasta do Empreendimento não encontrado -> {self.base_path}")
    
        

if __name__ == "__main__":
    pass