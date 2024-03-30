import imaplib, email, os
from email.header import decode_header
from src.process_xml import ProcessXml
from src.process_path import get_downloaded_ids
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.logging import RichHandler
import logging
import socket
from ssl import SSLEOFError

c = Console()

# Configurar o logger para redirecionar a saída para um arquivo de log
log_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

log_file_path = os.path.join(log_folder, "main.log")

# Configurar o logger para redirecionar a saída para o arquivo de log
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()
logger.addHandler(RichHandler())

def login_imap(username, password, imap_server):
    try:
        # Conectar ao servidor IMAP
        mail = imaplib.IMAP4_SSL(imap_server)
        # Fazer login na conta de e-mail
        mail.login(username, password)
        c.print(Panel('[green]Conexão IMAP estabelecida com sucesso![/]', style='#9400d3'))
        return mail
    except imaplib.IMAP4.error as e:
        print(f"Falha ao conectar ao servidor IMAP: {e}")
        return None
    
def add_marker_to_email(mail, email_id, marker):
    try:
        mail.select('inbox')
        mail.store(email_id, '+X-GM-LABELS', f'({marker})')
    except Exception as e:
        print(f"Erro ao adicionar marcador ao e-mail: {e}")

def scan_and_download_xml_attachments(download_folder, mail_connection, label, rename):
    try:
        mail_connection.select('inbox')

        # Obter IDs dos e-mails com anexos
        _, messages = mail_connection.search(None, 'ALL')
        email_ids = messages[0].split()

        # Obter IDs dos arquivos já baixados
        downloaded_ids = get_downloaded_ids(download_folder)

        c.print('\n')
        c.rule('\nBaixando XML', style='#9400d3')
        c.print(f"Emails na caixa de entrada: {len(email_ids)}\n", justify='center')
        count = 0

        # Verificar se a pasta de download existe
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        for email_id in email_ids:
            if mail_connection.noop()[0] != 'OK':
                raise Exception("Conexão com o servidor de e-mails perdida")
            
            _, msg_data = mail_connection.fetch(email_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue

                filename = part.get_filename()

            # Decodificar o cabeçalho do filename de forma mais robusta
                try:
                    filename_info = decode_header(filename)
                    if filename_info[0][1] is not None:
                        filename, encoding = filename_info[0]
                        filename = filename.decode(encoding or 'utf-8')
                    else:
                        # Lidar com o caso em que filename_info[0][1] é None
                        filename = filename_info[0][0]
                        encoding = 'utf-8'  # Ou escolha um valor padrão

                except Exception as e:
                    # Lidar com qualquer exceção durante a decodificação do cabeçalho
                    logger.error(f'Erro ao decodificar cabeçalho: {e}  - {email_id}')

                # Verificar se o anexo é um arquivo XML
                if filename and filename.lower().endswith(".xml"):
                    xml_content = part.get_payload(decode=True).decode('utf-8')
                    process_xml = ProcessXml(content=xml_content)
                    item_id = process_xml.extract_item_id()
                    item_emissor = process_xml.extract_emissor_name()
                    item_ano = process_xml.extract_year_from_xml()
                    item_mes = process_xml.extract_mes()

                    emissor_path = download_folder + f'\\{item_emissor}'
                    ano_path = emissor_path + f'\\{item_ano}'
                    mes_path = ano_path + f'\\{item_mes}'

                    # Verificar se o ID já foi baixado
                    if item_id not in downloaded_ids:

                        if not os.path.exists(emissor_path):
                            os.makedirs(emissor_path)

                        if not os.path.exists(ano_path):
                            os.makedirs(ano_path)
                        
                        if not os.path.exists(mes_path):
                            os.makedirs(mes_path)

                        if rename == 'True': filename = f'{item_id}.xml'
                        
                        # Criar caminho para o arquivo de destino
                        dest_path = os.path.join(mes_path, filename)

                        add_marker_to_email(mail_connection, email_id, label)

                        # Salvar o conteúdo XML no arquivo
                        try:
                            with open(dest_path, 'w', encoding='utf-8') as xml_file:
                                xml_file.write(xml_content)
                            c.print(f'[magenta]{item_id}[/] - [green]Baixado[/]')
                            count += 1
                        except Exception as e:
                            c.print(f'[magenta]{item_id}[/] - [red]Erro: {e}[/]')
                    else: 
                        add_marker_to_email(mail_connection, email_id, label)
        
        c.print(f"\n[green]Finalizado com sucesso! {count} xml's baixados.[/]")

    
    except (socket.error, SSLEOFError) as e:
        c.print(f"[red]Erro de conexão ao escanear e baixar arquivos XML:[/] {e}")

    except Exception as e:
        c.print(f"[red]Erro ao escanear e baixar arquivos XML:[/] {e, e.__cause__, e.__context__}")

def download_xml_attachments(download_folder, mail_connection, rename, label):
    try:
        mail_connection.select('inbox')

        # Obter IDs dos e-mails com anexos
        _, messages = mail_connection.search(None, 'ALL')
        email_ids = messages[0].split()

        # Obter IDs dos arquivos já baixados
        downloaded_ids = get_downloaded_ids(download_folder)

        c.print('\n')
        c.rule('\nBaixando XML', style='#9400d3')
        c.print(f"Emails na caixa de entrada: {len(email_ids)}\n", justify='center')
        count = 0

        # Verificar se a pasta de download existe
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        for email_id in email_ids:
            if mail_connection.noop()[0] != 'OK':
                raise Exception("Conexão com o servidor de e-mails perdida")
            
            _, msg_data = mail_connection.fetch(email_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue

                filename = part.get_filename()

                # Decodificar o cabeçalho do filename de forma mais robusta
                try:
                    filename_info = decode_header(filename)
                    if filename_info[0][1] is not None:
                        filename, encoding = filename_info[0]
                        filename = filename.decode(encoding or 'utf-8')
                    else:
                        # Lidar com o caso em que filename_info[0][1] é None
                        filename = filename_info[0][0]
                        encoding = 'utf-8'  # Ou escolha um valor padrão

                except Exception as e:
                    # Lidar com qualquer exceção durante a decodificação do cabeçalho
                    logger.error(f'Erro ao decodificar cabeçalho: {e}  - {email_id}')

                # Verificar se o anexo é um arquivo XML
                if filename and filename.lower().endswith(".xml"):
                    xml_content = part.get_payload(decode=True).decode('utf-8')
                    process_xml = ProcessXml(content=xml_content)
                    item_id = process_xml.extract_item_id()

                    # Verificar se o ID já foi baixado
                    if item_id not in downloaded_ids:
                        if rename == 'True': filename = f'{item_id}.xml'

                        # Criar caminho para o arquivo de destino
                        dest_path = os.path.join(download_folder, filename)

                        add_marker_to_email(mail_connection, email_id, label)

                        try:
                            with open(dest_path, 'w', encoding='utf-8') as xml_file:
                                xml_file.write(xml_content)
                            c.print(f'[magenta]{item_id}[/] - [green]Baixado[/]')
                            count += 1
                        except Exception as e:
                            c.print(f'[magenta]{item_id}[/] - [red]Erro: {e}[/]')
                    
                    else: 
                        add_marker_to_email(mail_connection, email_id, label)
                        
        c.print(f"\n[green]Finalizado com sucesso! {count} xml's baixados.[/]")

    except (socket.error, SSLEOFError) as e:
        c.print("[red]Erro de conexão:[/] Conexão com o servidor IMAP perdida.")

    except Exception as e:
        print(f"Erro ao escanear e baixar arquivos XML: {e}")

