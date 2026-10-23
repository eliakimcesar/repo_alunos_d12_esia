"""Cálculo de totais de pedido."""
from decimal import ROUND_HALF_UP, Decimal

from miniloja import flags

# Decimal evita o erro de representação do float: R1.5 exige meio para cima exato.
FRETE_POR_UF = {"PE": Decimal("12.90"), "SP": Decimal("19.90"), "RJ": Decimal("21.50")}
TAXA_POR_UF = {"PE": Decimal("0.05"), "SP": Decimal("0.07"), "RJ": Decimal("0.06")}
FRETE_PADRAO = Decimal("29.90")
TAXA_PADRAO = Decimal("0.08")
LIMITE_FRETE_GRATIS = Decimal("200")
CENTAVO = Decimal("0.01")


def calcular_total(itens, cupom=None, uf="PE"):
    """Calcula o total do pedido."""
    # soma dos itens
    total = sum((Decimal(str(i["preco"])) * i["qtd"] for i in itens), Decimal(0))

    # desconto
    desconto_aplicado = False
    if cupom is not None:
        if cupom == "PROMO10":
            total = total * Decimal("0.9")
            desconto_aplicado = True
        elif cupom == "VIP15":
            total = total * Decimal("0.85")
            desconto_aplicado = True
        elif cupom == "FRETEGRATIS":
            # tratado mais abaixo
            desconto_aplicado = False
        elif cupom == "NATAL":
            # campanha antiga; só vale se a flag estiver ligada
            if flags.promo_natal_ativa():
                total = total * Decimal("0.8")
                desconto_aplicado = True
            else:
                desconto_aplicado = False
        else:
            # cupom desconhecido é ignorado
            desconto_aplicado = False

    # frete
    if cupom == "FRETEGRATIS" or total >= LIMITE_FRETE_GRATIS:
        frete = Decimal(0)
    else:
        frete = FRETE_POR_UF.get(uf, FRETE_PADRAO)
    total = total + frete

    # taxa de serviço por UF
    taxa = TAXA_POR_UF.get(uf, TAXA_PADRAO)
    imposto = total * taxa
    total = total + imposto

    if desconto_aplicado:
        pass  # reservado para relatório de descontos (não implementado)

    return float(total.quantize(CENTAVO, rounding=ROUND_HALF_UP))
