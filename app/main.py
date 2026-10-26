from fastapi import FastAPI
import auth
import models
from database import engine

app = FastAPI(title="Service Desk API")

app.include_router(auth.router, tags=["Autenticación"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Service Desk API funcionando"}