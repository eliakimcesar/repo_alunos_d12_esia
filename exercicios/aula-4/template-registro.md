# Registro individual — AV1.4

**Limite: uma página, incluindo evidências essenciais.** Estudante: Eliakim — Data: 31/10/2026 Origem: `caso/legado/` (commit `1a49643`); modalidade: execução

| # | Afirmação | Trecho | Contraevidência | Status |
| --- | --- | --- | --- | --- |
| 1 | Ingestão: `ingest.run`, via `jobs ingest` e `jobs refresh`; cron chama os dois | `ingest.py:43`; `jobs.py:10,23,29`; `rodar_tudo.sh:6,11` | grep `__main__`: só `jobs.py:36` | Confirmada |
| 2 | 4 escritores em `trabalhos`; o REPLACE do `refresh` zera `exportado` | `ingest.py:17`; `exporta_parceiro.py:11`; `jobs.py:12,32`; `corrigir_anos.sql:2` | grep `trabalhos`; ordem do cron: `exportado` 120→79 | Confirmada; fora do repo: incerta |
| 3 | Área = `concepts[0]` (níveis misturados: 98/36/27); autores por `x_concepts` nível 0 | `ingest.py:7,15`; `instituicoes.py:22-26` | Níveis contados no `.cache/` | Confirmada no cache; API: incerta |
| 4 | 5 `rel_*` via `getattr`; só os habilitados rodam; cron dispara 2 | `relatorios.py:44`; `config.ini:21`; `rodar_tudo.sh:9-10` | grep: 0 chamadas diretas, mas o `getattr` chama | Confirmada |
| 5 | Cron exporta `CIENTO_AMBIENT` (typo) e roda em **dev**; `OFFLINE=1` deixa tudo no cache | `config.py:11`; `config.ini:2,15-18`; `rodar_tudo.sh:3-4` | Com `CIENTO_AMBIENT=prod`, ambiente continua `dev` | Confirmada; servidor: incerta |

**Resposta do assistente que parecia certa e estava errada:** classificar `/concepts`→`/topics` como codemod. **Como foi refutada:** `conceitos.py:8-12` lê `level`/`ancestors`, que topics não têm (apontado pela revisão por IA).

**Caracterização antes de mudar** (`CIENTO_OFFLINE=1 python -B -m cienciometria.jobs …`, banco novo, exit 0):

```text
ingest 120 | enriquecer 30 | top_instituicoes: Teste 64, Recife 64, Exemplolândia 58, Imaginário 46, Fictício 10
CSV parceiro: as mesmas 5 + Politécnico 5 | areas_autores: Ciência da Computação 30
```

| Fatia | Mudança | Codemod ou humana? | Verificação |
| --- | --- | --- | --- |
| 0a | Corrigir `CIENTO_AMBIENT` | Humana (ativa `/mnt`, 500 páginas) | `ambiente()`=`prod` |
| 0b | `refresh` antes do export | Humana | `exportado`=120 |
| 1 | `mailto`→`api_key`, fora do hash (`cliente.py:16,21,35`) | Humana + script | Saída = base (salvo empates) |
| 2a | `concepts.id`→`topics.id` | Codemod | grep vazio; teste novo |
| 2b | ID `C9000001`, esquema, lista vazia | Humana | Sem `IndexError` |
| 3 | `concepts[0]`→`primary_topic` | Humana | Diferenças aceitas |
| 4 | `x_concepts`→topics; CSV fixo | Humana | CSV = base (salvo empates) |

**Limite da leitura e condição para reabrir:** não cobre o servidor real, escritores externos nem respostas reais de `/topics`. Reabro se surgir outro agendamento ou resposta diferente da [doc](https://help.openalex.org/api/deprecations.md).

**Procedência/IA:** Claude Code (Opus 5.5) fez a leitura, as execuções e a redação; outra sessão de IA (Claude, Cowork) revisou. Reexecutei `top_instituicoes`, que bateu com a base. Escopo e aceite são meus.

**Revisão:** [x] cinco respostas com trecho; [x] uma refutação; [x] caracterização; [x] plano em fatias; [x] até uma página.
