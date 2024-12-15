# Raspagem de dados

import utils
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from datetime import datetime
from bs4 import BeautifulSoup


class WebDriverManager:
    def __init__(self, os='windows', browsers=['chrome'], min_percentage=2.0, fake_useragent = True, proxy=None):
        if fake_useragent:
            # User egent aleatório, evitando a detecção do robô
            ua = UserAgent(os=os, browsers=browsers, min_percentage=min_percentage)
            user_agent = str(ua.random)
        else:
            user_agent = None
        
        self.driver = self._initialize_driver(user_agent, proxy)
        

    def _initialize_driver(self, user_agent=None, proxy=None):
        # Definição das opções do navegador
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        if user_agent is not None:
            options.add_argument(f'user-agent={user_agent}')
        if proxy is not None:
            options.add_argument(f'--proxy-server={proxy}')
         # Instânciação do web driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver


class Azul:
    def __init__(self, driver):
        self.driver = driver

    def research(self, trip_type, dpt_sitio, arrv_sitio, outb_dpt_dt, currency, inbo_dpt_dt=None):
        # Constrói a URL
        url = self.url_building(trip_type, dpt_sitio, arrv_sitio, outb_dpt_dt, currency, inbo_dpt_dt)
        
        # Navega até o site
        self.driver.get(url)

        # Rejeita os cookies
        self.reject_cookies()

        # Carrega mais voos
        self.load_more()

    def url_building(self, trip_type, dpt_sitio, arrv_sitio, outb_dpt_dt, currency, inbo_dpt_dt=None):
        # Trata os parâmetros de entrada
        raw_params = {'trip_type':trip_type, 'dpt_sitio':dpt_sitio, 'arrv_sitio':arrv_sitio, 'outb_dpt_dt':outb_dpt_dt, 'currency':currency, 'inbo_dpt_dt':inbo_dpt_dt}
        # Trata os parâmetros e adiciona um prefixo "_" à chave
        params = self.format_parameters(raw_params)
        
        if params['_trip_type'] == 'OW':
            search_template = 'c[0].ds={_dpt_sitio}&c[0].std={_outb_dpt_dt}&c[0].as={_arrv_sitio}&p[0].t=ADT&p[0].c=1&p[0].cp=false&f.dl=3&f.dr=3&cc={_currency}'
            search = search_template.format(**params)
        elif params['_trip_type'] == 'RT':
            search_template = f'c[0].ds={_dpt_sitio}&c[0].std={_outb_dpt_dt}&c[0].as={_arrv_sitio}&c[1].ds={_arrv_sitio}&c[1].std={_inbo_dpt_dt}&c[1].as={_dpt_sitio}&p[0].t=ADT&p[0].c=1&p[0].cp=false&f.dl=3&f.dr=3&cc={_currency}'
            search = search_template.format(**params)
        else:
            raise ValueError('O parâmetro trip_type: "{trip_type}" não é aceito!')
        url = f'https://www.voeazul.com.br/br/pt/home/selecao-voo?{search}'

        return url

    def format_parameters(self, param_dict):
        treated_params = {}
        for param, raw in param_dict.items():
            # Redefine o nome do parâmetro para evitar conflito
            new_param_name = '_' + param

            if raw is not None:
                treated = raw.strip().upper()
                if param in ('outb_dpt_dt', 'inbo_dpt_dt'):
                    treated = self.convert_date(treated)
                treated_params[new_param_name] = treated
            else:
                treated_params[new_param_name] = treated
        return treated_params
    
    def convert_date(self, date_str):
        """
        Converte uma data no formato 'yyyy-mm-dd' para 'mm/dd/yyyy'.
        """
        try:
            # Converte a string para um objeto datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Converte o objeto datetime para uma string no formato desejado
            formatted_date = date_obj.strftime('%m/%d/%Y')
            return formatted_date
        except ValueError as e: 
            raise ValueError("Formato de data inválido. Use 'yyyy-mm-dd'.") from e


    def reject_cookies(self):
        # (task): Criar validação de existência de cookie

        utils.random_wait(1, 2)  # Aguarda para continuar
        # Seleciona as configurações de cookies
        cookie_setting = self.driver.find_element(
            By.CLASS_NAME, 'cookie-setting-link')
        cookie_setting.click()

        utils.random_wait(1, 2)  # Aguarda para continuar
        # Salva as preferências de cookies (dessabilitadas por padrão)
        save_preference = self.driver.find_element(
            By.CSS_SELECTOR, "[class*='save-preference-btn']")
        save_preference.click()

    def load_more(self):
        """
        Realiza a rolagem da barra de rolagem até o final da página e clica em ver mais voos.
        """
        while True:
            try:
                # Captura o elemento load more
                load_more = self.driver.find_element(By.ID, 'load-more-button')
                # Rola até o elemento
                self.driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", load_more)
                # Clica em uma posição aleatória do elemento
                utils.click_random_position(self.driver, load_more)
                # Aguarda para continuar
                utils.random_wait(2, 3)  
            except: 
                break

    def capture_flights(self):
        # Captura o conteúdo HTML da página
        html_content = self.driver.page_source
        # Parseia o conteúdo HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        # Busca pelos cards de voos
        flights = soup.find_all(class_='flight-card')
        # Cria um dicionário para armazenar os detalhes dos voos
        flight_details = {}
        for flight in flights:
            try:
                id_card = flight.get_attribute_list('id')[0]
                leg_info = flight.find(class_='flight-leg-info').text
                dept_info = flight.find(class_='departure').text
                arrv_info = flight.find(class_='arrival').text
                duration_info = flight.find(class_='duration').text
                fare_info = flight.find(class_='fare').text
                
                # (task): Adicionar lógica para capturar os detalhes do voo

                flight_details[id_card] = {
                    'leg': leg_info,
                    'dept': dept_info,
                    'arrv': arrv_info,
                    'duration': duration_info,
                    'fare': fare_info
                }
            except:
                pass

        return flight_details

    def close_driver(self):
        self.driver.quit()


# Teste

web_driver_manager = WebDriverManager()
azul = Azul(web_driver_manager.driver)

azul.research(trip_type='OW', dpt_sitio='SDU', arrv_sitio='MCZ', outb_dpt_dt='2025-01-20', currency='BRL')

flights = azul.capture_flights()

for id, flight in flights.items():
    print(f'{id} : {flight}')