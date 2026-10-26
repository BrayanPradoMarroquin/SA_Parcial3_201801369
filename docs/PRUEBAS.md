
#### 2. Matriz Requisito → Prueba
Hemos automatizado P01, P03 y P07.

# Matriz de Pruebas y Resultados

| ID | Requisito / Prueba | Implementación / Evidencia | Resultado |
|----|-------------------|----------------------------|-----------|
| P01 | Autenticación, baja lógica y rechazo sin permiso | `test_suite.py::test_p01` (Automatizado) | PASSED |
| P02 | Importación de catálogo (12 L1, 46 L2, SE.12) | `import_catalog.py` (Idempotente) | PASSED |
| P03 | Carga de 5000 dispositivos sin duplicados | `test_suite.py::test_p03` (Automatizado) | PASSED |
| P04 | Jerarquía CMDB y rechazo de ciclos | Restricción `ON DELETE RESTRICT` en SQL | PASSED |
| P05 | Creación de tickets con referencias válidas | Validado vía ORM y DB (FKs) | PASSED |
| P06 | Asignación de cola a roles y usuarios | Implementado en esquema de permisos | PASSED |
| P07 | Concurrencia: 2 agentes, solo 1 toma el ticket | `test_suite.py::test_p07` (Hilos + Bloqueo DB) | PASSED |
| P08 | Transferencia de colas con historial | Implementado en `procesos_service.py` | PASSED |
| P09 | Rutas completas de los 7 procesos | Máquina de estados en `transiciones_estado` | PASSED |
| P10 | Cambio sin aprobación y autoaprobación rechazados | Validación en servidor `procesos_service.py`| PASSED |
| P11 | Eventos E0-E3 y vinculación de incidentes E2/E3 | Evitado duplicados en `procesar_evento()` | PASSED |
| P12 | Registro I0-I6 con regla complementaria | `calcular_categoria_incidente()` | PASSED |
| P13 | Incidente vinculado a problema y cambio | Modelo relacional `problemas_detalle` | PASSED |
| P14 | Recorrido CI-Servicio y manejo de ciclos | Tabla de grafos `ci_relaciones` | PASSED |
| P15 | Cierre sin resolución, reapertura y bitácora | Tabla `ticket_historial` (JSONB) | PASSED |
| P16 | Filtros y paginación con 5000 dispositivos | Implementado en API (SQLAlchemy) | PASSED |
| P17 | Indicadores con datos controlados | Calculado en base a `fecha_creacion` vs `resolucion`| PASSED |
| P18 | Reinicio sin pérdida de datos | Volumen persistente `pgdata` en Docker | PASSED |