import streamlit as st
import tempfile
import os
import time
from pdf_processor import PDFProcessor
from image_analyzer import detect_split_points

# Set page configuration with increased memory limits for large files
st.set_page_config(
    page_title="PDF Splitter for Legal Documents",
    page_icon="📄",
    layout="wide"
)

# Aumentar los límites de tamaño de archivo (1GB)
MB = 1024 * 1024
st.session_state["file_uploader_key"] = st.session_state.get("file_uploader_key", 0)

# Configuración para trabajar con archivos extremadamente grandes
os.environ["STREAMLIT_SERVER_MAX_UPLOAD_SIZE"] = "1000"  # 1GB
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

# Initialize session state variables if they don't exist
if 'pdf_processor' not in st.session_state:
    st.session_state.pdf_processor = None
if 'selected_splits' not in st.session_state:
    st.session_state.selected_splits = set()
if 'suggested_splits' not in st.session_state:
    st.session_state.suggested_splits = set()
if 'temp_pdf_path' not in st.session_state:
    st.session_state.temp_pdf_path = None
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'total_pages' not in st.session_state:
    st.session_state.total_pages = 0
if 'processed_thumbnails' not in st.session_state:
    st.session_state.processed_thumbnails = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'show_split_options' not in st.session_state:
    st.session_state.show_split_options = False
if 'original_filename' not in st.session_state:
    st.session_state.original_filename = None

# Function to toggle page selection for splitting
def toggle_page(page_num):
    if page_num in st.session_state.selected_splits:
        st.session_state.selected_splits.remove(page_num)
    else:
        st.session_state.selected_splits.add(page_num)

# Function to reset all splits
def reset_splits():
    st.session_state.selected_splits = set()

# Function to use suggested splits
def use_suggested_splits():
    st.session_state.selected_splits = st.session_state.suggested_splits.copy()

