# main.py
from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import menu, pedidos

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(menu.router, prefix="/api")
app.include_router(pedidos.router, prefix="/api")

@app.get("/")
def root():
    return {"mensaje": "API del restaurante funcionando"}
