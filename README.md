# Divisor de PDF para Documentos Legales

Aplicación web desarrollada con Streamlit que permite dividir archivos PDF extensos en documentos más pequeños, especialmente útil para documentos legales.

## Características

- Carga archivos PDF de hasta 1 GB
- Visualización de miniaturas para facilitar la selección de puntos de división
- Detección automática de firmas y sellos como posibles puntos de división
- Interfaz gráfica intuitiva con visualización horizontal de páginas
- Procesamiento optimizado para PDFs muy grandes
- Descarga todos los PDFs divididos en un único archivo ZIP

## Instalación en servidor Ubuntu

1. Clona este repositorio:
```bash
git clone https://github.com/tu-usuario/pdf_splitter.git
cd pdf_splitter
```

2. Crea un entorno virtual y actívalo:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instala las dependencias:
```bash
pip install opencv-python-headless pymupdf streamlit pillow numpy
```

4. Configura Streamlit para archivos grandes:
```bash
mkdir -p .streamlit
cat > .streamlit/config.toml << EOF
[server]
headless = true
address = "0.0.0.0"
port = 5000
maxUploadSize = 1000

[global]
developmentMode = false

[browser]
gatherUsageStats = false
EOF
```

5. Crea la carpeta para los PDFs divididos:
```bash
mkdir -p pdf_divididos
```

6. Ejecuta la aplicación:
```bash
streamlit run app.py --server.maxUploadSize=1000
```

## Configuración como servicio (opcional)

Para mantener la aplicación ejecutándose continuamente:

1. Crea un archivo de servicio:
```bash
sudo nano /etc/systemd/system/pdf-splitter.service
```

2. Añade el siguiente contenido (ajusta las rutas):
```
[Unit]
Description=PDF Splitter Streamlit App
After=network.target

[Service]
User=tu_usuario
WorkingDirectory=/ruta_completa/a/pdf_splitter
ExecStart=/ruta_completa/a/pdf_splitter/venv/bin/streamlit run app.py --server.maxUploadSize=1000
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

3. Activa e inicia el servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pdf-splitter
sudo systemctl start pdf-splitter
```

## Uso

1. Abre la aplicación en tu navegador: `http://direccion-del-servidor:5000`
2. Sube un archivo PDF
3. Revisa y ajusta los puntos de división sugeridos
4. Divide el PDF
5. Descarga el archivo ZIP con todos los PDFs divididos