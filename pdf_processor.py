import fitz  # PyMuPDF
import io
import os
import numpy as np
from PIL import Image

class PDFProcessor:
    def __init__(self, pdf_path):
        """
        Initialize the PDF processor with a PDF file path
        
        Args:
            pdf_path: Path to the PDF file (can be a temporary file)
        """
        self.pdf_path = pdf_path
        # Abrir el documento con opciones para archivos grandes
        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)
        self.original_filename = None
        
        # Configuración de memoria para archivos grandes
        self.page_cache = {}  # Caché para miniaturas, para evitar procesamiento repetido
        self.memory_optimized = self.total_pages > 100  # Si hay muchas páginas, optimizar memoria
    
    def get_total_pages(self):
        """Return the total number of pages in the PDF"""
        return self.total_pages
    
    def get_page_image(self, page_idx, zoom=0.5):
        """
        Get a page as a PIL Image with reduced resolution for thumbnails
        Optimizado para documentos grandes con caché de imágenes
        
        Args:
            page_idx: Page index (0-based)
            zoom: Zoom factor to control thumbnail size
            
        Returns:
            PIL Image object
        """
        # Verificar si la imagen ya está en caché
        cache_key = f"{page_idx}_{zoom}"
        if cache_key in self.page_cache:
            return self.page_cache[cache_key]
            
        # Para archivos grandes, reducimos aún más el zoom para mejorar rendimiento
        if self.memory_optimized and zoom > 0.3:
            # Usar un zoom más bajo para documentos grandes
            actual_zoom = 0.3
        else:
            actual_zoom = zoom
            
        try:
            # Cargar la página específica
            page = self.doc[page_idx]
            
            # Get the page as an image with reduced resolution
            pix = page.get_pixmap(matrix=fitz.Matrix(actual_zoom, actual_zoom))
            
            # Convert pixmap to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            # Guardar en caché si el documento es grande
            if self.memory_optimized:
                self.page_cache[cache_key] = img
                
                # Limitar el tamaño del caché para no consumir demasiada memoria
                if len(self.page_cache) > 50:  # Mantener como máximo 50 miniaturas en memoria
                    oldest_key = next(iter(self.page_cache))
                    del self.page_cache[oldest_key]
                    
            return img
        except Exception as e:
            # En caso de error con páginas específicas, retornar una imagen en blanco
            print(f"Error al procesar página {page_idx}: {str(e)}")
            return Image.new('RGB', (100, 150), color='white')
    
    def get_page_as_array(self, page_idx):
        """
        Get a page as a numpy array for image processing
        
        Args:
            page_idx: Page index (0-based)
            
        Returns:
            numpy array representation of the page
        """
        page = self.doc[page_idx]
        
        # Get the page as an image at a reasonable resolution
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        # Convert pixmap to PIL Image
        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        
        # Convert PIL Image to numpy array
        return np.array(img)
    
    def split_pdf(self, split_points, output_dir, mid_page_splits=None, original_filename=None):
        """
        Split the PDF at the specified page numbers and save to output_dir
        Optimizado para archivos grandes mediante procesamiento por lotes
        
        Args:
            split_points: List of page numbers (1-based) where to split
            output_dir: Directory to save the split PDFs
            mid_page_splits: Dictionary {page_num: y_coord} for pages to split at specific points
            original_filename: Original name of the uploaded file to use as base for split files
            
        Returns:
            List of paths to the split PDF files
        """
        if not split_points:
            return []
        
        import sys
        import gc
        
        # Configurar límites de memoria más altos para archivos grandes
        is_large_file = os.path.getsize(self.pdf_path) > 100 * 1024 * 1024  # > 100MB
        
        # Ensure the split points are in ascending order
        split_points = sorted(split_points)
        
        # Add the last page + 1 to handle the final segment
        all_split_points = [0] + split_points + [self.total_pages]
        
        output_files = []
        
        # Usar el nombre original proporcionado directamente como parámetro
        if original_filename:
            # Usar el nombre del archivo original pasado como parámetro
            filename_base = os.path.splitext(original_filename)[0]
        elif self.original_filename:
            # Usar el nombre original guardado en la instancia si está disponible
            filename_base = os.path.splitext(self.original_filename)[0]
        else:
            # Si no hay nombre original disponible, usar el nombre del archivo temporal
            temp_name = os.path.basename(self.pdf_path)
            filename_base = os.path.splitext(temp_name)[0]
        
        # Obtener la extensión original o usar .pdf por defecto
        file_extension = ".pdf"
        if original_filename:
            ext = os.path.splitext(original_filename)[1]
            if ext:
                file_extension = ext
        
        # Create each split PDF
        for i in range(len(all_split_points) - 1):
            start_page = all_split_points[i]
            end_page = all_split_points[i + 1]
            
            # Skip empty segments
            if end_page <= start_page:
                continue
            
            try:
                # Para archivos grandes, trabajar con menos páginas a la vez
                if is_large_file and (end_page - start_page) > 50:
                    # Dividir en bloques de 30 páginas para evitar problemas de memoria
                    final_output_path = os.path.join(
                        output_dir, 
                        f"{filename_base}-{start_page+1}-{end_page}{file_extension}"
                    )
                    
                    # Crear un documento temporal vacío
                    temp_doc = fitz.open()
                    
                    # Procesar en bloques de máximo 30 páginas
                    batch_size = 30
                    for batch_start in range(start_page, end_page, batch_size):
                        batch_end = min(batch_start + batch_size, end_page)
                        
                        # Liberar memoria explícitamente
                        gc.collect()
                        
                        # Añadir este lote de páginas
                        temp_doc.insert_pdf(
                            self.doc, 
                            from_page=batch_start, 
                            to_page=batch_end-1
                        )
                    
                    # Guardar el archivo final
                    temp_doc.save(final_output_path)
                    temp_doc.close()
                    
                    output_files.append(final_output_path)
                    
                    # Liberar memoria
                    gc.collect()
                else:
                    # Proceso normal para archivos pequeños o segmentos pequeños
                    new_doc = fitz.open()
                    
                    # Add pages from the original document
                    for page_num in range(start_page, end_page):
                        new_doc.insert_pdf(self.doc, from_page=page_num, to_page=page_num)
                    
                    # Save the new document with page range in the filename
                    start_page_num = all_split_points[i] + 1  # Convert to 1-based for display
                    end_page_num = all_split_points[i+1]
                    
                    # Usar exactamente el nombre original con guiones y números de página
                    output_path = os.path.join(
                        output_dir, 
                        f"{filename_base}-{start_page_num}-{end_page_num}{file_extension}"
                    )
                    
                    new_doc.save(output_path)
                    new_doc.close()
                    
                    output_files.append(output_path)
            
            except Exception as e:
                print(f"Error al procesar segmento de páginas {start_page+1}-{end_page}: {str(e)}")
                # Continuar con el siguiente segmento en caso de error
                continue
        
        # Liberar memoria antes de finalizar
        gc.collect()
        
        return output_files
        
    def get_page_dimensions(self, page_idx):
        """
        Obtiene las dimensiones de una página
        
        Args:
            page_idx: Índice de la página (0-based)
            
        Returns:
            Tuple (width, height) con las dimensiones de la página
        """
        page = self.doc[page_idx]
        rect = page.rect
        return (rect.width, rect.height)
