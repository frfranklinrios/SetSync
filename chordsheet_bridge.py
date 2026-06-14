"""Ponte entre cifras SetSync e o módulo chordsheet (formato chordsheet.com)."""

from __future__ import annotations

import json
from typing import Any

from chordsheet.export import MODULE_ID, chart_to_payload, payload_to_chart
from chordsheet.parser import Chart, parse_chart
from chordsheet.render import render_chart_html
from chordsheet.transpose import transpose_chart
from leadsheet.converter import is_leadsheet_document, resolve_to_grade_flat


def _chordsheet_source_text(data: dict[str, Any]) -> str:
    """Retorna texto chordsheet.com; LeadSheet legado usa source como dict."""
    src = data.get("source")
    if isinstance(src, str):
        return src.strip()
    return ""


def _parse_stored_chordsheet(raw) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    if is_leadsheet_document(data):
        return None
    source_text = _chordsheet_source_text(data)
    if data.get("module") == MODULE_ID and source_text:
        return data
    if source_text and data.get("meta") is not None:
        return data
    return None


def load_stored_chordsheet(cifra: dict) -> dict[str, Any] | None:
    for field in ("chordsheet_json", "leadsheet_json"):
        data = _parse_stored_chordsheet(cifra.get(field))
        if data:
            return data
    return None


def _bar_acordes_for_grade(bar) -> list[str]:
    """Achata pulse_grid para grade legado (inclui semi-pulsos C&D)."""
    if bar.is_empty or bar.simile or bar.chords in (["%"], [""]):
        return ["%"]
    out: list[str] = []
    for beat in bar.get_pulse_grid():
        for c in beat:
            token = str(c or "").strip()
            if token in ("", "%"):
                continue
            if token == "*":
                out.append("%")
            else:
                out.append(token)
    return out or ["%"]


def chart_to_grade_flat(chart: Chart) -> list[dict]:
    """Converte Chart para grade plana (compatível com play mode legado)."""
    sec_at = {i: t for i, t in chart.sections}
    result: list[dict] = []
    bar_num = 0
    for i, bar in enumerate(chart.bars):
        if bar.blank_spacer:
            continue
        if bar.nav:
            continue
        if bar.annotation and not bar.chords and not bar.is_empty:
            continue
        bar_num += 1
        item: dict = {"compasso": bar_num, "acordes": _bar_acordes_for_grade(bar)}
        if i in sec_at:
            item["secao"] = sec_at[i]
        result.append(item)
    return result


def load_editor_initial(cifra: dict) -> dict[str, Any]:
    """Estado inicial do editor Chord Sheet para uma cifra."""
    stored = load_stored_chordsheet(cifra)
    if stored:
        return {
            "source": stored.get("source") or "",
            "meta": stored.get("meta") or {},
            "prefs": stored.get("prefs") or {},
        }

    flat = resolve_to_grade_flat(cifra)
    bpm = cifra.get("bpm")
    meta = {
        "title": (cifra.get("titulo") or "").strip() or "Sem título",
        "artist": (cifra.get("artista") or "").strip(),
        "key": (cifra.get("tom_original") or "").strip(),
        "bpm": str(int(bpm)) if bpm else "",
        "time_signature": "4/4",
        "capo": "",
        "style": "",
    }
    return {
        "source": grade_flat_to_source(flat) if flat else "",
        "meta": meta,
        "prefs": {},
    }


def grade_flat_to_source(grade_list: list[dict]) -> str:
    """Converte grade plana (LeadSheet) em texto estilo chordsheet.com."""
    lines: list[str] = []
    last_secao: str | None = None
    for item in grade_list or []:
        if not isinstance(item, dict):
            continue
        secao = (item.get("secao") or "").strip()
        if secao and secao != last_secao:
            lines.append(f"= {secao}")
            last_secao = secao
        acordes = item.get("acordes") or ["%"]
        if not isinstance(acordes, list):
            acordes = ["%"]
        tokens: list[str] = []
        for ch in acordes:
            token = str(ch or "").strip() or "%"
            tokens.append(token)
        lines.append(" ".join(tokens))
    return "\n".join(lines).strip()


def cifra_chart_payload(
    cifra: dict,
    *,
    grade_list: list[dict] | None = None,
) -> dict[str, Any] | None:
    """Monta {source, meta, prefs} para parse_chart (tom nativo, sem transposição de palco)."""
    stored = load_stored_chordsheet(cifra)
    if stored:
        return {
            "source": stored["source"],
            "meta": dict(stored.get("meta") or {}),
            "prefs": stored.get("prefs") or {},
        }

    flat = grade_list if grade_list is not None else resolve_to_grade_flat(cifra)
    if not flat:
        return None

    bpm = cifra.get("bpm")
    meta = {
        "title": (cifra.get("titulo") or "").strip() or "Sem título",
        "artist": (cifra.get("artista") or "").strip(),
        "key": (cifra.get("tom_original") or "").strip(),
        "bpm": str(int(bpm)) if bpm else "",
        "time_signature": "4/4",
    }
    return {"source": grade_flat_to_source(flat), "meta": meta, "prefs": {}}


