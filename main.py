import customtkinter as ctk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import os
import datetime
import logica
import pygame
from pygame import mixer
import pandas as pd
import numpy as np

# ================== CONFIGURACIÓN GENERAL ==================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ================== INICIALIZAR MÚSICA ==================
mixer.init()
volumen_actual = 0.5

def iniciar_musica():
    try:
        ruta = os.path.join(os.path.dirname(__file__), "musica_fondo.mp3")
        if os.path.exists(ruta):
            mixer.music.load(ruta)
            mixer.music.set_volume(volumen_actual)
            mixer.music.play(-1)
    except: pass

def cambiar_volumen(valor):
    global volumen_actual
    volumen_actual = float(valor) / 100
    mixer.music.set_volume(volumen_actual)

# ================== CONFIGURACIÓN VENTANA ==================
ANCHO = 1400
ALTO = 780

app = ctk.CTk()
app.title("Sistema de Gráficos Estadísticos")

# Centrar ventana
pantalla_ancho = app.winfo_screenwidth()
pantalla_alto = app.winfo_screenheight()
x0 = int((pantalla_ancho / 2) - (ANCHO / 2))
y0 = int((pantalla_alto / 2) - (ALTO / 2))
app.geometry(f"{ANCHO}x{ALTO}+{x0}+{y0}")
app.resizable(False, False)

# ================== VARIABLES GLOBALES ==================
tema_actual = None
canvas = None
fig_actual = None
estadisticas_actuales = None
ruta_imagen_actual = None
dataset_actual = None

# ================== FUNCIONES ==================
def leer_texto_hilo(texto, idioma=None):
    threading.Thread(target=lambda: logica.leer_texto(texto, idioma), daemon=True).start()

def cambiar_idioma(idioma):
    if logica.cambiar_idioma(idioma):
        if tema_actual:
            texto_teoria.configure(text=logica.teoria[tema_actual][idioma])

def cambiar_tema(tema):
    global tema_actual, estadisticas_actuales
    tema_actual = tema
    texto_teoria.configure(text=logica.teoria[tema][logica.idioma_actual])
    btn_generar.configure(state="normal")
    limpiar_grafico()
    actualizar_labels(tema)
    leer_texto_hilo(logica.teoria[tema][logica.idioma_actual])
    estadisticas_actuales = None
    texto_estadisticas.configure(text="📊 ESTADÍSTICAS")

def mostrar_terminos():
    global tema_actual, estadisticas_actuales
    tema_actual = None
    texto_teoria.configure(text=logica.obtener_terminos(logica.idioma_actual))
    btn_generar.configure(state="disabled")
    limpiar_grafico()
    leer_texto_hilo(logica.obtener_terminos(logica.idioma_actual))
    estadisticas_actuales = None
    texto_estadisticas.configure(text="📊 ESTADÍSTICAS")

def actualizar_labels(tema):
    if tema == "Histogramas":
        label_x.configure(text="📊 Datos:")
        entry_x.configure(placeholder_text="12,15,18,20,22")
        label_y.grid_remove(); entry_y.grid_remove()
        label_cat.grid_remove(); entrada_cat.grid_remove()
    elif tema == "Barras":
        label_x.configure(text="📊 Valores:")
        entry_x.configure(placeholder_text="10,20,15,30")
        label_cat.grid(); entrada_cat.grid()
        label_cat.configure(text="🏷️ Cats:")
        entrada_cat.configure(placeholder_text="A,B,C,D")
        label_y.grid_remove(); entry_y.grid_remove()
    elif tema == "Pastel":
        label_x.configure(text="🥧 Valores:")
        entry_x.configure(placeholder_text="30,25,45,60")
        label_cat.grid(); entrada_cat.grid()
        label_cat.configure(text="🏷️ Cats:")
        entrada_cat.configure(placeholder_text="A,B,C,D")
        label_y.grid_remove(); entry_y.grid_remove()
    elif tema == "Dispersion":
        label_x.configure(text="📈 X:")
        entry_x.configure(placeholder_text="1,2,3,4,5")
        label_y.grid(); entry_y.grid()
        label_y.configure(text="📉 Y:")
        entry_y.configure(placeholder_text="2,4,3,5,6")
        label_cat.grid_remove(); entrada_cat.grid_remove()

