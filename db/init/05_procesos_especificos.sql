-- 1. MÁQUINA DE ESTADOS (Transiciones permitidas)
CREATE TABLE transiciones_estado (
    id SERIAL PRIMARY KEY,
    proceso_id INT REFERENCES procesos(id),
    estado_origen VARCHAR(50) NOT NULL,
    estado_destino VARCHAR(50) NOT NULL,
    rol_requerido VARCHAR(50) -- Rol que puede hacer esta transición
);

-- Insertar transiciones para "CAMBIOS" (Ejemplo estricto)
INSERT INTO transiciones_estado (proceso_id, estado_origen, estado_destino, rol_requerido) VALUES
(2, 'Nuevo', 'Evaluacion', 'Agente'),
(2, 'Evaluacion', 'Aprobacion', 'Agente'),
(2, 'Aprobacion', 'Planificado', 'Aprobador'), -- No se pasa a ejecución sin aprobación
(2, 'Aprobacion', 'Rechazado', 'Aprobador'),
(2, 'Planificado', 'Ejecutado', 'Agente'),
(2, 'Ejecutado', 'Cerrado', 'Agente');

-- 2. DETALLES DE INCIDENTES (I0-I6 y reglas de duración)
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS categoria_incidente VARCHAR(5); -- I0, I1, etc.
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS solucion_aplicada TEXT;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS duracion_estimada_horas NUMERIC;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS duracion_real_horas NUMERIC;

-- 3. DETALLES DE EVENTOS (E0-E3)
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS categoria_evento VARCHAR(5); -- E0, E1, E2, E3
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS requiere_respuesta_operativa BOOLEAN DEFAULT FALSE;

-- 4. DETALLES DE CAMBIOS (CI afectados, plan de pruebas y rollback)
CREATE TABLE cambios_detalle (
    ticket_id INT PRIMARY KEY REFERENCES tickets(id) ON DELETE CASCADE,
    ci_afectado_id INT, -- Referencia a un CI que crearemos en el Paso 5
    plan_pruebas TEXT NOT NULL,
    plan_reversion TEXT NOT NULL,
    aprobado_por_id INT REFERENCES usuarios(id)
);

-- 5. DETALLES DE ACCESOS (Beneficiario, recurso, permiso)
CREATE TABLE accesos_detalle (
    ticket_id INT PRIMARY KEY REFERENCES tickets(id) ON DELETE CASCADE,
    beneficiario_id INT REFERENCES usuarios(id) NOT NULL,
    recurso VARCHAR(100) NOT NULL,
    permiso_requerido VARCHAR(100) NOT NULL
);

-- 6. DETALLES DE PROBLEMAS Y NUEVOS SERVICIOS
CREATE TABLE problemas_detalle (
    ticket_id INT PRIMARY KEY REFERENCES tickets(id) ON DELETE CASCADE,
    causa_raiz TEXT,
    error_conocido BOOLEAN DEFAULT FALSE,
    cambio_solucion_id INT REFERENCES tickets(id) -- Vinculación con el cambio
);

CREATE TABLE nuevos_servicios_detalle (
    ticket_id INT PRIMARY KEY REFERENCES tickets(id) ON DELETE CASCADE,
    servicio_catalogo_vinculado VARCHAR(15) REFERENCES catalogo_n2(codigo), -- Sin duplicar
    analisis_viabilidad TEXT
);