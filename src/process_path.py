import os
from shutil import move
from rich.progress import Progress
from src.process_xml import ProcessXml
from rich.console import Console
import logging

logger = logging.getLogger()

c = Console()

def get_downloaded_ids(download_folder):
    """
    Obtém os IDs de arquivos XML já baixados para evitar duplicação.

    A função percorre o diretório especificado, identifica arquivos com extensão `.xml` e extrai seus IDs. 
    Esses IDs são adicionados a um conjunto, que é então retornado para uso posterior.

    Parâmetros:
    - download_folder (str): Diretório raiz onde os arquivos XML baixados estão armazenados.

    Retorna:
    - set: Conjunto de IDs extraídos dos arquivos XML encontrados no diretório.

    Comportamento:
    - A função exibe uma barra de progresso para indicar o progresso da verificação.
    - Utiliza `ProcessXml` para extrair o ID de cada arquivo XML, que é então adicionado ao conjunto `downloaded_ids`.

    Exemplo de Uso:
    downloaded_ids = get_downloaded_ids("/caminho/para/download")
    """

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
    """
    Organiza arquivos XML em subdiretórios com base em informações extraídas de seu conteúdo.

    Esta função busca arquivos XML em uma pasta específica, extrai dados de cada arquivo (como emissor, ano e mês), 
    e os organiza em uma estrutura de subdiretórios. Se o ID do arquivo já existir na pasta de download, ele não é movido novamente.

    Parâmetros:
    - folder (str): Diretório de origem contendo arquivos XML para organizar.
    - folder_download (str): Diretório de destino onde os arquivos XML organizados serão salvos.
    - rename (bool): Indicador para renomear o arquivo XML baseado no ID extraído.

    Comportamento:
    - Utiliza a função `get_downloaded_ids` para obter os IDs de arquivos já baixados.
    - Cria subdiretórios conforme necessário, com base nas informações de emissor, ano e mês.
    - Exibe no console mensagens de status para cada arquivo (organizado, já baixado ou erro).

    Exemplo de Uso:
    organize_xml("/caminho/origem", "/caminho/download", rename=True)
    """
    
    downloaded_ids = get_downloaded_ids(folder_download)

    c.print('\n')
    c.rule('Organizando XML\n', style='#9400d3')
    c.print('\n')
    count = 0

    for pasta, subpastas, files in os.walk(folder):
        for filename in files:
            if filename.lower().endswith(".xml"):
                try:
                    xml = ProcessXml(path=os.path.join(pasta, filename))
                    xml_id = xml.extract_item_id()
                    xml_emissor = xml.extract_emissor_name()
                    xml_ano = xml.extract_year_from_xml()
                    xml_mes = xml.extract_mes()

                    path_emissor = os.path.join(folder_download, xml_emissor)
                    path_ano = os.path.join(path_emissor, xml_ano)
                    path_mes = os.path.join(path_ano, xml_mes)

                    # Criar caminho para o arquivo de destino
                    dest_path = os.path.join(path_mes, f'{xml_id}.xml')

                    # Verificar se o ID já foi baixado
                    if xml_id not in downloaded_ids:
                        # Criar diretórios se não existirem
                        os.makedirs(path_mes, exist_ok=True)

                        # Mover o arquivo para o destino
                        move(os.path.join(pasta, filename), dest_path)

                        c.print(f'[magenta]{xml_id}[/] - [green]Organizado[/]')
                        count += 1
                    else:
                        c.print(f'[magenta]{xml_id}[/] - [yellow]Já baixado[/]')
                except Exception as e:
                    c.print(f'[magenta]{filename}[/] - [red]Erro: {e}[/]')
                    logger.error(f'{xml_id}: {e}')

    c.print(f"\n[green]Finalizado com sucesso! {count} xml's organizados.[/]")