def limpiar_grafico():
    global canvas, fig_actual
    if canvas:
        canvas.get_tk_widget().destroy()
        canvas = None
    fig_actual = None

def actualizar_lista():
    nombres = logica.obtener_todos_los_nombres()
    txt_nombres.configure(state="normal")
    txt_nombres.delete("1.0", "end")
    for n in nombres[-10:]:
        txt_nombres.insert("end", f"• {n}\n")
    txt_nombres.configure(state="disabled")

def guardar_datos():
    nombre = entry_nombre.get().strip()
    if not nombre: return
    
    if tema_actual == "Histogramas":
        try:
            xs = logica.limpiar_lista(entry_x.get(), float)
            if logica.guardar_datos_persona(nombre, xs, [0]*len(xs)):
                messagebox.showinfo("OK", "Guardado")
                actualizar_lista()
                limpiar_campos()
        except: messagebox.showerror("Error", "Formato incorrecto")
    
    elif tema_actual in ["Barras", "Pastel"]:
        try:
            cats = logica.limpiar_lista(entrada_cat.get(), str)
            vals = logica.limpiar_lista(entry_x.get(), float)
            if len(cats) != len(vals):
                messagebox.showerror("Error", "Misma cantidad")
                return
            if logica.guardar_datos_categorias(nombre, cats, vals):
                messagebox.showinfo("OK", "Guardado")
                actualizar_lista()
                limpiar_campos()
        except: messagebox.showerror("Error", "Formato incorrecto")
    
    elif tema_actual == "Dispersion":
        try:
            xs = logica.limpiar_lista(entry_x.get(), float)
            ys = logica.limpiar_lista(entry_y.get(), float)
            if len(xs) != len(ys):
                messagebox.showerror("Error", "Misma cantidad")
                return
            if logica.guardar_datos_persona(nombre, xs, ys):
                messagebox.showinfo("OK", "Guardado")
                actualizar_lista()
                limpiar_campos()
        except: messagebox.showerror("Error", "Formato incorrecto")

def cargar_editar():
    nombre = entry_editar.get().strip()
    if not nombre: return
    datos = logica.obtener_datos_persona(nombre)
    if datos.empty: return
    
    if tema_actual in ["Histogramas", "Dispersion"]:
        entry_x.delete(0, "end")
        entry_x.insert(0, ",".join(map(str, datos["Edad"].tolist())))
        if tema_actual == "Dispersion":
            entry_y.delete(0, "end")
            entry_y.insert(0, ",".join(map(str, datos["Altura"].tolist())))
    elif tema_actual in ["Barras", "Pastel"] and 'Categoria' in datos.columns:
        cats = datos['Categoria'].dropna().tolist()
        if cats and cats[0]:
            entrada_cat.delete(0, "end")
            entrada_cat.insert(0, ",".join(cats))
            entry_x.delete(0, "end")
            entry_x.insert(0, ",".join(map(str, datos["Edad"].tolist())))
    
    entry_nombre.delete(0, "end")
    entry_nombre.insert(0, nombre)

def limpiar_campos():
    entry_x.delete(0, "end")
    entry_y.delete(0, "end")
    entrada_cat.delete(0, "end")
    entry_nombre.delete(0, "end")
    entry_editar.delete(0, "end")
    entry_graf.delete(0, "end")

def cargar_dataset():
    global dataset_actual
    archivo = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
    if archivo:
        df, error = logica.cargar_dataset(archivo)
        if error: messagebox.showerror("Error", error)
        else:
            dataset_actual = df
            messagebox.showinfo("OK", f"{df.shape[0]} filas")
            usar_dataset()

