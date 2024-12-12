# Raspagem de dados

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time


class WebDriverManager:
    def __init__(self, os='windows', browsers=['chrome', 'edge'], min_percentage=2.0):
        self.ua = UserAgent(os=os, browsers=browsers,
                            min_percentage=min_percentage)
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        # User egent aleatório, evitando a detecção do robô
        user_agent = str(self.ua.random)
        # Definição das opções do navegador
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument(f'user-agent={user_agent}')
        # Instânciação do web driver
        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)
        return driver


class Azul:
    def __init__(self, driver):
        self.driver = driver

    def research(self, trip_type, dpt_sitio, arrv_sitio, outb_dpt_dt, currency, inbo_dpt_dt=None):
        # (task): tratar inputs de data antes de usar
        if trip_type == 'OW':
            busca = f'c[0].ds={dpt_sitio}&c[0].std={outb_dpt_dt}&c[0].as={
                arrv_sitio}&p[0].t=ADT&p[0].c=1&p[0].cp=false&f.dl=3&f.dr=3&cc={currency}'
        elif trip_type == 'RT':
            busca = f'c[0].ds={dpt_sitio}&c[0].std={outb_dpt_dt}&c[0].as={arrv_sitio}&c[1].ds={arrv_sitio}&c[1].std={
                inbo_dpt_dt}&c[1].as={dpt_sitio}&p[0].t=ADT&p[0].c=1&p[0].cp=false&f.dl=3&f.dr=3&cc={currency}'

        url = f'https://www.voeazul.com.br/br/pt/home/selecao-voo?{busca}'

        self.driver.get(url)

    def reject_cookies(self):
        # (task): Criar validação de existência de cookie

        time.sleep(2)  # Aguarda 2 segundos
        # Seleciona as configurações de cookies
        cookie_setting = self.driver.find_element(
            By.CLASS_NAME, 'cookie-setting-link')
        cookie_setting.click()

        time.sleep(2)  # Aguarda 2 segundos
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
