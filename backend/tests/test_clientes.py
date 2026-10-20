"""
Testes da rota de clientes.

Responsabilidades:
- Garantir que o resumo e a listagem de clientes calculam o mesmo saldo
  devedor, evitando duas fontes de verdade.
- Cobrir o bloqueio de exclusão de cliente com compras/pagamentos.
- Cobrir o estorno de compras e seu efeito no saldo e no estoque.
"""

from fastapi.testclient import TestClient


def _criar_cliente(client: TestClient, nome: str = "Fulano") -> int:
    """Cria um cliente via API e retorna seu id.

    Args:
        client: Cliente de teste da API.
        nome: Nome do cliente a ser criado.

    Returns:
        Id do cliente criado.
    """
    resposta = client.post("/clientes/", json={"nome": nome})
    return resposta.json()["id"]


def _criar_produto(client: TestClient, **overrides: object) -> dict:
    """Cria uma marca e um produto via API e retorna o produto completo."""
    marca_id = client.post("/marcas/", json={"nome": "Golden"}).json()["id"]
    payload = {
        "nome": "Ração Teste",
        "marca_id": marca_id,
        "especie": "cachorro",
        "fase_vida": "adulto",
        "peso_kg": 10.0,
        "preco": 50.0,
        "quantidade_estoque": 10,
    }
    payload.update(overrides)
    return client.post("/produtos/", json=payload).json()


def test_excluir_cliente_com_pagamento_retorna_400(client: TestClient) -> None:
    cliente_id = _criar_cliente(client)
    client.post(f"/clientes/{cliente_id}/pagamentos", json={"valor": 10.0})

    resposta = client.delete(f"/clientes/{cliente_id}")

    assert resposta.status_code == 400
    assert "compras ou pagamentos" in resposta.json()["detail"].lower()


def test_resumo_e_listagem_calculam_o_mesmo_saldo_devedor(client: TestClient) -> None:
    produto = _criar_produto(client, quantidade_estoque=10, preco=50.0)
    cliente_id = _criar_cliente(client)
    client.post(f"/clientes/{cliente_id}/compras", json={"produto_id": produto["id"], "quantidade": 3})
    estornada = client.post(
        f"/clientes/{cliente_id}/compras", json={"produto_id": produto["id"], "quantidade": 1}
    ).json()
    client.post(f"/clientes/{cliente_id}/compras/{estornada['id']}/estornar")
    client.post(f"/clientes/{cliente_id}/pagamentos", json={"valor": 40.0})

    resumo = client.get(f"/clientes/{cliente_id}/resumo").json()
    listado = next(c for c in client.get("/clientes/").json() if c["id"] == cliente_id)

    assert resumo["saldo_devedor"] == 110.0
    assert listado["saldo_devedor"] == resumo["saldo_devedor"]


def test_editar_ou_excluir_compra_estornada_retorna_400(client: TestClient) -> None:
    produto = _criar_produto(client, quantidade_estoque=10, preco=50.0)
    cliente_id = _criar_cliente(client)
    compra = client.post(
        f"/clientes/{cliente_id}/compras", json={"produto_id": produto["id"], "quantidade": 3}
    ).json()
    client.post(f"/clientes/{cliente_id}/compras/{compra['id']}/estornar")

    editar = client.put(f"/clientes/{cliente_id}/compras/{compra['id']}", json={"quantidade": 1})
    excluir = client.delete(f"/clientes/{cliente_id}/compras/{compra['id']}")

    assert editar.status_code == 400
    assert excluir.status_code == 400
    # O estorno devolveu as 3 unidades uma única vez.
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_estoque"] == 10


def test_estornar_compra_devolve_estoque_e_zera_saldo(client: TestClient) -> None:
    produto = _criar_produto(client, quantidade_estoque=10, preco=50.0)
    cliente_id = _criar_cliente(client)
    compra = client.post(
        f"/clientes/{cliente_id}/compras", json={"produto_id": produto["id"], "quantidade": 3}
    ).json()

    resposta = client.post(f"/clientes/{cliente_id}/compras/{compra['id']}/estornar")

    assert resposta.status_code == 200
    assert resposta.json()["estornado_em"] is not None

    produto_final = client.get(f"/produtos/{produto['id']}").json()
    assert produto_final["quantidade_estoque"] == 10

    cliente_final = next(
        c for c in client.get("/clientes/").json() if c["id"] == cliente_id
    )
    assert cliente_final["saldo_devedor"] == 0


