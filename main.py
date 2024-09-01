import os
from src.interface import exibir_menu, setup_logger
from dotenv import load_dotenv
import logging

# Configuração inicial
os.system('cls' if os.name == 'nt' else 'clear')

# Obter o caminho do diretório do script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Configurar o logger
setup_logger()
logger = logging.getLogger()

# Carregar variáveis de ambiente
load_dotenv()

# Chamar a função para exibir o menu principal
exibir_menu()
