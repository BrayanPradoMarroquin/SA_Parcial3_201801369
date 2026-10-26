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

## Mapeo de Procesos a Tipos de Ticket (Lección 25)
*   **Solicitud de acceso:** Mapeado al proceso de Gestión de Accesos.
*   **Evento:** Mapeado al proceso de Gestión de Eventos.
*   **Incidente:** Mapeado al proceso de Gestión de Incidentes.
*   **Solicitud de cambio:** Mapeado al proceso de Gestión de Cambios.
*   **Requisición de servicio:** Mapeado a Gestión de Servicios de Tecnología (para servicios existentes) y Gestión de Nuevos Servicios (como subtipo para creación de servicios).
*   **Problema:** Mapeado al proceso de Gestión de Problemas.

## Decisión de Proyecto: Solapamiento I0-I6
Dado que los rótulos temporales de la presentación se solapan (ej. I1 e I2 comparten el límite de 3 horas y 8 horas), se define la siguiente regla de intervalo cerrado-abierto para el motor de base de datos:
*   **I0:** 0 hrs.
*   **I1:** (0, 3] hrs.
*   **I2:** (3, 8] hrs.
*   **I3:** (8, 48] hrs.
*   **I4:** (48, 168] hrs.
*   **I5:** > 168 hrs.
*   **I6:** Categoría transversal exclusiva para incidentes de seguridad de la información.
*   **Niveles de soporte:** Se adopta el esquema configurable 0-4 (Autoservicio, Help Desk, Soporte Técnico, Ingenieros, Externo), mapeando a los proveedores en el Nivel 3 (resolviendo la discrepancia entre la diapositiva 11 y 12-13).