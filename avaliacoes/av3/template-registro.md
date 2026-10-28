# Registro individual — AV3

**Limite: três páginas + até duas de evidências.** Estudante: Eliakim Cordeiro — Data: 27/10/2026 — Caminho: B (MiniLoja: B3)

**Modo de interação usado e por quê (raio de impacto, oráculo, familiaridade):** agente (Claude Code no VS Code, não autocompletar) com plano revisado por mim. Raio pequeno e reversível (3 arquivos, branch própria); oráculo claro (R2.2 + teste vermelho antes da correção); conheço `estoque.py` da AV1.3. **Alternativa comparada:** chat + edição manual (mesmo oráculo, mas testes, sabotagem e mutação rodados à parte; na T1 da AV1.1, mesma tarefa: chat 9'45" × agente 3'55" até verificado, uma execução por modo e quem veio depois já conhecia o problema); agente sem plano revisado, descartado pelo raio de impacto (foi a revisão do plano que corrigiu o `liberar`). Limite: alternativas não executadas nesta AV3.

**Escopo declarado antes (seis campos):** objetivo: item sem estoque → recusa sem reserva remanescente (R2.2); pode tocar: `pedidos.py`, `estoque.py` (novo `liberar`), `test_pedidos.py`; não pode tocar: `testes/`, `regras.md`, `calculo.py`, cadastro, `handlers.py`, assinaturas, pagamento recusado; invariantes: totais e 409 iguais, suíte verde, verificações 8/3, só biblioteca padrão; pronto quando: teste vermelho no original e verde na correção, sabotagem detectada, diff em `caso/` só nos 3 arquivos; pare e pergunte se: mudar assinatura, handler ou pagamento, ou o contrato não responder. Aprovado por mim na sessão às 18:07:53, antes do 1º commit (`e039c68`, 18:08:40), mas versionado só depois da correção (`7dd40c5`); a prova do "antes" é a sessão (Evidências). **Cumprido? Como verifiquei (comando ou barreira):** sim; `git diff --stat main -- caso/` → só os 3 arquivos (+61/−3); suíte `Ran 29 … OK`; verificações `FAILED (failures=3)`, as mesmas v08–v10.

**Verificação:** *reserva* = saldo baixado **e** entrada `(pedido_id, sku)` em `reservas`; R2.2 exige desfazer os dois. Testes que falhariam sem a mudança (`test_pedidos.py`): `test_item_sem_estoque_nao_deixa_reserva` (exceção → recusa; saldo e `reservas` → R2.2; sem cobrança/pedido salvo → **derivado**, fora do contrato); `test_falha_no_ultimo_item_desfaz_todas_as_reservas` (várias reservas → R2.2); `test_handler_responde_409_sem_deixar_reserva` (`409` + sem reserva → R2.2 em HTTP). Prova (comandos e saídas em Evidências): `main` + testes → 3 falhas; corrigido → `OK`; sabotagens `pass` (3 falhas), `break` após o 1º `liberar` (`1 != 4`), sem `pop` (3 falhas) e sem `raise` (4 falhas). Mutação 74%, igual à AV1.3: nenhuma das 31 mutações atinge o rollback.

| O que a IA errou (o quê, onde) | Como detectei | O que corrigi e por quê (causa e impacto) |
| --- | --- | --- |
| 1º teste (`e039c68`) com uma só reserva antes da falha | Revisão (Sonnet 5.5); sabotagem `break` → suíte `OK` | Teste de três itens (`ea70c8a`): um item não distingue liberar tudo de liberar só a primeira; rollback parcial passaria verde |
| Opus, ao avaliar a revisão, afirmou que nada verificava o "409 continua" | S4: o teste antigo `test_handlers` falha (`201 != 409`) | O 409 já tinha teste, mas sem checar reservas; `post_pedidos` (`ea70c8a`) acrescenta 409 + sem reserva |
| Aplicou "SKU repetido fica como limite" antes da minha resposta | Horários da sessão: resposta 18:21:53, depois do `8cc20d6` (18:18:11) | Confirmei a decisão depois; registro a ordem real no anexo da sessão |
| Plano de commits deixou o escopo por último (`7dd40c5`) | Revisão (Sonnet 5.5) + horários do `git log` | Declarei a data real e anexei o trecho da sessão: o "antes" não era verificável pelo repositório |
| `liberar(sku, pedido_id)` lendo a quantidade de `reservas` | Revisão do plano: `reservar` sobrescreve a chave | `liberar(sku, qtd, pedido_id)` com lista local: com SKU repetido o saldo voltaria errado |
| "Sabotagem ou mutação" tratadas como provas equivalentes | Escore 74% idêntico antes e depois | Prova pela sabotagem; as mutações são fixas e não testam a mudança |

**Dependências novas (se houver) e checagem:** nenhuma; o diff só importa `EstoqueInsuficiente` e `handlers`, já do pacote.

| Medição do meu time | Meu desenho |
| --- | --- |
| Pergunta e decisão | A IA reduz o tempo de correção de bugs pequenos sem mais retrabalho? Decide se o agente pode **propor** correções |
| Métrica primária e guardrail | Tempo até verificado (suíte verde), por bug. Guardrail: reabertura ≤ baseline; nenhum teste alterado sem revisão |
| Baseline, período e método | Mediana sem IA dos bugs pequenos das 4 semanas anteriores (PRs e issues), a coletar (mín. 10); depois 4 semanas alternando com e sem IA; comparar medianas. Liberar se a mediana cair ≥30% e a reabertura ficar ≤ baseline |
| Risco de manipulação e contramedida | "Pronto" sem verificar, fatiar bugs, editar o teste. Contramedida: saída do teste anexada, tempo por bug, diff em teste exige revisão |
| Tarefa recorrente a automatizar e verificação exigida | Propor diff para falhas simples de teste (~2/semana, 30–50 min; estimativa). Antes de aplicar: o teste falha sem o diff e passa com ele; suíte verde numa cópia; diff só nos arquivos do bug, nenhum de teste (`git diff --name-only`). Sandbox sem commit, segredos ou PR de fork; 5 min; 50 mil tokens; o dev aprova. Parar se >30% forem descartadas em 2 semanas |

**Limites e condição para rever:** `pedido_id = "tmp-{usuario_id}"` é compartilhado: `liberar` pode apagar a entrada de pedido anterior do mesmo usuário (saldo certo); SKU repetido segue sobrescrevendo `reservas`; pagamento recusado ainda deixa reservas; exceção diferente de `EstoqueInsuficiente` deixaria reservas; o teste do handler usa o estoque global. Rever se `pedido_id` passar a ser único ou se o contrato exigir liberar reservas no pagamento recusado.

**Procedência/IA:** utilizada / ferramenta e modelo visíveis: Claude Code (VS Code), Opus 5.5 (execução); Claude app desktop, Sonnet 5.5 (revisão); tarefa delegada e contexto: ao Opus, explicar o enunciado e montar o roteiro, rascunhar escopo e plano, escrever testes e correção, rodar sabotagens e mutação, redigir PR e registro (contexto: `regras.md`, código do caso, enunciado e rubrica da AV3, minha AV1.6); ao Sonnet, revisar o registro contra a rubrica e propor uma versão; trecho aproveitado: testes e correção do agente, sem edição manual; PR e registro revisados por mim, combinando as duas versões; medição da minha AV1.6; minha verificação/intervenção: escolhi B3 e o modo, aprovei o escopo, decidi os limites, avaliei os pontos do Sonnet (confirmei o `break` verde), exigi que as sabotagens citadas fossem executadas e conferi as saídas. O raciocínio e a decisão registrados são meus.

**Revisão:** [x] modo; [x] escopo; [x] verificação; [x] erros da IA; [x] medição e automação; [x] procedência.

---

## Evidências

**Escopo antes do código (sessão Claude Code `b2c4e7ce-c87d-43d5-aa01-9374099f9e69`, 27/10/2026; horários convertidos de UTC para −0300, o fuso do `git log`; linha do tempo completa em `av3/sessao-trecho.md`):** o agente apresentou os seis campos às 17:53:31; às 18:07:53 respondi "Escopo: OK; Modo: Agente no editor (Claude Code) com plano revisado por mim". Plano revisado: "Siga a 1 com o recomendado" às 18:17:21, antes da correção (1ª pergunta do plano, sobre `pedido_id`; decisão: não tratar e registrar como limite), e "SKU duplicado no pedido não mexer e registrar como limite" às 18:21:53, depois da correção.

```
e039c68  18:08  teste de regressão (vermelho)
8cc20d6  18:18  correção (liberar + rollback em criar)
7dd40c5  18:19  PR e registro
ea70c8a  23:37  testes de várias reservas e de 409
```

```
e039c68 (só o 1º teste):  AssertionError: 3 != 5 | Ran 27 ... FAILED (failures=1)
main + 3 testes:          3 != 5 | 46 != 48 | 3 != 5 | Ran 29 ... FAILED (failures=3)
av3-b3-reserva:           --existentes: Ran 29 ... OK
verificações (v08–v10):   Ran 11 ... FAILED (failures=3)
mutação:                  Mutantes: 31 | mortos: 23 | sobreviventes: 8 | escore: 74%
```

Reprodução de "main + 3 testes" (esperado: `failures=3`):

```
git checkout main
git checkout av3-b3-reserva -- caso/testes_existentes/test_pedidos.py
python -B testes/test_miniloja.py --codigo caso --existentes
git restore --source=HEAD --staged --worktree caso/testes_existentes/test_pedidos.py
git checkout av3-b3-reserva
```

Sabotagens, uma por vez em `av3-b3-reserva` (rodar `python -B testes/test_miniloja.py --codigo caso --existentes`; desfazer com `git restore caso/miniloja/`):

```
S1 pass:      corpo de liberar() trocado por `pass`            → failures=3 (3 != 5 | 46 != 48 | 3 != 5)
S2 break:     `break` após o 1º liberar() em criar()           → failures=1 (1 != 4)
S3 sem pop:   sed -i '/self.reservas.pop/d' caso/miniloja/estoque.py
              → failures=3 ({('tmp-1', 'BOLA-01'): 2} != {} e equivalentes)
S4 sem raise: sed -i '/^            raise$/d' caso/miniloja/pedidos.py
              → failures=4 (EstoqueInsuficiente not raised ×2; 201 != 409 ×2,
                um deles do teste antigo test_handlers)
```

Mutação (Git Bash, na raiz):

```
MINILOJA_TEST_CMD="python -B testes/test_miniloja.py --existentes --codigo caso -x" python -B testes/mutacao_manual.py
```
