# AV3 · B3 — Desfazer reservas quando um item não tem estoque (R2.2)

## Intenção
R2.2: "Se algum item não tiver estoque, o pedido é recusado (`409`) e **nenhuma reserva pode permanecer**." Hoje `PedidoService.criar` reserva item por item; quando o segundo item falha, a reserva do primeiro fica (saldo baixado e entrada em `estoque.reservas`).

## Escopo (declarado antes da mudança)
Escrito e aprovado na sessão com o agente antes do primeiro commit (`e039c68`); versionado só depois da correção, neste arquivo (`7dd40c5`). O trecho da sessão está nas evidências do registro.

- **Objetivo:** item sem estoque → pedido recusado sem nenhuma reserva remanescente.
- **Pode tocar:** `caso/miniloja/pedidos.py`, `caso/miniloja/estoque.py` (novo `liberar`), `caso/testes_existentes/test_pedidos.py`.
- **Não pode tocar:** `testes/`, `caso/regras.md`, `calculo.py`, cadastro, `handlers.py`, assinaturas de `criar` e `reservar`, fluxo de pagamento recusado.
- **Invariantes:** totais e status HTTP iguais (409 continua); suíte existente verde; verificações 8 passam / 3 falham (v08–v10); só biblioteca padrão.
- **Pronto quando:** teste novo falha no original e passa com a correção; sabotagem o faz falhar; diff só nos três arquivos.
- **Pare e pergunte se:** precisar mudar assinatura pública, `handlers.py` ou pagamento; o contrato não responder (ex.: SKU repetido).

## Plano (revisado antes de executar)
1. Teste de regressão, vermelho no código atual (commit `e039c68`).
2. `Estoque.liberar(sku, qtd, pedido_id)`; em `criar`, lista local dos itens reservados, rollback em `EstoqueInsuficiente` e `raise` (commit `8cc20d6`).
3. Registro e esta descrição (`7dd40c5`).
4. Após revisão do registro: teste com várias reservas, teste do 409 no handler e rótulos regra/derivado nas asserções (`ea70c8a`).

Decisão de revisão: a quantidade devolvida vem da lista local, não de `estoque.reservas`, porque `reservar` sobrescreve a chave `(pedido_id, sku)`. Os problemas do `pedido_id` compartilhado e do SKU duplicado em `reservas` ficaram fora do escopo (ver Limites).

## Como verificar
```
git checkout e039c68   # só o teste
python -B testes/test_miniloja.py --codigo caso --existentes
# AssertionError: 3 != 5 ... Ran 27 tests ... FAILED (failures=1)

git checkout av3-b3-reserva
python -B testes/test_miniloja.py --codigo caso --existentes
# Ran 29 tests ... OK
python -B testes/test_miniloja.py --codigo caso
# Ran 11 tests ... FAILED (failures=3)   -> v08, v09, v10, as mesmas do material inicial
git diff --stat main -- caso/
# 3 arquivos: estoque.py (+5), pedidos.py (+11/-2), test_pedidos.py (+45/-1)
```
Código de `main` com os três testes (esperado `failures=3`: `3 != 5`, `46 != 48`, `3 != 5`):
```
git checkout main
git checkout av3-b3-reserva -- caso/testes_existentes/test_pedidos.py
python -B testes/test_miniloja.py --codigo caso --existentes
git restore --source=HEAD --staged --worktree caso/testes_existentes/test_pedidos.py
git checkout av3-b3-reserva
```
Sabotagens, uma por vez em `av3-b3-reserva` (desfazer com `git restore caso/miniloja/`):
```
S1 corpo de liberar() -> pass                                   failures=3
S2 break após o 1º liberar() em criar()                         failures=1 (1 != 4)
S3 sed -i '/self.reservas.pop/d' caso/miniloja/estoque.py       failures=3 (reservas != {})
S4 sed -i '/^            raise$/d' caso/miniloja/pedidos.py     failures=4 (not raised; 201 != 409)
```
Mutação (`MINILOJA_TEST_CMD="python -B testes/test_miniloja.py --existentes --codigo caso -x"`): `Mutantes: 31 | mortos: 23 | sobreviventes: 8 | escore: 74%`, igual ao anterior; nenhuma das 31 mutações atinge o rollback, então a prova dos testes é a sabotagem.

## Testes que falhariam sem a mudança
*Reserva* = saldo baixado **e** entrada `(pedido_id, sku)` em `estoque.reservas`; "nenhuma reserva permanece" exige desfazer os dois. Em `caso/testes_existentes/test_pedidos.py`:
- `test_item_sem_estoque_nao_deixa_reserva`: BOLA-01×2 + CHUTEIRA-42 sem saldo → `EstoqueInsuficiente` (R2.2 recusa); saldo 5 e `reservas` vazio (R2.2); sem cobrança e sem pedido salvo (**derivado**, não escrito no contrato).
- `test_falha_no_ultimo_item_desfaz_todas_as_reservas`: BOLA×2, CAMISA×3, CHUTEIRA sem saldo → os dois saldos voltam (R2.2 com várias reservas; pega o rollback parcial).
- `test_handler_responde_409_sem_deixar_reserva`: via `handlers.post_pedidos` → `409` com o `sku` e saldo intacto (R2.2 na camada HTTP; verifica o invariante "409 continua").

## Dependências novas
Nenhuma (somente biblioteca padrão).

## Modo de interação
Agente no editor (Claude Code, Claude Opus 5.5) com plano revisado por mim antes de executar. Motivo: raio de impacto pequeno e reversível (dois arquivos de código, branch própria), oráculo claro (R2.2 + teste vermelho antes da correção) e código já conhecido da AV1.3. Alternativas comparadas: chat + edição manual (na T1 da AV1.1, mesma tarefa: chat 9'45" × agente 3'55" até verificado, uma execução por modo e quem veio depois já conhecia o problema) e agente sem plano revisado (descartado pelo raio de impacto; foi a revisão do plano que corrigiu o `liberar`). As alternativas não foram executadas nesta AV3.

## Limites
- `pedido_id = f"tmp-{usuario_id}"` é o mesmo para todos os pedidos de um usuário: o `liberar` remove a entrada `(tmp-N, sku)` de `reservas` mesmo que ela venha de um pedido anterior aprovado (o saldo fica correto). Corrigir exige `pedido_id` único, fora do escopo.
- SKU repetido no mesmo pedido: o saldo volta certo, mas `reservas` continua sobrescrevendo a entrada (comportamento anterior).
- Pagamento recusado (R2.3) ainda deixa reservas; o contrato só exige "não salva".
- Exceção diferente de `EstoqueInsuficiente` durante as reservas não dispara o rollback.
- O teste do handler usa o estoque global do módulo (usuário 9001 para não colidir com outros testes).
- A branch parte de `main`; as correções de R1.3/R1.5 estão no PR da AV2 (`av2-refatoracao`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
