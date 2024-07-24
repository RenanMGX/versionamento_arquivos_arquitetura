from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement # for typing
from selenium.webdriver.chrome.webdriver import WebDriver # for typing
from Entities.files_manipulation import FilesManipulation, EmpreendimentoFolder
from typing import List, Literal, Dict
from time import sleep
import shutil
import re
import os
from datetime import datetime
from .functions import P, verificar_arquivos_download
from .logs import Logs
import traceback

class LoginError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
class PageNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Nav(Chrome):
    @property
    def download_path(self) -> str:
        return self.__download_path
    
    def __init__(self,service: Service = None, keep_alive: bool = True) -> None: #type: ignore
        self.__download_path:str = os.path.join(os.getcwd(), 'Download_Projects')
        
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        
        for file in os.listdir(self.download_path):
            file = os.path.join(self.download_path, file)
            
            if os.path.isfile(file):
                os.unlink(file)
            elif os.path.isdir(file):
                shutil.rmtree(file)
                
        
        prefs:dict = {"download.default_directory": self.download_path}
        chrome_options: Options = Options()
        chrome_options.add_experimental_option('prefs', prefs)
        
        super().__init__(chrome_options, service, keep_alive)
        print(P("Instanciando Navegador"))
    
    def find_element(self,
                    by:Literal["id", "class name", "css selector", "link text", "name", "partial link text", "tag name", "xpath"]="id",
                    value: str | None = None,
                    *,
                    tries:int = 2,
                    force:bool = False,
                    wait:int = 0
                    ) -> WebElement:
        if wait > 0:
            sleep(wait)
        if tries <= 0:
            return super().find_element(by, value)
        else:
            for _ in range(tries*4):
                try:
                    return super().find_element(by, value)
                except:
                    sleep(0.25)
            if force:
                return super().find_element(By.TAG_NAME, 'html')
        
        raise Exception(f"'{by}: {value}' não foi encontrado")

    def find_elements(self, 
                    by:Literal["id", "class name", "css selector", "link text", "name", "partial link text", "tag name", "xpath"]="id",
                    value: str | None = None,
                    *,
                    tries:int = 2,
                    wait:int = 0
                    ) -> List[WebElement]:
        if wait > 0:
            sleep(wait)
        if tries <= 0:
            return super().find_elements(by, value)
        else:
            for _ in range(tries*4):
                if (result:=super().find_elements(by, value)) != []:
                    return result
                else:
                    sleep(0.25)

            return super().find_elements(by, value)

