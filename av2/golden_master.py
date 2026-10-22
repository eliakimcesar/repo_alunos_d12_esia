"""Golden master de calcular_total (AV2): grava o comportamento atual e compara com igualdade exata.

Uso, a partir da raiz do pacote:
  python -B av2/golden_master.py gravar [--codigo caso]    # antes da refatoração
  python -B av2/golden_master.py comparar [--codigo caso]  # depois; código de saída 1 se houver diferença

Preserva o comportamento ATUAL, inclusive divergências do contrato (R1.3 "> 200", R1.5 round de float).
"""
import argparse
import itertools
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO = Path(__file__).resolve().parent / "golden_master.json"

CARRINHOS = {
    "vazio": [],
    "um_centavo": [{"preco": 0.01, "qtd": 1}],
    "arredonda_1_20": [{"preco": 1.2, "qtd": 1}],
    "simples_50x2": [{"preco": 50.0, "qtd": 2}],
    "c3_19_99x3": [{"preco": 19.99, "qtd": 3}],
    "c1_camisa_bola": [{"preco": 80.0, "qtd": 1}, {"preco": 50.0, "qtd": 1}],
    "abaixo_200": [{"preco": 199.99, "qtd": 1}],
    "exato_200": [{"preco": 100.0, "qtd": 2}],
    "acima_200": [{"preco": 200.01, "qtd": 1}],
    "promo10_cruza_200": [{"preco": 222.23, "qtd": 1}],
    "promo10_exato_200": [{"preco": 222.22, "qtd": 1}],
    "vip15_perto_200": [{"preco": 235.3, "qtd": 1}],
    "natal_exato_200": [{"preco": 250.0, "qtd": 1}],
    "varios_itens": [{"preco": 9.9, "qtd": 7}, {"preco": 0.1, "qtd": 3}, {"preco": 33.33, "qtd": 2}],
    "grande": [{"preco": 1234.56, "qtd": 4}],
}
CUPONS = [None, "PROMO10", "VIP15", "FRETEGRATIS", "NATAL", "CUPOMFALSO", "promo10"]
UFS = ["PE", "SP", "RJ", "XX", "pe"]
FLAG_NATAL = ["0", "1"]


def chave(carrinho, cupom, uf, flag):
    return f"{carrinho}|{cupom}|{uf}|natal={flag}"


def executar(codigo):
    sys.path.insert(0, str(RAIZ / codigo))
    from miniloja.calculo import calcular_total

    saidas = {}
    anterior = os.environ.get("MINILOJA_PROMO_NATAL")
    try:
        for flag, (nome, itens), cupom, uf in itertools.product(FLAG_NATAL, CARRINHOS.items(), CUPONS, UFS):
            os.environ["MINILOJA_PROMO_NATAL"] = flag
            saidas[chave(nome, cupom, uf, flag)] = repr(calcular_total([dict(i) for i in itens], cupom, uf))
    finally:
        if anterior is None:
            os.environ.pop("MINILOJA_PROMO_NATAL", None)
        else:
            os.environ["MINILOJA_PROMO_NATAL"] = anterior
    return saidas


def main():
    p = argparse.ArgumentParser()
    p.add_argument("modo", choices=["gravar", "comparar"])
    p.add_argument("--codigo", default="caso")
    args = p.parse_args()
    atuais = executar(args.codigo)

    if args.modo == "gravar":
        ARQUIVO.write_text(json.dumps(atuais, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"Gravadas {len(atuais)} entradas em {ARQUIVO.name}")
        return 0

    gravadas = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    diferencas = [(k, gravadas.get(k), atuais.get(k)) for k in sorted(set(gravadas) | set(atuais))
                  if gravadas.get(k) != atuais.get(k)]
    print(f"Entradas: {len(gravadas)} | diferenças: {len(diferencas)}")
    for k, antes, depois in diferencas:
        print(f"  DIFERE  {k}: gravado={antes} atual={depois}")
    return 1 if diferencas else 0


if __name__ == "__main__":
    sys.exit(main())
