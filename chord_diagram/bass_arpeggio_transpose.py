"""Transposição de arpejos de baixo — formas do manual (raiz em Dó) para qualquer tom."""

from __future__ import annotations

from chord_diagram.theory.chord_parser import chord_theory_block
from chord_diagram.theory.pitch import note_to_pc, pc_to_spelling

STRING_OPEN_PC = {'E': 4, 'A': 9, 'D': 2, 'G': 7}
TUNING_LOW_TO_HIGH = ('E', 'A', 'D', 'G')


def _semitone_delta(from_pc: int, to_pc: int) -> int:
    d = (to_pc - from_pc) % 12
    return d if d <= 6 else d - 12


def _frets_for_pc(string: str, pc: int, max_fret: int = 14) -> list[int]:
    o = STRING_OPEN_PC.get(string)
    if o is None:
        return []
    return [f for f in range(0, max_fret + 1) if (o + f) % 12 == pc]


def _position_cost(
    string: str,
    fret: int,
    template_string: str,
    template_fret: int,
) -> float:
    si = TUNING_LOW_TO_HIGH.index(string) if string in TUNING_LOW_TO_HIGH else 0
    ti = TUNING_LOW_TO_HIGH.index(template_string) if template_string in TUNING_LOW_TO_HIGH else 0
    return abs(fret - template_fret) + abs(si - ti) * 0.35


def transpose_steps(
    steps: list[dict],
    template_root: str,
    target_root: str,
    *,
    key_context: str | None = None,
) -> list[dict]:
    """Transpõe uma forma (ex. Dó maior 7) para outra tônica mantendo o desenho do manual."""
    if not steps:
        return []

    root_pc_t = note_to_pc(target_root)
    root_pc_0 = note_to_pc(template_root)
    if root_pc_t is None or root_pc_0 is None:
        return [dict(s) for s in steps]

    shift = _semitone_delta(root_pc_0, root_pc_t)
    out: list[dict] = []

    for st in steps:
        old_pc = note_to_pc(st.get('note', ''))
        if old_pc is None:
            continue
        new_pc = (old_pc + shift) % 12
        new_note = pc_to_spelling(new_pc, key_context or target_root)
        options = _frets_for_pc(st['string'], new_pc)
        if not options:
            # mesma região do braço em outra corda
            best_f, best_s, best_cost = None, None, 1e9
            for s in TUNING_LOW_TO_HIGH:
                for f in _frets_for_pc(s, new_pc):
                    cost = _position_cost(s, f, st['string'], st['fret'])
                    if cost < best_cost:
                        best_cost, best_f, best_s = cost, f, s
            if best_f is None:
                continue
            fret, string = best_f, best_s
        else:
            fret = min(options, key=lambda f: abs(f - st['fret']))
            string = st['string']

        out.append({
            'string': string,
            'fret': fret,
            'finger': st.get('finger'),
            'interval': st.get('interval', ''),
            'note': new_note,
            'isRoot': bool(st.get('isRoot')),
        })

    return out


def quality_from_theory(theory: dict | None) -> str:
    if not theory:
        return 'maj7'
    notes = theory.get('notes') or []
    if len(notes) >= 3:
        inferred = _infer_quality_from_notes(notes)
        if inferred:
            return inferred
    q = (theory.get('quality') or '').lower()
    if q in ('maj', 'major'):
        return 'maj'
    if q == 'maj7':
        return 'maj7'
    if q in ('m', 'min', 'minor'):
        return 'm'
    if q == 'm7':
        return 'm7'
    if q in ('7', 'dom7', 'dominant'):
        return '7'
    if q in ('m7b5', 'hdim', 'half-diminished'):
        return 'm7b5'
    if q in ('dim7',):
        return 'dim7'
    if q in ('dim',):
        return 'dim'
    if q in ('aug',):
        return 'aug'
    return q or 'maj7'


def _infer_quality_from_notes(notes: list[str]) -> str | None:
    root_pc = note_to_pc(notes[0])
    if root_pc is None:
        return None
    pcs = {
        (note_to_pc(n) - root_pc) % 12
        for n in notes
        if note_to_pc(n) is not None
    }
    if {0, 3, 6, 10} <= pcs or pcs == {0, 3, 6, 9}:
        return 'dim7' if pcs == {0, 3, 6, 9} else 'm7b5'
    if {0, 3, 7, 10} <= pcs:
        return 'm7'
    if {0, 4, 7, 11} <= pcs:
        return 'maj7'
    if {0, 4, 7, 10} <= pcs:
        return '7'
    if {0, 3, 7} <= pcs:
        return 'm'
    if {0, 4, 7} <= pcs:
        return 'maj'
    if {0, 3, 6} <= pcs:
        return 'dim'
    if {0, 4, 8} <= pcs:
        return 'aug'
    return None


def resolve_steps_for_symbol(
    symbol: str,
    quality_templates: dict[str, list[dict]],
    *,
    key_context: str | None = None,
) -> list[dict] | None:
    theory = chord_theory_block(symbol, key_context=key_context)
    if not theory:
        return None
    quality = quality_from_theory(theory)
    template = quality_templates.get(quality)
    if not template:
        # símbolos simples (Am → m)
        if quality.endswith('7') and quality[:-1] in quality_templates:
            template = quality_templates.get(quality[:-1])
        if not template:
            return None
    root = theory.get('root') or symbol[0]
    template_root = next(
        (s['note'] for s in template if s.get('isRoot')),
        template[0]['note'],
    )
    return transpose_steps(template, template_root, root, key_context=key_context)
