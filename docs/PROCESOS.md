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