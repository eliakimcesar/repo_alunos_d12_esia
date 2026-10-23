# ADR-001 — Entradas inválidas em `calcular_total`: lacuna do contrato, sem teste nem correção na AV2

**Status:** aceito · **Data:** 22/10/2026 · **Autor:** Eliakim · **Escopo:** AV2, Caminho B (MiniLoja)

## Contexto
A suíte `av2/test_contrato.py` deriva cada esperado de `caso/regras.md` (R1). Ao revisar a cobertura, procurei casos de entrada inválida (carrinho vazio, quantidade zero ou negativa, preço negativo) e verifiquei que **R1 não define nenhum deles**. O carrinho vazio só aparece em R2.1, no nível do pedido (`400`), e `PedidoService.criar` já o rejeita com `if not itens` (coberto pela verificação v05). Quantidade e preço não têm validação definida em lugar nenhum do contrato.

Comportamento observado no código atual (`caso/`, após o commit `8b7c937`), executado a partir de `caso/`:

| Entrada (UF PE, sem cupom) | `calcular_total` devolve |
| --- | --- |
| `[]` | `13.54` (frete e taxa sobre subtotal zero) |
| `[{"preco": 50.0, "qtd": 0}]` | `13.54` |
| `[{"preco": 50.0, "qtd": -1}]` | `-38.95` |
| `[{"preco": -300.0, "qtd": 1}]` | `-301.46` |

### Quantidade negativa (`qtd = -1`): efeito no cálculo e no estoque
O efeito não se limita ao cálculo. Com `qtd = -1`:

| Onde | Entrada | Observado | Por quê |
| --- | --- | --- | --- |
| `calcular_total` | `[{"preco": 50.0, "qtd": -1}]`, PE | `-38.95` | subtotal `-50`; `-50 + 12,90 = -37,10`; `× 1,05 = -38,955` |
| `Estoque.reservar` | `reservar("BOLA-01", -1, "p1")` com saldo 50 | saldo passa a **51** | `disponivel < qtd` (`50 < -1`) é falso, então não barra; `disponivel - qtd` = `50 - (-1)` soma |
| `PedidoService.criar` | pedido com `qtd = -1` | passa por `if not itens` (lista não vazia), reserva aumentando o estoque e chama `gateway.cobrar` com total negativo | não há validação de quantidade em nenhuma camada |

Reprodução (a partir de `caso/`):
```
python -B -c "from miniloja.calculo import calcular_total as c; print(c([{'preco':50.0,'qtd':-1}],None,'PE'))"
python -B -c "from miniloja.estoque import Estoque; e=Estoque({'BOLA-01':50}); e.reservar('BOLA-01',-1,'p1'); print(e.saldo('BOLA-01'))"
```
Saídas observadas em 22/10/2026 (Python 3.14.0): `-38.95` e `51`.

## Decisão
Registrar como **lacuna do contrato** e **não** escrever teste nem alterar o código nesta entrega:
- Sem regra, não há esperado derivável; qualquer valor (exceção, `0`, `422`) seria inventado, e o teste viraria opinião, não verificação do contrato.
- Corrigir mudaria comportamento fora do escopo declarado da AV2 (refatoração com comportamento preservado) e tocaria `estoque.py`/`pedidos.py`, que estão em "não pode tocar".
- O escopo prevê "pare e pergunte" quando a mudança exige decidir algo que o contrato não diz: esta é essa situação.

## Consequências
- A suíte de contrato **não garante nada** sobre quantidade zero, negativa ou preço negativo; o golden master preserva só o carrinho vazio (entrada `vazio`); todas as outras entradas têm `qtd >= 1` e preço positivo, então uma refatoração que mudasse esse comportamento passaria despercebida.
- O risco conhecido (total negativo e aumento de estoque) fica documentado aqui, não mitigado.

## Alternativas consideradas
- **Testar o comportamento atual** (ex.: afirmar `-38.95`): rejeitada; seria teste espelho, que congela um provável defeito como se fosse regra.
- **Validar em `calcular_total` lançando `ValueError`**: rejeitada nesta entrega; muda comportamento, exige definir status HTTP e mensagem, e a validação talvez pertença ao handler ou ao pedido, não ao cálculo.

## Condição para rever
Rever quando o contrato passar a definir a validação de itens (quantidade mínima, preço não negativo e onde a recusa acontece, com status e formato de erro). Nesse momento: escrever primeiro os testes derivados da nova regra, mostrar que falham no código atual, e só então corrigir `calcular_total`/`estoque.py` em mudança com escopo próprio.
