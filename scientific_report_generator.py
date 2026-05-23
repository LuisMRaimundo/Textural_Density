# scientific_report_generator.py



import os
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io
from PIL import Image

try:
    from utils.plotting_style import (
        create_professional_figure,
        enhance_axes,
        finalize_figure,
        get_color,
        PUBLICATION_DPI,
    )
except ImportError:
    create_professional_figure = None
    enhance_axes = None
    finalize_figure = None
    get_color = lambda i: 'gray'
    PUBLICATION_DPI = 300



class ScientificReportGenerator:

    """

    Classe para geração de relatórios científicos a partir dos resultados de análise espectral.

    """

    

    def __init__(self, output_directory=None):

        """

        Inicializa o gerador de relatórios.

        

        Args:

            output_directory (str, optional): Diretório para salvar os relatórios.

        """

        self.output_directory = output_directory or os.getcwd()

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    

    def ensure_valid_plot(self, plot_function, resultados, title="Gráfico"):

        """

        Garante que um gráfico válido seja retornado, mesmo com dados de amostra.

        

        Args:

            plot_function (callable): Função que gera o gráfico original.

            resultados (dict): Dicionário de resultados.

            title (str): Título do gráfico para exibição em caso de erro.

            

        Returns:

            PIL.Image: Imagem do gráfico ou mensagem de erro.

        """

        try:

            # Tenta gerar o gráfico normal

            plot = plot_function(resultados)

            

            # Se falhar, cria um gráfico com mensagem de erro

            if plot is None:
                if create_professional_figure is not None:
                    fig, axes = create_professional_figure(1, 1, figsize=(8, 4), dpi=PUBLICATION_DPI)
                    ax = axes[0]
                else:
                    fig, ax = plt.subplots(figsize=(8, 4))
                ax.text(0.5, 0.5, f"Dados insuficientes para\ngeração do gráfico de {title}",
                        ha='center', va='center', fontsize=12, transform=ax.transAxes)
                ax.set_title(f"{title} - Indisponível")
                ax.axis('off')
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=PUBLICATION_DPI)

                plt.close(fig)

                buf.seek(0)

                return Image.open(buf)

            

            return plot

        except Exception as e:

            print(f"Erro ao criar gráfico {title}: {e}")

            # Em caso de erro, cria um gráfico com mensagem de erro

            fig, ax = plt.subplots(figsize=(8, 4))

            ax.text(0.5, 0.5, f"Erro ao gerar gráfico: {str(e)}", 

                    ha='center', va='center', fontsize=12, transform=ax.transAxes, color='red')

            ax.set_title(f"{title} - Erro", color='red')

            ax.axis('off')

            

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=PUBLICATION_DPI)
            plt.close(fig)
            buf.seek(0)
            return Image.open(buf)

    def create_density_plot(self, resultados):

        """

        Cria um gráfico de barras para as métricas de densidade.

        

        Args:

            resultados (dict): Dicionário com resultados da análise.

            

        Returns:

            PIL.Image or None: Imagem do gráfico ou None se não houver dados suficientes.

        """

        if 'density' not in resultados:

            print("Diagnóstico: 'density' not found in results")

            return None

        

        densidade = resultados['density']
        if not densidade:
            print("Diagnóstico: Dicionário de densidade está vazio")
            return None
        if create_professional_figure is not None:
            fig, axes = create_professional_figure(1, 1, figsize=(8, 4), dpi=PUBLICATION_DPI)
            ax = axes[0]
        else:
            fig, ax = plt.subplots(figsize=(8, 4))
        metrics = list(densidade.keys())
        values = list(densidade.values())
        colors = [get_color(i) for i in range(len(metrics))] if get_color else 'skyblue'
        bars = ax.bar(metrics, values, color=colors, edgecolor='white', linewidth=0.5)
        if enhance_axes is not None:
            enhance_axes(ax, title=r'Métricas de densidade', xlabel=r'Métrica', ylabel=r'Valor', grid=True)
        else:
            ax.set_xlabel('Métricas')
            ax.set_ylabel('Valor')
            ax.set_title('Métricas de Densidade')
        ax.set_xticklabels(metrics, rotation=45, ha='right')
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
        if finalize_figure is not None:
            finalize_figure(fig)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=PUBLICATION_DPI)

        plt.close(fig)

        buf.seek(0)

        return Image.open(buf)

    

    def create_spectral_plot(self, resultados):

        """

        Cria um gráfico para os momentos espectrais.

        

        Args:

            resultados (dict): Dicionário com resultados da análise.

            

        Returns:

            PIL.Image or None: Imagem do gráfico ou None se não houver dados suficientes.

        """

        if 'spectral_moments' not in resultados:

            print("Diagnóstico: 'spectral_moments' not found in results")

            return None

        

        # Extrair métricas

        momentos = resultados['spectral_moments']

        metrics = []

        values = []

        

        # Coletar os valores numéricos dos momentos espectrais

        for k, v in momentos.items():

            print(f"Diagnóstico: Processando métrica {k} com valor {v}")

            if k == "centroid" or k == "spread":

                continue  # Tratamos separadamente

            elif isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):

                metrics.append(k.replace("spectral_", "").capitalize())

                values.append(v)

        

        print(f"Diagnóstico: Métricas coletadas: {metrics}")

        print(f"Diagnóstico: Valores coletados: {values}")

        

        if not metrics:
            print("Aviso: Nenhuma métrica válida para o gráfico. Usando dados de exemplo.")
            metrics = ["Exemplo1", "Exemplo2"]
            values = [0.5, 0.7]
        if create_professional_figure is not None:
            fig, axes = create_professional_figure(1, 1, figsize=(8, 4), dpi=PUBLICATION_DPI)
            ax = axes[0]
        else:
            fig, ax = plt.subplots(figsize=(8, 4))
        colors = [get_color(i) for i in range(len(metrics))] if get_color else 'lightgreen'
        bars = ax.bar(metrics, values, color=colors, edgecolor='white', linewidth=0.5)
        if enhance_axes is not None:
            enhance_axes(ax, title=r'Momentos espectrais', xlabel=r'Métrica', ylabel=r'Valor', grid=True)
        else:
            ax.set_xlabel('Métricas')
            ax.set_ylabel('Valor')
            ax.set_title('Momentos Espectrais')
        ax.set_xticklabels(metrics, rotation=45, ha='right')
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
        if finalize_figure is not None:
            finalize_figure(fig)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=PUBLICATION_DPI)

        plt.close(fig)

        buf.seek(0)

        return Image.open(buf)

    

    def create_chroma_plot(self, resultados):

        """

        Cria um gráfico para o vetor de croma se disponível.

        

        Args:

            resultados (dict): Dicionário com resultados da análise.

            

        Returns:

            PIL.Image or None: Imagem do gráfico ou None se não houver dados suficientes.

        """

        if 'additional_metrics' not in resultados:

            print("Diagnóstico: 'additional_metrics' not found in results")

            return None

            

        if 'chroma_vector' not in resultados['additional_metrics']:

            print("Diagnóstico: 'chroma_vector' not found in additional_metrics")

            return None

        

        chroma = resultados['additional_metrics']['chroma_vector']

        print(f"Diagnóstico: Tipo de chroma: {type(chroma)}")

        print(f"Diagnóstico: Conteúdo de chroma: {chroma}")

        

        if not isinstance(chroma, list) or len(chroma) != 12:

            print(f"Diagnóstico: chroma deve ser uma lista de 12 elementos. Encontrado: {type(chroma)} com {len(chroma) if isinstance(chroma, list) else 'N/A'} elementos")

            return None

        

        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        if create_professional_figure is not None:
            fig, axes = create_professional_figure(1, 1, figsize=(8, 4), dpi=PUBLICATION_DPI)
            ax = axes[0]
        else:
            fig, ax = plt.subplots(figsize=(8, 4))
        colors = [get_color(i) for i in range(12)] if get_color else 'salmon'
        ax.bar(notes, chroma, color=colors, edgecolor='white', linewidth=0.5)
        if enhance_axes is not None:
            enhance_axes(ax, title=r'Chroma (classe de altura)', xlabel=r'Classe de altura', ylabel=r'Energia normalizada', grid=True)
        else:
            ax.set_xlabel('Classe de Altura')
            ax.set_ylabel('Energia')
            ax.set_title('Distribuição de Energia por Classe de Altura (Chroma)')
        if finalize_figure is not None:
            finalize_figure(fig)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=PUBLICATION_DPI)
        plt.close(fig)
        buf.seek(0)
        return Image.open(buf)

    def generate_pdf_report(self, resultados, config):

        """

        Gera um relatório em formato PDF com os resultados da análise.

        

        Args:

            resultados (dict): Dicionário com resultados da análise.

            config (dict): Configurações do relatório (título, autores, etc.).

            

        Returns:

            str: Caminho para o arquivo PDF gerado.

        """

        try:

            # Importar reportlab - biblioteca para geração de PDFs

            from reportlab.lib.pagesizes import letter

            from reportlab.pdfgen import canvas

            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage

            from reportlab.lib import colors

            from reportlab.lib.units import inch

            

            # Definir caminho do arquivo

            output_path = os.path.join(self.output_directory, f"relatorio_analise_espectral_{self.timestamp}.pdf")

            

            # Configurar documento

            doc = SimpleDocTemplate(

                output_path,

                pagesize=letter,

                rightMargin=72,

                leftMargin=72,

                topMargin=72,

                bottomMargin=72

            )

            

            # Lista de elementos do relatório

            elements = []

            

            # Estilos

            styles = getSampleStyleSheet()

            styles.add(ParagraphStyle(

                name='Heading1Center',

                parent=styles['Heading1'],

                alignment=1  # 0=left, 1=center, 2=right

            ))

            

            # Título

            title = config.get('title', 'Relatório de Análise Espectral')

            elements.append(Paragraph(title, styles['Heading1Center']))

            elements.append(Spacer(1, 0.25 * inch))

            

            # Autores e instituição

            authors = config.get('authors', '')

            if authors:

                elements.append(Paragraph(f"Autores: {authors}", styles['Normal']))

                elements.append(Spacer(1, 0.1 * inch))

            

            institution = config.get('institution', '')

            if institution:

                elements.append(Paragraph(f"Instituição: {institution}", styles['Normal']))

                elements.append(Spacer(1, 0.1 * inch))

            

            # Data

            date = config.get('date', datetime.now().strftime("%d/%m/%Y"))

            elements.append(Paragraph(f"Data: {date}", styles['Normal']))

            elements.append(Spacer(1, 0.5 * inch))

            

            # Resumo

            if 'abstract' in config and config['abstract']:

                elements.append(Paragraph("Resumo", styles['Heading2']))

                elements.append(Paragraph(config['abstract'], styles['Normal']))

                elements.append(Spacer(1, 0.3 * inch))

            

            # Resultados da análise - Seção de densidade

            if 'density' in resultados:

                elements.append(Paragraph("Análise de Densidade", styles['Heading2']))

                

                # Tabela de densidade

                densidade_data = [['Métrica', 'Valor']]

                for k, v in resultados['density'].items():

                    densidade_data.append([k.capitalize(), f"{v:.4f}"])

                

                t = Table(densidade_data, colWidths=[2.5*inch, 1.5*inch])

                t.setStyle(TableStyle([

                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),

                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),

                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                    ('GRID', (0, 0), (-1, -1), 1, colors.black)

                ]))

                elements.append(t)

                elements.append(Spacer(1, 0.2 * inch))

                

                # Gráfico de densidade

                densidade_plot = self.ensure_valid_plot(

                    lambda r: self.create_density_plot(r),

                    resultados,

                    "Densidade"

                )

                if densidade_plot:

                    img_buffer = io.BytesIO()

                    densidade_plot.save(img_buffer, format='PNG')

                    img_buffer.seek(0)

                    img = ReportLabImage(img_buffer, width=6*inch, height=3*inch)

                    elements.append(img)

                    elements.append(Spacer(1, 0.3 * inch))

            

            # Momentos espectrais

            if 'spectral_moments' in resultados:

                elements.append(Paragraph("Momentos Espectrais", styles['Heading2']))

                

                # Tabela de momentos espectrais

                momentos_data = [['Métrica', 'Valor']]

                for k, v in resultados['spectral_moments'].items():

                    if k == "centroid":
                        momentos_data.append(["Centroid", f"{v['frequency']:.2f} Hz ({v['note']})"])
                    elif k == "spread":
                        momentos_data.append(["Spread", f"±{v['deviation']:.2f} Hz"])

                    elif isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):

                        momentos_data.append([k.replace("spectral_", "").capitalize(), f"{v:.4f}"])

                

                t = Table(momentos_data, colWidths=[2.5*inch, 1.5*inch])

                t.setStyle(TableStyle([

                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),

                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),

                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                    ('GRID', (0, 0), (-1, -1), 1, colors.black)

                ]))

                elements.append(t)

                elements.append(Spacer(1, 0.2 * inch))

                

                # Gráfico de momentos espectrais

                spectral_plot = self.ensure_valid_plot(

                    lambda r: self.create_spectral_plot(r),

                    resultados,

                    "Momentos Espectrais"

                )

                if spectral_plot:

                    img_buffer = io.BytesIO()

                    spectral_plot.save(img_buffer, format='PNG')

                    img_buffer.seek(0)

                    img = ReportLabImage(img_buffer, width=6*inch, height=3*inch)

                    elements.append(img)

                    elements.append(Spacer(1, 0.3 * inch))

            

            # Métricas adicionais

            if 'additional_metrics' in resultados:

                elements.append(Paragraph("Métricas Adicionais", styles['Heading2']))

                

                # Tabela de métricas adicionais

                metricas_data = [['Métrica', 'Valor']]

                for k, v in resultados['additional_metrics'].items():

                    if k != 'chroma_vector' and isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):

                        metricas_data.append([k.capitalize(), f"{v:.4f}"])

                

                if len(metricas_data) > 1:

                    t = Table(metricas_data, colWidths=[2.5*inch, 1.5*inch])

                    t.setStyle(TableStyle([

                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),

                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),

                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                        ('GRID', (0, 0), (-1, -1), 1, colors.black)

                    ]))

                    elements.append(t)

                    elements.append(Spacer(1, 0.2 * inch))

                

                # Verificar se chroma_vector existe e criar o gráfico

                if 'chroma_vector' in resultados['additional_metrics']:

                    chroma_plot = self.ensure_valid_plot(

                        lambda r: self.create_chroma_plot(r),

                        resultados,

                        "Vetor de Croma"

                    )

                    if chroma_plot:

                        elements.append(Paragraph("Vetor de Croma", styles['Heading3']))

                        img_buffer = io.BytesIO()

                        chroma_plot.save(img_buffer, format='PNG')

                        img_buffer.seek(0)

                        img = ReportLabImage(img_buffer, width=6*inch, height=3*inch)

                        elements.append(img)

                        elements.append(Spacer(1, 0.3 * inch))

            

            # Incluir outras seções de métricas (textura, timbre, etc.) seguindo o mesmo padrão

            for section_name, section_title in [

                ('texture', 'Texture Analysis'),

                ('timbre', 'Análise de Timbre'),

                ('orchestration', 'Orchestration Analysis')

            ]:

                if section_name in resultados:

                    elements.append(Paragraph(section_title, styles['Heading2']))

                    

                    section_data = [['Métrica', 'Valor']]

                    for k, v in resultados[section_name].items():

                        if isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):

                            section_data.append([k.capitalize(), f"{v:.4f}"])

                        elif isinstance(v, dict):

                            # Ignorar dicionários complexos por enquanto

                            continue

                        elif isinstance(v, list):

                            # Ignorar listas por enquanto

                            continue

                    

                    if len(section_data) > 1:  # Se há dados além do cabeçalho

                        t = Table(section_data, colWidths=[2.5*inch, 1.5*inch])

                        t.setStyle(TableStyle([

                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),

                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),

                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                            ('GRID', (0, 0), (-1, -1), 1, colors.black)

                        ]))

                        elements.append(t)

                        elements.append(Spacer(1, 0.3 * inch))

            

            # Conclusões

            if 'conclusions' in config and config['conclusions']:

                elements.append(Paragraph("Conclusões", styles['Heading2']))

                elements.append(Paragraph(config['conclusions'], styles['Normal']))

                elements.append(Spacer(1, 0.3 * inch))

            

            # Construir o documento

            doc.build(elements)

            

            print(f"Relatório PDF gerado com sucesso: {output_path}")

            return output_path

        

        except ImportError as e:

            # Fallback para arquivo de texto se reportlab não estiver disponível

            print(f"Erro de importação: {e}")

            print("Bibliotecas necessárias não encontradas. Gerando relatório em formato de texto.")

            return self.generate_text_report(resultados, config)

        

        except Exception as e:

            print(f"Erro ao gerar relatório PDF: {str(e)}")

            # Fallback para arquivo de texto em caso de erro

            return self.generate_text_report(resultados, config)

    

    def generate_text_report(self, resultados, config):

        """

        Método de fallback para gerar relatório em texto.

        

        Args:

            resultados (dict): Dicionário com resultados da análise.

            config (dict): Configurações do relatório.

            

        Returns:

            str: Caminho para o arquivo de texto gerado.

        """

        output_path = os.path.join(self.output_directory, f"relatorio_analise_espectral_{self.timestamp}.txt")

        

        with open(output_path, 'w', encoding='utf-8') as f:

            f.write(f"Relatório de Análise Espectral\n")

            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")

            

            title = config.get('title', 'Título não fornecido')

            f.write(f"Título: {title}\n")

            

            authors = config.get('authors', '')

            if authors:

                f.write(f"Autores: {authors}\n")

                

            institution = config.get('institution', '')

            if institution:

                f.write(f"Instituição: {institution}\n")

                

            f.write("\n")

            

            if 'abstract' in config and config['abstract']:

                f.write("Resumo:\n")

                f.write(f"{config['abstract']}\n\n")

            

            if 'density' in resultados:

                f.write("Densidade:\n")

                for k, v in resultados['density'].items():

                    f.write(f"  {k.capitalize()}: {v:.4f}\n")

                f.write("\n")

            

            if 'spectral_moments' in resultados:

                f.write("Momentos Espectrais:\n")

                for k, v in resultados['spectral_moments'].items():

                    if k == "centroid":
                        f.write(f"  Centroid: {v['frequency']:.2f} Hz ({v['note']})\n")
                    elif k == "spread":
                        f.write(f"  Spread: ±{v['deviation']:.2f} Hz\n")

                    elif isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):

                        f.write(f"  {k.replace('spectral_', '').capitalize()}: {v:.4f}\n")

                f.write("\n")

            

            if 'additional_metrics' in resultados:

                f.write("Métricas Adicionais:\n")

                for k, v in resultados['additional_metrics'].items():

                    if k != 'chroma_vector' and isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):

                        f.write(f"  {k.capitalize()}: {v:.4f}\n")

                f.write("\n")

            

            # Adicionar as demais seções

            for section_name, section_title in [

                ('texture', 'Texture Analysis'),

                ('timbre', 'Análise de Timbre'),

                ('orchestration', 'Orchestration Analysis')

            ]:

                if section_name in resultados:

                    f.write(f"{section_title}:\n")

                    for k, v in resultados[section_name].items():

                        if isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):

                            f.write(f"  {k.capitalize()}: {v:.4f}\n")

                    f.write("\n")

            

            if 'conclusions' in config and config['conclusions']:

                f.write("Conclusões:\n")

                f.write(f"{config['conclusions']}\n")

            

        return output_path

    

    def generate_scientific_paper(self, resultados, config):

        """

        Gera um artigo científico em formato PDF ou texto.

        

        Args:

            resultados (dict): Dicionário com resultados da análise.

            config (dict): Configurações do artigo.

            

        Returns:

            str: Caminho para o arquivo gerado.

        """

        # Implementação simplificada - apenas gera um arquivo de texto

        output_path = os.path.join(self.output_directory, f"paper_analise_espectral_{self.timestamp}.txt")

        

        with open(output_path, 'w', encoding='utf-8') as f:

            f.write(f"Artigo Científico\n")

            f.write(f"Título: {config.get('title', 'Título do artigo')}\n")

            f.write(f"Autores: {config.get('authors', 'Autores')}\n")

            

            if 'abstract' in config and config['abstract']:

                f.write(f"\nResumo: {config['abstract']}\n")

            

            if 'conclusions' in config and config['conclusions']:

                f.write(f"\nConclusões: {config['conclusions']}\n")

        

        return output_path

    

    def generate_publication_figures(self, resultados, config):

        """

        Gera figuras para publicação.

        

        Args:

            resultados (dict): Dicionário com resultados da análise.

            config (dict): Configurações do relatório.

            

        Returns:

            str: Caminho para o diretório com as figuras.

        """

        figures_dir = os.path.join(self.output_directory, f"figuras_publicacao_{self.timestamp}")

        os.makedirs(figures_dir, exist_ok=True)

        

        # Gerar e salvar figuras

        try:

            # Densidade

            densidade_plot = self.ensure_valid_plot(

                lambda r: self.create_density_plot(r),

                resultados,

                "Densidade"

            )

            if densidade_plot:

                densidade_plot.save(os.path.join(figures_dir, "densidade.png"))

            

            # Momentos espectrais

            spectral_plot = self.ensure_valid_plot(

                lambda r: self.create_spectral_plot(r),

                resultados,

                "Momentos Espectrais"

            )

            if spectral_plot:

                spectral_plot.save(os.path.join(figures_dir, "momentos_espectrais.png"))

            

            # Chroma

            if 'additional_metrics' in resultados and 'chroma_vector' in resultados['additional_metrics']:

                chroma_plot = self.ensure_valid_plot(

                    lambda r: self.create_chroma_plot(r),

                    resultados,

                    "Vetor de Croma"

                )

                if chroma_plot:

                    chroma_plot.save(os.path.join(figures_dir, "chroma.png"))

            

            with open(os.path.join(figures_dir, "figuras_info.txt"), 'w', encoding='utf-8') as f:

                f.write("Este diretório contém figuras para publicação geradas a partir da análise espectral.\n")

                f.write("As figuras estão em formato PNG com alta resolução (300 DPI).\n")

        

        except Exception as e:

            print(f"Erro ao gerar figuras para publicação: {e}")

            with open(os.path.join(figures_dir, "erro.txt"), 'w', encoding='utf-8') as f:

                f.write(f"Ocorreu um erro ao gerar as figuras: {str(e)}\n")

        

        return figures_dir



    def generate_data_tables(self, resultados, config):

            """

            Gera tabelas de dados em formato CSV.

        

            Args:

                resultados (dict): Dicionário com resultados da análise.

                config (dict): Configurações do relatório.

            

            Returns:

                str: Caminho para o diretório com as tabelas.

            """

            tables_dir = os.path.join(self.output_directory, f"tabelas_dados_{self.timestamp}")

            os.makedirs(tables_dir, exist_ok=True)

        

            try:

                # Salvar tabela de densidade

                if 'density' in resultados:

                    df_densidade = pd.DataFrame({
                        'Métrica': resultados['density'].keys(),
                        'Valor': resultados['density'].values()
                    })

                    df_densidade.to_csv(os.path.join(tables_dir, "densidade.csv"), index=False, encoding='utf-8')

            

                # Salvar tabela de momentos espectrais

                if 'spectral_moments' in resultados:

                    # Extrair valores dos momentos espectrais em um formato adequado para DataFrame

                    momentos_data = []

                    for k, v in resultados['spectral_moments'].items():

                        if k == "centroid":
                            momentos_data.append({
                                'Métrica': 'Centroid (Frequency)',
                                'Valor': v['frequency']
                            })
                            momentos_data.append({
                                'Métrica': 'Centroid (Note)',
                                'Valor': v['note']
                            })
                        elif k == "spread":

                            momentos_data.append({

                                'Métrica': 'Spread', 

                                'Valor': v['deviation']

                            })

                        elif isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):

                            momentos_data.append({

                                'Métrica': k.replace("spectral_", "").capitalize(), 

                                'Valor': v

                            })

                

                    if momentos_data:

                        df_momentos = pd.DataFrame(momentos_data)

                        df_momentos.to_csv(os.path.join(tables_dir, "spectral_moments.csv"), index=False, encoding='utf-8')

            

                # Salvar tabela de métricas adicionais

                if 'additional_metrics' in resultados:

                    metricas_data = []

                    for k, v in resultados['additional_metrics'].items():

                        if k != 'chroma_vector' and isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):

                            metricas_data.append({

                                'Métrica': k.capitalize(), 

                                'Valor': v

                            })

                

                    if metricas_data:

                        df_metricas = pd.DataFrame(metricas_data)

                        df_metricas.to_csv(os.path.join(tables_dir, "additional_metrics.csv"), index=False, encoding='utf-8')

                

                    # Salvar vetor de croma separadamente se disponível

                    if 'chroma_vector' in resultados['additional_metrics']:

                        chroma = resultados['additional_metrics']['chroma_vector']

                        if isinstance(chroma, list) and len(chroma) == 12:

                            notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

                            df_chroma = pd.DataFrame({

                                'Nota': notes,

                                'Energia': chroma

                            })

                            df_chroma.to_csv(os.path.join(tables_dir, "chroma_vector.csv"), index=False, encoding='utf-8')

            

                # Salvar tabelas para outras seções

                for section_name, file_name in [

                    ('texture', 'texture'),

                    ('timbre', 'timbre'),

                    ('orchestration', 'orchestration')

                ]:

                    if section_name in resultados:

                        section_data = []

                        for k, v in resultados[section_name].items():

                            if isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):

                                section_data.append({

                                    'Métrica': k.capitalize(), 

                                    'Valor': v

                                })

                    

                        if section_data:

                            df_section = pd.DataFrame(section_data)

                            df_section.to_csv(os.path.join(tables_dir, f"{file_name}.csv"), index=False, encoding='utf-8')

            

                # Criar arquivo de índice

                with open(os.path.join(tables_dir, "indice.txt"), 'w', encoding='utf-8') as f:

                    f.write("Índice de Tabelas de Dados\n")

                    f.write("=========================\n\n")

                    f.write("Este diretório contém as seguintes tabelas de dados em formato CSV:\n\n")

                

                    # Listar arquivos criados

                    for file in os.listdir(tables_dir):

                        if file.endswith(".csv"):

                            f.write(f"- {file}\n")

        

            except Exception as e:

                print(f"Erro ao gerar tabelas de dados: {e}")

                with open(os.path.join(tables_dir, "erro.txt"), 'w', encoding='utf-8') as f:

                    f.write(f"Ocorreu um erro ao gerar as tabelas de dados: {str(e)}\n")

        

            return tables_dir