def test_estornar_compra_ja_estornada_retorna_400(client: TestClient) -> None:
    produto = _criar_produto(client)
    cliente_id = _criar_cliente(client)
    compra = client.post(
        f"/clientes/{cliente_id}/compras", json={"produto_id": produto["id"], "quantidade": 1}
    ).json()
    client.post(f"/clientes/{cliente_id}/compras/{compra['id']}/estornar")

    resposta = client.post(f"/clientes/{cliente_id}/compras/{compra['id']}/estornar")

    assert resposta.status_code == 400


def test_resumo_cliente_mantem_compra_estornada_visivel_mas_fora_do_total(
    client: TestClient,
) -> None:
    produto = _criar_produto(client, preco=50.0)
    cliente_id = _criar_cliente(client)
    compra = client.post(
        f"/clientes/{cliente_id}/compras", json={"produto_id": produto["id"], "quantidade": 2}
    ).json()
    client.post(f"/clientes/{cliente_id}/compras/{compra['id']}/estornar")

    resumo = client.get(f"/clientes/{cliente_id}/resumo").json()

    assert len(resumo["compras"]) == 1
    assert resumo["compras"][0]["estornado_em"] is not None
    assert resumo["total_compras"] == 0
    assert resumo["saldo_devedor"] == 0


def test_editar_quantidade_da_compra_acerta_estoque_e_gera_movimentacao(client: TestClient) -> None:
    produto = _criar_produto(client, quantidade_estoque=10, preco=50.0)
    cliente_id = _criar_cliente(client)
    compra = client.post(
        f"/clientes/{cliente_id}/compras", json={"produto_id": produto["id"], "quantidade": 3}
    ).json()

    aumentar = client.put(f"/clientes/{cliente_id}/compras/{compra['id']}", json={"quantidade": 5})
    assert aumentar.status_code == 200
    assert aumentar.json()["quantidade"] == 5
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_estoque"] == 5

    diminuir = client.put(f"/clientes/{cliente_id}/compras/{compra['id']}", json={"quantidade": 1})
    assert diminuir.status_code == 200
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_estoque"] == 9

    sem_estoque = client.put(f"/clientes/{cliente_id}/compras/{compra['id']}", json={"quantidade": 50})
    assert sem_estoque.status_code == 400
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_estoque"] == 9

    tipos = [m["tipo"] for m in client.get("/movimentacoes/").json()]
    assert sorted(tipos) == ["entrada", "saida", "saida"]


def _alterar_quantidade_depois_da_leitura(monkeypatch, funcao: str, nova_quantidade: int) -> None:
    """Simula outra ação mudando a quantidade da compra entre a leitura e a escrita da rota."""
    from sqlalchemy import update

    from app import models
    from app.routers import clientes

    original = getattr(clientes, funcao)

    def lida_e_alterada(db, cliente_id, compra_id):
        compra = original(db, cliente_id, compra_id)
        # Sem sincronizar a sessão: o objeto lido continua com a quantidade antiga, como numa outra conexão.
        db.execute(
            update(models.Compra)
            .where(models.Compra.id == compra_id)
            .values(quantidade=nova_quantidade)
            .execution_options(synchronize_session=False)
        )
        return compra

    monkeypatch.setattr(clientes, funcao, lida_e_alterada)


def test_estornar_compra_alterada_por_outra_acao_nao_devolve_quantidade_antiga(
    client: TestClient, monkeypatch
) -> None:
    produto = _criar_produto(client, quantidade_estoque=10, preco=50.0)
    cliente_id = _criar_cliente(client)
    compra = client.post(
        f"/clientes/{cliente_id}/compras", json={"produto_id": produto["id"], "quantidade": 3}
    ).json()
    _alterar_quantidade_depois_da_leitura(monkeypatch, "_obter_compra", 5)

    resposta = client.post(f"/clientes/{cliente_id}/compras/{compra['id']}/estornar")

    assert resposta.status_code == 409
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_estoque"] == 7


def test_excluir_compra_alterada_por_outra_acao_nao_devolve_quantidade_antiga(
    client: TestClient, monkeypatch
) -> None:
    produto = _criar_produto(client, quantidade_estoque=10, preco=50.0)
    cliente_id = _criar_cliente(client)
    compra = client.post(
        f"/clientes/{cliente_id}/compras", json={"produto_id": produto["id"], "quantidade": 3}
    ).json()
    _alterar_quantidade_depois_da_leitura(monkeypatch, "_obter_compra_ativa", 5)

    resposta = client.delete(f"/clientes/{cliente_id}/compras/{compra['id']}")

    assert resposta.status_code == 409
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade_estoque"] == 7
