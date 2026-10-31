# Registro individual — AV1.4

**Limite: uma página, incluindo evidências essenciais.** Estudante: Eliakim — Data: 31/10/2026
Origem: repositório desconhecido liberado no bloco (`caso/legado/`, commit `1a49643`); modalidade: **[x] execução/leitura real, feita por agente (Claude Code) no meu ambiente** / [ ] resposta simulada. Caminhos relativos a `caso/legado/`.

| # | Afirmação | Trecho (arquivo:linha) | Contraevidência buscada | Status |
| --- | --- | --- | --- | --- |
| 1 | A ingestão começa em `ingest.run`, disparada por `jobs ingest` e por `jobs refresh` (reingere os 2 últimos anos); o cron chama os dois. | `cienciometria/ingest.py:43`; `cienciometria/jobs.py:10,22-23,28-29`; `scripts/rodar_tudo.sh:6,11` | `grep -rn "ingest\.\|__main__\|argparse"`: único ponto de entrada é `jobs.py:36` | Confirmada (no repo) |
| 2 | **Não é só a ingestão:** 4 pontos escrevem em `trabalhos` (INSERT OR REPLACE, `exportado=1`, zera citações negativas, SQL arbitrário via `jobs sql`). O REPLACE do `refresh` desfaz `exportado` e o `corrigir_anos`. | `ingest.py:17`; `exporta_parceiro.py:11`; `jobs.py:12,32`; `scripts/corrigir_anos.sql:2` | `grep -rn "trabalhos"` em .py/.sql; execução na ordem do cron: `exportado` 120→79 e 2 trabalhos com `ano=0` voltam após `refresh` | Confirmada; escritas fora do repo: incerta |
| 3 | Trabalhos: filtro `concepts.id`; área principal = `concepts[0]` (assume ordem da API). Autores: `x_concepts` nível 0 de maior score; instituição de `last_known_institution`. `validar_instituicao` sempre retorna `True`. | `ingest.py:7,15,39`; `instituicoes.py:10,14-18,22-26` | `grep -rn "concept\|level\|score"`; formato real conferido num JSON de `.cache/` | Confirmada |
| 4 | 5 funções `rel_*`, chamadas **dinamicamente** por `getattr` (grep da chamada não acha nada); só as listadas em `config.ini` rodam (`rel_conceitos` existe mas falha). O cron dispara `top_instituicoes` e `exporta_parceiro`. | `relatorios.py:7-38,42-44`; `config.ini:21`; `rodar_tudo.sh:9-10` | `grep "rel_top_instituicoes("` = 0 chamadas (derrubaria "nunca é chamado"); `jobs relatorio conceitos` → `ValueError: relatório desabilitado` | Confirmada |
| 5 | `config.py` usa `[producao]` com `CIENTO_AMBIENTE=prod`, mas o cron exporta `CIENTO_AMBIENT` (sem E): **o agendamento roda em `dev`** (50 páginas, CSV em `saida_parceiro`). `CIENTO_OFFLINE=1` faz o `refresh` nunca buscar citações novas. | `config.py:11,15-16`; `rodar_tudo.sh:3-4`; `cliente.py:26-33` | Execução: `CIENTO_AMBIENT=prod` → `dev 50 saida_parceiro`; `CIENTO_AMBIENTE=prod` → `prod 500 /mnt/compartilhado/parceiro` | Confirmada no código; ambiente do servidor: incerta |

**Resposta do assistente que parecia certa e estava errada:** para a caracterização, o assistente sugeriu `python -m cienciometria.relatorios <nome>` e disse que o `.cache/` bastava para rodar sem rede. **Como foi refutada:** executado, o comando sai com código 0 e **nenhuma saída** (falso sucesso), porque `relatorios.py` não tem `__main__`; a entrada real é `jobs.py:1,36` (`jobs relatorio <nome>`). Sem `CIENTO_OFFLINE=1`, cache com mais de 24 h faz o cliente tentar a rede (`cliente.py:26-29`).

**Caracterização antes de mudar (comando e saída gravada):** cópia do legado, banco novo, sem rede, Python 3.14.0; cada comando com `[exit=0]`. Saída completa também em `caracterizacao-av1-4.txt` (mesma pasta); a essencial:

