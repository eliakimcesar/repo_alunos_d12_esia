# Registro individual — AV3

**Limite: três páginas + até duas de evidências.** Estudante: Eliakim — Data: 27/10/2026 — Caminho: B (MiniLoja: B3)

**Modo de interação usado e por quê (raio de impacto, oráculo, familiaridade):** agente no editor (Claude Code) com plano revisado por mim antes de executar. Raio de impacto pequeno e reversível: dois arquivos de código em branch própria do meu fork (`av3-b3-reserva`). Oráculo claro: R2.2 ("nenhuma reserva pode permanecer") e um teste escrito e visto vermelho antes da correção. Familiaridade: já tinha lido `estoque.py` na AV1.3 (mutante `<` → `<=`). **Alternativa comparada:** chat + edição manual. Descartei porque o agente roda suíte, sabotagem e mutação no próprio repositório e a revisão do plano mantém a decisão comigo; com o chat eu copiaria código sem execução no mesmo passo.

**Escopo declarado antes (seis campos):** objetivo: item sem estoque → pedido recusado sem reserva remanescente (R2.2); pode tocar: `pedidos.py`, `estoque.py` (novo `liberar`), `testes_existentes/test_pedidos.py`; não pode tocar: `testes/`, `regras.md`, `calculo.py`, cadastro, `handlers.py`, assinaturas de `criar`/`reservar`, fluxo de pagamento recusado; invariantes: totais e 409 iguais, suíte existente verde, verificações 8/3 (v08–v10), só biblioteca padrão; pronto quando: teste novo vermelho no original e verde na correção, sabotagem detectada, diff só nos três arquivos; pare e pergunte se: mudar assinatura, handler ou pagamento, ou se o contrato não responder. **Cumprido? Como verifiquei (comando ou barreira):** sim. `git diff --stat main -- caso/` → 3 arquivos (estoque +5; pedidos +11/−2; test_pedidos +15/−1); `--existentes` → `Ran 27 tests … OK`; verificações → `Ran 11 tests … FAILED (failures=3)`, as mesmas v08–v10. O "pare e pergunte" disparou uma vez (`pedido_id` compartilhado) e decidi não tratar (ver Limites).

**Verificação:** teste que falharia sem a mudança: `TestPedidos.test_item_sem_estoque_nao_deixa_reserva` (BOLA-01: 5, CHUTEIRA-42: 0; pedido BOLA×2 + CHUTEIRA×1 → `EstoqueInsuficiente`, saldo BOLA volta a 5, `reservas` vazio, sem cobrança, sem pedido salvo); prova: no commit `e039c68` (só o teste) → `AssertionError: 3 != 5 … FAILED (failures=1)`; no `8cc20d6` → `OK`; sabotagem em cópia (`liberar` → `pass`) → `3 != 5`; mutação → `31 | mortos: 23 | escore: 74%`, igual à AV1.3, porque nenhuma das 31 mutações fixas atinge o rollback.

| O que a IA errou (o quê, onde) | Como detectei | O que corrigi e por quê (causa e impacto) |
| --- | --- | --- |
| No roteiro, tratou "sabotagem ou mutação" como provas equivalentes para o teste novo (`testes/mutacao_manual.py`) | Rodei a mutação depois da correção: escore 74%, idêntico ao de antes, e nenhuma mutação em `pedidos.py` cobre o rollback | Usei a sabotagem como prova e registrei o escore como limite. Causa: a lista de mutações é fixa. Impacto: citar o 74% como prova seria evidência que não testa a mudança |
| O primeiro escopo previa `liberar(sku, pedido_id)`, tirando a quantidade de `estoque.reservas` (`estoque.py`) | Na revisão do plano, a leitura de `reservar` mostrou que ele sobrescreve `reservas[(pedido_id, sku)]` em vez de somar | O plano aprovado usa `liberar(sku, qtd, pedido_id)` com a lista local de itens reservados. Causa: o dicionário perde a quantidade com SKU repetido. Impacto: o saldo voltaria errado |
| O roteiro mandava trabalhar numa cópia `trabalho/`, mas a mudança foi feita em `caso/` na branch | Confronto entre o roteiro e o `git diff` | Mantive em `caso/` na branch do fork, porque o revisor roda `--codigo caso` e o diff fica no PR. Impacto: nenhum no código; só a instrução estava inconsistente |
| Tentou commitar sem conferir a identidade do git (`fatal: unable to auto-detect email address`) | Erro do próprio `git commit` | Configurei `user.name`/`user.email` só no repositório, iguais aos da AV2. Impacto: commit autoral correto, sem mexer na configuração global |

**Dependências novas (se houver) e checagem:** nenhuma; `git diff main -- caso/` não tem `import` novo além de `EstoqueInsuficiente`, que já existia no pacote.

| Medição do meu time | Meu desenho |
| --- | --- |
| Pergunta e decisão | ___ |
| Métrica primária e guardrail | ___ |
| Baseline, período e método | ___ |
| Risco de manipulação e contramedida | ___ |
| Tarefa recorrente a automatizar e verificação exigida | ___ |

**Limites e condição para rever:** `pedido_id = "tmp-{usuario_id}"` é compartilhado entre pedidos do mesmo usuário: `liberar` remove a entrada de `reservas` de um pedido anterior com o mesmo SKU (o saldo fica certo). SKU repetido continua sobrescrevendo `reservas`. Pagamento recusado ainda deixa reservas (R2.3 só exige "não salva"). O teste cobre um cenário (falha no 2º item), não falhas no 1º nem pedidos com três ou mais itens. A branch parte de `main`; R1.3/R1.5 estão no PR da AV2. Rever se `pedido_id` passar a ser único ou se o contrato exigir liberar reservas no pagamento recusado.

**Procedência/IA:** utilizada / ferramenta e modelo visíveis: Claude Code, Claude Opus 5.5; tarefa delegada e contexto: roteiro da atividade, rascunho do escopo, teste de regressão, correção, sabotagem, mutação, descrição do PR e rascunho deste registro; trecho aproveitado: teste, correção e PR, após minha revisão do plano; minha verificação/intervenção: aprovei o escopo, escolhi o B3 e o modo, revisei o plano e decidi deixar `pedido_id` compartilhado e SKU repetido como limites, conferi as saídas e escrevi a medição. O raciocínio e a decisão registrados são meus.

**Revisão:** [x] modo; [x] escopo; [x] verificação; [x] erros da IA; [ ] medição e automação; [ ] procedência.
