"""Exemplos inspirados no manual do Chord Sheet Maker."""

EXAMPLES = {
    "manual_meta": {
        "title": "★ Manual — Meta Characters (oficial)",
        "meta": {"title": "All Meta Characters", "key": "C", "bpm": "120"},
        "source": """# Fonte: chordsheet.com/manual/meta
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
3:4 C Am F G""",
    },
    "manual_basics": {
        "title": "Manual — Basics (seções e texto)",
        "meta": {"title": "Titles and Sections", "key": "G"},
        "source": """: Parte A (só rótulo)
G Em C D
= Parte B (rótulo + ||)
Am D7 G G
-
- linha em branco acima (espaço extra)
<= A
<- 5
C Am F G
; literal   com   espaços
- três colunas  centro  direita""",
    },
    "galeria_grafica": {
        "title": "★ Galeria — todas as possibilidades gráficas",
        "meta": {
            "title": "Galeria de Notação",
            "artist": "SetSync Demo",
            "key": "Eb",
            "bpm": "128",
            "time_signature": "4/4",
            "style": "jazz / demo",
        },
        "source": """# Galeria gráfica — carregue no dropdown "Exemplos"
# Comentários (#) não aparecem na folha.

- Cabeçalho: tom, BPM, título, artista (campos acima do editor)

: Parte A (rótulo sem barra dupla — só :)
Ebmaj7 Bb7 Ebmaj7 Bb7

= Parte B (rótulo + barra dupla de seção)
Cm7 Fm7 Bb7 Ebmaj7

- Compassos divididos (_), simile (%) e repetição (%N)
G Em C_D G
Am % %% %1

- Ritornello (|: :|) — abre e fecha a linha
|: C Am F G :|

- Primeira e segunda volta (1. 2.) + indentação (X)
1. C Am F G
X 2. Dm G C C

- Compassos vazios (*) e acorde N.C.
Eb * * N.C.

- Grupo repetido (A B C D)x2
(F G Am Bb)x2

- Segno ($) e coda (o / O)
$ C Am F G
D A D A o
- ponte instrumental
O C Am F G

- Instruções de navegação (cada uma em linha própria)
D.C.
D.S.
D.C. al fine
D.C. al coda
D.S. al coda
D.C. al coda con rep.
D.C. al coda senza rep.
D.S. al coda con rep.
fine

+ Página 2 — Refrão
- quebra de página (+) com rótulo opcional
Ab Bb Eb Cm
Ab Bb Eb Eb""",
    },
    "basico": {
        "title": "Progressão básica",
        "meta": {"title": "Exemplo básico", "artist": "Demo", "key": "C", "bpm": "120"},
        "source": """= Intro
C Am F G
= Verso
C Am F G
Am F C G
= Refrão
F G C Am
F G C C""",
    },
    "compassos_divididos": {
        "title": "Compassos divididos (_)",
        "meta": {"title": "Split bars", "key": "G", "bpm": "96"},
        "source": """= Verso
G Em C_D G
Am D7 G %""",
    },
    "semi_pulsos": {
        "title": "Semi-pulsos (&)",
        "meta": {"title": "Semi-pulsos", "key": "C", "bpm": "100", "time_signature": "4/4"},
        "source": """= Demo semi-pulsos (extensão SetSync)
C&D
C&D_E
C&D_E&F_G
G C&D Am F""",
    },
    "simile": {
        "title": "Simile e repetição (%)",
        "meta": {"title": "Simile", "key": "C"},
        "source": """C Am F G
F % % %
C G Am F
%1 %1""",
    },
    "secoes": {
        "title": "Seções e quebra de página",
        "meta": {"title": "Autumn Sketch", "artist": "Demo", "key": "Eb", "bpm": "128"},
        "source": """= Intro
Eb Bb7 % %
+ Verso
Cm Ab Bb Eb
= Refrão
Ab Bb Eb Cm""",
    },
    "navegacao": {
        "title": "Ritornello e navegação (|: :| D.C. coda)",
        "meta": {"title": "Comfortably Numb (demo)", "artist": "Pink Floyd", "key": "Bm"},
        "source": """= intro
Bm
= verse
$ Bm A G_Em Bm
|: D A D A
C G C G :|
= chorus
A C_G D D o
= interlude
- solo de guitarra
D A D A
C G C G
= chorus
A C_G D D
D.S. al coda con rep.
= coda
O Bm A G_Em Bm
fine""",
    },
}
