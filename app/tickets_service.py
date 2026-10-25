from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException

def tomar_ticket(db: Session, ticket_id: int, agente_id: int):
    """
    Asigna un ticket a un agente de forma atómica.
    Si otro agente ya lo tomó, lanza un error 409 (Conflict).
    """
    # Iniciamos una transacción explícita
    try:
        # El UPDATE condicional (WHERE asignado_a_id IS NULL) es atómico en Postgres.
        # Si dos agentes entran a la vez, solo el primero afectará 1 fila. El segundo afectará 0 filas.
        result = db.execute(
            text("""
                UPDATE tickets 
                SET asignado_a_id = :agente_id, 
                    estado = 'En Proceso', 
                    fecha_actualizacion = CURRENT_TIMESTAMP,
                    version = version + 1
                WHERE id = :ticket_id AND asignado_a_id IS NULL
                RETURNING id
            """),
            {"agente_id": agente_id, "ticket_id": ticket_id}
        )
        
        row = result.fetchone()
        
        if row is None:
            db.rollback()
            raise HTTPException(status_code=409, detail="El ticket ya fue tomado por otro agente o no existe.")
            
        # Registrar en la bitácora (Auditoría)
        db.execute(
            text("""
                INSERT INTO ticket_historial (ticket_id, actor_id, accion, valor_nuevo)
                VALUES (:ticket_id, :actor_id, 'ASIGNACION', CAST(:nuevo AS JSONB))
            """),
            {"ticket_id": ticket_id, "actor_id": agente_id, "nuevo": f'{{"asignado_a": {agente_id}}}'}
        )
        
        db.commit()
        return {"status": "success", "message": "Ticket asignado correctamente"}
        
    except Exception as e:
        db.rollback()
        raise e