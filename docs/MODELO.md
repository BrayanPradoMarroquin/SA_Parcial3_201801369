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