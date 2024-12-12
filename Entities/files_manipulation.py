import os
import re
from .dictionary.dictionary import CODIGO_DISCIPLINA, ETAPA_PROJETOS, SUB_PASTAS
from typing import List, Dict
import shutil
from .functions import tratar_nome_arquivo, P, remover_acentos, Config_costumer
from dependencies.logs import Logs
from datetime import datetime


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
    
    @property
    def folder_teste(self) -> str:
        return self.__folder_teste
    
    
    def __init__(self, *, emp_folder:str, base_path:str, folder_teste:str="") -> None:
        """Metodo construtor ele ira listar os arquivos dentro da pasta

        Args:
            emp_folder (str): caminho da pasta do empreendimento
            base_path (str): caminho base da classe mae

        Raises:
            FileNotFoundError: caso não encontre o arquivo
        """
        self.__base_path:str = base_path
        self.__emp_folder:str = emp_folder
        self.__folder_teste:str = folder_teste
        self.__config:Config_costumer = Config_costumer()
        
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
                disciplina = os.path.join(target, f"{SUB_PASTAS[codigo]}\\XXXX-{tratar_nome_arquivo(disciplina)}".upper())
            except:
                disciplina = os.path.join(target, f"XXXX-{tratar_nome_arquivo(disciplina)}".upper())
        except:
            disciplina = os.path.join(target, f"-- Não Identificado --\\XXXX-{codigo}".upper())
            
        return disciplina.replace("XXXX", self.centro)
    
    def __montar_caminhos_etapa_projeto(self, *, target:str, codigo:str):
        codigo = codigo.upper()
        
        etapa:str
        try:
            etapa = ETAPA_PROJETOS[codigo]
            etapa = os.path.join(target, tratar_nome_arquivo(etapa.upper()))
        except:
            etapa = os.path.join(target, f"-- Não Identificado --\\--{codigo}--".upper())
        
        return etapa
    
    def __identificar_arquivos_antigos(self, path:str, *, pattern:str=r'[A-z]{1}[0-9]{3}-[\d\D]+(?=R[\d\D]+)', onlyFiles: bool=False) -> list:
        """
        Identifica arquivos antigos em um diretório com base no nome da revisão contida no nome do arquigo exp 'R01'.

        Args:
            path (str): O caminho do diretório onde os arquivos serão verificados.
            pattern (int): formula pattern para bib 're' para identificar qual versão do arquivo pelo nome exp 'R01'.

        Returns:
            list: Lista de caminhos dos arquivos antigos.
        """
        if not os.path.exists(path):
            raise Exception(f"caminho não encontrado '{path}'")    

        files:Dict[str, list] = {}
        for values in os.listdir(path):
            file = re.search(pattern, values)
            if file:
                try:
                    files[file.group()].append(file.string)
                except KeyError:
                    files[file.group()] = [file.string]
                    
        arquivos_ultrapassados:list = []
        for key, arquivos in files.items():
            revisoes:Dict[str, list] = {}
            for file in arquivos:
                
                num_revisao = re.search(r'R[0-9]+', file)
                if num_revisao:
                    #file = re.search(pattern, file).group() #type: ignore
                    try:
                        revisoes[num_revisao.group()].append(file)
                    except KeyError:
                        revisoes[num_revisao.group()] = [file]
            try:
                ultima_revisao_temp:tuple = revisoes.popitem()
            except KeyError:
                return []
            ultima_revisao:list = ultima_revisao_temp[1]

            for revisao, values in revisoes.items():
                for file in values:
                    #if file in ultima_revisao:
                    if re.search(pattern, file).group() in [re.search(pattern, file).group() for file in ultima_revisao]:#type: ignore
                        arquivos_ultrapassados.append(file)
        
        if onlyFiles:                
            return arquivos_ultrapassados 
        
        return [os.path.join(path, file) for file in arquivos_ultrapassados]        
    
    def __mover_substituidos(self, path_file:str, *, sub_path:str="SUBSTITUÍDOS") -> None:
        if not os.path.exists(path_file):
            raise Exception(f"o arquivo '{path_file}' não foi encontrado")
        sub_path = os.path.join(os.path.dirname(path_file), sub_path)
        if not os.path.exists(sub_path):
            os.makedirs(sub_path)
        
        try:
            shutil.move(path_file, sub_path)
        except shutil.Error:
            new_file = os.path.join(sub_path, datetime.now().strftime(f'Copia-%d%m%Y%H%M%S__{os.path.basename(path_file)}'))
            shutil.move(path_file, new_file)  
            
    def __organizar_subistituidos(self, path_base:str, *, sub_path:str="SUBSTITUÍDOS") -> None:
        sub_path = os.path.join(path_base, sub_path)

        if os.path.exists(sub_path):
            revisao:Dict[str, list] = {}
            for file in os.listdir(sub_path):
                if os.path.isfile(os.path.join(sub_path, file)):
                    rev = re.search(r'R[0-9]+', file)
                    if rev:
                        try:
                            revisao[rev.group()].append(os.path.join(sub_path, file))
                        except KeyError:
                            revisao[rev.group()] = [os.path.join(sub_path, file)]
            

            for key, values in revisao.items():

                rev_path:str = os.path.join(sub_path, key)
                if not os.path.exists(rev_path):
                    os.makedirs(rev_path)
                
                for file in values:
                    try:
                        shutil.move(file, rev_path)
                    except shutil.Error:
                        new_file = os.path.join(rev_path, datetime.now().strftime(f'Copia-%d%m%Y%H%M%S__{os.path.basename(file)}'))
                        shutil.move(file, new_file)    
                        
                         
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
            if not self.folder_teste:
                target = self.base_path
            else:
                target = self.folder_teste
        
        caminho_para_salvar = self.__identificar_caminho_final(arquivo_original=original_file, target=target, **kargs)
        
        if not os.path.exists(os.path.dirname(caminho_para_salvar)):
            os.makedirs(os.path.dirname(caminho_para_salvar))
        
        shutil.move(original_file, caminho_para_salvar)
        #print(P(f"arquivo salvo no caminho {caminho_para_salvar}"))
        self.logs.register(status='Report', description=f"Arquivo salvo no caminho {caminho_para_salvar}",exception=None)
        
    def versionar_arquivos(self):
        
        print(P(f"Preparando para versionar os aquivos do empreendimento '{self.centro}'"))
        for path, folders, files in os.walk(self.emp_folder):
            #print(path)
            if (os.path.basename(path) in ETAPA_PROJETOS.values()) or ((valid_path:=re.search(r'[A-z]{1}[0-9]{3}+-[\d\D]+', os.path.basename(path)))):
                self.analizados_arquivos_em_analise(path=path, files=files)
                if (arquivos:=self.__identificar_arquivos_antigos(path)):
                    for arquivo in arquivos:
                        self.__mover_substituidos(arquivo)
                self.__organizar_subistituidos(path)
                   
                   
    def analizados_arquivos_em_analise(self, *,path:str, files:list, analise:str="Em Analise"):
        arquivos_em_analise = self.__config.param.get('em_analise')
        if not arquivos_em_analise:
            arquivos_em_analise = []                
        
        if os.path.basename(path) in ETAPA_PROJETOS.values():            
            path_em_analise = os.path.join(path, analise)
            if not os.path.exists(path_em_analise):
                os.makedirs(path_em_analise)
                
            for file in files:
                for arquivo_em_analise in arquivos_em_analise:
                    if arquivo_em_analise in file:
                        file = os.path.join(path, file)
                            
                        self.__mover_substituidos(file, sub_path=path_em_analise)
            
            if (arquivos_na_pasta_em_analise:=os.listdir(path_em_analise)):
                for arquivo_na_pasta_em_analise in arquivos_na_pasta_em_analise:
                    try:
                        arquivo_na_pasta_em_analise_sem_exten = os.path.splitext(arquivo_na_pasta_em_analise)[0]
                        if not arquivo_na_pasta_em_analise_sem_exten in arquivos_em_analise:  
                            arquivo_na_pasta_em_analise = os.path.join(path_em_analise, arquivo_na_pasta_em_analise)            
                            self.__mover_substituidos(arquivo_na_pasta_em_analise, sub_path=path)
                    except Exception as err:
                        print(err)
                
            if not (arquivos_na_pasta_em_analise:=os.listdir(path_em_analise)):
                try:
                    shutil.rmtree(path_em_analise)
                except:
                    pass

            
        
