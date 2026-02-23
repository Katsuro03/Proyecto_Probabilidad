import customtkinter as ctk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import os
import datetime  # <-- ESTA LÍNEA ES CRUCIAL, ESTABA FALTANDO
import logica
import pygame
from pygame import mixer
import pandas as pd
import numpy as np

# ================== CONFIGURACIÓN GENERAL ==================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ================== INICIALIZAR MÚSICA DE FONDO ==================
mixer.init()
volumen_actual = 0.5

def iniciar_musica():
    try:
        ruta_musica = os.path.join(os.path.dirname(__file__), "musica_fondo.mp3")
        if os.path.exists(ruta_musica):
            mixer.music.load(ruta_musica)
            mixer.music.set_volume(volumen_actual)
            mixer.music.play(-1)
    except Exception as e:
        print(f"Error al reproducir música: {e}")

def cambiar_volumen(valor):
    global volumen_actual
    volumen_actual = float(valor) / 100
    mixer.music.set_volume(volumen_actual)

# ================== CONFIGURACIÓN VENTANA ==================
ANCHO = 1400  # <-- REDUCIDO PARA QUE QUEPA MEJOR
ALTO = 800

app = ctk.CTk()
app.title("Sistema de Interpretación de Gráficos Estadísticos")

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
tamaño_base = 13
estadisticas_actuales = None
ruta_imagen_actual = None
dataset_actual = None

# ================== FUNCIONES DE ACCESIBILIDAD ==================
def cambiar_tema_visual(modo):
    if modo == "Claro":
        ctk.set_appearance_mode("light")
    elif modo == "Oscuro":
        ctk.set_appearance_mode("dark")

def cambiar_tamaño(valor):
    escala = int(valor)
    nuevo_tamaño = int(tamaño_base * (escala / 100))
    titulo.configure(font=("Arial", nuevo_tamaño + 8))
    texto_teoria.configure(font=("Arial", nuevo_tamaño))
    texto_estadisticas.configure(font=("Arial", nuevo_tamaño - 1))

def leer_texto_hilo(texto, idioma=None):
    def run():
        try:
            logica.leer_texto(texto, idioma)
        except Exception as e:
            messagebox.showerror("Error de audio", str(e))
    threading.Thread(target=run, daemon=True).start()

def cambiar_idioma(idioma):
    if logica.cambiar_idioma(idioma):
        label_idioma.configure(text=f"Idioma: {idioma.capitalize()}")
        if tema_actual:
            texto_teoria.configure(text=logica.teoria[tema_actual][idioma])
        return True
    return False

# ================== FUNCIONES DE NAVEGACIÓN ==================
def cambiar_tema(tema):
    global tema_actual, estadisticas_actuales
    tema_actual = tema
    texto_teoria.configure(text=logica.teoria[tema][logica.idioma_actual])
    boton_hacer.configure(state="normal")
    limpiar_grafico()
    actualizar_labels_segun_tema(tema)
    leer_texto_hilo(logica.teoria[tema][logica.idioma_actual], logica.idioma_actual)
    estadisticas_actuales = None
    texto_estadisticas.configure(text="📊 ESTADÍSTICAS:\n\nSeleccione un gráfico para ver estadísticas")

def mostrar_terminos():
    global tema_actual, estadisticas_actuales
    tema_actual = None
    terminos = logica.obtener_terminos(logica.idioma_actual)
    texto_teoria.configure(text=terminos)
    boton_hacer.configure(state="disabled")
    limpiar_grafico()
    leer_texto_hilo(terminos, logica.idioma_actual)
    estadisticas_actuales = None
    texto_estadisticas.configure(text="📊 ESTADÍSTICAS:\n\nSeleccione un gráfico para ver estadísticas")

def actualizar_labels_segun_tema(tema):
    if tema == "Histogramas":
        label_x.configure(text="📊 Datos (una variable):")
        entry_x.configure(placeholder_text="Ej: 12,15,18,20,22,25,30")
        label_y.grid_remove()
        entry_y.grid_remove()
        label_cat.grid_remove()
        entrada_cat.grid_remove()
    elif tema == "Barras":
        label_x.configure(text="📊 Valores numéricos:")
        entry_x.configure(placeholder_text="Ej: 10,20,15,30,25")
        label_cat.grid()
        entrada_cat.grid()
        label_cat.configure(text="🏷️ Categorías:")
        entrada_cat.configure(placeholder_text="Ej: Manzanas,Peras,Naranjas,UVAS")
        label_y.grid_remove()
        entry_y.grid_remove()
    elif tema == "Pastel":
        label_x.configure(text="🥧 Valores numéricos:")
        entry_x.configure(placeholder_text="Ej: 30,25,45,60,15")
        label_cat.grid()
        entrada_cat.grid()
        label_cat.configure(text="🏷️ Categorías:")
        entrada_cat.configure(placeholder_text="Ej: Ventas,Marketing,Producción,IT")
        label_y.grid_remove()
        entry_y.grid_remove()
    elif tema == "Dispersion":
        label_x.configure(text="📈 Variable X:")
        entry_x.configure(placeholder_text="Ej: 1,2,3,4,5,6,7,8")
        label_y.grid()
        entry_y.grid()
        label_y.configure(text="📉 Variable Y:")
        entry_y.configure(placeholder_text="Ej: 2,4,3,5,6,7,8,9")
        label_cat.grid_remove()
        entrada_cat.grid_remove()

