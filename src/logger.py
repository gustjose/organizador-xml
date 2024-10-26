import os
import logging

def setup_logger():
    """
    Configura o logger para registrar eventos e erros em um arquivo de log com codificação UTF-8.

    Esta função cria um diretório de logs (se ele não existir) e configura o logger do Python para 
    salvar mensagens em um arquivo de log específico. O logger é configurado para registrar mensagens 
    com nível INFO ou superior, e as mensagens são formatadas com data e hora.

    Retorna:
    - logger (obj): Objeto do logger configurado, pronto para uso em outras partes do código.

    Comportamento:
    - Verifica se o diretório de logs e o arquivo de log existem, e cria-os se necessário.
    - Configura um handler de arquivo para salvar mensagens no arquivo "logs.log" com codificação UTF-8.
    - Define o nível de log para INFO e o formato da mensagem com a data.

    Exemplo de Uso:
    logger = setup_logger()
    logger.info("Log configurado com sucesso.")
    """

    # Configurar o caminho para o arquivo de log
    log_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    
    # Verificar se a pasta de logs existe, caso contrário, criar
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_file_path = os.path.join(log_folder, "logs.log")
    
    # Verificar se o arquivo de log existe, caso contrário, criar
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w', encoding='utf-8') as file:
            pass  # Apenas criar o arquivo vazio

    # Criar um handler para o arquivo de log com codificação UTF-8
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

    # Configura o logger com o handler de arquivo
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    return logger