class ConstruCode:
    @property
    def nav(self) -> Nav:
        return self.__nav
    
    @property
    def email(self) -> str:
        return self.__email
    
    @property
    def password(self) -> str:
        return self.__password
    
    @property
    def base_link(self) -> str:
        return self.__base_link
    
    @property
    def date(self) -> datetime:
        return self.__date
    
    @property
    def file_manipulation(self) -> FilesManipulation:
        return self.__file_manipulation
    
    def __init__(self, *, email:str, password:str, file_manipulation:FilesManipulation, link:str="https://next.construcode.com.br/", date:datetime=datetime.now()) -> None:
        if not isinstance(file_manipulation, FilesManipulation):
            raise TypeError("Apenas objetos do tipo FilesManipulation")
        self.__file_manipulation:FilesManipulation = file_manipulation
        self.__email:str = email
        self.__password:str = password
        self.__base_link:str = link
        self.__date:datetime = date
        self.__start_nav(self.base_link)
        
        self.__logs:Logs = Logs(name="ConstruCode")
                
    def __start_nav(self, link:str, *, timeout:int=5):
        print(P(f"Abrindo a pagina '{link}'"))
        for _ in range(timeout):
            try:
                self.__nav:Nav = Nav()
                self.nav.get(link)
                print(P("Pagina Carregada!"))
                return
            except:
                print(P("Erro ao carregar a Pagina, Tentando novamente"))
                self.nav.close()
                sleep(1)
        raise PageNotFound("não foi possivel carregar a pagina")
        
    def __verific_login_window(self) -> bool:
        try:
            self.nav.find_element('id', 'password', tries=1)
            self.nav.find_element('id', 'email', tries=1)
            print(P("Abriu uma tela de Login"))
            return True
        except:
            return False
        
    def __login(self, no_exception:bool=False) -> bool:
        if self.__verific_login_window():
            self.nav.find_element('id', 'email', tries=1).send_keys(self.email)
            self.nav.find_element('id', 'password', tries=1).send_keys(self.password)
            self.nav.find_element('id', 'password', tries=1).send_keys(Keys.RETURN)
            
            if "senha inserida está incorreta." in self.nav.find_element('id', 'login-form', tries=1, wait=2, force=True).text:
                raise LoginError("senha inserida está incorreta.")
            print(P("Login Efetuado"))
            return True
        else:
            if not no_exception:
                raise LoginError("não foi possivel fazer login")
            return False
        
        
    def __listar_arquivos(self, *, emprendimento:str, link:str, base_link:str="https://construcode.com.br/") -> List[dict]:
        print(P(f"Iniciando Listagem de projetos do empreendimento {emprendimento}"))
        self.nav.get(link)
        
        self.nav.find_element('xpath', '//*[@id="menuLateral"]/li[9]/a').click()
        
        self.nav.find_element('xpath', '//*[@id="datatableListraMestra_length"]/div/select/option[4]').click()
        
        
        tbody = self.nav.find_element('tag name', 'tbody',wait=2)
        if tbody.text == 'Nenhum registro encontrado':
            return []
        
        
        centro_custo = re.search(r'[A-z0-9]{4}', emprendimento)
        if not centro_custo is None:
            centro_custo = centro_custo.group()
            pasta_empreendimento = self.file_manipulation.find_empreendimento(centro_custo)
        else:
            raise Exception(f"Centro de Custo não encontrado {centro_custo}")
        
        projetos:List[dict] = []
        cont = 0
        while True:
            parar:bool = True
            if cont >= 60:
                break
            else:
                cont += 1
                
            tbody = self.nav.find_element('tag name', 'tbody') 
            for tag_tr in tbody.find_elements(By.TAG_NAME, 'tr'):
                if ((id:=tag_tr.get_attribute('id')) != "") and (("Liberado com ressalvas" in tag_tr.text) or ("Liberado para obra" in tag_tr.text)):
                    url:str = os.path.join(base_link, f"Plantas/View?id={id}")
                    name:str = tag_tr.find_element(By.TAG_NAME, 'a').text
                    
                    if not pasta_empreendimento.file_exist(name):
                        parar = False
                        projetos.append({'url': url, 'name': name})
            
            paginate:WebElement = self.nav.find_element(By.ID, 'datatableListraMestra_next')
            if "disable" in str(paginate.get_attribute("class")):
                break
            else:
                paginate.location_once_scrolled_into_view
                sleep(1)
                paginate.click()
            sleep(1)
            if parar:
                break

        return projetos
        
    def __download_dos_projetos(self, *, dados:dict, files_manipulation:EmpreendimentoFolder):
        for _ in range(60):
            self.nav.get(dados['url'])
            if self.__verific_login_window():
                self.__login()
            else:
                break
            sleep(1)
        
        #TEMPORARIO APAGAR DEPOIS   
        target = ""
        #########################
        
                
        nome = self.nav.find_element('id', 'ViewDataTitle').text
        print(P(f"Carregando Pagina do Projeto '{nome}'"))
        
        try:
            #download PDF
            for _ in range(60):
                try:
                    self.nav.find_element('id', 'downloadOriginalFile').click()
                    break
                except:
                    sleep(1)          
                
            self.nav.find_element('xpath', '/html/body/div[13]/div/div[3]/button[2]').click()
            verificar_arquivos_download(self.nav.download_path, wait=1)
            files_manipulation.copy_file_to(original_file=self.ultimo_download(), target=target) 
            
            #download dwg
            for _ in range(60):
                try:
                    self.nav.find_element('id', 'downloadOriginalFile').click()
                    break
                except:
                    sleep(1)          
                
            self.nav.find_element('xpath', '/html/body/div[13]/div/div[2]/div[3]/label[2]/input').click()
            self.nav.find_element('xpath', '/html/body/div[13]/div/div[3]/button[2]').click()
            verificar_arquivos_download(self.nav.download_path, wait=1)
            files_manipulation.copy_file_to(original_file=self.ultimo_download(), target=target) 

            sleep(1)
            print(P(f"Download do Projeto '{nome}' Concluido!"))
        except:
            print(P(f"O projeto '{nome}' tem apenas tipo de arquivo para download"))
            verificar_arquivos_download(self.nav.download_path, wait=1)
            files_manipulation.copy_file_to(original_file=self.ultimo_download(), target=target) 
            
          
        
    def ultimo_download(self) -> str:
        for _ in range(60):
            lista_arquivos:list = [os.path.join(self.nav.download_path, file) for file in os.listdir(self.nav.download_path)]
            arquivo = max(lista_arquivos, key=os.path.getctime)
            if '.crdownload' in arquivo:
                sleep(1)
                continue
            else:
                break
        return arquivo
        

    def start(self, centro_custo_empreendimento:list=[]):
        
        print(P("Iniciando Automação no Site"))
        self.__login()
        self.nav.find_element('xpath', '//*[@id="radix-:r0:"]/div/div/span/p', force=True, tries=2).click()


        print(P("Listando Empreendimentos Disponiveis"))
        empreendimentos:dict = {}
        for links in self.nav.find_elements('tag name', 'a'):
            if not (emp:=re.search(r'[A-z](?<!\d)\d{3}(?!\d)[^\n]+', links.text, re.IGNORECASE)) is None:
                if centro_custo_empreendimento:
                    for centro_custo in centro_custo_empreendimento:
                        centro_custo_encontrado = re.search(r'[0-9A-z]{4}', emp.group(), re.IGNORECASE)
                        if not centro_custo_encontrado is None:
                            if centro_custo_encontrado.group() == centro_custo:
                                empreendimentos[emp.group()] = links.get_attribute('href')
                else:
                    empreendimentos[emp.group()] = links.get_attribute('href')
        print(P(f"Empreendimentos encontrados {[key for key,value in empreendimentos.items()]}"))
        
        if not empreendimentos:
            raise Exception(f"Empreendimentos não encontrados '{centro_custo_empreendimento}'")
        
        print(P(f"Listando projetos lancados na data de hoje por empreendimento!"))
        for key,value in empreendimentos.items():
            empreendimentos[key] = self.__listar_arquivos(emprendimento=key, link=value)
        print(P("Listagem de todos os projetos terminada"))
        
        if not empreendimentos:
            raise Exception("sem arquivos para download")

        print(P("Iniciando Download dos Projetos"))       
        for key, value in empreendimentos.items():
            try:
                centro = re.search(r'[A-z]{1}[0-9]{3}', key).group() # type: ignore
                files_manipulation = self.file_manipulation.find_empreendimento(centro)
            except Exception as error:
                    self.__logs.register(status='Error', description=str(error), exception=traceback.format_exc())
                    print(P(error))
                    continue
            for dados in value:
                try:
                    self.__download_dos_projetos(dados=dados, files_manipulation=files_manipulation)
                except Exception as error:
                    self.__logs.register(status='Error', description=f"Não foi possivel fazer o download do projeto '{dados['url']}'", exception=traceback.format_exc())
                    print(P(f"Não foi possivel fazer o download do projeto '{dados['url']}'"))
                sleep(2)
        print(P("Download Finalizado"))         
                
        print(P("Fim da Automatação WEB!"))    
        

        
        
#https://www.construcode.com.br/Plantas/View?id=1516854
if __name__ == "__main__":
    pass