# Portafolio Django

Este proyecto es una aplicación web desarrollada con Django que permite gestionar y mostrar un portafolio personal de proyectos, con funcionalidades básicas de administración y visualización.

## Características principales

- CRUD para proyectos.
- Panel de administración de Django personalizado.
- Interfaz sencilla para visualizar proyectos.
- Soporte para imágenes y descripciones de cada proyecto.
- Arquitectura modular y escalable.

## Tecnologías usadas

- Python 3.x
- Django 4.x
- HTML5 / CSS3
- SQLite
- Bootstrap 

## Estructura del proyecto

portafolio-django/
├── portafolio/ # Aplicación principal
│ ├── admin.py
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ └── templates/
│ └── portafolio/
│ └── ...html
├── portafolio_django/ # Proyecto Django (settings, urls)
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
├── db.sqlite3 # Base de datos SQLite
└── manage.py # Script principal de Django

## 🚀 Instalación y uso local

1. Clona el repositorio:
```
git clone https://github.com/Betha2516/portafolio-django.git
cd portafolio-django

```

2. Crea y activa un entorno virtual:
```
python -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate
```

3. Instala dependencias:
```
pip install -r requirements.txt
``` 
4. Aplica migraciones y ejecuta el servidor:
```
python manage.py migrate
python manage.py runserver
Accede a: http://localhost:8000
```



