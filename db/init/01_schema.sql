-- 1. JERARQUÍA ORGANIZACIONAL
CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE areas (
    id SERIAL PRIMARY KEY,
    empresa_id INT REFERENCES empresas(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE departamentos (
    id SERIAL PRIMARY KEY,
    area_id INT REFERENCES areas(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE secciones (
    id SERIAL PRIMARY KEY,
    departamento_id INT REFERENCES departamentos(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE puestos (
    id SERIAL PRIMARY KEY,
    seccion_id INT REFERENCES secciones(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL
);

-- 2. USUARIOS Y ROLES (Base del Parcial + Nuevos)
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    puesto_id INT REFERENCES puestos(id) ON DELETE SET NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Almacenará bcrypt/argon2
    email VARCHAR(100) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE, -- Bajas lógicas
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. JERARQUÍA DE LA CMDB (Clasificación original)
-- Se modela como árbol para reproducir los niveles de la Lección 22 / CMDB.xlsx
CREATE TABLE ci_clases (
    id SERIAL PRIMARY KEY,
    padre_id INT REFERENCES ci_clases(id) ON DELETE RESTRICT, -- Evita ciclos si se maneja bien en app
    nombre VARCHAR(100) NOT NULL,
    nivel INT NOT NULL,
    UNIQUE(padre_id, nombre)
);

-- 4. DISPOSITIVOS / CI (Preparado para los 5,000)
CREATE TABLE ci_dispositivos (
    id SERIAL PRIMARY KEY,
    clase_id INT REFERENCES ci_clases(id) ON DELETE RESTRICT,
    codigo_unico VARCHAR(100) UNIQUE NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    estado VARCHAR(50) NOT NULL,
    ubicacion_fisica VARCHAR(150),
    propietario VARCHAR(150),
    numero_serie VARCHAR(100),
    version VARCHAR(50),
    fecha_adquisicion DATE,
    -- Atributos dinámicos/JSON para los campos del CMDB.xlsx que no aplican a todos
    atributos_tecnicos JSONB DEFAULT '{}'::jsonb,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);