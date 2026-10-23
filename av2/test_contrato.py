"""Testes de calcular_total derivados do contrato R1 (caso/regras.md), não do código.

Cada esperado foi calculado à mão a partir da regra citada; a conta está no comentário do teste.
Uso, a partir da raiz do pacote:
  python -B av2/test_contrato.py                   # contra caso/
  python -B av2/test_contrato.py --codigo <pasta>  # contra uma cópia (ex.: sabotada)
"""
import argparse
import os
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def item(preco, qtd=1):
    return {"preco": preco, "qtd": qtd}


class TestContratoR1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from miniloja.calculo import calcular_total

        cls.total = staticmethod(calcular_total)

    def setUp(self):
        self._natal = os.environ.pop("MINILOJA_PROMO_NATAL", None)

    def tearDown(self):
        os.environ.pop("MINILOJA_PROMO_NATAL", None)
        if self._natal is not None:
            os.environ["MINILOJA_PROMO_NATAL"] = self._natal

    # R1.1 subtotal
    def test_subtotal_soma_preco_vezes_quantidade(self):
        # 9,90×7 + 0,10×3 + 33,33×2 = 136,26; +12,90 (PE) = 149,16; ×1,05 = 156,618 -> 156,62
        self.assertEqual(self.total([item(9.9, 7), item(0.1, 3), item(33.33, 2)], None, "PE"), 156.62)

    # R1.3 frete por UF (sem desconto, abaixo de 200) e R1.4 taxa por UF
    def test_frete_e_taxa_pe(self):
        # 50×2 = 100; +12,90 = 112,90; ×1,05 = 118,545 -> 118,55
        self.assertEqual(self.total([item(50.0, 2)], None, "PE"), 118.55)

    def test_frete_e_taxa_sp(self):
        # 40 + 19,90 = 59,90; ×1,07 = 64,093 -> 64,09
        self.assertEqual(self.total([item(40.0)], None, "SP"), 64.09)

    def test_frete_e_taxa_rj(self):
        # 40 + 21,50 = 61,50; ×1,06 = 65,19
        self.assertEqual(self.total([item(40.0)], None, "RJ"), 65.19)

    def test_frete_e_taxa_demais_ufs(self):
        # 40 + 29,90 = 69,90; ×1,08 = 75,492 -> 75,49
        self.assertEqual(self.total([item(40.0)], None, "XX"), 75.49)

    # R1.2 cupons
    def test_promo10_desconta_dez_por_cento(self):
        # 80 × 0,90 = 72; +19,90 (SP) = 91,90; ×1,07 = 98,333 -> 98,33
        self.assertEqual(self.total([item(80.0)], "PROMO10", "SP"), 98.33)

    def test_vip15_desconta_quinze_por_cento(self):
        # 100 × 0,85 = 85; +21,50 (RJ) = 106,50; ×1,06 = 112,89
        self.assertEqual(self.total([item(100.0)], "VIP15", "RJ"), 112.89)

    def test_natal_com_campanha_ativa_desconta_vinte_por_cento(self):
        os.environ["MINILOJA_PROMO_NATAL"] = "1"
        # 100 × 0,80 = 80; +21,50 (RJ) = 101,50; ×1,06 = 107,59
        self.assertEqual(self.total([item(100.0)], "NATAL", "RJ"), 107.59)

    def test_natal_sem_campanha_nao_desconta(self):
        # 100 + 21,50 (RJ) = 121,50; ×1,06 = 128,79
        self.assertEqual(self.total([item(100.0)], "NATAL", "RJ"), 128.79)

    def test_fretegratis_zera_frete_sem_alterar_valor(self):
        # 40 + 0 = 40; ×1,06 (RJ) = 42,40
        self.assertEqual(self.total([item(40.0)], "FRETEGRATIS", "RJ"), 42.4)

    def test_cupom_desconhecido_e_ignorado(self):
        # igual a sem cupom: 30 + 21,50 (RJ) = 51,50; ×1,06 = 54,59
        self.assertEqual(self.total([item(30.0)], "CUPOMFALSO", "RJ"), 54.59)

    # R1.3 fronteira do frete grátis (subtotal com desconto >= 200)
    def test_fronteira_199_99_paga_frete(self):
        # 199,99 + 12,90 = 212,89; ×1,05 = 223,5345 -> 223,53
        self.assertEqual(self.total([item(199.99)], None, "PE"), 223.53)

    def test_fronteira_exatamente_200_tem_frete_gratis(self):
        # 200 >= 200 -> frete 0; 200 × 1,05 = 210,00
        self.assertEqual(self.total([item(200.0)], None, "PE"), 210.0)

    def test_fronteira_200_01_tem_frete_gratis(self):
        # 200,01 × 1,05 = 210,0105 -> 210,01
        self.assertEqual(self.total([item(200.01)], None, "PE"), 210.01)

    # R1.6 ordem: desconto antes do frete
    def test_desconto_que_leva_abaixo_de_200_volta_a_pagar_frete(self):
        # 220 × 0,90 = 198 < 200 -> frete 21,50 (RJ) = 219,50; ×1,06 = 232,67
        self.assertEqual(self.total([item(220.0)], "PROMO10", "RJ"), 232.67)

    def test_desconto_que_resulta_exatamente_200_tem_frete_gratis(self):
        os.environ["MINILOJA_PROMO_NATAL"] = "1"
        # 250 × 0,80 = 200 >= 200 -> frete 0; ×1,05 (PE) = 210,00
        self.assertEqual(self.total([item(250.0)], "NATAL", "PE"), 210.0)

    # R1.5 arredondamento meio para cima
    def test_arredondamento_meio_para_cima(self):
        # 1,20 + 12,90 = 14,10; ×1,05 = 14,805 -> 14,81 (meio para cima)
        self.assertEqual(self.total([item(1.2)], None, "PE"), 14.81)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--codigo", default="caso")
    args, resto = p.parse_known_args()
    sys.path.insert(0, str(RAIZ / args.codigo))
    unittest.main(argv=[sys.argv[0]] + resto, verbosity=2)
