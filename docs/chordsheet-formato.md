# Formato Chord Sheet — SetSync

Especificação para gerar chord sheets **100% compatíveis** com o módulo `chordsheet` do SetSync.

Baseado no [Chord Sheet Maker](https://www.chordsheet.com/) (meta caracteres e estilo), com a extensão **`&`** (semi-pulsos) documentada abaixo.

| | |
|---|---|
| **Módulo** | `setsync.chordsheet` |
| **Versão** | `1.0.0` |
| **Código** | `chordsheet/parser.py`, `render.py`, `prefs.py`, `chord_token.py`, `export.py` |
| **Prompt IA (curto)** | [chordsheet-prompt-ia.md](./chordsheet-prompt-ia.md) |

---

## Índice

1. [Referência rápida](#1-referência-rápida)
2. [Payload JSON](#2-payload-json)
3. [Estrutura do `source`](#3-estrutura-do-source)
4. [Compassos e acordes](#4-compassos-e-acordes)
5. [Sintaxe de acordes](#5-sintaxe-de-acordes)
6. [Metadados (`meta`)](#6-metadados-meta)
7. [Preferências (`prefs`)](#7-preferências-prefs)
8. [Renderização](#8-renderização)
9. [Modelo interno](#9-modelo-interno)
10. [Exemplo completo](#10-exemplo-completo)
11. [Checklist e anti-padrões](#11-checklist-e-anti-padrões)
12. [Validação](#12-validação)
13. [API e integração SetSync](#13-api-e-integração-setsync)
14. [Referências](#14-referências)

---

## 1. Referência rápida

### Separadores — a distinção mais importante

| Escrita | Significado | Exemplo |
|---------|-------------|---------|
| **espaço** | Um **compasso** por token | `C D` → 2 compassos |
| **`_`** | Vários **pulsos** no mesmo compasso | `C_D` → 1 compasso, 2 tempos |
| **`&`** | Vários acordes no **mesmo tempo** (semi-pulso) | `C&D` → 1 compasso, 2 semi-pulsos |

```
C D       →  | C | D |           dois compassos
C_D       →  | C   D · · |       um compasso, 4/4
C&D       →  | C | D |             um compasso, metade cada
C&D_E     →  | C|D  E |           semi-pulso no 1º tempo + E no 2º
```

### Linhas especiais

| Sintaxe | Efeito |
|---------|--------|
| `# texto` | Comentário (ignorado) |
| `- Verso 1` | Rótulo / anotação |
| `-` (só hífen) | Espaço vertical extra |
| `= Refrão` | Seção com barra dupla `‖` |
| `: Parte A` | Seção só com rótulo |
| `+` / `+ Página 2` | Quebra de página |
| `; texto` | Literal (preserva espaços) |
| `<= rótulo` / `<- 5` | Rótulo flutuante no próximo compasso |
| `3:4` | Compasso local no próximo token |

### Simile e repetição

| Token | Efeito |
|-------|--------|
| `%` | Repete 1 compasso anterior |
| `%%` | Simile de 2 compassos |
| `%1` | Clona o último compasso |
| `%2` … `%4` | Clona N compassos ou simile de N |
| `(A B C D)x2` | Grupo com `\|:` … `:\|` e `×2` — **não duplica** compassos no parser |

### Proibido

| ✗ Errado | ✓ Correto |
|----------|-----------|
| `C \| D` | `C_D` |
| `C+D` | `C&D` |
| Repetir compassos à mão | `%` ou `( … )xN` |
| `D.C.` na linha dos acordes | Linha dedicada |
| `//` ou `\|` no acorde | `/` só para baixo (`C/G`) |

---

## 2. Payload JSON

Estrutura **obrigatória** para agentes de IA, API e persistência:

```json
{
  "module": "setsync.chordsheet",
  "version": "1.0.0",
  "source": "C Am F G\n= Refrão\nF G C Am",
  "meta": {
    "title": "Título",
    "artist": "Artista",
    "key": "C",
    "bpm": "120",
    "time_signature": "4/4",
    "capo": "",
    "style": ""
  },
  "prefs": {
    "bars_per_row": 4,
    "font_size": "M",
    "line_spacing": "normal",
    "align_chords": "auto",
    "maj7_style": "delta",
    "dim_style": "circle",
    "half_dim_style": "oslash",
    "show_footer": true,
    "bar_line_style": "tab",
    "tab_lines": 6,
    "tab_show_barlines": true
  }
}
```

**Regras:**

- `source` é sempre **string** (texto plano com `\n`).
- Se `source` estiver presente, o parser **reconstrói** o chart a partir dele (`payload_to_chart`).
- Round-trip: `parse_chart(source)` → `chart.to_source()` deve preservar a semântica.
- Campo no banco SetSync: `chordsheet_json` (ou legado em `leadsheet_json` com mesmo formato).

---

## 3. Estrutura do `source`

- **Uma linha** = uma linha lógica da partitura.
- Linhas vazias e `# …` são ignoradas.
- Tokens na mesma linha separados por **espaço** → cada token = um **compasso** (exceto grupos `( … )xN`).
- Parênteses não fechados → **continua na linha seguinte**.
- Na exportação (`to_source`), compassos consecutivos na mesma linha são reunidos: `C Am F G`.

### Prioridade de linha

O parser classifica cada linha nesta ordem:

1. Navegação isolada (`D.C.`, `fine`, …)
2. `-` vazio (espaçador)
3. `;` literal
4. `<=` / `<-` (pendente para o próximo compasso)
5. `- texto` (anotação)
6. `=` seção / `:` seção / `+` página
7. Linha de acordes (tokenização)

---

## 4. Compassos e acordes

### 4.1 Um acorde por compasso

```
C Am F G
```

→ 4 compassos; em 4/4 cada um mostra o acorde **centralizado**.

### 4.2 Vários pulsos no mesmo compasso — `_`

O **`_`** une segmentos no **mesmo compasso**, um acorde por **pulso inteiro**.

| Fonte (4/4) | `pulse_grid` | Prévia |
|-------------|--------------|--------|
| `C_D` | `[["C"], ["D"]]` | Colunas: C · · · / D ocupa 1º e 2º tempo; 3º e 4º = `·` |
| `C_D_E_F` | 4 pulsos | 4 colunas preenchidas |
| `C_*_*_D` | C, vazio, vazio, D | `*` dentro do segmento = pulso vazio |

> `C D` (espaço) = **dois compassos**. `C_D` = **um compasso**.

### 4.3 Semi-pulsos — `&` *(extensão SetSync)*

O **`&`** divide um **único pulso** em semi-pulsos.

| Fonte | `pulse_grid` | Prévia |
|-------|--------------|--------|
| `C&D` | `[["C", "D"]]` | Compasso dividido 50% + 50% |
| `C&D_E` | `[["C","D"], ["E"]]` | 1º tempo dividido + 2º tempo com E |
| `C&D_E&F_G` | 4 segmentos | Combina `&` e `_` |
| `C&*_D` | C + vazio no 1º tempo; D no 2º | |

**Serialização (round-trip):**

- Pulsos inteiros → `_`
- Semi-pulsos dentro de um pulso → `&` dentro do segmento

```
C&D      →  C&D
C&D_E    →  C&D_E
C_D      →  C_D
```

### 4.4 Compasso vazio — `*`

```
A * * D
```

→ Quatro **compassos**: A, vazio, vazio, D.  
Token `*` sozinho = um compasso sem acorde.

### 4.5 Baixo em branco — `*/`

```
*/G C
```

→ Fundamental omitida; exibe `/G` (manual chordsheet.com).

### 4.6 Simile

| Token | Comportamento no parser |
|-------|-------------------------|
| `%` | Simile 1 compasso |
| `%%` | Simile 2 compassos |
| `%1` | Clona o último compasso do histórico |
| `%2` | Clona 2 compassos; se histórico < 2, vira simile ×2 |
| `%4` | Clona 4 compassos; se histórico < 4, vira simile ×4 |

```
C Am F G
F % % %
```

### 4.7 Grupos repetidos

```
(A B C D)x2
(A B C D)2x
```

→ Marca `|:` no primeiro e `:|` no último compasso do grupo; `×N` no fechamento. **Não insere cópias extras** dos compassos.

Multilinha:

```
(A B %2
C_D E_F %2 )x3
```

### 4.8 Barras na linha

| Entrada | Efeito |
|---------|--------|
| `\|:` no token | Abre repetição |
| `:\|` no token | Fecha repetição |
| `\|:` `:` `:\|` separados | Normalizados |
| `\|` solto | Ignorado |
| `:` sozinho | Abre no **próximo** compasso |
| `:\|` sozinho | Fecha no compasso **anterior** |
| `\|\|` | Fecha `‖` no anterior; abre `‖` no próximo |

```
|: C Am F G :|
C Am F G:|
```

O **último compasso** da música recebe barra final `|]` automaticamente.

### 4.9 Voltas

```
(A B 1. C D 2. E F)
```

- `1.` / `2.` aplicam-se ao **próximo** token.
- `X` no início do token = indentação (alinha 2ª volta):

```
1. C Am F G
X 2. Dm G C C
```

### 4.10 Navegação

**Frases longas** — sempre em **linha própria**:

`D.C.` · `D.S.` · `D.C. al fine` · `D.C. al coda` · `D.S. al coda` ·  
`D.C. al coda con rep.` · `D.C. al coda senza rep.` · `D.S. al coda con rep.` · `fine`

**Símbolos** — linha própria **ou** token em linha de acordes:

| Símbolo | Significado |
|---------|-------------|
| `$` | Segno |
| `o` / `O` | Coda |

---

## 5. Sintaxe de acordes

Parser: `chordsheet/chord_token.py`.

### 5.1 Formas básicas

- Raiz `A`–`G` + `#` / `b`
- Qualidades: `m`, `maj7`, `m7`, `dim`, `aug`, `sus4`, `7`, `9`, `m7b5`, …
- Baixo: `C/E`, `Am/G`
- Sem acorde: `N.C.` / `NC`

### 5.2 Modificadores no token

| Sintaxe | Exemplo | Efeito |
|---------|---------|--------|
| Opcional | `Am?` | Parênteses na prévia |
| Batidas | `G,,,` | Vírgulas após o acorde |
| Anotação | `E7 "rit."` | Texto ao lado (token `"rit."` é fundido ao anterior) |
| Baixo em branco | `*/G` | Só baixo |

### 5.3 Grafia visual (`prefs`)

| Pref | Valores | Exemplo |
|------|---------|---------|
| `maj7_style` | `delta`, `MA7`, `maj7` | `Cmaj7` → `CΔ7` |
| `dim_style` | `circle`, `dim` | `Cdim` → `C°` |
| `half_dim_style` | `oslash`, `m7b5` | `Cm7b5` → `Cø7` |
| (automático) | — | `aug` → `+` |

O SetSync também aplica grafia do tom da cifra (`apply_chart_cifra_spelling`).

---

## 6. Metadados (`meta`)

| Campo | Padrão | Uso |
|-------|--------|-----|
| `title` | `"Sem título"` | Título na folha |
| `artist` | `""` | Artista (MAIÚSCULAS na prévia) |
| `key` | `""` | `tom de C` no cabeçalho |
| `bpm` | `""` | `♩=120` |
| `time_signature` | `"4/4"` | Compasso global (define colunas de pulso) |
| `capo` | `""` | Capotraste (editor) |
| `style` | `""` | Subtítulo |

Compasso local por compasso: `3:4` imediatamente antes do token.

---

## 7. Preferências (`prefs`)

| Campo | Valores | Padrão | Descrição |
|-------|---------|--------|-----------|
| `bars_per_row` | 1–8 | `4` | Compassos por linha |
| `font_size` | `M`, `S`, `XS` | `M` | Tamanho |
| `line_spacing` | `compact`, `normal`, `relaxed` | `normal` | Espaçamento |
| `align_chords` | `auto`, `left`, `center` | `auto` | Alinhamento |
| `maj7_style` | `delta`, `MA7`, `maj7` | `delta` | Maj7 |
| `dim_style` | `circle`, `dim` | `circle` | Diminuto |
| `half_dim_style` | `oslash`, `m7b5` | `oslash` | Meio-diminuto |
| `show_footer` | bool | `true` | Rodapé SetSync + data |
| `bar_line_style` | ver abaixo | **`tab`** | Estilo de barras |
| `tab_lines` | 3–8 | `6` | Linhas da pauta TAB |
| `tab_show_barlines` | bool | `true` | Barras verticais no modo tab |

### Estilos de barra (`bar_line_style`)

| Valor | Uso |
|-------|-----|
| **`tab`** | Pauta horizontal — **padrão SetSync**; voicings manuscritos |
| `regular` | Barras verticais clássicas |
| `none` | Sem barras |
| `grille` | Grade com borda (jazz manouche; prefira 8/linha) |
| `trackline` | Linha contínua sob os acordes |

**Barras entre compassos:** só o **primeiro** compasso de cada linha desenha barra esquerda; os seguintes usam a barra direita do anterior (evita `||` duplo). Entre semi-pulsos (`C&D`) há **uma** linha divisória.

---

## 8. Renderização

Comportamento em **4/4** (ajuste mental para outros compassos via `time_signature`):

| `source` | Layout na prévia |
|----------|------------------|
| `C` | Acorde centralizado |
| `C_D` | Grade 4 colunas; pulsos vazios = `·` |
| `C&D` | 2 colunas 50% + 50% no compasso |
| `C&D_E` | Grade compacta (só colunas com conteúdo) |
| `%` / `%%` | Símbolo simile centralizado |
| `*` | Compasso vazio |

### Anotações

- **Três colunas:** `- esq  centro  dir` (2+ espaços entre partes).
- **Rótulo curto** (≤40 chars, sem `  `) após `-` → caixa de seção.

---

## 9. Modelo interno

Após `parse_chart(source)`:

```
Chart
├── meta: ChartMeta
├── prefs: Prefs
├── sections: [(bar_index, título), …]
├── page_breaks: [bar_index, …]
└── bars: [Bar, …]
```

### `Bar` (campos principais)

| Campo | Descrição |
|-------|-----------|
| `chords` | Lista plana (um item por pulso; semi-pulsos como `"C&D"`) |
| `pulse_grid` | `list[list[str]]` — grade canônica de pulsos/semi-pulsos |
| `simile` / `simile_span` | Simile de N compassos |
| `volta` | `"1."`, `"2."`, … |
| `line_left` / `line_right` | `single`, `double`, `repeat-start`, `repeat-end`, `final` |
| `indent` | Contagem de `X` |
| `nav` / `annotation` | Navegação ou texto |
| `is_empty` | Compasso `*` |
| `repeat_times` | Multiplicador no `:|` |

Métodos úteis: `bar.get_pulse_grid()`, `bar.set_pulse_grid(grid)`.

---

## 10. Exemplo completo

```text
# Demo — SetSync + chordsheet.com
- All Meta Characters
= A
(A B C D)x2
A %1 C_D E
= B
(A B 1. C&D 2. E F)
- simile mark one bar
A B C %
- simile mark two bars
A B %%
+ A second Page
(A B %2
C_D E_F %2 )x3
- 4 bars repeat
( E F G A
%4)
- empty bars
A * * D
- optional chord
Am_B? C
- strokes
G,,, Am,B,
- blank bass
*/G C
- annotation
E7 "rit."
3:4 C Am F G
```

Fonte embutida: `chordsheet/examples.py` → `manual_meta`.

---

## 11. Checklist e anti-padrões

### Antes de retornar (agentes de IA)

1. `meta.key` alinhado com os acordes?
2. `meta.time_signature` correto?
3. Parênteses de grupo fechados?
4. Navegação em linhas dedicadas?
5. `%` usado onde há repetição?
6. Separadores corretos (espaço / `_` / `&`)?

### Checklist técnico

- [ ] JSON com `module`, `version`, `source`, `meta`, `prefs`
- [ ] `source` UTF-8, linhas bem formadas
- [ ] `parse_chart(source)` sem erro
- [ ] `render_chart_html(chart)` contém `cs-chart`
- [ ] Payload salvo com `module: setsync.chordsheet`

### Anti-padrões

| Erro | Correto |
|------|---------|
| `C D` querendo um compasso | `C_D` |
| `C+D` para semi-pulso | `C&D` |
| `C&D D` como um só compasso com C+D e D | `C&D_D` |
| `(A B)x2` escrito como `A B A B` | `(A B)x2` |
| `D.C.` junto com acordes | Linha só com `D.C.` |

---

## 12. Validação

### Python

```python
from chordsheet.parser import parse_chart
from chordsheet.render import render_chart_html

chart = parse_chart(data["source"], meta=data.get("meta"), prefs=data.get("prefs"))
html = render_chart_html(chart)
assert "cs-chart" in html
print(len(chart.bars), "compassos")
```

### CLI

```bash
python3 scripts/validate_chordsheet.py payload.json
# ou: cat payload.json | python3 scripts/validate_chordsheet.py
```

### Testes automatizados

```bash
python3 -m unittest chordsheet.test_meta -v
```

---

## 13. API e integração SetSync

| Método | Rota | Corpo → resposta |
|--------|------|------------------|
| POST | `/cifras/<id>/chordsheet/api/render` | `{source, meta, prefs}` → `{html}` |
| POST | `/cifras/<id>/chordsheet/api/transpose` | + `semitones` → `{html, meta}` |
| POST | `/cifras/<id>/chordsheet/api/save` | payload completo |
| GET | `/cifras/<id>/chordsheet/render` | HTML (play mode; query `semitones`) |

Transposição: `chordsheet/transpose.py` — altera acordes e `meta.key`.

Conversão legado: `chart_to_grade_flat()` em `chordsheet_bridge.py`.

---

## 14. Referências

- [Meta characters](https://www.chordsheet.com/manual/meta)
- [Style / bar lines](https://www.chordsheet.com/manual/style)
- [Prompt IA (curto)](./chordsheet-prompt-ia.md)
- Editor SetSync → **Exemplos** → `manual_meta`, `galeria_grafica`

### Diferenças em relação ao chordsheet.com

| Recurso | chordsheet.com | SetSync |
|---------|----------------|---------|
| Semi-pulsos (`&`) | Não documentado | **Suportado** (`C&D`, `C&D_E`) |
| Padrão de barra | Regular | **TAB** |
| Barras duplas entre compassos | — | Uma barra por fronteira |

---

*Em caso de divergência entre este documento e o comportamento real, prevalece o código em `chordsheet/`.*
