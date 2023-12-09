import os
from shutil import move
from rich.progress import Progress
from src.process_xml import ProcessXml
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

c = Console()

def get_downloaded_ids(download_folder):
    # Obter IDs dos arquivos já baixados na pasta de download
    downloaded_ids = set()

    # Obter o total de arquivos para a barra de progresso
    total_files = sum(len(files) for _, _, files in os.walk(download_folder))

    # Criar uma barra de progresso com Rich
    with Progress() as progress:
        task = progress.add_task("[cyan]Scaneando pastas", total=total_files, completed=0, unit=" arquivo")

        # Percorrer pastas e subpastas usando os.walk()
        for root, dirs, files in os.walk(download_folder):
            for filename in files:
                if filename.lower().endswith(".xml"):
                    item_id = ProcessXml(os.path.join(root, filename)).extract_item_id()
                    if item_id:
                        downloaded_ids.add(item_id)

                # Atualizar a barra de progresso
                progress.update(task, advance=1)

    return downloaded_ids

def organize_xml(folder, folder_download, rename):
    downloaded_ids = get_downloaded_ids(folder_download)

    c.print('\n')
    c.rule('Baixando XML\n', style='#9400d3')
    c.print('\n')
    count = 0

    for pasta, subpastas, files in os.walk(folder):
        for filename in files:
            if filename.lower().endswith(".xml"):
                xml = ProcessXml(path=os.path.join(pasta, filename))
                xml_id = xml.extract_item_id()
                xml_emissor = xml.extract_emissor_name()
                xml_ano = xml.extract_year_from_xml()
                xml_mes = xml.extract_mes()

                path_emissor = folder_download + f'\\{xml_emissor}'
                path_ano = path_emissor + f'\\{xml_ano}'
                path_mes = path_ano + f'\\{xml_mes}'
            
            try:
                if xml_id not in downloaded_ids:
                    if not os.path.exists(os.path.join(folder_download, xml_emissor)):
                        os.makedirs(path_emissor)

                        if not os.path.exists(os.path.join(path_emissor, xml_ano)):
                            os.makedirs(path_ano)

                            if not os.path.exists(os.path.join(path_ano, xml_mes)):
                                os.makedirs(path_mes)
                    
                if os.path.exists(path_mes):
                    move(os.path.join(pasta, filename), path_mes)
                    if rename == 'True': os.rename(os.path.join(path_mes, filename), os.path.join(path_mes, f'{xml_id}.xml'))
                    c.print(f'[magenta]{xml_id}[/] - [green]Organizado[/]')
                    count += 1
            except Exception as e:
                c.print(f'[magenta]{xml_id}[/] - [red]Erro: {e}[/]')
    
    c.print(f"\n[green]Finalizado com sucesso! {count} xml's organizados.[/]")

