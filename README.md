<h3 align="center">
	<img src="https://imgur.com/d7GOhhR.png" width="200" alt="Logo"/><br/>
    <p style="font-size:xx-large;">Xml Organize</p>
</h3>

<p align="center" style="margin-top:5vh;">
	<a href="https://github.com/gustjose/organizador-xml/stargazers" style="padding:1%;"><img src="https://img.shields.io/github/stars/gustjose/organizador-xml?colorA=21232f&colorB=bd93f9&style=for-the-badge"></a>
	<a href="https://github.com/gustjose/organizador-xml/issues" style="padding:1%;"><img src="https://img.shields.io/github/issues/gustjose/organizador-xml?colorA=21232f&colorB=ffb86c&style=for-the-badge"></a>
	<a href="https://github.com/gustjose/organizador-xml/contributors" style="padding:1%;"><img src="https://img.shields.io/github/contributors/gustjose/organizador-xml?colorA=21232f&colorB=a6da95&style=for-the-badge"></a>
</p>

<p align="center" style="margin:5vh 0vh; display:flex; justify-content:space-evenly;">
	<img src="https://imgur.com/UaKWjcd.png" style="width:48%; height:auto;">
    <img src="https://imgur.com/KsVeX3s.png" style="width:48%; height:auto;">
</p>

<p style="padding:0vh 0vh 5vh 0vh; font-size:large;" align="center">
    Este script em Python foi desenvolvido para baixar e organizar <b>Notas Ficais Eletrônicas (NFe)</b> em formato XML armazenadas em e-mail e em pastas de maneira automatizada.
</p>

# Instalação

> [!IMPORTANT] 
> Certifique-se de ter o Python 3.7 ou superior instalado, bem como o Poetry. Para instalar o Poetry, consulte a [documentação oficial](https://python-poetry.org/docs/).

1. Clone o repositório:  
    ```bash
    git clone https://github.com/seu-usuario/xml-organize.git
    cd xml-organize
    ```

2. Instale as dependências:  
    ```bash
    poetry install
    ```

3. Ative o ambiente virtual gerenciado pelo Poetry (opcional):  
    ```bash
    poetry shell
    ```

4. Execute o script:  
    ```bash
    poetry run python main.py
    ```

# IMAP's suportados:
- Gmail.
- Outlook.

# Funcionalidades

- **Configurações:** Configure o script para o seu provedor de e-mail, pasta de download e outras opções.
- **Importar XML do E-mail:** Baixe e organize automaticamente os arquivos XML do seu e-mail.
- **Baixar XML do E-mail:** Baixe apenas os arquivos XML sem organizá-los.
- **Organizar XML em Pasta:** Organize manualmente os arquivos XML em uma pasta específica.
- **Gerar DANFE:** Permite a geração de DANFE's em PDF.

<p style="margin-top:8vh;" align="center">
	<b>Copyright &copy; 2025 - Gustavo Carreiro</b>
</p>

<p align="center">
	<a href=""><img src="https://img.shields.io/static/v1.svg?style=for-the-badge&label=License&message=MIT&logoColor=d9e0ee&colorA=21232f&colorB=bd93f9"/></a>
</p>
