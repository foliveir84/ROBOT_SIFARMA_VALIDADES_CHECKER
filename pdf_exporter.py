from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime

def generate_pdf(df):
    """
    Gera um PDF formatado (Vertical A4) similar ao original do Sifarma.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=portrait(A4),
        rightMargin=1.0*cm,
        leftMargin=1.0*cm,
        topMargin=1.0*cm,
        bottomMargin=1.0*cm
    )

    elements = []
    styles = getSampleStyleSheet()
    
    # --- Título ---
    # Estilo similar ao cabeçalho do documento original
    title_style = ParagraphStyle(
        'TitleCustom',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=1, # Center
        spaceAfter=10,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleCustom',
        parent=styles['Normal'],
        fontSize=9,
        alignment=1, # Center
        spaceAfter=20,
        textColor=colors.black
    )

    elements.append(Paragraph("Lista de Controlo de Prazos de Validades", title_style))
    elements.append(Paragraph(f"Relatório Comparativo (Sifarma vs Robot) - Gerado em {datetime.now().strftime('%d-%m-%Y')}", subtitle_style))
    
    # --- Tabela ---
    # Mapeamento de colunas para simular o layout original
    # Original: Ord. | Código | Designação | Lote | Stock | Pratel. | Validade | Correcção
    # Adaptado: Ord. | Código | Designação | Val. Robot | Stock | Robot | Validade | Divergência
    
    headers = ['Ord.', 'Código', 'Designação', 'Val. Robot', 'Stock', 'Robot', 'Validade', 'Divergência']
    
    # Larguras aproximadas para caber em 19cm (A4 Portrait - Margens)
    # Ajustado para dar prioridade à Designação e Divergência
    col_widths = [
        0.8*cm,  # Ord.
        1.8*cm,  # Código
        6.2*cm,  # Designação
        2.0*cm,  # Val. Robot (No lugar de Lote)
        1.0*cm,  # Stock
        1.0*cm,  # Robot (No lugar de Pratel.)
        2.0*cm,  # Validade
        4.2*cm   # Divergência (No lugar de Correcção)
    ]
    
    # Estilos de Célula
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=7,
        leading=8,
        alignment=0 # Left
    )
    
    header_para_style = ParagraphStyle(
        'HeaderParaStyle',
        parent=cell_style,
        fontName='Helvetica-Bold',
        fontSize=8,
        alignment=1 # Center
    )

    data = []
    
    # Linha de Cabeçalho Formatada
    header_row = [Paragraph(h, header_para_style) for h in headers]
    data.append(header_row)
    
    # Linhas de Dados
    for idx, row in df.iterrows():
        # Extração segura de dados
        ord_val = str(row.get('Ord.', ''))
        cod_val = str(row.get('Codigo', ''))
        des_val = str(row.get('Designacao', ''))
        stk_sif = str(row.get('Stock', ''))
        stk_rob = str(row.get('Stock Robot', ''))
        val_sif = str(row.get('Validade Sifarma', ''))
        val_rob = str(row.get('Validade Real', ''))
        err_val = str(row.get('Stock errado', ''))
        
        # Cor de destaque para erros
        is_error = bool(err_val) and err_val.strip() != ""
        text_color = colors.red if is_error else colors.black
        
        # Estilo específico para a linha (cor)
        row_style = ParagraphStyle(
            f'Row_{idx}',
            parent=cell_style,
            textColor=text_color
        )
        
        # Montagem da linha
        # Mapeamento:
        # Ord -> Ord
        # Codigo -> Codigo
        # Designacao -> Designacao
        # Val. Robot -> Validade Real (ocupando coluna Lote)
        # Stock -> Stock
        # Robot -> Stock Robot (ocupando coluna Pratel.)
        # Validade -> Validade Sifarma
        # Divergência -> Stock errado
        
        row_cells = [
            Paragraph(ord_val, row_style),
            Paragraph(cod_val, row_style),
            Paragraph(des_val, row_style),
            Paragraph(val_rob, row_style),
            Paragraph(stk_sif, row_style),
            Paragraph(stk_rob, row_style),
            Paragraph(val_sif, row_style),
            Paragraph(err_val, row_style)
        ]
        data.append(row_cells)

    # Configuração da Tabela
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    style_cmds = [
        # Grelha
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        # Alinhamento
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'), # Header center
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]
    
    table.setStyle(TableStyle(style_cmds))
    elements.append(table)
    
    # Rodapé simples
    elements.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8)
    now_str = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    elements.append(Paragraph(f"Impressão: {now_str}", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer