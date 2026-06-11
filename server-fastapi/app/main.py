# main.py
from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import facturas, estadisticas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(facturas.router,     prefix="/api")
app.include_router(estadisticas.router, prefix="/api")

@app.get("/")
def root():
    return {"mensaje": "API del restaurante funcionando"}
