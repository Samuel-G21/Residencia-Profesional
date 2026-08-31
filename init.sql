-- Usar la base de datos definida en Docker
USE pemex_db;

-- Tabla para registrar los eventos/cursos impartidos
CREATE TABLE IF NOT EXISTS cursos (
    id_evento VARCHAR(50) PRIMARY KEY,
    nombre_evento VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para el historial de trabajadores capacitados
CREATE TABLE IF NOT EXISTS historial_capacitacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_evento VARCHAR(50),
    ficha_trabajador VARCHAR(50) NOT NULL,
    nombre_trabajador VARCHAR(255) NOT NULL,
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_evento) REFERENCES cursos(id_evento) ON DELETE CASCADE
);