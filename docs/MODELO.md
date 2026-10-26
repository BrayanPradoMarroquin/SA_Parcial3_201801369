# Diccionario y Jerarquía CMDB

## Jerarquía Organizacional
Reproducida del Parcial Práctico 2. Niveles: Empresa → Área → Departamento → Sección → Puesto → Usuario.

## Jerarquía de Clasificación CMDB
*Fuente: Transicion.pptx.pdf (SACM) y CMDB.xlsx*
Se implementa mediante la tabla recursiva `ci_clases`. 
- **Nivel 1:** Hardware, Software, Redes.
- **Nivel 2:** Servidores, Equipos de Usuario, Switches.

## Mapeo de Columnas (CMDB.xlsx)
- Nombre del CI -> `ci_dispositivos.nombre`
- Tipo de CI -> Relación con `ci_clases.id`
- Descripción -> `atributos_tecnicos` (JSONB)
- Número de Serie -> `ci_dispositivos.numero_serie`

### Tratamiento del Conflicto SE.12
Al analizar `Servicios.xlsx`, se identificó que el código Nivel 1 `SE.12` aparece dos veces en la fuente original: "Suministrar Analitica" y "Mantener Tableros de Control". 
**Decisión de proyecto:** No se inventó una nueva categoría. Se preservó el código único `SE.12` en la tabla `catalogo_n1`, concatenando ambos nombres en la descripción para reflejar fielmente el archivo original. Los 3 servicios de nivel 2 asociados (`SE.12.1`, `SE.12.2`, `SE.12.3`) se importaron correctamente respetando la integridad referencial.

### Tratamiento de datos ausentes
Los valores vacíos en el Excel (ej. descripciones en blanco, mínimos/máximos nulos) se importaron como `NULL` en PostgreSQL. **No se convirtieron en 0 ni se inventaron valores**, tal como exige el enunciado.

# Procesos y Colas

Se implementaron los 7 procesos obligatorios. Cada cola en la base de datos (`colas`) apunta exactamente a uno de estos procesos.
1. Gestión de nuevos servicios (`NUEVOS_SERVICIOS`)
2. Gestión de cambios (`CAMBIOS`)
3. Gestión de incidentes (`INCIDENTES`)
4. Gestión de eventos (`EVENTOS`)
5. Gestión de problemas (`PROBLEMAS`)
6. Gestión de accesos (`ACCESOS`)
7. Gestión de servicios de tecnología (`SERVICIOS_TEC`)

**Política de Asignación:** Manual con bloqueo pesimista a nivel de base de datos. El primer agente que envía la petición de "Tomar ticket" es el único que recibe el código HTTP 200; el resto recibe 409 Conflict.

### Jerarquía y Diccionario CMDB
De acuerdo con la lección 22 y `CMDB.xlsx`, la jerarquía implementada en `ci_clases` es:
- Nivel 1: Hardware, Software, Redes.
- Nivel 2: Servidores, Equipos de Usuario, Switches.

**Mapeo de Fuente (CMDB.xlsx a PostgreSQL):**
*   *Nombre del CI* -> `ci_dispositivos.nombre`
*   *Tipo de CI* -> `ci_dispositivos.clase_id` (FK a `ci_clases`)
*   *Descripción / Atributos* -> `ci_dispositivos.atributos_tecnicos` (JSONB)
*   *Número de Serie* -> `ci_dispositivos.numero_serie`
*   *Versión* -> `ci_dispositivos.version`
*   *Fecha de Adquisición* -> `ci_dispositivos.fecha_adquisicion`
*   *Estado Actual* -> `ci_dispositivos.estado`
*   *Relaciones* -> `ci_relaciones` (Grafo técnico: depende_de, conectado_a, alojado_en)
*   *Ubicación Física* -> `ci_dispositivos.ubicacion_fisica`
*   *Propietario/Responsable* -> `ci_dispositivos.propietario`
*   *Niveles de Seguridad* -> `ci_dispositivos.nivel_seguridad`
*   *Cumplimiento* -> `ci_dispositivos.estado_configuracion`
*   *Número de Licencia* -> `ci_dispositivos.licencia`

**Manejo de Ciclos:**
La jerarquía de clasificación (`ci_clases`) tiene una restricción estricta `ON DELETE RESTRICT` y se valida en el servidor para evitar ciclos padre-hijo. Las relaciones técnicas (`ci_relaciones`) permiten ciclos (ej. un servidor depende de un switch y el switch está conectado al servidor), pero se manejan en las consultas de grafos con límites de profundidad para evitar desbordamiento de pila.