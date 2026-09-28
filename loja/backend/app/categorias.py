"""Categorias da loja: acessórios para músicos em geral."""

from __future__ import annotations

CATEGORIAS = [
    "Transmissores",
    "Pedais",
    "Encordoamentos",
    "Palhetas",
    "Correias",
    "Cabos",
    "Afinadores",
    "Capotrastes",
    "Capas e bags",
    "Suportes",
    "Percussão",
    "Acessórios",
]

_REGRAS = (
    (("wireless", "transmitter", "transmissor", "receiver", "2.4g"), "Transmissores"),
    (("pedal", "overdrive", "distortion", "reverb"), "Pedais"),
    (("string", "encordoamento", "corda", "strings"), "Encordoamentos"),
    (("pick", "plectrum", "palheta"), "Palhetas"),
    (("strap", "correia"), "Correias"),
    (("cable", "cabo", "jack", "xlr"), "Cabos"),
    (("tuner", "afinador", "metronome", "metronomo"), "Afinadores"),
    (("capo", "capotraste"), "Capotrastes"),
    (("bag", "case", "capa", "gigbag"), "Capas e bags"),
    (("stand", "suporte", "hanger", "clamp"), "Suportes"),
    (("stick", "baqueta", "mallet", "shaker"), "Percussão"),
)


def categoria_do_texto(*textos: str) -> str:
    junto = " ".join(t or "" for t in textos).lower()
    for termos, nome in _REGRAS:
        if any(t in junto for t in termos):
            return nome
    return "Acessórios"
