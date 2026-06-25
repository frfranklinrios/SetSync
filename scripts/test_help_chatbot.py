#!/usr/bin/env python3
"""Testes do assistente de ajuda."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_kb_nonempty():
    from help_chatbot import get_knowledge_base
    kb = get_knowledge_base()
    assert len(kb) >= 20, len(kb)


def test_answer_transposicao():
    from help_chatbot import answer_question
    r = answer_question('Como transpor cifra no SetSync?')
    assert r['ok']
    assert r['answer']
    assert 'transpor' in r['answer'].lower() or 'tom' in r['answer'].lower()


def test_answer_estudio():
    from help_chatbot import answer_question
    r = answer_question('reservar estúdio de ensaio')
    assert r['ok']
    assert r['links']


if __name__ == '__main__':
    test_kb_nonempty()
    test_answer_transposicao()
    test_answer_estudio()
    print('OK help_chatbot')
