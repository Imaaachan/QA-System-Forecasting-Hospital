# 🏥 QA System & Forecasting - RS Sehat Selalu

Sistem ini dirancang untuk mendigitalisasi pencarian data operasional rumah sakit dan memberikan proyeksi kunjungan pasien menggunakan *Machine Learning*.
Repositori ini merupakan implementasi **Pilihan 1**, di mana seluruh data operasional ditransformasikan secara langsung ke dalam **OpenSearch**, dan Modul QA melakukan *query* pencarian secara *real-time* ke *index* OpenSearch.

✨ Fitur Utama
1. Interactive QA Chatbot: Antarmuka web interaktif yang mampu merespons pertanyaan bahasa natural terkait:
   - Pencarian profil pasien & dokter spesialis.
   - Pengecekan daftar obat dan tagihan tertinggi.
   - Statistik ringkasan pendapatan rumah sakit.
2. Predictive Forecasting: Implementasi model *Random Forest* untuk memprediksi lonjakan jumlah kunjungan pasien selama 30 hari ke depan berdasarkan data historis.
3. Data Dashboarding: Terintegrasi penuh dengan OpenSearch Dashboards untuk visualisasi data demografi, finansial, dan proyeksi masa depan.

🛠️ Teknologi yang Digunakan
- Database & Search Engine: OpenSearch v2.x (Port 9200)
- Backend Framework: FastAPI (Python) & Uvicorn (Port 8000)
- Machine Learning: Scikit-Learn (Random Forest Regressor), Pandas
- Frontend: HTML5, Vanilla JavaScript, CSS3

🚀 Cara Menjalankan Sistem Secara Lokal
1. Prasyarat
Pastikan komputer Anda sudah terinstal:
- Python 3.10+
- OpenSearch (Berjalan di latar belakang pada http://localhost:9200)
- Instalasi dependensi Python:

Bash
pip install fastapi uvicorn opensearch-py pandas scikit-learn

2. Ingesti Data & Forecasting
Buka terminal pada folder root (folder utama) proyek ini, dan jalankan skrip berikut untuk memasukkan data ke OpenSearch:

Bash
# Memasukkan data statis (pasien, dokter, tagihan, obat)
python backend/load_data.py

# Menjalankan model peramalan dan memuat prediksi ke OpenSearch
python backend/forecast_and_load.py

3. Menjalankan Backend Server
Jalankan server FastAPI menggunakan Uvicorn dari root folder:

Bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
(Server akan berjalan dan menunggu koneksi API pada port 8000).

4. Menjalankan Frontend
Navigasikan ke folder frontend di File Explorer, lalu buka file index.html menggunakan browser pilihan (seperti Google Chrome atau Microsoft Edge).

Proyek ini dikembangkan sebagai bentuk implementasi Sistem Manajemen Basis Data Terdistribusi dan Analitik Big Data Mata Kuliah ROBD.
