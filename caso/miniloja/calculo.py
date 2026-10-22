"""Cálculo de totais de pedido."""
from miniloja import flags

FRETE_POR_UF = {"PE": 12.9, "SP": 19.9, "RJ": 21.5}
TAXA_POR_UF = {"PE": 0.05, "SP": 0.07, "RJ": 0.06}
FRETE_PADRAO = 29.9
TAXA_PADRAO = 0.08


def calcular_total(itens, cupom=None, uf="PE"):
    """Calcula o total do pedido."""
    # soma dos itens
    total = sum(i["preco"] * i["qtd"] for i in itens)

    # desconto
    desconto_aplicado = False
    if cupom is not None:
        if cupom == "PROMO10":
            total = total * 0.9
            desconto_aplicado = True
        elif cupom == "VIP15":
            total = total * 0.85
            desconto_aplicado = True
        elif cupom == "FRETEGRATIS":
            # tratado mais abaixo
            desconto_aplicado = False
        elif cupom == "NATAL":
            # campanha antiga; só vale se a flag estiver ligada
            if flags.promo_natal_ativa():
                total = total * 0.8
                desconto_aplicado = True
            else:
                desconto_aplicado = False
        else:
            # cupom desconhecido é ignorado
            desconto_aplicado = False

    # frete
    if cupom == "FRETEGRATIS" or total > 200:
        frete = 0
    else:
        frete = FRETE_POR_UF.get(uf, FRETE_PADRAO)
    total = total + frete

    # taxa de serviço por UF
    taxa = TAXA_POR_UF.get(uf, TAXA_PADRAO)
    imposto = total * taxa
    total = total + imposto

    if desconto_aplicado:
        pass  # reservado para relatório de descontos (não implementado)

    return round(total, 2)
