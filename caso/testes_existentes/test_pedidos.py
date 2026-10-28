import unittest
from unittest.mock import MagicMock

from miniloja.estoque import Estoque, EstoqueInsuficiente
from miniloja.pagamentos import GatewayFake
from miniloja.pedidos import PedidoService
from miniloja.repositorio import RepositorioPedidos


class TestPedidos(unittest.TestCase):
    def test_criar_pedido(self):
        repo = MagicMock()
        repo.salvar.return_value = {"id": 1}
        svc = PedidoService(repo, MagicMock(), MagicMock())
        svc.gateway.cobrar.return_value = {"status": "aprovado", "id": "x"}
        r = svc.criar(1, [{"sku": "BOLA-01", "preco": 10.0, "qtd": 1}])
        self.assertTrue(repo.salvar.called)
        self.assertEqual(r, {"id": 1})

    def test_fluxo_chama_colaboradores(self):
        estoque, gateway, repo = MagicMock(), MagicMock(), MagicMock()
        gateway.cobrar.return_value = {"status": "aprovado", "id": "x"}
        repo.salvar.return_value = {"id": 7}
        PedidoService(repo, estoque, gateway).criar(2, [{"sku": "CAMISA-M", "preco": 50.0, "qtd": 2}])
        self.assertTrue(estoque.reservar.called)
        self.assertTrue(gateway.cobrar.called)
        self.assertTrue(repo.salvar.called)

    def test_pedido_sem_itens_e_rejeitado(self):
        svc = PedidoService(RepositorioPedidos(), Estoque(), GatewayFake())
        with self.assertRaises(ValueError):
            svc.criar(1, [])

    def test_pagamento_recusado_nao_salva_pedido(self):
        repo = RepositorioPedidos()
        svc = PedidoService(repo, Estoque({"BOLA-01": 5}), GatewayFake())
        r = svc.criar(1, [{"sku": "BOLA-01", "preco": 10.0, "qtd": 1}], token="recusado")
        self.assertEqual(r["status"], "pagamento_recusado")
        self.assertEqual(repo.todos(), [])

    def test_item_sem_estoque_nao_deixa_reserva(self):
        # R2.2: se algum item não tiver estoque, nenhuma reserva pode permanecer
        repo, estoque, gateway = RepositorioPedidos(), Estoque({"BOLA-01": 5, "CHUTEIRA-42": 0}), GatewayFake()
        itens = [
            {"sku": "BOLA-01", "preco": 10.0, "qtd": 2},
            {"sku": "CHUTEIRA-42", "preco": 50.0, "qtd": 1},
        ]
        with self.assertRaises(EstoqueInsuficiente):  # R2.2: pedido recusado
            PedidoService(repo, estoque, gateway).criar(1, itens)
        # R2.2: nenhuma reserva permanece (saldo devolvido e nenhuma entrada em reservas)
        self.assertEqual(estoque.saldo("BOLA-01"), 5)
        self.assertEqual(estoque.reservas, {})
        # derivado, não escrito no contrato: a recusa ocorre antes de cobrar e de salvar
        self.assertEqual(gateway.cobrancas, [])
        self.assertEqual(repo.todos(), [])

    def test_falha_no_ultimo_item_desfaz_todas_as_reservas(self):
        # R2.2 com várias reservas feitas antes da falha
        estoque = Estoque({"BOLA-01": 5, "CAMISA-M": 4, "CHUTEIRA-42": 0})
        itens = [
            {"sku": "BOLA-01", "preco": 10.0, "qtd": 2},
            {"sku": "CAMISA-M", "preco": 50.0, "qtd": 3},
            {"sku": "CHUTEIRA-42", "preco": 50.0, "qtd": 1},
        ]
        with self.assertRaises(EstoqueInsuficiente):
            PedidoService(RepositorioPedidos(), estoque, GatewayFake()).criar(1, itens)
        self.assertEqual(estoque.saldo("BOLA-01"), 5)
        self.assertEqual(estoque.saldo("CAMISA-M"), 4)
        self.assertEqual(estoque.reservas, {})

    def test_handler_responde_409_sem_deixar_reserva(self):
        # R2.2 na camada HTTP: 409 e saldo intacto; usuário próprio para não colidir com outros testes
        from miniloja import handlers

        antes = handlers._estoque.saldo("BOLA-01")
        status, corpo = handlers.post_pedidos(9001, {"itens": [
            {"sku": "BOLA-01", "preco": 10.0, "qtd": 2},
            {"sku": "CHUTEIRA-42", "preco": 50.0, "qtd": 10**6},
        ]})
        self.assertEqual(status, 409)
        self.assertEqual(corpo["sku"], "CHUTEIRA-42")
        self.assertEqual(handlers._estoque.saldo("BOLA-01"), antes)
        self.assertNotIn(("tmp-9001", "BOLA-01"), handlers._estoque.reservas)
