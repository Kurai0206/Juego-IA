import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk
import os

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
            return [(ficha, 'ambos') for ficha in mano]
            
        validas = []
        for f in mano:
            # Lógica corregida: Evaluaciones independientes y sin bloqueos
            if f.v1 == self.extremo_izq or f.v2 == self.extremo_izq:
                validas.append((f, 'izq'))
            if f.v1 == self.extremo_der or f.v2 == self.extremo_der:
                validas.append((f, 'der'))
        return validas

    def jugar_ficha(self, ficha, lado, jugador_es_humano):
        mano = self.mano_humano if jugador_es_humano else self.mano_agente
        mano.remove(ficha)
        
        if not self.tablero:
            self.tablero.append(ficha)
            self.extremo_izq = ficha.v1
            self.extremo_der = ficha.v2
            return

        if lado == 'izq':
            if ficha.v1 == self.extremo_izq:
                ficha.v1, ficha.v2 = ficha.v2, ficha.v1
            self.tablero.insert(0, ficha)
            self.extremo_izq = ficha.v1
        else:
            if ficha.v2 == self.extremo_der:
                ficha.v1, ficha.v2 = ficha.v2, ficha.v1
            self.tablero.append(ficha)
            self.extremo_der = ficha.v2

    def robar(self, jugador_es_humano):
        if self.pozo:
            ficha = self.pozo.pop(0)
            if jugador_es_humano:
                self.mano_humano.append(ficha)
            else:
                self.mano_agente.append(ficha)
            return True
        return False

