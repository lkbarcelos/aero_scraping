# Funções Úteis
import time
import random


def random_wait(min_time, max_time):
    """
    Aguarda um tempo aleatório entre min_time e max_time segundos.
    """
    wait_time = random.uniform(min_time, max_time)
    print(f"Aguardando {wait_time:.2f} segundos...")
    time.sleep(wait_time)




