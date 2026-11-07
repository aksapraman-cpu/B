# NaratorID TTS — Text to Speech Bahasa Indonesia

Aplikasi Gradio untuk mengubah teks menjadi narasi bahasa Indonesia dengan gaya tenang, jelas, sedikit *breathy*, dan jeda natural.

## Fitur
- **Lokal — F5-TTS Indonesia:** gunakan cuplikan suara sendiri (3–11 detik) dan transkrip yang cocok sebagai referensi karakter suara.
- **ElevenLabs — Voice ID:** gunakan API key dan Voice ID yang sudah ada di akun ElevenLabs; mode ini **tidak** menggunakan audio referensi untuk cloning.
- Hasil MP3, serta WAV dalam mode lokal.

## Jalankan versi HTML di HP (tanpa Python)

Versi HTML ada di [index.html](./index.html). Ini adalah TTS yang memanfaatkan fitur suara dari browser/HP; **bukan voice clone dari audio contoh** dan tidak menghasilkan MP3. Untuk model suara yang mirip audio referensi, gunakan backend Python di bawah ini.

Untuk mengakses sebagai website (sekali pengaturan):
1. Buka **Settings → Pages** di repositori ini: https://github.com/aksapraman-cpu/B/settings/pages
2. Pada **Build and deployment**, pilih **Deploy from a branch**.
3. Pilih branch **main** dan folder **/(root)**, lalu klik **Save**.
4. Setelah halaman terbit, akses **https://aksapraman-cpu.github.io/B/** lewat Chrome di HP.

Catatan: tautan GitHub Pages di atas **belum diverifikasi aktif** sampai pengaturan Pages selesai.

## Jalankan di komputer
Memerlukan Python **3.11**, FFmpeg dalam PATH, dan koneksi internet untuk unduhan model awal. CPU bisa sangat lambat; GPU direkomendasikan. Untuk mode lokal, siapkan memori yang cukup.

```bash
python -m venv .venv
# Aktifkan venv:
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Buka **http://127.0.0.1:7860** di komputer tempat aplikasi dijalankan.

## Referensi suara
Untuk audio referensi yang dipakai saat membuat proyek ini, gunakan cuplikan sekitar **6,3 detik** dan transkrip:

> Apel segar yang baru saja kamu beli di supermarket, kemungkinan besar sudah dipetik satu tahun yang lalu.

**Jangan unggah rekaman pribadi, API key, output, atau checkpoint model ke repositori publik.** Referensi suara diunggah hanya ketika kamu menjalankan aplikasi, bukan disimpan dalam GitHub. Jangan gunakan suara orang lain tanpa izin.

Model lokal akan diunduh otomatis pada penggunaan pertama dari `Eempostor/F5-TTS-INDO-FINETUNE-V2` (sekitar 1,35 GB untuk checkpoint; belum termasuk paket lain).

## Ketentuan
- Model [F5-TTS-INDO-FINETUNE-V2](https://huggingface.co/Eempostor/F5-TTS-INDO-FINETUNE-V2) menggunakan lisensi **CC BY-NC 4.0** (nonkomersial). Periksa lisensi dan izin penggunaan sebelum menerbitkan atau memonetisasi konten.
- Integrasi ElevenLabs memerlukan API key dan Voice ID sendiri serta bisa memiliki kuota/biaya.
- GitHub adalah penyimpanan kode, **bukan server untuk menjalankan UI Gradio**. Aplikasi belum dihosting online. Untuk website publik dibutuhkan hosting terpisah.
- Kode belum diverifikasi menghasilkan audio di server; perlu dijalankan dengan model atau API key yang sesuai.

## Struktur
`app.py` antarmuka, `engine.py` sintesis, `requirements.txt` dependensi, `tests/test_engine.py` tes utilitas, `.gitignore` proteksi file pribadi.