# Function to split PDF and save
def split_pdf():
    if not st.session_state.pdf_processor or not st.session_state.selected_splits:
        st.error("Por favor, suba un PDF y seleccione puntos de división primero.")
        return
    
    splits = sorted(list(st.session_state.selected_splits))
    
    # Usar carpeta temporal para generar archivos antes de crear el ZIP
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        # Obtener el nombre original del archivo para pasarlo a la función de división
        original_name = None
        if st.session_state.original_filename:
            original_name = st.session_state.original_filename
        
        st.info("Procesando división del PDF...")
        
        # Botón para confirmar y dividir
        if st.button("Confirmar y Dividir PDF"):
            # Dividir el PDF y guardar en la carpeta temporal
            split_files = st.session_state.pdf_processor.split_pdf(splits, temp_dir, original_filename=original_name)
            
            # Mostrar información sobre los archivos generados
            if split_files:
                st.success(f"¡El PDF ha sido dividido en {len(split_files)} partes!")
                
                # Crear una sección para descarga con instrucciones
                st.write("### Descargar Archivos Divididos")
                
                # Instrucciones para la descarga
                st.markdown("""
                <style>
                .download-instructions {
                    background-color: #e8f4ff;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    border-left: 4px solid #0066cc;
                }
                </style>
                <div class="download-instructions">
                    <h4>📋 Instrucciones:</h4>
                    <ol>
                        <li>Haga clic en el botón "Descargar PDFs en ZIP" para descargar todos los archivos.</li>
                        <li>El archivo ZIP se descargará automáticamente a su carpeta de Descargas.</li>
                        <li>Extraiga los archivos del ZIP donde desee tener los PDFs divididos.</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)
                
                # Preparar archivo ZIP con todos los PDFs para descarga conjunta
                import zipfile
                import io
                
                # Crear un archivo ZIP en memoria con todos los PDFs
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file_path in split_files:
                        file_name = os.path.basename(file_path)
                        with open(file_path, 'rb') as f:
                            zip_file.writestr(file_name, f.read())
                
                zip_buffer.seek(0)
                
                # Mostrar resumen de los archivos divididos
                st.write("### Archivos incluidos en el ZIP:")
                
                # Crea una tabla con la información de los archivos
                file_info = []
                for file_path in split_files:
                    file_name = os.path.basename(file_path)
                    # Extraer la información de las páginas
                    filename_base = os.path.splitext(file_name)[0]
                    import re
                    match = re.search(r'-(\d+)-(\d+)$', filename_base)
                    if match:
                        start_page, end_page = match.groups()
                        page_info = f"{start_page}-{end_page}"
                    else:
                        page_info = ""
                        
                    file_size = f"{os.path.getsize(file_path)/1024:.1f} KB"
                    file_info.append([file_name, f"Páginas {page_info}", file_size])
                
                # Mostrar los archivos en una tabla
                st.table({
                    "Nombre del archivo": [info[0] for info in file_info],
                    "Rango de páginas": [info[1] for info in file_info],
                    "Tamaño": [info[2] for info in file_info]
                })
                
                # Botón para descargar todos los PDFs como un ZIP con el nombre original y fecha
                from datetime import datetime
                fecha_actual = datetime.now().strftime("%Y%m%d")
                nombre_original = os.path.splitext(st.session_state.original_filename)[0] if st.session_state.original_filename else "documento"
                zip_filename = f"{nombre_original}_dividido_{fecha_actual}.zip"
                
                # Estilo personalizado para el botón de descarga
                st.markdown("""
                <style>
                div.stDownloadButton > button {
                    background-color: #4CAF50 !important;
                    color: white !important;
                    font-size: 18px !important;
                    font-weight: bold !important;
                    padding: 20px 16px !important;
                    border-radius: 8px !important;
                    width: 100% !important;
                    margin: 15px 0 !important;
                    border: none !important;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
                }
                div.stDownloadButton > button:hover {
                    background-color: #45a049 !important;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                st.download_button(
                    label="📦 DESCARGAR PDFs EN ZIP",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip",
                    key="download_all_zip",
                    help="Descarga todos los PDFs divididos en un archivo ZIP comprimido.",
                )
                
                # Mensaje adicional de éxito
                st.success("✅ Los archivos están listos para descarga. El ZIP contiene todos los PDFs divididos.")

# Main application header
st.title("Divisor de PDF para Documentos Legales")
st.write("Suba un archivo PDF grande, vea miniaturas y divídalo en documentos más pequeños")

# File uploader con soporte para archivos muy grandes
uploaded_file = st.file_uploader(
    "Seleccione un archivo PDF (admite archivos de hasta 1 GB)", 
    type=['pdf'],
    key=f"pdf_uploader_{st.session_state['file_uploader_key']}",
    help="Puede cargar archivos PDF extremadamente grandes, incluso documentos legales de más de 500 MB"
)

# Estilos CSS generales para la aplicación
st.markdown("""
<style>
    .preview-container {
        border: 1px solid #ddd;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        background-color: #f9f9f9;
    }
    .miniatura-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .fondo-negro {
        background-color: black;
        padding: 20px;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .miniaturas-fila {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Mostrar instrucciones solo si no hay ningún PDF cargado
if uploaded_file is None:
    with st.expander("ℹ️ Instrucciones de uso", expanded=True):
        st.markdown("### Ejemplo de Visualización del Documento")
        
        st.markdown("""
        <div class="preview-container">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span style="border: 1px dashed #666; padding: 20px 10px; width: 60px; text-align: center;">PDF 1</span>
                <span style="color: #0088ff; margin-top: 20px;">|</span>
                <span style="border: 1px dashed #666; padding: 20px 10px; width: 60px; text-align: center;">PDF 2</span>
                <span style="color: #0088ff; margin-top: 20px;">|</span>
                <span style="border: 1px dashed #666; padding: 20px 10px; width: 60px; text-align: center;">PDF 3</span>
                <span style="color: #0088ff; margin-top: 20px;">|</span>
                <span style="border: 1px dashed #666; padding: 20px 10px; width: 60px; text-align: center;">PDF 4</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span>&nbsp;</span>
                <span style="background-color: #4cc2ff; color: white; padding: 5px 10px; border-radius: 4px;">✓</span>
                <span>&nbsp;</span>
                <span style="background-color: #4cc2ff; color: white; padding: 5px 10px; border-radius: 4px;">✓</span>
                <span>&nbsp;</span>
                <span style="background-color: #4cc2ff; color: white; padding: 5px 10px; border-radius: 4px;">✓</span>
                <span>&nbsp;</span>
            </div>
            <div style="text-align: center; margin-bottom: 10px;">
                <span>◄─────────── [ <span style="color: #4cc2ff; font-weight: bold;">===================</span> ] ───────────►</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Explicación de los elementos de visualización
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("✓ **Líneas verticales** entre páginas para indicar posibles divisiones")
        with col2:
            st.info("✓ **Botones azules** para aceptar/rechazar cada división propuesta")
        with col3:
            st.info("✓ **Barra de navegación** para desplazarse entre páginas")
            
        st.markdown("""
        ### Cómo usar la aplicación:

        1. **Subir PDF**: Seleccione un archivo PDF usando el cargador de archivos
        2. **Revisar divisiones sugeridas**: La aplicación detectará automáticamente posibles puntos de división
        3. **Seleccionar/deseleccionar divisiones**: Use los botones para confirmar las divisiones que desee
        4. **Navegar entre páginas**: Use la barra inferior para ver diferentes secciones del documento
        5. **Dividir PDF**: Haga clic en el botón "Dividir PDF" cuando esté listo
        """)

# Ya declaramos el uploaded_file más arriba, no necesitamos hacerlo dos veces
if uploaded_file is not None:
    # Save uploaded file to a temporary file
    if st.session_state.temp_pdf_path is None or st.session_state.pdf_processor is None:
        # Guardar el nombre original del archivo subido
        st.session_state.original_filename = uploaded_file.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(uploaded_file.getvalue())
            st.session_state.temp_pdf_path = tmp.name
        
        with st.spinner("Procesando archivo PDF..."):
            # Initialize PDF processor with the uploaded file
            st.session_state.pdf_processor = PDFProcessor(st.session_state.temp_pdf_path)
            # Guardar el nombre original para usarlo en los archivos divididos
            st.session_state.pdf_processor.original_filename = st.session_state.original_filename
            st.session_state.total_pages = st.session_state.pdf_processor.get_total_pages()
            st.session_state.processed_thumbnails = {}  # Reset thumbnails
            
            # Get suggested split points based on signatures/stamps
            progress_bar = st.progress(0)
            st.session_state.suggested_splits = set()
            
            for i in range(st.session_state.total_pages):
                # Create a placeholder for the current page
                if i + 1 not in st.session_state.processed_thumbnails:
                    image = st.session_state.pdf_processor.get_page_image(i)
                    has_signature = detect_split_points(image)
                    
                    # If the page has a signature or stamp, suggest it as a split point
                    if has_signature:
                        st.session_state.suggested_splits.add(i + 1)
                    
                    # Store the processed thumbnail
                    st.session_state.processed_thumbnails[i + 1] = (image, has_signature)
                
                # Update progress
                progress_bar.progress((i + 1) / st.session_state.total_pages)
            
            progress_bar.empty()
            st.success(f"¡PDF procesado con éxito! Se detectaron {len(st.session_state.suggested_splits)} posibles puntos de división.")
    
    # Display file information
    st.write(f"Nombre del archivo: {uploaded_file.name}")
    st.write(f"Total de páginas: {st.session_state.total_pages}")
    
    # Split control buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Opciones de División", key="split_btn", type="primary"):
            st.session_state.show_split_options = True
    
    with col2:
        if st.button("Borrar Selecciones", key="reset_btn"):
            reset_splits()
    
    with col3:
        if st.button("Usar Divisiones Sugeridas", key="suggested_btn"):
            use_suggested_splits()
    
    with col4:
        if st.button("Limpiar Todo", key="clear_btn"):
            # Reset everything to initial state
            st.session_state.pdf_processor = None
            st.session_state.selected_splits = set()
            st.session_state.suggested_splits = set()
            if st.session_state.temp_pdf_path and os.path.exists(st.session_state.temp_pdf_path):
                os.unlink(st.session_state.temp_pdf_path)
            st.session_state.temp_pdf_path = None
            st.session_state.show_split_options = False
            
    # Mostrar opciones de división cuando se pulsa el botón
    if 'show_split_options' in st.session_state and st.session_state.show_split_options:
        st.write("---")
        st.write("### Opciones de División")
        split_pdf()
    
    # Selected pages indicator
    st.write(f"Puntos de división seleccionados: {len(st.session_state.selected_splits)}")
    
    # Título y visualización del documento
    st.write("### Previsualización del documento")
    
    # Mostrar miniaturas y controles
    if len(st.session_state.processed_thumbnails) > 0:
        st.write("**Miniaturas de páginas:**")
        
        # Definir la página actual para navegación
        current_page = st.session_state.current_page
        start_idx = max(0, current_page - 1)
        
        # Crear las columnas con separadores visuales entre ellas
        # Usaremos más columnas para intercalar las líneas divisorias
        num_pages_to_show = min(4, st.session_state.total_pages - start_idx)
        
        # HTML para las miniaturas con líneas divisorias
        st.markdown("""
        <style>
        .page-container {
            display: flex;
            align-items: stretch;
            gap: 0px;
            margin: 20px 0;
        }
        .page-item {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .divider-container {
            width: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        .divider-line {
            width: 3px;
            height: 100%;
            background: repeating-linear-gradient(
                to bottom,
                #666 0px,
                #666 10px,
                transparent 10px,
                transparent 20px
            );
            position: relative;
        }
        .divider-button-container {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            z-index: 10;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Crear columnas alternadas: página, divisor, página, divisor, etc.
        total_cols = num_pages_to_show * 2 - 1  # páginas + divisores entre ellas
        
        # Asegurar que total_cols sea al menos 1
        if total_cols < 1:
            total_cols = 1
            cols = st.columns(1)
        else:
            cols = st.columns([3 if i % 2 == 0 else 0.5 for i in range(total_cols)])
        
        # Mostrar miniaturas con divisores entre ellas
        col_idx = 0
        for i in range(num_pages_to_show):
            page_idx = start_idx + i
            
            if page_idx < st.session_state.total_pages and (page_idx + 1) in st.session_state.processed_thumbnails:
                img, has_signature = st.session_state.processed_thumbnails[page_idx + 1]
                
                # Mostrar la miniatura en la columna correspondiente
                with cols[col_idx]:
                    # Mostrar la miniatura
                    st.image(img, caption=f"Página {page_idx + 1}", use_container_width=True)
                    
                    # Mostrar si es un punto de división sugerido
                    if has_signature:
                        st.markdown("🔍 **División sugerida**")
                
                col_idx += 1
                
                # Si no es la última página, mostrar el divisor
                if i < num_pages_to_show - 1 and col_idx < len(cols):
                    next_page = page_idx + 2  # La siguiente página después de esta
                    
                    with cols[col_idx]:
                        # Verificar si este punto está seleccionado como división
                        is_selected = next_page in st.session_state.selected_splits
                        is_suggested = next_page in st.session_state.suggested_splits
                        
                        # Línea divisoria visual que ocupa toda la altura
                        line_color = "#4CAF50" if is_selected else ("#FFA500" if is_suggested else "#999")
                        line_style = "solid" if is_selected else "dashed"
                        
                        # Contenedor principal para la línea y los botones
                        st.markdown(f"""
                        <div style="display: flex; flex-direction: column; align-items: center; justify-content: space-between; height: 100%; min-height: 600px; padding: 20px 0;">
                            <div style="flex: 1; width: 3px; border-left: 3px {line_style} {line_color}; margin: 10px 0;"></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Espacio para centrar los botones
                        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                        
                        # Botón para activar/desactivar la división en este punto
                        if is_selected:
                            if st.button("✗", key=f"remove_split_{next_page}", help=f"Quitar división antes de página {next_page}"):
                                st.session_state.selected_splits.remove(next_page)
                                st.rerun()
                            st.markdown(f"<p style='text-align: center; color: #4CAF50; font-size: 11px; margin: 5px 0;'>✓ Dividir aquí</p>", unsafe_allow_html=True)
                        else:
                            if st.button("✓", key=f"add_split_{next_page}", help=f"Dividir antes de página {next_page}"):
                                st.session_state.selected_splits.add(next_page)
                                st.rerun()
                            if is_suggested:
                                st.markdown(f"<p style='text-align: center; color: #FFA500; font-size: 11px; margin: 5px 0;'>⚠ Sugerido</p>", unsafe_allow_html=True)
                        
                        # Línea divisoria en la parte inferior
                        st.markdown(f"""
                        <div style="display: flex; flex-direction: column; align-items: center; justify-content: space-between; height: 100%; min-height: 300px; padding: 0;">
                            <div style="flex: 1; width: 3px; border-left: 3px {line_style} {line_color}; margin: 10px 0;"></div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    col_idx += 1
        
        # Navegación entre páginas
        st.write("**Navegación entre páginas:**")
        
        # Barra de progreso visual
        progress_percent = min(100, (current_page / st.session_state.total_pages) * 100)
        progress_html = f"""
        <div style="width:100%; background-color:#f0f0f0; height:10px; border-radius:5px; margin:10px 0;">
            <div style="width:{progress_percent}%; background-color:#4cc2ff; height:10px; border-radius:5px;"></div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
        
        # Controles de navegación
        col1, col2, col3 = st.columns([1, 5, 1])
        with col1:
            if st.button("◀ Anterior", key="prev_btn"):
                if current_page > 1:
                    st.session_state.current_page = current_page - 1
                    st.rerun()
        with col2:
            page_slider = st.slider("Página actual", 1, max(1, st.session_state.total_pages), current_page, key="page_slider")
            if page_slider != current_page:
                st.session_state.current_page = page_slider
                st.rerun()
        with col3:
            if st.button("Siguiente ▶", key="next_btn"):
                if current_page < st.session_state.total_pages - 3:  # -3 porque mostramos 4 miniaturas a la vez
                    st.session_state.current_page = current_page + 1
                    st.rerun()
