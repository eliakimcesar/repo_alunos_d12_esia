# Registro individual — AV3

**Limite: três páginas + até duas de evidências.** Estudante: Eliakim Cordeiro — Data: 27/10/2026 — Caminho: B (MiniLoja: B3)

**Modo de interação usado e por quê (raio de impacto, oráculo, familiaridade):** agente no editor (Claude Code) com plano revisado por mim antes de executar. *Raio de impacto:* dois arquivos de código e um de teste, em branch própria do fork (`av3-b3-reserva`), reversível com git. *Oráculo:* R2.2 e um teste visto vermelho antes da correção. *Familiaridade:* conheço `estoque.py` da AV1.3. **Alternativa comparada:** (a) **chat + edição manual**: mesmo oráculo, mas eu copiaria o código e rodaria testes, sabotagem e mutação à parte. Na T1 da AV1.1, na mesma tarefa, o chat levou 9'45" até verificado e o agente 3'55". (b) **Agente sem plano revisado**: descartado pelo raio de impacto, porque sem escopo e plano o agente pode tocar `handlers.py` ou o pagamento, e foi a revisão do plano que cortou `liberar` lendo de `reservas`. *Limite:* na AV3 as alternativas não foram executadas; a comparação vem da AV1.1 (uma tarefa, uma pessoa).

**Escopo declarado antes (seis campos):** objetivo: item sem estoque → pedido recusado sem reserva remanescente (R2.2); pode tocar: `pedidos.py`, `estoque.py` (novo `liberar`), `testes_existentes/test_pedidos.py`; não pode tocar: `testes/`, `regras.md`, `calculo.py`, cadastro, `handlers.py`, assinaturas de `criar`/`reservar`, fluxo de pagamento recusado; invariantes: totais e 409 iguais, suíte existente verde, verificações 8/3 (v08–v10), só biblioteca padrão; pronto quando: teste novo vermelho no original e verde na correção, sabotagem detectada, diff só nos três arquivos; pare e pergunte se: mudar assinatura, handler ou pagamento, ou se o contrato não responder. **Quando foi declarado:** escrito na sessão com o agente e aprovado por mim ("Escopo: OK") **antes** do primeiro commit (`e039c68`, 18:08). Só foi **versionado depois** da correção, em `7dd40c5` (18:19), porque o plano de commits deixava a documentação por último (ver erros da IA). A prova de "antes" é a transcrição da sessão (trecho em Evidências), não o histórico git. **Cumprido? Como verifiquei:** sim. `git diff --stat main -- caso/` → os três arquivos permitidos (estoque +5; pedidos +11/−2; test_pedidos +45/−1); `handlers.py` intocado; suíte existente `Ran 29 tests … OK`; verificações `Ran 11 tests … FAILED (failures=3)`, as mesmas v08–v10. O "pare e pergunte" disparou uma vez (`pedido_id` compartilhado); decidi não tratar (ver Limites).

**Verificação.** *Reserva*, neste caso, é o efeito de `Estoque.reservar`: saldo do SKU baixado **e** entrada `(pedido_id, sku)` em `reservas`. "Nenhuma reserva permanece" = os dois desfeitos. Testes e mapeamento:

| Teste (`test_pedidos.py`) | Asserção → regra |
| --- | --- |
| `test_item_sem_estoque_nao_deixa_reserva` (BOLA×2 + CHUTEIRA sem saldo) | `EstoqueInsuficiente` → R2.2 recusa; `saldo == 5` e `reservas == {}` → R2.2 nenhuma reserva; sem cobrança e sem pedido salvo → **derivado**, não escrito no contrato (a recusa ocorre antes de cobrar) |
| `test_falha_no_ultimo_item_desfaz_todas_as_reservas` (BOLA×2, CAMISA×3, CHUTEIRA sem saldo) | saldos de BOLA **e** CAMISA voltam, `reservas == {}` → R2.2 com várias reservas |
| `test_handler_responde_409_sem_deixar_reserva` (via `handlers.post_pedidos`) | `status == 409` e `sku` no corpo → R2.2 "recusado (`409`)"; saldo do estoque do handler intacto → R2.2 |

