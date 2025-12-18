# Manual Técnico - PDF Splitter App

## Resumen del Proyecto

La aplicación PDF Splitter es una herramienta desarrollada con Python y Streamlit que permite a los usuarios dividir documentos PDF extensos en archivos más pequeños. La aplicación incorpora inteligencia artificial para detectar automáticamente posibles puntos de división basados en la presencia de firmas, sellos u otros marcadores que indiquen finales de documentos.

## Estructura de Archivos

El proyecto consta de los siguientes archivos principales:

- `app.py`: Aplicación principal con la interfaz de usuario de Streamlit
- `pdf_processor.py`: Funciones para el procesamiento de archivos PDF
- `image_analyzer.py`: Algoritmos para el análisis de imágenes y detección de firmas/sellos
- `.streamlit/config.toml`: Configuración del servidor Streamlit

## Tecnologías Utilizadas

- **Streamlit**: Framework para la creación de interfaces de usuario web con Python
- **PyMuPDF (Fitz)**: Biblioteca para manipulación de archivos PDF
- **OpenCV**: Biblioteca de visión artificial para análisis de imágenes
- **Pillow (PIL)**: Biblioteca para procesamiento de imágenes
- **NumPy**: Biblioteca para procesamiento numérico y manipulación de matrices

## Componentes Principales

### 1. Interfaz de Usuario (app.py)

La interfaz de usuario está desarrollada con Streamlit y proporciona las siguientes funcionalidades:

- Carga de archivos PDF mediante un selector de archivos
- Visualización de miniaturas de las páginas del PDF
- Navegación entre páginas mediante un slider
- Botones interactivos para aceptar/rechazar puntos de división sugeridos
- Visualización de puntos de división aceptados
- Funcionalidad para dividir el PDF y descargar los archivos resultantes

La estructura principal del código sigue este patrón:

```python
# Inicialización de estados de sesión para mantener el estado entre recargas
if 'splittable_pages' not in st.session_state:
    st.session_state.splittable_pages = {}
    
# Interfaz para subida de archivo
uploaded_file = st.file_uploader("Seleccione un archivo PDF", type=['pdf'])

# Procesamiento cuando se carga un archivo
if uploaded_file is not None:
    # Procesar PDF, mostrar miniaturas, etc.
```

### 2. Procesador de PDF (pdf_processor.py)

Este módulo contiene la clase `PDFProcessor` que maneja las operaciones relacionadas con archivos PDF:

- Inicialización y carga de documentos PDF
- Extracción de imágenes de páginas para miniaturas y análisis
- División del documento en múltiples PDFs según los puntos de división especificados
- Obtención de información sobre el documento (número de páginas, dimensiones, etc.)

La funcionalidad principal de división se implementa en el método `split_pdf`:

```python
def split_pdf(self, split_points, output_dir, mid_page_splits=None):
    # Ordenar puntos de división
    split_points = sorted(split_points)
    
    # Generar los PDFs divididos
    for i in range(len(all_split_points) - 1):
        start_page = all_split_points[i]
        end_page = all_split_points[i + 1]
        
        # Crear nuevo documento para este segmento
        new_doc = fitz.open()
        
        # Añadir páginas desde el documento original
        for page_num in range(start_page, end_page):
            new_doc.insert_pdf(self.doc, from_page=page_num, to_page=page_num)
        
        # Guardar el nuevo documento con el rango de páginas en el nombre
        output_path = os.path.join(output_dir, f"{filename_base}_pages{start_page_num}-{end_page_num}.pdf")
        new_doc.save(output_path)
```

### 3. Analizador de Imágenes (image_analyzer.py)

Este módulo contiene algoritmos de visión artificial para analizar las páginas del PDF y detectar posibles puntos de división:

- Conversión de imágenes a escala de grises
- Detección de características como firmas o sellos mediante algoritmos de procesamiento de imágenes
- Evaluación de la probabilidad de que una página sea un punto de división

El algoritmo principal `detect_split_points` utiliza técnicas de OpenCV para analizar la imagen:

```python
def detect_split_points(pil_image):
    # Convertir a array numpy
    img = np.array(pil_image)
    
    # Procesar la imagen para detectar características
    # (bordes, contornos, áreas de interés, etc.)
    
    # Retornar True si la página parece ser un buen punto de división
    return has_signature_features
```

## Flujo de Datos

1. El usuario carga un archivo PDF a través de la interfaz de Streamlit
2. El archivo se guarda temporalmente y se crea una instancia de `PDFProcessor`
3. Se generan miniaturas de todas las páginas para visualización
4. El módulo `image_analyzer` analiza cada página para detectar posibles puntos de división
5. Los puntos de división sugeridos se muestran al usuario para confirmación
6. El usuario ajusta los puntos de división según sea necesario
7. Al hacer clic en "Dividir PDF", `PDFProcessor` divide el documento según los puntos seleccionados
8. Los archivos resultantes se guardan en la carpeta "pdf_divididos" y están disponibles para descarga

## Optimizaciones y Rendimiento

- Las miniaturas se generan con resolución reducida para mejorar el rendimiento
- Los estados de sesión de Streamlit mantienen la persistencia de datos entre interacciones
- La visualización de páginas usa un sistema de paginación para manejar documentos extensos

## Extensibilidad

El código está estructurado para facilitar la adición de nuevas funcionalidades:

- Mejoras en algoritmos de detección
- Soporte para divisiones en medio de una página
- Implementación de funciones adicionales de edición de PDF

## Requisitos del Sistema

- Python 3.7+
- Dependencias: streamlit, pymupdf, opencv-python, pillow, numpy
- Sistema operativo: Windows, macOS, Linux (multiplataforma)

---

Este manual técnico ofrece una visión general de la implementación de la aplicación PDF Splitter. Para más detalles sobre la implementación, consulte los comentarios en el código fuente.