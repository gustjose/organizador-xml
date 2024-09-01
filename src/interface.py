import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from dotenv import load_dotenv, set_key
from time import sleep
from datetime import datetime
from src import *  # Supondo que suas funções auxiliares estejam aqui
import logging

c = Console()
p = Prompt()

logger = logging.getLogger()

username = os.getenv('USER')
password = os.getenv('SENHA')
imap_server = os.getenv('IMAP_SERVER')
download_folder = os.getenv('FOLDER_DOWNLOAD')
rename = os.getenv('RENAME')
label = os.getenv('LABEL')

def exibir_menu():
    
    os.system('cls' if os.name == 'nt' else 'clear')
    c.rule('Menu', style='#9400d3')
    c.print(Panel('[[green]1[/]] - [white]Configurações[/]', style='#50fa7b'))
    c.print(Panel('[[green]2[/]] - [white]Importar XML do e-mail[/]', style='#50fa7b'))
    c.print(Panel('[[green]3[/]] - [white]Baixar XML do e-mail[/]', style='#50fa7b'))
    c.print(Panel('[[green]4[/]] - [white]Organizar XML em pasta[/]', style='#50fa7b'))
    c.print(Panel('[[green]5[/]] - [white]Agendar Importação do e-mail[/]', style='#50fa7b'))

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
        agendar_importacao()

def configurar_sistema():
    global rename
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        c.print(Panel(f"Pasta Receptora de XML: {download_folder}\nProvedor:\n server: {imap_server}\n user: {username}\n senha: {password[0:3] + (len(password) - 3) *'*'}\nRenomear arquivos XML: {rename}", style='#50fa7b'))
        c.print(Panel('[[green]1[/]] - [white]Alterar pasta receptora[/]', style='#50fa7b'))
        c.print(Panel('[[green]2[/]] - [white]Alterar Provedor[/]', style='#50fa7b'))
        c.print(Panel('[[green]3[/]] - [white]Alterar Email[/]', style='#50fa7b'))
        c.print(Panel('[[green]4[/]] - [white]Alterar Senha[/]', style='#50fa7b'))
        c.print(Panel('[[green]5[/]] - [white]Ativar/Desativar renomear XML[/]', style='#50fa7b'))
        c.print(Panel('[[green]6[/]] - [white]Finalizar[/]', style='#50fa7b'))

        suboption = str(p.ask("Escolha uma das opções:", choices=["1", "2", "3", "4", "5", "6"]))

        if suboption == "1":
            try: 
                set_key('.env', 'FOLDER_DOWNLOAD', c.input('Qual o endereço da pasta que receberá os XML: '))
                c.print('[green]Configuração salva com sucesso![/]')
                sleep(3)
            except Exception as e:
                c.print(f'[red]Erro: {e}[/]')
                logger.error(f'Interface: {e}')
                sleep(3)
        elif suboption == "2":
            try: 
                set_key('.env', 'IMAP_SERVER', c.input('Alterar provedor: '))
                c.print('[green]Configuração salva com sucesso![/]')
                sleep(3)
            except Exception as e:
                c.print(f'[red]Erro: {e}[/]')
                logger.error(f'Interface: {e}')
                sleep(3)
        elif suboption == "3":
            try: 
                set_key('.env', 'USER', c.input('Alterar email: '))
                c.print('[green]Configuração salva com sucesso![/]')
                sleep(3)
            except Exception as e:
                c.print(f'[red]Erro: {e}[/]')
                logger.error(f'Interface: {e}')
                sleep(3)
        elif suboption == "4":
            try: 
                set_key('.env', 'SENHA', c.input('Alterar senha: '))
                c.print('[green]Configuração salva com sucesso![/]')
                sleep(3)
            except Exception as e:
                c.print(f'[red]Erro: {e}[/]')
                logger.error(f'Interface: {e}')
                sleep(3)
        elif suboption == "5":
            try: 
                rename = p.ask("\nDeseja que os arquivos sejam renomeados automaticamente após processados: ", choices=["S", "N"], default="S")
                if rename == "S": set_key('.env', 'RENAME', 'True')
                if rename == "N": set_key('.env', 'RENAME', 'False')
                c.print('[green]Configuração salva com sucesso![/]')
                sleep(3)
            except Exception as e:
                c.print(f'[red]Erro: {e}[/]')
                logger.error(f'Interface: {e}')
                sleep(3)
        elif suboption == "6": break

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

def agendar_importacao():
    os.system('cls' if os.name == 'nt' else 'clear')
    c.rule('Configurar Agendamento de Importação', style='#9400d3')

    if get_scheduled_task_info():
        c.print(Panel('[[green]1[/]] - [white]Excluir agendamento[/]', style='#50fa7b'))
        if p.ask("Escolha uma das opções:", choices=["1"]):
            if delete_scheduled_task():
                c.print('[green]\nTarefa excluída com sucesso![/]')
                input('Digite enter para continuar ')
            else:
                c.print('[red]\nErro na execução![/]')
                input('Digite enter para continuar ')
    else:
        c.print(Panel('[green]1[/]] - [white]Criar agendamento[/]', style='#50fa7b'))
        if p.ask("Escolha uma das opções:", choices=["1"]):
            c.rule('Definindo', style='#9400d3')
            # Obter a data atual
            data_atual = datetime.now()
            # Formatar a data como "AAAA-MM-DD"
            data_formatada = data_atual.strftime("%Y-%m-%d")
            while True:
                try:
                    hora_usuario = p.ask("Digite a hora de execução no formato HH:MM (24h)")
                    datetime.strptime(hora_usuario, "%H:%M")
                    break
                except ValueError:
                    print("Formato de hora inválido. Use o formato HH:MM (24h).")
            data_hora_concatenada = f"{data_formatada}T{hora_usuario}:00"

            c.print("\nQual a frequência?")
            c.print('[green]1[/]] - [white]Diariamente[/]')
            c.print('[green]2[/]] - [white]Semanalmente[/]')
            c.print('[green]3[/]] - [white]Mensalmente[/]')
            c.print('[green]4[/]] - [white]A cada logon[/]')

            freq = {1 : 'daily', 2 : 'weekly', 3 : 'monthly', 4 : 'onlogon'}
            frequencia = freq[int(p.ask("Qual a frequência: ", choices=["1", "2", "3", "4"]))]
            if add_scheduled_task(start_time=data_hora_concatenada, frequency=frequencia):
                c.print('[green]\nTarefa agendada com sucesso![/]')
                input('Digite enter para continuar ')
            else:
                c.print('[red]\nErro na execução![/]')
                input('Digite enter para continuar ')