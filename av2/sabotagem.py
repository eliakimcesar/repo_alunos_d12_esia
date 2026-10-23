"""Sabotagem do calcular_total corrigido (AV2): prova de que as suítes falhariam.

testes/mutacao_manual.py não serve mais: procura trechos do código antigo e muta caso/ no lugar.
Este script copia caso/miniloja para uma pasta temporária, aplica UMA sabotagem por vez na cópia
(caso/ nunca é alterado) e roda cada suíte contra ela com --codigo.

Uso, a partir da raiz do pacote:  python -B av2/sabotagem.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "caso" / "miniloja"

SUITES = {
    "contrato": [sys.executable, "-B", "av2/test_contrato.py"],
    "existente": [sys.executable, "-B", "testes/test_miniloja.py", "--existentes"],
}

SABOTAGENS = [
    # (trecho no código corrigido, trecho sabotado, descrição, regra)
    ("total >= LIMITE_FRETE_GRATIS", "total > LIMITE_FRETE_GRATIS", "fronteira volta a > 200", "R1.3"),
    ('LIMITE_FRETE_GRATIS = Decimal("200")', 'LIMITE_FRETE_GRATIS = Decimal("300")', "limite 200 vira 300", "R1.3"),
    ('total * Decimal("0.9")', 'total * Decimal("0.91")', "PROMO10: 10% -> 9%", "R1.2"),
    ('total * Decimal("0.85")', 'total * Decimal("0.86")', "VIP15: 15% -> 14%", "R1.2"),
    ('total * Decimal("0.8")', 'total * Decimal("0.79")', "NATAL: 20% -> 21%", "R1.2"),
    ("if flags.promo_natal_ativa():", "if True:", "NATAL vale sem campanha", "R1.2"),
    ('elif cupom == "VIP15":', 'elif cupom == "VIP16":', "VIP15 deixa de existir", "R1.2"),
    ('if cupom == "FRETEGRATIS" or', 'if cupom == "XFRETEGRATIS" or', "FRETEGRATIS deixa de zerar o frete", "R1.2"),
    ("if cupom is not None:", "if cupom is None:", "nenhum cupom é aplicado", "R1.2"),
    ('"PE": Decimal("12.90")', '"PE": Decimal("13.90")', "frete PE", "R1.3"),
    ('"SP": Decimal("19.90")', '"SP": Decimal("20.90")', "frete SP", "R1.3"),
    ('"RJ": Decimal("21.50")', '"RJ": Decimal("22.50")', "frete RJ", "R1.3"),
    ('FRETE_PADRAO = Decimal("29.90")', 'FRETE_PADRAO = Decimal("30.90")', "frete demais UFs", "R1.3"),
    ("frete = Decimal(0)", "frete = Decimal(1)", "frete grátis cobra R$ 1", "R1.3"),
    ('"PE": Decimal("0.05")', '"PE": Decimal("0.06")', "taxa PE", "R1.4"),
    ('"SP": Decimal("0.07")', '"SP": Decimal("0.08")', "taxa SP", "R1.4"),
    ('"RJ": Decimal("0.06")', '"RJ": Decimal("0.07")', "taxa RJ", "R1.4"),
    ('TAXA_PADRAO = Decimal("0.08")', 'TAXA_PADRAO = Decimal("0.09")', "taxa demais UFs", "R1.4"),
    ("imposto = total * taxa", "imposto = (total - frete) * taxa", "taxa só sobre o subtotal, sem o frete", "R1.4"),
    ('* i["qtd"]', '+ i["qtd"]', "soma dos itens: * vira +", "R1.1"),
    ('Decimal(str(i["preco"]))', 'Decimal(i["preco"])', "preço convertido do float binário", "R1.5"),
    ("rounding=ROUND_HALF_UP", "rounding=ROUND_HALF_EVEN", "arredondamento bancário", "R1.5"),
    ('CENTAVO = Decimal("0.01")', 'CENTAVO = Decimal("0.1")', "arredonda em 1 casa", "R1.5"),
    ("if desconto_aplicado:", "if not desconto_aplicado:", "variável sem efeito (equivalente)", "-"),
]


def falha(suite, codigo):
    r = subprocess.run(SUITES[suite] + ["--codigo", str(codigo)], cwd=RAIZ, capture_output=True, timeout=120)
    return r.returncode != 0


def main():
    with tempfile.TemporaryDirectory() as tmp:
        # a suíte existente é descoberta em <codigo>/testes_existentes, então ela vai junto na cópia
        for pasta in ("miniloja", "testes_existentes"):
            shutil.copytree(ORIGEM.parent / pasta, Path(tmp) / pasta, ignore=shutil.ignore_patterns("__pycache__"))
        alvo = Path(tmp) / "miniloja" / "calculo.py"
        original = alvo.read_text(encoding="utf-8")
        base = {s: falha(s, tmp) for s in SUITES}
        if any(base.values()):
            sys.exit(f"Alguma suíte já falha sem sabotagem: {base}")

        mortos = {s: 0 for s in SUITES}
        print(f"{'regra':5} | {'sabotagem':40} | contrato  | existente")
        for velho, novo, desc, regra in SABOTAGENS:
            assert original.count(velho) == 1, f"trecho ausente ou repetido: {velho!r}"
            alvo.write_text(original.replace(velho, novo), encoding="utf-8")
            try:
                res = {s: falha(s, tmp) for s in SUITES}
            finally:
                alvo.write_text(original, encoding="utf-8")
            for s, morreu in res.items():
                mortos[s] += morreu
            cel = {s: "morto" if res[s] else "SOBREVIVE" for s in SUITES}
            print(f"{regra:5} | {desc:40} | {cel['contrato']:9} | {cel['existente']}")
        n = len(SABOTAGENS)
        print(f"Sabotagens: {n} | contrato: {mortos['contrato']} mortos ({100 * mortos['contrato'] / n:.0f}%)"
              f" | existente: {mortos['existente']} mortos ({100 * mortos['existente'] / n:.0f}%)")


if __name__ == "__main__":
    main()
