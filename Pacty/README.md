# Pacty

Una aplicación basada en Kivy para gestionar actividades y registros de usuarios.

## Instalación

0. Entra en la carpeta raíz del proyecto:
```bash
cd Pacty
```


1. Crea un entorno virtual:
```bash
python -m venv venv
```

2. Activa el entorno virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecuta la migración de la base de datos:
```bash
python migrate.py
```

5. Ejecuta la aplicación:
```bash
python src/app.py
```

## Funcionalidades

- Autenticación y gestión de usuarios
- Creación y gestión de actividades
- Registro de usuarios en actividades
- Valoraciones y comentarios de actividades
- Gestión de información de empresas

## Base de datos

La aplicación utiliza SQLite para el almacenamiento de datos. El archivo de la base de datos se encuentra en `data/pacty.db`.

## Estructura del proyecto

- `src/`: Código fuente
  - `screens/`: Definición de pantallas
  - `utils/`: Funciones utilitarias y módulo de base de datos
  - `app.py`: Archivo principal de la aplicación
- `data/`: Directorio de datos
  - `pacty.db`: Archivo de base de datos SQLite
- `migrate.py`: Script de migración de la base de datos
- `requirements.txt`: Dependencias de Python

## Uso

Tras ejecutar `python main.py`, debería cargar la aplicación

## Estructura de la base de datos

- `users`: Usuarios registrados
- `activities`: Actividades disponibles
- `categories`: Categorías de actividades
- `companies`: Información de empresas

## Contribuir

¿Quieres colaborar? Haz un fork, crea una rama y envía un pull request.

## Licencia

Licencia MIT

## Soporte

Para dudas o problemas, abre un issue en este repositorio.