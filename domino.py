import tkinter as tk
from tkinter import messagebox
import random
import os

from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_FICHAS = os.path.join(BASE_DIR, "fichas")

try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS

COLOR_FONDO = "#F5F1EA"
COLOR_PANEL = "#FFFDF9"
COLOR_TEXTO = "#3A3A3A"
COLOR_SUAVE = "#8A8578"
COLOR_ACENTO = "#7C9A82"
COLOR_ACENTO_HOVER = "#6B8871"
COLOR_ALERTA = "#C97B5A"
COLOR_INFO = "#7A8FA6"


class Ficha:
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2
        self.peso = v1 + v2
        self.es_doble = (v1 == v2)

    def __str__(self):
        return f"[{self.v1}|{self.v2}]"

    def coincide(self, extremo):
        return self.v1 == extremo or self.v2 == extremo


class JuegoDomino:
    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        fichas = [Ficha(i, j) for i in range(7) for j in range(i, 7)]
        random.shuffle(fichas)

        self.mano_humano = fichas[0:7]
        self.mano_agente = fichas[7:14]
        self.pozo = fichas[14:]

        self.tablero = []
        self.extremo_izq = None
        self.extremo_der = None
        self.turno_humano = True

    def jugadas_validas(self, mano):
        if not self.tablero:
            return [(ficha, 'der') for ficha in mano]

        validas = []
        for f in mano:
            if f.v1 == self.extremo_izq or f.v2 == self.extremo_izq:
                validas.append((f, 'izq'))
            if f.v1 == self.extremo_der or f.v2 == self.extremo_der:
                validas.append((f, 'der'))
        return validas

    def puede_jugar(self, ficha, lado):
        if not self.tablero:
            return True
        if lado == 'izq':
            return ficha.v1 == self.extremo_izq or ficha.v2 == self.extremo_izq
        if lado == 'der':
            return ficha.v1 == self.extremo_der or ficha.v2 == self.extremo_der
        return False

    def jugar_ficha(self, ficha, lado, jugador_es_humano):
        if self.tablero and not self.puede_jugar(ficha, lado):
            return False

        mano = self.mano_humano if jugador_es_humano else self.mano_agente
        if ficha not in mano:
            return False
        mano.remove(ficha)

        if not self.tablero:
            self.tablero.append(Ficha(ficha.v1, ficha.v2))
            self.extremo_izq = ficha.v1
            self.extremo_der = ficha.v2
            return True

        if lado == 'izq':
            if ficha.v2 == self.extremo_izq:
                nueva = Ficha(ficha.v1, ficha.v2)
            else:
                nueva = Ficha(ficha.v2, ficha.v1)
            self.tablero.insert(0, nueva)
            self.extremo_izq = nueva.v1
        else:
            if ficha.v1 == self.extremo_der:
                nueva = Ficha(ficha.v1, ficha.v2)
            else:
                nueva = Ficha(ficha.v2, ficha.v1)
            self.tablero.append(nueva)
            self.extremo_der = nueva.v2

        return True

    def robar(self, jugador_es_humano):
        if self.pozo:
            ficha = self.pozo.pop(0)
            if jugador_es_humano:
                self.mano_humano.append(ficha)
            else:
                self.mano_agente.append(ficha)
            return True
        return False

    def hay_jugadas(self, mano):
        return len(self.jugadas_validas(mano)) > 0


class BotonSuave(tk.Button):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("bd", 0)
        kwargs.setdefault("font", ("Segoe UI", 11, "bold"))
        kwargs.setdefault("fg", "white")
        kwargs.setdefault("activeforeground", "white")
        kwargs.setdefault("cursor", "hand2")
        kwargs.setdefault("padx", 18)
        kwargs.setdefault("pady", 8)
        super().__init__(master, **kwargs)

        self.color_base = self.cget("bg")
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _):
        self.config(bg=self._oscurecer(self.color_base))

    def _on_leave(self, _):
        self.config(bg=self.color_base)

    @staticmethod
    def _oscurecer(hex_color):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        r = max(0, int(r * 0.88))
        g = max(0, int(g * 0.88))
        b = max(0, int(b * 0.88))
        return f"#{r:02x}{g:02x}{b:02x}"


