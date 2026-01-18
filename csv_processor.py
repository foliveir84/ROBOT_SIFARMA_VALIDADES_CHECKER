import pandas as pd
import sys
import os

def process_csv_to_dataframe(csv_path):
    """
    Reads a stock maintenance CSV file and calculates stock and minimum validity per barcode.
    
    Args:
        csv_path (str): Path to the CSV file.
        
    Returns:
        pd.DataFrame: DataFrame with columns ['Código de barras', 'stock robot', 'validade robot'].
                      'validade robot' will be in string format (DD-MM-YYYY).
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")

    # Try reading with different encodings
    try:
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(csv_path, sep=';', encoding='latin1')
        except Exception as e:
            raise ValueError(f"Could not read CSV with utf-8 or latin1 encoding: {e}")

    # Normalize column names to handle encoding issues like "Cdigo"
    # We look for a column that looks like "Codigo de barras"
    target_code_col = None
    target_date_col = None
    
    for col in df.columns:
        if "digo de barras" in col or "Codigo de barras" in col or "Código de barras" in col:
            target_code_col = col
        if "Data de validade" in col:
            target_date_col = col
            
    if not target_code_col or not target_date_col:
        # Fallback: try by index if names fail (1: Code, 5: Date based on sample)
        # Ord.;Cdigo de barras;Unidade;Dosagem;Armazenado em;Data de validade;Nome do artigo
        # 0     1                2       3        4              5                 6
        if len(df.columns) >= 6:
            target_code_col = df.columns[1]
            target_date_col = df.columns[5]
        else:
            raise ValueError(f"Required columns not found. Available: {df.columns.tolist()}")

    # Ensure Code is string to prevent numeric issues
    df[target_code_col] = df[target_code_col].astype(str).str.strip()
    
    # Filter out empty codes or rows that are just separators
    df = df[df[target_code_col] != 'nan']
    df = df[df[target_code_col] != '']

    # Convert Date column to datetime
    # The format appears to be DD-MM-YYYY
    df['date_obj'] = pd.to_datetime(df[target_date_col], format='%d-%m-%Y', errors='coerce')
    
    # Drop rows with invalid dates if necessary, or keep them? 
    # For now, we drop NaT to ensure sorting works
    df = df.dropna(subset=['date_obj'])

    # Group by Barcode
    grouped = df.groupby(target_code_col).agg(
        stock_robot=('date_obj', 'count'),
        validade_robot=('date_obj', 'min')
    ).reset_index()

    # Rename columns for output
    grouped.rename(columns={target_code_col: 'Código de barras', 'stock_robot': 'stock robot', 'validade_robot': 'validade robot'}, inplace=True)

    # Format the date back to string MM-YYYY
    grouped['validade robot'] = grouped['validade robot'].dt.strftime('%m-%Y')

    return grouped

if __name__ == "__main__":
    # Test with the specific file mentioned
    csv_file = "20260115_150433.Manutenção de stock.csv"
    output_test_csv = "stock_robot_grouped.csv"
    
    print(f"Processing {csv_file}...")
    try:
        df_result = process_csv_to_dataframe(csv_file)
        print("Processing successful.")
        print(df_result.head(10))
        print(f"\nTotal unique codes: {len(df_result)}")
        
        df_result.to_csv(output_test_csv, index=False, sep=';')
        print(f"Saved test result to {output_test_csv}")
    except Exception as e:
        print(f"An error occurred: {e}")
