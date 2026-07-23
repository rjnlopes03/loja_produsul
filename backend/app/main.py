from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine, SessionLocal
from .routers import auth, marcas, produtos, movimentacoes, clientes

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Produsul Cereais - Controle de Estoque")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):5173",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(marcas.router)
app.include_router(produtos.router)
app.include_router(movimentacoes.router)
app.include_router(clientes.router)


@app.on_event("startup")
def seed_marcas():
    db = SessionLocal()
    try:
        if db.query(models.Marca).count() == 0:
            db.add_all([models.Marca(nome=n) for n in ["Golden", "Premier Pet", "Royal Canin", "Purina"]])
            db.commit()
    finally:
        db.close()


@app.get("/")
def raiz():
    return {"status": "ok", "servico": "Produsul Cereais API"}
