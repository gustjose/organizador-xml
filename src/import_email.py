import imaplib, email, os
from email.header import decode_header
from process_xml import ProcessXml
from dotenv import load_dotenv
from rich.logging import RichHandler
import logging
from plyer import notification
from win10toast import ToastNotifier

# Configurar o logger para redirecionar a saída para um arquivo de log
log_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

log_file_path = os.path.join(log_folder, "organizador-xml.log")

# Configurar o logger para redirecionar a saída para o arquivo de log
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()
logger.addHandler(RichHandler())

# Adicione essa linha para testar se o logger está funcionando corretamente
logger.info("Início do log")

load_dotenv()

username = os.getenv('USER')
password = os.getenv('SENHA')
imap_server = os.getenv('IMAP_SERVER')
download_folder = os.getenv('FOLDER_DOWNLOAD')
rename = os.getenv('RENAME')
label = os.getenv('LABEL')

def get_downloaded_ids(download_folder):
    # Obter IDs dos arquivos já baixados na pasta de download
    downloaded_ids = set()

    for root, dirs, files in os.walk(download_folder):
        for filename in files:
            if filename.lower().endswith(".xml"):
                item_id = ProcessXml(os.path.join(root, filename)).extract_item_id()
                if item_id:
                    downloaded_ids.add(item_id)

    return downloaded_ids

def login_imap(username, password, imap_server):
    try:
        # Conectar ao servidor IMAP
        mail = imaplib.IMAP4_SSL(imap_server)
        # Fazer login na conta de e-mail
        mail.login(username, password)
        logger.info('Conexao IMAP estabelecida com sucesso.')
        return mail
    except imaplib.IMAP4.error as e:
        logger.error(f"Falha ao conectar ao servidor IMAP: {e}")
        notification.notify(title='Xml Organize', message="Não foi possível conectar no email para importar os XML's!", app_icon='organizador-xml\icone.ico',)
        return None
    
def add_marker_to_email(mail, email_id, marker):
    try:
        mail.select('inbox')
        mail.store(email_id, '+X-GM-LABELS', f'({marker})')
    except Exception as e:
        logger.error(f"Erro ao adicionar marcador ao e-mail: {e}")

def scan_and_download_xml_attachments(download_folder, mail_connection, label, rename):
    try:
        mail_connection.select('inbox')

        # Obter IDs dos e-mails com anexos
        _, messages = mail_connection.search(None, 'ALL')
        email_ids = messages[0].split()

        # Obter IDs dos arquivos já baixados
        downloaded_ids = get_downloaded_ids(download_folder)

        count = 0

        # Verificar se a pasta de download existe
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        for email_id in email_ids:
            _, msg_data = mail_connection.fetch(email_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue

                filename = part.get_filename()

                # Decodificar o cabeçalho do filename
                filename, encoding = decode_header(filename)[0]
                if isinstance(filename, bytes):
                    filename = filename.decode(encoding or 'utf-8')

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
                            logger.info(f"Arquivo '{filename}' (ID: {item_id}) baixado.")
                            count += 1
                        except Exception as e:
                            logger.error(f"Erro '{filename}' (ID: {item_id}): {e}")
                    else: 
                        add_marker_to_email(mail_connection, email_id, label)
        
            if count == 0: 
                notification.notify(title='Xml Organize', message="Nenhum novo arquivo XML encontrado!", app_icon='organizador-xml\icone.ico',)
            else:
                notification.notify(title='Xml Organize', message=f"{count} XML's importados com sucesso!", app_icon='organizador-xml\icone.ico',)

    except Exception as e:
        logger.error(f"Erro ao escanear e baixar arquivos XML: {e}")
        notification.notify(title='Xml Organize', message="Ocorreu um erro ao importar os arquivos XML!", app_icon='organizador-xml\icone.ico',)


mail = login_imap(username, password, imap_server)
if mail:
    scan_and_download_xml_attachments(download_folder, mail, label, rename)