Prova de que falhariam sem a mudança: código de `main` + testes novos → `FAILED (failures=3)` (`3 != 5`, `46 != 48`, `3 != 5`); com a correção → `OK`. Sabotagens em cópia: `liberar` → `pass` → os três falham; `break` após o primeiro `liberar` → `test_falha_no_ultimo_item…` falha (`1 != 4`), e era isso que o teste original não pegava. Mutação → `31 | mortos: 23 | escore: 74%`, igual à AV1.3: nenhuma das 31 mutações fixas atinge o rollback, então a prova é a sabotagem.

| O que a IA errou (o quê, onde) | Como detectei | O que corrigi e por quê (causa e impacto) |
| --- | --- | --- |
| O primeiro teste (`e039c68`) tinha uma só reserva antes da falha | Na revisão do registro (Sonnet 5.5, app desktop); confirmei com a sabotagem `break`: suíte `OK` | Teste de três itens (`ea70c8a`). Causa: um único item não distingue "liberar tudo" de "liberar só a primeira". Impacto: rollback parcial passaria verde |
| Declarou "409 continua" como invariante sem teste que o verificasse | Revisão do registro (Sonnet 5.5): os testes eram do serviço, não do handler | Teste via `post_pedidos` (`ea70c8a`). Causa: invariante só afirmado. Impacto: uma mudança no handler poderia quebrar o 409 sem aviso |
| O plano de commits deixou o escopo para o último commit (`7dd40c5`, depois de `8cc20d6`) | Revisão do registro (Sonnet 5.5), confrontando horários do `git log` | Declarei no registro quando o escopo foi escrito e anexei o trecho da sessão. Causa: documentação tratada como etapa final. Impacto: o "antes" não é verificável só pelo repositório |
| No roteiro, tratou "sabotagem ou mutação" como provas equivalentes | Escore 74% idêntico antes e depois; nenhuma mutação cobre o rollback | Prova pela sabotagem; escore como limite. Causa: lista fixa de mutações. Impacto: o 74% seria evidência que não testa a mudança |
| Primeiro esboço de `liberar(sku, pedido_id)` pegava a quantidade de `estoque.reservas` | Na revisão do plano: `reservar` sobrescreve a chave em vez de somar | `liberar(sku, qtd, pedido_id)` com lista local. Causa: o dicionário perde quantidade com SKU repetido. Impacto: saldo devolvido errado |
| Processo: o roteiro pedia cópia `trabalho/`, mas a mudança foi em `caso/`; o commit foi tentado sem identidade git | `git diff`; erro `unable to auto-detect email address` | Mantive em `caso/` (o revisor roda `--codigo caso`); identidade só no repositório, igual à da AV2. Impacto: nenhum no código |

**Dependências novas (se houver) e checagem:** nenhuma; o diff não tem `import` novo além de `EstoqueInsuficiente` e `handlers`, já existentes no pacote.

