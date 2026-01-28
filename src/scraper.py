"""
Módulo de Web Scraping para Concursos Objetivas
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from loguru import logger
import time
from tqdm import tqdm


class ConcursoScraper:
    """Scraper para extrair informações de concursos do site Objetiva"""
    
    BASE_URL = "https://concursos.objetivas.com.br"
    ABERTOS_URL = f"{BASE_URL}/index/abertos/"
    
    def __init__(self, delay: float = 1.0):
        """
        Inicializa o scraper
        
        Args:
            delay: Tempo de espera entre requisições (em segundos)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def _sleep(self):
        """Aguarda o delay configurado entre requisições"""
        time.sleep(self.delay)
    
    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Faz requisição HTTP e retorna o conteúdo parseado
        
        Args:
            url: URL da página
            
        Returns:
            BeautifulSoup object ou None em caso de erro
        """
        try:
            logger.info(f"Acessando: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except requests.RequestException as e:
            logger.error(f"Erro ao acessar {url}: {e}")
            return None
    
    def get_concursos_abertos(self) -> List[Dict[str, str]]:
        """
        Extrai lista de concursos abertos
        
        Returns:
            Lista de dicionários com informações dos concursos
            Formato: [{'nome': str, 'url': str, 'id': str}, ...]
        """
        soup = self._get_page(self.ABERTOS_URL)
        if not soup:
            return []
        
        concursos = []
        concursos_ids = set()  # Para evitar duplicatas
        
        # Procura por links de concursos na página
        links = soup.find_all('a', href=lambda x: x and '/informacoes/' in x)
        
        for link in links:
            href = link.get('href')
            if href:
                # Construir URL completo se for relativo
                if not href.startswith('http'):
                    href = self.BASE_URL + href
                
                # Extrair ID do concurso da URL
                concurso_id = href.rstrip('/').split('/')[-1]
                
                # Evitar duplicatas
                if concurso_id in concursos_ids:
                    continue
                
                # Nome do concurso (texto do link ou título)
                nome = link.get_text(strip=True) or link.get('title', '')
                
                # Filtrar botões genéricos ("Inscrições Abertas", "Mais Informações", etc.)
                if nome.lower() in ['inscrições abertas!', 'mais informações', 'inscreva-se', '']:
                    continue
                
                concursos_ids.add(concurso_id)
                concursos.append({
                    'id': concurso_id,
                    'nome': nome,
                    'url': href
                })
        
        logger.info(f"Encontrados {len(concursos)} concursos abertos")
        return concursos
    
    def get_edital_links(self, concurso_url: str) -> List[Dict[str, str]]:
        """
        Extrai links dos editais de um concurso específico
        
        Args:
            concurso_url: URL da página de informações do concurso
            
        Returns:
            Lista de dicionários com informações dos editais
            Formato: [{'titulo': str, 'url': str, 'tipo': str}, ...]
        """
        self._sleep()
        soup = self._get_page(concurso_url)
        if not soup:
            return []
        
        editais = []
        
        # Procura por links de PDFs (editais)
        # Prioriza "Edital de Abertura das Inscrições"
        pdf_links = soup.find_all('a', href=lambda x: x and x.endswith('.pdf'))
        
        for link in pdf_links:
            href = link.get('href')
            titulo = link.get_text(strip=True)
            
            # Classificar tipo de edital
            tipo = 'outro'
            if 'abertura' in titulo.lower() and 'inscri' in titulo.lower():
                tipo = 'abertura_inscricoes'
            elif 'edital' in titulo.lower():
                tipo = 'edital'
            
            editais.append({
                'titulo': titulo,
                'url': href,
                'tipo': tipo
            })
        
        logger.info(f"Encontrados {len(editais)} editais")
        return editais
    
    def scrape_all(self) -> List[Dict]:
        """
        Executa scraping completo de todos os concursos abertos
        
        Returns:
            Lista de dicionários com informações completas
        """
        results = []
        
        # 1. Buscar concursos abertos
        concursos = self.get_concursos_abertos()
        
        if not concursos:
            logger.warning("Nenhum concurso aberto encontrado")
            return results
        
        # 2. Para cada concurso, buscar editais
        for concurso in tqdm(concursos, desc="Processando concursos"):
            logger.info(f"Processando: {concurso['nome']}")
            
            editais = self.get_edital_links(concurso['url'])
            
            # Priorizar edital de abertura de inscrições
            edital_principal = None
            for edital in editais:
                if edital['tipo'] == 'abertura_inscricoes':
                    edital_principal = edital
                    break
            
            # Se não encontrar, pegar o primeiro edital
            if not edital_principal and editais:
                edital_principal = editais[0]
            
            results.append({
                'concurso': concurso,
                'editais': editais,
                'edital_principal': edital_principal
            })
        
        logger.success(f"Scraping concluído: {len(results)} concursos processados")
        return results


if __name__ == "__main__":
    # Configurar logging
    logger.add("logs/scraper.log", rotation="10 MB")
    
    # Executar scraper
    scraper = ConcursoScraper()
    resultados = scraper.scrape_all()
    
    # Exibir resumo
    for resultado in resultados:
        print(f"\n{resultado['concurso']['nome']}")
        print(f"  URL: {resultado['concurso']['url']}")
        if resultado['edital_principal']:
            print(f"  Edital: {resultado['edital_principal']['titulo']}")
            print(f"  PDF: {resultado['edital_principal']['url']}")
