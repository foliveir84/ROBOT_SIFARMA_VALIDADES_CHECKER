# Validação de Stock Robot

## 1. Visão Geral
Este projeto é uma aplicação web desenvolvida em **Streamlit** destinada a auxiliar farmácias na reconciliação de stock entre o sistema de gestão (Sifarma) e o sistema de automação (Robot). A aplicação compara um relatório PDF (Sifarma) com uma exportação CSV (Robot), identifica discrepâncias de quantidades e validades, e gera um relatório final em Excel.

## 2. Estrutura do Projeto

### Ficheiros Principais
- **`app.py`**: Ponto de entrada da aplicação. Gere a interface do utilizador (UI), o upload de ficheiros, o estado da sessão (`st.session_state`) e a execução dos processadores.
- **`pdf_processor.py`**: Módulo responsável pela extração de dados do ficheiro PDF.
- **`csv_processor.py`**: Módulo responsável pela limpeza e agregação dos dados do ficheiro CSV.
- **`data_merger.py`**: Módulo que contém a lógica de negócio para cruzar as tabelas e determinar o estado do stock.
- **`requirements.txt`**: Lista de dependências Python.

## 3. Lógica de Processamento

### A. Processamento de PDF (`pdf_processor.py`)
- **Biblioteca:** `pdfplumber`.
- **Desafio:** O PDF original apresenta, por vezes, o número de ordem (`Ord.`) e o `Código` colados (ex: `15323951` em vez de `1 5323951`).
- **Solução:** Utiliza Regex robusta (`^(\d+?)\s*(\d{7})`) que captura os **últimos 7 dígitos** do bloco numérico inicial como Código CNP. Isto garante a extração correta independentemente de existir espaço ou não entre o Nº de Ordem e o Código, resolvendo casos de números colados ou separados.
- **Campos Extraídos:** Ord., Código, Designação, Stock (Qtd), Validade.

### B. Processamento de CSV (`csv_processor.py`)
- **Biblioteca:** `pandas`.
- **Lógica:**
    1.  Deteta delimitadores (`;`) e encodings (`utf-8` ou `latin1`).
    2.  Limpa nomes de colunas para garantir consistência.
    3.  **Agrupamento:** Agrupa as linhas por `Código de barras`.
    4.  **Cálculo de Stock:** Conta o número de ocorrências de cada código (`count`).
    5.  **Cálculo de Validade:** Converte datas com `dayfirst=True` para suportar formatos com barras (`DD/MM/YYYY`) ou hífens. Identifica a data de validade mais antiga (`min`) e formata para `MM-YYYY`.

### C. Fusão e Análise (`data_merger.py`)
- **Método:** *Left Join* usando a tabela do PDF como base (Tabela da esquerda) e o CSV como complemento (Tabela da direita).
- **Lógica de Comparação ("Stock errado"):**
    - **Se `Stock Sifarma` > `Stock Robot`**: Significa que o sistema diz que há mais do que o robot tem.
      - *Output:* `"{Diferença} emb fora do Robot"`
    - **Se `Stock Sifarma` < `Stock Robot`**: Significa que o robot tem mais unidades do que o sistema regista.
      - *Output:* `"Stock em excesso"`
    - **Se Iguais**: Campo vazio.

## 4. Interface (UI/UX)
- **Estilo:** Tema "PharmaTouch Glass" definido em CSS personalizado (Fundo escuro, cartões com efeito *glassmorphism*, gradientes néon).
- **Funcionalidades:**
    - Upload unificado (arrastar e largar PDF e CSV no mesmo campo).
    - Destaque visual: Linhas com erros de stock são sublinhadas a vermelho (`rgba(255, 50, 50, 0.2)`).
    - Créditos: "App Desenvolvida por Filipe Oliveira" fixo no canto superior direito.
    - **Exportação:** Gera um ficheiro Excel (`.xlsx`) mantendo a ordem original do PDF.

## 5. Instalação e Execução

### Dependências
```bash
pip install -r requirements.txt
```
*Conteúdo do requirements.txt:*
- streamlit
- pandas
- pdfplumber
- numpy
- openpyxl

### Executar a App
```bash
streamlit run app.py
```
