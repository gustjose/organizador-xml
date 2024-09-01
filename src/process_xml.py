from xml.etree import ElementTree as ET
import logging

logger = logging.getLogger()

class ProcessXml:
    def __init__(self, path=None, content=None) -> None:
        self.file_path = path
        if path is not None:
            self.xml_content = self.read_xml_file()
        else:
            self.xml_content = content
        pass

    def read_xml_file(self):
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            xml_content = ET.tostring(root, encoding='utf-8').decode('utf-8')
            return xml_content
        except ET.ParseError as e:
            logger.error(f'Processar XML - Arquivo: {self.file_path} / {e} ')
            return None
    
    def extract_emissor_name(self):
        root = ET.fromstring(self.xml_content)
        emissor = root.find('.//{http://www.portalfiscal.inf.br/nfe}emit/{http://www.portalfiscal.inf.br/nfe}xNome')
        if emissor is not None:
            return emissor.text.strip().replace('/', '').replace("\\", "")
    
    def extract_emissor_cnpj(self):
        root = ET.fromstring(self.xml_content)
        emissor = root.find('.//{http://www.portalfiscal.inf.br/nfe}emit/{http://www.portalfiscal.inf.br/nfe}CNPJ')
        if emissor is not None:
            return emissor.text.strip()
    
    def extract_year_from_xml(self):
        root = ET.fromstring(self.xml_content)
        dhEmi_tag = root.find('.//{http://www.portalfiscal.inf.br/nfe}dhEmi')
        dEmi_tag = root.find('.//{http://www.portalfiscal.inf.br/nfe}dEmi')
        if dhEmi_tag is not None:
            dhEmi_text = dhEmi_tag.text.strip()
            return dhEmi_text.split('-')[0]
        if dEmi_tag is not None:
            dEmi_text = dEmi_tag.text.strip()
            return dEmi_text.split('-')[0]
    
    def extract_mes(self):
        root = ET.fromstring(self.xml_content)
        dhEmi_tag = root.find('.//{http://www.portalfiscal.inf.br/nfe}dhEmi')
        dEmi_tag = root.find('.//{http://www.portalfiscal.inf.br/nfe}dEmi')

        month_name = {
            1: 'Janeiro',
            2: 'Fevereiro',
            3: 'Março',
            4: 'Abril',
            5: 'Maio',
            6: 'Junho',
            7: 'Julho',
            8: 'Agosto',
            9: 'Setembro',
            10: 'Outubro',
            11: 'Novembro',
            12: 'Dezembro'        
        }

        if dhEmi_tag is not None:
            dhEmi_text = dhEmi_tag.text.strip()
            mes = int(dhEmi_text.split('-')[1])
            return month_name[mes]
        if dEmi_tag is not None:
            dEmi_text = dEmi_tag.text.strip()
            mes = int(dEmi_text.split('-')[1])
            return month_name[mes]
    
    def extract_item_id(self):
        root = ET.fromstring(self.xml_content)
        item_element = root.find('.//{http://www.portalfiscal.inf.br/nfe}infNFe')
        if item_element is not None:
            id_value = item_element.get('Id')
            return id_value
        return None
    