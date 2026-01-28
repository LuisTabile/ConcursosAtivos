"""
Script Principal - Web Scraper de Concursos Públicos

Orquestra o fluxo completo:
1. Scraping dos concursos abertos
2. Download e parsing dos editais
3. Exportação dos dados
"""

import sys
from pathlib import Path
from loguru import logger
from tqdm import tqdm

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.scraper import ConcursoScraper
from src.pdf_parser import PDFParser
from src.models import Concurso, ConcursosDatabase
from src.utils import extract_cidade_estado, clean_salary, clean_text
import config


def setup_logging():
    """Configura o sistema de logging"""
    logger.remove()  # Remove handler padrão
    
    # Console
    logger.add(
        sys.stderr,
        format=config.LOG_FORMAT,
        level="INFO"
    )
    
    # Arquivo de log
    logger.add(
        config.LOGS_DIR / "main.log",
        rotation=config.LOG_ROTATION,
        retention=config.LOG_RETENTION,
        format=config.LOG_FORMAT,
        level="DEBUG"
    )
    
    logger.info("Sistema de logging configurado")


def main():
    """Função principal"""
    logger.info("=" * 60)
    logger.info("Iniciando Web Scraper de Concursos Públicos")
    logger.info("=" * 60)
    
    # Inicializar componentes
    scraper = ConcursoScraper(delay=config.REQUEST_DELAY)
    pdf_parser = PDFParser(download_dir=str(config.RAW_DATA_DIR))
    database = ConcursosDatabase(output_dir=str(config.PROCESSED_DATA_DIR))
    
    try:
        # ETAPA 1: Scraping dos concursos abertos
        logger.info("\n[ETAPA 1/3] Buscando concursos abertos...")
        concursos_data = scraper.scrape_all()
        
        if not concursos_data:
            logger.error("Nenhum concurso encontrado. Encerrando.")
            return
        
        logger.success(f"✓ {len(concursos_data)} concursos encontrados")
        
        # ETAPA 2: Processar cada concurso
        logger.info("\n[ETAPA 2/3] Processando editais e extraindo dados...")
        
        for concurso_info in tqdm(concursos_data, desc="Processando concursos"):
            concurso_obj = concurso_info['concurso']
            edital_principal = concurso_info['edital_principal']
            
            # Criar objeto Concurso
            logger.info(f"\nProcessando: {concurso_obj['nome']}")
            
            # Extrair cidade e estado do nome
            cidade, estado = extract_cidade_estado(concurso_obj['nome'])
            
            concurso = Concurso(
                id=concurso_obj['id'],
                nome=concurso_obj['nome'],
                url=concurso_obj['url'],
                cidade=cidade,
                estado=estado
            )
            
            # Se houver edital principal, processar
            if edital_principal:
                concurso.edital_url = edital_principal['url']
                logger.info(f"  Edital: {edital_principal['titulo']}")
                
                # Processar PDF
                try:
                    cargos = pdf_parser.process_edital(
                        url=edital_principal['url'],
                        cidade=cidade,
                        concurso_id=concurso_obj['id']
                    )
                    
                    # Adicionar cargos ao concurso
                    for cargo in cargos:
                        # Limpar dados
                        cargo['cargo'] = clean_text(cargo['cargo'])
                        cargo['requisito'] = clean_text(cargo['requisito'])
                        cargo['salario'] = clean_salary(cargo['salario'])
                        
                        concurso.add_cargo(cargo)
                    
                    logger.success(f"  ✓ {len(cargos)} cargos extraídos")
                    
                except Exception as e:
                    logger.error(f"  ✗ Erro ao processar edital: {e}")
            else:
                logger.warning(f"  ⚠ Nenhum edital encontrado")
            
            # Adicionar concurso ao banco de dados
            database.add_concurso(concurso)
        
        # ETAPA 3: Exportar dados
        logger.info("\n[ETAPA 3/3] Exportando dados...")
        
        # Exibir resumo
        summary = database.get_summary()
        logger.info(f"\n📊 Resumo da coleta:")
        logger.info(f"  • Total de concursos: {summary['total_concursos']}")
        logger.info(f"  • Total de cargos: {summary['total_cargos']}")
        logger.info(f"  • Total de cidades: {summary['total_cidades']}")
        
        if summary['cidades']:
            logger.info(f"  • Cidades: {', '.join(summary['cidades'][:5])}" + 
                       (f"... (+{len(summary['cidades'])-5} mais)" if len(summary['cidades']) > 5 else ""))
        
        # Exportar em múltiplos formatos
        if 'csv' in config.EXPORT_FORMATS:
            csv_file = database.export_to_csv(config.DEFAULT_CSV_FILENAME)
            logger.success(f"  ✓ CSV exportado: {csv_file}")
        
        if 'excel' in config.EXPORT_FORMATS:
            excel_file = database.export_to_excel(config.DEFAULT_EXCEL_FILENAME)
            logger.success(f"  ✓ Excel exportado: {excel_file}")
        
        if 'json' in config.EXPORT_FORMATS:
            json_file = database.export_to_json(config.DEFAULT_JSON_FILENAME)
            logger.success(f"  ✓ JSON exportado: {json_file}")
        
        logger.info("\n" + "=" * 60)
        logger.success("✓ Scraping concluído com sucesso!")
        logger.info("=" * 60)
        
        # Exibir preview dos dados
        df = database.to_dataframe()
        if not df.empty:
            logger.info("\n📋 Preview dos dados (primeiras 5 linhas):")
            print("\n" + df.head().to_string(index=False))
        
    except KeyboardInterrupt:
        logger.warning("\n⚠ Processo interrompido pelo usuário")
        sys.exit(1)
    
    except Exception as e:
        logger.exception(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    main()
