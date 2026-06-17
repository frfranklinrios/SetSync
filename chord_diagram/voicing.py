"""Motor de voicings — backtracking com filtro de tocabilidade (port do JS)."""

from __future__ import annotations

from chord_diagram.instruments import InstrumentSpec, open_string_pcs
from chord_diagram.theory.pitch import note_to_pc

MAX_VOICINGS_DEFAULT = 8


def _fret_pitch(open_pc: int, fret) -> int | None:
    if fret == 'x' or fret is None:
        return None
    if fret == 0:
        return open_pc
    if isinstance(fret, int) and fret > 0:
        return (open_pc + fret) % 12
    return None


def _is_playable_span(frets: list, max_span: int) -> bool:
    nums = [f for f in frets if isinstance(f, int) and f > 0]
    if not nums:
        return any(f == 0 for f in frets)
    return max(nums) - min(nums) <= max_span


def _options_per_string(open_pcs: list[int], chord_pcs: set[int], max_fret: int) -> list[list]:
    per = []
    for oi in open_pcs:
        opts: list = ['x']
        if oi in chord_pcs:
            opts.append(0)
        for f in range(1, max_fret + 1):
            if (oi + f) % 12 in chord_pcs:
                opts.append(f)
        per.append(opts)
    return per


def _validate(frets, open_pcs: list[int], chord_pcs: set[int], root_pc: int, max_span: int) -> bool:
    played: set[int] = set()
    active = 0
    for si, f in enumerate(frets):
        if f == 'x':
            continue
        active += 1
        pitch = _fret_pitch(open_pcs[si], f)
        if pitch is None or pitch not in chord_pcs:
            return False
        played.add(pitch)
    if active < min(2, len(open_pcs)):
        return False
    if root_pc not in played:
        return False
    if not _is_playable_span(frets, max_span):
        return False
    req = list(chord_pcs)
    if len(req) <= 4:
        for pc in req:
            if pc not in played:
                return False
    elif len(played) < max(3, int(len(req) * 0.75)):
        return False
    return True


def _score(frets, open_pcs: list[int], root_pc: int) -> float:
    score = 0.0
    nums = []
    for si, f in enumerate(frets):
        if f == 'x':
            score += 8
        elif f == 0:
            score -= 6
        elif isinstance(f, int):
            nums.append(f)
            score += f * 2
            if _fret_pitch(open_pcs[si], f) == root_pc and si == len(frets) - 1:
                score -= 3
    if nums:
        score += (max(nums) - min(nums)) * 5
        score += min(nums) * 3
    return score


def _backtrack(per_string, open_pcs, chord_pcs, root_pc, si, current, out, seen, max_span, limit):
    if len(out) >= limit:
        return
    if si >= len(per_string):
        if not _validate(current, open_pcs, chord_pcs, root_pc, max_span):
            return
        key = ''.join(str(x) for x in current)
        if key in seen:
            return
        seen.add(key)
        out.append({'frets': current[:], 'score': _score(current, open_pcs, root_pc)})
        return
    for opt in per_string[si]:
        current.append(opt)
        _backtrack(per_string, open_pcs, chord_pcs, root_pc, si + 1, current, out, seen, max_span, limit)
        current.pop()
        if len(out) >= limit:
            return


def discover_voicings(
    spec: InstrumentSpec,
    note_names: list[str],
    *,
    limit: int = MAX_VOICINGS_DEFAULT,
) -> list[dict]:
    open_pcs = open_string_pcs(spec)
    if not open_pcs:
        return []
    pcs = []
    for n in note_names:
        pc = note_to_pc(n)
        if pc is not None and pc not in pcs:
            pcs.append(pc)
    if not pcs:
        return []
    root_pc = note_to_pc(note_names[0]) or pcs[0]
    chord_set = set(pcs)
    per = _options_per_string(open_pcs, chord_set, spec.max_fret)
    raw: list[dict] = []
    seen: set[str] = set()
    _backtrack(per, open_pcs, chord_set, root_pc, 0, [], raw, seen, spec.max_span, limit)
    raw.sort(key=lambda x: x['score'])
    return raw[:limit]


def _barre_allowed_on_string(frets: list, string_idx: int, barre_fret: int) -> bool:
    """Pestana no traste F só é válida se cordas mais graves não tiverem nota em traste < F."""
    for g in range(string_idx):
        fg = frets[g]
        if isinstance(fg, int) and 0 < fg < barre_fret:
            return False
    return True


