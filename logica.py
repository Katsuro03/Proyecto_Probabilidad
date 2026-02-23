import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import pyttsx3
import numpy as np
from fpdf import FPDF
import webbrowser
import tempfile

# ================== CONFIGURACIÓN DE RUTAS ==================
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_csv = os.path.join(ruta_actual, "datos.csv")
carpeta_guardado = os.path.join(ruta_actual, "graficos_guardados")
carpeta_reportes = os.path.join(ruta_actual, "reportes")

os.makedirs(carpeta_guardado, exist_ok=True)
os.makedirs(carpeta_reportes, exist_ok=True)

# ================== CONFIGURACIÓN DE IDIOMA ==================
idioma_actual = "español"  # Por defecto español

voces_disponibles = {
    "español": {
        "media": "La media es {:.2f}",
        "mediana": "La mediana es {:.2f}",
        "moda": "La moda es {}",
        "desviacion": "La desviación estándar es {:.2f}",
        "minimo": "El valor mínimo es {:.2f}",
        "maximo": "El valor máximo es {:.2f}",
        "rango": "El rango es {:.2f}",
        "correlacion": "La correlación entre las variables es {:.2f}",
        "total": "Total de datos: {}",
        "sin_datos": "No hay suficientes datos para calcular estadísticas"
    },
    "ingles": {
        "media": "The mean is {:.2f}",
        "mediana": "The median is {:.2f}",
        "moda": "The mode is {}",
        "desviacion": "The standard deviation is {:.2f}",
        "minimo": "The minimum value is {:.2f}",
        "maximo": "The maximum value is {:.2f}",
        "rango": "The range is {:.2f}",
        "correlacion": "The correlation between variables is {:.2f}",
        "total": "Total data points: {}",
        "sin_datos": "Insufficient data to calculate statistics"
    }
}

def cambiar_idioma(idioma):
    """Cambia el idioma para la lectura de estadísticas"""
    global idioma_actual
    if idioma in voces_disponibles:
        idioma_actual = idioma
        return True
    return False

# ================== TEORÍA BILINGÜE ==================
teoria = {
    "Histogramas": {
        "español": """📊 HISTOGRAMA:
Muestra la distribución de frecuencias de una variable.

✓ Los datos se agrupan en intervalos
✓ La altura indica la frecuencia
✓ Útil para ver la forma de los datos
✓ Identifica valores atípicos""",
        "ingles": """📊 HISTOGRAM:
Shows the frequency distribution of a variable.

✓ Data is grouped into intervals
✓ Height indicates frequency
✓ Useful for seeing data shape
✓ Identifies outliers"""
    },
    "Barras": {
        "español": """📊 GRÁFICO DE BARRAS:
Compara diferentes categorías.

✓ Cada barra es una categoría
✓ La altura muestra el valor
✓ Ideal para comparar grupos
✓ Fácil de interpretar""",
        "ingles": """📊 BAR CHART:
Compares different categories.

✓ Each bar is a category
✓ Height shows the value
✓ Ideal for comparing groups
✓ Easy to interpret"""
    },
    "Pastel": {
        "español": """🥧 GRÁFICO DE PASTEL:
Muestra proporciones de un total.

✓ Cada sector es un porcentaje
✓ Los valores deben ser positivos
✓ Muestra la composición
✓ Ideal para ver distribución""",
        "ingles": """🥧 PIE CHART:
Shows proportions of a total.

✓ Each slice is a percentage
✓ Values must be positive
✓ Shows composition
✓ Ideal for distribution"""
    },
    "Dispersion": {
        "español": """📈 DIAGRAMA DE DISPERSIÓN:
Relación entre dos variables.

✓ Cada punto es un par (X,Y)
✓ Muestra correlaciones
✓ Identifica tendencias
✓ Detecta valores atípicos""",
        "ingles": """📈 SCATTER PLOT:
Relationship between two variables.

✓ Each point is an (X,Y) pair
✓ Shows correlations
✓ Identifies trends
✓ Detects outliers"""
    }
}

