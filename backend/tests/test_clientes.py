"""
Testes da rota de clientes.

Responsabilidades:
- Garantir que o resumo e a listagem de clientes calculam o mesmo saldo
  devedor, evitando duas fontes de verdade.
- Cobrir o bloqueio de exclusão de cliente com compras/pagamentos.
- Cobrir o estorno de compras e seu efeito no saldo e no estoque.
- Cobrir a situação da conta: pagamentos parciais e excedentes, vencimento
  (inclusive na virada do ano), status manual e limite de crédito.
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


# Datas bem no passado vencem sempre; datas bem no futuro nunca vencem. Assim os testes
# não dependem do dia em que rodam.
DATA_VENCIDA = "2020-01-15"
DATA_A_VENCER = "2099-06-15"
CAMPOS_SITUACAO = (
    "saldo_devedor",
    "valor_vencido",
    "proximo_vencimento",
    "status_automatico",
    "status",
    "acima_do_limite",
)


def _situacao_conta(client: TestClient, cliente_id: int) -> dict:
    """Lê a situação da conta pelo resumo e confere que a listagem calcula o mesmo.

    Args:
        client: Cliente de teste da API.
        cliente_id: Id do cliente consultado.

    Returns:
        Os campos de situação da conta, como devolvidos pelo resumo.
    """
    resumo = client.get(f"/clientes/{cliente_id}/resumo").json()
    listado = next(c for c in client.get("/clientes/").json() if c["id"] == cliente_id)
    situacao = {campo: resumo[campo] for campo in CAMPOS_SITUACAO}
    assert {campo: listado[campo] for campo in CAMPOS_SITUACAO} == situacao
    return situacao


def _comprar(client: TestClient, cliente_id: int, produto_id: int, quantidade: int, data: str) -> dict:
    """Registra uma compra com data escolhida e devolve a compra criada.

    Args:
        client: Cliente de teste da API.
        cliente_id: Id do cliente comprador.
        produto_id: Id do produto comprado.
        quantidade: Quantidade comprada.
        data: Data da compra (AAAA-MM-DD).

    Returns:
        A compra criada.
    """
    resposta = client.post(
        f"/clientes/{cliente_id}/compras",
        json={"produto_id": produto_id, "quantidade": quantidade, "data": data},
    )
    assert resposta.status_code == 201
    return resposta.json()


def _pagar(client: TestClient, cliente_id: int, valor: float) -> None:
    """Registra um pagamento do cliente.

    Args:
        client: Cliente de teste da API.
        cliente_id: Id do cliente pagador.
        valor: Valor pago.
    """
    assert client.post(f"/clientes/{cliente_id}/pagamentos", json={"valor": valor}).status_code == 201


def _atualizar_cliente(client: TestClient, cliente_id: int, **campos: object) -> None:
    """Grava campos da conta do cliente (vencimento, limite, status manual).

    Args:
        client: Cliente de teste da API.
        cliente_id: Id do cliente alterado.
        **campos: Campos a gravar.
    """
    assert client.put(f"/clientes/{cliente_id}", json=campos).status_code == 200


def test_pagamento_parcial_deixa_o_restante_vencido(client: TestClient) -> None:
    produto = _criar_produto(client, preco=50.0)
    cliente_id = _criar_cliente(client)
    _atualizar_cliente(client, cliente_id, dia_vencimento=10)
    _comprar(client, cliente_id, produto["id"], 2, DATA_VENCIDA)
    _pagar(client, cliente_id, 40.0)

    situacao = _situacao_conta(client, cliente_id)

    assert situacao["saldo_devedor"] == 60.0
    assert situacao["valor_vencido"] == 60.0
    assert situacao["proximo_vencimento"] == "2020-02-10"
    assert situacao["status"] == "atrasado"


def test_pagamento_quita_primeiro_a_compra_mais_antiga(client: TestClient) -> None:
    produto = _criar_produto(client, preco=50.0)
    cliente_id = _criar_cliente(client)
    _atualizar_cliente(client, cliente_id, dia_vencimento=10)
    # A compra nova é registrada antes, para a ordem ser pela data e não pelo id.
    _comprar(client, cliente_id, produto["id"], 1, DATA_A_VENCER)
    _comprar(client, cliente_id, produto["id"], 2, DATA_VENCIDA)
    _pagar(client, cliente_id, 100.0)

    situacao = _situacao_conta(client, cliente_id)

    assert situacao["saldo_devedor"] == 50.0
    assert situacao["valor_vencido"] == 0
    assert situacao["proximo_vencimento"] == "2099-07-10"
    assert situacao["status"] == "em_dia"


def test_pagamento_maior_que_as_compras_vira_credito(client: TestClient) -> None:
    produto = _criar_produto(client, preco=50.0)
    cliente_id = _criar_cliente(client)
    _atualizar_cliente(client, cliente_id, dia_vencimento=10)
    _comprar(client, cliente_id, produto["id"], 1, DATA_VENCIDA)
    _pagar(client, cliente_id, 80.0)

    situacao = _situacao_conta(client, cliente_id)

    assert situacao["saldo_devedor"] == -30.0
    assert situacao["valor_vencido"] == 0
    assert situacao["proximo_vencimento"] is None
    assert situacao["status"] == "em_dia"


def test_compra_estornada_nao_conta_no_vencimento(client: TestClient) -> None:
    produto = _criar_produto(client, preco=50.0)
    cliente_id = _criar_cliente(client)
    _atualizar_cliente(client, cliente_id, dia_vencimento=10)
    compra = _comprar(client, cliente_id, produto["id"], 2, DATA_VENCIDA)
    client.post(f"/clientes/{cliente_id}/compras/{compra['id']}/estornar")

    situacao = _situacao_conta(client, cliente_id)

    assert situacao["saldo_devedor"] == 0
    assert situacao["valor_vencido"] == 0
    assert situacao["proximo_vencimento"] is None
    assert situacao["status"] == "em_dia"


def test_compra_de_dezembro_vence_em_janeiro_do_ano_seguinte(client: TestClient) -> None:
    produto = _criar_produto(client, preco=50.0)
    a_vencer = _criar_cliente(client)
    _atualizar_cliente(client, a_vencer, dia_vencimento=5)
    _comprar(client, a_vencer, produto["id"], 1, "2099-12-20")
    vencida = _criar_cliente(client, nome="Beltrano")
    _atualizar_cliente(client, vencida, dia_vencimento=5)
    _comprar(client, vencida, produto["id"], 1, "2020-12-20")

    situacao_a_vencer = _situacao_conta(client, a_vencer)
    situacao_vencida = _situacao_conta(client, vencida)

    assert situacao_a_vencer["proximo_vencimento"] == "2100-01-05"
    assert situacao_a_vencer["status"] == "em_dia"
    assert situacao_vencida["proximo_vencimento"] == "2021-01-05"
    assert situacao_vencida["status"] == "atrasado"


def test_sem_dia_de_vencimento_a_conta_nunca_atrasa(client: TestClient) -> None:
    produto = _criar_produto(client, preco=50.0)
    cliente_id = _criar_cliente(client)
    _comprar(client, cliente_id, produto["id"], 1, DATA_VENCIDA)

    situacao = _situacao_conta(client, cliente_id)

    assert situacao["saldo_devedor"] == 50.0
    assert situacao["valor_vencido"] == 0
    assert situacao["proximo_vencimento"] is None
    assert situacao["status"] == "em_dia"


def test_status_manual_sobrepoe_o_automatico(client: TestClient) -> None:
    produto = _criar_produto(client, preco=50.0)
    perdoado = _criar_cliente(client)
    _atualizar_cliente(client, perdoado, dia_vencimento=10, status_manual="em_dia")
    _comprar(client, perdoado, produto["id"], 1, DATA_VENCIDA)
    marcado = _criar_cliente(client, nome="Beltrano")
    _atualizar_cliente(client, marcado, status_manual="atrasado")

    situacao_perdoado = _situacao_conta(client, perdoado)
    situacao_marcado = _situacao_conta(client, marcado)

    assert situacao_perdoado["status_automatico"] == "atrasado"
    assert situacao_perdoado["status"] == "em_dia"
    assert situacao_marcado["status_automatico"] == "em_dia"
    assert situacao_marcado["status"] == "atrasado"


def test_acima_do_limite_so_quando_o_saldo_passa_do_limite(client: TestClient) -> None:
    produto = _criar_produto(client, preco=50.0)
    cliente_id = _criar_cliente(client)
    _atualizar_cliente(client, cliente_id, limite_credito=100.0)
    sem_limite = _criar_cliente(client, nome="Beltrano")
    _comprar(client, sem_limite, produto["id"], 5, DATA_A_VENCER)

    _comprar(client, cliente_id, produto["id"], 2, DATA_A_VENCER)
    no_limite = _situacao_conta(client, cliente_id)
    _comprar(client, cliente_id, produto["id"], 1, DATA_A_VENCER)
    acima = _situacao_conta(client, cliente_id)

    assert no_limite["acima_do_limite"] is False
    assert acima["acima_do_limite"] is True
    assert _situacao_conta(client, sem_limite)["acima_do_limite"] is False
