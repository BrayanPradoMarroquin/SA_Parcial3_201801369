import pandas as pd
from sqlalchemy import create_engine, text # <-- Añadido 'text'
import os

# Configuración DB
DB_URL = os.getenv("DATABASE_URL", "postgresql://admin:adminpassword@localhost:5432/servicedesk")
engine = create_engine(DB_URL)

def importar_catalogo(ruta_excel):
    # Leer saltando las primeras 3 filas de títulos
    df = pd.read_excel(ruta_excel, sheet_name='Servicios Externos', skiprows=3)
    
    # Limpiar columnas vacías
    df = df.dropna(how='all')
    
    # Rellenar hacia adelante los códigos N1 (esto maneja las celdas combinadas del Excel)
    df['COD.N1'] = df['COD.N1'].ffill()
    df['SERVICIO - Nivel 1'] = df['SERVICIO - Nivel 1'].ffill()

    # 1. Insertar Nivel 1 (Evitando duplicados)
    n1_data = df[['COD.N1', 'SERVICIO - Nivel 1']].drop_duplicates(subset=['COD.N1'])
    
    with engine.begin() as conn:
        for _, row in n1_data.iterrows():
            # Tratamiento documentado del conflicto SE.12
            if row['COD.N1'] == 'SE.12':
                # Concatenamos ambas descripciones para no perder información de la fuente
                nombre_n1 = "Suministrar Analitica / Mantener Tableros de Control"
            else:
                nombre_n1 = row['SERVICIO - Nivel 1']
            
            conn.execute(
                text("INSERT INTO catalogo_n1 (codigo, nombre) VALUES (:c, :n) ON CONFLICT (codigo) DO NOTHING"),
                {"c": row['COD.N1'], "n": nombre_n1}
            )

    # 2. Insertar Nivel 2 (Solo los que tienen código N2)
    n2_data = df.dropna(subset=['COD.N2'])
    
    with engine.begin() as conn:
        for _, row in n2_data.iterrows():
            # Tratar datos ausentes como NULL, NO como cero.
            def safe_val(val):
                return None if pd.isna(val) else val

            conn.execute(
                text("""
                    INSERT INTO catalogo_n2 
                    (codigo, codigo_n1, nombre, descripcion, activo, clase_servicio, criticidad, tipo_servicio, metrica, minimo, maximo) 
                    VALUES (:c, :c1, :n, :d, :a, :cs, :cr, :ts, :m, :min, :max)
                    ON CONFLICT (codigo) DO NOTHING
                """),
                {
                    "c": row['COD.N2'], "c1": row['COD.N1'], "n": row['SERVICIO - Nivel 2'],
                    "d": safe_val(row.get('Descripción')), "a": safe_val(row.get('ACTIVO')),
                    "cs": safe_val(row.get('CLASE DE SERVICIO')), "cr": safe_val(row.get('CRITICIDAD')),
                    "ts": safe_val(row.get('TIPO DE SERVICIO')), "m": safe_val(row.get('Métrica')),
                    "min": safe_val(row.get('Minimo')), "max": safe_val(row.get('Maximo'))
                }
            )

    print("Importación completada.")

# Al final del archivo
if __name__ == "__main__":
    importar_catalogo("Servicios.xlsx") 