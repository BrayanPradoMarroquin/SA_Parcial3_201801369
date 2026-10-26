# Resolución del Proyecto

## Arquitectura
* **Base de Datos:** PostgreSQL 15 (Docker).
* **Backend:** Python 3.11 con FastAPI y SQLAlchemy 2.0.
* **Infraestructura:** Docker Compose (Aislamiento total).

## Decisiones Clave
* **SE.12:** Se unificó el nombre para no perder datos del Excel original.
* **Categorías I0-I6:** Se usó intervalo semiabierto para evitar solapamientos. I0 (0h), I1 (0-3h], I2 (3-8h], I3 (8-48h], I4 (48-168h], I5 (>168h), I6 (Seguridad).
* **Concurrencia:** Bloqueo atómico a nivel de fila en PostgreSQL (`UPDATE ... WHERE asignado IS NULL`) para evitar *race conditions*.
* **Niveles de soporte:** Se adoptó Nivel 0 a 4, mapeando a proveedores en Nivel 3.

## Limitaciones
* El envío de notificaciones (Ej. E2/E3 genera incidente) se hace registrando el evento en la base de datos y en la bitácora, no vía correo real (según lo permitido por el enunciado).
* La interfaz gráfica de UI no fue implementada (el foco está en la API REST y la lógica SRE robusta), validable a través de Swagger (`/docs`).