# Raspagem de dados

from src import utils
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from datetime import datetime
from bs4 import BeautifulSoup


class WebDriverManager:
    def __init__(self, os='windows', browsers=['chrome'], min_percentage=2.0):
        self.ua = UserAgent(os=os, browsers=browsers, min_percentage=min_percentage)
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        # User egent aleatório, evitando a detecção do robô
        user_agent = str(self.ua.random)
        # Definição das opções do navegador
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument(f'user-agent={user_agent}')
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

    def capture_flights(self):
        # (task): Adicionar iteração de varregura dos voos:
        #   - Verificar voos existentes;
        #   - Capturar suas informações;
        #   - Buscar por mais voos;
        #   - Filtrar IDs de voos não capturados;
        #   - Repetir a iteração;
        # Busca pelos cards de voos
        flights = self.driver.find_elements(By.CLASS_NAME, 'flight-card')
        flight_details = {}
        for flight in flights:
            # (task): Adicionar lógica para capturar os detalhes do voo
            try:
                id_card = flight.get_attribute('id')
                leg_info = flight.find_element(
                    By.CLASS_NAME, 'flight-leg-info').text
                dept_info = flight.find_element(
                    By.CSS_SELECTOR, "[class*='departure']").text
                arrv_info = flight.find_element(
                    By.CSS_SELECTOR, "[class*='arrival']").text
                duration_info = flight.find_element(
                    By.CSS_SELECTOR, "[class*='duration']").text
                fare_info = flight.find_element(
                    By.CSS_SELECTOR, "[class*='fare']").text

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