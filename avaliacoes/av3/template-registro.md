# Registro individual — AV3

**Limite: três páginas + até duas de evidências.** Estudante: Eliakim Cordeiro — Data: 27/10/2026 — Caminho: B (MiniLoja: B3)

**Modo de interação usado e por quê (raio de impacto, oráculo, familiaridade):** agente no editor (Claude Code) com plano revisado por mim. Raio pequeno e reversível (3 arquivos, branch própria); oráculo claro (R2.2 + teste vermelho antes da correção); conheço `estoque.py` da AV1.3. **Alternativa comparada:** chat + edição manual (mesmo oráculo, mas testes, sabotagem e mutação rodados à parte; na T1 da AV1.1, mesma tarefa: chat 9'45" × agente 3'55" até verificado); agente sem plano revisado, descartado pelo raio de impacto (foi a revisão do plano que corrigiu o `liberar`). Limite: alternativas não executadas nesta AV3.

**Escopo declarado antes (seis campos):** objetivo: item sem estoque → recusa sem reserva remanescente (R2.2); pode tocar: `pedidos.py`, `estoque.py` (novo `liberar`), `test_pedidos.py`; não pode tocar: `testes/`, `regras.md`, `calculo.py`, cadastro, `handlers.py`, assinaturas, pagamento recusado; invariantes: totais e 409 iguais, suíte verde, verificações 8/3, só biblioteca padrão; pronto quando: teste vermelho no original e verde na correção, sabotagem detectada, diff só nos 3 arquivos; pare e pergunte se: mudar assinatura, handler ou pagamento, ou o contrato não responder. Aprovado por mim na sessão antes do 1º commit (`e039c68`), mas versionado só depois da correção (`7dd40c5`); a prova do "antes" é o trecho da sessão (Evidências). **Cumprido? Como verifiquei (comando ou barreira):** sim; `git diff --stat main -- caso/` → só os 3 arquivos (+61/−3); suíte `Ran 29 … OK`; verificações `FAILED (failures=3)`, as mesmas v08–v10.

**Verificação:** *reserva* = saldo baixado **e** entrada `(pedido_id, sku)` em `reservas`; R2.2 exige desfazer os dois. Testes que falhariam sem a mudança (`test_pedidos.py`): `test_item_sem_estoque_nao_deixa_reserva` (exceção → recusa; saldo e `reservas` → R2.2; sem cobrança/pedido salvo → **derivado**, fora do contrato); `test_falha_no_ultimo_item_desfaz_todas_as_reservas` (várias reservas → R2.2); `test_handler_responde_409_sem_deixar_reserva` (`409` → R2.2 na camada HTTP). Prova: `main` + testes → `FAILED (failures=3)`; corrigido → `OK`; sabotagem `pass` → 3 falhas; `break` após o 1º `liberar` → `1 != 4`. Mutação 74%, igual à AV1.3: nenhuma das 31 mutações atinge o rollback.

| O que a IA errou (o quê, onde) | Como detectei | O que corrigi e por quê (causa e impacto) |
| --- | --- | --- |
| 1º teste (`e039c68`) com uma só reserva antes da falha | Revisão (Sonnet 5.5); sabotagem `break` → suíte `OK` | Teste de três itens (`ea70c8a`): um item não distingue liberar tudo de liberar só a primeira; rollback parcial passaria verde |
| Invariante "409 continua" sem teste | Revisão (Sonnet 5.5): testes só do serviço | Teste via `post_pedidos` (`ea70c8a`): mudança no handler quebraria o 409 sem aviso |
| Plano de commits deixou o escopo por último (`7dd40c5`) | Revisão (Sonnet 5.5) + horários do `git log` | Declarei a data real e anexei o trecho da sessão: o "antes" não era verificável pelo repositório |
| `liberar(sku, pedido_id)` lendo a quantidade de `reservas` | Revisão do plano: `reservar` sobrescreve a chave | `liberar(sku, qtd, pedido_id)` com lista local: com SKU repetido o saldo voltaria errado |
| "Sabotagem ou mutação" tratadas como provas equivalentes | Escore 74% idêntico antes e depois | Prova pela sabotagem; as mutações são fixas e não testam a mudança |

**Dependências novas (se houver) e checagem:** nenhuma; o diff só importa `EstoqueInsuficiente` e `handlers`, já do pacote.

| Medição do meu time | Meu desenho |
| --- | --- |
| Pergunta e decisão | A IA reduz o tempo de correção de bugs pequenos sem aumentar o retrabalho? Decide se o agente pode **propor** correções, em ambiente de teste |
| Métrica primária e guardrail | Tempo até verificado (suíte verde), por bug. Guardrail: zero reabertura em 4 semanas; nenhum teste alterado sem revisão |
| Baseline, período e método | Mediana sem IA dos bugs pequenos das 4 semanas anteriores (PRs e issues), a coletar; depois 4 semanas alternando com e sem IA; comparar medianas. A T1 da AV1.1 só compara modos |
| Risco de manipulação e contramedida | "Pronto" sem verificar, fatiar bugs, editar o teste. Contramedida: saída do teste anexada, tempo por bug, diff em teste exige revisão |
| Tarefa recorrente a automatizar e verificação exigida | Propor diff para falhas simples de teste (~2/semana, 30–50 min). Antes de aplicar: o teste falha sem o diff e passa com ele; suíte verde numa cópia; diff só nos arquivos do bug. Sandbox sem commit, segredos ou PR de fork; 5 min; 50 mil tokens; o dev aprova. Parar se >30% forem descartadas em 2 semanas |

**Limites e condição para rever:** `pedido_id = "tmp-{usuario_id}"` é compartilhado, e `liberar` pode apagar a entrada de um pedido anterior do mesmo usuário (o saldo fica certo); SKU repetido segue sobrescrevendo `reservas`; pagamento recusado ainda deixa reservas; o teste do handler usa o estoque global (usuário 9001). Rever se `pedido_id` passar a ser único ou se o contrato exigir liberar reservas no pagamento recusado.

**Procedência/IA:** utilizada / ferramenta e modelo visíveis: Claude Code (VS Code), Claude Opus 5.5, na execução; Claude app desktop, Claude Sonnet 5.5, na revisão do registro; tarefa delegada e contexto: roteiro, rascunho do escopo, testes, correção, sabotagens, mutação, PR e rascunho do registro (contexto: `regras.md`, código, enunciado, rubrica, minha AV1.6); ao Sonnet, revisar o registro contra a rubrica; trecho aproveitado: testes e correção escritos pelo agente, sem edição manual minha; PR e registro revisados por mim; medição da minha AV1.6; minha verificação/intervenção: escolhi B3 e o modo, aprovei o escopo, decidi os limites do plano, avaliei os pontos da revisão (confirmei o `break` verde) e conferi as saídas. O raciocínio e a decisão registrados são meus.

**Revisão:** [x] modo; [x] escopo; [x] verificação; [x] erros da IA; [x] medição e automação; [x] procedência.

---

## Evidências

**Escopo antes do código (sessão, 27/10/2026):** o agente apresentou os seis campos; respondi "Escopo: OK; Modo: Agente no editor (Claude Code) com plano revisado por mim". Plano revisado: "Siga a 1 com o recomendado" (`pedido_id`) e "SKU duplicado no pedido não mexer e registrar como limite".

```
e039c68 18:08 teste de regressão (vermelho)    8cc20d6 18:18 correção
7dd40c5 18:19 PR e registro                    ea70c8a       testes de várias reservas e 409

e039c68:          AssertionError: 3 != 5        Ran 27 ... FAILED (failures=1)
main + 3 testes:  3 != 5 | 46 != 48 | 3 != 5    Ran 29 ... FAILED (failures=3)
av3-b3-reserva:   --existentes Ran 29 ... OK    verificações Ran 11 ... FAILED (failures=3)
sabotagem pass:   FAILED (failures=3)           sabotagem break: 1 != 4
mutação:          Mutantes: 31 | mortos: 23 | sobreviventes: 8 | escore: 74%
```