| Medição do meu time | Meu desenho |
| --- | --- |
| Pergunta e decisão | A IA reduz o tempo de correção de bugs pequenos sem aumentar o retrabalho? Decide se o agente pode **propor** correções, em ambiente de teste, para bugs apontados pela suíte de regressão |
| Métrica primária e guardrail | Tempo até pronto e verificado (suíte verde), por bug. Guardrail: zero reabertura em 4 semanas e nenhum teste alterado sem revisão |
| Baseline, período e método | Baseline: mediana do tempo até verificado dos bugs pequenos corrigidos **sem IA** nas 4 semanas anteriores (histórico de PRs e issues), ainda a coletar. Depois, 4 semanas alternando bugs comparáveis com e sem IA, comparando medianas. A T1 da AV1.1 (correção, chat 9'45" × agente 3'55") só compara modos, não mede ganho sobre "sem IA" |
| Risco de manipulação e contramedida | Marcar "pronto" sem verificar, fatiar um bug para parecer rápido, editar o teste em vez do código. Contramedida: "pronto" exige a saída do teste anexada; tempo por bug; diff em testes exige revisão |
| Tarefa recorrente a automatizar e verificação exigida | Propor diff para falhas simples de teste (~2/semana, 30–50 min cada). Antes de aplicar: o teste que motivou falha sem o diff e passa com ele (como `e039c68` → `8cc20d6`); suíte verde numa cópia; diff só nos arquivos do bug; nenhum teste alterado. Sandbox só com leitura e testes, sem commit, segredos ou PR de fork; 5 min; 50 mil tokens. O dev da tarefa aprova. Parar se >30% das propostas forem descartadas em 2 semanas |

**Limites e condição para rever:** `pedido_id = "tmp-{usuario_id}"` é compartilhado entre pedidos do mesmo usuário: `liberar` remove a entrada de `reservas` de um pedido anterior com o mesmo SKU (o saldo fica certo). SKU repetido continua sobrescrevendo `reservas`. Pagamento recusado ainda deixa reservas (R2.3 só exige "não salva"). O teste do handler usa o estoque global do módulo (usuário 9001 para não colidir). A falha no 1º item não tem teste próprio (não há reserva a desfazer). A branch parte de `main`; R1.3/R1.5 estão no PR da AV2. Rever se `pedido_id` passar a ser único ou se o contrato exigir liberar reservas no pagamento recusado.

**Procedência/IA:** utilizada / ferramenta e modelo visíveis: Claude Code (extensão VS Code), Claude Opus 5.5, na execução; Claude app desktop, Claude Sonnet 5.5, na revisão do registro; tarefa delegada e contexto: explicar o enunciado e montar o roteiro; rascunhar os seis campos; escrever os testes e a correção; rodar suíte, verificações, sabotagens e mutação; redigir o PR e este registro; aplicar os pontos da revisão do registro. Ao Sonnet 5.5 (app desktop) delegei revisar o registro contra a rubrica; ele apontou escopo versionado depois, falta de teste com várias reservas e do 409, mapeamento asserção → regra, medição longa com baseline incompatível, procedência incompleta e alternativa fraca do modo. Contexto dado: `regras.md`, código do caso, enunciado e rubrica da AV3, meu registro AV1.6. Trecho aproveitado: os três testes (`e039c68`, `ea70c8a`) e a correção (`8cc20d6`) foram escritos pelo agente e aproveitados sem edição manual minha; `av3/PR.md` e este registro são rascunhos do agente que revisei; a medição é a da minha AV1.6, condensada. Minha verificação/intervenção: escolhi o B3 e o modo; aprovei o escopo; no plano, decidi deixar `pedido_id` compartilhado e SKU repetido como limites; forneci a AV1.6 (baseline, tarefa e números); pedi a revisão ao Sonnet 5.5, avaliei cada ponto com o Opus 5.5 (confirmei a sabotagem `break` passando verde) e mandei aplicar todos; conferi as saídas registradas. O raciocínio e a decisão registrados são meus.

**Revisão:** [x] modo; [x] escopo; [x] verificação; [x] erros da IA; [x] medição e automação; [x] procedência.

---

## Evidências

**Escopo antes do código (trecho da sessão, 27/10/2026).** O agente apresentou "Rascunho do escopo (seis campos)" com os campos acima e perguntou se eu aprovava. Respondi: "Escopo: OK; Modo: Agente no editor (Claude Code) com plano revisado por mim; Commits: Faça os commits você mesmo". Em seguida o agente criou a branch e o primeiro commit (`e039c68`).

**Plano revisado (cortes meus).** O agente apontou dois "pare e pergunte": `pedido_id` compartilhado e SKU repetido. Decidi não tratar e registrar como limite ("Siga a 1 com o recomendado"; "SKU duplicado no pedido não mexer e registrar como limite").

**Histórico.**
```
e039c68 18:08 teste de regressão de R2.2 (vermelho)
8cc20d6 18:18 desfaz reservas quando um item não tem estoque
7dd40c5 18:19 descrição do PR e registro
ea70c8a       cobre várias reservas e o 409 do handler; rotula asserções
```

**Saídas.**
```
# e039c68, só o primeiro teste
python -B testes/test_miniloja.py --codigo caso --existentes
AssertionError: 3 != 5          Ran 27 tests ... FAILED (failures=1)

# código de main + os três testes
AssertionError: 3 != 5 | 46 != 48 | 3 != 5      Ran 29 tests ... FAILED (failures=3)

# av3-b3-reserva
python -B testes/test_miniloja.py --codigo caso --existentes     Ran 29 tests ... OK
python -B testes/test_miniloja.py --codigo caso                  Ran 11 tests ... FAILED (failures=3)  # v08, v09, v10

# sabotagens (cópia fora do repositório)
liberar -> pass                 FAILED (failures=3)
break após o 1º liberar         AssertionError: 1 != 4   FAILED (failures=1)

# mutação (MINILOJA_TEST_CMD="python -B testes/test_miniloja.py --existentes --codigo caso -x")
Mutantes: 31 | mortos: 23 | sobreviventes: 8 | escore: 74%
```
