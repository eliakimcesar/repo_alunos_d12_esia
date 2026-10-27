"""Controle de estoque em memória."""


class EstoqueInsuficiente(Exception):
    pass


class Estoque:
    def __init__(self, saldos=None):
        self.saldos = dict(saldos or {})
        self.reservas = {}

    def reservar(self, sku, qtd, pedido_id):
        """Reserva a quantidade do SKU no estoque."""
        disponivel = self.saldos.get(sku, 0)
        if disponivel < qtd:
            raise EstoqueInsuficiente(sku)
        self.saldos[sku] = disponivel - qtd
        self.reservas[(pedido_id, sku)] = qtd
        return True

    def liberar(self, sku, qtd, pedido_id):
        """Devolve ao estoque a quantidade reservada do SKU."""
        self.saldos[sku] = self.saldos.get(sku, 0) + qtd
        self.reservas.pop((pedido_id, sku), None)

    def saldo(self, sku):
        return self.saldos.get(sku, 0)
