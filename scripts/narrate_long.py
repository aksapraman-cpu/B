"""Render naskah panjang menjadi satu MP3 dengan referensi suara F5-TTS lokal.

Prasyarat: pip install -r requirements.txt, FFmpeg, checkpoint F5-TTS.
Jangan commit file rekaman, API key, atau hasil sintesis ke GitHub publik.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import tempfile

from pydub import AudioSegment

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import get_f5  # noqa: E402

DEFAULT_REF_TEXT = (
    "Apel segar yang baru saja kamu beli di supermarket, "
    "kemungkinan besar sudah dipetik satu tahun yang lalu."
)


def split_narration(text: str, limit: int = 240) -> list[str]:
    """Split on natural sentence boundaries; never exceed limit."""
    if not 80 <= limit <= 600:
        raise ValueError("Panjang segmen harus antara 80 hingga 600 karakter.")
    text = text.strip()
    if not text:
        raise ValueError("File naskah kosong.")

    units: list[str] = []
    paragraphs = re.split(r"\n\s*\n", text)
    for paragraph in paragraphs:
        paragraph = " ".join(paragraph.split())
        if not paragraph:
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
            if not sentence:
                continue
            if len(sentence) <= limit:
                units.append(sentence)
            else:
                # Unusually long sentence: wrap at spaces.
                words = sentence.split()
                segment = ""
                for word in words:
                    candidate = f"{segment} {word}".strip()
                    if len(candidate) > limit and segment:
                        units.append(segment)
                        segment = word
                    elif len(word) > limit:
                        raise ValueError("Satu kata lebih panjang dari batas segmen.")
                    else:
                        segment = candidate
                if segment:
                    units.append(segment)

    chunks: list[str] = []
    segment = ""
    for sentence in units:
        candidate = f"{segment} {sentence}".strip()
        if len(candidate) > limit and segment:
            chunks.append(segment)
            segment = sentence
        else:
            segment = candidate
    if segment:
        chunks.append(segment)
    return chunks


def render(
    text_file: Path,
    reference_file: Path,
    output_file: Path,
    transcript: str,
    start_seconds: float,
    clip_seconds: float,
    speed: float,
    steps: int,
    max_chars: int,
) -> tuple[int, float]:
    if not text_file.is_file() or not reference_file.is_file():
        raise ValueError("File naskah atau rekaman referensi tidak ditemukan.")
    if not 3 <= clip_seconds <= 11 or start_seconds < 0:
        raise ValueError("Pilih durasi referensi 3–11 detik dan start >= 0.")
    if not 0.75 <= speed <= 1.3 or not 16 <= steps <= 64:
        raise ValueError("Parameter sintesis tidak valid.")
    if not transcript.strip():
        raise ValueError("Transkrip referensi tidak boleh kosong.")
    chunks = split_narration(text_file.read_text(encoding="utf-8"), max_chars)

    with tempfile.TemporaryDirectory(prefix="naratorid_") as tmp:
        tmp_dir = Path(tmp)
        raw = AudioSegment.from_file(reference_file)
        start_ms = round(start_seconds * 1000)
        end_ms = start_ms + round(clip_seconds * 1000)
        if end_ms > len(raw):
            raise ValueError("Rentang referensi melebihi durasi rekaman.")
        ref_wav = tmp_dir / "reference.wav"
        raw[start_ms:end_ms].set_channels(1).set_frame_rate(24000).export(
            ref_wav, format="wav"
        )

        model = get_f5()  # Muat model satu kali untuk semua segmen.
        combined = AudioSegment.empty()
        for i, part in enumerate(chunks, start=1):
            wav_path = tmp_dir / f"seg_{i:03d}.wav"
            print(f"[{i}/{len(chunks)}] Sintesis {len(part)} karakter...", flush=True)
            model.infer(
                ref_file=str(ref_wav),
                ref_text=transcript.strip(),
                gen_text=part,
                speed=float(speed),
                nfe_step=int(steps),
                cross_fade_duration=0.15,
                file_wave=str(wav_path),
                show_info=lambda _: None,
            )
            if not wav_path.exists():
                raise RuntimeError(f"Model tidak menghasilkan audio segmen ke-{i}.")
            combined += AudioSegment.from_wav(wav_path)
            if i < len(chunks):
                combined += AudioSegment.silent(duration=280, frame_rate=24000)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        combined.set_channels(1).export(
            output_file, format="mp3", bitrate="192k"
        )
        return len(chunks), len(combined) / 1000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True, type=Path, help="Path naskah .txt UTF-8")
    parser.add_argument("--reference", required=True, type=Path, help="Path MP3/WAV contoh suara")
    parser.add_argument("--output", default=Path("private/outputs/narasi_waktu.mp3"), type=Path)
    parser.add_argument("--reference-text", default=DEFAULT_REF_TEXT)
    parser.add_argument("--start", default=0.0, type=float, help="Awal cuplikan (detik)")
    parser.add_argument("--duration", default=6.3, type=float, help="Durasi cuplikan (3–11 detik)")
    parser.add_argument("--speed", default=0.98, type=float)
    parser.add_argument("--steps", default=32, type=int)
    parser.add_argument("--max-chars", default=240, type=int)
    args = parser.parse_args()
    segments, duration = render(
        text_file=args.text,
        reference_file=args.reference,
        output_file=args.output,
        transcript=args.reference_text,
        start_seconds=args.start,
        clip_seconds=args.duration,
        speed=args.speed,
        steps=args.steps,
        max_chars=args.max_chars,
    )
    print(f"MP3 selesai: {args.output} ({segments} segmen, {duration:.1f} detik)")


if __name__ == "__main__":
    main()
