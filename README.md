# Web Scraper de Concursos Públicos

Sistema automatizado para extração de informações de concursos públicos do site [Objetiva Concursos](https://concursos.objetivas.com.br).

## 📋 Funcionalidades

- **Scraping Web**: Extrai lista de concursos abertos
- **Download de PDFs**: Baixa editais automaticamente
- **Parsing de PDFs**: Extrai tabelas com informações de cargos
- **Exportação de Dados**: Salva resultados em CSV, Excel e JSON

## 🚀 Como Usar

### 1. Instalação

```bash
# Clonar o repositório (ou baixar os arquivos)
cd Concursos

# Criar ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### 2. Execução

```bash
# Executar scraping completo
python main.py

# Ou executar módulos individualmente
python src/scraper.py      # Apenas scraping
python src/pdf_parser.py   # Apenas parsing de PDF
```

### 3. Resultados

Os dados são salvos em `data/processed/`:
- **concursos.csv** - Formato CSV (Excel compatível)
- **concursos.xlsx** - Formato Excel (com múltiplas sheets)
- **concursos.json** - Formato JSON (estruturado)

## 📊 Dados Extraídos

Para cada cargo:
- **Cidade**: Município do concurso
- **Cargo**: Nome do cargo público
- **Requisito**: Escolaridade e requisitos exigidos
- **Salário**: Remuneração inicial
- **Carga Horária**: Horas semanais
- **Vagas**: Número de vagas disponíveis

## 🛠️ Estrutura do Projeto

```
Concursos/
├── src/
│   ├── scraper.py      # Scraping do site
│   ├── pdf_parser.py   # Extração de dados dos PDFs
│   ├── models.py       # Modelos de dados
│   └── utils.py        # Funções auxiliares
├── data/
│   ├── raw/           # PDFs baixados
│   └── processed/     # Dados extraídos
├── logs/              # Logs de execução
├── config.py          # Configurações
├── main.py           # Script principal
└── requirements.txt   # Dependências
```

## 📦 Dependências Principais

- **requests** - Requisições HTTP
- **beautifulsoup4** - Parsing HTML
- **pdfplumber** - Extração de tabelas de PDFs
- **pandas** - Manipulação e exportação de dados
- **loguru** - Logging
- **tqdm** - Barras de progresso

## ⚙️ Configurações

Edite `config.py` para ajustar:
- Delay entre requisições
- Timeout de downloads
- Formatos de exportação
- Diretórios de saída

## 📝 Logs

Logs são salvos automaticamente em `logs/`:
- `scraper.log` - Logs do scraping
- `pdf_parser.log` - Logs do parsing de PDFs

## 🤝 Contribuindo

Contribuições são bem-vindas! Sugestões:
- Suporte a outros sites de concursos
- Melhorias na detecção de tabelas
- Filtros e buscas avançadas
- Interface gráfica

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.

## ⚠️ Avisos

- Respeite os termos de uso dos sites
- Use delays adequados entre requisições
- Verifique a legalidade do scraping em sua região

## 🐛 Problemas Conhecidos

- Alguns PDFs podem não ser extraídos corretamente se forem imagens escaneadas
- A estrutura das tabelas pode variar entre editais

## 📞 Suporte

Para reportar bugs ou sugerir melhorias, abra uma issue no repositório.

---

**Desenvolvido com Python** 🐍
