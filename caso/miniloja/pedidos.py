"""Serviço de pedidos."""
from miniloja.calculo import calcular_total
from miniloja.estoque import EstoqueInsuficiente


def moeda(v):
    # formata valor em reais
    return "R$ " + ("%.2f" % v).replace(".", ",")


class PedidoService:
    def __init__(self, repo, estoque, gateway):
        self.repo = repo
        self.estoque = estoque
        self.gateway = gateway

    def criar(self, usuario_id, itens, cupom=None, uf="PE", token="tok_ok"):
        """Cria um pedido."""
        if not itens:
            raise ValueError("pedido sem itens")
        total = calcular_total(itens, cupom, uf)
        pedido_id = f"tmp-{usuario_id}"
        reservados = []
        try:
            for i in itens:
                self.estoque.reservar(i["sku"], i["qtd"], pedido_id=pedido_id)
                reservados.append(i)
        except EstoqueInsuficiente:
            # R2.2: nenhuma reserva pode permanecer
            for i in reservados:
                self.estoque.liberar(i["sku"], i["qtd"], pedido_id=pedido_id)
            raise
        cobranca = self.gateway.cobrar(total, token)
        if cobranca["status"] != "aprovado":
            return {"status": "pagamento_recusado", "total": total}
        pedido = self.repo.salvar(
            {
                "usuario_id": usuario_id,
                "itens": itens,
                "total": total,
                "total_fmt": moeda(total),
                "status": "pago",
            }
        )
        return pedido