def chordsheet_performance_semitones(
    cifra: dict,
    performance_semitones: int = 0,
    *,
    chart_source_key: str | None = None,
) -> tuple[int, str]:
    """Semitons para o chord sheet chegar ao mesmo tom da cifra transposta."""
    from util import (
        key_at_transpose,
        normalize_tom_label,
        normalize_transpose_semitones,
        semitones_between_keys,
    )

    performance = normalize_transpose_semitones(performance_semitones)
    tom_orig = normalize_tom_label(cifra.get("tom_original") or "")
    target_key = key_at_transpose(tom_orig, performance)
    source_key = normalize_tom_label(chart_source_key or tom_orig)
    chart_semi = semitones_between_keys(source_key, target_key)
    return chart_semi, target_key


def cifra_has_chordsheet(cifra: dict) -> bool:
    return cifra_chart_payload(cifra) is not None


_AWKWARD_ROOT = {"E#": "F", "B#": "C", "Cb": "B", "Fb": "E"}


def _spell_chord_like_cifra(chord: str, target_key: str) -> str:
    """Grafia de acorde igual à cifra (Bb em vez de A#, etc.)."""
    from util import _split_chord_root_quality, format_text_chords_br

    token = (chord or "").strip()
    if not token or token in ("%", "NC", "N.C."):
        return chord
    if token.startswith("*"):
        return chord

    respelled = format_text_chords_br(token, target_key)
    if respelled == token:
        return token

    orig = _split_chord_root_quality(token)
    new = _split_chord_root_quality(respelled)
    if not orig or not new:
        return respelled

    orig_root, _, orig_bass = orig
    new_root, quality, new_bass = new

    natural = _AWKWARD_ROOT.get(new_root)
    if natural and orig_root.upper() == natural:
        new_root = natural

    if new_bass:
        bass_nat = _AWKWARD_ROOT.get(new_bass)
        if bass_nat and (orig_bass or "").upper() == bass_nat:
            new_bass = bass_nat

    out = new_root + quality
    if new_bass:
        out += "/" + new_bass
    return out


def apply_chart_cifra_spelling(chart, target_key: str):
    """Reescreve acordes e tom do chart com as regras de grafia da cifra SetSync."""
    from util import normalize_tom_label

    key = normalize_tom_label(target_key or "")
    if not key:
        return chart

    chart.meta.key = key
    for bar in chart.bars:
        if bar.nav or bar.annotation:
            continue
        grid = bar.get_pulse_grid()
        bar.set_pulse_grid(
            [[_spell_chord_like_cifra(c, key) for c in beat] for beat in grid]
        )
    return chart


def render_cifra_chordsheet_html(
    cifra: dict,
    *,
    semitones: int = 0,
    display_key: str | None = None,
    grade_list: list[dict] | None = None,
) -> str | None:
    """Renderiza HTML do chord sheet no mesmo tom da cifra (tom_original + transposição)."""
    from util import key_at_transpose, normalize_tom_label, normalize_transpose_semitones

    performance = normalize_transpose_semitones(semitones)
    tom_orig = normalize_tom_label(cifra.get("tom_original") or "")
    target_key = display_key or key_at_transpose(tom_orig, performance)

    stored = load_stored_chordsheet(cifra)
    if stored:
        chart = payload_to_chart(stored)
    else:
        payload = cifra_chart_payload(cifra, grade_list=grade_list)
        if not payload:
            return None
        chart = parse_chart(
            payload["source"],
            meta=payload.get("meta"),
            prefs=payload.get("prefs"),
        )
    source_key = normalize_tom_label(chart.meta.key or tom_orig)
    if grade_list is not None:
        # Grade já transposta pelo caller (legado) — só garante o rótulo do tom.
        chart.meta.key = target_key
    else:
        chart_semi, target_key = chordsheet_performance_semitones(
            cifra, performance, chart_source_key=source_key
        )
        if chart_semi:
            chart = transpose_chart(chart, chart_semi)
        chart.meta.key = target_key
    apply_chart_cifra_spelling(chart, target_key)
    return render_chart_html(chart)


def persist_chordsheet_payload(cifra_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Salva payload chordsheet e sincroniza grade_json."""
    from db import get_cifra, update_cifra

    cifra = get_cifra(cifra_id)
    if not cifra:
        raise ValueError("Cifra não encontrada")

    chart = payload_to_chart(data)
    payload = chart_to_payload(chart)
    flat = chart_to_grade_flat(chart)
    meta = payload.get("meta") or {}

    bpm_raw = (meta.get("bpm") or "").strip()
    bpm = None
    if bpm_raw:
        try:
            bpm = float(bpm_raw)
        except ValueError:
            pass

    update_cifra(
        cifra_id,
        (meta.get("title") or "").strip() or cifra["titulo"],
        (meta.get("artist") or "").strip() or cifra["artista"],
        (meta.get("key") or "").strip() or cifra["tom_original"],
        cifra["conteudo"],
        cifra.get("cifra_json"),
        json.dumps(flat, ensure_ascii=False) if flat else None,
        json.dumps(payload, ensure_ascii=False),
        bpm if bpm is not None else cifra.get("bpm"),
        cifra.get("duracao_seg"),
    )
    return payload