def usar_dataset():
    if not dataset_actual or not tema_actual: return
    cols_num = logica.obtener_columnas_numericas(dataset_actual)
    if not cols_num: return
    
    ventana = ctk.CTkToplevel(app)
    ventana.title("Seleccionar")
    ventana.geometry("300x200")
    ventana.transient(app)
    
    if tema_actual in ["Histogramas", "Barras", "Pastel"]:
        ctk.CTkLabel(ventana, text="Columna:").pack(pady=5)
        combo = ctk.CTkComboBox(ventana, values=cols_num, width=200)
        combo.pack(pady=5)
        combo.set(cols_num[0])
        
        def aplicar():
            vals = dataset_actual[combo.get()].dropna().tolist()
            nombre = f"data_{datetime.datetime.now().strftime('%H%M%S')}"
            logica.guardar_datos_persona(nombre, vals, [0]*len(vals))
            entry_graf.delete(0, "end")
            entry_graf.insert(0, nombre)
            ventana.destroy()
            generar_grafico()
        
        ctk.CTkButton(ventana, text="Aplicar", command=aplicar).pack(pady=15)

def generar_grafico():
    global fig_actual, canvas, tema_actual, estadisticas_actuales, ruta_imagen_actual
    
    if not tema_actual: return
    nombre = entry_graf.get().strip()
    if not nombre:
        nombres = logica.obtener_todos_los_nombres()
        if nombres: nombre = nombres[-1]
        else: return
    
    datos = logica.obtener_datos_persona(nombre)
    if datos.empty: return
    
    limpiar_grafico()
    fig_actual = plt.Figure(figsize=(5, 3.5), dpi=90)
    ax = fig_actual.add_subplot(111)
    
    if tema_actual == "Histogramas":
        vals = datos["Edad"].dropna().tolist()
        ax.hist(vals, bins='auto', edgecolor='black', alpha=0.7)
        estadisticas_actuales = logica.calcular_estadisticas(vals)
    elif tema_actual == "Barras":
        if 'Categoria' in datos.columns and datos['Categoria'].iloc[0]:
            df_agg = datos.groupby('Categoria')['Edad'].mean()
            ax.bar(df_agg.index, df_agg.values, color='skyblue')
            vals = df_agg.values.tolist()
        else:
            vals = datos["Edad"].value_counts().values.tolist()
            ax.bar(range(len(vals)), vals, color='skyblue')
        estadisticas_actuales = logica.calcular_estadisticas(vals)
    elif tema_actual == "Pastel":
        if 'Categoria' in datos.columns and datos['Categoria'].iloc[0]:
            df_agg = datos.groupby('Categoria')['Edad'].sum()
            ax.pie(df_agg.values, labels=df_agg.index, autopct='%1.0f%%')
            vals = df_agg.values.tolist()
        else:
            vals = datos["Edad"].value_counts().head(4).values.tolist()
            ax.pie(vals, autopct='%1.0f%%')
        estadisticas_actuales = logica.calcular_estadisticas(vals)
    elif tema_actual == "Dispersion":
        x = datos["Edad"].dropna().tolist()
        y = datos["Altura"].dropna().tolist()
        ax.scatter(x, y, s=30)
        estadisticas_actuales = logica.calcular_estadisticas_bivariadas(x, y)
    
    ax.set_title(f"{tema_actual[:4]} - {nombre}", fontsize=9)
    fig_actual.tight_layout()
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_imagen_actual = os.path.join(logica.carpeta_guardado, f"temp_{timestamp}.png")
    fig_actual.savefig(ruta_imagen_actual, dpi=150, bbox_inches="tight")
    
    canvas = FigureCanvasTkAgg(fig_actual, master=frame_canvas)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    mostrar_estadisticas(estadisticas_actuales)
    if estadisticas_actuales:
        threading.Timer(0.5, lambda: logica.leer_estadisticas(estadisticas_actuales, tema_actual, logica.idioma_actual)).start()

