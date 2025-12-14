import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ctypes
import math
import random
from PIL import Image, ImageTk
import os
import sys

# --- Configuração de Alta Resolução ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


def resource_path(relative_path):
    """ Obtém o caminho absoluto para recursos (imagens) """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class PhibApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Projeto Phib")
        self.root.geometry("900x700")

        # Estilo geral
        style = ttk.Style()
        style.theme_use('clam')

        # Correção visual do Combobox (fundo branco)
        style.map('TCombobox', fieldbackground=[('readonly', 'white')])
        style.map('TCombobox', selectbackground=[('readonly', 'white')])
        style.map('TCombobox', selectforeground=[('readonly', 'black')])

        # --- ESTRUTURA PRINCIPAL ---
        self.main_container = ttk.Frame(root)
        self.main_container.pack(side="top", fill="both", expand=True)

        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

        self.footer_frame = ttk.Frame(root, height=60)
        self.footer_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        self.setup_logo()

        # --- ABAS ---
        self.tab_perimetro = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_perimetro, text='   Perímetro   ')

        self.tab_angulo = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_angulo, text='   Ângulo Interno   ')

        self.tab_area = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_area, text='   Cálculo de Área   ')

        # Lista que guarda: (Entry, Combobox, Frame_da_Linha)
        self.inputs_lados = []
        self.setup_tab_perimetro()

    def setup_logo(self):
        try:
            img_path = resource_path("logo.png")
            if os.path.exists(img_path):
                pil_image = Image.open(img_path)
                baseheight = 40
                hpercent = (baseheight / float(pil_image.size[1]))
                wsize = int((float(pil_image.size[0]) * float(hpercent)))
                pil_image = pil_image.resize(
                    (wsize, baseheight), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(pil_image)

                lbl_logo = ttk.Label(self.footer_frame, image=self.logo_img)
                lbl_logo.pack(side="right")
        except Exception:
            pass

    def bloquear_interface(self, bloqueado=True):
        estado = "disabled" if bloqueado else "normal"
        cursor = "watch" if bloqueado else "arrow"
        try:
            if hasattr(self, 'btn_calc'):
                self.btn_calc.config(state=estado)
            if hasattr(self, 'btn_add'):
                self.btn_add.config(state=estado)
            self.root.config(cursor=cursor)
        except Exception:
            pass

    # =========================================
    # LÓGICA DO PERÍMETRO
    # =========================================
    def setup_tab_perimetro(self):
        header_frame = ttk.Frame(self.tab_perimetro)
        header_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(header_frame, text="Perímetro é a soma dos comprimentos de todos os lados de uma figura geométrica fechada.",
                  font=("Segoe UI", 12, "italic")).pack()

        self.lbl_resultado_perimetro = ttk.Label(
            header_frame,
            text="Resultado: ---",
            font=("Segoe UI", 21,"bold"),
            foreground="#333"
        )
        self.lbl_resultado_perimetro.pack(pady=10)

        self.btn_calc = tk.Button(
            header_frame,
            text="CALCULAR",
            command=self.calcular_perimetro,
            bg="#779ecb",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=20, pady=5,
            cursor="hand2"
        )
        self.btn_calc.pack(pady=5)
        self.root.bind('<Control-Return>',
                       lambda event: self.calcular_perimetro())
        self.root.bind('<Alt-F4>', lambda event: self.root.destroy())
        
        # Scroll area
        scroll_container = ttk.Frame(self.tab_perimetro)
        scroll_container.pack(fill="both", expand=True, padx=20, pady=5)

        self.canvas = tk.Canvas(scroll_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            scroll_container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botão Adicionar
        bottom_controls = ttk.Frame(self.tab_perimetro)
        bottom_controls.pack(fill='x', pady=10)

        self.btn_add = ttk.Button(
            bottom_controls, text="+ Adicionar Novo Lado",
            command=lambda: self.add_lado_input(removivel=True)
        )
        self.root.bind('<Control-=>', lambda event: self.add_lado_input())
        self.btn_add.pack(anchor="center")

        # Cria os 3 primeiros lados (NÃO removíveis)
        for _ in range(3):
            self.add_lado_input(removivel=False)

    def add_lado_input(self, removivel=True):
        """
        Adiciona uma linha. 
        removivel=False para os 3 primeiros (fixos).
        """
        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.pack(fill='x', pady=5)

        # Label dinâmica (o texto "Lado X" será atualizado se removermos algúem)
        idx = len(self.inputs_lados) + 1
        lbl = ttk.Label(
            row_frame, text=f"Lado {idx}:", width=8, font=("Segoe UI", 10))
        lbl.pack(side="left")

        entry = ttk.Entry(row_frame, width=20, font=("Segoe UI", 10))
        entry.pack(side="left", padx=5)

        # --- NOVA FUNCIONALIDADE: Enter pula para o próximo ---
        entry.bind("<Return>", self.focar_proximo_campo)
        # ----------------------------------------------------

        unidades = ['m', 'km', 'hm', 'dam', 'dm', 'cm', 'mm']
        combo = ttk.Combobox(row_frame, values=unidades,
                             width=5, state="readonly", font=("Segoe UI", 10))
        combo.set('m')
        combo.pack(side="left", padx=2)

        # Botão de Remover (Lixeira/X) - Só para os novos
        if removivel:
            btn_remove = tk.Button(
                row_frame, text="✕", bg="#ffcccc", fg="red",
                font=("Arial", 8, "bold"), relief="flat", cursor="hand2",
                command=lambda: self.remover_lado(row_frame, entry)
            )
            btn_remove.pack(side="left", padx=10)

        # Guardamos a referência completa: (Entry, Combobox, Frame, Label)
        # Precisamos da Label para renomear "Lado 4", "Lado 5" se apagarmos um do meio
        self.inputs_lados.append({
            'entry': entry,
            'combo': combo,
            'frame': row_frame,
            'label': lbl
        })

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def remover_lado(self, frame_to_remove, entry_ref):
        """Remove a linha visualmente e da lista de memória"""
        # 1. Destroi o visual
        frame_to_remove.destroy()

        # 2. Remove da lista de dados
        # Filtra a lista mantendo apenas quem NÃO é a entry removida
        self.inputs_lados = [
            item for item in self.inputs_lados if item['entry'] != entry_ref]

        # 3. Renumera as Labels (Lado 1, Lado 2...)
        for i, item in enumerate(self.inputs_lados):
            item['label'].config(text=f"Lado {i+1}:")

    def focar_proximo_campo(self, event):
        """Lógica para a tecla Enter mover o foco"""
        widget_atual = event.widget
        found = False

        for i, item in enumerate(self.inputs_lados):
            if item['entry'] == widget_atual:
                # Se não for o último, foca no próximo
                if i < len(self.inputs_lados) - 1:
                    self.inputs_lados[i+1]['entry'].focus_set()
                else:
                    # Se for o último, foca no botão calcular
                    self.btn_calc.focus_set()
                found = True
                break

    def calcular_perimetro(self):
        total_metros = 0.0
        lados_validos_count = 0
        fatores = {'km': 1000, 'hm': 100, 'dam': 10,
                   'm': 1, 'dm': 0.1, 'cm': 0.01, 'mm': 0.001}

        try:
            for item in self.inputs_lados:
                entry = item['entry']
                combo = item['combo']

                # --- TRATAMENTO DE TEXTO ---
                texto_original = entry.get().strip()

                # 1. Se vazio, IGNORA (pula para o próximo loop)
                if not texto_original:
                    continue

                # 2. Troca vírgula por ponto
                texto_corrigido = texto_original.replace(',', '.')

                safe_math = {'pi': math.pi, 'e': math.e, 'sqrt': math.sqrt}
                valor = eval(texto_corrigido, {
                             "__builtins__": None}, safe_math)
                valor_float = float(valor)

                # 3. ERRO SE FOR ZERO
                if valor_float == 0:
                    messagebox.showerror(
                        "Erro de Valor", "Um lado geométrico não pode ser 0.\nPor favor, corrija o valor.")
                    return  # Para a execução aqui

                fator = fatores[combo.get()]
                total_metros += valor_float * fator
                lados_validos_count += 1

            # 4. VERIFICAÇÃO DE MÍNIMO DE LADOS
            # O usuário pode ter 10 caixas, mas se preencher só 2, é erro.
            if lados_validos_count < 3:
                messagebox.showerror(
                    "Geometria Inválida", "Para formar um polígono fechado,\né necessário informar pelo menos 3 lados válidos.")
                return

            # Formatação do resultado
            if abs(total_metros - round(total_metros)) < 1e-9:
                texto_final = f"= {int(round(total_metros))} m"
            else:
                texto_final = f"≈ {total_metros:.6f} m".rstrip('0')

            self.lbl_resultado_perimetro.config(
                text=f"Perímetro Total {texto_final}",
                foreground="#006400"
            )

            self.disparar_confete()

        except ValueError:
            messagebox.showerror(
                "Erro de Digitação", "Por favor, insira apenas números válidos.\nUse 'pi' ou 'sqrt' se necessário.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

    # =========================================
    # SISTEMA DE CONFETES "TRANSPARENTE"
    # =========================================
    def disparar_confete(self):
        self.bloquear_interface(True)
        chroma_key_color = "#abcdef"

        self.win_confete = tk.Toplevel(self.root)
        self.win_confete.overrideredirect(True)
        self.win_confete.attributes('-topmost', True)

        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.win_confete.geometry(f"{w}x{h}+{x}+{y}")
        self.win_confete.config(bg=chroma_key_color)

        try:
            self.win_confete.wm_attributes(
                '-transparentcolor', chroma_key_color)
        except Exception:
            pass

        self.confetti_canvas = tk.Canvas(
            self.win_confete, bg=chroma_key_color, highlightthickness=0)
        self.confetti_canvas.pack(fill="both", expand=True)

        cores = ['#FF0000', '#00FF00', '#0000FF',
                 '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500']
        self.particulas = []

        for _ in range(60):
            px = random.randint(0, w)
            py = random.randint(-h, 0)
            tamanho = random.randint(5, 10)
            cor = random.choice(cores)
            if random.choice([True, False]):
                item = self.confetti_canvas.create_oval(
                    px, py, px+tamanho, py+tamanho, fill=cor, outline="")
            else:
                item = self.confetti_canvas.create_rectangle(
                    px, py, px+tamanho, py+tamanho, fill=cor, outline="")
            velocidade = random.randint(5, 15)
            self.particulas.append({'id': item, 'vel': velocidade})

        self.animar_confete()

    def animar_confete(self):
        if not hasattr(self, 'win_confete') or not self.win_confete.winfo_exists():
            self.bloquear_interface(False)
            return

        altura_tela = self.win_confete.winfo_height()
        particulas_vivas = False

        for p in self.particulas:
            self.confetti_canvas.move(p['id'], 0, p['vel'])
            coords = self.confetti_canvas.coords(p['id'])
            if coords and coords[1] < altura_tela:
                particulas_vivas = True

        if particulas_vivas:
            self.root.after(20, self.animar_confete)
        else:
            self.win_confete.destroy()
            del self.win_confete
            self.bloquear_interface(False)


if __name__ == "__main__":
    root = tk.Tk()
    app = PhibApp(root)
    root.mainloop()