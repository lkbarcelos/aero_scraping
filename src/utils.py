# Funções Úteis
import time
import random
from selenium.webdriver.common.action_chains import ActionChains


def random_wait(min_time, max_time):
    """
    Aguarda um tempo aleatório entre min_time e max_time segundos.
    """
    wait_time = random.uniform(min_time, max_time)
    
    time.sleep(wait_time)

def click_random_position(driver, element, min_wait=0.2, max_wait=1.1):
    """
    Move o mouse para uma posição aleatória dentro do elemento, aguarda um tempo aleatório e clica nele.
    """
    # Obtém o tamanho do elemento
    width = element.size['width']
    height = element.size['height']
    
    # Gera uma posição aleatória dentro do elemento
    random_x = random.randint(0, width - 1)
    random_y = random.randint(0, height - 1)
    
    # Move o mouse para a posição aleatória
    actions = ActionChains(driver)
    actions.move_to_element_with_offset(element, random_x, random_y)
    
    # Aguarda um tempo aleatório
    random_wait(min_wait, max_wait)
    
    # Clica no elemento
    actions.click().perform()