def _detect_barres_contiguous(frets: list) -> list[dict]:
    barres = []
    n = len(frets)
    i = 0
    while i < n:
        f = frets[i]
        if not isinstance(f, int) or f <= 0:
            i += 1
            continue
        j = i + 1
        while j < n and frets[j] == f:
            j += 1
        s = i
        while s < j:
            if not _barre_allowed_on_string(frets, s, f):
                s += 1
                continue
            e = s + 1
            while e < j and _barre_allowed_on_string(frets, e, f):
                e += 1
            if e - s >= 2:
                barres.append({'fret': f, 'startString': s + 1, 'endString': e})
            s = e
        i = j
    return barres


def _detect_barres_from_fingers(frets: list, fingers: list[int] | None) -> list[dict]:
    if not fingers:
        return []
    by_fret: dict[int, list[int]] = {}
    for i, f in enumerate(frets):
        if not isinstance(f, int) or f <= 0:
            continue
        if i >= len(fingers) or fingers[i] != 1:
            continue
        by_fret.setdefault(f, []).append(i)
    barres: list[dict] = []
    for fret, strings in by_fret.items():
        if len(strings) < 2:
            continue
        start = min(strings)
        end = max(strings)
        valid = True
        for s in range(start, end + 1):
            fg = frets[s]
            if fg in ('x', 'X'):
                valid = False
                break
            if isinstance(fg, int) and 0 < fg < fret:
                valid = False
                break
            if not _barre_allowed_on_string(frets, s, fret):
                valid = False
                break
        if valid and end > start:
            barres.append({'fret': fret, 'startString': start + 1, 'endString': end + 1})
    barres.sort(key=lambda b: b['fret'])
    return barres


def detect_barres(frets: list, fingers: list[int] | None = None) -> list[dict]:
    """Detecta pestanas — prioriza dedo 1 em múltiplas cordas no mesmo traste."""
    from_fingers = _detect_barres_from_fingers(frets, fingers)
    if from_fingers:
        return from_fingers
    return _detect_barres_contiguous(frets)


def string_on_barre(string_idx: int, frets: list, barres: list[dict]) -> dict | None:
    fval = frets[string_idx]
    for bar in barres:
        s0 = bar['startString'] - 1
        s1 = bar['endString'] - 1
        if s0 <= string_idx <= s1 and fval == bar['fret']:
            return bar
    return None


def assign_fingers(frets: list, barres: list[dict]) -> list[int]:
    """Heurística simples de dedilhado (1=polegar … 4=mindinho)."""
    barre_strings: set[int] = set()
    for b in barres:
        for s in range(b['startString'], b['endString'] + 1):
            barre_strings.add(s - 1)

    fingers = [0] * len(frets)
    used = set()
    nums = sorted({f for f in frets if isinstance(f, int) and f > 0})
    fret_to_finger = {f: i + 1 for i, f in enumerate(nums[:4])}

    for si, f in enumerate(frets):
        if f == 'x':
            fingers[si] = 0
        elif f == 0:
            fingers[si] = 0
        elif si in barre_strings:
            fingers[si] = 1
        elif isinstance(f, int):
            fingers[si] = fret_to_finger.get(f, 1)
    return fingers


def frets_to_api(frets: list) -> list:
    out = []
    for f in frets:
        if f == 'x':
            out.append('X')
        else:
            out.append(f)
    return out


def compute_base_fret(frets: list) -> int:
    nums = [f for f in frets if isinstance(f, int) and f > 0]
    if not nums:
        return 0
    return max(0, min(nums) - 1)


# Cordas D G B E do violão → cavaco D G B D (aproximação chords-db)
_GUITAR_TO_CAVACO_IDX = (2, 3, 4, 5)


def adapt_guitar_voicing_to_four_strings(voicing: dict) -> dict:
    """Reduz voicing de 6 cordas (violão) para 4 (cavaco/cavaquinho)."""
    frets = list(voicing.get('frets') or [])
    if len(frets) != 6:
        return dict(voicing)
    fingers = voicing.get('fingers')
    new_frets = [frets[i] for i in _GUITAR_TO_CAVACO_IDX]
    new_fingers = [fingers[i] for i in _GUITAR_TO_CAVACO_IDX] if fingers else None
    new_barres = detect_barres(new_frets, new_fingers)
    out = dict(voicing)
    out['frets'] = new_frets
    out['fingers'] = new_fingers
    out['barres'] = [
        {'fret': b['fret'], 'from': b['startString'] - 1, 'to': b['endString'] - 1}
        for b in new_barres
    ]
    return out