# ================== FUNCIONES DE CARGA DE DATASETS ==================
def cargar_dataset():
    global dataset_actual
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo CSV",
        filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
    )
    if archivo:
        df, error = logica.cargar_dataset(archivo)
        if error:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{error}")
        else:
            dataset_actual = df
            preview = df.head(10).to_string()
            messagebox.showinfo(
                "✅ Dataset cargado",
                f"Dataset cargado exitosamente\n\n"
                f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas\n"
                f"Columnas numéricas: {', '.join(logica.obtener_columnas_numericas(df))}\n\n"
                f"Vista previa:\n{preview}"
            )
            usar_dataset_para_grafico()

def usar_dataset_para_grafico():
    global dataset_actual, tema_actual
    if dataset_actual is None:
        messagebox.showerror("Error", "Primero cargue un dataset")
        return
    if tema_actual is None:
        messagebox.showerror("Error", "Seleccione un tipo de gráfico")
        return
    
    columnas_numericas = logica.obtener_columnas_numericas(dataset_actual)
    if len(columnas_numericas) == 0:
        messagebox.showerror("Error", "El dataset no tiene columnas numéricas")
        return
    
    ventana_columnas = ctk.CTkToplevel(app)
    ventana_columnas.title("Seleccionar columnas")
    ventana_columnas.geometry("450x350")
    ventana_columnas.transient(app)
    ventana_columnas.grab_set()
    
    ctk.CTkLabel(
        ventana_columnas,
        text="📊 Seleccione las columnas para el gráfico",
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=15)
    
    if tema_actual in ["Histogramas", "Barras", "Pastel"]:
        ctk.CTkLabel(ventana_columnas, text="Columna de valores:", font=ctk.CTkFont(size=14)).pack(pady=5)
        columna_valores = ctk.CTkComboBox(ventana_columnas, values=columnas_numericas, width=300)
        columna_valores.pack(pady=5)
        columna_valores.set(columnas_numericas[0])
        
        if tema_actual in ["Barras", "Pastel"]:
            ctk.CTkLabel(ventana_columnas, text="Columna de categorías:", font=ctk.CTkFont(size=14)).pack(pady=5)
            columnas_texto = dataset_actual.select_dtypes(include=['object']).columns.tolist()
            if not columnas_texto:
                columnas_texto = ["No hay columnas de texto"]
            columna_cat = ctk.CTkComboBox(ventana_columnas, values=columnas_texto, width=300)
            columna_cat.pack(pady=5)
            columna_cat.set(columnas_texto[0] if columnas_texto else "No disponible")
    
    elif tema_actual == "Dispersion":
        ctk.CTkLabel(ventana_columnas, text="Columna para X:", font=ctk.CTkFont(size=14)).pack(pady=5)
        columna_x = ctk.CTkComboBox(ventana_columnas, values=columnas_numericas, width=300)
        columna_x.pack(pady=5)
        columna_x.set(columnas_numericas[0])
        ctk.CTkLabel(ventana_columnas, text="Columna para Y:", font=ctk.CTkFont(size=14)).pack(pady=5)
        columna_y = ctk.CTkComboBox(ventana_columnas, values=columnas_numericas, width=300)
        columna_y.pack(pady=5)
        columna_y.set(columnas_numericas[1] if len(columnas_numericas) > 1 else columnas_numericas[0])
    
    def aplicar_seleccion():
        nombre = f"dataset_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            if tema_actual in ["Histogramas", "Barras", "Pastel"]:
                valores = dataset_actual[columna_valores.get()].dropna().tolist()
                if tema_actual in ["Barras", "Pastel"] and columna_cat.get() != "No disponible" and columna_cat.get() != "No hay columnas de texto":
                    categorias = dataset_actual[columna_cat.get()].astype(str).tolist()
                    df_temp = pd.DataFrame({'categoria': categorias[:len(valores)], 'valor': valores[:len(categorias)]})
                    df_agrupado = df_temp.groupby('categoria')['valor'].mean().reset_index()
                    logica.guardar_datos_categorias(nombre, df_agrupado['categoria'].tolist(), df_agrupado['valor'].tolist())
                else:
                    logica.guardar_datos_persona(nombre, valores, [0]*len(valores))
            elif tema_actual == "Dispersion":
                x_vals = dataset_actual[columna_x.get()].dropna().tolist()
                y_vals = dataset_actual[columna_y.get()].dropna().tolist()
                min_len = min(len(x_vals), len(y_vals))
                logica.guardar_datos_persona(nombre, x_vals[:min_len], y_vals[:min_len])
            
            entry_nombre_grafica.delete(0, "end")
            entry_nombre_grafica.insert(0, nombre)
            ventana_columnas.destroy()
            generar_grafico()
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar datos: {str(e)}")
    
    ctk.CTkButton(
        ventana_columnas,
        text="✅ Aplicar y generar",
        width=200,
        height=40,
        command=aplicar_seleccion
    ).pack(pady=20)

