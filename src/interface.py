import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from time import sleep
from datetime import datetime
from src.imap_email import login_imap, scan_and_download_xml_attachments, download_xml_attachments
from src.process_path import organize_xml
from src.danfe import danfe_pdf, diretorio_danfe_pdf
import logging
import json

c = Console()
p = Prompt()

# Logger
logger = logging.getLogger()

# ACESSANDO DADOS DO USUARIO
db = 'data.json'
if not os.path.exists(db) or os.path.getsize(db) == 0:
    try:
        c.rule('Configurando', style='#9400d3')
        download_folder = c.input('Qual o endereço da pasta que receberá os XML: ')

        c.print("\nQual o seu provedor de e-mail?", justify='center')
        c.print('[[green]1[/]] - [white]Gmail[/]')
        c.print('[[green]2[/]] - [white]Outlook[/]')
        provedor = p.ask("Escolha uma das opções:", choices=["1", "2"], default="1")

        if provedor == "1": imap_server = "imap.gmail.com"
        if provedor == "2": imap_server = "outlook.office365.com"

        username = c.input('\nEmail: ')
        password = c.input('Senha: ')

        rename = p.ask("\nDeseja que os arquivos sejam renomeados automaticamente após processados: ", choices=["S", "N"], default="S")

        if rename == "S": rename = True
        else: rename = False

        label = c.input('Nome do marcador que será adicionado ao email após baixar o xml: ')

        initial_data = {
            "USER": username,
            "SENHA": password,
            "IMAP_SERVER": imap_server,
            "FOLDER_DOWNLOAD": download_folder,
            "RENAME": rename, 
            "LABEL": label
        }
        with open(db, 'w') as file:
            json.dump(initial_data, file, indent=4)
        
        c.print('[green]Configuração salva com sucesso![/]')
        sleep(3)
        
    except Exception as e:
        c.print(f'[red]Erro: {e}[/]')
        logger.error(f'Database: {e}')

else:
    with open(db, 'r') as file:
        data = json.load(file)
    
    username = data['USER']
    password = data['SENHA']
    imap_server = data['IMAP_SERVER']
    download_folder = data['FOLDER_DOWNLOAD']
    rename = data['RENAME']
    label = data['LABEL']

def exibir_menu():
    
    os.system('cls' if os.name == 'nt' else 'clear')
    c.rule('Menu', style='#9400d3')
    c.print(Panel('[[green]1[/]] - [white]Configurações[/]', style='#50fa7b'))
    c.print(Panel('[[green]2[/]] - [white]Importar XML do e-mail[/]', style='#50fa7b'))
    c.print(Panel('[[green]3[/]] - [white]Baixar XML do e-mail[/]', style='#50fa7b'))
    c.print(Panel('[[green]4[/]] - [white]Organizar XML em pasta[/]', style='#50fa7b'))
    c.print(Panel('[[green]5[/]] - [white]Gerar DANFE do XML[/]', style='#50fa7b'))

    option = str(p.ask("Escolha uma das opções:", choices=["1", "2", "3", "4", "5"]))

    if option == "1":
        configurar_sistema()
    elif option == "2":
        importar_xml(username, password, imap_server, download_folder, rename, label)
    elif option == "3":
        baixar_xml(username, password, imap_server, download_folder, rename, label)
    elif option == "4":
        organizar_xml_interface(download_folder, rename)
    elif option == "5":
        gerar_danfe()
        

