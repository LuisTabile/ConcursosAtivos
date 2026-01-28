"""
Módulo para Download e Parsing de PDFs (Editais de Concursos)
"""

import requests
import pdfplumber
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger
import re


class PDFParser:
    """Parser para extrair tabelas de editais em PDF"""
    
    def __init__(self, download_dir: str = "data/raw"):
        """
        Inicializa o parser
        
        Args:
            download_dir: Diretório para salvar PDFs baixados
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download_pdf(self, url: str, filename: Optional[str] = None) -> Optional[Path]:
        """
        Baixa um arquivo PDF
        
        Args:
            url: URL do PDF
            filename: Nome do arquivo (opcional, extraído da URL se não fornecido)
            
        Returns:
            Path do arquivo baixado ou None em caso de erro
        """
        try:
            logger.info(f"Baixando PDF: {url}")
            
            # Gerar nome do arquivo se não fornecido
            if not filename:
                filename = url.split('/')[-1]
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
            
            filepath = self.download_dir / filename
            
            # Baixar arquivo
            response = requests.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Salvar arquivo
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.success(f"PDF salvo: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erro ao baixar PDF {url}: {e}")
            return None
    
    def extract_text(self, pdf_path: Path) -> str:
        """
        Extrai todo o texto de um PDF
        
        Args:
            pdf_path: Caminho do arquivo PDF
            
        Returns:
            Texto extraído
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {e}")
            return ""
    
    def extract_tables(self, pdf_path: Path) -> List[pd.DataFrame]:
        """
        Extrai todas as tabelas de um PDF
        
        Args:
            pdf_path: Caminho do arquivo PDF
            
        Returns:
            Lista de DataFrames com as tabelas encontradas
        """
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_tables = page.extract_tables()
                    
                    for table in page_tables:
                        if table:
                            # Converter para DataFrame
                            df = pd.DataFrame(table[1:], columns=table[0])
                            df['_pagina'] = page_num
                            tables.append(df)
                            logger.debug(f"Tabela extraída da página {page_num}: {df.shape}")
            
            logger.info(f"Total de tabelas extraídas: {len(tables)}")
            
        except Exception as e:
            logger.error(f"Erro ao extrair tabelas do PDF: {e}")
        
        return tables
    
    def find_cargos_table(self, tables: List[pd.DataFrame]) -> Optional[pd.DataFrame]:
        """
        Identifica e consolida tabelas com informações de cargos
        (podem estar distribuídas em múltiplas páginas)
        
        Args:
            tables: Lista de DataFrames extraídos
            
        Returns:
            DataFrame consolidado da tabela de cargos ou None
        """
        # Palavras-chave para identificar a tabela de cargos
        keywords = ['cargo', 'escolaridade', 'requisito', 'salário', 'remuneração', 
                   'vencimento', 'vagas', 'chs', 'carga horária']
        
        # Encontrar todas as tabelas que parecem ser de cargos
        cargo_tables = []
        reference_shape = None
        
        for df in tables:
            if df.empty:
                continue
            
            # Verificar colunas
            columns_text = ' '.join([str(col).lower() for col in df.columns])
            
            # Verificar primeira linha (pode conter cabeçalhos)
            if len(df) > 0:
                first_row_text = ' '.join([str(val).lower() for val in df.iloc[0]])
            else:
                first_row_text = ""
            
            combined_text = columns_text + ' ' + first_row_text
            
            # Calcular score baseado em palavras-chave encontradas
            score = sum(1 for keyword in keywords if keyword in combined_text)
            
            # Se tem pelo menos 2 palavras-chave ou tem a mesma estrutura
            if score >= 2:
                if reference_shape is None:
                    reference_shape = df.shape[1]  # Número de colunas
                
                # Se tem o mesmo número de colunas, é continuação da tabela
                if df.shape[1] == reference_shape:
                    cargo_tables.append(df)
                    logger.debug(f"Tabela de cargos encontrada (página {df['_pagina'].iloc[0] if '_pagina' in df.columns else '?'}): {df.shape}")
        
        if not cargo_tables:
            logger.warning("Nenhuma tabela de cargos identificada")
            return None
        
        # Consolidar todas as tabelas
        if len(cargo_tables) == 1:
            consolidated = cargo_tables[0]
        else:
            # Concatenar mantendo as mesmas colunas
            logger.info(f"Consolidando {len(cargo_tables)} tabelas de cargos")
            consolidated = pd.concat(cargo_tables, ignore_index=True)
        
        logger.success(f"Tabela de cargos consolidada: {consolidated.shape}")
        return consolidated
    
    def parse_cargos(self, df: pd.DataFrame, cidade: str = "") -> List[Dict]:
        """
        Extrai informações de cargos de um DataFrame
        
        Args:
            df: DataFrame com tabela de cargos
            cidade: Nome da cidade do concurso
            
        Returns:
            Lista de dicionários com informações dos cargos
        """
        cargos = []
        
        if df is None or df.empty:
            return cargos
        
        logger.debug(f"DataFrame shape: {df.shape}")
        logger.debug(f"Colunas: {list(df.columns)}")
        
        # Tentar identificar colunas importantes
        col_mapping = {}
        
        # Verificar se a primeira linha contém dados válidos (não é cabeçalho)
        primeira_linha_tem_dados = False
        if len(df) > 0:
            primeira_celula = str(df.iloc[0, 0]).strip()
            # Se a primeira célula contém muito texto, provavelmente é um cargo
            if len(primeira_celula) > 10 and 'None' not in primeira_celula:
                primeira_linha_tem_dados = True
        
        # Mapear colunas por posição (padrão comum em editais)
        # Coluna 0: Cargo
        # Coluna 2: Requisitos/Escolaridade  
        # Coluna 3: Carga Horária
        # Coluna 4: Vagas
        # Coluna 7: Salário
        
        num_cols = len(df.columns)
        
        if num_cols >= 8:  # Formato com múltiplas colunas
            col_mapping = {
                'cargo': 0,
                'requisito': 2,
                'carga_horaria': 3,
                'vagas': 4,
                'salario': 7
            }
        elif num_cols >= 5:
            col_mapping = {
                'cargo': 0,
                'requisito': 1,
                'carga_horaria': 2,
                'vagas': 3,
                'salario': 4
            }
        else:
            # Tentar mapear por nome de coluna
            for idx, col in enumerate(df.columns):
                col_lower = str(col).lower()
                
                if 'cargo' in col_lower or 'função' in col_lower:
                    col_mapping['cargo'] = idx
                elif 'escolaridade' in col_lower or 'requisito' in col_lower:
                    col_mapping['requisito'] = idx
                elif 'salário' in col_lower or 'vencimento' in col_lower or 'remuneração' in col_lower or 'valor inicial' in col_lower:
                    col_mapping['salario'] = idx
                elif 'chs' in col_lower or 'carga' in col_lower:
                    col_mapping['carga_horaria'] = idx
                elif 'vagas' in col_lower:
                    col_mapping['vagas'] = idx
        
        logger.debug(f"Mapeamento de colunas: {col_mapping}")
        
        # Extrair dados linha por linha
        for idx, row in df.iterrows():
            cargo_info = {
                'cidade': cidade,
                'cargo': '',
                'requisito': '',
                'salario': '',
                'carga_horaria': '',
                'vagas': ''
            }
            
            # Preencher informações disponíveis usando índices
            try:
                if 'cargo' in col_mapping:
                    cargo_info['cargo'] = str(row.iloc[col_mapping['cargo']]).strip()
                
                if 'requisito' in col_mapping:
                    cargo_info['requisito'] = str(row.iloc[col_mapping['requisito']]).strip()
                
                if 'salario' in col_mapping:
                    cargo_info['salario'] = str(row.iloc[col_mapping['salario']]).strip()
                
                if 'carga_horaria' in col_mapping:
                    cargo_info['carga_horaria'] = str(row.iloc[col_mapping['carga_horaria']]).strip()
                
                if 'vagas' in col_mapping:
                    cargo_info['vagas'] = str(row.iloc[col_mapping['vagas']]).strip()
            except Exception as e:
                logger.warning(f"Erro ao processar linha {idx}: {e}")
                continue
            
            # Limpar valores None/nan
            for key in cargo_info:
                if cargo_info[key] in ['nan', 'None', 'null']:
                    cargo_info[key] = ''
            
            # Adicionar apenas se tiver cargo e salário preenchidos
            if (cargo_info['cargo'] and 
                len(cargo_info['cargo']) > 3 and
                cargo_info['salario'] and
                cargo_info['salario'] not in ['nan', 'None', '-']):
                cargos.append(cargo_info)
                logger.debug(f"Cargo adicionado: {cargo_info['cargo'][:50]}...")
        
        logger.info(f"Extraídos {len(cargos)} cargos")
        return cargos
    
    def process_edital(self, url: str, cidade: str = "", concurso_id: str = "") -> List[Dict]:
        """
        Processa um edital completo: download, extração e parsing
        
        Args:
            url: URL do PDF do edital
            cidade: Nome da cidade
            concurso_id: ID do concurso
            
        Returns:
            Lista de dicionários com informações dos cargos
        """
        # Gerar nome do arquivo
        filename = f"concurso_{concurso_id}.pdf" if concurso_id else None
        
        # 1. Download
        pdf_path = self.download_pdf(url, filename)
        if not pdf_path:
            return []
        
        # 2. Extrair tabelas
        tables = self.extract_tables(pdf_path)
        if not tables:
            logger.warning(f"Nenhuma tabela encontrada no PDF: {pdf_path}")
            return []
        
        # 3. Identificar tabela de cargos
        cargos_table = self.find_cargos_table(tables)
        if cargos_table is None:
            logger.warning(f"Tabela de cargos não identificada: {pdf_path}")
            return []
        
        # 4. Extrair informações dos cargos
        cargos = self.parse_cargos(cargos_table, cidade)
        
        return cargos


if __name__ == "__main__":
    # Configurar logging
    logger.add("logs/pdf_parser.log", rotation="10 MB")
    
    # Teste com URL de exemplo
    parser = PDFParser()
    
    # URL de exemplo do edital
    test_url = "https://anexos.cdn.selecao.net.br/uploads/361/concursos/2577/anexos/cf42044f-baf4-4a87-a9b7-36365be9bffc.pdf"
    
    cargos = parser.process_edital(test_url, cidade="Sossêgo/PB", concurso_id="2577")
    
    # Exibir resultados
    for cargo in cargos:
        print(f"\nCargo: {cargo['cargo']}")
        print(f"  Cidade: {cargo['cidade']}")
        print(f"  Requisito: {cargo['requisito'][:80]}...")
        print(f"  Salário: {cargo['salario']}")
        print(f"  Carga Horária: {cargo['carga_horaria']}")