# ================== FUNCIONES DE MANEJO DE DATOS ==================
def actualizar_lista_nombres():
    nombres = logica.obtener_todos_los_nombres()
    cuadro_nombres.configure(state="normal")
    cuadro_nombres.delete("1.0", "end")
    for n in nombres:
        cuadro_nombres.insert("end", f"  • {n}\n")
    cuadro_nombres.configure(state="disabled")

def guardar_datos():
    nombre = entry_nombre_guardar.get().strip()
    if not nombre:
        messagebox.showerror("Error", "Ingrese un nombre")
        return
    
    if tema_actual == "Histogramas":
        x_txt = entry_x.get().strip()
        if not x_txt:
            messagebox.showerror("Error", "Complete los datos")
            return
        try:
            xs = logica.limpiar_lista(x_txt, float)
            if logica.guardar_datos_persona(nombre, xs, [0]*len(xs)):
                messagebox.showinfo("✅ Éxito", "Datos guardados correctamente")
                actualizar_lista_nombres()
                limpiar_campos()
            else:
                messagebox.showerror("Error", "No se pudieron guardar los datos")
        except:
            messagebox.showerror("Error", "Formato incorrecto. Use: 1,2,3")
    
    elif tema_actual in ["Barras", "Pastel"]:
        cat_txt = entrada_cat.get().strip()
        val_txt = entry_x.get().strip()
        if not cat_txt or not val_txt:
            messagebox.showerror("Error", "Complete todos los campos")
            return
        try:
            categorias = logica.limpiar_lista(cat_txt, str)
            valores = logica.limpiar_lista(val_txt, float)
            if len(categorias) != len(valores):
                messagebox.showerror("Error", "Categorías y valores deben tener la misma cantidad")
                return
            if logica.guardar_datos_categorias(nombre, categorias, valores):
                messagebox.showinfo("✅ Éxito", "Datos guardados correctamente")
                actualizar_lista_nombres()
                limpiar_campos()
            else:
                messagebox.showerror("Error", "No se pudieron guardar los datos")
        except:
            messagebox.showerror("Error", "Formato incorrecto")
    
    elif tema_actual == "Dispersion":
        x_txt = entry_x.get().strip()
        y_txt = entry_y.get().strip()
        if not x_txt or not y_txt:
            messagebox.showerror("Error", "Complete X e Y")
            return
        try:
            xs = logica.limpiar_lista(x_txt, float)
            ys = logica.limpiar_lista(y_txt, float)
            if len(xs) != len(ys):
                messagebox.showerror("Error", "X e Y deben tener la misma cantidad")
                return
            if logica.guardar_datos_persona(nombre, xs, ys):
                messagebox.showinfo("✅ Éxito", "Datos guardados correctamente")
                actualizar_lista_nombres()
                limpiar_campos()
            else:
                messagebox.showerror("Error", "No se pudieron guardar los datos")
        except:
            messagebox.showerror("Error", "Formato incorrecto. Use: 1,2,3")

