import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import auth, models
from .database import engine
from .routers import marcas, produtos, movimentacoes, clientes

# Em produção (DATABASE_URL definida) o sistema fica na internet: exige senha.
if os.getenv("DATABASE_URL") and not auth.ADMIN_PASSWORD:
    raise RuntimeError("Defina ADMIN_PASSWORD para rodar em produção.")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Produsul Cereais - Controle de Estoque")

# Origens extras (ex.: domínio da Vercel), separadas por vírgula.
cors_origins = [o.strip().rstrip("/") for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"http://(localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):5173",
    allow_methods=["*"],
    allow_headers=["*"],
)

protegido = [Depends(auth.exigir_admin)]
app.include_router(auth.router)
app.include_router(marcas.router, dependencies=protegido)
app.include_router(produtos.router, dependencies=protegido)
app.include_router(movimentacoes.router, dependencies=protegido)
app.include_router(clientes.router, dependencies=protegido)


@app.get("/")
def raiz():
    return {"status": "ok", "servico": "Produsul Cereais API"}
