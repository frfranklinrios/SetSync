"""Testes dos meta caracteres do chord sheet."""

from __future__ import annotations

import unittest

from chordsheet.examples import EXAMPLES
from chordsheet.parser import parse_chart
from chordsheet.render import render_chart_html


class MetaCharactersTest(unittest.TestCase):
    def test_repeat_group_x2_not_duplicated(self):
        chart = parse_chart("(A B C D)x2", meta={"title": "T", "key": "C"})
        self.assertEqual(len(chart.bars), 4)
        self.assertEqual(chart.bars[0].line_left, "repeat-start")
        self.assertEqual(chart.bars[-1].line_right, "repeat-end")
        self.assertEqual(chart.bars[-1].repeat_times, 2)

    def test_repeat_group_renders_markers(self):
        html = render_chart_html(
            parse_chart("(A B C D)x2", meta={"title": "T", "key": "C"}),
        )
        self.assertIn("cs-bl-repeat-start", html)
        self.assertIn("cs-bl-repeat-end", html)
        self.assertIn("×2", html)

    def test_two_bar_simile_single_slot(self):
        chart = parse_chart("A B %%", meta={"title": "T", "key": "C"})
        self.assertEqual(len(chart.bars), 3)
        self.assertTrue(chart.bars[2].simile)
        self.assertEqual(chart.bars[2].simile_span, 2)

    def test_percent_one_clones_bar(self):
        chart = parse_chart("A %1 C_D E", meta={"title": "T", "key": "C"})
        self.assertEqual(chart.bars[0].chords, ["A"])
        self.assertEqual(chart.bars[1].chords, ["A"])
        self.assertEqual(chart.bars[2].chords, ["C", "D"])
        self.assertEqual(chart.bars[2].get_pulse_grid(), [["C"], ["D"]])

    def test_semi_pulse_in_one_beat(self):
        chart = parse_chart("C&D", meta={"title": "T", "key": "C"})
        self.assertEqual(chart.bars[0].get_pulse_grid(), [["C", "D"]])
        self.assertEqual(chart.bars[0].chords, ["C&D"])
        html = render_chart_html(chart)
        self.assertIn("cs-chords-beats", html)
        self.assertIn("cs-beat--split", html)
        self.assertNotIn("cs-chords-semi-bar", html)
        self.assertEqual(html.count("cs-empty"), 3)

    def test_single_chord_shows_all_pulses(self):
        chart = parse_chart("C", meta={"title": "T", "time_signature": "4/4"})
        html = render_chart_html(chart)
        self.assertIn("cs-chords-beats", html)
        self.assertEqual(html.count('class="cs-beat"'), 4)
        self.assertEqual(html.count("cs-empty"), 3)

    def test_semi_pulse_with_underscore(self):
        chart = parse_chart("C&D_E_F", meta={"title": "T", "key": "C"})
        self.assertEqual(chart.bars[0].get_pulse_grid(), [["C", "D"], ["E"], ["F"]])
        html = render_chart_html(chart)
        self.assertIn("cs-beat--split", html)
        self.assertNotIn("cs-chords-semi-bar", html)

    def test_semi_pulse_round_trip(self):
        chart = parse_chart("C&D_E", meta={"title": "T", "key": "C"})
        self.assertIn("C&D_E", chart.to_source())

    def test_volta_in_repeat_group(self):
        chart = parse_chart("(A B 1. C D 2. E F)", meta={"title": "T", "key": "C"})
        self.assertEqual(chart.bars[2].volta, "1.")
        self.assertEqual(chart.bars[4].volta, "2.")
        self.assertEqual(chart.bars[0].line_left, "repeat-start")
        self.assertEqual(chart.bars[-1].line_right, "repeat-end")

    def test_comments_skipped(self):
        chart = parse_chart("# comentário\nC Am", meta={"title": "T"})
        self.assertEqual(len(chart.bars), 2)

    def test_text_and_section_lines(self):
        chart = parse_chart("- Cabeçalho\n= A\nC D", meta={"title": "T"})
        self.assertEqual(chart.bars[0].annotation, "Cabeçalho")
        self.assertEqual(chart.sections[0][1], "A")

    def test_f_not_respelled_to_e_sharp_in_f_sharp_key(self):
        from chordsheet_bridge import apply_chart_cifra_spelling

        chart = parse_chart("(A B 1. C D 2. E F)", meta={"title": "T", "key": "F#"})
        apply_chart_cifra_spelling(chart, "F#")
        chords = [c for b in chart.bars for c in b.chords if c not in ("%", "")]
        self.assertIn("F", chords)
        self.assertNotIn("E#", chords)

    def test_manual_meta_example_parses(self):
        ex = EXAMPLES["manual_meta"]
        chart = parse_chart(ex["source"], meta=ex["meta"])
        self.assertGreater(len(chart.bars), 20)
        html = render_chart_html(chart)
        self.assertIn("cs-chart", html)

    def test_adjacent_bars_single_barline(self):
        html = render_chart_html(parse_chart("C Am F G", meta={"title": "T"}))
        chunk = html.split("cs-row-bars")[1][:2500]
        self.assertEqual(chunk.count("cs-barline-start cs-bl-single"), 1)

    def test_export_pulse_grid_roundtrip(self):
        from chordsheet.export import chart_to_payload, payload_to_chart

        chart = parse_chart("C&D_E", meta={"title": "T"})
        payload = chart_to_payload(chart)
        self.assertEqual(payload["bars"][0]["pulse_grid"], [["C", "D"], ["E"]])
        restored = payload_to_chart({**payload, "source": ""})
        self.assertEqual(restored.bars[0].get_pulse_grid(), [["C", "D"], ["E"]])

    def test_grade_flat_expands_semi_pulses(self):
        from chordsheet_bridge import chart_to_grade_flat

        chart = parse_chart("C&D", meta={"title": "T"})
        flat = chart_to_grade_flat(chart)
        self.assertEqual(flat[0]["acordes"], ["C", "D"])

    def test_source_line_breaks_render_on_new_row(self):
        chart = parse_chart("C Am F G\nD Em Am G", meta={"title": "T"})
        self.assertEqual(chart.line_breaks, [4])
        html = render_chart_html(chart)
        self.assertEqual(html.count("cs-row-bars"), 2)

    def test_to_source_roundtrip_preserves_line_breaks(self):
        from chordsheet.export import chart_to_payload, payload_to_chart

        src = "C Am\nF G\nD Em"
        chart = parse_chart(src, meta={"title": "T"})
        self.assertEqual(chart.line_breaks, [2, 4])
        payload = chart_to_payload(chart)
        self.assertIn("\n", payload["source"])
        restored = payload_to_chart(payload)
        self.assertEqual(restored.line_breaks, [2, 4])
        self.assertEqual(restored.to_source(), chart.to_source())

    def test_smufl_chord_glyphs_in_render(self):
        from chordsheet.format_chord import chord_to_html
        from chordsheet.prefs import Prefs
        from chordsheet.smufl_chord import (
            CSYM_ACCIDENTAL_SHARP,
            CSYM_MAJOR_SEVENTH,
            CSYM_MINOR,
        )

        prefs = Prefs(notation_style="intl")
        self.assertIn(CSYM_ACCIDENTAL_SHARP, chord_to_html("F#m7", prefs))
        self.assertIn(CSYM_MINOR, chord_to_html("Am7", prefs))
        self.assertIn(CSYM_MAJOR_SEVENTH, chord_to_html("Cmaj7", prefs))
        html_out = render_chart_html(
            parse_chart(
                "F#m7 Cmaj7 Am/E",
                meta={"title": "T", "key": "C"},
                prefs={"notation_style": "intl", "notation_style_chosen": True},
            ),
        )
        self.assertIn("cs-smufl", html_out)
        self.assertIn(CSYM_ACCIDENTAL_SHARP, html_out)

    def test_notation_style_brasil(self):
        from chordsheet.format_chord import chord_to_html, format_chord_display
        from chordsheet.prefs import Prefs

        prefs = Prefs(notation_style="br")
        self.assertEqual(format_chord_display("Cmaj7", prefs), "C7+")
        self.assertEqual(format_chord_display("Gdim", prefs), "G°")
        self.assertEqual(format_chord_display("A-", prefs), "Am")
        self.assertEqual(format_chord_display("D-7", prefs), "Dm7")
        self.assertEqual(format_chord_display("Cm7b5", prefs), "Cm7b5")
        self.assertEqual(format_chord_display("C#ø7", prefs), "C#m7b5")
        html = chord_to_html("Cmaj7", prefs)
        self.assertIn("C7+", html)
        self.assertNotIn("cs-smufl", html)

    def test_default_notation_is_brasil_without_explicit_style(self):
        from chordsheet.prefs import Prefs

        prefs = Prefs.from_dict({"maj7_style": "delta", "half_dim_style": "oslash"})
        self.assertEqual(prefs.notation_style, "br")

    def test_intl_reverted_without_explicit_choice(self):
        from chordsheet.prefs import Prefs

        prefs = Prefs.from_dict(
            {"notation_style": "intl", "maj7_style": "delta", "half_dim_style": "oslash"}
        )
        self.assertEqual(prefs.notation_style, "br")
        kept = Prefs.from_dict(
            {
                "notation_style": "intl",
                "notation_style_chosen": True,
            }
        )
        self.assertEqual(kept.notation_style, "intl")

    def test_notation_style_americana(self):
        from chordsheet.format_chord import chord_to_html, format_chord_display
        from chordsheet.prefs import Prefs

        prefs = Prefs(notation_style="us")
        self.assertEqual(format_chord_display("Cmaj7", prefs), "Cmaj7")
        html = chord_to_html("Cm7b5", prefs)
        self.assertIn("m7b5", html)
        self.assertNotIn("cs-smufl", html)


if __name__ == "__main__":
    unittest.main()
