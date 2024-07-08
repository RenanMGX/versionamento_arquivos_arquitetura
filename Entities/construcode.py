from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement # for typing
from selenium.webdriver.chrome.webdriver import WebDriver # for typing
from typing import List, Literal
from time import sleep
import re
import os
from datetime import datetime

class LoginError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
class PageNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Nav(Chrome):
    def __init__(self, options: Options = None, service: Service = None, keep_alive: bool = True) -> None: #type: ignore
        super().__init__(options, service, keep_alive)
    
    def find_element(self,
                    by:Literal["id", "class name", "css selector", "link text", "name", "partial link text", "tag name", "xpath"]="id",
                    value: str | None = None,
                    *,
                    tries:int = 0,
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
                    tries:int = 0,
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
    
    def __init__(self, *, email:str, password:str, link:str="https://next.construcode.com.br/") -> None:
        self.__email:str = email
        self.__password:str = password
        self.__base_link:str = link
        self.__start_nav(self.base_link)
                
    def __start_nav(self, link:str, *, timeout:int=5):
        for _ in range(timeout):
            try:
                self.__nav:Nav = Nav()
                self.nav.get(link)
                return
            except:
                self.nav.close()
                sleep(1)
        raise PageNotFound("não foi possivel carregar a pagina")
        
    def __verific_login_window(self) -> bool:
        try:
            self.nav.find_element('id', 'password', tries=1)
            self.nav.find_element('id', 'email', tries=1)
            return True
        except:
            return False
        
    def __login(self) -> bool:
        if self.__verific_login_window():
            self.nav.find_element('id', 'email', tries=1).send_keys(self.email)
            self.nav.find_element('id', 'password', tries=1).send_keys(self.password)
            self.nav.find_element('id', 'password', tries=1).send_keys(Keys.RETURN)
            
            if "senha inserida está incorreta." in self.nav.find_element('id', 'login-form', tries=1, wait=2, force=True).text:
                raise LoginError("senha inserida está incorreta.")
            return True
        else:
            raise LoginError("não foi possivel fazer login")
         

    def start(self):
        self.__login()
        self.nav.find_element('xpath', '//*[@id="radix-:r0:"]/div/div/span/p', force=True, tries=2).click()


        empreendimentos:dict = {}
        for links in self.nav.find_elements('tag name', 'a'):
            if not (emp:=re.search(r'[A-z](?<!\d)\d{3}(?!\d)[^\n]+', links.text)) is None:
                empreendimentos[emp.group()] = links.get_attribute('href')
        
        self.__empreendimentos = empreendimentos
        
        for key,value in self.__empreendimentos.items():
            self.__coletar_arquivos(emprendimento=key, link=value)

        #import pdb; pdb.set_trace()    
        

    def __coletar_arquivos(self, *, emprendimento:str, link:str, base_link:str="https://construcode.com.br/"):
        self.nav.get(link)
        import pdb; pdb.set_trace()
        self.nav.find_element('xpath', '//*[@id="menuLateral"]/li[9]/a').click()
        
        
        self.nav.find_element('id', 'search_DataEnvio').clear()
        self.nav.find_element('id', 'search_DataEnvio').send_keys(datetime.now().strftime('%d/%m/%Y - %d/%m/%Y'))
        self.nav.find_element('id', 'search_DataEnvio').send_keys(Keys.RETURN)
        self.nav.find_element('xpath', '/html/body/header/nav/ol/li[3]').click()
        


if __name__ == "__main__":
    pass