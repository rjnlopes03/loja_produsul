# Loja Produsul

Sistema de controle de estoque de rações da Produsul Cereais.

Permite cadastrar, editar, remover e filtrar rações por espécie de animal
(cachorro, gato, coelho, galinha, cavalo, vaca, multiespécie) e por fase de
vida (filhote, adulto, sênior, qualquer), além de registrar movimentações de
entrada e saída de estoque e controlar contas de clientes (fiado mensal):
compras e pagamentos com data, edição e exclusão de lançamentos, dia de
vencimento, limite de crédito e status em dia / atrasado (automático pelo
vencimento ou definido manualmente).

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
    routers/          # Rotas CRUD (marcas, produtos, movimentacoes, clientes)
    main.py           # App FastAPI (CORS, login e rotas)
frontend/
  src/
    pages/            # Estoque, Nova Ração, Marcas, Movimentacoes, Clientes, ClienteDetalhe
    api/client.js      # Cliente HTTP da API
```

## Deploy

| Parte | Onde |
|---|---|
| Frontend (React + Vite) | Vercel |
| Backend (FastAPI) | Render (ou Railway) |
| Banco de dados | PostgreSQL gerenciado (Neon, Supabase ou Render) |

O SQLite não serve em produção nesses serviços: o disco é temporário e o
`loja.db` seria apagado a cada deploy ou reinício.

### Variáveis de ambiente

Backend (veja `backend/.env.example`):

- `DATABASE_URL`: URL do PostgreSQL (`postgres://...` ou `postgresql://...`).
  Sem ela, o backend usa o SQLite local.
- `CORS_ORIGINS`: origens extras liberadas no CORS, separadas por vírgula
  (ex.: o domínio da Vercel). As origens locais (`:5173`) continuam liberadas.
- `ADMIN_PASSWORD`: senha de acesso ao sistema. Obrigatória quando
  `DATABASE_URL` está definida (o backend não sobe sem ela). Sem ela, em uso
  local, o login fica desligado. Trocar a senha encerra as sessões abertas.

Frontend (veja `frontend/.env.example`):

- `VITE_API_URL`: URL do backend, sem barra no final. É lida no build, então
  mudar o valor exige um novo deploy.

### Backend no Render

- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend na Vercel

- Root Directory: `frontend` (preset Vite)
- O `frontend/vercel.json` redireciona todas as rotas para o `index.html`,
  para o React Router funcionar ao recarregar a página.
