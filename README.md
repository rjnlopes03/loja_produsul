# Loja Produsul

Sistema de controle de estoque de rações da Produsul Cereais.

Permite cadastrar, editar, remover e filtrar rações por espécie de animal
(cachorro, gato, coelho, galinha, cavalo, vaca) e por fase de vida
(filhote, adulto, sênior, castrado), além de registrar movimentações de
entrada e saída de estoque.

## Stack

- **Backend:** Python + FastAPI + SQLAlchemy
- **Banco de dados:** SQLite (via SQLAlchemy, arquivo `backend/loja.db`)
- **Frontend:** JavaScript + React + Vite

## Como rodar

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API disponível em `http://localhost:8000` (docs em `/docs`).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Aplicação disponível em `http://localhost:5173`.

## Estrutura

```text
backend/
  app/
    models.py       # Marca, Produto (Ração), Movimentação
    schemas.py       # Schemas Pydantic
    routers/          # Rotas CRUD (marcas, produtos, movimentacoes)
    main.py           # App FastAPI + seed de marcas
frontend/
  src/
    pages/            # Estoque, Nova Ração, Marcas
    api/client.js      # Cliente HTTP da API
```
