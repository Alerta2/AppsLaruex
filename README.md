# Bienvenido a Weblaruex: Plataforma Django de servicios del LARUEX

![Weblaruex Logo](http://alerta2.es/static/img/logos/logo_laruex.png)

## Descripción

WebLaruex es una aplicación de servicios del Laboratorio de Radiactividad Ambiental de la Universidad de Extremadura LARUEX

## Instalación

Sigue estos pasos para instalar Weblaruex en tu entorno local:

1. **Clonar el repositorio:**
git clone https://github.com/Alerta2/AppsLaruex.git
2. **Acceder al directorio:**
cd weblaruex
3. **Crear un entorno virtual:**
python -m venv venv o equivalente en conda
4. **Instalar las dependencias:**
pip install -r requirements.txt o importar el entorno en conda
5. **Solicita el fichero de configuración de credenciales:**
El fichero config.ini incluye las credenciales necesarias para el uso de los servicios
6. **Solicita el fichero de configuración de la aplicación Django:**
El fichero settings.py contiene la configuración de las diferentes aplicaciones y rutas de trabajo. Recuerde configurar la ubicación del fichero config.ini 

## Uso

Una vez que tienes Weblaruex instalado y el servidor de desarrollo en funcionamiento, puedes acceder a la plataforma en tu navegador web:
http://localhost:8000/