```text
$ CIENTO_OFFLINE=1 python -B -m cienciometria.jobs ingest      → 120 trabalhos
$ ... jobs enriquecer                                          → 30 autores
$ ... jobs relatorio top_instituicoes      # empate 64/64: ordem não garantida
Universidade Federal de Teste 64 | Universidade Exemplo do Recife 64 | Universidade de Exemplolândia 58
Centro de Pesquisa Imaginário 46 | Instituto Fictício de Tecnologia 10
$ ... jobs relatorio evolucao_anual   (ano: trabalhos/citações)
0: 2/21 | 2018: 22/1797 | 2019: 18/1781 | 2020: 21/2003 | 2021: 18/1465 | 2022: 18/1374 | 2023: 21/2400
$ ... jobs relatorio areas_autores                             → Ciência da Computação 30
$ ... jobs relatorio exporta_parceiro ; cat saida_parceiro/trabalhos_por_instituicao.csv
instituicao,trabalhos,citacoes
Universidade Federal de Teste,64,7811 | Universidade Exemplo do Recife,64,8081 | Universidade de Exemplolândia,58,6359
Centro de Pesquisa Imaginário,46,5286 | Instituto Fictício de Tecnologia,10,814 | Instituto Politécnico Ficcional,5,570
$ sqlite: SELECT conceito_principal, COUNT(*) FROM trabalhos GROUP BY 1   (base da classificação)
Aprendizado de Máquina 31 | Engenharia de Software 28 | Ciência da Computação 23 | Mineração de Dados 20 | Inteligência Artificial 18
```

| Fatia do plano | Mudança (API atual do OpenAlex, doc oficial de deprecações) | Mecânica (codemod) ou decisão humana? | Verificação da fatia |
| --- | --- | --- | --- |
| 0 | Corrigir `CIENTO_AMBIENT` e ordem `exporta`→`refresh` antes de migrar | Humana (confirmar com o mantenedor) | `config.ambiente()` = `prod` no cron; `exportado` não cai após `refresh` |
| 1 | `mailto` ignorado desde fev/2026 → `api_key` (`cliente.py:16`), fora do hash do cache (`cliente.py:21`) | Humana (guarda do segredo) + mecânica | Rodar offline: as 6 saídas acima idênticas |
| 2a | Renomear nomes de campo/rota: `concepts.id`→`topics.id`, `/concepts`→`/topics`, `last_known_institution`→`last_known_institutions[0]` | Codemod (só os nomes) | `grep` sem nomes antigos; código importa e roda offline |
| 2b | Mapear **valores e esquema**: `C9000001` (`config.ini:9`) não tem `T…` equivalente 1:1; `conceitos.salvar` lê `level` e `ancestors` (`conceitos.py:8-12`), que topics não tem (tem subfield/field/domain) | **Humana** (escolher topic(s) e novo esquema da tabela `conceitos`) | Contagem de trabalhos ingeridos com o novo filtro × 120 da base, diferenças justificadas |
| 3 | `concepts[0]`→`primary_topic`; escolher o nível de "área" (domain/field/subfield/topic); `nivel_minimo_conceito` perde sentido | **Humana** | Distribuição de `conceito_principal` gravada acima × nova, diferenças registradas |
| 4 | `x_concepts` (será removido) → `group_by=topics.id` nos trabalhos do autor; destino das tabelas `conceitos*`; CSV do parceiro (`exporta_parceiro.py:7`) não pode mudar colunas/ordem | **Humana** (regra de negócio, acordo com parceiro) | `areas_autores` × base gravada; CSV byte a byte igual ao gravado (salvo mudança acordada) |

**Limite da leitura e condição para reabrir uma resposta:** não cobre o crontab e as variáveis reais do servidor, scripts externos que escrevam no SQLite, o parceiro que lê o CSV, nem respostas reais de `/topics` (só a doc). A chamada dinâmica (`getattr`) escapa de grep simples; `requirements.txt` pede `requests`, que o código não usa. Reabro uma resposta se aparecer outro agendamento/variável de ambiente, outro escritor do banco ou uma resposta da API diferente da documentação.

**Procedência/IA:** ferramenta e modelo visíveis: Claude Code (extensão VS Code), Claude Opus 5.5; tarefa delegada e contexto: leitura do legado, buscas de contraevidência, execuções numa cópia offline, consulta à doc de deprecações do OpenAlex e redação deste registro, com acesso ao repositório; trecho aproveitado: respostas, refutação, caracterização e plano acima; minha verificação/intervenção: defini a tarefa, o formato de entrega e a branch; submeti o registro a revisão e pedi as correções apontadas (divisão da fatia 2, linhas de base de `areas_autores`/CSV/classificação, saída colada no registro, esta declaração). Reexecutei por conta própria, em `caso/legado`, `CIENTO_OFFLINE=1 python -B -m cienciometria.jobs relatorio top_instituicoes`: a primeira tentativa saiu **vazia com exit 0**, porque o banco recém-criado não tinha dados (o relatório só lê o banco; quem o preenche é o `ingest`). Depois rodei `jobs ingest` (120 trabalhos) e o relatório outra vez: bateu com a caracterização (64/64/58/46/10). Os demais comandos e trechos não reexecutei nem abri; para eles, a conferência se apoia nas saídas gravadas acima. A leitura e o raciocínio técnico são do agente; minhas são as decisões de escopo, de entrega e de aceite deste registro.

**Revisão:** [x] cinco respostas com trecho; [x] uma refutação; [x] caracterização (com linha de base de todas as verificações do plano); [x] plano em fatias; [ ] até uma página (a saída colada aumentou o registro).
