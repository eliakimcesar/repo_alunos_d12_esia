# Registro individual — AV1.4

**Limite: uma página, incluindo evidências essenciais.** Estudante: Eliakim — Data: 31/10/2026
Origem: `caso/legado/` (commit `1a49643`); modalidade: **[x] execução/leitura real, feita por agente no meu ambiente** / [ ] resposta simulada. Caminhos relativos a `caso/legado/`.

| # | Afirmação | Trecho | Contraevidência buscada | Status |
| --- | --- | --- | --- | --- |
| 1 | Ingestão = `ingest.run`, disparada por `jobs ingest` e `jobs refresh` (2 últimos anos); o cron chama os dois. | `ingest.py:43`; `jobs.py:10,22-23,28-29`; `rodar_tudo.sh:6,11` | grep `__main__`/`argparse`/`ingest.`: única entrada é `jobs.py:36` | Confirmada (no repo) |
| 2 | **Não só a ingestão:** 4 escritores (REPLACE, `exportado=1`, zera citações < 0, SQL arbitrário via `jobs sql`). O REPLACE do `refresh` desfaz `exportado` e `corrigir_anos`. | `ingest.py:17`; `exporta_parceiro.py:11`; `jobs.py:12,32`; `corrigir_anos.sql:2` | grep `trabalhos` em .py/.sql; ordem do cron executada: `exportado` 120→79, 2 obras com `ano=0` voltam | Confirmada; fora do repo: incerta |
| 3 | Trabalhos: filtro `concepts.id`; área = `concepts[0]`, que **mistura níveis** (nível 1: 98, nível 0: 36, nível 2: 27 no cache). Autores: `x_concepts` nível 0 de maior score; instituição de `last_known_institution`. | `ingest.py:7,15,39`; `instituicoes.py:10,22-26` | Contagem de níveis e da ordem por score em `.cache/*.json` | Confirmada no cache; ordem garantida pela API: incerta |
| 4 | 5 `rel_*`; só os de `config.ini:21` rodam (`rel_conceitos` falha). O cron dispara `top_instituicoes` e `exporta_parceiro`; `evolucao_anual` e `areas_autores` estão habilitados, mas fora do cron. | `relatorios.py:7-38,42-44`; `config.ini:21`; `rodar_tudo.sh:9-10` | grep acha 0 chamadas diretas, mas o `getattr` em `relatorios.py:44` chama, logo "nunca é chamado" é falso | Confirmada |
| 5 | Padrão `dev` (`config.ini:2`); `[producao]` (`config.ini:15-18`) só vale com `CIENTO_AMBIENTE=prod`, mas o cron exporta `CIENTO_AMBIENT` e roda em **dev**. `OFFLINE=1` deixa o cron **inteiro** só no cache. `por_pagina` não é lida (200 fixo). | `config.py:11,15-16`; `rodar_tudo.sh:3-4`; `cliente.py:26-33`; `ingest.py:8` | Execução: `CIENTO_AMBIENT=prod` → `dev 50 saida_parceiro`; `CIENTO_AMBIENTE=prod` → `prod 500 /mnt/...`; grep `por_pagina`: só `config.ini:6`, 0 leituras no código Python | Confirmada no código; servidor: incerta |

**Resposta do assistente que parecia certa e estava errada:** na primeira versão do plano, o assistente classificou `/concepts`→`/topics` como **codemod** (troca de nomes). **Como foi refutada:** `conceitos.salvar` lê `c["level"]` e `ancestors` (`conceitos.py:8-12`), campos que um topic não tem (ele tem subfield/field/domain). Trocar a rota quebra a gravação, e a mudança exige decisão de esquema, por isso virou a fatia 2b (humana). Quem apontou foi a revisão por IA; o trecho confirma. Outro erro real, refutado ao executar: `python -m cienciometria.relatorios` sai com exit 0 sem fazer nada, porque não tem `__main__`.

**Caracterização antes de mudar** (cópia, banco novo, `CIENTO_OFFLINE=1 python -B -m cienciometria.jobs …`, todos exit 0):

