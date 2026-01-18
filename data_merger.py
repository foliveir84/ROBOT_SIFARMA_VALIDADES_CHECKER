import pandas as pd
import numpy as np

def merge_stock_data(df_pdf, df_csv):
    """
    Merges the PDF dataframe (Sifarma) with the CSV dataframe (Robot).
    
    Args:
        df_pdf (pd.DataFrame): Data from PDF (columns: Ord., Código, Designação, Stock, Validade)
        df_csv (pd.DataFrame): Data from CSV (columns: Código de barras, stock robot, validade robot)
        
    Returns:
        pd.DataFrame: Merged and analyzed dataframe.
    """
    
    # 1. Prepare Join Keys (Ensure string format and strip whitespace)
    # Using .copy() to avoid SettingWithCopyWarning on the original dfs
    left_df = df_pdf.copy()
    right_df = df_csv.copy()
    
    left_df['Código'] = left_df['Código'].astype(str).str.strip()
    right_df['Código de barras'] = right_df['Código de barras'].astype(str).str.strip()
    
    # 2. Merge (Left Join on PDF codes)
    # We use left join because the PDF is the "Control List" (Lista de Controlo)
    merged = pd.merge(
        left_df,
        right_df,
        left_on='Código',
        right_on='Código de barras',
        how='left'
    )
    
    # 3. Clean up and Rename Columns
    # Fill NaN values for Stock Robot with 0 (if product not in CSV, robot has 0)
    merged['stock robot'] = merged['stock robot'].fillna(0).astype(int)
    
    # Rename columns to target structure
    column_mapping = {
        'Ord.': 'Ord.',
        'Código': 'Codigo',
        'Designação': 'Designacao',
        'Stock': 'Stock', # Sifarma Stock
        'stock robot': 'Stock Robot',
        'Validade': 'Validade Sifarma',
        'validade robot': 'Validade Real'
    }
    
    merged.rename(columns=column_mapping, inplace=True)
    
    # 4. Calculate 'Stock errado' column based on user logic
    # Logic: 
    # If Stock < Stock Robot -> "X caixas fora do robot"
    # If Stock > Stock Robot -> "Stock em excesso"
    # Else (Equal) -> "" (Empty)
    
    def calculate_stock_status(row):
        sifarma = row['Stock']
        robot = row['Stock Robot']
        
        diff = abs(sifarma - robot)
        
        if sifarma == robot:
            return ""
        elif sifarma < robot:
            return "Stock em excesso"
        else: # sifarma > robot
            return f"{diff} emb fora do Robot"

    merged['Stock errado'] = merged.apply(calculate_stock_status, axis=1)
    
    # 5. Select Final Columns
    # Handle the case where 'Ord.' might be an index in df_pdf
    if 'Ord.' not in merged.columns and 'Ord.' in df_pdf.index.names:
        merged['Ord.'] = merged.index
        
    final_columns = [
        'Ord.', 
        'Codigo', 
        'Designacao', 
        'Stock', 
        'Stock Robot', 
        'Validade Sifarma', 
        'Validade Real', 
        'Stock errado'
    ]
    
    # Ensure Ord. exists if it was preserved from left join or index
    cols_to_keep = [c for c in final_columns if c in merged.columns]
    
    return merged[cols_to_keep]

if __name__ == "__main__":
    # Test block
    from pdf_processor import process_pdf_to_dataframe
    from csv_processor import process_csv_to_dataframe
    
    print("Loading Data...")
    try:
        df_pdf = process_pdf_to_dataframe("01 robot.pdf")
        df_csv = process_csv_to_dataframe("20260115_150433.Manutenção de stock.csv")
        
        # Reset index of PDF to make Ord. a column if it is currently index
        if df_pdf.index.name == 'Ord.':
            df_pdf.reset_index(inplace=True)
            
        print("Merging...")
        final_df = merge_stock_data(df_pdf, df_csv)
        
        print("Result Head:")
        print(final_df.head())
        
        final_df.to_csv("final_stock_analysis.csv", index=False, sep=';', encoding='utf-8-sig')
        print("Saved to final_stock_analysis.csv")
        
    except Exception as e:
        print(f"Error: {e}")
