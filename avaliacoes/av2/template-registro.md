# Registro individual — AV2

Limite: duas páginas de análise + anexo técnico curto.Estudante: Eliakim — Data: 22/10/2026 — Caminho: B (MiniLoja), branch `av2-refatoracao`

**Escopo (antes da mudança):** objetivo: trocar os ifs aninhados de `calcular_total` por `FRETE_POR_UF`/`TAXA_POR_UF` (sem uso); pode tocar: só `calculo.py`; não pode: assinatura, `descontos.py`, `testes/`, `regras.md`; invariantes: saída `==` no golden master, inclusive bugs `> 200` e `round`; pronto: golden master igual, 26 existentes OK, verificações 8/3; pare se: a IA quiser corrigir bug, mudar assinatura ou tocar outro arquivo.

**Plano do agente: o que cortei:** cortei D1 (remover `desconto_aplicado`), D2 (dicionário de cupons, o que retirou E3) e D3 (docstring); mantive D4 (`FRETE_PADRAO`/`TAXA_PADRAO`) e não troquei `total + total*taxa` por `total*(1+taxa)` (difere em float). `> 200` e `round` foram reportados, não corrigidos.

**Comportamento preservado:** golden master (`av2/golden_master.py`) gravado em `a90afab`, antes da refatoração (`8b7c937`). São 1050 entradas: 15 carrinhos (vazio, 1,20, 199,99/200/200,01, descontos cruzando 200, vários itens) × 7 cupons × 5 UFs × flag NATAL, comparadas com `repr` e `!=`. `golden_master.py comparar` → 0 diferenças; existentes 26 OK; verificações 8/3. Sabotar `>=` numa cópia gera 40 diferenças.

| Teste (regra) | Prova de que falharia | Resultado |
| --- | --- | --- |
| Fronteira 200, exato e via NATAL (R1.3/R1.6 → 210,00) | `223.55 != 210.0` em `cf639eb`; sabotagens `>`, 200→300 | Vermelho → verde (`70825da`); mortas |
| Arredondamento (R1.5: 14,805 → 14,81) | `14.8 != 14.81`; oráculo `Decimal` (640.016 entradas); sabotagens `HALF_EVEN`, 1 casa, `Decimal(preco)` do float | Vermelho → verde; mortas (a do float sobrevive à suíte existente) |
| Frete RJ e NATAL 20% (R1.3/R1.2) | Sobreviviam à mutação inicial (18 mutantes, 3 sobreviventes); sabotagens RJ, NATAL 21%, NATAL sem campanha | Mortas pelo contrato; sobrevivem à existente |

**Mutantes sobreviventes:** `av2/sabotagem.py` aplica 24 sabotagens numa cópia de `caso/`. O contrato mata 23 (96%) e a suíte existente, 19 (79%). O sobrevivente, `if desconto_aplicado:` invertido, é equivalente: o corpo é só `pass` (mantido por eu ter cortado D1).

**Documentação/ADR:** a ADR-002 registra a correção de R1.3/R1.5 feita depois dos testes vermelhos. `Decimal` vai na conta toda porque só no fim divergia do oráculo em 433 entradas, contra 0. Ela também explica as 70 mudanças do golden master (40 na fronteira, 30 em empates de PE), as alternativas e a condição para rever. A ADR-001 registra como lacuna, sem teste nem correção, que `qtd ≤ 0` e preço negativo não têm regra: `qtd = -1` dá `-38.95` e sobe o estoque de 50 para 51.

**O que a IA errou:** (1) propôs `Decimal` só no arredondamento final; o diferencial mostrou 433 divergências, porque o float acumulado já erra (14,805 vira 14,8049…). (2) A ADR-001 negava entrada inválida no golden master, mas `vazio` existe; detectei relendo `CARRINHOS`. (3) `sabotagem.py` não copiava `testes_existentes/` (barrado na linha de base), quebrava em cp1252 e usava trecho repetido; foi corrigido. À parte (bug da ferramenta do pacote, não da IA): `mutacao_manual.py` falha no Windows (`shlex` remove `\`); contornei com `MINILOJA_TEST_CMD`.

**Limite e condição para rever:** (a) o oráculo e os esperados têm o mesmo autor, reveria se um cálculo independente divergir; (b) o diferencial cobre só 1 item e preço até R$ 400; (c) `qtd ≤ 0`, preço negativo e minúsculas não têm regra, e reveria quando o contrato definir; (d) `mutacao_manual.py` ficou inutilizável, e 24 sabotagens manuais não esgotam falhas; (e) o escopo da correção foi decidido durante o trabalho (ADR-002), não em seis campos prévios; (f) Python 3.14.0, não 3.12.3; (g) R2–R4 ficaram fora.

**Procedência/IA:** Claude Code (VS Code), Claude Opus 5.5 (`claude-opus-5-5`), com commits `Co-Authored-By`. Delegado: plano, scripts e testes de `av2/`, oráculo, correção, rascunhos das ADRs e do registro, com `CLAUDE.md`, `regras.md`, código e enunciado como contexto. Aproveitado: `av2/` e o diff de `calculo.py`, depois de revisados. Minha intervenção: escrevi os seis campos; cortei D1–D3; escolhi corrigir em vez de `expectedFailure`; atualizei o snapshot pelo contrato; registrei a lacuna com `qtd = -1` explícito; conferi os cenários sugeridos e cenários para incluir. O raciocínio e a decisão registrados são meus.

**Anexo.** `git diff --stat 2c2fc89..HEAD`: 8 arquivos, +1448/−35. Commits: `a90afab` golden master · `8b7c937` refatoração (+6/−27) · `cf639eb` testes vermelhos + ADR-001 · `70825da` correção (`calculo.py` +16/−11, `test_calculo.py` +3/−1) · `6cb1388` golden master + ADR-002 · `02d5857` sabotagem. Reprodução: `git checkout cf639eb && python -B av2/test_contrato.py` (3 FAIL) → `git checkout 02d5857` (17 OK) → `python -B av2/sabotagem.py` (23/24). Testes: `av2/test_contrato.py` (17 casos, conta à mão em cada comentário); dois trechos:
```python
def test_fronteira_exatamente_200_tem_frete_gratis(self):
    # 200 >= 200 -> frete 0; 200 × 1,05 = 210,00
    self.assertEqual(self.total([item(200.0)],None,"PE"), 210.0)

def test_arredondamento_meio_para_cima(self):
    # 1,20 + 12,90 = 14,10; ×1,05 = 14,805 -> 14,81 (meio acima)
    self.assertEqual(self.total([item(1.2)], None, "PE"), 14.81)
```

**Revisão:** [x] escopo; [x] comportamento; [x] testes com prova; [x] documentação; [x] erros da IA; [x] limite.
