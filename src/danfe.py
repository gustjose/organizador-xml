import os
import logging
from rich.console import Console
from brazilfiscalreport.danfe import Danfe

c = Console()
logger = logging.getLogger()

def danfe_pdf(arquivo, destino):
    """
    Gera um PDF da DANFE a partir de um arquivo XML.

    Esta função lê o conteúdo de um arquivo XML, gera a representação da DANFE 
    usando o conteúdo lido e salva o PDF resultante em um diretório especificado. 
    O nome do PDF gerado será o mesmo do arquivo XML, com a extensão alterada para .pdf.

    Parâmetros:
    arquivo (str): O caminho para o arquivo XML que contém os dados da DANFE.
    destino (str): O diretório onde o PDF gerado será salvo.

    Retorna:
    bool: Retorna True se o PDF foi gerado com sucesso; False em caso de erro.

    Exceções:
    - ValueError: Lançada se o arquivo fornecido não for um arquivo XML.
    - Exception: Lançada para qualquer erro que ocorra durante o processo de geração do PDF.
    """

    try:
        # Verificar se o arquivo tem a extensão .xml
        if not arquivo.lower().endswith('.xml'):
            raise ValueError("O arquivo fornecido não é um arquivo XML.")

        # Abrir o arquivo XML com encoding UTF-8
        with open(arquivo, "r", encoding="utf8") as file:
            xml_content = file.read()

        # Gerar a DANFE a partir do conteúdo XML
        danfe = Danfe(xml=xml_content)

        # Extrair o nome base do arquivo (sem a extensão)
        nome_base = os.path.splitext(os.path.basename(arquivo))[0]

        # Especificar o destino do PDF com o mesmo nome do arquivo original
        pdf_destino = os.path.join(destino, f"{nome_base}.pdf")

        # Gerar o PDF e salvá-lo no destino
        danfe.output(pdf_destino)

        return True

    except Exception as e:
        logger.error(f'[DANFE]: {e}')
        return False

def diretorio_danfe_pdf(diretorio_origem, diretorio_destino):
    """
    Percorre o diretório fornecido para encontrar arquivos XML e gera PDFs 
    para cada um no diretório de destino, sem manter a estrutura de pastas.

    Esta função busca recursivamente por arquivos XML dentro do diretório 
    especificado e converte cada um deles em um PDF, salvando todos os PDFs 
    gerados no mesmo diretório de destino. Não mantém a estrutura de subpastas 
    do diretório de origem.

    Parâmetros:
    diretorio_origem (str): O caminho do diretório onde os arquivos XML estão localizados.
    diretorio_destino (str): O caminho do diretório onde os PDFs gerados serão salvos.

    Retorna:
    None: A função não retorna um valor, mas imprime mensagens de status sobre a 
    geração dos PDFs.

    Exceções:
    - Exception: Lançada para qualquer erro que ocorra durante a execução da função,
    como problemas de leitura de arquivos ou de criação de diretórios.
    """

    try:
        # Verificar se o diretório de destino existe, senão criar
        if not os.path.exists(diretorio_destino):
            os.makedirs(diretorio_destino)

        # Percorrer o diretório e subdiretórios
        for root, dirs, files in os.walk(diretorio_origem):
            for file in files:
                # Verificar se o arquivo é um XML
                if file.lower().endswith('.xml'):
                    # Caminho completo do arquivo XML
                    caminho_arquivo_xml = os.path.join(root, file)

                    # Gerar o PDF no diretório de destino
                    sucesso = danfe_pdf(caminho_arquivo_xml, diretorio_destino)

                    if sucesso:
                        c.print(f"PDF gerado para: {caminho_arquivo_xml}")
                    else:
                        c.print(f"Falha ao gerar PDF para: {caminho_arquivo_xml}")
                        
        return True

    except Exception as e:
        logger.error(f'[DANFE]: {e}')
        return False

