"""
Configurações do projeto
"""

import os
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"

# URLs
BASE_URL = "https://concursos.objetivas.com.br"
ABERTOS_URL = f"{BASE_URL}/index/abertos/"

# Configurações de scraping
REQUEST_DELAY = 1.0  # Segundos entre requisições
REQUEST_TIMEOUT = 30  # Timeout para requisições HTTP
PDF_DOWNLOAD_TIMEOUT = 60  # Timeout para download de PDFs

# User Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Configurações de exportação
EXPORT_FORMATS = ['csv', 'excel', 'json']  # Formatos de exportação habilitados
DEFAULT_CSV_FILENAME = "concursos.csv"
DEFAULT_EXCEL_FILENAME = "concursos.xlsx"
DEFAULT_JSON_FILENAME = "concursos.json"

# Logging
LOG_ROTATION = "10 MB"
LOG_RETENTION = "30 days"
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"

# PDF Processing
PDF_TABLE_SETTINGS = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 3,
}

# Palavras-chave para identificar tabelas de cargos
CARGO_TABLE_KEYWORDS = [
    'cargo', 'escolaridade', 'requisito', 'salário', 'remuneração',
    'vencimento', 'vagas', 'chs', 'carga horária', 'função'
]

# Criar diretórios se não existirem
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
