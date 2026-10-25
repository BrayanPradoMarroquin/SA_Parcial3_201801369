-- Roles y Permisos
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL -- Admin, Agente, Solicitante, Consulta, Aprobador
);

CREATE TABLE usuarios_roles (
    usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    rol_id INT REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (usuario_id, rol_id)
);

-- Catálogo de Servicios
CREATE TABLE catalogo_n1 (
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE catalogo_n2 (
    codigo VARCHAR(15) PRIMARY KEY,
    codigo_n1 VARCHAR(10) REFERENCES catalogo_n1(codigo),
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    activo VARCHAR(5),
    clase_servicio VARCHAR(50),
    criticidad VARCHAR(50),
    tipo_servicio VARCHAR(50),
    metrica VARCHAR(100),
    minimo NUMERIC,
    maximo NUMERIC,
    activo_logico BOOLEAN DEFAULT TRUE
);

-- Insertar Roles Base
INSERT INTO roles (nombre) VALUES 
('Admin'), ('Agente'), ('Solicitante'), ('Consulta'), ('Aprobador');