def obtener_terminos(idioma=None):
    if idioma is None:
        idioma = idioma_actual
    
    if idioma == "español":
        return """📊 TÉRMINOS ESTADÍSTICOS:

• Eje X: Variable independiente
• Eje Y: Variable dependiente
• Frecuencia: Número de repeticiones
• Moda: Valor más frecuente
• Mediana: Valor central
• Media: Promedio
• Desviación: Dispersión de los datos
• Correlación: Relación entre variables"""
    else:
        return """📊 STATISTICAL TERMS:

• X Axis: Independent variable
• Y Axis: Dependent variable
• Frequency: Number of repetitions
• Mode: Most frequent value
• Median: Central value
• Mean: Average
• Deviation: Data dispersion
• Correlation: Relationship between variables"""

# ================== AUDIO BILINGÜE ==================
def leer_texto(texto, idioma=None):
    """Lee texto en el idioma especificado"""
    if idioma is None:
        idioma = idioma_actual
    
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 0.9)
        
        # Configurar voz según idioma
        voices = engine.getProperty('voices')
        if idioma == "español":
            # Buscar voz en español
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'español' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
        else:  # inglés
            for voice in voices:
                if 'english' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
        
        engine.say(texto)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"Error de audio: {e}")

def leer_estadisticas(estadisticas, tipo_grafico="", idioma=None):
    """Lee las estadísticas calculadas"""
    if idioma is None:
        idioma = idioma_actual
    
    if not estadisticas:
        leer_texto(voces_disponibles[idioma]["sin_datos"], idioma)
        return
    
    texto = ""
    if tipo_grafico == "Histogramas" or tipo_grafico == "Barras":
        texto += voces_disponibles[idioma]["media"].format(estadisticas.get("media", 0)) + ". "
        texto += voces_disponibles[idioma]["mediana"].format(estadisticas.get("mediana", 0)) + ". "
        if estadisticas.get("moda") is not None:
            texto += voces_disponibles[idioma]["moda"].format(estadisticas["moda"]) + ". "
        texto += voces_disponibles[idioma]["desviacion"].format(estadisticas.get("desviacion", 0)) + ". "
        
    elif tipo_grafico == "Dispersion":
        texto += voces_disponibles[idioma]["correlacion"].format(estadisticas.get("correlacion", 0)) + ". "
    
    texto += voces_disponibles[idioma]["total"].format(estadisticas.get("total", 0))
    
    leer_texto(texto, idioma)

# ================== FUNCIONES ESTADÍSTICAS ==================
def calcular_estadisticas(datos):
    """
    Calcula estadísticas básicas
    datos: lista de números
    """
    if not datos or len(datos) == 0:
        return None
    
    datos_array = np.array(datos)
    
    # Calcular moda (el valor más frecuente)
    try:
        from scipy import stats
        moda = stats.mode(datos_array)[0][0]
    except:
        # Si no hay scipy, calcular moda manualmente
        valores, conteos = np.unique(datos_array, return_counts=True)
        moda = valores[np.argmax(conteos)]
    
    stats_dict = {
        "media": float(np.mean(datos_array)),
        "mediana": float(np.median(datos_array)),
        "moda": float(moda) if isinstance(moda, (int, float)) else moda,
        "desviacion": float(np.std(datos_array)),
        "minimo": float(np.min(datos_array)),
        "maximo": float(np.max(datos_array)),
        "rango": float(np.max(datos_array) - np.min(datos_array)),
        "total": len(datos_array)
    }
    return stats_dict

def calcular_estadisticas_bivariadas(x, y):
    """Calcula estadísticas para dos variables"""
    if len(x) != len(y) or len(x) < 2:
        return None
    
    x_array = np.array(x)
    y_array = np.array(y)
    
    correlacion = np.corrcoef(x_array, y_array)[0, 1]
    
    stats_dict = {
        "correlacion": float(correlacion),
        "total": len(x_array),
        "media_x": float(np.mean(x_array)),
        "media_y": float(np.mean(y_array)),
        "desviacion_x": float(np.std(x_array)),
        "desviacion_y": float(np.std(y_array))
    }
    return stats_dict

