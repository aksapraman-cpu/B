"""Backend sintesis NaratorID: F5-TTS Indonesia / ElevenLabs."""
from __future__ import annotations
import functools
from pathlib import Path
import uuid
from pydub import AudioSegment

MODEL_REPO = "Eempostor/F5-TTS-INDO-FINETUNE-V2"
ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models" / "f5-indo"
OUTPUT_DIR = ROOT / "private" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def validate_input(text: str, ref_text: str | None = None) -> str:
    text = (text or "").strip()
    if not text:
        raise ValueError("Masukkan teks yang ingin diubah menjadi suara.")
    if len(text) > 3500:
        raise ValueError("Maksimum 3.500 karakter per proses.")
    if ref_text is not None and not (ref_text or "").strip():
        raise ValueError("Isi transkrip yang sesuai audio referensi.")
    return text

def reference_clip_ms(seconds: float, available_ms: int) -> int:
    if not 3 <= seconds <= 11:
        raise ValueError("Durasi referensi harus 3–11 detik.")
    if available_ms < 2500:
        raise ValueError("Referensi terlalu singkat.")
    return min(round(seconds * 1000), available_ms)

def prepare_reference(audio_path: str, seconds: float, output_path: str) -> str:
    src = Path(audio_path)
    if not src.is_file():
        raise ValueError("Unggah MP3/WAV referensi dulu.")
    audio = AudioSegment.from_file(src)
    length = reference_clip_ms(seconds, len(audio))
    audio[:length].set_channels(1).set_frame_rate(24000).export(output_path, format="wav")
    return output_path

def ensure_model_files() -> tuple[str, str]:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint = MODEL_DIR / "f5_tts_indo_v2.pt"
    vocab = MODEL_DIR / "vocab.txt"
    if not checkpoint.exists() or not vocab.exists():
        from huggingface_hub import hf_hub_download
        for file in ("f5_tts_indo_v2.pt", "vocab.txt"):
            hf_hub_download(repo_id=MODEL_REPO, filename=file, local_dir=str(MODEL_DIR))
    return str(checkpoint), str(vocab)

@functools.lru_cache(maxsize=1)
def get_f5():
    from f5_tts.api import F5TTS
    ckpt, vocab = ensure_model_files()
    return F5TTS(model="F5TTS_v1_Base", ckpt_file=ckpt, vocab_file=vocab)

def generate_local(text, reference_path, transcript, ref_seconds=6.3, speed=0.98, steps=32):
    text = validate_input(text, transcript)
    if not reference_path:
        raise ValueError("Unggah audio referensi dulu.")
    if not 0.75 <= speed <= 1.3 or not 16 <= steps <= 64:
        raise ValueError("Parameter generasi di luar batas.")
    job = uuid.uuid4().hex[:12]
    ref = OUTPUT_DIR / f"ref_{job}.wav"
    wav = OUTPUT_DIR / f"narasi_{job}.wav"
    mp3 = OUTPUT_DIR / f"narasi_{job}.mp3"
    try:
        prepare_reference(reference_path, ref_seconds, str(ref))
        get_f5().infer(
            ref_file=str(ref), ref_text=transcript.strip(), gen_text=text,
            speed=float(speed), nfe_step=int(steps), cross_fade_duration=0.15,
            file_wave=str(wav), show_info=lambda _: None,
        )
        AudioSegment.from_wav(wav).export(mp3, format="mp3", bitrate="192k")
        return str(mp3), str(wav), str(mp3)
    finally:
        ref.unlink(missing_ok=True)

def generate_elevenlabs(text, api_key, voice_id, speed=0.98, stability=0.5, similarity=0.75):
    import requests
    text = validate_input(text)
    if not (api_key or "").strip() or not (voice_id or "").strip():
        raise ValueError("Masukkan API key dan Voice ID ElevenLabs.")
    if not 0.75 <= speed <= 1.3:
        raise ValueError("Kecepatan di luar batas.")
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id.strip()}",
        params={"output_format": "mp3_44100_128"},
        headers={"xi-api-key": api_key.strip(), "Content-Type": "application/json"},
        json={"text": text, "model_id": "eleven_multilingual_v2",
              "voice_settings": {"stability": float(stability),
                                 "similarity_boost": float(similarity),
                                 "speed": float(speed)}},
        timeout=180,
    )
    if not response.ok:
        raise ValueError(f"ElevenLabs HTTP {response.status_code}. Periksa key, Voice ID dan kuota.")
    if not response.headers.get("content-type", "").startswith("audio/") and response.content[:3] != b"ID3":
        raise ValueError("Respons ElevenLabs bukan berkas audio.")
    path = OUTPUT_DIR / f"elevenlabs_{uuid.uuid4().hex[:12]}.mp3"
    path.write_bytes(response.content)
    return str(path), None, str(path)
