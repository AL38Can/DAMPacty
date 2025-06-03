-- Añadir columna 'fecha' a la tabla comentarios
ALTER TABLE comentarios ADD COLUMN fecha TEXT;

-- Rellenar fechas para los comentarios existentes (ejemplo, ajusta los IDs según tus datos)
UPDATE comentarios SET fecha = '2025-05-20' WHERE id = 1; -- Antonio, Cata de vinos
UPDATE comentarios SET fecha = '2025-05-21' WHERE id = 2; -- Clara, Cata de vinos

UPDATE comentarios SET fecha = '2025-06-15' WHERE id = 3; -- Juan, Ruta en kayak
UPDATE comentarios SET fecha = '2025-06-15' WHERE id = 4; -- Maria, Ruta en kayak
UPDATE comentarios SET fecha = '2025-06-15' WHERE id = 5; -- Usuario Actual, Ruta en kayak
UPDATE comentarios SET fecha = '2025-06-15' WHERE id = 6; -- Usuario Actual, Ruta en kayak

UPDATE comentarios SET fecha = '2025-06-18' WHERE id = 7; -- Carlos, Senderismo
UPDATE comentarios SET fecha = '2025-06-18' WHERE id = 8; -- Ana, Senderismo

UPDATE comentarios SET fecha = '2025-05-01' WHERE id = 9; -- Lucía, Masaje

UPDATE comentarios SET fecha = '2025-06-14' WHERE id = 10; -- Pedro, Yoga en la playa
UPDATE comentarios SET fecha = '2025-06-14' WHERE id = 11; -- Laura, Yoga en la playa

UPDATE comentarios SET fecha = '2025-06-20' WHERE id = 12; -- Oscar, Bicicross

UPDATE comentarios SET fecha = '2025-06-15' WHERE id = 13; -- Fernando, Clases de surf
UPDATE comentarios SET fecha = '2025-06-15' WHERE id = 14; -- Isabel, Clases de surf

UPDATE comentarios SET fecha = '2025-06-17' WHERE id = 15; -- Sandra, Paseo en globo

UPDATE comentarios SET fecha = '2025-06-16' WHERE id = 16; -- Javier, Esquí acuático

UPDATE comentarios SET fecha = '2025-06-14' WHERE id = 17; -- Sofia, Parapente

UPDATE comentarios SET fecha = '2025-06-17' WHERE id = 18; -- Raúl, Ciclismo de montaña
UPDATE comentarios SET fecha = '2025-06-17' WHERE id = 19; -- Paco, Ciclismo de montaña

-- Si tienes más comentarios, añade más líneas siguiendo el patrón.

-- Comentarios

ALTER TABLE usuarios ADD COLUMN gustos TEXT;

INSERT INTO usuarios (email, password, perfil, nombre, telefono, direccion, fecha_registro, condiciones_medicas, gustos) VALUES
('ana@email.com', '1234', 'cliente', 'Ana Díaz', '600123456', 'Calle Sol 1', '2024-05-01', '', 'Noche, Aventurera'),
('luis@email.com', 'abcd', 'cliente', 'Luis Pérez', '600654321', 'Av. Luna 2', '2024-05-02', 'Asma', 'Día, Tranquilo'),
('marta@email.com', 'pass', 'empleado', 'Marta López', '600987654', 'Calle Río 3', '2024-05-03', '', 'Día, Aventurera'),
('carlos@email.com', 'qwerty', 'cliente', 'Carlos Ruiz', '600321987', 'Plaza Mar 4', '2024-05-04', 'Alergia polen', 'Noche, Tranquilo');



INSERT INTO usuarios (email, password, perfil, nombre, telefono, direccion, fecha_registro, condiciones_medicas, gustos) VALUES
('', '', 'cliente', 'Ana García', '+34 600 123 456', 'Calle Río Verde 23, Granada', '2024-11-02', 'Alergia al polen, asma leve', 'día, tranquilo'),
('e', '', 'empleado', 'Ana García', '+34 600 123 456', 'Calle Río Verde 23, Granada', '2024-11-02', 'Alergia al polen, asma leve', 'noche, aventurero'),
('cliente@example.com', '1234', 'cliente', 'Ana García', '+34 600 123 456', 'Calle Río Verde 23, Granada', '2024-11-02', 'Alergia al polen, asma leve', 'día, tranquilo'),
('empleado@example.com', '1234', 'empleado', 'Carlos Ruiz', '+34 611 654 321', 'Avenida del Trabajo 18, Sevilla', '2023-05-10', '', 'noche, aventurero'),
('admin@example.com', '1234', 'admin', 'Laura Martín', '+34 622 987 654', 'Plaza Mayor 1, Madrid', '2022-01-15', '', 'día, tranquilo'),
('a', '', 'admin', 'Laura Martín', '+34 622 987 654', 'Plaza Mayor 1, Madrid', '2022-01-15', '', 'noche, aventurero');



