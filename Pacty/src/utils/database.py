import sqlite3
from pathlib import Path
import json
from datetime import datetime
from src.utils.load_json import load_json

class Database:
    def __init__(self):
        self.db_path = Path("src/data/pacty.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.migrate_from_json()

    def create_tables(self):
        """Create all necessary tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                email TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                perfil TEXT NOT NULL,
                nombre TEXT NOT NULL,
                telefono TEXT,
                direccion TEXT,
                fecha_registro TEXT,
                condiciones_medicas TEXT
            )
        """)
        
        # actividades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                lugar TEXT NOT NULL,
                plazas INTEGER NOT NULL,
                categoria TEXT NOT NULL,
                activo BOOLEAN NOT NULL DEFAULT 1
            )
        """)
        
        # comentarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comentarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actividad_id INTEGER NOT NULL,
                usuario TEXT NOT NULL,
                comentario TEXT,
                puntuacion INTEGER,
                fecha TEXT,
                FOREIGN KEY (actividad_id) REFERENCES actividades (id)
            )
        """)
        
        # inscripciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inscripciones (
                actividad_id INTEGER NOT NULL,
                usuario_email TEXT NOT NULL,
                PRIMARY KEY (actividad_id, usuario_email),
                FOREIGN KEY (actividad_id) REFERENCES actividades (id),
                FOREIGN KEY (usuario_email) REFERENCES usuarios (email)
            )
        """)
        
        # empresa
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresa (
                nombre TEXT NOT NULL,
                direccion TEXT NOT NULL,
                telefono TEXT NOT NULL,
                email TEXT NOT NULL,
                cif TEXT NOT NULL
            )
        """)
        
        # empresa
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresa (
                nombre TEXT PRIMARY KEY,
                icono TEXT NOT NULL,
                color TEXT NOT NULL
            )
        """)
        
        self.conn.commit()

    def migrate_from_json(self):
        """Migrar datos JSON files to SQLite database."""
        data_dir = Path("src/data")
        
        # Migrar usuarios
        usuarios_file = data_dir / "usuarios.json"
        if usuarios_file.exists():
            with open(usuarios_file, "r", encoding="utf-8") as f:
                usuarios = json.load(f)
                for email, usuario in usuarios.items():
                    self.save_usuario(email, usuario)
        
        # Migrar actividades
        actividades_file = data_dir / "actividades.json"
        if actividades_file.exists():
            with open(actividades_file, "r", encoding="utf-8") as f:
                actividades = json.load(f)
                for actividad in actividades:
                    # Guardar actividad
                    self.save_actividad(actividad)
                    
                    # Guardar comentarios
                    for comentario in actividad.get('comentarios', []):
                        self.add_comentario(
                            actividad['id'],
                            comentario['usuario'],
                            comentario.get('comentario', ''),
                            comentario.get('puntuacion', 0)
                        )
        
        # Migrar inscripciones
        inscripciones_file = data_dir / "inscripciones.json"
        if inscripciones_file.exists():
            with open(inscripciones_file, "r", encoding="utf-8") as f:
                inscripciones = json.load(f)
                for actividad_id, emails in inscripciones.items():
                    for email in emails:
                        self.add_inscripcion(int(actividad_id), email)
        
        # Migrar empresa
        empresa_file = data_dir / "empresa.json"
        if empresa_file.exists():
            with open(empresa_file, "r", encoding="utf-8") as f:
                empresa = json.load(f)
                self.save_empresa(empresa)
        
        # Migrar categorías
        iconos_file = data_dir / "iconos_categorias.json"
        colores_file = data_dir / "color_categorias.json"
        if iconos_file.exists() and colores_file.exists():
            with open(iconos_file, "r", encoding="utf-8") as f:
                iconos = json.load(f)
            with open(colores_file, "r", encoding="utf-8") as f:
                colores = json.load(f)
            for categoria in iconos:
                self.save_categoria(categoria, iconos[categoria], colores.get(categoria, "#000000"))

    def authenticate_user(self, email, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        return user is not None

    def get_usuario(self, email):
        """Get user by email."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def save_usuario(self, email, data):
        """Save or update user data."""
        cursor = self.conn.cursor()
        
        # Verificar si el usuario existe
        cursor.execute("SELECT email FROM usuarios WHERE email = ?", (email,))
        if not cursor.fetchone():
            # Si el usuario no existe, no permitimos crear uno nuevo con datos incompletos
            return False
            
        # Si hay un nuevo email en los datos y es diferente al actual
        nuevo_email = data.get("email")
        if nuevo_email and nuevo_email != email:
            # Verificar si el nuevo email ya existe
            cursor.execute("SELECT email FROM usuarios WHERE email = ?", (nuevo_email,))
            if cursor.fetchone():
                return False  # El nuevo email ya está en uso
                
            # Actualizar el email en la tabla de usuarios
            cursor.execute("""
                UPDATE usuarios 
                SET email = ?,
                    nombre = ?,
                    telefono = ?,
                    direccion = ?,
                    condiciones_medicas = ?
                WHERE email = ?
            """, (
                nuevo_email,
                data.get("nombre", ""),
                data.get("telefono", ""),
                data.get("direccion", ""),
                data.get("condiciones_medicas", ""),
                email
            ))
            
            # Actualizar el email en las inscripciones
            cursor.execute("""
                UPDATE inscripciones 
                SET usuario_email = ? 
                WHERE usuario_email = ?
            """, (nuevo_email, email))
            
            # Actualizar el email en los comentarios
            cursor.execute("""
                UPDATE comentarios 
                SET usuario = ? 
                WHERE usuario = ?
            """, (nuevo_email, email))
        else:
            # Si no hay cambio de email, actualizar solo los otros campos
            cursor.execute("""
                UPDATE usuarios 
                SET nombre = ?,
                    telefono = ?,
                    direccion = ?,
                    condiciones_medicas = ?,
                    gustos = ?             
                WHERE email = ?
            """, (
                data.get("nombre", ""),
                data.get("telefono", ""),
                data.get("direccion", ""),
                data.get("condiciones_medicas", ""),
                data.get("gustos", ""),    
                email
            ))
            
        self.conn.commit()
        return True

    def get_all_actividades(self):
        """Get all activities with their comments and registrations."""
        cursor = self.conn.cursor()
        actividades = []
        
        # Get all activities
        cursor.execute("SELECT * FROM actividades ORDER BY fecha, hora")
        for actividad in cursor.fetchall():
            actividad_dict = dict(actividad)
            
            # Get comments
            cursor.execute("SELECT * FROM comentarios WHERE actividad_id = ?", (actividad['id'],))
            actividad_dict['comentarios'] = [dict(com) for com in cursor.fetchall()]
            
            # Get registrations
            cursor.execute("SELECT usuario_email FROM inscripciones WHERE actividad_id = ?", (actividad['id'],))
            actividad_dict['inscritos'] = [row['usuario_email'] for row in cursor.fetchall()]
            
            actividades.append(actividad_dict)
        
        return actividades

    def save_actividad(self, data):
        """Save or update activity data."""
        cursor = self.conn.cursor()
        # Verifica si la actividad ya existe
        cursor.execute("SELECT id FROM actividades WHERE id = ?", (data.get("id"),))
        if cursor.fetchone():
            # Si existe, haz UPDATE
            cursor.execute("""
                UPDATE actividades
                SET nombre = ?, descripcion = ?, fecha = ?, hora = ?, lugar = ?, plazas = ?, categoria = ?, activo = ?
                WHERE id = ?
            """, (
                data.get("nombre", ""),
                data.get("descripcion", ""),
                data.get("fecha", ""),
                data.get("hora", ""),
                data.get("lugar", ""),
                data.get("plazas", 0),
                data.get("categoria", ""),
                data.get("activo", True),
                data.get("id")
            ))
        else:
            # Si no existe, haz INSERT
            cursor.execute("""
                INSERT INTO actividades (id, nombre, descripcion, fecha, hora, lugar, plazas, categoria, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("id"),
                data.get("nombre", ""),
                data.get("descripcion", ""),
                data.get("fecha", ""),
                data.get("hora", ""),
                data.get("lugar", ""),
                data.get("plazas", 0),
                data.get("categoria", ""),
                data.get("activo", True)
            ))
        self.conn.commit()

    def get_empresa(self):
        """Get company data."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM empresa LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None

    def save_empresa(self, data):
        """Save or update company data."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO empresa (nombre, direccion, telefono, email, cif)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.get("nombre", ""),
            data.get("direccion", ""),
            data.get("telefono", ""),
            data.get("email", ""),
            data.get("cif", "")
        ))
        self.conn.commit()

    def get_categorias(self):
        """Get all categories with their icons and colors."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT nombre, icono, color FROM categorias")
        return {row["nombre"]: {"icono": row["icono"], "color": row["color"]} for row in cursor.fetchall()}

    def save_categoria(self, nombre, icono, color="#000000"):
        """Save or update category data."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO categorias (nombre, icono, color)
            VALUES (?, ?, ?)
        """, (nombre, icono, color))
        self.conn.commit()

    def delete_categoria(self, nombre):
        """Delete a category."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM categorias WHERE nombre = ?", (nombre,))
        self.conn.commit()

    def add_comentario(self, actividad_id, usuario, comentario, puntuacion, fecha=None):
        """Add a comment to an activity."""
        cursor = self.conn.cursor()
        if fecha is None:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("""
            INSERT INTO comentarios (actividad_id, usuario, comentario, puntuacion, fecha)
            VALUES (?, ?, ?, ?, ?)
        """, (actividad_id, usuario, comentario, puntuacion, fecha))
        self.conn.commit()

    def get_inscripcion(self, actividad_id, usuario_email):
        """Get registration for an activity and user."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM inscripciones 
            WHERE actividad_id = ? AND usuario_email = ?
        """, (actividad_id, usuario_email))
        row = cursor.fetchone()
        return dict(row) if row else None

    def add_inscripcion(self, actividad_id, usuario_email):
        """Add a registration for an activity."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO inscripciones (actividad_id, usuario_email)
            VALUES (?, ?)
        """, (actividad_id, usuario_email))
        self.conn.commit()

    def remove_inscripcion(self, actividad_id, usuario_email):
        """Remove a registration for an activity."""
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM inscripciones 
            WHERE actividad_id = ? AND usuario_email = ?
        """, (actividad_id, usuario_email))
        self.conn.commit()

    def get_all_usuarios(self):
        """Devuelve todos los usuarios como un diccionario {email: datos}."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT email, password, perfil, nombre, telefono, direccion, fecha_registro, condiciones_medicas, gustos FROM usuarios")
        usuarios = {}
        for row in cursor.fetchall():
            email, password, perfil, nombre, telefono, direccion, fecha_registro, condiciones_medicas, gustos = row
            usuarios[email] = {
                "password": password,
                "perfil": perfil,
                "nombre": nombre,
                "telefono": telefono,
                "direccion": direccion,
                "fecha_registro": fecha_registro,
                "condiciones_medicas": condiciones_medicas,
                "gustos": gustos
            }
        return usuarios

    def get_configuracion(self):
        """Devuelve los iconos y colores de las categorías desde la base de datos."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT nombre, icono, color FROM categorias")
        iconos = {}
        colores = {}
        for row in cursor.fetchall():
            iconos[row["nombre"]] = row["icono"]
            colores[row["nombre"]] = row["color"]
        return {
            "iconos_categorias": iconos,
            "color_categorias": colores
        }

    def close(self):
        """Close the database connection."""
        self.conn.close()