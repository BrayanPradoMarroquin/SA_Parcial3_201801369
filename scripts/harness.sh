#!/bin/bash
set -e # Detiene la ejecución si hay un error

echo "=== 🚀 SRE HARNESS: PREPARANDO ENTORNO ==="
docker compose down -v --remove-orphans
docker compose up --build -d
echo "Esperando a que PostgreSQL inicie..."
sleep 10

echo "=== 📦 SRE HARNESS: IMPORTANDO CATÁLOGO ==="
docker exec -it service_desk_app python import_catalog.py

echo "=== 🖥️ SRE HARNESS: GENERANDO CMDB ==="
docker exec -it service_desk_app python generate_cmdb.py

echo "=== 🧪 SRE HARNESS: EJECUTANDO PRUEBAS (P01-P18) ==="
docker exec -it service_desk_app pytest tests/ -v

echo "=== ✅ SRE HARNESS: TODO OK. SISTEMA LISTO ==="