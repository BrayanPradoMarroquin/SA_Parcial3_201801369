from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from datetime import datetime

# --- REGLA DE DECISIÓN DE PROYECTO: Solapamiento de Incidentes I0-I6 ---
# El enunciado dice que los tiempos se solapan. Nuestra regla determinista será:
# I0: 0 horas (No causa interrupción)
# I1: 0 < horas <= 3
# I2: 3 < horas <= 8
# I3: 8 < horas <= 48 (2 días)
# I4: 48 < horas <= 168 (1 semana)
# I5: > 168 horas (1 mes o más)
# I6: Seguridad de la información (independiente del tiempo)
def calcular_categoria_incidente(horas_estimadas: float, es_seguridad: bool) -> str:
    if es_seguridad:
        return "I6"
    if horas_estimadas == 0:
        return "I0"
    elif horas_estimadas <= 3:
        return "I1"
    elif horas_estimadas <= 8:
        return "I2"
    elif horas_estimadas <= 48:
        return "I3"
    elif horas_estimadas <= 168:
        return "I4"
    else:
        return "I5"

def validar_transicion(db: Session, ticket_id: int, nuevo_estado: str, usuario_rol: str):
    # Obtener el ticket actual
    ticket = db.execute(text("SELECT proceso_id, estado FROM tickets WHERE id = :id"), {"id": ticket_id}).fetchone()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    proceso_id, estado_actual = ticket
    
    # Verificar si la transición existe en la máquina de estados
    transicion = db.execute(text("""
        SELECT rol_requerido FROM transiciones_estado 
        WHERE proceso_id = :proc AND estado_origen = :origen AND estado_destino = :destino
    """), {"proc": proceso_id, "origen": estado_actual, "destino": nuevo_estado}).fetchone()
    
    if not transicion:
        raise HTTPException(status_code=400, detail=f"Transición inválida de {estado_actual} a {nuevo_estado}")
    
    rol_req = transicion[0]
    if rol_req and rol_req != usuario_rol:
        raise HTTPException(status_code=403, detail=f"Se requiere rol {rol_req} para esta acción")

def procesar_evento(db: Session, ticket_id: int, categoria_evento: str, usuario_id: int):
    """Lógica para E0-E3"""
    if categoria_evento not in ['E0', 'E1', 'E2', 'E3']:
        raise HTTPException(status_code=400, detail="Categoría de evento inválida")
    
    # Actualizar el ticket de evento
    db.execute(text("""
        UPDATE tickets SET categoria_evento = :cat, fecha_actualizacion = CURRENT_TIMESTAMP 
        WHERE id = :id
    """), {"cat": categoria_evento, "id": ticket_id})
    
    # E2 y E3 requieren creación/vinculación de incidente
    if categoria_evento in ['E2', 'E3']:
        # Evitar duplicados: Verificar si este evento ya generó un incidente
        incidente_existente = db.execute(text("""
            SELECT id FROM tickets WHERE titulo = :titulo AND proceso_id = 3
        """), {"titulo": f"Incidente generado por Evento #{ticket_id}"}).fetchone()
        
        if not incidente_existente:
            # Crear incidente automático (I6 si es E3, I2 por defecto si es E2)
            cat_inc = "I6" if categoria_evento == "E3" else "I2"
            db.execute(text("""
                INSERT INTO tickets (titulo, descripcion, proceso_id, estado, prioridad, categoria_incidente)
                VALUES (:titulo, :desc, 3, 'Nuevo', 'Alta', :cat_inc)
            """), {
                "titulo": f"Incidente generado por Evento #{ticket_id}",
                "desc": "Incidente autogenerado por regla E2/E3",
                "cat_inc": cat_inc
            })
            # Nota: En un entorno real, aquí se dispararía la notificación.
    
    db.commit()
    return {"status": "success", "message": f"Evento {categoria_evento} procesado"}

def aprobar_solicitud_acceso(db: Session, ticket_id: int, aprobador_id: int, aprobado: bool):
    """Impide la autoaprobación"""
    # Obtener el solicitante del ticket
    ticket = db.execute(text("SELECT solicitante_id FROM tickets WHERE id = :id"), {"id": ticket_id}).fetchone()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    if ticket[0] == aprobador_id:
        raise HTTPException(status_code=403, detail="Seguridad: Un usuario no puede aprobar su propia solicitud")
    
    nuevo_estado = "Aprobado" if aprobado else "Rechazado"
    db.execute(text("UPDATE tickets SET estado = :estado WHERE id = :id"), {"estado": nuevo_estado, "id": ticket_id})
    
    # Registrar en historial
    db.execute(text("""
        INSERT INTO ticket_historial (ticket_id, actor_id, accion, valor_nuevo)
        VALUES (:id, :actor, 'APROBACION_ACCESO', CAST(:nuevo AS JSONB))
    """), {"id": ticket_id, "actor": aprobador_id, "nuevo": f'{{"estado": "{nuevo_estado}"}}'})
    
    db.commit()
    return {"status": "success", "message": f"Acceso {nuevo_estado}"}