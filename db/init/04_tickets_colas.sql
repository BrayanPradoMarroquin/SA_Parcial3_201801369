-- 1. LOS 7 PROCESOS OBLIGATORIOS
CREATE TABLE procesos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL
);

INSERT INTO procesos (codigo, nombre) VALUES 
('NUEVOS_SERVICIOS', 'Gestión de nuevos servicios'),
('CAMBIOS', 'Gestión de cambios'),
('INCIDENTES', 'Gestión de incidentes'),
('EVENTOS', 'Gestión de eventos'),
('PROBLEMAS', 'Gestión de problemas'),
('ACCESOS', 'Gestión de accesos'),
('SERVICIOS_TEC', 'Gestión de servicios de tecnología');

-- 2. COLAS (Configuración exacta: una cola pertenece a un solo proceso)
CREATE TABLE colas (
    id SERIAL PRIMARY KEY,
    proceso_id INT REFERENCES procesos(id) ON DELETE RESTRICT,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activa BOOLEAN DEFAULT TRUE,
    nivel_soporte INT DEFAULT 1, -- Niveles 0-4
    reglas_ordenamiento VARCHAR(100) DEFAULT 'prioridad_desc, fecha_creacion_asc'
);

-- Insertar las 7 colas obligatorias (una por proceso)
INSERT INTO colas (proceso_id, codigo, nombre, descripcion) VALUES
(1, 'COLA-NUEVOS', 'Cola Nuevos Servicios', 'Atención de requerimientos de nuevos servicios'),
(2, 'COLA-CAMBIOS', 'Cola Cambios', 'Gestión de cambios de infraestructura'),
(3, 'COLA-INCIDENTES', 'Cola Incidentes', 'Resolución de incidentes de TI'),
(4, 'COLA-EVENTOS', 'Cola Eventos', 'Monitoreo y gestión de eventos'),
(5, 'COLA-PROBLEMAS', 'Cola Problemas', 'Investigación de causa raíz'),
(6, 'COLA-ACCESOS', 'Cola Accesos', 'Gestión de solicitudes de acceso'),
(7, 'COLA-SERVICIOS', 'Cola Servicios Tecnología', 'Requisiciones de servicios de TI');

-- 3. TICKETS (El núcleo del sistema)
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    solicitante_id INT REFERENCES usuarios(id),
    creador_id INT REFERENCES usuarios(id),
    servicio_n2_id VARCHAR(15) REFERENCES catalogo_n2(codigo),
    servicio_n1_id VARCHAR(10) REFERENCES catalogo_n1(codigo), -- Derivado automáticamente
    proceso_id INT REFERENCES procesos(id),
    cola_id INT REFERENCES colas(id),
    asignado_a_id INT REFERENCES usuarios(id), -- Agente responsable
    estado VARCHAR(50) NOT NULL DEFAULT 'Nuevo',
    prioridad VARCHAR(20) NOT NULL,
    impacto VARCHAR(20),
    urgencia VARCHAR(20),
    canal VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion TIMESTAMP,
    fecha_cierre TIMESTAMP,
    -- COLUMNA CRÍTICA PARA CONCURRENCIA (Optimistic Locking fallback)
    version INT DEFAULT 1
);

-- 4. BITÁCORA / HISTORIAL (Trazabilidad obligatoria)
CREATE TABLE ticket_historial (
    id SERIAL PRIMARY KEY,
    ticket_id INT REFERENCES tickets(id) ON DELETE CASCADE,
    actor_id INT REFERENCES usuarios(id),
    accion VARCHAR(100) NOT NULL, -- ej: 'CREACION', 'ASIGNACION', 'CAMBIO_ESTADO'
    valor_anterior JSONB,
    valor_nuevo JSONB,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. COMENTARIOS (Visibles vs Internos)
CREATE TABLE ticket_comentarios (
    id SERIAL PRIMARY KEY,
    ticket_id INT REFERENCES tickets(id) ON DELETE CASCADE,
    autor_id INT REFERENCES usuarios(id),
    contenido TEXT NOT NULL,
    es_interno BOOLEAN DEFAULT FALSE, -- TRUE = Nota interna, FALSE = Visible al solicitante
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);