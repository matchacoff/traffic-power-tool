# Gunakan base image Python yang umum
FROM python:3.10-slim

# Atur direktori kerja di dalam container
WORKDIR /app

# Salin file requirements terlebih dahulu untuk caching
COPY requirements.txt .

# Install dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# --- INI BAGIAN PENTING ---
# Jalankan instalasi Playwright beserta dependensinya sebagai langkah build terpisah
# Ini akan memakan waktu pada build pertama, tetapi akan di-cache untuk build selanjutnya
RUN playwright install --with-deps

# Salin sisa kode aplikasi Anda ke dalam container
COPY . .

# Beri tahu Railway port mana yang akan diekspos oleh aplikasi
EXPOSE 8000

# Perintah untuk menjalankan aplikasi Streamlit saat container dimulai
# Railway akan secara otomatis menggunakan $PORT yang benar
CMD streamlit run app.py --server.port $PORT --server.headless true