# ================== CARGA DE DATASETS ==================
def cargar_dataset(ruta_archivo):
    """
    Carga un archivo CSV y retorna un DataFrame
    """
    try:
        df = pd.read_csv(ruta_archivo)
        return df, None
    except Exception as e:
        return None, str(e)

def obtener_columnas_numericas(df):
    """Retorna las columnas numéricas de un DataFrame"""
    return df.select_dtypes(include=[np.number]).columns.tolist()

# ================== EXPORTACIÓN A PDF ==================
def generar_reporte_pdf(nombre, estadisticas, tipo_grafico, ruta_imagen):
    """Genera un reporte en PDF con estadísticas y gráfico"""
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Título
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Reporte Estadístico - {tipo_grafico}", 0, 1, "C")
        pdf.ln(10)
        
        # Información del dataset
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Nombre: {nombre}", 0, 1)
        pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
        pdf.ln(10)
        
        # Estadísticas
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Estadísticas:", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        if estadisticas:
            if "correlacion" in estadisticas:
                pdf.cell(0, 8, f"Correlación: {estadisticas['correlacion']:.3f}", 0, 1)
                pdf.cell(0, 8, f"Media X: {estadisticas.get('media_x', 0):.2f}", 0, 1)
                pdf.cell(0, 8, f"Media Y: {estadisticas.get('media_y', 0):.2f}", 0, 1)
                pdf.cell(0, 8, f"Desviación X: {estadisticas.get('desviacion_x', 0):.2f}", 0, 1)
                pdf.cell(0, 8, f"Desviación Y: {estadisticas.get('desviacion_y', 0):.2f}", 0, 1)
            else:
                pdf.cell(0, 8, f"Media: {estadisticas.get('media', 0):.2f}", 0, 1)
                pdf.cell(0, 8, f"Mediana: {estadisticas.get('mediana', 0):.2f}", 0, 1)
                pdf.cell(0, 8, f"Moda: {estadisticas.get('moda', 0):.2f}", 0, 1)
                pdf.cell(0, 8, f"Desviación: {estadisticas.get('desviacion', 0):.2f}", 0, 1)
                pdf.cell(0, 8, f"Mínimo: {estadisticas.get('minimo', 0):.2f}", 0, 1)
                pdf.cell(0, 8, f"Máximo: {estadisticas.get('maximo', 0):.2f}", 0, 1)
                pdf.cell(0, 8, f"Rango: {estadisticas.get('rango', 0):.2f}", 0, 1)
            
            pdf.cell(0, 8, f"Total de datos: {estadisticas.get('total', 0)}", 0, 1)
        
        pdf.ln(10)
        
        # Agregar gráfico si existe
        if ruta_imagen and os.path.exists(ruta_imagen):
            pdf.image(ruta_imagen, x=10, y=None, w=180)
        
        # Guardar PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"{nombre}_{tipo_grafico}_{timestamp}.pdf"
        ruta_completa = os.path.join(carpeta_reportes, nombre_archivo)
        pdf.output(ruta_completa)
        
        return ruta_completa
    except Exception as e:
        print(f"Error generando PDF: {e}")
        return None

# ================== MANEJO DE CSV ==================
def asegurar_csv():
    if not os.path.exists(ruta_csv):
        df = pd.DataFrame(columns=["Nombre", "Edad", "Altura", "Categoria"])
        df.to_csv(ruta_csv, index=False)

def leer_csv():
    asegurar_csv()
    try:
        return pd.read_csv(ruta_csv)
    except:
        return pd.DataFrame(columns=["Nombre", "Edad", "Altura", "Categoria"])

def guardar_csv(df):
    try:
        df.to_csv(ruta_csv, index=False)
        return True
    except:
        return False

# ================== FUNCIONES DE DATOS ==================
def limpiar_lista(texto, tipo=float):
    if not texto or not texto.strip():
        return []
    texto = texto.replace(';', ',')
    items = [x.strip() for x in texto.split(",") if x.strip()]
    resultado = []
    for item in items:
        try:
            if tipo == float:
                resultado.append(float(item))
            elif tipo == int:
                resultado.append(int(float(item)))
            else:
                resultado.append(tipo(item))
        except:
            continue
    return resultado

