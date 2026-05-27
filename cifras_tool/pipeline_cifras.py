from __future__ import annotations

import json
import re
import subprocess
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from cifras_tool.calibracao import (
    extrair_acordes_referencia,
    grade_compacta_da_cifra,
    montar_grade_da_cifra,
    resolver_tonalidade,
    resumo_processamento,
)
from cifras_tool.compasso import CompassoInfo, parsear_compasso
from cifras_tool.config import settings
from cifras_tool.downloader import AudioDownloader
from cifras_tool.formatter import HarmonicPart
from cifras_tool.pipeline import AudioPipeline
from cifras_tool.scraper import detectar_fonte, normalizar_url, raspar_cifra
from cifras_tool.scraper.comum import normalizar_url_youtube
from cifras_tool.setsync_export import montar_pacote_setsync


@dataclass
class ResultadoPipeline:
    pasta: Path
    titulo: str
    artista: str
    youtube: str
    mp3: Path
    cifra: str
    acordes_cifra: list[str]
    grade_harmonica: str
    grade_progressao_cifra: str
    tonalidade: str
    tonalidade_estimada: str
    compasso: str
    partes_grade: list[HarmonicPart]
    setsync: dict
    bpm: float | None
    duracao_seg: int | None


def validar_url_cifra(url: str) -> str:
    url = normalizar_url(url)
    fonte = detectar_fonte(url)
    parsed = urlparse(url)

    if fonte == "cifras.com.br" and "/cifra/" not in parsed.path:
        raise ValueError("URL do Cifras.com.br deve conter /cifra/ no caminho")

    if fonte == "cifraclub":
        partes = [p for p in parsed.path.strip("/").split("/") if p]
        if len(partes) < 2:
            raise ValueError(
                "URL do Cifra Club deve ser no formato "
                "cifraclub.com.br/artista/nome-da-musica"
            )

    return url


def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto.lower()).strip("-")
    return texto or "musica"


