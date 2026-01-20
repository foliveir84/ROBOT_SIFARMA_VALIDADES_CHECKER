import re
import pandas as pd
import sys

def process_pdf_to_dataframe(pdf_path):
    """
    Reads a PDF file and extracts the stock validation table into a pandas DataFrame.
    
    Args:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        pd.DataFrame: DataFrame with columns ['Ord.', 'Código', 'Designação', 'Stock', 'Validade'],
                      indexed by 'Ord.'.
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("The 'pdfplumber' library is required. Please install it with: pip install pdfplumber")

    data = []
    current_entry = None
    
    # Regex to capture the main data line.
    # Logic: The Code is ALWAYS the last 7 digits of the initial number block.
    # The rest (prefix) is the Order Number (Ord).
    # This handles both "1 5323951" (space) and "15323951" (merged) correctly.
    
    # ^(\d+?) matches Ord (lazy, consumes minimum needed)
    # \s* matches optional space
    # (\d{7}) matches Code (strict 7 digits)
    # \s+ matches space separator before Description
    line_regex = re.compile(r'^(\d+?)\s*(\d{7})\s+(.*?)LOTE\s+[^0-9]+?\s+(\d+)\s+[A-Z\.]+\s+(\d{2}-\d{4})')

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
                
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                match = line_regex.search(line)
                
                if match:
                    # New Entry Found
                    ord_val = match.group(1)
                    code_val = match.group(2)
                    desc_part = match.group(3).strip()
                    stock = match.group(4)
                    validade = match.group(5)
                    
                    current_entry = {
                        "Ord.": int(ord_val),
                        "Código": code_val,
                        "Designação": desc_part,
                        "Stock": int(stock),
                        "Validade": validade
                    }
                    data.append(current_entry)
                else:
                    # Not a main data line. 
                    # Check if it's a continuation of the description for the current entry.
                    # We must ignore headers/footers.
                    
                    # Heuristics to ignore headers/footers
                    lower = line.lower()
                    if "farmacia" in lower or "nif:" in lower or "telefone:" in lower:
                        continue
                    if "lista de controlo" in lower or "expiram entre" in lower:
                        continue
                    if "ord. código" in lower or "lotedesignação" in lower:
                        continue
                    if "impressão:" in lower or "página" in lower:
                        continue
                    
                    # If we have an active entry, append this text to its description
                    if current_entry:
                        current_entry["Designação"] += " " + line

    if not data:
        print("Warning: No data extracted.")
        return pd.DataFrame(columns=['Ord.', 'Código', 'Designação', 'Stock', 'Validade'])

    df = pd.DataFrame(data)
    df.set_index('Ord.', inplace=True)
    return df

if __name__ == "__main__":
    pdf_file = "01 robot.pdf"
    output_csv = "stock_validade_extracted.csv"
    
    print(f"Processing {pdf_file}...")
    try:
        df = process_pdf_to_dataframe(pdf_file)
        if not df.empty:
            print("Extraction successful.")
            print(df.head(10))
            print(f"\nTotal rows: {len(df)}")
            df.to_csv(output_csv)
            print(f"Saved to {output_csv}")
        else:
            print("Extraction failed (empty dataframe).")
    except Exception as e:
        print(f"An error occurred: {e}")