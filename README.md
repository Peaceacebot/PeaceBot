# PeaceBot - Forex Signal Bot (XAU/USD)

PeaceBot adalah bot Telegram yang memberikan sinyal beli/jual otomatis berdasarkan indikator RSI, MACD, dan EMA pada pair XAU/USD.

## Fitur
- Kirim sinyal beli/jual otomatis setiap 15 menit
- Sinyal dikirim hanya saat arah tren berubah
- Perintah manual: `/start`, `/info`, `/sinyal`

## Cara Deploy (Gratis)
1. Fork atau upload ke GitHub repo ini
2. Buat akun di [Render](https://render.com)
3. Klik "New Web Service" → Hubungkan ke repo PeaceBot
4. Atur Environment Variables:
   - `TOKEN` = Token dari @BotFather
   - `CHAT_ID` = ID pengguna Telegram (gunakan @userinfobot)

Bot akan langsung aktif dan berjalan otomatis 24/7.

## Indikator yang digunakan
- RSI (reversal di bawah 30 / di atas 70)
- MACD crossover
- EMA crossover (12/26)