def mostrar_estadisticas(est):
    if not est:
        texto_estadisticas.configure(text="📊 ESTADÍSTICAS")
        return
    txt = "📊 ESTADÍSTICAS\n"
    if "correlacion" in est:
        txt += f"r={est['correlacion']:.2f}\n"
        txt += f"X̄={est.get('media_x',0):.1f} σx={est.get('desviacion_x',0):.1f}\n"
        txt += f"Ȳ={est.get('media_y',0):.1f} σy={est.get('desviacion_y',0):.1f}"
    else:
        txt += f"μ={est.get('media',0):.1f}\n"
        txt += f"Md={est.get('mediana',0):.1f}\n"
        txt += f"Mo={est.get('moda',0):.1f}\n"
        txt += f"σ={est.get('desviacion',0):.1f}\n"
        txt += f"Min={est.get('minimo',0):.1f} Max={est.get('maximo',0):.1f}"
    txt += f"\nn={est.get('total',0)}"
    texto_estadisticas.configure(text=txt)

def guardar_img():
    if fig_actual:
        nombre = entry_graf.get().strip() or "grafico"
        logica.guardar_grafico(fig_actual, f"{nombre}_{tema_actual}")
        messagebox.showinfo("OK", "Imagen guardada")

def exportar_pdf():
    if estadisticas_actuales:
        nombre = entry_graf.get().strip() or "reporte"
        logica.generar_reporte_pdf(nombre, estadisticas_actuales, tema_actual, ruta_imagen_actual)
        messagebox.showinfo("OK", "PDF guardado")