def wav_para_mp3(wav_path: Path, mp3_path: Path) -> None:
    resultado = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(wav_path),
            "-codec:a",
            "libmp3lame",
            "-qscale:a",
            "2",
            str(mp3_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado.returncode != 0:
        raise RuntimeError(f"Falha ao converter para MP3: {resultado.stderr}")


def salvar_arquivos(pasta: Path, dados: dict, resultado: ResultadoPipeline) -> None:
    pasta.mkdir(parents=True, exist_ok=True)

    fonte = dados.get("fonte", "")
    (pasta / "cifra.txt").write_text(
        f"{dados['titulo']}\n{dados['artista']}\n"
        f"Tom: {resultado.tonalidade}\n"
        f"Fonte: {fonte}\n"
        f"YouTube: {dados['youtube']}\n\n{dados['cifra']}",
        encoding="utf-8",
    )

    (pasta / "youtube.txt").write_text(
        f"{dados['titulo']} - {dados['artista']}\n\n{dados['youtube']}\n",
        encoding="utf-8",
    )

    (pasta / "grade_harmonica.txt").write_text(
        f"{dados['titulo']} - {dados['artista']}\n"
        f"Tom: {resultado.tonalidade}\n"
        f"Compasso: {resultado.compasso}\n"
        f"Acordes: {', '.join(resultado.acordes_cifra)}\n\n"
        f"{resultado.grade_harmonica}",
        encoding="utf-8",
    )

    (pasta / "progressao_cifra.txt").write_text(
        f"{dados['titulo']} - {dados['artista']}\n\n{resultado.grade_progressao_cifra}",
        encoding="utf-8",
    )

    metadados = {
        "url_cifras": dados["url"],
        "fonte": fonte,
        "titulo": dados["titulo"],
        "artista": dados["artista"],
        "youtube": dados["youtube"],
        "song_id": dados.get("song_id", ""),
        "mp3": str(resultado.mp3),
        "tonalidade": resultado.tonalidade,
        "tom_site": dados.get("tom", ""),
        "tonalidade_estimada": resultado.tonalidade_estimada,
        "compasso": resultado.compasso,
        "acordes_cifra": resultado.acordes_cifra,
        "cifra": dados["cifra"],
        "grade_harmonica": resultado.grade_harmonica,
        "grade_progressao_cifra": resultado.grade_progressao_cifra,
        "videos_youtube": dados.get("videos_youtube", []),
        "youtube_manual": dados.get("youtube_manual", False),
        "bpm": resultado.bpm,
        "duracao_seg": resultado.duracao_seg,
    }
    (pasta / "resultado.json").write_text(
        json.dumps(metadados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (pasta / "setsync_cifra.json").write_text(
        json.dumps(resultado.setsync["cifra_json"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (pasta / "setsync_grade.json").write_text(
        json.dumps(resultado.setsync["grade_json"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (pasta / "setsync_upload.json").write_text(
        json.dumps(resultado.setsync, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def executar(
    url_cifras: str,
    pasta_saida: Path | None = None,
    youtube_url: str | None = None,
    compasso_manual: str | None = None,
) -> ResultadoPipeline:
    url_cifras = validar_url_cifra(url_cifras)
    dados = raspar_cifra(url_cifras)

    if not dados["cifra"]:
        raise ValueError("Não foi possível extrair a cifra da página.")

    if youtube_url:
        dados["youtube"] = normalizar_url_youtube(youtube_url)
        dados["youtube_manual"] = True
        video_id = re.search(r"v=([\w-]+)", dados["youtube"])
        vid = video_id.group(1) if video_id else ""
        dados["videos_youtube"] = [
            {
                "id": vid,
                "nome": "(informado pelo usuário)",
                "url": dados["youtube"],
            },
            *[
                v
                for v in dados.get("videos_youtube", [])
                if v.get("url") != dados["youtube"]
            ],
        ]
    elif not dados["youtube"]:
        raise ValueError(
            "Não foi possível encontrar link do YouTube para esta música. "
            "Use --youtube URL para informar o vídeo manualmente."
        )

    acordes_referencia = extrair_acordes_referencia(dados["cifra"])
    if not acordes_referencia:
        raise ValueError(
            "Não foi possível extrair acordes da cifra. "
            "Execute o pipeline após gerar cifra no formato [Acorde]."
        )

    nome_pasta = slugify(f"{dados['artista']}-{dados['titulo']}")
    pasta = pasta_saida or Path(settings.output_dir) / nome_pasta
    pasta.mkdir(parents=True, exist_ok=True)

    tmp_dir = Path(settings.tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    downloader = AudioDownloader(output_dir=tmp_dir)
    wav_path: Path | None = None
    try:
        wav_path = downloader.download_as_wav_mono_22050(dados["youtube"])
        mp3_path = pasta / f"{nome_pasta}.mp3"
        wav_para_mp3(wav_path, mp3_path)

        analise = AudioPipeline().run(wav_path)
        compasso_info: CompassoInfo = analise.compasso
        if compasso_manual:
            compasso_info = parsear_compasso(compasso_manual)

        grade_harmonica, _, acordes_no_tempo, partes_grade = montar_grade_da_cifra(
            dados["cifra"],
            acordes_referencia,
            len(analise.chords_by_beat),
            compasso=compasso_info,
        )
        grade_progressao = grade_compacta_da_cifra(
            acordes_referencia, compasso=compasso_info
        )
        tonalidade, tonalidade_estimada = resolver_tonalidade(
            dados.get("tom", ""), acordes_referencia
        )

        duracao_seg = None
        bpm = None
        try:
            import librosa

            y, sr = librosa.load(str(wav_path), sr=22050, mono=True)
            duracao_seg = int(len(y) / sr) if sr else None
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            if tempo:
                bpm = round(float(tempo), 1)
        except Exception:
            pass

        setsync = montar_pacote_setsync(
            titulo=dados["titulo"],
            artista=dados["artista"],
            tom_original=tonalidade,
            conteudo=dados["cifra"],
            partes_grade=partes_grade,
            bpm=bpm,
            duracao_seg=duracao_seg,
            url_cifra=url_cifras,
            url_youtube=dados["youtube"],
        )

        resultado = ResultadoPipeline(
            pasta=pasta,
            titulo=dados["titulo"],
            artista=dados["artista"],
            youtube=dados["youtube"],
            mp3=mp3_path,
            cifra=dados["cifra"],
            acordes_cifra=acordes_referencia,
            grade_harmonica=grade_harmonica,
            grade_progressao_cifra=grade_progressao,
            tonalidade=tonalidade,
            tonalidade_estimada=tonalidade_estimada,
            compasso=compasso_info.formula,
            partes_grade=partes_grade,
            setsync=setsync,
            bpm=bpm,
            duracao_seg=duracao_seg,
        )

        salvar_arquivos(pasta, dados, resultado)
        (pasta / "resumo.json").write_text(
            json.dumps(
                resumo_processamento(
                    acordes_referencia,
                    acordes_no_tempo,
                    len(analise.chords_by_beat),
                    compasso=compasso_info,
                ),
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return resultado
    finally:
        if wav_path and wav_path.exists():
            wav_path.unlink(missing_ok=True)
