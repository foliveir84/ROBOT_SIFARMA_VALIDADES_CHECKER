import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import tempfile
import os
import base64
from pdf_processor import process_pdf_to_dataframe
from csv_processor import process_csv_to_dataframe
from data_merger import merge_stock_data
from pdf_exporter import generate_pdf

# --- UI STYLE ---
def apply_custom_style():
    """Aplica o design System 'PharmaTouch Glass'."""
    st.markdown("""
    <style>
        /* Fundo e Estrutura Geral */
        .stApp {
            background: linear-gradient(135deg, #0e0b16 0%, #1a1625 100%);
        }
        
        /* Headers com Gradiente Suave */
        h1, h2, h3 {
            background: -webkit-linear-gradient(0deg, #00e5ff, #d900ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }
        
        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        
        /* Inputs Modernos */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #f0f2f6 !important; /* Texto visível (cor de texto do tema) */
            border-radius: 8px !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #d900ff !important;
            box-shadow: 0 0 0 1px #d900ff !important;
        }
        
        /* Botões */
        .stButton button {
            border-radius: 8px;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            background: linear-gradient(90deg, #d900ff, #00e5ff);
            color: white;
            border: none;
        }

        /* Sidebar Background */
        [data-testid="stSidebar"] {
            background-color: #1A1625;
        }
        
        /* Credit top right */
        .credit {
            position: fixed;
            top: 60px;
            right: 20px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
            font-weight: bold;
            z-index: 999999;
            pointer-events: none;
            text-shadow: 0 0 10px rgba(0,0,0,0.5);
        }
    </style>
    <div class="credit">App Desenvolvida por Filipe Oliveira</div>
    """, unsafe_allow_html=True)

def highlight_errors(row):
    """
    Highlights the row in reddish color if stock sifarma != stock robot.
    We check the 'Stock errado' column which is populated if there is a difference.
    """
    # If "Stock errado" has content, it means there is an error
    if row['Stock errado']:
        return ['background-color: rgba(255, 50, 50, 0.2)'] * len(row)
    else:
        return [''] * len(row)

