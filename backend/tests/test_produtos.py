"""
Testes da rota de produtos.

Responsabilidades:
- Cobrir a validação de marca_id em atualizar_produto (PUT /produtos/{id}).
- Cobrir a validação de valores positivos em preço, peso e estoque.
"""
from fastapi.testclient import TestClient


def _criar_marca(client: TestClient, nome: str = "Golden") -> int:
    """Cria uma marca via API e retorna seu id.

    Args:
        client: Cliente de teste da API.
        nome: Nome da marca a ser criada.

    Returns:
        Id da marca criada.
    """
    resposta = client.post("/marcas/", json={"nome": nome})
    return resposta.json()["id"]


def _payload_produto(marca_id: int, **overrides: object) -> dict:
    """Monta um payload válido de produto, com overrides pontuais.

    Args:
        marca_id: Id da marca à qual o produto pertence.
        **overrides: Campos a sobrescrever no payload padrão.

    Returns:
        Payload pronto para POST/PUT em /produtos/.
    """
    payload = {
        "nome": "Ração Teste",
        "marca_id": marca_id,
        "especie": "cachorro",
        "fase_vida": "adulto",
        "peso_kg": 10.0,
        "preco": 99.9,
        "quantidade_estoque": 5,
    }
    payload.update(overrides)
    return payload


def _criar_produto(client: TestClient, marca_id: int, **overrides: object) -> int:
    """Cria um produto via API e retorna seu id.

    Args:
        client: Cliente de teste da API.
        marca_id: Id da marca à qual o produto pertence.
        **overrides: Campos a sobrescrever no payload padrão.

    Returns:
        Id do produto criado.
    """
    resposta = client.post("/produtos/", json=_payload_produto(marca_id, **overrides))
    return resposta.json()["id"]


def test_atualizar_produto_com_marca_id_inexistente_retorna_400(client: TestClient) -> None:
    marca_id = _criar_marca(client)
    produto_id = _criar_produto(client, marca_id)

    resposta = client.put(f"/produtos/{produto_id}", json={"marca_id": 9999})

    assert resposta.status_code == 400
    assert "marca" in resposta.json()["detail"].lower()


def test_atualizar_produto_com_marca_id_valido_atualiza(client: TestClient) -> None:
    marca_id = _criar_marca(client, "Golden")
    outra_marca_id = _criar_marca(client, "Premier Pet")
    produto_id = _criar_produto(client, marca_id)

    resposta = client.put(f"/produtos/{produto_id}", json={"marca_id": outra_marca_id})

    assert resposta.status_code == 200
    assert resposta.json()["marca_id"] == outra_marca_id


def test_criar_produto_com_preco_negativo_retorna_422(client: TestClient) -> None:
    marca_id = _criar_marca(client)

    resposta = client.post("/produtos/", json=_payload_produto(marca_id, preco=-50))

    assert resposta.status_code == 422


def test_criar_produto_com_peso_zero_retorna_422(client: TestClient) -> None:
    marca_id = _criar_marca(client)

    resposta = client.post("/produtos/", json=_payload_produto(marca_id, peso_kg=0))

    assert resposta.status_code == 422


def test_criar_produto_com_estoque_negativo_retorna_422(client: TestClient) -> None:
    marca_id = _criar_marca(client)

    resposta = client.post("/produtos/", json=_payload_produto(marca_id, quantidade_estoque=-10))

    assert resposta.status_code == 422


def test_atualizar_produto_com_preco_negativo_retorna_422(client: TestClient) -> None:
    marca_id = _criar_marca(client)
    produto_id = _criar_produto(client, marca_id)

    resposta = client.put(f"/produtos/{produto_id}", json={"preco": -1})

    assert resposta.status_code == 422
