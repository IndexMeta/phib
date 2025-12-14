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
        self.root.title("Phib - Perímetro")

        # --- AJUSTE DE RESOLUÇÃO (CRÍTICO PARA TELAS PEQUENAS) ---
        self.root.geometry("900x650")
        self.root.minsize(800, 500)

        # Tenta iniciar maximizado (Melhor experiência)
        try:
            self.root.state('zoomed')
        except:
            pass

        # --- CONFIGURAÇÃO DO ÍCONE (NOVO) ---
        # Isso garante que o ícone apareça na barra de tarefas e na janela
        try:
            # ID único para a barra de tarefas
            myappid = 'projeto.phib.perimetro.v1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                myappid)

            # Define o ícone da janela
            self.root.iconbitmap(resource_path("tar.ico"))
        except Exception:
            pass  # Continua mesmo se não encontrar o ícone

        # Estilo geral
        style = ttk.Style()
        style.theme_use('clam')

        # Correção visual do Combobox
        style.map('TCombobox',
                  fieldbackground=[('readonly', 'white')],
                  selectbackground=[('readonly', 'white')],
                  selectforeground=[('readonly', 'black')],
                  background=[('readonly', 'white')]
                  )

        # --- ESTRUTURA PRINCIPAL ---
        # 1. Rodapé (Prioridade de Layout)
        self.footer_frame = ttk.Frame(root, height=60)
        self.footer_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        self.setup_logo()

        # 2. Container Principal
        self.main_container = ttk.Frame(root)
        self.main_container.pack(side="top", fill="both", expand=True)

        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # --- ABAS ---
        self.tab_perimetro = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_perimetro, text='   Perímetro   ')

        self.inputs_lados = []
        self.setup_tab_perimetro()

        # Atalho Global
        self.root.bind('<Alt-F4>', lambda event: self.root.destroy())

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
            if hasattr(self, 'btn_reset'):
                self.btn_reset.config(state=estado)
            if hasattr(self, 'combo_saida'):
                self.combo_saida.config(state=estado)
            self.root.config(cursor=cursor)
        except Exception:
            pass

    # =========================================
    # LÓGICA DO PERÍMETRO
    # =========================================
    def setup_tab_perimetro(self):
        # Header
        header_frame = ttk.Frame(self.tab_perimetro)
        header_frame.pack(side="top", fill='x', padx=10, pady=10)

        ttk.Label(header_frame, text="Encontre seu Perímetro",
                  font=("Segoe UI", 14, "bold")).pack()

        ttk.Label(header_frame, text="Perímetro é a soma dos comprimentos de todos os lados de uma figura geométrica fechada.",
                  font=("Segoe UI", 12, "italic"), foreground="gray").pack()

        self.lbl_resultado_perimetro = ttk.Label(
            header_frame,
            text="Resultado: ---",
            font=("Segoe UI", 20, "bold"),
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

        # Rodapé da Aba
        bottom_controls = ttk.Frame(self.tab_perimetro)
        bottom_controls.pack(side="bottom", fill='x', pady=10, padx=20)

        bottom_controls.columnconfigure(0, weight=1)
        bottom_controls.columnconfigure(1, weight=0)
        bottom_controls.columnconfigure(2, weight=1)
        bottom_controls.columnconfigure(3, weight=0)
        bottom_controls.columnconfigure(4, weight=0)
        bottom_controls.columnconfigure(5, weight=0)

        self.btn_add = ttk.Button(
            bottom_controls,
            text="+ Adicionar Novo Lado",
            command=lambda: self.add_lado_input(removivel=True)
        )
        self.btn_add.grid(row=0, column=1)

        ttk.Label(bottom_controls, text="Resposta em:").grid(
            row=0, column=3, padx=(0, 5), sticky="e")

        self.combo_saida = ttk.Combobox(
            bottom_controls,
            values=['km', 'hm', 'dam', 'm', 'dm', 'cm', 'mm'],
            width=5,
            state="readonly",
            font=("Segoe UI", 10)
        )
        self.combo_saida.set('m')
        self.combo_saida.grid(row=0, column=4, padx=(0, 10), sticky="e")

        self.btn_reset = tk.Button(
            bottom_controls,
            text="⟲ Reset",
            command=self.reset_perimetro,
            bg="#e06b6b",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10, pady=4,
            cursor="hand2"
        )
        self.btn_reset.grid(row=0, column=5, sticky="e")

        # Scroll
        scroll_container = ttk.Frame(self.tab_perimetro)
        scroll_container.pack(side="top", fill="both",
                              expand=True, padx=20, pady=5)

        self.canvas = tk.Canvas(scroll_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            scroll_container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Inicialização
        for _ in range(3):
            self.add_lado_input(removivel=False)

    def reset_perimetro(self):
        self.lbl_resultado_perimetro.config(
            text="Resultado: ---", foreground="#333")
        self.combo_saida.set('m')
        for item in self.inputs_lados:
            item['frame'].destroy()
        self.inputs_lados.clear()
        for _ in range(3):
            self.add_lado_input(removivel=False)

    def add_lado_input(self, removivel=True):
        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.pack(fill='x', pady=5, padx=5)

        idx = len(self.inputs_lados) + 1

        lbl = ttk.Label(
            row_frame, text=f"Lado {idx}:", width=8, font=("Segoe UI", 10))
        lbl.pack(side="left")

        if removivel:
            btn_remove = tk.Button(
                row_frame, text="✕", bg="#ffcccc", fg="red",
                font=("Arial", 8, "bold"), relief="flat", cursor="hand2",
                command=lambda: self.remover_lado(row_frame, entry)
            )
            btn_remove.pack(side="right", padx=5)

        unidades = ['m', 'km', 'hm', 'dam', 'dm', 'cm', 'mm']
        combo = ttk.Combobox(row_frame, values=unidades,
                             width=5, state="readonly", font=("Segoe UI", 10))
        combo.set('m')
        combo.pack(side="right", padx=5)

        entry = ttk.Entry(row_frame, font=("Segoe UI", 10))
        entry.pack(side="left", fill="x", expand=True, padx=5)

        entry.bind("<Return>", self.focar_proximo_campo)

        self.inputs_lados.append({
            'entry': entry,
            'combo': combo,
            'frame': row_frame,
            'label': lbl
        })

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def remover_lado(self, frame_to_remove, entry_ref):
        frame_to_remove.destroy()
        self.inputs_lados = [
            item for item in self.inputs_lados if item['entry'] != entry_ref]
        for i, item in enumerate(self.inputs_lados):
            item['label'].config(text=f"Lado {i+1}:")

    def focar_proximo_campo(self, event):
        widget_atual = event.widget
        for i, item in enumerate(self.inputs_lados):
            if item['entry'] == widget_atual:
                if i < len(self.inputs_lados) - 1:
                    self.inputs_lados[i+1]['entry'].focus_set()
                else:
                    self.btn_calc.focus_set()
                break

    def calcular_perimetro(self):
        total_metros = 0.0
        lados_validos_count = 0

        fatores_entrada = {'km': 1000, 'hm': 100, 'dam': 10,
                           'm': 1, 'dm': 0.1, 'cm': 0.01, 'mm': 0.001}

        fatores_saida = {'km': 0.001, 'hm': 0.01, 'dam': 0.1,
                         'm': 1, 'dm': 10, 'cm': 100, 'mm': 1000}

        try:
            for item in self.inputs_lados:
                entry = item['entry']
                combo = item['combo']
                texto_original = entry.get().strip()
                if not texto_original:
                    continue
                texto_corrigido = texto_original.replace(',', '.')

                safe_math = {'pi': math.pi, 'e': math.e, 'sqrt': math.sqrt}
                valor = eval(texto_corrigido, {
                             "__builtins__": None}, safe_math)
                valor_float = float(valor)

                if valor_float == 0:
                    messagebox.showerror(
                        "Erro de Valor", "Um lado geométrico não pode ser 0.\nPor favor, corrija o valor.")
                    return

                fator = fatores_entrada[combo.get()]
                total_metros += valor_float * fator
                lados_validos_count += 1

            if lados_validos_count < 3:
                messagebox.showerror(
                    "Geometria Inválida", "Para formar um polígono fechado,\né necessário informar pelo menos 3 lados válidos.")
                return

            unidade_saida = self.combo_saida.get()
            valor_final = total_metros * fatores_saida[unidade_saida]

            texto_formatado = f"{valor_final:.6f}".rstrip('0').rstrip('.')

            self.lbl_resultado_perimetro.config(
                text=f"Perímetro Total = {texto_formatado} {unidade_saida}",
                foreground="#006400"
            )

            self.disparar_confete()

        except ValueError:
            messagebox.showerror(
                "Erro de Digitação", "Por favor, insira apenas números válidos.\nUse 'pi' ou 'sqrt' se necessário.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

    # =========================================
    # SISTEMA DE CONFETES + PALMAS 👏
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

        # 1. Cria Confetes
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
            velocidade = random.randint(5, 7)
            self.particulas.append({'id': item, 'vel': velocidade})

        # 2. Cria Emoji de Palmas Gigante (Animação Extra)
        # Usamos texto unicode. Começa pequeno.
        self.palmas_id = self.confetti_canvas.create_text(
            w/2, h/2,
            text="👏  👏",
            font=("Segoe UI Emoji", 17, "bold"),
            fill="purple"
        )
        self.palmas_frame = 0  # Contador para a animação das palmas

        self.animar_confete()

    def animar_confete(self):
        if not hasattr(self, 'win_confete') or not self.win_confete.winfo_exists():
            self.bloquear_interface(False)
            return

        altura_tela = self.win_confete.winfo_height()
        particulas_vivas = False

        # Anima Confetes
        for p in self.particulas:
            self.confetti_canvas.move(p['id'], 0, p['vel'])
            coords = self.confetti_canvas.coords(p['id'])
            if coords and coords[1] < altura_tela:
                particulas_vivas = True

        # Animação das Palmas (Pulsar)
        # Aumenta até o frame 25, depois diminui
        self.palmas_frame += 1
        if self.palmas_frame < 50:
            # Efeito de pulsar: calcula tamanho da fonte baseado no frame
            tamanho_base = 10
            # Oscila entre 10 e 50
            fator_pulso = 30 + int(20 * math.sin(self.palmas_frame * 0.2))

            # Atualiza fonte
            # Nota: Atualizar fonte a cada frame pode ser pesado, fazemos de forma simples
            if self.palmas_frame % 2 == 0:
                self.confetti_canvas.itemconfig(
                    self.palmas_id,
                    font=("Segoe UI Emoji", fator_pulso, "bold")
                )
            particulas_vivas = True  # Mantém vivo enquanto tiver palmas

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
