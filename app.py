"""Antarmuka Gradio NaratorID TTS."""
import gradio as gr
from engine import generate_local, generate_elevenlabs

SAMPLE_TRANSCRIPT = ("Apel segar yang baru saja kamu beli di supermarket, "
                     "kemungkinan besar sudah dipetik satu tahun yang lalu.")
EXAMPLE_TEXT = ("Pernahkah kamu bertanya mengapa langit berubah warna saat matahari terbenam? "
                "Jawabannya lebih menarik daripada yang kita bayangkan.")

def synthesize(mode, text, audio_file, ref_text, ref_duration, speed, steps,
               api_key, voice_id, stability, similarity, permission):
    if not permission:
        raise gr.Error("Pastikan kamu memiliki izin menggunakan suara referensi/Voice ID.")
    try:
        if mode == "Lokal · F5-TTS Indonesia":
            return generate_local(text, audio_file, ref_text,
                                  ref_seconds=ref_duration, speed=speed, steps=steps)
        return generate_elevenlabs(text, api_key, voice_id, speed, stability, similarity)
    except Exception as exc:
        raise gr.Error(str(exc)) from None

with gr.Blocks(title="NaratorID · Teks ke Suara") as demo:
    gr.Markdown("# 🎙️ NaratorID — Text to Speech Bahasa Indonesia\n"
                "Narasi tenang, jelas, ekspresif, sedikit breathy. "
                "Gunakan cuplikan audio untuk mode lokal, atau Voice ID untuk ElevenLabs.")
    mode = gr.Radio(["Lokal · F5-TTS Indonesia", "ElevenLabs · Voice ID"],
                    value="Lokal · F5-TTS Indonesia", label="Mesin suara")
    with gr.Row():
        with gr.Column(scale=3):
            script = gr.Textbox(label="Naskah narasi", value=EXAMPLE_TEXT,
                                lines=8, info="Maksimum 3.500 karakter per proses")
            with gr.Group(visible=True) as local_section:
                gr.Markdown("### Mode lokal — Referensi suara")
                reference = gr.Audio(label="Unggah MP3/WAV contoh suara",
                                     sources=["upload"], type="filepath")
                ref_text = gr.Textbox(label="Transkrip tepat dari cuplikan audio",
                                      value=SAMPLE_TRANSCRIPT, lines=3)
                duration = gr.Slider(3, 11, value=6.3, step=0.1,
                                     label="Durasi awal referensi (detik)")
                steps = gr.Slider(16, 64, value=32, step=4, label="NFE steps")
            with gr.Group(visible=False) as eleven_section:
                gr.Markdown("### ElevenLabs (memerlukan Voice ID yang sudah dimiliki)")
                api_key = gr.Textbox(label="API key ElevenLabs", type="password")
                voice_id = gr.Textbox(label="Voice ID ElevenLabs")
                stability = gr.Slider(0, 1, value=0.5, step=0.05, label="Stability")
                similarity = gr.Slider(0, 1, value=0.75, step=0.05,
                                       label="Similarity boost")
        with gr.Column(scale=2):
            speed = gr.Slider(0.75, 1.3, value=0.98, step=0.01,
                              label="Kecepatan bicara")
            permission = gr.Checkbox(label="Saya berhak menggunakan suara referensi ini.")
            generate = gr.Button("🎧 Buat suara", variant="primary")
            result_audio = gr.Audio(label="Putar hasil", type="filepath")
            output_wav = gr.File(label="Unduh WAV (lokal)")
            output_mp3 = gr.File(label="Unduh MP3")
            gr.Markdown("Mode lokal mengunduh model pada penggunaan pertama. "
                        "GPU direkomendasikan. Hasil tidak dijamin identik dengan contoh.")

    def switch_mode(value):
        return gr.update(visible=value.startswith("Lokal")), gr.update(
            visible=value.startswith("ElevenLabs"))

    mode.change(switch_mode, inputs=mode, outputs=[local_section, eleven_section])
    generate.click(synthesize,
                   inputs=[mode, script, reference, ref_text, duration, speed,
                           steps, api_key, voice_id, stability, similarity, permission],
                   outputs=[result_audio, output_wav, output_mp3])
    gr.Markdown("Model lokal: CC BY-NC 4.0 (nonkomersial). Gunakan suara dengan izin.")

if __name__ == "__main__":
    demo.queue(max_size=10, default_concurrency_limit=1).launch(
        server_name="127.0.0.1", server_port=7860, share=False)