def ejemplo():
    if not tema_actual: return
    limpiar_grafico()
    fig_actual = logica.mostrar_grafico_ejemplo(tema_actual)
    if fig_actual:
        canvas = FigureCanvasTkAgg(fig_actual, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        datos = logica.cargar_datos_ejemplo()
        if tema_actual == "Histogramas":
            est = logica.calcular_estadisticas(datos["Edad"].tolist())
        elif tema_actual == "Dispersion":
            est = logica.calcular_estadisticas_bivariadas(datos["Edad"].tolist(), datos["Altura"].tolist())
        else:
            est = logica.calcular_estadisticas(datos["Edad"].tolist())
        mostrar_estadisticas(est)

# ================== INTERFAZ ULTRA COMPACTA ==================
titulo = ctk.CTkLabel(app, text="📊 SISTEMA DE GRÁFICOS", font=ctk.CTkFont(size=16, weight="bold"))
titulo.pack(pady=(5, 2))

# Barra superior mini
barra = ctk.CTkFrame(app, height=30)
barra.pack(fill="x", padx=10, pady=2)
ctk.CTkButton(barra, text="☀", width=25, height=22, command=lambda: ctk.set_appearance_mode("light")).pack(side="left", padx=1)
ctk.CTkButton(barra, text="🌙", width=25, height=22, command=lambda: ctk.set_appearance_mode("dark")).pack(side="left", padx=1)
ctk.CTkButton(barra, text="ES", width=30, height=22, command=lambda: cambiar_idioma("español")).pack(side="left", padx=5)
ctk.CTkButton(barra, text="EN", width=30, height=22, command=lambda: cambiar_idioma("ingles")).pack(side="left", padx=1)

# Contenedor principal
cont = ctk.CTkFrame(app)
cont.pack(fill="both", expand=True, padx=10, pady=2)
cont.grid_columnconfigure(0, weight=1, minsize=250)
cont.grid_columnconfigure(1, weight=2, minsize=550)
cont.grid_columnconfigure(2, weight=1, minsize=250)
cont.grid_rowconfigure(0, weight=1)

# ================== PANEL IZQUIERDO ==================
izq = ctk.CTkFrame(cont)
izq.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

# GRÁFICOS
ctk.CTkLabel(izq, text="📊 GRÁFICOS", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=(5, 2))
grid = ctk.CTkFrame(izq, fg_color="transparent")
grid.pack(padx=2)
for i, t in enumerate(["Histogramas", "Barras", "Pastel", "Dispersion"]):
    r, c = i // 2, i % 2
    btn = ctk.CTkButton(grid, text=t[:4], width=85, height=25, font=ctk.CTkFont(size=10),
                       command=lambda x=t: cambiar_tema(x))
    btn.grid(row=r, column=c, padx=2, pady=1)

# Términos y Ejemplo
frame_te = ctk.CTkFrame(izq, fg_color="transparent")
frame_te.pack(pady=2)
ctk.CTkButton(frame_te, text="📚 Términos", width=80, height=22, font=ctk.CTkFont(size=9), command=mostrar_terminos).pack(side="left", padx=1)
ctk.CTkButton(frame_te, text="📈 Ejemplo", width=80, height=22, font=ctk.CTkFont(size=9), command=ejemplo).pack(side="left", padx=1)

# Separador
ctk.CTkFrame(izq, height=1, fg_color="gray").pack(fill="x", padx=5, pady=4)

# DATOS
ctk.CTkLabel(izq, text="📋 DATOS", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=5, pady=(0, 1))

label_x = ctk.CTkLabel(izq, text="📊 Datos:", font=ctk.CTkFont(size=9))
label_x.pack(anchor="w", padx=8)
entry_x = ctk.CTkEntry(izq, placeholder_text="1,2,3", height=22, font=ctk.CTkFont(size=9))
entry_x.pack(fill="x", padx=5, pady=1)

label_y = ctk.CTkLabel(izq, text="📉 Y:", font=ctk.CTkFont(size=9))
label_y.pack(anchor="w", padx=8)
label_y.pack_forget()
entry_y = ctk.CTkEntry(izq, placeholder_text="4,5,6", height=22, font=ctk.CTkFont(size=9))
entry_y.pack(fill="x", padx=5, pady=1)
entry_y.pack_forget()

label_cat = ctk.CTkLabel(izq, text="🏷️ Cats:", font=ctk.CTkFont(size=9))
label_cat.pack(anchor="w", padx=8)
label_cat.pack_forget()
entrada_cat = ctk.CTkEntry(izq, placeholder_text="A,B,C", height=22, font=ctk.CTkFont(size=9))
entrada_cat.pack(fill="x", padx=5, pady=1)
entrada_cat.pack_forget()

# Botones acción
frame_acc = ctk.CTkFrame(izq, fg_color="transparent")
frame_acc.pack(pady=1)
ctk.CTkButton(frame_acc, text="💾", width=40, height=22, font=ctk.CTkFont(size=10), command=guardar_datos).pack(side="left", padx=1)
ctk.CTkButton(frame_acc, text="✏️", width=40, height=22, font=ctk.CTkFont(size=10), command=cargar_editar).pack(side="left", padx=1)
ctk.CTkButton(frame_acc, text="🗑️", width=40, height=22, font=ctk.CTkFont(size=10), command=limpiar_campos).pack(side="left", padx=1)

# Nombre
ctk.CTkLabel(izq, text="👤 Nombre:", font=ctk.CTkFont(size=9)).pack(anchor="w", padx=8, pady=(2, 0))
entry_nombre = ctk.CTkEntry(izq, placeholder_text="Nombre", height=22, font=ctk.CTkFont(size=9))
entry_nombre.pack(fill="x", padx=5, pady=1)

# Separador
ctk.CTkFrame(izq, height=1, fg_color="gray").pack(fill="x", padx=5, pady=4)

# CARGA
ctk.CTkLabel(izq, text="📁 CARGA", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=5)
ctk.CTkButton(izq, text="📂 CSV", height=24, font=ctk.CTkFont(size=9), command=cargar_dataset).pack(fill="x", padx=5, pady=1)

# Separador
ctk.CTkFrame(izq, height=1, fg_color="gray").pack(fill="x", padx=5, pady=4)

# GUARDADOS
frame_header = ctk.CTkFrame(izq, fg_color="transparent")
frame_header.pack(fill="x", padx=5, pady=1)
ctk.CTkLabel(frame_header, text="📋 Guardados:", font=ctk.CTkFont(size=10, weight="bold")).pack(side="left")
ctk.CTkButton(frame_header, text="🔄", width=20, height=20, font=ctk.CTkFont(size=9), command=actualizar_lista).pack(side="right")

txt_nombres = ctk.CTkTextbox(izq, height=70, font=ctk.CTkFont(size=8))
txt_nombres.pack(fill="x", padx=5, pady=1)
txt_nombres.configure(state="disabled")

# Editar
ctk.CTkLabel(izq, text="✏️ Editar:", font=ctk.CTkFont(size=9)).pack(anchor="w", padx=8, pady=(2, 0))
entry_editar = ctk.CTkEntry(izq, placeholder_text="Nombre", height=22, font=ctk.CTkFont(size=9))
entry_editar.pack(fill="x", padx=5, pady=1)

# ================== PANEL CENTRAL ==================
centro = ctk.CTkFrame(cont)
centro.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
centro.grid_rowconfigure(0, weight=1)
centro.grid_rowconfigure(1, weight=1)
centro.grid_columnconfigure(0, weight=1)

frame_teoria = ctk.CTkFrame(centro)
frame_teoria.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
texto_teoria = ctk.CTkLabel(frame_teoria, text="Seleccione un gráfico", font=ctk.CTkFont(size=11), wraplength=500)
texto_teoria.pack(expand=True, padx=5, pady=5)

frame_inputs = ctk.CTkFrame(centro)
frame_inputs.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

# ================== PANEL DERECHO ==================
der = ctk.CTkFrame(cont)
der.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)

