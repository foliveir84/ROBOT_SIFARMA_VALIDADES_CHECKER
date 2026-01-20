# Validação de Stock Robot

## 1. Visão Geral
Este projeto é uma aplicação web desenvolvida em **Streamlit** destinada a auxiliar farmácias na reconciliação de stock entre o sistema de gestão (Sifarma) e o sistema de automação (Robot). A aplicação compara um relatório PDF (Sifarma) com uma exportação CSV (Robot), identifica discrepâncias de quantidades e validades, e gera um relatório final em Excel ou **PDF formatado para impressão** (réplica do layout original).

## 2. Estrutura do Projeto

### Ficheiros Principais
- **`app.py`**: Ponto de entrada da aplicação. Gere a interface do utilizador (UI), o upload de ficheiros, o estado da sessão e a lógica de visualização (Streamlit + JS Components).
- **`pdf_processor.py`**: Módulo responsável pela extração de dados do ficheiro PDF.
- **`csv_processor.py`**: Módulo responsável pela limpeza e agregação dos dados do ficheiro CSV.
- **`data_merger.py`**: Módulo que contém a lógica de negócio para cruzar as tabelas e determinar o estado do stock.
- **`pdf_exporter.py`**: Módulo responsável pela geração do relatório PDF usando `reportlab`.
- **`requirements.txt`**: Lista de dependências Python.

## 3. Lógica de Processamento

### A. Processamento de PDF (`pdf_processor.py`)
- **Biblioteca:** `pdfplumber`.
- **Recuperação de Erros:** Utiliza Regex (`^(\d+?)\s*(\d{7})`) para separar Nº de Ordem e Código CNP mesmo quando "colados" no PDF original.
- **Campos:** Ord., Código, Designação, Stock (Qtd), Validade.

### B. Processamento de CSV (`csv_processor.py`)
- **Biblioteca:** `pandas`.
- **Normalização:** Agrupa por código de barras, soma quantidades e deteta a validade mais curta (`min`).

### C. Fusão e Análise (`data_merger.py`)
- **Método:** *Left Join* (Base Sifarma vs Robot).
- **Lógica de Erro:**
    - `Sifarma > Robot`: "X emb fora do Robot".
    - `Sifarma < Robot`: "Stock em excesso".
    - `Igual`: Vazio.

### D. Geração de PDF (`pdf_exporter.py`)
- **Biblioteca:** `reportlab`.
- **Layout:** A4 Vertical (Portrait).
- **Estrutura:** Mimetiza o documento original "Lista de Controlo de Prazos de Validades".
- **Colunas Mapeadas:**
    - *Ord.*, *Código*, *Designação* (Idênticas).
    - *Val. Robot* (Substitui Lote).
    - *Stock* (Sifarma) e *Robot* (Qtd Real).
    - *Validade* (Sifarma).
    - *Divergência* (Destaque a vermelho se houver erro).

## 4. Interface (UI/UX)
- **Estilo:** Tema "PharmaTouch Glass" (Dark Mode com gradientes néon).
- **Impressão PDF:**
    - Utiliza injeção de **JavaScript** e **Blobs** para contornar limitações de segurança do browser.
    - Tenta abrir o PDF automaticamente num novo separador (`window.open`).
    - Fornece um botão de fallback ("Abrir PDF em nova aba") e botão de download direto.
- **Exportação:** Excel (`.xlsx`) mantendo a ordem original.

## 5. Instalação e Execução

### Dependências
```bash
pip install -r requirements.txt
```
*Conteúdo:*
- streamlit
- pandas
- pdfplumber
- numpy
- openpyxl
- reportlab

### Executar a App
```bash
streamlit run app.py
```