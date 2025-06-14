CREATE TABLE actividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                lugar TEXT NOT NULL,
                plazas INTEGER NOT NULL,
                categoria TEXT NOT NULL,
                activo BOOLEAN NOT NULL DEFAULT 1
            );
CREATE TABLE comentarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actividad_id INTEGER NOT NULL,
                usuario TEXT NOT NULL,
                comentario TEXT,
                puntuacion INTEGER, fecha TEXT,
                FOREIGN KEY (actividad_id) REFERENCES actividades (id)
            );
CREATE TABLE inscripciones (
                actividad_id INTEGER NOT NULL,
                usuario_email TEXT NOT NULL,
                PRIMARY KEY (actividad_id, usuario_email),
                FOREIGN KEY (actividad_id) REFERENCES actividades (id),
                FOREIGN KEY (usuario_email) REFERENCES usuarios (email)
            );
CREATE TABLE empresa (
                nombre TEXT NOT NULL,
                direccion TEXT NOT NULL,
                telefono TEXT NOT NULL,
                email TEXT NOT NULL,
                cif TEXT NOT NULL
            );
CREATE TABLE categorias (
                nombre TEXT PRIMARY KEY,
                icono TEXT NOT NULL,
                color TEXT NOT NULL
            );
CREATE TABLE IF NOT EXISTS "usuarios" (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    email TEXT ,

    password TEXT  ,

    perfil TEXT NOT NULL,

    nombre TEXT,

    telefono TEXT,

    direccion TEXT,

    fecha_registro TEXT,

    condiciones_medicas TEXT,

    gustos TEXT

, activo INTEGER DEFAULT (1));
