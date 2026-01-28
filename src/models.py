"""
Modelos de Dados para Concursos e Cargos
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from pathlib import Path
import json


@dataclass
class Cargo:
    """Representa um cargo de concurso público"""
    cidade: str
    cargo: str
    requisito: str
    salario: str
    carga_horaria: str = ""
    vagas: str = ""
    concurso_id: str = ""
    concurso_nome: str = ""
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'cidade': self.cidade,
            'cargo': self.cargo,
            'requisito': self.requisito,
            'salario': self.salario,
            'carga_horaria': self.carga_horaria,
            'vagas': self.vagas,
            'concurso_id': self.concurso_id,
            'concurso_nome': self.concurso_nome
        }


@dataclass
class Concurso:
    """Representa um concurso público"""
    id: str
    nome: str
    url: str
    cidade: str = ""
    estado: str = ""
    cargos: List[Cargo] = field(default_factory=list)
    edital_url: str = ""
    data_extracao: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_cargo(self, cargo: Dict):
        """
        Adiciona um cargo ao concurso
        
        Args:
            cargo: Dicionário com informações do cargo
        """
        cargo_obj = Cargo(
            cidade=cargo.get('cidade', self.cidade),
            cargo=cargo.get('cargo', ''),
            requisito=cargo.get('requisito', ''),
            salario=cargo.get('salario', ''),
            carga_horaria=cargo.get('carga_horaria', ''),
            vagas=cargo.get('vagas', ''),
            concurso_id=self.id,
            concurso_nome=self.nome
        )
        self.cargos.append(cargo_obj)
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'url': self.url,
            'cidade': self.cidade,
            'estado': self.estado,
            'edital_url': self.edital_url,
            'data_extracao': self.data_extracao,
            'total_cargos': len(self.cargos),
            'cargos': [cargo.to_dict() for cargo in self.cargos]
        }


class ConcursosDatabase:
    """Gerenciador de dados de concursos"""
    
    def __init__(self, output_dir: str = "data/processed"):
        """
        Inicializa o gerenciador
        
        Args:
            output_dir: Diretório para salvar arquivos processados
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.concursos: List[Concurso] = []
    
    def add_concurso(self, concurso: Concurso):
        """Adiciona um concurso ao banco de dados"""
        self.concursos.append(concurso)
    
    def get_all_cargos(self) -> List[Dict]:
        """
        Retorna todos os cargos de todos os concursos
        
        Returns:
            Lista de dicionários com informações dos cargos
        """
        all_cargos = []
        for concurso in self.concursos:
            for cargo in concurso.cargos:
                all_cargos.append(cargo.to_dict())
        return all_cargos
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Converte todos os cargos para DataFrame
        
        Returns:
            DataFrame com todos os cargos
        """
        cargos = self.get_all_cargos()
        if not cargos:
            return pd.DataFrame()
        
        df = pd.DataFrame(cargos)
        
        # Reordenar colunas para melhor visualização
        cols_order = ['cidade', 'cargo', 'requisito', 'salario', 
                     'carga_horaria', 'vagas', 'concurso_nome', 'concurso_id']
        
        # Manter apenas colunas que existem
        cols_order = [col for col in cols_order if col in df.columns]
        
        return df[cols_order]
    
    def export_to_csv(self, filename: str = "concursos.csv") -> Path:
        """
        Exporta dados para CSV
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Path do arquivo criado
        """
        filepath = self.output_dir / filename
        df = self.to_dataframe()
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        return filepath
    
    def export_to_excel(self, filename: str = "concursos.xlsx") -> Path:
        """
        Exporta dados para Excel
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Path do arquivo criado
        """
        filepath = self.output_dir / filename
        df = self.to_dataframe()
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Sheet com todos os cargos
            df.to_excel(writer, sheet_name='Todos os Cargos', index=False)
            
            # Sheet com resumo por cidade
            if 'cidade' in df.columns:
                resumo_cidade = df.groupby('cidade').size().reset_index(name='total_cargos')
                resumo_cidade.to_excel(writer, sheet_name='Resumo por Cidade', index=False)
            
            # Ajustar largura das colunas
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return filepath
    
    def export_to_json(self, filename: str = "concursos.json") -> Path:
        """
        Exporta dados para JSON
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Path do arquivo criado
        """
        filepath = self.output_dir / filename
        
        data = {
            'total_concursos': len(self.concursos),
            'total_cargos': sum(len(c.cargos) for c in self.concursos),
            'data_extracao': datetime.now().isoformat(),
            'concursos': [concurso.to_dict() for concurso in self.concursos]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def get_summary(self) -> Dict:
        """
        Retorna resumo dos dados coletados
        
        Returns:
            Dicionário com estatísticas
        """
        total_cargos = sum(len(c.cargos) for c in self.concursos)
        
        cidades = set()
        for concurso in self.concursos:
            for cargo in concurso.cargos:
                if cargo.cidade:
                    cidades.add(cargo.cidade)
        
        return {
            'total_concursos': len(self.concursos),
            'total_cargos': total_cargos,
            'total_cidades': len(cidades),
            'cidades': sorted(list(cidades))
        }


if __name__ == "__main__":
    # Teste dos modelos
    db = ConcursosDatabase()
    
    # Criar concurso de exemplo
    concurso = Concurso(
        id="2577",
        nome="Município de Sossêgo/PB",
        url="https://concursos.objetivas.com.br/informacoes/2577/",
        cidade="Sossêgo",
        estado="PB"
    )
    
    # Adicionar cargos
    concurso.add_cargo({
        'cargo': 'Agente Comunitário de Saúde',
        'requisito': 'Ensino Médio completo',
        'salario': '3.036,00',
        'carga_horaria': '40h',
        'vagas': '04+CR'
    })
    
    concurso.add_cargo({
        'cargo': 'Enfermeiro PSF',
        'requisito': 'Ensino Superior completo e habilitação legal',
        'salario': '1.518,00',
        'carga_horaria': '40h',
        'vagas': '02+CR'
    })
    
    db.add_concurso(concurso)
    
    # Exportar
    print("Exportando dados...")
    csv_file = db.export_to_csv("test_concursos.csv")
    print(f"CSV criado: {csv_file}")
    
    excel_file = db.export_to_excel("test_concursos.xlsx")
    print(f"Excel criado: {excel_file}")
    
    # Resumo
    print("\nResumo:")
    print(db.get_summary())
