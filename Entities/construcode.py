from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement # for typing
from selenium.webdriver.chrome.webdriver import WebDriver # for typing
from Entities.files_manipulation import FilesManipulation, EmpreendimentoFolder
from Entities.functions import Config_costumer
from typing import List, Literal, Dict
from time import sleep
import shutil
import re
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from functions import P, verificar_arquivos_download, tratar_nome_arquivo
import traceback
import pandas as pd
import json
from botcity.maestro import * # type: ignore
from multiprocessing.synchronize import Lock as LockType


#crd:dict = Credential(Config()['credential']['crd']).load()

#DISCIPLINAS_FILE_PATH:str = os.path.join(os.getcwd(), f"Entities\\dictionary\\disciplinas.json")
DISCIPLINAS_FILE_PATH:str = os.path.join(os.environ['json_folders_path'], 'disciplinas.json')


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
    
    
    def __init__(self, empreendimento:str, service: Service = None, keep_alive: bool = True) -> None: #type: ignore
        self.__download_path:str = os.path.join(os.getcwd(), 'Downloads', f'Download_Projects_{empreendimento}_')
        print(self.download_path)
        if os.path.exists(self.download_path):
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
    
    def find_element(self, #type: ignore
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
        
        raise Exception(f"'{by}': '{value}' não foi encontrado")

    def find_elements(self,  #type: ignore
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
    
    @property
    def disciplinas_file_path(self):
        return DISCIPLINAS_FILE_PATH
    
    
    def __init__(self, *, maestro:BotMaestroSDK|None=None, file_manipulation:FilesManipulation, email:str, password:str, link:str="https://web.construcode.com.br/", date:datetime=datetime.now(), empreendimento:str=datetime.now().strftime('temp_%d%m%Y%H%M%S'), lock:LockType|None=None) -> None:
        """
        Inicializa uma nova instância da classe ConstruCode.

        Este método inicializa os atributos da classe com os valores fornecidos e inicia a navegação para o link base.

        Args:
            email (str): O email do usuário.
            password (str): A senha do usuário.
            file_manipulation (FilesManipulation): Uma instância da classe FilesManipulation para manipulação de arquivos.
            link (str, opcional): O link base para navegação. O padrão é "https://next.construcode.com.br/".
            date (datetime, opcional): A data atual. O padrão é a data e hora atuais.

        Raises:
            TypeError: Se file_manipulation não for uma instância de FilesManipulation.
        """
        if not isinstance(file_manipulation, FilesManipulation):
            raise TypeError("Apenas objetos do tipo FilesManipulation")
        self.__file_manipulation:FilesManipulation = file_manipulation
        self.__email:str = email
        self.__password:str = password
        self.__base_link:str = link
        self.__date:datetime = date
        self.__start_nav(self.base_link, empreendimento=empreendimento)
        
        self.__maestro:BotMaestroSDK|None = maestro
        if not lock is None:
            self.__config = Config_costumer(lock=lock)
        else:
            self.__config = Config_costumer()
    
    @staticmethod   
    def navegar(f):
        def wrap(self, *args, **kwargs):
            if self.verific_login_window():
                self.login()
            result = f(self, *args, **kwargs)
            return result
        return wrap
    
    @navegar
    def __start_nav(self, link:str, *, timeout:int=5, empreendimento:str):
        """
        Inicia a navegação para o link fornecido e tenta carregar a página.

        Este método tenta abrir a página especificada pelo link e verifica se a página foi carregada com sucesso.
        Se a página não for carregada dentro do tempo limite especificado, uma exceção `PageNotFound` será levantada.

        Args:
            link (str): O URL da página que deve ser carregada.
            timeout (int, opcional): O tempo máximo (em segundos) para tentar carregar a página. O padrão é 5 segundos.

        Raises:
            PageNotFound: Se a página não puder ser carregada dentro do tempo limite especificado.
        """    
        print(P(f"Abrindo a pagina '{link}'"))
        for _ in range(timeout):
            try:
                # Cria uma nova instância do navegador Nav
                self.__nav:Nav = Nav(empreendimento=empreendimento)
                # Tenta acessar o link fornecido
                self.nav.get(link)
                print(P("Pagina Carregada!"))
                return
            except:
                # Se ocorrer um erro, tenta novamente após fechar o navegador e esperar 1 segundo
                print(P("Erro ao carregar a Pagina, Tentando novamente"))
                self.nav.close()
                sleep(1)
        # Se a página não for carregada dentro do tempo limite, levanta uma exceção
        raise PageNotFound("não foi possivel carregar a pagina")
    
    def verific_login_window(self) -> bool:
        """
        Verifica se a janela de login está aberta.

        Este método tenta encontrar os elementos de entrada de email e senha na página atual.
        Se os elementos forem encontrados, assume-se que a janela de login está aberta.

        Returns:
            bool: Retorna True se a janela de login estiver aberta, caso contrário, False.
        """        
        try:
            # Tenta encontrar o campo de senha
            self.nav.find_element('id', 'password', tries=1)
            # Tenta encontrar o campo de email
            self.nav.find_element('id', 'email', tries=1)
            print(P("Abriu uma tela de Login"))
            return True
        except:
            return False


    def login(self, no_exception:bool=False) -> bool:
        #if self.verific_login_window():
        try:
            self.nav.find_element('id', 'email', tries=1)
        except:
            return True
        
        self.nav.find_element('id', 'email', tries=1).send_keys(self.email)
        self.nav.find_element('id', 'password', tries=1).send_keys(self.password)
        self.nav.find_element('id', 'password', tries=1).send_keys(Keys.RETURN)
            
        if "senha inserida está incorreta." in self.nav.find_element('id', 'login-form', tries=1, wait=2, force=True).text:
            print(self.email, self.password)
            raise LoginError("senha inserida está incorreta.")
        print(P("Login Efetuado"))
        return True
        # else:
        #     if not no_exception:
        #         raise LoginError("não foi possivel fazer login")
        #     return False
        
    @navegar      
    def __listar_arquivos(self, *, emprendimento:str, link:str, base_link:str="https://construcode.com.br/") -> List[dict]:
        print(P(f"Iniciando Listagem de projetos do empreendimento {emprendimento}"))
        #self.nav.get(link)
        
        if (project_id:=re.search(r'(?<=%3D)[\d]+', link)):
            project_ralatorio_link:str = f"{base_link}Relatorio/Index?id={project_id.group()}"
        #self.nav.find_element('xpath', '//*[@id="menuLateral"]/li[9]/a').click()
        self.nav.get(project_ralatorio_link) #type: ignore
        if self.verific_login_window():
            self.login()
            self.nav.get(project_ralatorio_link) #type: ignore
                
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
        
        executou_primeira_vez:list
        try:
            executou_primeira_vez = self.__config.param['executou_primeira_vez']
        except KeyError:
            executou_primeira_vez = []
            
        em_analise = []
        
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
                if ((id:=tag_tr.get_attribute('id')) != "") and (("Liberado com ressalvas" in tag_tr.text) or ("Liberado para obra" in tag_tr.text) or ("Em análise" in tag_tr.text)):
                    url:str = os.path.join(base_link, f"Plantas/View?id={id}")
                    name:str = tag_tr.find_element(By.TAG_NAME, 'a').text
                    
                    if not pasta_empreendimento.file_exist(name):
                        parar = False
                        projetos.append({'url': url, 'name': name})
                    
                    if "Em análise" in tag_tr.text:
                        em_analise.append(name)
            
            paginate:WebElement = self.nav.find_element(By.ID, 'datatableListraMestra_next')
            if "disable" in str(paginate.get_attribute("class")):
                break
            else:
                for _ in range(60):
                    try:
                        paginate.location_once_scrolled_into_view
                        paginate.click()
                        break
                    except:
                        sleep(1)
                    
            sleep(1)
            if centro_custo in executou_primeira_vez:
                #print(P(f"{centro_custo} já executou uma primeira vez"))
                if parar:
                    continue
                    #break

        self.__config.add(em_analise=list(set(em_analise)))
        
        executou_primeira_vez.append(centro_custo)
        self.__config.add(executou_primeira_vez=list(set(executou_primeira_vez)))

        return projetos
    
    def __verificar_2_abas(self, *, timeout:int=60, espera:int=3, num_abas:int=1) -> bool:
        agora = datetime.now()
        tempo_espera = agora
        for _ in range(timeout):
            logic = agora >= (tempo_espera + relativedelta(seconds=espera))
            if len(self.nav.window_handles) <= num_abas:
                if logic:
                    return True
            else:
                tempo_espera = datetime.now()
            agora = datetime.now()
            sleep(1)
        
        raise Exception("não foi possivel esperar ficar com apenas 1 aba aberta")
            
    sleep(1)   
    def __download_dos_projetos(self, *, dados:dict, files_manipulation:EmpreendimentoFolder):
        if not os.path.exists(self.nav.download_path):
            os.makedirs(self.nav.download_path)
        
        self.nav.get(dados['url'])
        if self.verific_login_window():
            self.login()
            self.nav.get(dados['url'])
            
        #TEMPORARIO APAGAR DEPOIS   
        target = ""
        #########################
        
        nome = self.nav.find_element('id', 'ViewDataTitle').text

        print(P(f"Carregando Pagina do Projeto '{nome}'", color='blue'))
        
        try:
            #download PDF
            for _ in range(60):
                try:
                    self.nav.find_element('id', 'downloadOriginalFile').click()
                    break
                except:
                    if "0" in str(_ + 1):
                        self.nav.refresh()
                    sleep(1) 
            
            sleep(2)
            #import pdb; pdb.set_trace()
            #self.nav.find_element('xpath', '/html/body/div[13]/div/div[3]/button[2]').click()
            self.nav.find_element('xpath', '/html/body/div[9]/div/div[3]/button[2]').click()
                                           

            self.__verificar_2_abas()
            verificar_arquivos_download(self.nav.download_path, wait=1)
            files_manipulation.copy_file_to(original_file=self.ultimo_download(), target=target, constucode_obj=self)
                 
            self.nav.refresh()
                   
            #download dwg
            for _ in range(60):
                try:
                    self.nav.find_element('id', 'downloadOriginalFile').click()
                    break
                except:
                    if "0" in str(_ + 1):
                        self.nav.refresh()
                    sleep(1)          
                
            self.nav.find_element('xpath', '/html/body/div[13]/div/div[2]/div[3]/label[2]/input').click()
            self.nav.find_element('xpath', '/html/body/div[9]/div/div[3]/button[2]').click()
            self.__verificar_2_abas()
            verificar_arquivos_download(self.nav.download_path, wait=1)    
            files_manipulation.copy_file_to(original_file=self.ultimo_download(), target=target, constucode_obj=self) 
            
            self.nav.refresh()
            
            try:
                #download terceiro arquivo
                for _ in range(60):
                    try:
                        self.nav.find_element('id', 'downloadOriginalFile').click()
                        break
                    except:
                        if "0" in str(_ + 1):
                            self.nav.refresh()
                        sleep(1) 

                self.nav.find_element('xpath', '/html/body/div[13]/div/div[2]/div[3]/label[3]/input').click()
                self.nav.find_element('xpath', '/html/body/div[9]/div/div[3]/button[2]').click()

                self.__verificar_2_abas()
                verificar_arquivos_download(self.nav.download_path, wait=1)
                files_manipulation.copy_file_to(original_file=self.ultimo_download(), target=target, constucode_obj=self)
                    
                self.nav.refresh()
            except:
                pass

            sleep(1)
            print(P(f"Download do Projeto '{nome}' Concluido!", color='green'))
        except:
            print(P(f"O projeto '{nome}' tem apenas um tipo de arquivo para download", color='cyan'))
            
            self.__verificar_2_abas()
            verificar_arquivos_download(self.nav.download_path, wait=1)
            files_manipulation.copy_file_to(original_file=self.ultimo_download(), target=target, constucode_obj=self)
            print(P(f"Download do Projeto '{nome}' Concluido!", color='green'))
            
        self.__verificar_2_abas()
    
    @navegar
    def __listar_empreendimentos(self, centro_custo_empreendimento:list=[]) -> dict:
        if self.verific_login_window():
            self.login()
            self.nav.get(self.base_link)

        try:    
            tag_p_s = self.nav.find_elements('tag name', 'p')
            for tag_p in tag_p_s:
                if "Não quero ver as novidades" in tag_p.text:
                    tag_p.click()
            #self.nav.find_element('xpath', '//*[@id="radix-:r0:"]/div/div/span/p', force=True, tries=2).click()
        except:
            pass
        print(P("Listando Empreendimentos Disponiveis"))
        empreendimentos:dict = {}
        for links in self.nav.find_elements('tag name', 'img'):
            alt = links.get_attribute('alt')
            if alt:
                if not (emp:=re.search(r'[A-z](?<!\d)\d{3}(?!\d)[^\n]+', alt, re.IGNORECASE)) is None:
                    if centro_custo_empreendimento:
                        for centro_custo in centro_custo_empreendimento:
                            centro_custo_encontrado = re.search(r'[A-z]{1}[0-9]{3}', emp.group(), re.IGNORECASE)
                            if not centro_custo_encontrado is None:
                                if centro_custo_encontrado.group() == centro_custo:
                                    url_img = links.get_attribute('src')
                                    if url_img:
                                        emp_id = re.search(r'(?<=_O)[0-9]+(?=_)', url_img).group()#type: ignore
                                        empreendimentos[emp.group()] = f"https://web.construcode.com.br/portal/going?url=%2FProjetos%2FIndex%3Fid%3D{emp_id}"
                                    else:
                                        if not self.__maestro is None:
                                            self.__maestro.alert(
                                                task_id=self.__maestro.get_execution().task_id,
                                                title="Erro em _listar_empreendimentos()",
                                                message=f"não foi possivel determinar o id do emprendimento {centro_custo_encontrado}",
                                                alert_type=AlertType.INFO
                                            )
                                        
                    else:
                        url_img = links.get_attribute('src')
                        if url_img:
                            if (emp_id:=re.search(r'(?<=_O)[0-9]+(?=_)', url_img)):
                                emp_id = emp_id.group()
                            else:
                                #import pdb; pdb.set_trace()
                                continue
                            #emp_id = re.search(r'(?<=_O)[0-9]+(?=_)', url_img).group()
                            empreendimentos[emp.group()] = f"https://web.construcode.com.br/portal/going?url=%2FProjetos%2FIndex%3Fid%3D{emp_id}"
                        else:
                            Logs().register(status='Report', description=f"não foi possivel determinar o id do emprendimento {centro_custo_encontrado}",) #type: ignore
                            
        print(P(f"Empreendimentos encontrados {[key for key,value in empreendimentos.items()]}"))
        
        self.__config.add(empreendimentos=list(set(empreendimentos)))
        
        #import pdb; pdb.set_trace()
        return empreendimentos
    
    @navegar  
    def __obter_disciplinas(self, *,url:str):
        get_id:re.Match|None = re.search(r'(?<=id%3D)[0-9]+', url)
        if get_id is None:
            print(P(f"id não identificado da url {url}", color='red'))
            raise Exception(f"id não identificado da url {url}")
        else:
            emp_id:str = get_id.group()
        
        self.nav.get(f"https://www.construcode.com.br/PadraoNomenclatura/Index?id={emp_id}")
        self.login()
        self.nav.get(f"https://www.construcode.com.br/PadraoNomenclatura/Index?id={emp_id}")
        
        self.nav.find_element('xpath', '/html/body/div[1]/main/div/div[1]/div/div/div[2]/div/div/table/tbody/tr/td[4]/a[1]/i').click()

        self.nav.find_element('xpath', '/html/body/div[1]/main/div/div/div/div/div[2]/div[2]/button').click()
        
        while True:
            try:
                self.nav.find_element('xpath', '/html/body/div[4]/div/div[3]/button[1]')
                sleep(.25)
                continue
            except:
                sleep(1)
                break
            
        self.nav.find_element('xpath', '//*[@id="badge_separadores"]/span[5]').click()
        
        
        
        def obter_elemento_sigla(element:List[WebElement]) -> WebElement:
            for div in element:
                try:
                    for label in div.find_elements(By.TAG_NAME, 'label'):
                        if label.text == 'Definir preenchimento':
                            return div
                except:
                    continue
            raise Exception("Elemento do preenchimento das Siglas não foi encontrado")
        
        #import pdb; pdb.set_trace()
        
        div_lista_siglas:WebElement = obter_elemento_sigla(self.nav.find_elements('class name', 'preenchimentoSigla'))
        
        
        
        
        disciplina:dict = {}

        for div in div_lista_siglas.find_elements(By.TAG_NAME, 'div'):
            if (id_disciplina:=div.get_attribute('id')) != '':
                for input in div.find_elements(By.TAG_NAME, 'input'):
                    if input.get_attribute('name') == f"Referencias[{id_disciplina}].Origem":
                        sigla:str|None = input.get_attribute('value')
                        break
                for span in div.find_elements(By.TAG_NAME, 'span'):
                    if span.get_attribute('role') == 'textbox':
                        nomeclatura:str|None = span.get_attribute('title')
                disciplina[sigla] = nomeclatura #type: ignore
                del sigla; del nomeclatura            #type: ignore         
        
        
        
        return disciplina
    
    @navegar    
    def ultimo_download(self) -> str:
        for _ in range(60):
            sleep(1)
            lista_arquivos:list = [os.path.join(self.nav.download_path, file) for file in os.listdir(self.nav.download_path)]
            arquivo:str = max(lista_arquivos, key=os.path.getctime)
            sleep(1)
            if '.crdownload' in arquivo:
                #print(arquivo)
                del lista_arquivos
                del arquivo
                continue
            else:
                return arquivo
        raise Exception("não foi possivel identificar ultimo download")
        
    @navegar 
    def extrair_projetos(self, centro_custo_empreendimento:list=[]):
        """metodo Principal

        Args:
            centro_custo_empreendimento (list, optional): lista com centro de custo dos empreendiemnto que serão verificados no site. Defaults to [].

        Raises:
            Exception: Caso os empreendimentos na lista não sejem encontrados
        """
        print(P("Iniciando Automação no Site"))
        
        if not os.path.exists(self.disciplinas_file_path):
            self.verificar_disciplinas()
        
        with open(self.disciplinas_file_path, 'r', encoding='utf-8')as _file:
            empreendimentos_com_disciplina:list = list(json.load(_file).keys())
        
        self.nav.get(self.base_link)
        empreendimentos:dict = self.__listar_empreendimentos(centro_custo_empreendimento)
        
        empreendimentos_sem_disciplina:list = []
        for key, value in empreendimentos.items():
            if key in  empreendimentos_com_disciplina:
                continue
            else:
                empreendimentos_sem_disciplina.append(key)
        
        if empreendimentos_sem_disciplina:
            self.verificar_disciplinas(empreendimentos=empreendimentos_sem_disciplina)
        
        if not empreendimentos:
            raise Exception(f"Empreendimentos não encontrados '{centro_custo_empreendimento}'")
        
        print(P(f"Listando projetos lancados na data de hoje por empreendimento!"))
        for key,value in empreendimentos.items():
            empreendimentos[key] = self.__listar_arquivos(emprendimento=key, link=value)
        print(P("Listagem de todos os projetos terminada"))
        
        # if not empreendimentos:
        #     raise Exception("sem arquivos para download")
        
        tem_download:bool = False
        for key,value in empreendimentos.items():
            if value:
                tem_download = True
        if not tem_download:
            print(P("sem arquivos para download", color='green'))
            return 
        
        #import pdb; pdb.set_trace()

        print(P("Iniciando Download dos Projetos", color='white'))       
        for key, value in empreendimentos.items():
            try:
                centro = re.search(r'[A-z]{1}[0-9]{3}', key).group() # type: ignore
                files_manipulation = self.file_manipulation.find_empreendimento(centro)
            except Exception as error:
                    if not self.__maestro is None:
                        self.__maestro.alert(
                            task_id=self.__maestro.get_execution().task_id,
                            title="Erro em extrair_projetos",
                            message=str(error),
                            alert_type=AlertType.INFO
                        )
                
                    print(P(str(error), color='red'))
                    continue
            for dados in value:
                try:
                    self.__download_dos_projetos(dados=dados, files_manipulation=files_manipulation)
                except Exception as error:
                    if not self.__maestro is None:
                        self.__maestro.alert(
                            task_id=self.__maestro.get_execution().task_id,
                            title="Erro em extrair_projetos",
                            message=f"Não foi possivel fazer o download do projeto '{dados['url']}'",
                            alert_type=AlertType.INFO
                        )
                    
                    print(P(f"Não foi possivel fazer o download do projeto '{dados['url']}'", color='red'))
                sleep(2)
        print(P("Download Finalizado", color='yellow'))         
                
        #print(P("Fim da Automatação WEB!",color='white'))    
    
    @navegar    
    def verificar_disciplinas(self, empreendimentos:list=[]):
        self.nav.get(self.base_link)
        # if self.verific_login_window():
        #     self.login()
        

        empreendimentos_urls = self.__listar_empreendimentos(centro_custo_empreendimento=[re.search(r'[A-z]{1}[0-9]{3}', x).group() for x in empreendimentos]) #type: ignore
        
        if not empreendimentos_urls:
            raise Exception(f"Empreendimentos não encontrados '{empreendimentos_urls}'")
        
        nomeclatura_disciplinas:dict = {}
        for key, value in empreendimentos_urls.items():
            try:
                nomeclatura_disciplinas[key] = self.__obter_disciplinas(url=value)
            except Exception as error:
                if not self.__maestro is None:
                    self.__maestro.alert(
                        task_id=self.__maestro.get_execution().task_id,
                        title="Erro em verificar_disciplinas",
                        message=str(error),
                        alert_type=AlertType.INFO
                    )                
                print(P(str(error), color='red'))
                continue
            
        if not os.path.exists(os.path.dirname(self.disciplinas_file_path)):
            os.makedirs(os.path.dirname(self.disciplinas_file_path))
        
        if os.path.exists(self.disciplinas_file_path):
            with open(self.disciplinas_file_path, 'r', encoding='utf-8') as _file:
                disciplinas_salvas:dict = json.load(_file)
            for key, value in disciplinas_salvas.items():
                if not key in nomeclatura_disciplinas:
                    nomeclatura_disciplinas[key] = value
        
        pd.DataFrame(nomeclatura_disciplinas).to_json(self.disciplinas_file_path, indent=4, force_ascii=False)
        print(P(f"Siglas das Nomeclaturas salvas no caminho {self.disciplinas_file_path}"))

    def obter_empreendimentos(self) -> list:
        emp:dict =  self.__listar_empreendimentos()
        return [re.search(r'[A-z]{1}[0-9]{3}',key).group() for key,value in emp.items()]#type: ignore
    
    
    @navegar
    def teste(self) -> None:
        import pdb;pdb.set_trace()
        self.nav.find_element('class name', 'draggable-wrapperDisciplina')
        lista_disciplinas = self.nav.find_element('id', 'draggable-wrapperDisciplina')
        lista_disciplinas.find_elements('class name', 'disciplinaTextTruncat')
        
#https://www.construcode.com.br/Plantas/View?id=1516854
if __name__ == "__main__":
    pass
