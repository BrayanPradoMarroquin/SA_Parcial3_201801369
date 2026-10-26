import os
import random
from faker import Faker
from sqlalchemy import create_engine, text
from psycopg2.extras import execute_values

DB_URL = os.getenv("DATABASE_URL", "postgresql://admin:adminpassword@db:5432/servicedesk")
engine = create_engine(DB_URL)
fake = Faker()
Faker.seed(42) # Semilla configurable para reproducibilidad
random.seed(42)

def generar_dispositivos(cantidad=5000):
    print(f"Generando {cantidad} dispositivos...")
    
    with engine.connect() as conn:
        # 1. Obtener clases existentes (Hardware, Software, Redes)
        clases = conn.execute(text("SELECT id, nombre, nivel FROM ci_clases")).fetchall()
        if not clases:
            print("Error: No hay clases en la CMDB. Ejecuta el init.sql primero.")
            return
            
        clases_hardware = [c for c in clases if c.nombre in ['Servidores', 'Equipos de Usuario', 'Switches']]
        clase_software = [c for c in clases if c.nombre == 'Software'][0]

        dispositivos = []
        relaciones = []
        
        # Listas para distribución
        estados = ['Activo', 'En Mantenimiento', 'Obsoleto', 'En Almacen']
        ubicaciones = ['Sala de Servidores 1', 'Sala de Servidores 2', 'Edificio A - Piso 1', 'Edificio B - Piso 3']
        seguridades = ['Alto', 'Medio', 'Bajo']

        for i in range(cantidad):
            # Asignación aleatoria de clase (Mayoría Hardware, algo de Software)
            if i % 10 == 0:
                clase_id = clase_software.id
                tipo_nombre = clase_software.nombre
                atributos_tecnicos = '{"version_sw": "v1.0", "tipo_licencia": "Suscripción"}'
            else:
                clase_elegida = random.choice(clases_hardware)
                clase_id = clase_elegida.id
                tipo_nombre = clase_elegida.nombre
                atributos_tecnicos = '{"ram_gb": 16, "cpu": "Intel i7", "ip": "192.168.1.' + str(i) + '"}' if 'Servidores' in tipo_nombre or 'Switches' in tipo_nombre else '{"ram_gb": 8, "cpu": "Intel i5"}'

            dispositivos.append((
                clase_id,
                f"CI-{i+1:05d}", # Código único: CI-00001
                f"{tipo_nombre}-{fake.word().capitalize()}-{i}",
                random.choice(estados),
                random.choice(ubicaciones),
                fake.name(), # Propietario sintético
                f"SN-{fake.uuid4()[:8]}",
                "v1.0",
                fake.date_between(start_date='-5y', end_date='today'),
                atributos_tecnicos,
                "http://docs.local/manual.pdf",
                random.choice(seguridades),
                "Aprobado",
                f"LIC-{fake.random_number(digits=6)}",
                fake.date_between(start_date='today', end_date='+2y')
            ))

        # Inserción masiva de dispositivos
        insert_query = """
            INSERT INTO ci_dispositivos 
            (clase_id, codigo_unico, nombre, estado, ubicacion_fisica, propietario, numero_serie, version, fecha_adquisicion, atributos_tecnicos, documentacion_url, nivel_seguridad, estado_configuracion, licencia, fecha_vencimiento)
            VALUES %s
            RETURNING id
        """
        result = execute_values(conn.connection.cursor(), insert_query, dispositivos, fetch=True)
        ids_generados = [row[0] for row in result]
        
        # 2. Crear Relaciones Técnicas (Grafos)
        print("Generando relaciones técnicas (Grafos)...")
        # Ejemplo: Servidores dependen de Switches, Software alojado en Servidores
        for _ in range(int(cantidad * 0.2)): # Generamos 1000 relaciones
            origen = random.choice(ids_generados)
            destino = random.choice(ids_generados)
            if origen != destino:
                tipo = random.choice(['depende_de', 'conectado_a', 'alojado_en'])
                relaciones.append((origen, destino, tipo))

        insert_rel_query = """
            INSERT INTO ci_relaciones (origen_id, destino_id, tipo_relacion)
            VALUES %s ON CONFLICT DO NOTHING
        """
        execute_values(conn.connection.cursor(), insert_rel_query, relaciones)
        
        conn.commit()
        print(f"Éxito: {len(dispositivos)} dispositivos y {len(relaciones)} relaciones insertadas.")
        
        # Reporte por categoría (Requisito)
        resumen = conn.execute(text("""
            SELECT c.nombre, COUNT(d.id) 
            FROM ci_clases c 
            LEFT JOIN ci_dispositivos d ON c.id = d.clase_id 
            GROUP BY c.nombre
        """)).fetchall()
        
        print("\n--- Reporte de Distribución ---")
        for row in resumen:
            print(f"Categoría: {row[0]} | Cantidad: {row[1]}")

if __name__ == "__main__":
    generar_dispositivos(5000)