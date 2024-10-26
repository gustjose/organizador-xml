import imaplib, email, os
from email.header import decode_header
from src.process_xml import ProcessXml
from src.process_path import get_downloaded_ids
from src.notification import notification
from rich.console import Console
from rich.panel import Panel
import logging
import socket
from ssl import SSLEOFError

c = Console()

logger = logging.getLogger()

def login_imap(username, password, imap_server):
    """
    Conecta ao servidor IMAP e autentica o usuário.

    Parâmetros:
    - username (str): Nome de usuário da conta de e-mail.
    - password (str): Senha da conta de e-mail.
    - imap_server (str): Endereço do servidor IMAP.

    Retorna:
    - obj: Objeto de conexão IMAP se a autenticação for bem-sucedida.
    - None: Se ocorrer uma falha de autenticação ou conexão.

    Exceções:
    - imaplib.IMAP4.error: Falha de autenticação ou conexão ao servidor IMAP.
    - Exception: Qualquer erro geral ocorrido durante a tentativa de login.
    """
    try:
        # Conectar ao servidor IMAP
        mail = imaplib.IMAP4_SSL(imap_server)
        # Fazer login na conta de e-mail
        mail.login(username, password)
        c.print(Panel('[green]Conexão IMAP estabelecida com sucesso![/]', style='#9400d3'))
        return mail
    except imaplib.IMAP4.error as e:
        c.print(f'[red]Falha ao conectar ao servidor IMAP: {e}')
        logger.error(f'Servidor IMAP: {e}')
        input('Digite enter para continuar ')
        return None
    except Exception as e:
        c.print(F'[red]Falha ao conectar ao servidor IMAP: {e}')
        logger.error(f'Servidor IMAP: {e}')
        input('Digite enter para continuar ')
        return None
    
def add_marker_to_email(mail, email_id, marker):
    """
    Adiciona um marcador a um e-mail específico no servidor IMAP.

    Parâmetros:
    - mail (obj): Objeto de conexão IMAP autenticado.
    - email_id (str): ID do e-mail ao qual o marcador será adicionado.
    - marker (str): Nome do marcador a ser adicionado.

    Exceções:
    - Exception: Falha ao adicionar o marcador ao e-mail.
    """
    try:
        mail.select('inbox')
        mail.store(email_id, '+X-GM-LABELS', f'({marker})')
    except Exception as e:
        c.print('Não foi possível adicionar o marcador aos e-mails.')
        logger.error(f"Marcador email: {e}")

def scan_and_download_xml_attachments(download_folder, mail_connection, label, rename):
    """
    Busca e baixa anexos XML de e-mails, organizando-os em uma estrutura de diretórios baseada 
    em remetente, ano e mês extraídos do conteúdo XML.

    Parâmetros:
    - download_folder (str): Diretório raiz para salvar os arquivos XML baixados.
    - mail_connection (obj): Objeto de conexão IMAP autenticado.
    - label (str): Marcador a ser adicionado aos e-mails processados.
    - rename (bool): Indica se o arquivo XML deve ser renomeado usando o ID do item extraído.

    Exceções:
    - socket.error, SSLEOFError: Erros de rede que interrompem o processo de download.
    - Exception: Erro geral durante o download ou gravação dos arquivos XML.
    """
    try: 
        mail_connection.select('inbox')

        # Obter IDs dos e-mails com anexos
        resposta, IdEmails = mail_connection.search(None, 'All')
        ids_emails = IdEmails[0].split()

        # Obter IDs dos arquivos já baixados
        downloaded_ids = get_downloaded_ids(download_folder)

        c.print('\n')
        c.rule('\nBaixando XML', style='#9400d3')
        c.print(f"Emails na caixa de entrada: {len(ids_emails)}\n", justify='center')
        count = 0

        with c.status(f"(0/{len(ids_emails)}) Carregando... ", spinner="dots") as status:

            count_emails = 0

            # Verificar se a pasta de download existe
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)

            # Loop de Emails
            for email_id in ids_emails:
                resultado, dados = mail_connection.fetch(email_id, '(RFC822)')
                text_email = dados[0][1]

                count_emails += 1
                status.update(f"({count_emails}/{len(ids_emails)}) Carregando... ")

                # Decodificar Dados
                text_email = email.message_from_bytes(text_email)

                for part in text_email.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    filename = part.get_filename()

                    # Verificar se o anexo é um arquivo XML
                    if filename and filename.lower().endswith(".xml"):
                        xml_content = part.get_payload(decode=True).decode('utf-8')
                        process_xml = ProcessXml(content=xml_content)
                        item_id = process_xml.extract_item_id()

                        # Verificar se o ID já foi baixado
                        if item_id not in downloaded_ids:

                            item_emissor = process_xml.extract_emissor_name()
                            item_ano = process_xml.extract_year_from_xml()
                            item_mes = process_xml.extract_mes()

                            emissor_path = os.path.join(download_folder, item_emissor)
                            ano_path = os.path.join(emissor_path, item_ano)
                            mes_path = os.path.join(ano_path, item_mes)

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
                
            status.stop()
            c.print(f"\n[green]Finalizado com sucesso! {count} xml's baixados.[/]")
            notification("Processo Finalizado", f"{count} xml's baixados.")

    
    except (socket.error, SSLEOFError) as e:
        c.print(f"[red]Não foi possível concluir o processo: {e}.[/]")
        notification("Error", "Não foi possível concluir o processo")
        logger.error(f'Socket: {e}')

    except Exception as e:
        c.print(f"[red]Não foi possível baixar o XML.[/]")
        notification("Error", "Não foi possível concluir o processo")
        logger.error(f'Download: {e, e.__cause__, e.__context__}')

