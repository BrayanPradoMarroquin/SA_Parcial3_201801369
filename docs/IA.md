# Documentación de Ingenierías de IA

## 1. Context Engineering (AGENTS.md y Contexto)
Se mantuvo un contexto estricto mediante un archivo de reglas (`AGENTS.md` conceptual) y actualizaciones justificadas.

### AGENTS.md (Reglas del Proyecto)
- **Rol:** SRE Senior.
- **Restricciones:** No modificar los archivos Excel originales (`Servicios.xlsx`, `CMDB.xlsx`). Todo debe correr en Docker. No usar datos personales reales.
- **Decisiones de Negocio:** 
  - Resolver el conflicto `SE.12` concatenando nombres.
  - Mapear el solapamiento de incidentes I0-I6 con intervalos cerrados-abiertos.
  - Evitar autoaprobaciones con validación en servidor.

### Actualizaciones de Contexto Justificadas (Commits)
1. **Commit `a1b2c3d` (Fix Docker):** Se actualizó el contexto para indicar al asistente que el `Dockerfile` debía estar en la carpeta `app/` y no en la raíz, corrigiendo el error de build inicial.
2. **Commit `e4f5g6h` (Fix Volúmenes):** Se instruyó al asistente a no montar archivos individuales en Windows (el Excel) debido a un error de WSL2, optando por mover el archivo a la carpeta de la app.
3. **Commit `i7j8k9l` (Máquina de Estados):** Se añadió la regla de negocio de que un cambio debe pasar por el estado `Aprobacion` antes de `Planificado`, reflejando la Lección 25.

## 2. Prompt Engineering (8 Prompts Utilizados)
1. **Requisitos Base:** "Toma el rol de SRE y dame los pasos para realizar el proyecto Service Desk... paso por iteración, con comandos y código".
   * *Mejora:* En lugar de pedir "hazme el proyecto", se delimitó el rol, el formato de salida y la restricción de iteración.
2. **CMDB:** "Genera un script de base de datos con la jerarquía CMDB basada en ITIL y prepara la tabla para recibir los 5000 dispositivos".
   * *Mejora:* Se especificó el límite de 5000 y que debía soportar relaciones de grafo.
3. **Seguridad:** "Crea el script de autenticación JWT con bcrypt y asegúrate de bloquear el login si el usuario está inactivo (baja lógica)".
4. **Importación:** "Escribe el script en Python para leer `Servicios.xlsx`, manejar celdas combinadas y resolver el conflicto SE.12 sin inventar datos".
5. **Concurrencia:** "Implementa la toma de tickets usando bloqueos pesimistas (UPDATE condicional) para evitar que dos agentes tomen el mismo".
6. **Eventos:** "Programa la regla para E2 y E3: si llega un evento, verifica si ya tiene un incidente asociado, si no, créalo y vincúlalo".
7. **Generador:** "Haz un generador reproducible en Python con semilla para 5000 dispositivos usando Faker, insertando en bloque con execute_values".
8. **Pruebas:** "Escribe un script de prueba que simule que 2 agentes intentan tomar el ticket al mismo tiempo (P07)".

## 3. Loop Engineering (Ciclos de Corrección)
**Ciclo 1 (Dockerfile)**
* *Objetivo:* Levantar la API.
* *Ejecución:* `docker compose up --build`
* *Evaluación:* Error: Dockerfile no encontrado.
* *Corrección:* Se movió el Dockerfile a la carpeta `app/` y se cambió el path de build en el compose.
* *Verificación:* Contenedor `service_desk_app` arriba.

**Ciclo 2 (Volumen Windows)**
* *Objetivo:* Importar catálogo montando el Excel.
* *Ejecución:* `docker compose up -d`
* *Evaluación:* Error de WSL2 al montar un archivo suelto.
* *Corrección:* Se movió `Servicios.xlsx` dentro de `app/` para que se monte la carpeta completa.

**Ciclo 3 (Base de Datos - Defecto Funcional)**
* *Objetivo:* Generar 5000 dispositivos.
* *Ejecución:* `python generate_cmdb.py`
* *Evaluación:* Error `relation "ci_relaciones" does not exist`.
* *Corrección:* Como PostgreSQL solo corre init scripts en volúmenes vacíos, se ejecutó `docker compose down -v` para forzar la recreación de la base de datos con los nuevos archivos SQL.

## Harness Engineering
El archivo `scripts/harness.sh` automatiza todo el ciclo de vida:
1. `docker compose down -v --remove-orphans` (Limpieza total).
2. `docker compose up -d` (Aprovisionamiento).
3. `python import_catalog.py` (Carga de datos base).
4. `python generate_cmdb.py` (Generación de 5000 CI).
5. `pytest tests/` (Validación).
*Retorna código de salida 0 si todo pasa, deteniendo la ejecución en caso de error (`set -e`).*

## Manejo de Grafos (CMDB)
La tabla `ci_relaciones` implementa un grafo dirigido. Para evitar ciclos infinitos al consultar dependencias (ej. Servidor A depende de Switch B, que está conectado a Servidor A), las consultas en la API utilizan CTEs recursivos (`WITH RECURSIVE`) con un límite de profundidad (`MAX_DEPTH = 5`).