# Narasi panjang dengan referensi suara (lokal)

Script `scripts/narrate_long.py` memecah naskah panjang menjadi beberapa segmen, menghasilkan audio setiap segmen menggunakan **F5-TTS Indonesia** dengan referensi yang sama, lalu menggabungkannya ke **satu MP3**.

**Penting:** Ini menggunakan voice conditioning saat sintesis, **bukan melatih ulang model suara secara permanen**. Hasil tidak dijamin identik dengan sumber audio.

## Syarat

- Python 3.11 dan FFmpeg (lihat [README utama](../README.md)).
- GPU direkomendasikan. Model diunduh saat penggunaan pertama.
- Rekaman suara yang kamu punya izin untuk digunakan.

## Cara menggunakan

1. Simpan naskah teks (UTF-8) di komputer, misalnya `narasi_waktu.txt`.
2. Simpan rekaman MP3/WAV referensi hanya di komputer (jangan unggah ke GitHub publik).
3. Instal dependensi dari root repositori: `pip install -r requirements.txt`
4. Jalankan dari root repositori:

```bash
python scripts/narrate_long.py \
  --text narasi_waktu.txt \
  --reference "contoh_suara.mp3" \
  --output private/outputs/narasi_waktu.mp3 \
  --start 0 \
  --duration 6.3 \
  --speed 0.98
```

**Transkrip referensi** default adalah kalimat "Apel segar..." dari contoh audio sebelumnya. Jika memilih cuplikan lain, wajib sesuaikan `--reference-text` agar benar-benar cocok dengan ucapan di rentang referensi.

Script ini mempertahankan teks sumber tetapi menggabungkan kalimat ke segmen pendek. Gunakan `--max-chars 180` untuk segmen lebih singkat bila model kesulitan. File hasil MP3 ditulis secara lokal di lokasi `--output` dan tidak diunggah ke GitHub.
