# Main.py
"""
Versão integrada do arquivo principal com suporte
for lambda calibration.
"""

import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import logging
import os
import pandas as pd

# Calibration module
from calibration import (
    run_calibration,
    get_current_lambda,
    analyze_consonance_vs_lambda,
    visualize_decay_function,
    test_calibrated_model,
)

# Importações originais mantidas
from gui_components import DensityCalculatorGUI
from gui.controllers.analysis_controller import AnalysisController
from validation.gui_validation import generate_validation_text
from plot_metr_espectrais import extract_and_plot_metrics
from statistical_validation import (
    validate_metrics_reliability,
    create_metrics_profile,
    plot_metrics_comparison,
)
import logging_config  # noqa: F401  (mantém o side-effect)

# Importar módulos de utilidades
from utils.serialize_utils import ensure_directory_exists, log_execution_time

# Importar tratamento de erros (ajusta para o módulo correto, se diferente)
from error_handler import (
    handle_exceptions,
    init_global_exception_hook,
    InputError,
)

# Importar configurações
from config import DEFAULT_OUTPUT_DIRECTORY

# Configurar logging
logger = logging.getLogger('main')

class DensityAnalyzerApp:
    """
    Classe principal da aplicação de análise de densidade musical.
    Integra interface gráfica com funcionalidades de processamento e calibração.
    """
    
    def __init__(self, root):
        """
        Inicializa a aplicação.
        
        Args:
            root: O widget raiz tkinter
        """
        self.root = root
        
        # Inicializar tratamento global de exceções
        init_global_exception_hook()
        
        # Garantir que o diretório de saída existe
        ensure_directory_exists(DEFAULT_OUTPUT_DIRECTORY)
        
        # Lista para armazenar histórico de resultados para validação
        self.resultados_historicos = []
        
        # Armazenar resultados completos para geração de relatórios
        self.resultados_completos = None
        
        # Armazenar último input_data para uso em visualizações
        self._last_input_data = {}
        
        # Criar callbacks para a interface
        callbacks = {
            "calculate": self.calcular,
            "clear": self.limpar,
            "generate_report": self.gerar_relatorio_cientifico,
            "execute_validation": self.executar_validacao,
            "calibrate": self.calibrar_lambda,
            "load_xml": self.carregar_xml,
            "load_midi": self.carregar_midi,
        }
        
        # Inicializar a interface
        self.gui = DensityCalculatorGUI(root, callbacks)
        
        # Adicionar opção de calibração ao menu
        self._adicionar_menu_calibracao()
    
    def _adicionar_menu_calibracao(self):
        """Add a menu for calibration and analysis."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu de arquivo
        filemenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Quit", command=self.root.quit)
        
        # Menu de ferramentas
        toolsmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=toolsmenu)
        
        # Submenu de calibração
        calibmenu = tk.Menu(toolsmenu, tearoff=0)
        toolsmenu.add_cascade(label="Calibration", menu=calibmenu)
        
        # Opções de calibração
        calibmenu.add_command(label="Calibrate Lambda", command=self.calibrar_lambda)
        calibmenu.add_command(label="Visualize Decay Function",
                              command=lambda: visualize_decay_function(get_current_lambda()))
        calibmenu.add_command(label="Test Calibrated Model",
                              command=test_calibrated_model)
        calibmenu.add_command(label="Analyze Lambda Effect",
                              command=lambda: analyze_consonance_vs_lambda())
        
    
    @handle_exceptions(show_dialog=True)
    def calibrar_lambda(self):
        """
        Open a dialog to calibrate the lambda parameter.
        """
        # Criar janela de diálogo
        dialog = tk.Toplevel(self.root)
        dialog.title("Lambda Calibration")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Mostrar valor atual
        lambda_atual = get_current_lambda()
        tk.Label(dialog, text=f"Current lambda: {lambda_atual:.4f}",
                font=("Arial", 12)).pack(pady=10)

        tk.Button(dialog, text="Calibrate with Default Data",
                 command=lambda: self._executar_calibracao(dialog)).pack(pady=5)
        tk.Button(dialog, text="Visualize Current Function",
                 command=lambda: visualize_decay_function(lambda_atual)).pack(pady=5)
        tk.Button(dialog, text="Test Current Model",
                 command=test_calibrated_model).pack(pady=5)
        tk.Button(dialog, text="Sensitivity Analysis",
                 command=lambda: analyze_consonance_vs_lambda()).pack(pady=5)
        
        # Opção para inserir lambda manualmente
        tk.Label(dialog, text="Or enter a value manually:").pack(pady=5)
        
        entry_frame = tk.Frame(dialog)
        entry_frame.pack(pady=5)
        
        lambda_entry = tk.Entry(entry_frame, width=10)
        lambda_entry.pack(side=tk.LEFT, padx=5)
        lambda_entry.insert(0, str(lambda_atual))
        
        tk.Button(entry_frame, text="Set",
                 command=lambda: self._definir_lambda_manual(dialog, lambda_entry.get())).pack(side=tk.LEFT)
        tk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    def _executar_calibracao(self, dialog):
        """Executa a calibração e fecha o diálogo."""
        lambda_otimizado = run_calibration()
        dialog.destroy()
        tk.messagebox.showinfo("Calibration Complete",
                              f"Calibration completed successfully.\nNew lambda: {lambda_otimizado:.4f}")
    
    def _definir_lambda_manual(self, dialog, valor_texto):
        """Define o valor de lambda manualmente."""
        try:
            valor = float(valor_texto)
            if 0.01 <= valor <= 1.0:
                from calibration import save_calibrated_parameters
                save_calibrated_parameters({'lambda': valor})
                dialog.destroy()
                tk.messagebox.showinfo("Lambda Set", f"Lambda set to: {valor:.4f}")
            else:
                tk.messagebox.showerror("Error", "Value must be between 0.01 and 1.0")
        except ValueError:
            tk.messagebox.showerror("Error", "Enter a valid number")
    
    @handle_exceptions(show_dialog=True)
    def _plot_detailed_visualizations(self, notas, instrumentos, numeros_instrumentos, densidades_instrumento, pitches):
        """
        Plota visualizações detalhadas dos resultados (exceto os 3 gráficos de orquestração).
        """
        # Extrair e plotar métricas espectrais
        extract_and_plot_metrics(
            notas, instrumentos, numeros_instrumentos,
            densidades_instrumento
        )

        input_data = getattr(self, '_last_input_data', {})
        show_graphs = input_data.get('show_graphs', True)

        # Espectrograma de densidade espectral
        if self.resultados_completos and show_graphs:
            try:
                from plot_spectrogram import plot_spectrogram_density
                from microtonal import hz_to_midi

                if pitches and densidades_instrumento and len(pitches) == len(densidades_instrumento):
                    plot_spectrogram_density(
                        pitches=pitches,
                        densities=densidades_instrumento,
                        notes=notas,
                        instruments=instrumentos,
                        title="Spectral Density Spectrogram",
                    )
                else:
                    logger.warning(
                        "Invalid data for spectrogram: pitches=%s, densities=%s",
                        len(pitches),
                        len(densidades_instrumento),
                    )
            except Exception as e:
                logger.error(f"Error creating spectrogram: {e}", exc_info=True)

        # Comparação de métricas
        if self.resultados_completos:
            profile_df = create_metrics_profile(
                self.resultados_completos['spectral_moments'],
                self.resultados_completos['texture'],
                self.resultados_completos['timbre']
            )
            if len(profile_df.columns) > 2:
                plot_metrics_comparison(profile_df, "Musical Metrics Analysis")

    @handle_exceptions(show_dialog=True)
    def limpar(self):
        """Limpa todos os campos de entrada e resultados."""
        self.gui.clear_inputs()
        self.resultados_completos = None

    @handle_exceptions(show_dialog=True)
    def carregar_xml(self):
        """Abre um ficheiro XML e preenche a interface com notas, instrumentos, dinâmicas e opções."""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Load density analysis",
            filetypes=[("XML", "*.xml"), ("Todos", "*.*")],
            defaultextension=".xml",
            initialdir=os.getcwd(),
        )
        if not path:
            return
        try:
            from xml_loader import parse_xml
            data = parse_xml(path)
            if data.get("lambda") is not None:
                try:
                    from calibration import save_calibrated_parameters
                    save_calibrated_parameters({"lambda": float(data["lambda"])})
                    logger.info(f"Lambda do XML aplicado: {data['lambda']}")
                except Exception as e:
                    logger.warning(f"Não foi possível aplicar lambda do XML: {e}")
            self.gui.load_from_xml_data(data)
            tk.messagebox.showinfo("XML loaded", f"File loaded with {len(data['notes'])} voice(s).")
        except Exception as e:
            logger.error(f"Error loading XML: {e}", exc_info=True)
            tk.messagebox.showerror("Error loading XML", str(e))

    @handle_exceptions(show_dialog=True)
    def carregar_midi(self):
        """Abre um ficheiro MIDI e preenche a interface com notas e dinâmicas (velocity -> dynamic)."""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Load MIDI",
            filetypes=[("MIDI", "*.mid;*.midi"), ("Todos", "*.*")],
            defaultextension=".mid",
            initialdir=os.getcwd(),
        )
        if not path:
            return
        try:
            from midi_loader import parse_midi
            data = parse_midi(path)
            self.gui.load_from_xml_data(data)
            tk.messagebox.showinfo("MIDI loaded", f"File loaded with {len(data['notes'])} note(s).")
        except Exception as e:
            logger.error(f"Error loading MIDI: {e}", exc_info=True)
            tk.messagebox.showerror("Error loading MIDI", str(e))

    @handle_exceptions(show_dialog=True)
    @log_execution_time
    def calcular(self):
        """
        Executa os cálculos de métricas com base nos dados de entrada.
        """
        # Obter dados de entrada
        input_data = self.gui.get_input_data()
    
        # Validar entrada básica
        if not input_data['notes']:
            raise InputError("No notes selected. Check at least one note.")
    
        logger.info(f"Starting calculation with notes: {input_data['notes']}")
    
        resultados, densidades_instrumento, pitches = AnalysisController.analyze(input_data)
    
        # Armazenar resultados para histórico e relatórios
        self.resultados_completos = resultados
        self.resultados_historicos.append(resultados)
    
        # Formatar e exibir resultados
        output_text = AnalysisController.format_results(resultados)
        self.gui.show_results(output_text)
    
        # Atualizar a árvore de métricas
        self.gui.update_metrics_tree(resultados)
    
        # Criar gráficos embutidos
        self.gui.create_embedded_graphs(pitches, densidades_instrumento)

        # Mostrar gráficos detalhados (exceto os 3 de orquestração)
        self._last_input_data = input_data
        if input_data['show_graphs']:
            self._plot_detailed_visualizations(
                input_data['notes'],
                input_data['instruments'],
                input_data['num_instruments'],
                densidades_instrumento,
                pitches
            )
    
        # Se solicitado, salvar resultados
        if input_data['save_results']:
            try:
                # Criar nome de arquivo com timestamp para evitar sobrescrita
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
                # Garantir que o diretório existe
                import os
                from config import DEFAULT_OUTPUT_DIRECTORY
                if not os.path.exists(DEFAULT_OUTPUT_DIRECTORY):
                    os.makedirs(DEFAULT_OUTPUT_DIRECTORY, exist_ok=True)
                
                # Gerar caminho completo
                output_file = os.path.join(DEFAULT_OUTPUT_DIRECTORY, f"resultados_{timestamp}.json")
            
                # Salvar usando a função centralizada
                from score_io.exporters import write_results_json
                arquivo_salvo = write_results_json(resultados, output_file)
            
                if arquivo_salvo:
                    from tkinter import messagebox
                    messagebox.showinfo("Info", f"Results saved successfully to:\n{arquivo_salvo}")
                    logger.info(f"File saved successfully to: {arquivo_salvo}")
                else:
                    logger.warning("save_results did not return a valid path")
            except Exception as e:
                logger.error(f"Error saving results: {e}", exc_info=True)
                from tkinter import messagebox
                messagebox.showerror("Error", f"Error saving results: {str(e)}")
    
        return resultados
    
    @handle_exceptions(show_dialog=True)
    @log_execution_time
    def executar_validacao(self):
        """Executa análise de validação estatística nos resultados históricos."""
        if len(self.resultados_historicos) < 5:  # Verificar quantidade mínima de amostras
            raise InputError(
                "At least 5 result sets are required for statistical validation.",
                f"Currently have {len(self.resultados_historicos)} sets."
            )
        
        # Extrair métricas do histórico
        metricas_extraidas = {}
        
        # Usar conjunto de primeira ordem (métricas diretas)
        for resultado in self.resultados_historicos:
            for categoria, valores in resultado.items():
                if categoria not in ["input_data"]:
                    for metrica, valor in valores.items():
                        if isinstance(valor, (int, float)) and not np.isnan(valor) and not np.isinf(valor):
                            chave = f"{categoria}.{metrica}"
                            if chave not in metricas_extraidas:
                                metricas_extraidas[chave] = []
                            metricas_extraidas[chave].append(valor)
        
        # Analisar correlações entre métricas
        df_metricas = pd.DataFrame({k: v for k, v in metricas_extraidas.items() 
                                   if len(v) == len(self.resultados_historicos)})
        
        if df_metricas.shape[1] < 2:
            raise InputError("Not enough metrics for correlation analysis.")
        
        # Executar validação
        resultados_validacao = validate_metrics_reliability(df_metricas)
        
        # Gerar texto de validação
        texto_validacao = generate_validation_text(resultados_validacao, len(self.resultados_historicos))
        
        # Exibir resultados
        self.gui.show_validation_results(texto_validacao)
        
        # Exibir gráfico da matriz de correlação
        plt.figure(figsize=(10, 8))
        import seaborn as sns
        sns.heatmap(resultados_validacao['correlation_matrix'], annot=True, cmap='coolwarm', center=0)
        plt.title('Correlation Matrix of Metrics')
        plt.tight_layout()
        plt.show()
    
    @handle_exceptions(show_dialog=True)
    @log_execution_time
    def gerar_relatorio_cientifico(self):
        """
        Gera relatórios científicos com os resultados da análise.
        Deve ser chamado após o cálculo das métricas.
        """
        # Verificar se há resultados para gerar relatório
        if self.resultados_completos is None:
            raise InputError(
                "Calculate metrics first before generating a report."
            )
        
        # Mostrar diálogo de configuração para o relatório
        self.gui.show_report_config_dialog(self._generate_report_with_config)
    
    @handle_exceptions(show_dialog=True)
    @log_execution_time
    def _generate_report_with_config(self, config):
        """
        Gera relatórios científicos com base na configuração fornecida.
        
        Args:
            config (dict): Report configuration
        """
        from scientific_report_generator import ScientificReportGenerator
        
        # Garantir que o diretório de saída existe
        output_dir = config.get('output_directory', DEFAULT_OUTPUT_DIRECTORY)
        ensure_directory_exists(output_dir)
        
        # Inicializar gerador de relatórios
        generator = ScientificReportGenerator(output_dir)
        
        report_paths = {}
        
        # Gerar relatórios selecionados
        if config['formats']['pdf']:
            pdf_path = generator.generate_pdf_report(self.resultados_completos, config)
            report_paths['pdf'] = pdf_path
        
        if config['formats']['paper']:
            paper_path = generator.generate_scientific_paper(self.resultados_completos, config)
            report_paths['paper'] = paper_path
        
        if config['formats']['figures']:
            figures_dir = generator.generate_publication_figures(self.resultados_completos, config)
            report_paths['figures'] = figures_dir
        
        if config['formats']['tables']:
            tables_path = generator.generate_data_tables(self.resultados_completos, config)
            report_paths['tables'] = tables_path
        
        # Mostrar resultados
        result_text = "Reports generated:\n\n"
        for tipo, caminho in report_paths.items():
            if caminho:
                if tipo == 'pdf':
                    result_text += f"PDF report: {os.path.basename(caminho)}\n"
                elif tipo == 'paper':
                    result_text += f"Scientific paper: {os.path.basename(caminho)}\n"
                elif tipo == 'figures':
                    result_text += f"Publication figures: {os.path.basename(caminho)}\n"
                elif tipo == 'tables':
                    result_text += f"Data tables: {os.path.basename(caminho)}\n"
        result_text += f"\nSaved in: {output_dir}"
        
        # Mostrar mensagem com resultados
        tk.messagebox.showinfo("Reports Generated", result_text)


# Ponto de entrada principal
if __name__ == "__main__":
    # Criar a janela principal
    root = tk.Tk()
    
    # Definir um tamanho inicial maior para garantir que todos os campos sejam visíveis
    root.geometry("1200x700")
    
    app = DensityAnalyzerApp(root)
    
    # Iniciar o loop principal da aplicação
    root.mainloop()