def main():
    st.set_page_config(page_title="Validação de Stock Robot", layout="wide")
    apply_custom_style()
    
    st.title("Validação de Stock Robot")
    
    # Initialize session state for dataframes
    if 'df_pdf' not in st.session_state:
        st.session_state.df_pdf = None
    if 'df_csv' not in st.session_state:
        st.session_state.df_csv = None

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("Carregue os ficheiros PDF (Sifarma) e CSV (Robot) para iniciar a validação.")
    
    uploaded_files = st.file_uploader(
        "Arraste e solte ficheiros PDF e CSV aqui", 
        type=['pdf', 'csv'], 
        accept_multiple_files=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            # Save temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            try:
                if file_extension == 'pdf':
                    with st.spinner(f"Processando PDF: {uploaded_file.name}..."):
                        df = process_pdf_to_dataframe(tmp_path)
                        # Reset index to ensure 'Ord.' is available as a column if it was index
                        if df.index.name == 'Ord.':
                            df.reset_index(inplace=True)
                        st.session_state.df_pdf = df
                        st.success(f"PDF carregado: {len(df)} linhas.")
                
                elif file_extension == 'csv':
                    with st.spinner(f"Processando CSV: {uploaded_file.name}..."):
                        df = process_csv_to_dataframe(tmp_path)
                        st.session_state.df_csv = df
                        st.success(f"CSV carregado: {len(df)} códigos únicos.")
            
            except Exception as e:
                st.error(f"Erro ao processar {uploaded_file.name}: {e}")
            finally:
                os.unlink(tmp_path)

    # Check if both dataframes are ready
    if st.session_state.df_pdf is not None and st.session_state.df_csv is not None:
        st.markdown("---")
        st.subheader("Análise Comparativa")
        
        try:
            final_df = merge_stock_data(st.session_state.df_pdf, st.session_state.df_csv)
            
            # Sort by Ord. if available to maintain original order
            if 'Ord.' in final_df.columns:
                final_df['Ord.'] = pd.to_numeric(final_df['Ord.'], errors='coerce')
                final_df.sort_values('Ord.', inplace=True)
            
            # Display metrics
            total_items = len(final_df)
            error_items = final_df[final_df['Stock errado'] != ""].shape[0]
            
            col1, col2 = st.columns(2)
            col1.metric("Total de Itens", total_items)
            col2.metric("Itens com Divergência", error_items, delta_color="inverse")

            # Apply styling
            styled_df = final_df.style.apply(highlight_errors, axis=1)
            
            st.dataframe(
                styled_df, 
                width='stretch',
                height=600,
                hide_index=True
            )
            
            # Export Options
            import io
            
            # Excel Generation
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Analise_Stock')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Exportar Excel",
                    data=buffer.getvalue(),
                    file_name="analise_stock_robot.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
            with col2:
                if st.button("🖨️ Imprimir PDF", use_container_width=True):
                    with st.spinner("Gerando PDF..."):
                        pdf_buffer = generate_pdf(final_df)
                        pdf_bytes = pdf_buffer.getvalue()
                        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                        
                        # Javascript to open PDF in new tab via Blob and provide a working manual link
                        pdf_display_js = f"""
                            <html>
                            <head>
                            <style>
                                body {{
                                    background-color: transparent;
                                    color: white;
                                    font-family: "Source Sans Pro", sans-serif;
                                }}
                                .btn {{
                                    display: inline-flex;
                                    align-items: center;
                                    justify-content: center;
                                    padding: 0.5rem 1rem;
                                    background-color: #ff4b4b;
                                    color: white;
                                    text-decoration: none;
                                    border-radius: 0.5rem;
                                    font-weight: 600;
                                    border: 1px solid rgba(255, 255, 255, 0.2);
                                    transition: background-color 0.3s;
                                }}
                                .btn:hover {{ background-color: #ff2b2b; }}
                            </style>
                            </head>
                            <body>
                            <div style="display: flex; flex-direction: column; align-items: center; gap: 10px;">
                                <span>Se a aba não abrir, clique aqui:</span>
                                <a id="pdfLink" href="#" target="_blank" class="btn">📄 Abrir PDF em nova aba</a>
                            </div>
                            
                            <script>
                                function b64toBlob(b64Data, contentType='', sliceSize=512) {{
                                    const byteCharacters = atob(b64Data);
                                    const byteArrays = [];

                                    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {{
                                        const slice = byteCharacters.slice(offset, offset + sliceSize);

                                        const byteNumbers = new Array(slice.length);
                                        for (let i = 0; i < slice.length; i++) {{
                                            byteNumbers[i] = slice.charCodeAt(i);
                                        }}

                                        const byteArray = new Uint8Array(byteNumbers);
                                        byteArrays.push(byteArray);
                                    }}

                                    const blob = new Blob(byteArrays, {{type: contentType}});
                                    return blob;
                                }}

                                const b64pdf = "{base64_pdf}";
                                const blob = b64toBlob(b64pdf, "application/pdf");
                                const blobUrl = URL.createObjectURL(blob);
                                
                                const link = document.getElementById('pdfLink');
                                link.href = blobUrl;
                                
                                // Attempt auto-open
                                window.open(blobUrl, "_blank");
                            </script>
                            </body>
                            </html>
                        """
                        # Render component with enough height to show the link
                        components.html(pdf_display_js, height=100)
                        
                        st.success("PDF gerado!")
                        
                        st.download_button(
                            label="⬇️ Baixar PDF",
                            data=pdf_bytes,
                            file_name="relatorio_stock.pdf",
                            mime="application/pdf",
                            key='pdf-download'
                        )
            
        except Exception as e:
            st.error(f"Erro na fusão dos dados: {e}")

if __name__ == "__main__":
    main()
