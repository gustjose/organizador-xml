import os
from src.interface import exibir_menu
from src.logger import setup_logger
import logging

# Obter o caminho do diretório do script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Configurar o logger
setup_logger()
logger = logging.getLogger()

# Chamar a função para exibir o menu principal
exibir_menu()
