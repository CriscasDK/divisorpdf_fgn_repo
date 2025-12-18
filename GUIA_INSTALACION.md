# Guía de Instalación en Servidor Ubuntu

Esta guía te ayudará a instalar el Divisor de PDF desde GitHub a tu servidor Ubuntu.

## Paso 1: Preparar el entorno

Primero, asegúrate de tener Python 3 y pip instalados:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

## Paso 2: Clonar el repositorio

```bash
# Clona el repositorio (reemplaza "tu-usuario" con tu nombre de usuario de GitHub)
git clone https://github.com/tu-usuario/pdf_splitter.git

# Entra al directorio del proyecto
cd pdf_splitter
```

## Paso 3: Crear y activar entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

## Paso 4: Instalar dependencias

```bash
# Instalar las bibliotecas necesarias
pip install opencv-python-headless pymupdf streamlit pillow numpy
```

## Paso 5: Configurar Streamlit para archivos grandes

```bash
# Crear directorio de configuración
mkdir -p .streamlit

# Crear archivo de configuración
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

## Paso 6: Crear carpeta para archivos divididos

```bash
mkdir -p pdf_divididos
```

## Paso 7: Ejecutar la aplicación

```bash
streamlit run app.py --server.maxUploadSize=1000
```

## Paso 8: Configurar como servicio (opcional)

Si quieres que la aplicación se ejecute automáticamente al iniciar el sistema:

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/pdf-splitter.service
```

Añade este contenido (reemplaza las rutas y el usuario):

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

Activa el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pdf-splitter
sudo systemctl start pdf-splitter
```

## Paso 9: Acceder a la aplicación

Abre un navegador y accede a:

```
http://tu-direccion-ip:5000
```

## Solución de problemas

Si encuentras el error "Limit 200MB per file":
1. Asegúrate de usar el parámetro `--server.maxUploadSize=1000`
2. Verifica que el archivo de configuración `.streamlit/config.toml` exista y tenga el contenido correcto
3. Reinicia la aplicación o el servicio después de hacer cambios