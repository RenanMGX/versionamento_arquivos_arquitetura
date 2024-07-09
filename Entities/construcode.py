from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement # for typing
from selenium.webdriver.chrome.webdriver import WebDriver # for typing
from typing import List, Literal, Dict
from time import sleep
import shutil
import re
import os
from datetime import datetime
from .functions import P, verificar_arquivos_download

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
    
    def __init__(self, *, email:str, password:str, link:str="https://next.construcode.com.br/", date:datetime=datetime.now()) -> None:
        self.__email:str = email
        self.__password:str = password
        self.__base_link:str = link
        self.__date:datetime = date
        self.__start_nav(self.base_link)
                
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
    
        

    def start(self):
        print(P("Iniciando Automação no Site"))
        self.__login()
        self.nav.find_element('xpath', '//*[@id="radix-:r0:"]/div/div/span/p', force=True, tries=2).click()


        print(P("Listando Empreendimentos Disponiveis"))
        empreendimentos:dict = {}
        for links in self.nav.find_elements('tag name', 'a'):
            if not (emp:=re.search(r'[A-z](?<!\d)\d{3}(?!\d)[^\n]+', links.text)) is None:
                empreendimentos[emp.group()] = links.get_attribute('href')
        print(P(f"Empreendimentos encontrados {[key for key,value in empreendimentos.items()]}"))
        
        print(P(f"Listando projetos lancados na data de hoje por empreendimento!"))
        for key,value in empreendimentos.items():
            empreendimentos[key] = self.__listar_arquivos(emprendimento=key, link=value)
        print(P("Listagem de todos os projetos terminada"))

        print(P("Iniciando Download dos Projetos"))       
        for key, value in empreendimentos.items():
            for links_projetos in value:
                self.__download_dos_projetos(links_projetos)
                sleep(2)
        print(P("Download Finalizado"))         
                
        # for l in empreendimentos['A048 - SKYLINE']:
        #     self.nav.get(value)
        #     sleep(2)
        
        #self.nav.get(empreendimentos['A048 - SKYLINE'][0])
        #import pdb; pdb.set_trace()  
        print(P("Fim da Automatação WEB!"))    
        import pdb; pdb.set_trace() 
        

    def __listar_arquivos(self, *, emprendimento:str, link:str, base_link:str="https://construcode.com.br/") -> List[str]:
        print(P(f"Iniciando Listagem de projetos do empreendimento {emprendimento}"))
        self.nav.get(link)
        
        self.nav.find_element('xpath', '//*[@id="menuLateral"]/li[9]/a').click()
        
        self.nav.find_element('id', 'search_DataEnvio',wait=1).clear()
        self.nav.find_element('id', 'search_DataEnvio').send_keys(self.date.strftime('%d/%m/%Y - %d/%m/%Y'))
        self.nav.find_element('id', 'search_DataEnvio').send_keys(Keys.RETURN)
        self.nav.find_element('xpath', '/html/body/header/nav/ol/li[3]',wait=1).click()
        
        tbody = self.nav.find_element('tag name', 'tbody',wait=2)
        if tbody.text == 'Nenhum registro encontrado':
            return []
        
        links_projetos:List[str] = []
        for tag_a in tbody.find_elements(By.TAG_NAME, 'a'):
            url_tratar:str = str(tag_a.get_attribute('href'))
            if not (id_plan:=re.search(r'[0-9]+', url_tratar)) is None:
                links_projetos.append(os.path.join(base_link, f"Plantas/View?id={id_plan.group()}"))
        
        return links_projetos
        
    def __download_dos_projetos(self, link:str):
        for _ in range(60):
            self.nav.get(link)
            if self.__verific_login_window():
                self.__login()
            else:
                break
            sleep(1)
            
        nome = self.nav.find_element('id', 'ViewDataTitle').text
        print(P(f"Carregando Pagina do Projeto '{nome}'"))
        
        
        #download PDF
        for _ in range(60):
            try:
                self.nav.find_element('id', 'downloadOriginalFile').click()
                break
            except:
                sleep(1)          
            
        self.nav.find_element('xpath', '/html/body/div[13]/div/div[3]/button[2]').click()
        verificar_arquivos_download(self.nav.download_path, wait=1)
        
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

        sleep(1)
        
        #import pdb; pdb.set_trace()  
        
        
#https://www.construcode.com.br/Plantas/View?id=1516854
if __name__ == "__main__":
    pass