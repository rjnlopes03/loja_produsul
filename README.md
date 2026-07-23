# Loja Produsul

Sistema de controle de estoque de rações da Produsul Cereais.

Permite cadastrar, editar, remover e filtrar rações por espécie de animal
(cachorro, gato, coelho, galinha, cavalo, vaca, multiespécie) e por fase de
vida (filhote, adulto, sênior, qualquer), além de registrar movimentações de
entrada e saída de estoque e controlar contas de clientes (fiado mensal).

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

#### Autenticação

Toda a API (exceto `POST /auth/login`) exige um token obtido no login.
Credenciais configuráveis via variáveis de ambiente:

```bash
AUTH_USERNAME=admin   # default: admin
AUTH_PASSWORD=admin   # default: admin
```

Em desenvolvimento, sem configurar nada, o login padrão é `admin` / `admin`.
Troque `AUTH_PASSWORD` antes de expor o backend fora da máquina local.

#### Migrations (Alembic)

Mudanças de schema em `app/models.py` devem ser acompanhadas de uma migration:

```bash
cd backend
alembic revision --autogenerate -m "descrição da mudança"
alembic upgrade head
```

Em um checkout novo (banco ainda não existe), rode `alembic upgrade head` para criar o schema.

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
    models.py       # Marca, Produto (Ração), Movimentação, Cliente, Compra, Pagamento
    schemas.py       # Schemas Pydantic
    auth.py           # Autenticação (login, validação de token)
    routers/          # Rotas CRUD (auth, marcas, produtos, movimentacoes, clientes)
    main.py           # App FastAPI + seed de marcas
frontend/
  src/
    pages/            # Login, Estoque, Nova Ração, Marcas, Movimentacoes, Clientes, ClienteDetalhe
    api/client.js      # Cliente HTTP da API
```