def configurar_sistema():
    global username, password, imap_server, download_folder, rename, label
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        c.print(Panel(f"Pasta Receptora de XML: {download_folder}\nProvedor:\n server: {imap_server}\n user: {username}\n senha: {password[0:3] + (len(password) - 3) *'*'}\nRenomear arquivos XML: {rename}", style='#50fa7b'))
        c.print(Panel('[[green]1[/]] - [white]Alterar pasta receptora[/]', style='#50fa7b'))
        c.print(Panel('[[green]2[/]] - [white]Alterar Provedor[/]', style='#50fa7b'))
        c.print(Panel('[[green]3[/]] - [white]Alterar Email[/]', style='#50fa7b'))
        c.print(Panel('[[green]4[/]] - [white]Alterar Senha[/]', style='#50fa7b'))
        c.print(Panel('[[green]5[/]] - [white]Ativar/Desativar renomear XML[/]', style='#50fa7b'))
        c.print(Panel('[[green]6[/]] - [white]Salvar alterações[/]', style='#50fa7b'))

        suboption = str(p.ask("Escolha uma das opções:", choices=["1", "2", "3", "4", "5", "6"]))

        if suboption == "1":
            try:
                download_folder = c.input('Qual o endereço da pasta que receberá os XML: ')
                data['FOLDER_DOWNLOAD'] = download_folder
            except Exception as e:
                c.print(f'[red]Erro: {e}[/]')
                logger.error(f'Interface: {e}')
                sleep(3)
        elif suboption == "2":
            try:
                imap_server = c.input('Alterar provedor: ')
                data['IMAP_SERVER'] = imap_server
            except Exception as e:
                c.print(f'[red]Erro: {e}[/]')
                logger.error(f'Interface: {e}')
                sleep(3)
        elif suboption == "3":
            try:
                username = c.input('Alterar email: ')
                data['USER'] = username
            except Exception as e:
                c.print(f'[red]Erro: {e}[/]')
                logger.error(f'Interface: {e}')
                sleep(3)
        elif suboption == "4":
            try:
                password = c.input('Alterar senha: ')
                data['SENHA'] = password
            except Exception as e:
                c.print(f'[red]Erro: {e}[/]')
                logger.error(f'Interface: {e}')
                sleep(3)
        elif suboption == "5":
            try:
                rename = p.ask("\nDeseja que os arquivos sejam renomeados automaticamente após processados: ", choices=["S", "N"], default="S") == "S"
                data['RENAME'] = rename
            except Exception as e:
                c.print(f'[red]Erro: {e}[/]')
                logger.error(f'Interface: {e}')
                sleep(3)
        elif suboption == "6":
            try:
                with open(db, 'w') as file:
                    json.dump(data, file, indent=4)
                
                c.print('[green]Configuração salva com sucesso![/]')
                input('Digite enter para continuar ')
                exibir_menu()
            except Exception as e:
                c.print(f'[red]Erro ao salvar as configurações: {e}[/]')
                logger.error(f'Salvamento: {e}')
            break

def importar_xml(username, password, imap_server, download_folder, rename, label):
    os.system('cls' if os.name == 'nt' else 'clear')
    mail = login_imap(username, password, imap_server)
    if mail:
        scan_and_download_xml_attachments(download_folder, mail, label, rename)
        input('Digite enter para continuar ')

def baixar_xml(username, password, imap_server, download_folder, rename, label):
    os.system('cls' if os.name == 'nt' else 'clear')
    mail = login_imap(username, password, imap_server)
    if mail:
        download_xml_attachments(download_folder, mail, rename, label)
        input('Digite enter para continuar ')

def organizar_xml_interface(download_folder, rename):
    pasta_final = input('Em qual pasta estão os arquivos: ')
    os.system('cls' if os.name == 'nt' else 'clear')
    organize_xml(pasta_final, download_folder, rename)
    input('Digite enter para continuar ')

def gerar_danfe():
    os.system('cls' if os.name == 'nt' else 'clear')
    c.rule('Gerar DANFE', style='#9400d3')
    c.print(Panel('[[green]1[/]] - [white]XML único[/]\n[[green]2[/]] - [white]Todos os arquivos de uma pasta[/]', style='#50fa7b'))
    option = p.ask("Escolha uma das opções:", choices=["1", "2"])

    if option == "1":
        arquivo = c.input('Caminho do arquivo: ')
        destino = c.input('Pasta de Destino: ')
        if danfe_pdf(arquivo, destino):
            c.print('\n[green]DANFE gerado com sucesso![/]')
            input('Digite enter para continuar ')
            exibir_menu()
        else:
            c.print('\n[red]Erro! Não foi possível gerar o PDF.[/]')
            input('Digite enter para continuar ')
    elif option == "2":
        arquivo = c.input("Pasta com os XML's: ")
        destino = c.input('Pasta de Destino: ')
        if diretorio_danfe_pdf(arquivo, destino):
            c.print("\n[green]DANFE's gerados com sucesso![/]")
            input('Digite enter para continuar ')
            exibir_menu()
        else:
            c.print("\n[red]Erro! Não foi possível gerar os PDF's.[/]")
            input('Digite enter para continuar ')         