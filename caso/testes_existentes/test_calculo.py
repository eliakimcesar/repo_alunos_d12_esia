import os
import unittest

from miniloja.calculo import calcular_total


class TestCalculo(unittest.TestCase):
    def test_total_simples_pe(self):
        itens = [{"preco": 50.0, "qtd": 2}]
        self.assertEqual(calcular_total(itens, None, "PE"), 118.55)

    def test_cupom_promo10_sp(self):
        self.assertEqual(calcular_total([{"preco": 80.0, "qtd": 1}], "PROMO10", "SP"), 98.33)

    def test_frete_gratis_rj(self):
        self.assertEqual(calcular_total([{"preco": 40.0, "qtd": 1}], "FRETEGRATIS", "RJ"), 42.4)

    def test_pedido_acima_de_200_nao_paga_frete(self):
        self.assertEqual(calcular_total([{"preco": 250.0, "qtd": 1}], None, "PE"), 262.5)

    def test_uf_desconhecida_usa_frete_e_taxa_padrao(self):
        self.assertEqual(calcular_total([{"preco": 60.0, "qtd": 1}], None, "XX"), 97.09)

    def test_cupom_desconhecido_e_ignorado(self):
        itens = [{"preco": 30.0, "qtd": 1}]
        self.assertEqual(calcular_total(itens, "CUPOMFALSO", "PE"), calcular_total(itens, None, "PE"))

    def test_retorna_numero(self):
        resultado = calcular_total([{"preco": 10.0, "qtd": 1}], None, "PE")
        self.assertIsInstance(resultado, float)

    def test_cupom_natal_com_flag(self):
        os.environ["MINILOJA_PROMO_NATAL"] = "1"
        try:
            resultado = calcular_total([{"preco": 100.0, "qtd": 1}], "NATAL", "PE")
            self.assertIsNotNone(resultado)
        finally:
            os.environ.pop("MINILOJA_PROMO_NATAL", None)

    def test_cenarios_gravados(self):
        cenarios = {
            "simples": calcular_total([{"preco": 19.99, "qtd": 3}], None, "PE"),
            "vip": calcular_total([{"preco": 100.0, "qtd": 3}], "VIP15", "SP"),
            "limite_200": calcular_total([{"preco": 100.0, "qtd": 2}], None, "PE"),
            "vazio": calcular_total([], None, "PE"),
        }
        self.assertEqual(
            cenarios,
            # limite_200 e vazio pelo contrato (AV2, ADR-002): R1.3 200 >= 200 -> frete 0, 200 × 1,05 = 210,00;
            # R1.5 12,90 × 1,05 = 13,545 -> 13,55 (meio para cima). Antes gravavam 223.55 e 13.54 (bugs).
            {"simples": 76.51, "vip": 272.85, "limite_200": 210.0, "vazio": 13.55},
        )
