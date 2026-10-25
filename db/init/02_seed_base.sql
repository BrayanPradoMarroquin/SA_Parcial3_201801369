-- Datos Organizacionales Base
INSERT INTO empresas (nombre) VALUES ('FIUSAC');
INSERT INTO areas (empresa_id, nombre) VALUES (1, 'Tecnología');
INSERT INTO departamentos (area_id, nombre) VALUES (1, 'Infraestructura');
INSERT INTO secciones (departamento_id, nombre) VALUES (1, 'Redes');
INSERT INTO puestos (seccion_id, nombre) VALUES (1, 'Administrador de Red');

-- Jerarquía CMDB (Nivel 1)
INSERT INTO ci_clases (nombre, nivel) VALUES ('Hardware', 1), ('Software', 1), ('Redes', 1);
-- Jerarquía CMDB (Nivel 2 - Ejemplo)
INSERT INTO ci_clases (padre_id, nombre, nivel) VALUES 
(1, 'Servidores', 2), 
(1, 'Equipos de Usuario', 2), 
(3, 'Switches', 2);