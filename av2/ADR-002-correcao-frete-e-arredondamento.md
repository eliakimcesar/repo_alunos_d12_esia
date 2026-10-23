# ADR-002 — Corrigir `calcular_total` para o contrato: frete grátis em `>= 200` (R1.3) e arredondamento meio para cima (R1.5)

**Status:** aceito · **Data:** 22/10/2026 · **Autor:** Eliakim · **Escopo:** AV2, Caminho B (MiniLoja) · **Commits:** `cf639eb` (testes vermelhos), `70825da` (correção)

## Contexto
A refatoração (`8b7c937`) preservou o comportamento por invariante, inclusive duas divergências do contrato `caso/regras.md`. Os testes de `av2/test_contrato.py`, com esperado calculado à mão a partir de R1, falharam 3 de 17 no código preservado:

| Teste | Regra | Esperado (contrato) | Código antigo | Causa |
| --- | --- | --- | --- | --- |
| `test_fronteira_exatamente_200_tem_frete_gratis` (200, PE) | R1.3 | 210.0 | 223.55 | `total > 200` |
| `test_desconto_que_resulta_exatamente_200_tem_frete_gratis` (250 com NATAL, PE) | R1.3 + R1.6 | 210.0 | 223.55 | `total > 200` |
| `test_arredondamento_meio_para_cima` (1,20, PE: 14,805) | R1.5 | 14.81 | 14.8 | `round()` de float: 14,805 é armazenado como 14,8049999… |

A suíte existente do caso não acusava nada: `test_cenarios_gravados` gravava a saída do código (`limite_200: 223.55`, `vazio: 13.54`), congelando os dois bugs como se fossem regra.

## Decisão
O contrato vale mais que o código atual (`CLAUDE.md`), então corrigi o código, em commit separado da refatoração e depois do commit dos testes vermelhos:
1. Frete grátis quando o subtotal **com desconto** é `>= LIMITE_FRETE_GRATIS` (`Decimal("200")`).
2. Toda a aritmética de `calcular_total` em `Decimal` (preço convertido por `Decimal(str(preco))`, constantes como `Decimal` em texto) e arredondamento final `quantize(Decimal("0.01"), ROUND_HALF_UP)`. O retorno continua `float`, para não mudar a interface usada por `pedidos.py` e pelos testes.
3. Atualizei os dois valores de `test_cenarios_gravados` para o que o contrato manda (210.0 e 13.55), com a conta em comentário. O esperado veio do contrato, não do código novo.

**Por que `Decimal` ponta a ponta, e não só no arredondamento:** comparei as duas implementações com um oráculo do contrato (`Decimal`, sem chamar o código) em 640.016 entradas (preço de 0,00 a 400,00 de centavo em centavo × 4 cupons × 4 UFs). Manter float e arredondar com `Decimal(repr(total))` no fim divergiu em **433**; `Decimal` ponta a ponta divergiu em **0**. O erro já está no float acumulado antes do arredondamento.

## Consequências
- **Verificação:** `test_contrato` 17/17 (antes 14/17); suíte existente 26 OK; 11 verificações 8/3 (v08–v10, inalteradas).
- **Golden master:** 70 de 1050 entradas mudaram, todas explicadas: 40 na fronteira (subtotal com desconto exatamente 200, ex.: 223.55 → 210.0) e 30 em empates de arredondamento, todas em PE (taxa de 5%, ex.: 13.54 → 13.55, 247.06 → 247.07). As 1050 saídas novas batem com o oráculo do contrato. O golden master foi regravado como nova linha de base.
- **Mudança visível para quem usa:** pedidos de exatamente R$ 200,00 (após desconto) ficam mais baratos; alguns totais sobem 1 centavo nos empates.
- **Ferramenta de mutação:** `testes/mutacao_manual.py` procura trechos literais do código antigo (`frete = 12.9`, `if total > 200:`) e agora aborta com `AssertionError` em `calculo.py`. A prova de que os testes falhariam passa a ser por sabotagem manual sobre o código novo.

## Alternativas consideradas
- **Manter o código e marcar os 3 testes com `@unittest.expectedFailure`:** rejeitada. Deixaria um defeito conhecido em produção didática e um teste que "passa" falhando.
- **Arredondar com `Decimal` só no `return`:** rejeitada pela medição acima (433 divergências).
- **Inteiros em centavos:** equivalente em correção, mas exige converter taxas percentuais e muda mais linhas; `Decimal` é da biblioteca padrão e mantém a leitura próxima do contrato.

## Condição para rever
Rever se o contrato mudar a regra de fronteira ou de arredondamento (ex.: arredondamento bancário, arredondar por item) ou se a interface passar a exigir `Decimal` no retorno. Rever também se aparecer entrada cujo total diverge do oráculo: o oráculo e a grade de 640.016 entradas cobrem um item por carrinho e preço até R$ 400; carrinhos com vários itens só estão cobertos pelo golden master e por `test_subtotal_soma_preco_vezes_quantidade`.
