# 📊 Sistema de Interpretación de Gráficos Estadísticos

Aplicación de escritorio desarrollada en **Python** con **CustomTkinter**, orientada a la **visualización, análisis e interpretación de gráficos estadísticos**, incluyendo un **cuestionario interactivo** para reforzar el aprendizaje.

---

## 🚀 Características principales

### 📈 Tipos de gráficos
- Histograma
- Gráfico de Barras
- Gráfico de Pastel
- Diagrama de Dispersión

### 📊 Estadísticas automáticas
- Media
- Mediana
- Moda
- Desviación estándar
- Mínimo y máximo
- Rango
- Correlación (para dispersión)
- Total de datos

Las estadísticas se muestran en un **panel con scroll**, permitiendo visualizar correctamente grandes cantidades de información.

---

## 🧠 Cuestionario interactivo (Actualizado)

- Preguntas de selección múltiple
- Navegación pregunta por pregunta
- Contador visible de:
  - ✔ Respuestas correctas
  - ❌ Respuestas incorrectas
- Validación: no permite avanzar sin responder
- Resultado final con puntaje
- Lectura por voz de preguntas y resultados

---

## 🔊 Accesibilidad
- Lectura por voz mediante **Text-to-Speech (pyttsx3)**
- Control de volumen
- Soporte de idioma:
  - Español 🇪🇸
  - Inglés 🇺🇸

---

## 💾 Gestión de datos
- Ingreso manual de datos
- Carga de archivos CSV
- Guardado automático de gráficos
- Historial de gráficos generados
- Exportación de reportes en PDF con:
  - Gráfico
  - Estadísticas
  - Fecha y nombre del conjunto de datos

---

## 🖥️ Interfaz gráfica
- Tema claro y oscuro
- Diseño moderno con **CustomTkinter**
- Paneles organizados:
  - Tipos de gráficos
  - Área de visualización
  - Estadísticas con scroll
  - Historial de gráficos guardados

---

## 🛠️ Tecnologías utilizadas

- Python 3.12
- CustomTkinter
- Tkinter
- Matplotlib
- Pandas
- NumPy
- pyttsx3
- FPDF
- SciPy (opcional, para cálculo de moda)

---

## 📂 Estructura del proyecto

Proyecto_ver3/
│
├── main.py # Interfaz gráfica principal
├── logica.py # Lógica estadística, gráficos y cuestionario
├── datos.csv # Dataset principal
│
├── graficos_guardados/ # Imágenes generadas
├── reportes/ # Reportes PDF
│
└── README.md # Documentación del proyecto


---

## ▶️ Ejecución

1. Instalar dependencias:
```bash
pip install customtkinter matplotlib pandas numpy pyttsx3 fpdf scipy


