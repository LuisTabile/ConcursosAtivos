"""
Script de Debug para analisar estrutura dos PDFs
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pdfplumber
import pandas as pd

def debug_pdf(pdf_path):
    """Analisa estrutura de um PDF"""
    print(f"\n{'='*80}")
    print(f"Analisando: {pdf_path}")
    print(f"{'='*80}\n")
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total de páginas: {len(pdf.pages)}\n")
        
        # Analisar tabelas
        all_tables = []
        for page_num, page in enumerate(pdf.pages[:5], 1):  # Primeiras 5 páginas
            tables = page.extract_tables()
            
            if tables:
                print(f"\n--- Página {page_num} ---")
                print(f"Tabelas encontradas: {len(tables)}")
                
                for idx, table in enumerate(tables, 1):
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        all_tables.append((page_num, idx, df))
                        
                        print(f"\nTabela {idx}:")
                        print(f"  Dimensões: {df.shape}")
                        print(f"  Colunas: {list(df.columns)}")
                        print(f"\n  Primeiras linhas:")
                        print(df.head(3).to_string(index=False))
        
        # Procurar tabela de cargos
        print(f"\n\n{'='*80}")
        print("ANÁLISE DE TABELAS DE CARGOS")
        print(f"{'='*80}\n")
        
        keywords = ['cargo', 'escolaridade', 'requisito', 'salário', 'remuneração', 
                   'vencimento', 'vagas', 'chs', 'carga']
        
        for page_num, table_idx, df in all_tables:
            columns_text = ' '.join([str(col).lower() for col in df.columns])
            
            # Contar palavras-chave
            matches = [kw for kw in keywords if kw in columns_text]
            
            if len(matches) >= 3:  # Pelo menos 3 palavras-chave
                print(f"\n✓ POSSÍVEL TABELA DE CARGOS:")
                print(f"  Página {page_num}, Tabela {table_idx}")
                print(f"  Dimensões: {df.shape}")
                print(f"  Palavras-chave encontradas: {matches}")
                print(f"  Colunas: {list(df.columns)}")
                print(f"\n  Dados:")
                print(df.to_string(index=False, max_rows=10))
                print(f"\n  Tipos de dados nas colunas:")
                for col in df.columns:
                    sample = df[col].dropna().head(3).tolist()
                    print(f"    {col}: {sample}")


if __name__ == "__main__":
    # Analisar PDFs baixados
    pdf_dir = Path("data/raw")
    
    pdfs = list(pdf_dir.glob("*.pdf"))
    
    if not pdfs:
        print("Nenhum PDF encontrado em data/raw/")
    else:
        print(f"PDFs encontrados: {len(pdfs)}")
        
        for pdf_path in pdfs[:2]:  # Analisar primeiros 2 PDFs
            debug_pdf(pdf_path)