def obtener_todos_los_nombres():
    df = leer_csv()
    return sorted(df["Nombre"].dropna().unique().tolist())

def obtener_datos_persona(nombre):
    df = leer_csv()
    return df[df["Nombre"] == nombre].copy()

def guardar_datos_persona(nombre, edades, alturas):
    df = leer_csv()
    df = df[df["Nombre"] != nombre]
    
    nuevos = pd.DataFrame({
        "Nombre": [nombre] * len(edades),
        "Edad": edades,
        "Altura": alturas,
        "Categoria": [""] * len(edades)
    })
    
    df = pd.concat([df, nuevos], ignore_index=True)
    return guardar_csv(df)

def guardar_datos_categorias(nombre, categorias, valores):
    df = leer_csv()
    df = df[df["Nombre"] != nombre]
    
    nuevos = pd.DataFrame({
        "Nombre": [nombre] * len(categorias),
        "Edad": valores,
        "Altura": [0] * len(categorias),
        "Categoria": categorias
    })
    
    df = pd.concat([df, nuevos], ignore_index=True)
    return guardar_csv(df)

def guardar_datos_desde_df(nombre, df):
    """Guarda datos desde un DataFrame cargado"""
    if 'Categoria' in df.columns:
        return guardar_datos_categorias(nombre, df['Categoria'].tolist(), df['Valores'].tolist())
    elif len(df.columns) >= 2:
        # Asumir que las dos primeras columnas numéricas son X e Y
        cols_numericas = df.select_dtypes(include=[np.number]).columns
        if len(cols_numericas) >= 2:
            x_col = cols_numericas[0]
            y_col = cols_numericas[1]
            return guardar_datos_persona(nombre, df[x_col].tolist(), df[y_col].tolist())
    return False

# ================== GRÁFICOS ==================
def cargar_datos_ejemplo():
    if not os.path.exists(ruta_csv) or len(leer_csv()) < 5:
        df_ejemplo = pd.DataFrame({
            "Nombre": ["Ejemplo1", "Ejemplo2", "Ejemplo3", "Ejemplo4", "Ejemplo5"],
            "Edad": [12, 15, 18, 22, 25],
            "Altura": [140, 155, 165, 170, 175],
            "Categoria": ["A", "B", "C", "D", "E"]
        })
        df_ejemplo.to_csv(ruta_csv, index=False)
    return leer_csv()

def mostrar_grafico_ejemplo(tema):
    datos = cargar_datos_ejemplo()
    
    fig = plt.Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)
    
    if tema == "Histogramas":
        ax.hist(datos["Edad"], bins=5, edgecolor='black', alpha=0.7, color='skyblue')
        ax.set_xlabel("Edad")
        ax.set_ylabel("Frecuencia")
        ax.set_title("Ejemplo de Histograma")
        ax.grid(True, alpha=0.3)
        
    elif tema == "Barras":
        ax.bar(["A", "B", "C", "D", "E"], datos["Edad"][:5], 
               color='skyblue', edgecolor='black')
        ax.set_xlabel("Categorías")
        ax.set_ylabel("Valores")
        ax.set_title("Ejemplo de Barras")
        ax.grid(True, axis='y', alpha=0.3)
        
    elif tema == "Pastel":
        ax.pie(datos["Edad"][:4], labels=["A", "B", "C", "D"], 
               autopct='%1.1f%%', startangle=90, shadow=True)
        ax.set_title("Ejemplo de Pastel")
        ax.axis('equal')
        
    elif tema == "Dispersion":
        ax.scatter(datos["Edad"], datos["Altura"], 
                  s=80, alpha=0.7, color='blue', edgecolor='black')
        ax.set_xlabel("Edad")
        ax.set_ylabel("Altura")
        ax.set_title("Ejemplo de Dispersión")
        ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    return fig

def guardar_grafico(fig, nombre_base):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"{nombre_base}_{timestamp}.png"
        ruta_completa = os.path.join(carpeta_guardado, nombre_archivo)
        fig.savefig(ruta_completa, dpi=300, bbox_inches="tight")
        return ruta_completa
    except:
        return None