from notifypy import Notify
import os

def notification(title, message):
    """
    Envia uma notificação de sistema com título, mensagem e ícone personalizados.

    A função utiliza a biblioteca `notifypy` para exibir uma notificação no sistema operacional. 
    O ícone exibido na notificação é definido por um caminho fixo na pasta "assets", relativa ao diretório do script.

    Parâmetros:
    - title (str): Título da notificação.
    - message (str): Mensagem de corpo da notificação.

    Comportamento:
    - Define o nome da aplicação como "XML Organize" para exibição na notificação.
    - Define o ícone como um arquivo "icone.png" localizado na pasta "assets" (um diretório acima do script).
    - Envia a notificação ao sistema operacional.

    Exemplo de Uso:
    notification("Download Concluído", "O arquivo XML foi baixado com sucesso.")
    """
    icon_path = icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets/icone.png"))

    notify = Notify()
    notify.application_name = "XML Organize"
    notify.title = title
    notify.message = message
    notify.icon = icon_path
    notify.send()