def cargar_para_editar():
    nombre = entry_nombre_editar.get().strip()
    if not nombre:
        messagebox.showerror("Error", "Ingrese un nombre")
        return
    
    datos = logica.obtener_datos_persona(nombre)
    if datos.empty:
        messagebox.showerror("Error", "Nombre no encontrado")
        return
    
    if tema_actual in ["Histogramas", "Dispersion"]:
        entry_x.delete(0, "end")
        entry_x.insert(0, ",".join(map(str, datos["Edad"].tolist())))
        if tema_actual == "Dispersion":
            entry_y.delete(0, "end")
            entry_y.insert(0, ",".join(map(str, datos["Altura"].tolist())))
    elif tema_actual in ["Barras", "Pastel"]:
        if 'Categoria' in datos.columns and datos['Categoria'].iloc[0]:
            categorias = datos['Categoria'].tolist()
            valores = datos['Edad'].tolist()
            entrada_cat.delete(0, "end")
            entrada_cat.insert(0, ",".join(categorias))
            entry_x.delete(0, "end")
            entry_x.insert(0, ",".join(map(str, valores)))
        else:
            entry_x.delete(0, "end")
            entry_x.insert(0, ",".join(map(str, datos["Edad"].tolist())))
    
    entry_nombre_guardar.delete(0, "end")
    entry_nombre_guardar.insert(0, nombre)
    label_estado_edicion.configure(text=f"✏️ Editando: {nombre}")
    mostrar_datos_persona(nombre)

def mostrar_datos_persona(nombre):
    datos = logica.obtener_datos_persona(nombre)
    cuadro_editar.configure(state="normal")
    cuadro_editar.delete("1.0", "end")
    if datos.empty:
        cuadro_editar.insert("end", "📁 No hay datos para este nombre")
    else:
        cuadro_editar.insert("end", f"📁 Datos de: {nombre}\n")
        cuadro_editar.insert("end", "═" * 45 + "\n")
        for _, row in datos.iterrows():
            if row['Categoria'] and row['Categoria'] != "":
                cuadro_editar.insert("end", f"  • {row['Categoria']}: {row['Edad']}\n")
            else:
                cuadro_editar.insert("end", f"  • Edad: {row['Edad']:>5}  |  Altura: {row['Altura']:>5}\n")
    cuadro_editar.configure(state="disabled")

def limpiar_campos():
    entry_x.delete(0, "end")
    entry_y.delete(0, "end")
    entrada_cat.delete(0, "end")
    entry_nombre_guardar.delete(0, "end")
    entry_nombre_editar.delete(0, "end")
    entry_nombre_grafica.delete(0, "end")
    label_estado_edicion.configure(text="")
    cuadro_editar.configure(state="normal")
    cuadro_editar.delete("1.0", "end")
    cuadro_editar.configure(state="disabled")
    limpiar_grafico()

def limpiar_grafico():
    global canvas, fig_actual, ruta_imagen_actual
    if canvas:
        canvas.get_tk_widget().destroy()
        canvas = None
    fig_actual = None
    ruta_imagen_actual = None