############################################   

class FilesManipulation:
    @property
    def base_path(self):
        path = self.__base_path
        if (path.endswith("\\")) or (path.endswith("/")):
            path = path[0:-1]
        if not os.path.exists(path):
            raise FileNotFoundError(f"Caminho não encontrado! -> {path}")
        return path
    
    @property
    def folder_teste(self) -> bool:
        return self.__folder_teste
    
    def __init__(self, base_path:str, *, folder_teste:bool=False) -> None:
        self.__base_path:str = base_path
        self.__config:Config_costumer = Config_costumer()
        self.__folder_teste:bool = folder_teste
   
    def __str__(self) -> str:
        return self.base_path
    
    def find_empreendimento(self, centro_custo:str) -> EmpreendimentoFolder:
        for _ in range(2):
            for folders in os.listdir(self.base_path):
                folders = os.path.join(self.base_path, folders)
                if os.path.isdir(folders):
                    for folder in os.listdir(folders):
                        result = re.search(centro_custo, folder, re.IGNORECASE)
                        if not result is None:
                            folder = os.path.join(folders, folder)
                            if os.path.isdir(folder):
                                if self.folder_teste:
                                    
                                    folder += "---RPA---"#<------------ apariativo tecnico para testes remover depois
                                    if not os.path.exists(folder):#<------------ apariativo tecnico para testes remover depois
                                        os.makedirs(folder)#<------------ apariativo tecnico para testes remover depois
                                print(folder) #<------------ apariativo tecnico para testes remover depois
                                
                                    #return EmpreendimentoFolder(emp_folder=folder, base_path=self.base_path, folder_teste=folder_teste)
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
    
    
    def find_empreendimentos(self) -> List[EmpreendimentoFolder]:
        try:
            empreendimentos_obj:List[EmpreendimentoFolder] = []
            empreendimentos:list = [] 
            for emp in self.__config.param.get('empreendimentos'):#type: ignore
                if (emp:=re.search(r'[A-z]{1}[0-9]{3}', emp, re.IGNORECASE)):
                    empreendimentos.append(emp.group())
            
            for empr in empreendimentos:
                try:
                    empreendimentos_obj.append(self.find_empreendimento(empr))
                except FileNotFoundError:
                    continue
                
            return empreendimentos_obj
            
        except:
            return []
        

if __name__ == "__main__":
    pass