ctk.CTkLabel(der, text="📈 VISUALIZACIÓN", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(3, 1))

frame_canvas = ctk.CTkFrame(der, height=200)
frame_canvas.pack(fill="both", expand=True, padx=3, pady=2)

frame_stats = ctk.CTkFrame(der)
frame_stats.pack(fill="both", expand=True, padx=3, pady=2)
texto_estadisticas = ctk.CTkLabel(frame_stats, text="📊 ESTADÍSTICAS", font=ctk.CTkFont(size=10), justify="left")
texto_estadisticas.pack(expand=True, padx=3, pady=3)

# ================== PANEL INFERIOR ==================
inf = ctk.CTkFrame(app)
inf.pack(fill="x", padx=10, pady=2)
inf.grid_columnconfigure(1, weight=1)

btn_generar = ctk.CTkButton(inf, text="📊 Generar", width=70, height=25, font=ctk.CTkFont(size=10), state="disabled", command=generar_grafico)
btn_generar.grid(row=0, column=0, padx=2, pady=2)

entry_graf = ctk.CTkEntry(inf, placeholder_text="Nombre", width=180, height=25, font=ctk.CTkFont(size=9))
entry_graf.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

ctk.CTkButton(inf, text="💾 Img", width=50, height=25, font=ctk.CTkFont(size=9), command=guardar_img).grid(row=0, column=2, padx=2)
ctk.CTkButton(inf, text="📄 PDF", width=50, height=25, font=ctk.CTkFont(size=9), command=exportar_pdf).grid(row=0, column=3, padx=2)

frame_vol = ctk.CTkFrame(inf, fg_color="transparent")
frame_vol.grid(row=0, column=4, padx=(5, 2))
ctk.CTkLabel(frame_vol, text="🔊", font=ctk.CTkFont(size=12)).pack(side="left", padx=1)
slider_vol = ctk.CTkSlider(frame_vol, from_=0, to=100, width=60, command=cambiar_volumen)
slider_vol.set(50)
slider_vol.pack(side="left")

# ================== INICIALIZAR ==================
logica.asegurar_csv()
actualizar_lista()
iniciar_musica()

if __name__ == "__main__":
    app.mainloop()