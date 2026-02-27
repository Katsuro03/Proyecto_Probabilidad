📊 Sistema de Interpretación de Gráficos Estadísticos

Aplicación de escritorio desarrollada en Python que permite crear, visualizar e interpretar gráficos estadísticos de forma interactiva y accesible, incorporando texto a voz, generación de PDF, carga de datasets CSV y visualización clara de estadísticas.

🎯 Objetivo del proyecto

Facilitar la comprensión de gráficos estadísticos (Histogramas, Barras, Pastel y Dispersión) mediante:

Visualización clara

Cálculo automático de estadísticas

Lectura por voz (accesibilidad)

Exportación de resultados

🖥️ Características principales

✔ Interfaz gráfica moderna con CustomTkinter
✔ Gráficos con Matplotlib
✔ Texto a voz con pyttsx3
✔ Música de fondo con pygame
✔ Carga de archivos CSV
✔ Exportación a imagen y PDF
✔ Estadísticas descriptivas automáticas
✔ Cuestionario interactivo con lectura por voz

📈 Tipos de gráficos soportados

📊 Histograma

📊 Gráfico de Barras

🥧 Gráfico de Pastel

📈 Diagrama de Dispersión

🧮 Estadísticas calculadas

Media

Mediana

Moda

Desviación estándar

Mínimo y máximo

Rango

Correlación (en dispersión)

♿ Accesibilidad

🔊 Lectura automática de teoría y estadísticas

🔊 Control de volumen

🧠 Cuestionario guiado por voz

📁 Estructura del proyecto
Proyecto_ver3/
│
├── main.py              # Interfaz gráfica
├── logica.py            # Lógica, estadísticas, audio y PDF
├── datos.csv             # Datos almacenados
├── musica_fondo.mp3      # Música de fondo
├── graficos_guardados/
├── reportes/
└── README.md
⚙️ Requisitos

Instalar dependencias:

pip install customtkinter matplotlib pandas numpy pygame pyttsx3 fpdf

(Opcional: scipy para cálculo de moda)

▶️ Ejecución
python main.py
📌 Autor

Proyecto académico desarrollado para interpretación y análisis de gráficos estadísticos.

📜 Licencia

Uso educativo y académico.
