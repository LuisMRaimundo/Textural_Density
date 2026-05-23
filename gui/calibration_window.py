"""Lambda calibration window (legacy helper; Main uses calibration menu)."""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from calibration import get_current_lambda, run_calibration
from densidade_intervalar import CONSONANCE_RATINGS, analyze_consonance_vs_lambda


def abrir_janela_calibracao(root: tk.Misc) -> None:
    """Open a window to calibrate the lambda parameter from experimental data."""
    calibration_window = tk.Toplevel(root)
    calibration_window.title("Parameter Calibration")
    calibration_window.geometry("800x600")

    control_frame = ttk.Frame(calibration_window)
    control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    lambda_atual = get_current_lambda()
    lambda_label = ttk.Label(control_frame, text=f"Valor atual de lambda: {lambda_atual:.4f}")
    lambda_label.pack(side=tk.LEFT, padx=5)

    plot_frame = ttk.Frame(calibration_window)
    plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

    fig, ax = plt.subplots(figsize=(8, 5))
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def atualizar_grafico() -> None:
        ax.clear()
        current = get_current_lambda()
        intervalos: list[str] = []
        valores_exp: list[float] = []
        valores_calc: list[float] = []
        for intervalo, valor_exp in CONSONANCE_RATINGS.items():
            intervalos.append(str(intervalo))
            valores_exp.append(valor_exp)
            if intervalo == 0:
                densidade = 0.0
            else:
                delta = intervalo * 2
                densidade = math.exp(-current * delta) if delta > 0 else 0.0
            max_valor = max(CONSONANCE_RATINGS.values())
            densidade_norm = 2 * (densidade / max_valor) - 1
            valores_calc.append(densidade_norm)

        bar_width = 0.35
        x = np.arange(len(intervalos))
        ax.bar(x - bar_width / 2, valores_exp, bar_width, label="Experimental", alpha=0.7)
        ax.bar(
            x + bar_width / 2,
            valores_calc,
            bar_width,
            label=f"Modelo (λ={current:.4f})",
            alpha=0.7,
        )
        ax.set_xlabel("Intervalo (semitons)")
        ax.set_ylabel("Normalised Consonance")
        ax.set_title("Experimental vs. Model Consonance")
        ax.set_xticks(x)
        ax.set_xticklabels(intervalos)
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        canvas.draw()

    atualizar_grafico()

    def calibrar_com_dados_padrao() -> None:
        try:
            run_calibration()
            current = get_current_lambda()
            lambda_label.config(text=f"Valor atual de lambda: {current:.4f}")
            atualizar_grafico()
            messagebox.showinfo("Calibration", f"Calibration complete. New lambda: {current:.4f}")
        except Exception as exc:
            messagebox.showerror("Error", f"Calibration error: {exc}")

    def definir_lambda_manual() -> None:
        try:
            valor = simpledialog.askfloat(
                "Definir Lambda",
                "Digite o valor de lambda (0.01-1.0):",
                minvalue=0.01,
                maxvalue=1.0,
            )
            if valor is not None:
                from calibration import save_calibrated_parameters

                save_calibrated_parameters({"lambda": valor})
                current = get_current_lambda()
                lambda_label.config(text=f"Valor atual de lambda: {current:.4f}")
                atualizar_grafico()
        except Exception as exc:
            messagebox.showerror("Error", f"Error setting lambda: {exc}")

    def coletar_dados_experimentais() -> None:
        try:
            data_window = tk.Toplevel(calibration_window)
            data_window.title("Experimental Data Collection")
            data_window.geometry("500x400")
            frame = ttk.Frame(data_window)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            ttk.Label(frame, text="Rate consonance for each interval (-1 to 1):").grid(
                row=0, column=0, columnspan=3, pady=10
            )
            intervalos = [
                (0, "Unison (C-C)"),
                (2, "Minor 2nd (C-C#/Db)"),
                (4, "Major 2nd (C-D)"),
                (6, "Minor 3rd (C-D#/Eb)"),
                (8, "Major 3rd (C-E)"),
                (10, "Perfect 4th (C-F)"),
                (12, "Tritone (C-F#/Gb)"),
                (14, "Perfect 5th (C-G)"),
            ]
            sliders: dict[int, tuple[ttk.Scale, tk.StringVar]] = {}
            row = 1
            for intervalo, descricao in intervalos:
                ttk.Label(frame, text=descricao).grid(
                    row=row, column=0, sticky=tk.W, padx=5, pady=5
                )
                slider = ttk.Scale(frame, from_=-1.0, to=1.0, orient=tk.HORIZONTAL, length=200)
                slider.grid(row=row, column=1, padx=5, pady=5)
                slider.set(CONSONANCE_RATINGS.get(intervalo, 0))
                var = tk.StringVar(value=f"{slider.get():.2f}")
                slider.configure(command=lambda v, var=var: var.set(f"{float(v):.2f}"))
                ttk.Label(frame, textvariable=var).grid(row=row, column=2, padx=5, pady=5)
                sliders[intervalo] = (slider, var)
                row += 1

            def calibrar_com_dados_coletados() -> None:
                dados = {intervalo: slider.get() for intervalo, (slider, _) in sliders.items()}
                data_window.destroy()
                run_calibration(dados)
                current = get_current_lambda()
                lambda_label.config(text=f"Valor atual de lambda: {current:.4f}")
                atualizar_grafico()
                messagebox.showinfo(
                    "Calibration", f"Calibration complete. New lambda: {current:.4f}"
                )

            button_frame = ttk.Frame(data_window)
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            ttk.Button(
                button_frame, text="Calibrar", command=calibrar_com_dados_coletados
            ).pack(side=tk.RIGHT, padx=5)
            ttk.Button(button_frame, text="Cancelar", command=data_window.destroy).pack(
                side=tk.RIGHT, padx=5
            )
        except Exception as exc:
            messagebox.showerror("Error", f"Error collecting data: {exc}")

    def analisar_efeito_lambda() -> None:
        try:
            analyze_consonance_vs_lambda()
        except Exception as exc:
            messagebox.showerror("Error", f"Analysis error: {exc}")

    button_frame = ttk.Frame(calibration_window)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
    ttk.Button(
        button_frame, text="Calibrate (Literature Data)", command=calibrar_com_dados_padrao
    ).pack(side=tk.LEFT, padx=5)
    ttk.Button(
        button_frame, text="Enter Experimental Data", command=coletar_dados_experimentais
    ).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Definir Lambda Manualmente", command=definir_lambda_manual).pack(
        side=tk.LEFT, padx=5
    )
    ttk.Button(button_frame, text="Analisar Efeito Lambda", command=analisar_efeito_lambda).pack(
        side=tk.LEFT, padx=5
    )
    ttk.Button(button_frame, text="Fechar", command=calibration_window.destroy).pack(
        side=tk.RIGHT, padx=5
    )


def adicionar_opcao_calibracao(root: tk.Misc, menu_principal: tk.Menu | None = None) -> None:
    """Add calibration entry to a menu or as a standalone button."""
    if menu_principal:
        menu_principal.add_command(
            label="Calibrate Parameters",
            command=lambda: abrir_janela_calibracao(root),
        )
    else:
        ttk.Button(
            root,
            text="Calibrate Parameters",
            command=lambda: abrir_janela_calibracao(root),
        ).pack(pady=10)
