# AV3 · B3 — Desfazer reservas quando um item não tem estoque (R2.2)

## Intenção
R2.2: "Se algum item não tiver estoque, o pedido é recusado (`409`) e **nenhuma reserva pode permanecer**." Hoje `PedidoService.criar` reserva item por item; quando o segundo item falha, a reserva do primeiro fica (saldo baixado e entrada em `estoque.reservas`).

## Escopo (declarado antes da mudança)
- **Objetivo:** item sem estoque → pedido recusado sem nenhuma reserva remanescente.
- **Pode tocar:** `caso/miniloja/pedidos.py`, `caso/miniloja/estoque.py` (novo `liberar`), `caso/testes_existentes/test_pedidos.py`.
- **Não pode tocar:** `testes/`, `caso/regras.md`, `calculo.py`, cadastro, `handlers.py`, assinaturas de `criar` e `reservar`, fluxo de pagamento recusado.
- **Invariantes:** totais e status HTTP iguais (409 continua); suíte existente verde; verificações 8 passam / 3 falham (v08–v10); só biblioteca padrão.
- **Pronto quando:** teste novo falha no original e passa com a correção; sabotagem o faz falhar; diff só nos três arquivos.
- **Pare e pergunte se:** precisar mudar assinatura pública, `handlers.py` ou pagamento; o contrato não responder (ex.: SKU repetido).

## Plano (revisado antes de executar)
1. Teste de regressão, vermelho no código atual (commit `e039c68`).
2. `Estoque.liberar(sku, qtd, pedido_id)`; em `criar`, lista local dos itens reservados, rollback em `EstoqueInsuficiente` e `raise` (commit `8cc20d6`).
3. Registro e esta descrição.

Decisão de revisão: a quantidade devolvida vem da lista local, não de `estoque.reservas`, porque `reservar` sobrescreve a chave `(pedido_id, sku)`. Os problemas do `pedido_id` compartilhado e do SKU duplicado em `reservas` ficaram fora do escopo (ver Limites).

## Como verificar
```
git checkout e039c68   # só o teste
python -B testes/test_miniloja.py --codigo caso --existentes
# AssertionError: 3 != 5 ... Ran 27 tests ... FAILED (failures=1)

git checkout av3-b3-reserva
python -B testes/test_miniloja.py --codigo caso --existentes
# Ran 27 tests ... OK
python -B testes/test_miniloja.py --codigo caso
# Ran 11 tests ... FAILED (failures=3)   -> v08, v09, v10, as mesmas do material inicial
git diff --stat main -- caso/
# 3 arquivos: estoque.py (+5), pedidos.py (+11/-2), test_pedidos.py (+15/-1)
```
Sabotagem (cópia fora do repositório, `liberar(...)` trocado por `pass`): `AssertionError: 3 != 5`.
Mutação (`MINILOJA_TEST_CMD="python -B testes/test_miniloja.py --existentes --codigo caso -x"`): `Mutantes: 31 | mortos: 23 | sobreviventes: 8 | escore: 74%`, igual ao anterior; nenhuma das 31 mutações atinge o rollback, então a prova do teste é a sabotagem.

## Teste que falharia sem a mudança
`caso/testes_existentes/test_pedidos.py::TestPedidos.test_item_sem_estoque_nao_deixa_reserva`: estoque `BOLA-01: 5`, `CHUTEIRA-42: 0`; pedido com BOLA-01×2 e CHUTEIRA-42×1 → `EstoqueInsuficiente`, saldo de BOLA-01 volta a 5, `reservas` vazio, sem cobrança, sem pedido salvo.

## Dependências novas
Nenhuma (somente biblioteca padrão).

## Modo de interação
Agente no editor (Claude Code, Claude Opus 5.5) com plano revisado por mim antes de executar. Motivo: raio de impacto pequeno e reversível (dois arquivos de código, branch própria), oráculo claro (R2.2 + teste vermelho antes da correção) e código já conhecido da AV1.3. Alternativa comparada: chat + edição manual, descartada porque o agente roda os testes, a sabotagem e a mutação no próprio repositório, e a revisão do plano mantém a decisão comigo.

## Limites
- `pedido_id = f"tmp-{usuario_id}"` é o mesmo para todos os pedidos de um usuário: o `liberar` remove a entrada `(tmp-N, sku)` de `reservas` mesmo que ela venha de um pedido anterior aprovado (o saldo fica correto). Corrigir exige `pedido_id` único, fora do escopo.
- SKU repetido no mesmo pedido: o saldo volta certo, mas `reservas` continua sobrescrevendo a entrada (comportamento anterior).
- Pagamento recusado (R2.3) ainda deixa reservas; o contrato só exige "não salva".
- A branch parte de `main`; as correções de R1.3/R1.5 estão no PR da AV2 (`av2-refatoracao`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