def download_xml_attachments(download_folder, mail_connection, rename, label):
    """
    Baixa anexos XML de e-mails, salvando-os em um diretório especificado.

    Parâmetros:
    - download_folder (str): Diretório onde os arquivos XML baixados serão salvos.
    - mail_connection (obj): Objeto de conexão IMAP autenticado.
    - rename (bool): Indica se o arquivo XML deve ser renomeado usando o ID do item extraído.
    - label (str): Marcador a ser adicionado aos e-mails processados.

    Exceções:
    - socket.error, SSLEOFError: Erros de rede que interrompem o processo de download.
    - Exception: Erro geral durante o download ou gravação dos arquivos XML.
    """
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
        count = 0  # Contador de arquivos XML baixados

        # Verificar se a pasta de download existe
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        # Iniciar o status dinâmico do Rich com contador
        with c.status(f"(0/{len(email_ids)}) Carregando... ", spinner="dots") as status:

            count_emails = 0  # Contador de e-mails processados

            # Loop sobre os e-mails
            for email_id in email_ids:
                if mail_connection.noop()[0] != 'OK':
                    raise Exception("Conexão com o servidor de e-mails perdida")
                
                _, msg_data = mail_connection.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                count_emails += 1  # Atualizar contador de e-mails
                status.update(f"({count_emails}/{len(email_ids)}) Carregando... ")

                # Percorrer partes do e-mail
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue

                    filename = part.get_filename()

                    # Verificar se o anexo é um arquivo XML
                    if filename and filename.lower().endswith(".xml"):
                        xml_content = part.get_payload(decode=True).decode('utf-8')
                        process_xml = ProcessXml(content=xml_content)
                        item_id = process_xml.extract_item_id()

                        # Verificar se o ID já foi baixado
                        if item_id not in downloaded_ids:

                            # Renomear arquivo se solicitado
                            if rename == 'True': 
                                filename = f'{item_id}.xml'

                            # Criar caminho para o arquivo de destino
                            dest_path = os.path.join(download_folder, filename)

                            add_marker_to_email(mail_connection, email_id, label)

                            # Salvar o conteúdo XML no arquivo
                            try:
                                with open(dest_path, 'w', encoding='utf-8') as xml_file:
                                    xml_file.write(xml_content)
                                c.print(f'[magenta]{item_id}[/] - [green]Baixado[/]')
                                logger.info(f'XML Baixado: {item_id}')
                                count += 1
                                
                                # Atualizar o status com o contador de XML baixados
                                status.update(f"({count_emails}/{len(email_ids)}) Carregando... {count} XMLs baixados")

                            except Exception as e:
                                c.print(f'[magenta]{item_id}[/] - [red]Não foi possível baixar o XML[/]')
                                logger.error(f'{item_id}: {e}')
                        
                        else:
                            add_marker_to_email(mail_connection, email_id, label)

            # Parar o status ao fim do processo
            status.stop()

            # Exibir mensagem de sucesso final
            c.print(f"\n[green]Finalizado com sucesso! {count} XML's baixados.[/]")
            notification("Processo Finalizado", f"{count} XML's baixados.")

    except (socket.error, SSLEOFError) as e:
        c.print(f"[red]Não foi possível concluir o processo: {e}.[/]")
        notification("Error", "Não foi possível concluir o processo")
        logger.error(f'Socket: {e}')

    except Exception as e:
        c.print(f"[red]Não foi possível baixar o XML.[/]")
        notification("Error", "Não foi possível concluir o processo")
        logger.error(f'Download: {e, e.__cause__, e.__context__}')