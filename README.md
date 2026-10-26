# Service Desk - Parcial 3 (SRE)

## Requisitos
* Docker y Docker Compose instalados.
* No se requiere instalar Python, PostgreSQL ni dependencias locales.

## Ejecución desde un clon limpio
Para levantar todo el entorno, importar catálogo, generar la CMDB y ejecutar las pruebas automáticas:
```bash
docker compose down -v --remove-orphans
docker compose up --build -d
# Esperar 10 segundos a que Postgres inicialice
bash scripts/harness.sh
```

## Acceso
API Docs (Swagger): http://localhost:8000/docs

Base de Datos: localhost:5432 (Usuario: admin, Pass: adminpassword, DB: servicedesk)

## Cuentas de Demostración
Admin: admin / password123 (Creada vía seed o script)

Agente: agent1 / password123

Solicitante: solicitante_test / password123

