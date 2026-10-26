import sys
import os
# Esto le dice a Python que busque módulos en la carpeta padre (app/)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import threading

# Ahora estas importaciones funcionarán sin problemas
from auth import obtener_password_hash

DB_URL = os.getenv("DATABASE_URL", "postgresql://admin:adminpassword@db:5432/servicedesk")
engine = create_engine(DB_URL)
API_URL = "http://localhost:8000"

# --- P01: Autenticación y Seguridad (Baja Lógica) ---
def test_p01_auth_y_baja_logica():
    hashed_pass = obtener_password_hash("password123")

    with engine.begin() as conn:
        # Insertar usuario y darle un rol (id=1)
        conn.execute(text("""
            INSERT INTO usuarios (username, password_hash, email, activo) 
            VALUES ('test_agent', :hash, 'test@example.com', true)
            ON CONFLICT (username) DO UPDATE SET activo = true, password_hash = :hash
        """), {"hash": hashed_pass})
        
        conn.execute(text("""
            INSERT INTO usuarios_roles (usuario_id, rol_id) 
            SELECT id, 1 FROM usuarios WHERE username = 'test_agent'
            ON CONFLICT DO NOTHING
        """))

    # Login exitoso
    res = requests.post(f"{API_URL}/token", data={"username": "test_agent", "password": "password123"})
    assert res.status_code == 200, f"P01 Fallo: Login debió ser exitoso, retornó {res.status_code} - {res.text}"
    
    # Simular baja lógica
    with engine.begin() as conn:
        conn.execute(text("UPDATE usuarios SET activo = false WHERE username = 'test_agent'"))
    
    # Reintentar login (debe fallar con 401)
    res2 = requests.post(f"{API_URL}/token", data={"username": "test_agent", "password": "password123"})
    assert res2.status_code == 401, "P01 Fallo: Usuario inactivo pudo loguearse"

# --- P03: Generación de CMDB sin duplicados ---
def test_p03_cmdb_integridad():
    with engine.connect() as conn:
        dupes = conn.execute(text("""
            SELECT codigo_unico, COUNT(*) FROM ci_dispositivos 
            GROUP BY codigo_unico HAVING COUNT(*) > 1
        """)).fetchall()
        assert len(dupes) == 0, "P03 Fallo: Existen dispositivos con códigos únicos duplicados"
        
        total = conn.execute(text("SELECT COUNT(*) FROM ci_dispositivos")).scalar()
        assert total >= 5000, f"P03 Fallo: Faltan dispositivos (hay {total})"

# --- P07: Concurrencia (Dos agentes intentan tomar el mismo ticket) ---
def test_p07_concurrencia_tomar_ticket():
    with engine.begin() as conn:
        # Crear el solicitante y DOS agentes válidos
        conn.execute(text("""
            INSERT INTO usuarios (username, password_hash, email, activo) 
            VALUES ('solicitante_test', 'hash', 'soli@example.com', true),
                   ('agent1', 'hash', 'agent1@test.com', true),
                   ('agent2', 'hash', 'agent2@test.com', true)
            ON CONFLICT (username) DO NOTHING
        """))
        
        solicitante_id = conn.execute(text("SELECT id FROM usuarios WHERE username = 'solicitante_test'")).scalar()
        agente1_id = conn.execute(text("SELECT id FROM usuarios WHERE username = 'agent1'")).scalar()
        agente2_id = conn.execute(text("SELECT id FROM usuarios WHERE username = 'agent2'")).scalar()

        # Crear ticket huérfano
        result = conn.execute(text("""
            INSERT INTO tickets (titulo, descripcion, estado, prioridad, proceso_id, cola_id, solicitante_id) 
            VALUES ('Ticket Concurrencia', 'Test de SRE', 'Nuevo', 'Alta', 1, 1, :soli_id)
            RETURNING id
        """), {"soli_id": solicitante_id})
        ticket_id = result.scalar()

    resultados = []
    
    def tomar_ticket(agente_id):
        try:
            from tickets_service import tomar_ticket as service_tomar
            with Session(engine) as session:
                service_tomar(session, ticket_id, agente_id)
                resultados.append("Exito")
        except Exception as e:
            print(f"Agente {agente_id} falló: {e}")
            resultados.append("Conflict")

    # Lanzar hilos con los IDs de los agentes
    t1 = threading.Thread(target=tomar_ticket, args=(agente1_id,))
    t2 = threading.Thread(target=tomar_ticket, args=(agente2_id,))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert resultados.count("Exito") == 1, f"P07 Fallo: Resultados {resultados}"
    assert resultados.count("Conflict") == 1, f"P07 Fallo: Resultados {resultados}"
    
    with engine.connect() as conn:
        asignado = conn.execute(text("SELECT asignado_a_id FROM tickets WHERE id = :id"), {"id": ticket_id}).scalar()
        assert asignado is not None, "P07 Fallo: El ticket quedó huérfano"