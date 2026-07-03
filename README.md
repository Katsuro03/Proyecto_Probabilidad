# 📊 Sistema Interactivo de Análisis e Interpretación Estadística

![Python](https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blue?style=for-the-badge)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?style=for-the-badge)
![NumPy](https://img.shields.io/badge/Numpy-777BB4?style=for-the-badge&logo=numpy&logoColor=white)

---

## 📌 Descripción General

Este repositorio contiene el código fuente de una aplicación de escritorio desarrollada en **Python**, orientada a la visualización, análisis e interpretación de datos estadísticos. El proyecto fue concebido como una herramienta didáctica e interactiva para la asignatura de **Probabilidad y Estadística** en la **Universidad Politécnica Salesiana**.

La aplicación permite a los usuarios ingresar datasets (manualmente o mediante archivos CSV) para generar gráficos estadísticos dinámicos, calcular medidas de tendencia central y dispersión automáticamente, y evaluar sus conocimientos mediante un módulo de cuestionario interactivo con soporte de accesibilidad (Text-to-Speech).

---

## 🎯 Objetivos

### Objetivo General

Desarrollar una herramienta de software interactiva que facilite la comprensión y el análisis de datos estadísticos mediante visualizaciones gráficas y gamificación, aplicando los conceptos teóricos de Probabilidad y Estadística.

### Objetivos Específicos

- Procesar conjuntos de datos tabulares utilizando `Pandas` y `NumPy` para el cálculo automático de métricas estadísticas (Media, Mediana, Moda, Varianza, Correlación, etc.).
- Diseñar una Interfaz Gráfica de Usuario (GUI) moderna y responsiva utilizando `CustomTkinter`.
- Generar visualizaciones de datos precisas (Histogramas, Dispersión, Barras, Pastel) integrando `Matplotlib` en el entorno de Tkinter.
- Implementar funciones de Accesibilidad Universal (a11y) mediante síntesis de voz (`pyttsx3`) para la lectura de resultados y cuestionarios.
- Automatizar la generación de reportes ejecutivos en formato PDF utilizando `FPDF`.

---

## 🚀 Arquitectura y Funcionalidades Principales

El sistema está compuesto por cuatro módulos principales:

### 1️⃣ Motor de Visualización y Estadística

- **Cálculo Automático:** Extrae al instante la Media, Mediana, Moda, Desviación Estándar, Rango y Correlación de Pearson (para gráficos de dispersión).
- **Renderizado Gráfico:** Soporte integrado para múltiples tipos de gráficos.
- **Gestión de Datos:** Ingreso manual de vectores o importación masiva de datos mediante archivos `.csv`.

### 2️⃣ Módulo de Gamificación (Cuestionario)

- Evaluación interactiva de conceptos estadísticos con validación de estado (no permite avanzar sin responder).
- Tracking en tiempo real de respuestas correctas/incorrectas.
- Cálculo de puntaje final para retroalimentación inmediata.

### 3️⃣ Accesibilidad y Experiencia de Usuario (UX)

- **Soporte Text-to-Speech (TTS):** Lectura por voz de las preguntas del cuestionario y los resultados estadísticos, con control de volumen y soporte bilingüe (Español/Inglés).
- **Temas Dinámicos:** Soporte nativo para modo claro y oscuro (`Light/Dark mode`).
- Paneles con scroll dinámico para la correcta visualización de grandes volúmenes de métricas.

### 4️⃣ Exportación y Persistencia

- Autoguardado de gráficos generados en el directorio local.
- Historial de sesión navegable.
- Compilación de **Reportes PDF** que incluyen el gráfico generado, la tabla de estadísticas, fecha y metadatos del dataset.

---

## 📊 Estructura del Repositorio

```text
Proyecto_ver3/
├── main.py                # Controlador principal de la Interfaz Gráfica (GUI)
├── logica.py              # Motor de cálculos estadísticos, gráficos y TTS
├── datos.csv              # Dataset de prueba / template
├── graficos_guardados/    # Directorio de salida para imágenes (.png)
├── reportes/              # Directorio de salida para reportes (.pdf)
└── README.md              # Documentación técnica del proyecto
```

---

## ⚙️ Requisitos y Ejecución

### Entorno de Desarrollo

- Python 3.12+

### Instalación de Dependencias

Abre tu terminal y ejecuta el siguiente comando para instalar todas las librerías necesarias:

```bash
pip install customtkinter matplotlib pandas numpy pyttsx3 fpdf scipy
```

### Ejecutar la Aplicación

Una vez instaladas las dependencias, levanta la interfaz gráfica ejecutando:

```bash
python main.py
```

---

## 🔬 Conclusiones Principales

- La transición de una herramienta de línea de comandos (CLI) a una Interfaz Gráfica (GUI) con `CustomTkinter` mejoró exponencialmente la curva de aprendizaje para usuarios no técnicos.
- La integración del motor `pyttsx3` demostró cómo las herramientas estadísticas pueden ser inclusivas mediante prácticas de accesibilidad de software.
- El uso de `Pandas` y `NumPy` permitió optimizar el tiempo de cálculo de medidas de dispersión y tendencia central, evitando bloqueos en el hilo principal de la interfaz al cargar datasets grandes.

---

## 👨‍💻 Autor

- **Carlos Pilatuña** 

Proyecto desarrollado para la asignatura de **Probabilidad y Estadística**  
**Universidad Politécnica Salesiana**  
Quito, Ecuador

---

## 📜 Licencia

Este proyecto fue desarrollado con fines educativos y de divulgación académica. Todos los derechos pertenecen a sus respectivos autores.