class InterfazDomino(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dominó IA - Arquitectura de Tres Capas")
        self.geometry("1100x850")
        self.configure(bg="#FFFFFF")
        self.dificultad = tk.StringVar(value="Fácil")
        
        self.imagenes_tablero = []
        self.imagenes_humano = []
        self.idx_seleccionado = None
        
        self.pantalla_inicio()

    def pantalla_inicio(self):
        self.limpiar_ventana()
        tk.Label(self, text="Inteligencia Artificial en Dominó", font=("Arial", 28, "bold"), bg="#FFFFFF", fg="#333333").pack(pady=60)
        tk.Label(self, text="Selecciona la estrategia de Gem:", font=("Arial", 16), bg="#FFFFFF", fg="#555555").pack(pady=10)
        
        estilo_rb = {"bg": "#FFFFFF", "fg": "#333333", "font": ("Arial", 14), "selectcolor": "#F0F0F0"}
        tk.Radiobutton(self, text="Fácil (Aleatorio)", variable=self.dificultad, value="Fácil", **estilo_rb).pack()
        tk.Radiobutton(self, text="Medio (Voraz)", variable=self.dificultad, value="Medio", **estilo_rb).pack()
        tk.Radiobutton(self, text="Difícil (Heurística)", variable=self.dificultad, value="Difícil", **estilo_rb).pack()

        tk.Button(self, text="Comenzar Partida", font=("Arial", 16, "bold"), bg="#4CAF50", fg="white", relief="flat", padx=20, pady=10, command=self.iniciar_juego).pack(pady=50)

    def iniciar_juego(self):
        self.juego = JuegoDomino()
        self.idx_seleccionado = None
        self.pantalla_juego()

    def pantalla_juego(self):
        self.limpiar_ventana()

        self.frame_agente = tk.Frame(self, bg="#FFFFFF")
        self.frame_agente.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        self.lbl_agente = tk.Label(self.frame_agente, text="Gem (IA) - Fichas", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#333333")
        self.lbl_agente.pack()
        self.canvas_agente = tk.Canvas(self.frame_agente, bg="#FFFFFF", height=100, highlightthickness=0)
        self.canvas_agente.pack(fill=tk.X)

        self.frame_inferior = tk.Frame(self, bg="#FFFFFF")
        self.frame_inferior.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.frame_controles = tk.Frame(self.frame_inferior, bg="#FFFFFF")
        self.frame_controles.pack(side=tk.BOTTOM, anchor=tk.E, padx=20, pady=5)
        
        estilo_btn = {"font": ("Arial", 12, "bold"), "fg": "white", "relief": "flat", "padx": 15, "pady": 5}
        tk.Button(self.frame_controles, text="Jugar Izquierda", bg="#2196F3", command=lambda: self.accion_humano('izq'), **estilo_btn).grid(row=0, column=0, padx=10)
        tk.Button(self.frame_controles, text="Jugar Derecha", bg="#2196F3", command=lambda: self.accion_humano('der'), **estilo_btn).grid(row=0, column=1, padx=10)
        tk.Button(self.frame_controles, text="Robar / Pasar", bg="#FF9800", command=self.robar_o_pasar_humano, **estilo_btn).grid(row=0, column=2, padx=10)

        self.scroll_humano = tk.Scrollbar(self.frame_inferior, orient=tk.HORIZONTAL)
        self.scroll_humano.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas_humano = tk.Canvas(self.frame_inferior, bg="#FFFFFF", height=180, highlightthickness=0)
        self.canvas_humano.config(xscrollcommand=self.scroll_humano.set)
        self.scroll_humano.config(command=self.canvas_humano.xview)
        self.canvas_humano.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_info = tk.Label(self.frame_inferior, text=f"Dificultad: {self.dificultad.get()} | Tu turno, Kurai | Pozo: {len(self.juego.pozo)}", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#333333")
        self.lbl_info.pack(side=tk.BOTTOM, anchor=tk.W, padx=20, pady=5)

        self.frame_tablero = tk.Frame(self, bg="#FFFFFF")
        self.frame_tablero.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10)
        
        # --- NUEVO HUD DE EXTREMOS ---
        self.lbl_extremos = tk.Label(self.frame_tablero, text="Mesa vacía. Juega tu primera ficha.", font=("Arial", 14, "bold"), bg="#FFFFFF", fg="#4CAF50")
        self.lbl_extremos.pack(side=tk.TOP, pady=5)

        self.canvas_tablero = tk.Canvas(self.frame_tablero, bg="#FFFFFF", height=200, highlightthickness=0)
        self.scroll_tablero = tk.Scrollbar(self.frame_tablero, orient=tk.HORIZONTAL, command=self.canvas_tablero.xview)
        self.canvas_tablero.config(xscrollcommand=self.scroll_tablero.set)
        self.canvas_tablero.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.scroll_tablero.pack(side=tk.BOTTOM, fill=tk.X)

        self.actualizar_ui()

    def seleccionar_ficha(self, idx):
        self.idx_seleccionado = idx
        self.renderizar_humano()

    def renderizar_agente(self):
        self.canvas_agente.delete("all")
        num_fichas = len(self.juego.mano_agente)
        ancho_ficha = 40
        alto_ficha = 80
        espaciado = 10
        ancho_total = (num_fichas * ancho_ficha) + ((num_fichas - 1) * espaciado)
        
        self.update_idletasks()
        x_inicio = (self.winfo_width() - ancho_total) // 2
        if x_inicio < 20: x_inicio = 20
        
        for i in range(num_fichas):
            x = x_inicio + (i * (ancho_ficha + espaciado))
            self.canvas_agente.create_rectangle(x, 10, x + ancho_ficha, 10 + alto_ficha, fill="#FAFAFA", outline="#CCCCCC", width=2)

    def _buscar_imagen(self, v_min, v_max):
        extensiones = [".png", ".jpg", ".jpeg", ".PNG", ".JPG"]
        for ext in extensiones:
            ruta = f"{v_min}_{v_max}{ext}"
            if os.path.exists(ruta):
                return ruta
        return None

    def renderizar_humano(self):
        self.canvas_humano.delete("all")
        self.imagenes_humano.clear()
        
        if not self.juego.mano_humano: return

        ancho_ficha = 70 
        alto_ficha = 140
        espaciado = 15
        x_actual = 20 
        
        for i, f in enumerate(self.juego.mano_humano):
            v_min, v_max = min(f.v1, f.v2), max(f.v1, f.v2)
            ruta_imagen = self._buscar_imagen(v_min, v_max)
            
            try:
                if not ruta_imagen:
                    raise FileNotFoundError("Imagen no encontrada")
                    
                img = Image.open(ruta_imagen)
                es_horizontal = img.width > img.height
                
                if es_horizontal:
                    img = img.resize((140, 70), getattr(Image, 'LANCZOS', Image.Resampling.LANCZOS))
                    img = img.rotate(90, expand=True)
                else:
                    img = img.resize((70, 140), getattr(Image, 'LANCZOS', Image.Resampling.LANCZOS))
                
                img_tk = ImageTk.PhotoImage(img)
                self.imagenes_humano.append(img_tk)
                
                if self.idx_seleccionado == i:
                    self.canvas_humano.create_rectangle(x_actual-4, 15-4, x_actual+ancho_ficha+4, 15+alto_ficha+4, outline="#2196F3", width=4)
                
                item = self.canvas_humano.create_image(x_actual, 15, image=img_tk, anchor=tk.NW)
                self.canvas_humano.tag_bind(item, '<Button-1>', lambda event, idx=i: self.seleccionar_ficha(idx))
                
            except Exception as e:
                rect = self.canvas_humano.create_rectangle(x_actual, 15, x_actual+ancho_ficha, 15+alto_ficha, fill="#EEEEEE", outline="#FF5722")
                self.canvas_humano.create_text(x_actual+(ancho_ficha/2), 15+(alto_ficha/2), text=str(f), font=("Arial", 12, "bold"), fill="#333333")
                self.canvas_humano.tag_bind(rect, '<Button-1>', lambda event, idx=i: self.seleccionar_ficha(idx))
                
            x_actual += ancho_ficha + espaciado

        self.canvas_humano.config(scrollregion=(0, 0, x_actual + 20, 180))

    def renderizar_tablero(self):
        self.canvas_tablero.delete("all")
        self.imagenes_tablero.clear()
        
        if not self.juego.tablero:
            return

        # --- DIMENSIONES REDUCIDAS PARA EL TABLERO ---
        ancho_largo = 80
        ancho_corto = 40
        
        x_actual = 40
        y_centro = 100
        espaciado = 4

        for f in self.juego.tablero:
            v_min, v_max = min(f.v1, f.v2), max(f.v1, f.v2)
            ruta_imagen = self._buscar_imagen(v_min, v_max)
            
            try:
                if not ruta_imagen:
                    raise FileNotFoundError("Imagen no encontrada")
                    
                img = Image.open(ruta_imagen)
                es_horizontal = img.width > img.height
                
                if f.es_doble:
                    if es_horizontal:
                        img = img.resize((ancho_largo, ancho_corto), getattr(Image, 'LANCZOS', Image.Resampling.LANCZOS))
                        img = img.rotate(90, expand=True)
                    else:
                        img = img.resize((ancho_corto, ancho_largo), getattr(Image, 'LANCZOS', Image.Resampling.LANCZOS))
                    ancho_actual = ancho_corto
                else:
                    if not es_horizontal:
                        img = img.resize((ancho_corto, ancho_largo), getattr(Image, 'LANCZOS', Image.Resampling.LANCZOS))
                        img = img.rotate(90, expand=True) 
                    else:
                        img = img.resize((ancho_largo, ancho_corto), getattr(Image, 'LANCZOS', Image.Resampling.LANCZOS))
                    
                    if f.v1 > f.v2:
                        img = img.rotate(180)
                    ancho_actual = ancho_largo

                img_tk = ImageTk.PhotoImage(img)
                self.imagenes_tablero.append(img_tk)
                self.canvas_tablero.create_image(x_actual, y_centro, image=img_tk, anchor=tk.W)
                x_actual += ancho_actual + espaciado
                
            except Exception as e:
                self.canvas_tablero.create_text(x_actual + (ancho_largo//2), y_centro, text=str(f), fill="#FF5722", font=("Arial", 12, "bold"))
                x_actual += ancho_largo + espaciado

        self.canvas_tablero.config(scrollregion=(0, 0, x_actual + 40, 200))
        self.canvas_tablero.xview_moveto(1.0) 

    def actualizar_ui(self):
        self.lbl_agente.config(text=f"Gem (IA) - {len(self.juego.mano_agente)} fichas")
        self.lbl_info.config(text=f"Dificultad: {self.dificultad.get()} | Tu turno, Kurai | Pozo: {len(self.juego.pozo)}")
        
        # Actualización del HUD de Extremos
        if self.juego.tablero:
            self.lbl_extremos.config(text=f"👈 Izquierda: [ {self.juego.extremo_izq} ]      |      Derecha: [ {self.juego.extremo_der} ] 👉", fg="#2196F3")
        else:
            self.lbl_extremos.config(text="Mesa vacía. Juega tu primera ficha.", fg="#4CAF50")
        
        self.renderizar_agente()
        self.renderizar_tablero()
        self.renderizar_humano()
        
        self.verificar_fin_juego()

    def accion_humano(self, lado):
        if self.idx_seleccionado is None:
            messagebox.showwarning("Atención", "Haz clic sobre una ficha de tu mano para seleccionarla primero.")
            return

        ficha = self.juego.mano_humano[self.idx_seleccionado]
        validas = self.juego.jugadas_validas(self.juego.mano_humano)

        jugada_valida = False
        for f, l in validas:
            if f == ficha and (l == lado or l == 'ambos' or not self.juego.tablero):
                jugada_valida = True
                break

        if jugada_valida:
            lado_final = lado if self.juego.tablero else 'der'
            self.juego.jugar_ficha(ficha, lado_final, jugador_es_humano=True)
            self.juego.turno_humano = False
            self.idx_seleccionado = None
            self.actualizar_ui()
            if not self.verificar_fin_juego():
                self.lbl_info.config(text="Turno de Gem...", fg="#FF5722")
                self.update_idletasks()
                self.after(1200, self.turno_agente)
        else:
            messagebox.showerror("Movimiento Inválido", "Esa ficha no coincide en ese extremo.")

    def robar_o_pasar_humano(self):
        validas = self.juego.jugadas_validas(self.juego.mano_humano)
        if validas:
            messagebox.showinfo("Aviso", "Aún tienes fichas válidas. ¡Debes jugar!")
            return
            
        if self.juego.pozo:
            self.juego.robar(jugador_es_humano=True)
            self.actualizar_ui()
        else:
            self.juego.turno_humano = False
            self.lbl_info.config(text="Turno de Gem...", fg="#FF5722")
            self.after(1200, self.turno_agente)

    def turno_agente(self):
        validas = self.juego.jugadas_validas(self.juego.mano_agente)
        while not validas and self.juego.pozo:
            self.juego.robar(jugador_es_humano=False)
            validas = self.juego.jugadas_validas(self.juego.mano_agente)
            
        if not validas:
            self.juego.turno_humano = True
            self.lbl_info.config(text="Tu turno, Kurai", fg="#333333")
            self.actualizar_ui()
            if not self.juego.jugadas_validas(self.juego.mano_humano) and not self.juego.pozo:
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
                numero_expuesto = f.v1 if (l == 'der' and f.v2 == self.juego.extremo_der) or (l == 'izq' and f.v2 == self.juego.extremo_izq) else f.v2
                if not self.juego.tablero: numero_expuesto = f.v1
                puntaje = conteos[numero_expuesto]
                if puntaje > mejor_puntaje:
                    mejor_puntaje = puntaje
                    ficha_elegida, lado = f, l

        lado_final = 'der' if lado == 'ambos' else lado
        self.juego.jugar_ficha(ficha_elegida, lado_final, jugador_es_humano=False)
        
        self.juego.turno_humano = True
        self.lbl_info.config(text="Tu turno, Kurai", fg="#333333")
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
        if tranque:
            p = sum(f.peso for f in self.juego.mano_humano)
            pa = sum(f.peso for f in self.juego.mano_agente)
            mensaje = f"¡Tranque!\nKurai: {p} puntos\nGem: {pa} puntos"
            color = "#FF9800"
        else:
            if ganador == "Humano":
                mensaje = "¡Felicidades Kurai!\nHas derrotado a la IA."
                color = "#4CAF50"
            else:
                mensaje = "¡Victoria para Gem (IA)!"
                color = "#F44336"

        tk.Label(self, text=mensaje, font=("Arial", 24, "bold"), bg="#FFFFFF", fg=color).pack(pady=100)
        tk.Button(self, text="Volver al Menú", font=("Arial", 16), bg="#333333", fg="white", relief="flat", padx=20, pady=10, command=self.pantalla_inicio).pack(pady=20)

    def limpiar_ventana(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = InterfazDomino()
    app.mainloop()