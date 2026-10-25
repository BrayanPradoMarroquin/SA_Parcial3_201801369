from fastapi import FastAPI
from . import auth, models
from .database import engine

# (Opcional: crear tablas si no existen, aunque ya lo hace el init.sql)
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Service Desk API")

app.include_router(auth.router, tags=["Autenticación"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Service Desk API funcionando"}