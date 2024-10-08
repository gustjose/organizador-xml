import imaplib, email, os
from email.header import decode_header
from src.process_xml import ProcessXml
from src.process_path import get_downloaded_ids
from rich.console import Console
from rich.panel import Panel
import logging
import socket
from ssl import SSLEOFError

c = Console()

logger = logging.getLogger()

def login_imap(username, password, imap_server):
    try:
        # Conectar ao servidor IMAP
        mail = imaplib.IMAP4_SSL(imap_server)
        # Fazer login na conta de e-mail
        mail.login(username, password)
        c.print(Panel('[green]Conexão IMAP estabelecida com sucesso![/]', style='#9400d3'))
        return mail
    except imaplib.IMAP4.error as e:
        c.print('Falha ao conectar ao servidor IMAP: {e}')
        logger.error(f'Servidor IMAP: {e}')
        return None
    
def add_marker_to_email(mail, email_id, marker):
    try:
        mail.select('inbox')
        mail.store(email_id, '+X-GM-LABELS', f'({marker})')
    except Exception as e:
        c.print('Não foi possível adicionar o marcador aos e-mails.')
        logger.error(f"Marcador email: {e}")

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

                # Decodificar o cabeçalho
                if filename:
                    try:
                        filename_info = decode_header(filename)
                        if isinstance(filename_info[0][0], bytes):
                            filename = filename_info[0][0].decode(filename_info[0][1] or 'utf-8')
                        elif isinstance(filename_info[0][0], str):
                            filename = filename_info[0][0]
                        else:
                            logger.warning(f"Filename Type: {type(filename_info[0][0])} / Valor: {filename_info[0][0]} / ID: {email_id}")
                            continue

                    except Exception as e:
                        logger.warning(f'Filename Decodificacao: {e} / ID: {email_id}')
                        continue

                # Verificar se o anexo é um arquivo XML
                if filename and filename.lower().endswith(".xml"):
                    xml_content = part.get_payload(decode=True).decode('utf-8')
                    process_xml = ProcessXml(content=xml_content)
                    item_id = process_xml.extract_item_id()
                    item_emissor = process_xml.extract_emissor_name()
                    item_ano = process_xml.extract_year_from_xml()
                    item_mes = process_xml.extract_mes()

                    emissor_path = os.path.join(download_folder, item_emissor)
                    ano_path = os.path.join(emissor_path, item_ano)
                    mes_path = os.path.join(ano_path, item_mes)

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
                            logger.info(f'XML Baixado: {item_id}')
                            count += 1
                        except Exception as e:
                            c.print(f'[magenta]{item_id}[/] - [red]Não foi possível baixar o XML[/]')
                            logger.error(f'{item_id}: {e}')
                    else: 
                        add_marker_to_email(mail_connection, email_id, label)
        
        c.print(f"\n[green]Finalizado com sucesso! {count} xml's baixados.[/]")

    
    except (socket.error, SSLEOFError) as e:
        c.print(f"[red]Não foi possível concluir o processo: {e}.[/]")
        logger.error(f'Socket: {e}')

    except Exception as e:
        c.print(f"[red]Não foi possível baixar o XML.[/]")
        logger.error(f'Download: {e, e.__cause__, e.__context__}')

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
                    if isinstance(filename_info[0][0], bytes):
                        filename = filename_info[0][0].decode(filename_info[0][1] or 'utf-8')
                    elif isinstance(filename_info[0][0], str):
                        filename = filename_info[0][0]
                    else:
                        logger.warning(f"Filename Type: {type(filename_info[0][0])} / Valor: {filename_info[0][0]} / ID: {email_id}")
                        continue

                except Exception as e:
                    logger.warning(f'Filename Decodificacao: {e} / ID: {email_id}')
                    continue

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
                            logger.info(f'XML Baixado: {item_id}')
                            count += 1
                        except Exception as e:
                            c.print(f'[magenta]{item_id}[/] - [red]Não foi possível baixar o XML[/]')
                            logger.error(f'{item_id}: {e}')
                    
                    else: 
                        add_marker_to_email(mail_connection, email_id, label)
                        
        c.print(f"\n[green]Finalizado com sucesso! {count} xml's baixados.[/]")

    except (socket.error, SSLEOFError) as e:
        c.print(f"[red]Não foi possível concluir o processo: {e}.[/]")
        logger.error(f'Socket: {e}')

    except Exception as e:
        c.print(f"[red]Não foi possível baixar o XML.[/]")
        logger.error(f'Download: {e, e.__cause__, e.__context__}')