# ================== FUNCIONES DE GRÁFICOS Y ESTADÍSTICAS ==================
def generar_grafico():
    global fig_actual, canvas, tema_actual, estadisticas_actuales, ruta_imagen_actual
    
    if tema_actual is None:
        messagebox.showerror("Error", "Seleccione un tipo de gráfico")
        return
    
    nombre = entry_nombre_grafica.get().strip()
    if not nombre:
        nombres = logica.obtener_todos_los_nombres()
        if nombres:
            nombre = nombres[-1]
            entry_nombre_grafica.insert(0, nombre)
        else:
            messagebox.showerror("Error", "Ingrese un nombre o cargue datos primero")
            return
    
    datos = logica.obtener_datos_persona(nombre)
    if datos.empty:
        messagebox.showerror("Error", f"Nombre '{nombre}' no encontrado")
        return
    
    limpiar_grafico()
    fig_actual = plt.Figure(figsize=(7, 4.5), dpi=100)
    ax = fig_actual.add_subplot(111)
    
    if tema_actual == "Histogramas":
        valores = datos["Edad"].dropna().tolist()
        ax.hist(valores, bins='auto', edgecolor='black', alpha=0.7, color='skyblue')
        ax.set_xlabel("Valores", fontsize=11)
        ax.set_ylabel("Frecuencia", fontsize=11)
        ax.set_title(f"📊 Histograma - {nombre}", fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        estadisticas_actuales = logica.calcular_estadisticas(valores)
        
    elif tema_actual == "Barras":
        if 'Categoria' in datos.columns and datos['Categoria'].iloc[0]:
            df_agg = datos.groupby('Categoria')['Edad'].mean().reset_index()
            bars = ax.bar(df_agg['Categoria'], df_agg['Edad'], color='skyblue', edgecolor='black')
            valores = df_agg['Edad'].tolist()
            for bar, val in zip(bars, valores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height, f'{val:.1f}', ha='center', va='bottom', fontsize=8)
        else:
            conteo = datos["Edad"].value_counts().sort_index()
            bars = ax.bar(conteo.index.astype(str), conteo.values, color='skyblue', edgecolor='black')
            valores = conteo.values.tolist()
            for bar, val in zip(bars, valores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height, f'{val}', ha='center', va='bottom', fontsize=8)
        ax.set_xlabel("Categorías", fontsize=11)
        ax.set_ylabel("Valores", fontsize=11)
        ax.set_title(f"📊 Gráfico de Barras - {nombre}", fontsize=12, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
        estadisticas_actuales = logica.calcular_estadisticas(valores)
        
    elif tema_actual == "Pastel":
        if 'Categoria' in datos.columns and datos['Categoria'].iloc[0]:
            df_agg = datos.groupby('Categoria')['Edad'].sum().reset_index()
            wedges, texts, autotexts = ax.pie(df_agg['Edad'], labels=df_agg['Categoria'], 
                   autopct='%1.1f%%', startangle=90, shadow=True, textprops={'fontsize': 8})
            valores = df_agg['Edad'].tolist()
        else:
            conteo = datos["Edad"].value_counts().head(6)
            wedges, texts, autotexts = ax.pie(conteo.values, labels=conteo.index, 
                   autopct='%1.1f%%', startangle=90, shadow=True, textprops={'fontsize': 8})
            valores = conteo.values.tolist()
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax.set_title(f"🥧 Gráfico de Pastel - {nombre}", fontsize=12, fontweight='bold')
        ax.axis('equal')
        estadisticas_actuales = logica.calcular_estadisticas(valores)
        
    elif tema_actual == "Dispersion":
        x_vals = datos["Edad"].dropna().tolist()
        y_vals = datos["Altura"].dropna().tolist()
        ax.scatter(x_vals, y_vals, s=60, alpha=0.7, color='blue', edgecolor='black')
        ax.set_xlabel("Variable X", fontsize=11)
        ax.set_ylabel("Variable Y", fontsize=11)
        ax.set_title(f"📈 Diagrama de Dispersión - {nombre}", fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        if len(x_vals) >= 3:
            try:
                z = np.polyfit(x_vals, y_vals, 1)
                p = np.poly1d(z)
                x_trend = np.linspace(min(x_vals), max(x_vals), 100)
                ax.plot(x_trend, p(x_trend), "r--", alpha=0.7, linewidth=2, label='Tendencia')
                ax.legend(fontsize=8)
            except: pass
        estadisticas_actuales = logica.calcular_estadisticas_bivariadas(x_vals, y_vals)
    
    fig_actual.tight_layout()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_imagen_actual = os.path.join(logica.carpeta_guardado, f"temp_{timestamp}.png")
    fig_actual.savefig(ruta_imagen_actual, dpi=250, bbox_inches="tight")
    
    canvas = FigureCanvasTkAgg(fig_actual, master=frame_canvas)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    mostrar_estadisticas(estadisticas_actuales)
    if estadisticas_actuales:
        threading.Timer(0.5, lambda: logica.leer_estadisticas(estadisticas_actuales, tema_actual, logica.idioma_actual)).start()

def mostrar_estadisticas(estadisticas):
    if not estadisticas:
        texto_estadisticas.configure(text="📊 ESTADÍSTICAS:\n\nNo hay suficientes datos para calcular estadísticas")
        return
    texto = "📊 ESTADÍSTICAS:\n\n"
    if "correlacion" in estadisticas:
        texto += f"• Correlación: {estadisticas['correlacion']:.3f}\n"
        texto += f"• Media X: {estadisticas.get('media_x', 0):.2f}\n"
        texto += f"• Media Y: {estadisticas.get('media_y', 0):.2f}\n"
        texto += f"• Desviación X: {estadisticas.get('desviacion_x', 0):.2f}\n"
        texto += f"• Desviación Y: {estadisticas.get('desviacion_y', 0):.2f}\n"
    else:
        texto += f"• Media: {estadisticas.get('media', 0):.2f}\n"
        texto += f"• Mediana: {estadisticas.get('mediana', 0):.2f}\n"
        texto += f"• Moda: {estadisticas.get('moda', 0):.2f}\n"
        texto += f"• Desviación: {estadisticas.get('desviacion', 0):.2f}\n"
        texto += f"• Mínimo: {estadisticas.get('minimo', 0):.2f}\n"
        texto += f"• Máximo: {estadisticas.get('maximo', 0):.2f}\n"
        texto += f"• Rango: {estadisticas.get('rango', 0):.2f}\n"
    texto += f"\n📊 Total datos: {estadisticas.get('total', 0)}"
    texto_estadisticas.configure(text=texto)

def guardar_imagen():
    global fig_actual, tema_actual, ruta_imagen_actual
    if fig_actual is None:
        messagebox.showerror("Error", "Primero genere un gráfico")
        return
    nombre = entry_nombre_grafica.get().strip()
    if not nombre:
        nombre = f"grafico_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    ruta = logica.guardar_grafico(fig_actual, f"{nombre}_{tema_actual}")
    if ruta:
        ruta_imagen_actual = ruta
        messagebox.showinfo("✅ Éxito", f"Imagen guardada correctamente:\n{os.path.basename(ruta)}")
    else:
        messagebox.showerror("Error", "No se pudo guardar la imagen")

def exportar_reporte():
    global estadisticas_actuales, tema_actual, ruta_imagen_actual
    if not estadisticas_actuales:
        messagebox.showerror("Error", "Primero genere un gráfico con estadísticas")
        return
    nombre = entry_nombre_grafica.get().strip()
    if not nombre:
        nombre = f"reporte_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    ruta = logica.generar_reporte_pdf(nombre, estadisticas_actuales, tema_actual, ruta_imagen_actual)
    if ruta:
        messagebox.showinfo("✅ Éxito", f"Reporte PDF guardado:\n{os.path.basename(ruta)}")
    else:
        messagebox.showerror("Error", "No se pudo generar el reporte PDF")

def mostrar_grafico_ejemplo():
    global fig_actual, canvas, tema_actual, estadisticas_actuales, ruta_imagen_actual
    if tema_actual is None:
        messagebox.showerror("Error", "Seleccione un tipo de gráfico")
        return
    limpiar_grafico()
    fig_actual = logica.mostrar_grafico_ejemplo(tema_actual)
    if fig_actual:
        canvas = FigureCanvasTkAgg(fig_actual, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        datos_ejemplo = logica.cargar_datos_ejemplo()
        if tema_actual == "Histogramas":
            estadisticas_actuales = logica.calcular_estadisticas(datos_ejemplo["Edad"].tolist())
        elif tema_actual == "Dispersion":
            estadisticas_actuales = logica.calcular_estadisticas_bivariadas(
                datos_ejemplo["Edad"].tolist(), datos_ejemplo["Altura"].tolist())
        else:
            estadisticas_actuales = logica.calcular_estadisticas(datos_ejemplo["Edad"].tolist())
        mostrar_estadisticas(estadisticas_actuales)
        if estadisticas_actuales:
            threading.Timer(0.5, lambda: logica.leer_estadisticas(estadisticas_actuales, tema_actual, logica.idioma_actual)).start()

# ================== INTERFAZ GRÁFICA ==================
titulo = ctk.CTkLabel(
    app,
    text="📊 SISTEMA DE INTERPRETACIÓN DE GRÁFICOS ESTADÍSTICOS",
    font=ctk.CTkFont(size=20, weight="bold")
)
titulo.pack(pady=10)

barra_superior = ctk.CTkFrame(app, fg_color="transparent")
barra_superior.pack(fill="x", padx=15, pady=5)

ctk.CTkButton(barra_superior, text="☀ Claro", width=80, height=30,
              command=lambda: cambiar_tema_visual("Claro")).pack(side="left", padx=3)
ctk.CTkButton(barra_superior, text="🌙 Oscuro", width=80, height=30,
              command=lambda: cambiar_tema_visual("Oscuro")).pack(side="left", padx=3)

label_idioma = ctk.CTkLabel(barra_superior, text="Idioma: Español", font=ctk.CTkFont(size=12))
label_idioma.pack(side="left", padx=(20, 5))
ctk.CTkButton(barra_superior, text="🇪🇸 ES", width=50, height=30,
              command=lambda: cambiar_idioma("español")).pack(side="left", padx=1)
ctk.CTkButton(barra_superior, text="🇬🇧 EN", width=50, height=30,
              command=lambda: cambiar_idioma("ingles")).pack(side="left", padx=1)

ctk.CTkLabel(barra_superior, text="Tamaño:", font=ctk.CTkFont(size=12)).pack(side="right", padx=5)
slider_tamaño = ctk.CTkSlider(barra_superior, from_=80, to=150, width=120, command=cambiar_tamaño)
slider_tamaño.set(100)
slider_tamaño.pack(side="right", padx=5)

contenedor = ctk.CTkFrame(app)
contenedor.pack(fill="both", expand=True, padx=15, pady=5)
contenedor.grid_columnconfigure(0, weight=1, minsize=250)
contenedor.grid_columnconfigure(1, weight=2, minsize=550)
contenedor.grid_columnconfigure(2, weight=1, minsize=250)
contenedor.grid_rowconfigure(0, weight=1)

# ================== PANEL IZQUIERDO ==================
panel_izq = ctk.CTkFrame(contenedor)
panel_izq.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

ctk.CTkLabel(panel_izq, text="📊 TIPOS DE GRÁFICOS", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 8))

for tema in ["Histogramas", "Barras", "Pastel", "Dispersion"]:
    ctk.CTkButton(panel_izq, text=tema, width=220, height=32,
                  command=lambda t=tema: cambiar_tema(t)).pack(pady=3)

ctk.CTkButton(panel_izq, text="📚 Términos Estadísticos", width=220, height=32,
              command=mostrar_terminos).pack(pady=(8, 3))
ctk.CTkButton(panel_izq, text="📈 Gráfico ejemplo", width=220, height=32,
              command=mostrar_grafico_ejemplo).pack(pady=3)

ctk.CTkFrame(panel_izq, height=1, fg_color="gray").pack(fill="x", padx=15, pady=10)

# ================== PANEL CENTRAL ==================
panel_centro = ctk.CTkFrame(contenedor)
panel_centro.grid(row=0, column=1, sticky="nsew", padx=3, pady=3)
panel_centro.grid_rowconfigure(0, weight=1)
panel_centro.grid_rowconfigure(1, weight=1)
panel_centro.grid_columnconfigure(0, weight=1)

frame_teoria = ctk.CTkFrame(panel_centro)
frame_teoria.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
texto_teoria = ctk.CTkLabel(frame_teoria, text="Seleccione un tipo de gráfico para ver su teoría",
                            font=ctk.CTkFont(size=12), wraplength=500, justify="left")
texto_teoria.pack(expand=True, fill="both", padx=10, pady=10)

frame_inputs = ctk.CTkFrame(panel_centro)
frame_inputs.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
frame_inputs.grid_columnconfigure(1, weight=1)

label_x = ctk.CTkLabel(frame_inputs, text="📊 Datos:", font=ctk.CTkFont(size=12))
label_x.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
entry_x = ctk.CTkEntry(frame_inputs, placeholder_text="Ingrese datos", width=350, height=30)
entry_x.grid(row=0, column=1, columnspan=2, sticky="ew", padx=8, pady=(8, 2))

label_y = ctk.CTkLabel(frame_inputs, text="📉 Variable Y:", font=ctk.CTkFont(size=12))
label_y.grid(row=1, column=0, sticky="w", padx=8, pady=(2, 2))
label_y.grid_remove()
entry_y = ctk.CTkEntry(frame_inputs, placeholder_text="Ingrese datos Y", width=350, height=30)
entry_y.grid(row=1, column=1, columnspan=2, sticky="ew", padx=8, pady=(2, 2))
entry_y.grid_remove()

label_cat = ctk.CTkLabel(frame_inputs, text="🏷️ Categorías:", font=ctk.CTkFont(size=12))
label_cat.grid(row=2, column=0, sticky="w", padx=8, pady=(2, 2))
label_cat.grid_remove()
entrada_cat = ctk.CTkEntry(frame_inputs, placeholder_text="Ingrese categorías", width=350, height=30)
entrada_cat.grid(row=2, column=1, columnspan=2, sticky="ew", padx=8, pady=(2, 2))
entrada_cat.grid_remove()

frame_botones = ctk.CTkFrame(frame_inputs, fg_color="transparent")
frame_botones.grid(row=3, column=0, columnspan=3, pady=8)

btn_guardar = ctk.CTkButton(frame_botones, text="💾 Guardar", width=100, height=30, command=guardar_datos)
btn_guardar.pack(side="left", padx=4)
btn_editar = ctk.CTkButton(frame_botones, text="✏️ Cargar", width=100, height=30, command=cargar_para_editar)
btn_editar.pack(side="left", padx=4)
btn_limpiar = ctk.CTkButton(frame_botones, text="🗑️ Limpiar", width=100, height=30, command=limpiar_campos)
btn_limpiar.pack(side="left", padx=4)

ctk.CTkLabel(frame_inputs, text="👤 Nombre:", font=ctk.CTkFont(size=12)).grid(row=4, column=0, sticky="w", padx=8, pady=4)
entry_nombre_guardar = ctk.CTkEntry(frame_inputs, placeholder_text="Nombre", width=350, height=30)
entry_nombre_guardar.grid(row=4, column=1, columnspan=2, sticky="ew", padx=8, pady=4)

label_estado_edicion = ctk.CTkLabel(frame_inputs, text="", font=ctk.CTkFont(size=10), text_color="orange")
label_estado_edicion.grid(row=5, column=0, columnspan=3, sticky="w", padx=8, pady=1)

ctk.CTkLabel(frame_inputs, text="✏️ Editar:", font=ctk.CTkFont(size=11)).grid(
    row=6, column=0, sticky="w", padx=8, pady=(6, 2))
entry_nombre_editar = ctk.CTkEntry(frame_inputs, placeholder_text="Nombre a editar", width=350, height=30)
entry_nombre_editar.grid(row=6, column=1, columnspan=2, sticky="ew", padx=8, pady=(6, 2))

cuadro_editar = ctk.CTkTextbox(frame_inputs, height=80, font=ctk.CTkFont(size=10))
cuadro_editar.grid(row=7, column=0, columnspan=3, sticky="ew", padx=8, pady=6)
cuadro_editar.configure(state="disabled")

# ================== PANEL DERECHO ==================
panel_der = ctk.CTkFrame(contenedor)
panel_der.grid(row=0, column=2, sticky="nsew", padx=3, pady=3)
panel_der.grid_rowconfigure(0, weight=0)
panel_der.grid_rowconfigure(1, weight=2)
panel_der.grid_rowconfigure(2, weight=1)
panel_der.grid_columnconfigure(0, weight=1)

frame_nombres = ctk.CTkFrame(panel_der)
frame_nombres.grid(row=0, column=0, sticky="ew", padx=8, pady=4)

ctk.CTkLabel(frame_nombres, text="📋 Guardados:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=1)
frame_boton_actualizar = ctk.CTkFrame(frame_nombres, fg_color="transparent")
frame_boton_actualizar.pack(fill="x", padx=5, pady=1)
ctk.CTkButton(frame_boton_actualizar, text="🔄 Actualizar", width=120, height=25,
              command=actualizar_lista_nombres).pack(side="left")

cuadro_nombres = ctk.CTkTextbox(frame_nombres, height=100, font=ctk.CTkFont(size=10))
cuadro_nombres.pack(fill="x", padx=5, pady=3)
cuadro_nombres.configure(state="disabled")

ctk.CTkLabel(panel_der, text="📈 VISUALIZACIÓN", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, pady=2)
frame_canvas = ctk.CTkFrame(panel_der)
frame_canvas.grid(row=1, column=0, sticky="nsew", padx=8, pady=2)

frame_stats = ctk.CTkFrame(panel_der)
frame_stats.grid(row=2, column=0, sticky="nsew", padx=8, pady=4)
texto_estadisticas = ctk.CTkLabel(frame_stats, text="📊 ESTADÍSTICAS:\n\nSeleccione un gráfico",
                                   font=ctk.CTkFont(size=10), justify="left", wraplength=280)
texto_estadisticas.pack(fill="both", expand=True, padx=6, pady=6)

# ================== PANEL INFERIOR ==================
frame_inferior = ctk.CTkFrame(app)
frame_inferior.pack(fill="x", padx=15, pady=5)
frame_inferior.grid_columnconfigure(1, weight=1)

boton_hacer = ctk.CTkButton(frame_inferior, text="📊 Generar", width=120, height=32,
                            font=ctk.CTkFont(size=12), state="disabled", command=generar_grafico)
boton_hacer.grid(row=0, column=0, padx=5, pady=5)

entry_nombre_grafica = ctk.CTkEntry(frame_inferior, placeholder_text="Nombre para gráfico",
                                     width=250, height=32, font=ctk.CTkFont(size=11))
entry_nombre_grafica.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

ctk.CTkButton(frame_inferior, text="💾 Imagen", width=100, height=32,
              font=ctk.CTkFont(size=11), command=guardar_imagen).grid(row=0, column=2, padx=5, pady=5)
ctk.CTkButton(frame_inferior, text="📄 PDF", width=100, height=32,
              font=ctk.CTkFont(size=11), command=exportar_reporte).grid(row=0, column=3, padx=5, pady=5)

frame_volumen = ctk.CTkFrame(frame_inferior, fg_color="transparent")
frame_volumen.grid(row=1, column=0, columnspan=4, pady=2)
ctk.CTkLabel(frame_volumen, text="🔊 Volumen:", font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
slider_volumen = ctk.CTkSlider(frame_volumen, from_=0, to=100, width=150, command=cambiar_volumen)
slider_volumen.set(50)
slider_volumen.pack(side="left", padx=5)

# ================== INICIALIZAR ==================
logica.asegurar_csv()
actualizar_lista_nombres()
iniciar_musica()

if __name__ == "__main__":
    app.mainloop()