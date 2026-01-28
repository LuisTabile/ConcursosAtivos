"""
Funções utilitárias
"""

import re
from typing import Optional, Tuple
from loguru import logger


def extract_cidade_estado(text: str) -> Tuple[str, str]:
    """
    Extrai cidade e estado de um texto
    
    Args:
        text: Texto contendo cidade/estado (ex: "Sossêgo/PB")
        
    Returns:
        Tupla (cidade, estado)
    """
    # Padrão: Cidade/UF
    match = re.search(r'([A-Za-zÀ-ÿ\s]+)/([A-Z]{2})', text)
    if match:
        cidade = match.group(1).strip()
        estado = match.group(2).strip()
        return cidade, estado
    
    # Padrão: MUNICÍPIO DE Cidade/UF
    match = re.search(r'MUNICÍPIO DE\s+([A-Za-zÀ-ÿ\s]+)/([A-Z]{2})', text, re.IGNORECASE)
    if match:
        cidade = match.group(1).strip()
        estado = match.group(2).strip()
        return cidade, estado
    
    return "", ""


def clean_salary(salary_text: str) -> str:
    """
    Limpa e formata valor de salário
    
    Args:
        salary_text: Texto com valor do salário
        
    Returns:
        Valor formatado
    """
    if not salary_text or salary_text.lower() in ['nan', 'none', '']:
        return ""
    
    # Remove espaços extras
    salary_text = salary_text.strip()
    
    # Remove "R$" se presente
    salary_text = re.sub(r'R\$\s*', '', salary_text)
    
    return salary_text


def clean_text(text: str) -> str:
    """
    Limpa texto removendo espaços extras e caracteres indesejados
    
    Args:
        text: Texto a ser limpo
        
    Returns:
        Texto limpo
    """
    if not text:
        return ""
    
    # Converter para string se necessário
    text = str(text)
    
    # Remover espaços extras
    text = ' '.join(text.split())
    
    # Remover quebras de linha
    text = text.replace('\n', ' ').replace('\r', '')
    
    return text.strip()


def format_carga_horaria(chs: str) -> str:
    """
    Formata carga horária semanal
    
    Args:
        chs: Texto com carga horária
        
    Returns:
        Carga horária formatada
    """
    if not chs:
        return ""
    
    # Extrair apenas números seguidos de 'h'
    match = re.search(r'(\d+)\s*h', chs.lower())
    if match:
        return f"{match.group(1)}h"
    
    return chs.strip()


def is_valid_pdf_url(url: str) -> bool:
    """
    Verifica se uma URL é válida para PDF
    
    Args:
        url: URL a ser verificada
        
    Returns:
        True se é uma URL de PDF válida
    """
    if not url:
        return False
    
    url = url.lower()
    return url.startswith('http') and url.endswith('.pdf')


def sanitize_filename(filename: str) -> str:
    """
    Remove caracteres inválidos de nomes de arquivo
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        Nome de arquivo sanitizado
    """
    # Remover caracteres não permitidos em Windows
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limitar tamanho
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:200] + (f'.{ext}' if ext else '')
    
    return filename


def parse_vagas(vagas_text: str) -> Tuple[int, int]:
    """
    Extrai número de vagas e cadastro reserva
    
    Args:
        vagas_text: Texto com informação de vagas (ex: "03+CR", "01")
        
    Returns:
        Tupla (vagas_imediatas, cadastro_reserva)
    """
    if not vagas_text:
        return 0, 0
    
    # Padrão: XX+CR
    match = re.search(r'(\d+)\s*\+\s*CR', vagas_text, re.IGNORECASE)
    if match:
        vagas = int(match.group(1))
        return vagas, 1  # Tem cadastro reserva
    
    # Apenas número
    match = re.search(r'(\d+)', vagas_text)
    if match:
        return int(match.group(1)), 0
    
    return 0, 0


if __name__ == "__main__":
    # Testes
    print("=== Testes de funções utilitárias ===\n")
    
    # Teste extract_cidade_estado
    print("extract_cidade_estado:")
    print(extract_cidade_estado("MUNICÍPIO DE SOSSÊGO/PB"))
    print(extract_cidade_estado("São Paulo/SP"))
    print()
    
    # Teste clean_salary
    print("clean_salary:")
    print(clean_salary("R$ 3.036,00"))
    print(clean_salary("  1.518,00  "))
    print()
    
    # Teste format_carga_horaria
    print("format_carga_horaria:")
    print(format_carga_horaria("40h"))
    print(format_carga_horaria("30 h"))
    print()
    
    # Teste parse_vagas
    print("parse_vagas:")
    print(parse_vagas("03+CR"))
    print(parse_vagas("01"))
    print(parse_vagas("10 + CR"))