```text
ingest → 120 trabalhos | enriquecer → 30 autores | areas_autores → Ciência da Computação 30
top_instituicoes: Federal de Teste 64 | Exemplo do Recife 64 (empate) | Exemplolândia 58 | Imaginário 46 | Fictício 10
evolucao_anual (trab/cit): 0: 2/21 | 2018: 22/1797 | 2019: 18/1781 | 2020: 21/2003 | 2021: 18/1465 | 2022: 18/1374 | 2023: 21/2400
exporta_parceiro CSV: instituicao,trabalhos,citacoes | …Teste,64,7811 | …Recife,64,8081 | …Exemplolândia,58,6359 | …Imaginário,46,5286 | …Fictício,10,814 | …Politécnico Ficcional,5,570
conceito_principal: Aprend. de Máquina 31 | Eng. de Software 28 | Ciência da Computação 23 | Mineração de Dados 20 | IA 18
```

| Fatia | Mudança | Codemod ou humana? | Verificação |
| --- | --- | --- | --- |
| 0a | `CIENTO_AMBIENT`→`CIENTO_AMBIENTE` no cron | Humana: ativa prod = pasta `/mnt/compartilhado/parceiro`, 500 páginas e cache agressivo | `config.ambiente()`=`prod` no cron; os 3 efeitos aceitos pelo mantenedor |
| 0b | `refresh` antes de `corrigir_anos` e de `exporta_parceiro` | Humana | Pipeline completo: `exportado`=120 e 0 obras com `ano<1900` |
| 1 | `mailto` → `api_key` na URL e fora do User-Agent; nenhuma das duas entra no hash do cache (`cliente.py:16,21,35`) | Humana (segredo) + script que re-chaveia o cache atual | Saídas offline idênticas à base acima |
| 2a | Nomes `concepts.id`→`topics.id`, `/concepts`→`/topics` | Codemod (só nomes; URL muda, exige cache novo) | grep sem nomes antigos; teste novo de `montar_url` |
| 2b | Valor `C9000001` (`config.ini:9`) sem `T…` 1:1; `conceitos.salvar` lê `level`/`ancestors` (`conceitos.py:8-12`); `last_known_institutions` é lista, pode vir vazia | Humana (topic(s), esquema, regra para vazio/múltiplas) | Obras ingeridas × 120; nenhum `IndexError` com lista vazia |
| 3 | `concepts[0]`→`primary_topic`; nível da "área" (domain/field/subfield/topic) | Humana | `conceito_principal` × base acima; diferenças (esperadas) registradas e aceitas |
| 4 | `x_concepts` (será removido) → `group_by=topics.id`; CSV do parceiro com colunas e ordem fixas (`exporta_parceiro.py:7`) | Humana (acordo com parceiro) | `areas_autores` × base; CSV byte a byte igual |

**Limite da leitura e condição para reabrir:** não cobre o crontab e as variáveis reais do servidor, outros escritores do SQLite, o parceiro que lê o CSV, nem respostas reais de `/topics` (só a doc). Chamadas por `getattr` escapam de grep. Reabro uma resposta se surgir outro agendamento ou variável, outro escritor ou uma resposta da API diferente da doc. Fontes: [deprecações do OpenAlex](https://help.openalex.org/api/deprecations.md); [chaves de API obrigatórias desde 13/02/2026](https://groups.google.com/g/openalex-users/c/rI1GIAySpVQ).

**Procedência/IA:** Claude Code (VS Code), Claude Opus 5.5. Fez a leitura, as buscas, as execuções numa cópia offline, a consulta à doc e a redação. A revisão foi feita por outra sessão de IA (Claude, Cowork), que apontou as correções aplicadas; quem as aplicou foi o Claude Code. Eu defini a tarefa, a entrega e a branch e levei a revisão de uma sessão para a outra. Reexecutei `relatorio top_instituicoes`: sem `ingest`, saiu vazio com exit 0; depois de `jobs ingest`, bateu com a base. O resto não reexecutei. São minhas as decisões de escopo, entrega e aceite.

**Revisão:** [x] cinco respostas com trecho; [x] uma refutação; [x] caracterização; [x] plano em fatias; [x] até uma página.
