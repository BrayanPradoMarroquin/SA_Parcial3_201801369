-- 1. VINCULACIÓN CI <-> SERVICIOS (Catálogo)
CREATE TABLE ci_servicios (
    ci_id INT REFERENCES ci_dispositivos(id) ON DELETE CASCADE,
    servicio_codigo_n2 VARCHAR(15) REFERENCES catalogo_n2(codigo) ON DELETE CASCADE,
    PRIMARY KEY (ci_id, servicio_codigo_n2)
);

-- 2. RELACIONES TÉCNICAS ENTRE CI (Grafos)
-- Distinguimos de la jerarquía de clasificación (que ya está en ci_clases)
CREATE TABLE ci_relaciones (
    id SERIAL PRIMARY KEY,
    origen_id INT REFERENCES ci_dispositivos(id) ON DELETE CASCADE,
    destino_id INT REFERENCES ci_dispositivos(id) ON DELETE CASCADE,
    tipo_relacion VARCHAR(50) NOT NULL CHECK (tipo_relacion IN ('depende_de', 'conectado_a', 'alojado_en')),
    UNIQUE(origen_id, destino_id, tipo_relacion)
);

-- 3. Añadir campos del CMDB.xlsx que faltaban en la tabla de dispositivos
ALTER TABLE ci_dispositivos 
ADD COLUMN IF NOT EXISTS documentacion_url TEXT,
ADD COLUMN IF NOT EXISTS nivel_seguridad VARCHAR(50),
ADD COLUMN IF NOT EXISTS estado_configuracion VARCHAR(50),
ADD COLUMN IF NOT EXISTS licencia VARCHAR(100),
ADD COLUMN IF NOT EXISTS fecha_vencimiento DATE;