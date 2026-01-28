"""
Script de Debug Avançado - Análise detalhada de tabelas específicas
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pdfplumber
import pandas as pd

def analyze_specific_pdf(pdf_path, start_page=1, end_page=5):
    """Analisa páginas específicas buscando por tabelas de cargos"""
    print(f"\n{'='*100}")
    print(f"Análise detalhada: {pdf_path}")
    print(f"{'='*100}\n")
    
    with pdfplumber.open(pdf_path) as pdf:
        all_tables = []
        
        for page_num in range(start_page-1, min(end_page, len(pdf.pages))):
            page = pdf.pages[page_num]
            tables = page.extract_tables()
            
            if tables:
                print(f"\n--- Página {page_num + 1} ---")
                for idx, table in enumerate(tables, 1):
                    if not table:
                        continue
                    
                    df = pd.DataFrame(table[1:], columns=table[0])
                    
                    # Verificar se contém palavras-chave de cargos
                    keywords = ['cargo', 'escolaridade', 'requisito', 'salário', 'vagas']
                    columns_text = ' '.join([str(col).lower() for col in df.columns])
                    first_row = ' '.join([str(val).lower() for val in df.iloc[0]]) if len(df) > 0 else ""
                    combined = columns_text + ' ' + first_row
                    
                    matches = [kw for kw in keywords if kw in combined]
                    
                    if matches or len(df) > 15:  # Muitas linhas podem ser tabela de cargos
                        print(f"\nTabela {idx} - POTENCIAL TABELA DE CARGOS")
                        print(f"  Dimensões: {df.shape}")
                        print(f"  Palavras-chave: {matches}")
                        print(f"  Colunas ({len(df.columns)}): {list(df.columns)[:5]}...")
                        print(f"\n  Primeiras 3 linhas:")
                        
                        # Mostrar primeiras linhas com todas as colunas
                        for i in range(min(3, len(df))):
                            row = df.iloc[i]
                            print(f"    Linha {i}:")
                            for col_idx, val in enumerate(row):
                                val_str = str(val)[:80] if val else "None"
                                print(f"      Col{col_idx}: {val_str}")
                        
                        all_tables.append((page_num+1, idx, df))

if __name__ == "__main__":
    # Analisar PDF do Sossêgo (33 cargos esperados)
    pdf_path = Path("data/raw/concurso_2577.pdf")
    
    if pdf_path.exists():
        print("\n🔍 Análise do PDF de Sossêgo/PB")
        print("Esperado: 33 cargos")
        analyze_specific_pdf(pdf_path, start_page=2, end_page=4)
    else:
        print(f"PDF não encontrado: {pdf_path}")