class InterfazDomino(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Domin AI")
        self.geometry("1100x850")
        self.configure(bg=COLOR_FONDO)
        self.minsize(900, 700)

        self.dificultad = tk.StringVar(value="Fácil")
        self.nombre_jugador = tk.StringVar(value="")

        self.imagenes_tablero = []
        self.imagenes_humano = []
        self.idx_seleccionado = None

        self.pantalla_inicio()

    def _card(self, parent, **pack_kwargs):
        card = tk.Frame(parent, bg=COLOR_PANEL,
                        highlightbackground="#E4DDD1", highlightthickness=1)
        if pack_kwargs:
            card.pack(**pack_kwargs)
        return card

    def pantalla_inicio(self):
        self.limpiar_ventana()

        contenedor = tk.Frame(self, bg=COLOR_FONDO)
        contenedor.pack(expand=True, fill=tk.BOTH)

        card = tk.Frame(contenedor, bg=COLOR_PANEL,
                        highlightbackground="#E4DDD1", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=480, height=560)

        tk.Label(card, text="Domin AI",
                 font=("Segoe UI", 30, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(45, 5))

        tk.Label(card, text="Un duelo sereno contra la inteligencia artificial",
                 font=("Segoe UI", 11, "italic"),
                 bg=COLOR_PANEL, fg=COLOR_SUAVE).pack(pady=(0, 30))

        tk.Label(card, text="¿Cómo te llamas?",
                 font=("Segoe UI", 11),
                 bg=COLOR_PANEL, fg=COLOR_SUAVE).pack(pady=(0, 6))

        entrada = tk.Entry(card, textvariable=self.nombre_jugador,
                           font=("Segoe UI", 13),
                           width=24, justify="center",
                           bg="#FFFFFF", fg=COLOR_TEXTO,
                           relief="flat", bd=0,
                           highlightthickness=1,
                           highlightbackground="#E4DDD1",
                           highlightcolor=COLOR_ACENTO)
        entrada.pack(ipady=8, pady=(0, 25))
        entrada.focus_set()
        self.entry_nombre = entrada

        tk.Label(card, text="Estrategia de la IA",
                 font=("Segoe UI", 11),
                 bg=COLOR_PANEL, fg=COLOR_SUAVE).pack(pady=(0, 10))

        estilo_rb = {
            "bg": COLOR_PANEL, "fg": COLOR_TEXTO,
            "font": ("Segoe UI", 11),
            "activebackground": COLOR_PANEL,
            "selectcolor": "#FFFFFF",
            "bd": 0, "highlightthickness": 0,
            "cursor": "hand2",
        }
        tk.Radiobutton(card, text="Fácil  ·  aleatoria", variable=self.dificultad,
                       value="Fácil", **estilo_rb).pack(pady=2)
        tk.Radiobutton(card, text="Media  ·  voraz", variable=self.dificultad,
                       value="Medio", **estilo_rb).pack(pady=2)
        tk.Radiobutton(card, text="Difícil  ·  heurística", variable=self.dificultad,
                       value="Difícil", **estilo_rb).pack(pady=2)

        BotonSuave(card, text="Comenzar partida",
                   bg=COLOR_ACENTO, command=self.iniciar_juego).pack(pady=35)

        self.bind("<Return>", lambda _: self.iniciar_juego())

    def iniciar_juego(self):
        nombre = self.nombre_jugador.get().strip()
        if not nombre:
            messagebox.showwarning("Falta tu nombre",
                                   "Escribe tu nombre para comenzar la partida.")
            self.entry_nombre.focus_set()
            return
        self.nombre_jugador.set(nombre)
        self.juego = JuegoDomino()
        self.idx_seleccionado = None
        self.pantalla_juego()

    def pantalla_juego(self):
        self.limpiar_ventana()

        header = tk.Frame(self, bg=COLOR_FONDO)
        header.pack(side=tk.TOP, fill=tk.X, padx=24, pady=(16, 8))

        tk.Label(header, text="Domin AI",
                 font=("Segoe UI", 16, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side=tk.LEFT)

        self.lbl_agente = tk.Label(header,
                                   text=f"Gem · {len(self.juego.mano_agente)} fichas",
                                   font=("Segoe UI", 11),
                                   bg=COLOR_FONDO, fg=COLOR_SUAVE)
        self.lbl_agente.pack(side=tk.RIGHT)

        self.frame_agente = tk.Frame(self, bg=COLOR_FONDO)
        self.frame_agente.pack(side=tk.TOP, fill=tk.X, padx=24)
        self.canvas_agente = tk.Canvas(self.frame_agente, bg=COLOR_FONDO,
                                       height=90, highlightthickness=0)
        self.canvas_agente.pack(fill=tk.X)

        mesa_card = tk.Frame(self, bg=COLOR_PANEL,
                             highlightbackground="#E4DDD1", highlightthickness=1)
        mesa_card.pack(side=tk.TOP, fill=tk.BOTH, expand=True,
                       padx=24, pady=(8, 12))

        self.lbl_extremos = tk.Label(mesa_card,
                                     text="La mesa está vacía. Juega tu primera ficha.",
                                     font=("Segoe UI", 12),
                                     bg=COLOR_PANEL, fg=COLOR_SUAVE)
        self.lbl_extremos.pack(side=tk.TOP, pady=(12, 4))

        self.canvas_tablero = tk.Canvas(mesa_card, bg=COLOR_PANEL,
                                        height=200, highlightthickness=0)
        self.scroll_tablero = tk.Scrollbar(mesa_card, orient=tk.HORIZONTAL,
                                           command=self.canvas_tablero.xview)
        self.canvas_tablero.config(xscrollcommand=self.scroll_tablero.set)
        self.canvas_tablero.pack(side=tk.TOP, fill=tk.BOTH, expand=True,
                                 padx=12, pady=(0, 12))

        pie = tk.Frame(self, bg=COLOR_FONDO)
        pie.pack(side=tk.BOTTOM, fill=tk.X, padx=24, pady=(0, 16))

        self.lbl_info = tk.Label(pie,
                                 text=f"{self.nombre_jugador.get()} · turno · pozo {len(self.juego.pozo)}",
                                 font=("Segoe UI", 11, "bold"),
                                 bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.lbl_info.pack(side=tk.TOP, anchor=tk.W, pady=(0, 8))

        self.scroll_humano = tk.Scrollbar(pie, orient=tk.HORIZONTAL)
        self.scroll_humano.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas_humano = tk.Canvas(pie, bg=COLOR_FONDO,
                                       height=170, highlightthickness=0)
        self.canvas_humano.config(xscrollcommand=self.scroll_humano.set)
        self.scroll_humano.config(command=self.canvas_humano.xview)
        self.canvas_humano.pack(side=tk.BOTTOM, fill=tk.X)

        controles = tk.Frame(pie, bg=COLOR_FONDO)
        controles.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 6))

        BotonSuave(controles, text="Izquierda",
                   bg=COLOR_INFO,
                   command=lambda: self.accion_humano('izq')).pack(side=tk.LEFT, padx=(0, 8))
        BotonSuave(controles, text="Derecha",
                   bg=COLOR_INFO,
                   command=lambda: self.accion_humano('der')).pack(side=tk.LEFT, padx=(0, 8))
        BotonSuave(controles, text="Robar / Pasar",
                   bg=COLOR_ALERTA,
                   command=self.robar_o_pasar_humano).pack(side=tk.LEFT)

        BotonSuave(controles, text="Volver al menú",
                   bg="#B9B2A4",
                   command=self.pantalla_inicio).pack(side=tk.RIGHT)

        self.actualizar_ui()

        if not self.juego.hay_jugadas(self.juego.mano_humano) and self.juego.pozo:
            self.after(400, self.robar_o_pasar_humano)

    def seleccionar_ficha(self, idx):
        self.idx_seleccionado = idx
        self.renderizar_humano()

    def renderizar_agente(self):
        self.canvas_agente.delete("all")
        num_fichas = len(self.juego.mano_agente)
        if num_fichas == 0:
            return

        ancho_ficha = 36
        alto_ficha = 72
        espaciado = 8
        ancho_total = (num_fichas * ancho_ficha) + ((num_fichas - 1) * espaciado)

        self.update_idletasks()
        x_inicio = (self.winfo_width() - ancho_total) // 2
        if x_inicio < 20:
            x_inicio = 20

        for i in range(num_fichas):
            x = x_inicio + (i * (ancho_ficha + espaciado))
            self.canvas_agente.create_rectangle(
                x, 8, x + ancho_ficha, 8 + alto_ficha,
                fill="#FFFFFF", outline="#E4DDD1", width=1
            )

    def _buscar_imagen(self, v_min, v_max):
        extensiones = [".png", ".jpg", ".jpeg", ".PNG", ".JPG"]
        for ext in extensiones:
            ruta = os.path.join(CARPETA_FICHAS, f"{v_min}_{v_max}{ext}")
            if os.path.exists(ruta):
                return ruta
        return None

    def renderizar_humano(self):
        self.canvas_humano.delete("all")
        self.imagenes_humano.clear()

        if not self.juego.mano_humano:
            return

        ancho_ficha = 66
        alto_ficha = 132
        espaciado = 14
        x_actual = 16

        for i, f in enumerate(self.juego.mano_humano):
            v_min, v_max = min(f.v1, f.v2), max(f.v1, f.v2)
            ruta_imagen = self._buscar_imagen(v_min, v_max)

            try:
                if not ruta_imagen:
                    raise FileNotFoundError("Imagen no encontrada")

                img = Image.open(ruta_imagen).convert("RGBA")
                img = img.resize((ancho_ficha, alto_ficha), RESAMPLE)

                if f.v1 > f.v2:
                    img = img.rotate(180, expand=True)

                img_tk = ImageTk.PhotoImage(img)
                self.imagenes_humano.append(img_tk)

                if self.idx_seleccionado == i:
                    self.canvas_humano.create_rectangle(
                        x_actual - 5, 11 - 5,
                        x_actual + ancho_ficha + 5, 11 + alto_ficha + 5,
                        outline=COLOR_ACENTO, width=3
                    )

                item = self.canvas_humano.create_image(x_actual, 11,
                                                       image=img_tk, anchor=tk.NW)
                self.canvas_humano.tag_bind(
                    item, '<Button-1>',
                    lambda _, idx=i: self.seleccionar_ficha(idx)
                )

            except Exception:
                rect = self.canvas_humano.create_rectangle(
                    x_actual, 11,
                    x_actual + ancho_ficha, 11 + alto_ficha,
                    fill="#FFFFFF", outline=COLOR_ALERTA
                )
                self.canvas_humano.create_text(
                    x_actual + (ancho_ficha / 2), 11 + (alto_ficha / 2),
                    text=str(f), font=("Segoe UI", 12, "bold"), fill=COLOR_TEXTO
                )
                self.canvas_humano.tag_bind(
                    rect, '<Button-1>',
                    lambda _, idx=i: self.seleccionar_ficha(idx)
                )

            x_actual += ancho_ficha + espaciado

        self.canvas_humano.config(scrollregion=(0, 0, x_actual + 20, 170))

    def renderizar_tablero(self):
        self.canvas_tablero.delete("all")
        self.imagenes_tablero.clear()

        if not self.juego.tablero:
            return

        ancho_largo = 96
        ancho_corto = 48
        x_actual = 30
        y_centro = 100
        espaciado = 6

        for f in self.juego.tablero:
            v_min, v_max = min(f.v1, f.v2), max(f.v1, f.v2)
            ruta_imagen = self._buscar_imagen(v_min, v_max)

            try:
                if not ruta_imagen:
                    raise FileNotFoundError("Imagen no encontrada")

                img = Image.open(ruta_imagen).convert("RGBA")

                if f.es_doble:
                    img = img.resize((ancho_corto, ancho_largo), RESAMPLE)
                    ancho_actual = ancho_corto
                else:
                    img = img.resize((ancho_corto, ancho_largo), RESAMPLE)

                    if f.v1 < f.v2:
                        img = img.rotate(-90, expand=True)
                    elif f.v1 > f.v2:
                        img = img.rotate(90, expand=True)

                    ancho_actual = ancho_largo

                img_tk = ImageTk.PhotoImage(img)
                self.imagenes_tablero.append(img_tk)
                self.canvas_tablero.create_image(x_actual, y_centro,
                                                 image=img_tk, anchor=tk.W)
                x_actual += ancho_actual + espaciado

            except Exception:
                self.canvas_tablero.create_text(
                    x_actual + 48, y_centro, text=str(f),
                    fill=COLOR_ALERTA, font=("Segoe UI", 12, "bold")
                )
                x_actual += ancho_largo + espaciado

        self.canvas_tablero.config(scrollregion=(0, 0, x_actual + 40, 200))
        self.canvas_tablero.xview_moveto(1.0)

    def actualizar_ui(self):
        self.lbl_agente.config(text=f"Gem · {len(self.juego.mano_agente)} fichas")
        self.lbl_info.config(
            text=f"{self.nombre_jugador.get()} · turno · pozo {len(self.juego.pozo)}"
        )

        if self.juego.tablero:
            self.lbl_extremos.config(
                text=f"◂  izquierda  {self.juego.extremo_izq}          {self.juego.extremo_der}  derecha  ▸",
                fg=COLOR_ACENTO
            )
        else:
            self.lbl_extremos.config(
                text="La mesa está vacía. Juega tu primera ficha.",
                fg=COLOR_SUAVE
            )

        self.renderizar_agente()
        self.renderizar_tablero()
        self.renderizar_humano()

        self.verificar_fin_juego()

    def accion_humano(self, lado):
        if self.idx_seleccionado is None:
            messagebox.showinfo("Selecciona una ficha",
                                "Toca una ficha de tu mano para seleccionarla.")
            return

        if self.idx_seleccionado >= len(self.juego.mano_humano):
            self.idx_seleccionado = None
            return

        ficha = self.juego.mano_humano[self.idx_seleccionado]

        if not self.juego.puede_jugar(ficha, lado):
            messagebox.showinfo("Jugada no válida",
                                f"La ficha {ficha} no encaja en el extremo "
                                f"{'izquierdo' if lado == 'izq' else 'derecho'} "
                                f"({self.juego.extremo_izq if lado == 'izq' else self.juego.extremo_der}).")
            return

        lado_final = lado if self.juego.tablero else 'der'
        if not self.juego.jugar_ficha(ficha, lado_final, jugador_es_humano=True):
            messagebox.showinfo("No se pudo jugar", "Intenta con otra ficha.")
            return

        self.juego.turno_humano = False
        self.idx_seleccionado = None
        self.actualizar_ui()

        if self.juego.mano_humano and self.juego.mano_agente:
            self.lbl_info.config(text="Gem está pensando…")
            self.update_idletasks()
            self.after(1100, self.turno_agente)

    def robar_o_pasar_humano(self):
        if self.juego.hay_jugadas(self.juego.mano_humano):
            messagebox.showinfo("Tienes jugadas",
                                "Aún tienes fichas válidas. Debes jugar.")
            return

        robo = False
        while not self.juego.hay_jugadas(self.juego.mano_humano) and self.juego.pozo:
            self.juego.robar(jugador_es_humano=True)
            robo = True

        if robo:
            self.actualizar_ui()
            if self.juego.hay_jugadas(self.juego.mano_humano):
                messagebox.showinfo("Robaste del pozo",
                                    "Ahora tienes jugadas disponibles.")
                return

        self.juego.turno_humano = False
        self.lbl_info.config(text="Gem está pensando…")
        self.after(1100, self.turno_agente)

    def turno_agente(self):
        validas = self.juego.jugadas_validas(self.juego.mano_agente)
        while not validas and self.juego.pozo:
            self.juego.robar(jugador_es_humano=False)
            validas = self.juego.jugadas_validas(self.juego.mano_agente)
            self.update_idletasks()

        if not validas:
            self.juego.turno_humano = True
            self.actualizar_ui()
            if not self.juego.hay_jugadas(self.juego.mano_humano) and not self.juego.pozo:
                self.finalizar_partida(tranque=True)
            return

        dif = self.dificultad.get()

        if dif == "Fácil":
            ficha_elegida, lado = random.choice(validas)
        elif dif == "Medio":
            ficha_elegida, lado = max(validas, key=lambda x: x[0].peso)
        else:
            conteos = {i: 0 for i in range(7)}
            for f in self.juego.mano_agente:
                conteos[f.v1] += 1
                conteos[f.v2] += 1

            mejor_puntaje = -1
            ficha_elegida, lado = validas[0]

            for f, l in validas:
                if not self.juego.tablero:
                    numero_expuesto = f.v1
                elif l == 'izq':
                    numero_expuesto = f.v2 if f.v1 == self.juego.extremo_izq else f.v1
                else:
                    numero_expuesto = f.v1 if f.v2 == self.juego.extremo_der else f.v2

                puntaje = conteos[numero_expuesto]
                if puntaje > mejor_puntaje:
                    mejor_puntaje = puntaje
                    ficha_elegida, lado = f, l

        lado_final = 'der' if not self.juego.tablero else lado
        if not self.juego.jugar_ficha(ficha_elegida, lado_final, jugador_es_humano=False):
            self.actualizar_ui()
            return

        self.juego.turno_humano = True
        self.actualizar_ui()

    def verificar_fin_juego(self):
        if not self.juego.mano_humano:
            self.finalizar_partida("Humano")
            return True
        if not self.juego.mano_agente:
            self.finalizar_partida("Agente")
            return True
        return False

    def finalizar_partida(self, ganador=None, tranque=False):
        self.limpiar_ventana()

        contenedor = tk.Frame(self, bg=COLOR_FONDO)
        contenedor.pack(expand=True, fill=tk.BOTH)

        card = tk.Frame(contenedor, bg=COLOR_PANEL,
                        highlightbackground="#E4DDD1", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=460, height=300)

        if tranque:
            p = sum(f.peso for f in self.juego.mano_humano)
            pa = sum(f.peso for f in self.juego.mano_agente)
            titulo = "Empate por tranque"
            subtitulo = f"{self.nombre_jugador.get()} · {p} pts        Gem · {pa} pts"
            color = COLOR_ALERTA
        else:
            if ganador == "Humano":
                titulo = f"¡Ganaste, {self.nombre_jugador.get()}!"
                subtitulo = "Has vencido a la inteligencia artificial."
                color = COLOR_ACENTO
            else:
                titulo = "Victoria de Gem"
                subtitulo = "La IA ha ganado esta partida."
                color = COLOR_ALERTA

        tk.Label(card, text=titulo, font=("Segoe UI", 22, "bold"),
                 bg=COLOR_PANEL, fg=color).pack(pady=(50, 10))
        tk.Label(card, text=subtitulo, font=("Segoe UI", 12),
                 bg=COLOR_PANEL, fg=COLOR_SUAVE).pack(pady=(0, 30))

        BotonSuave(card, text="Volver al menú",
                   bg=COLOR_ACENTO,
                   command=self.pantalla_inicio).pack()

    def limpiar_ventana(self):
        self.unbind("<Return>")
        for widget in self.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = InterfazDomino()
    app.mainloop()