import random
import pandas as pd
from datetime import datetime, timedelta

def generate_hospital_data(start_date_str, days=730):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    # 1. GENERATE MASTER DATA
    # ---------------------------------------------------------
    # a. Data Pasien (Misal kita buat 1000 pasien unik)
    pasien_data = []
    for i in range(1, 1001):
        pasien_data.append({
            "id_pasien": f"P-{i:03d}",
            "nama": f"Pasien_{i}",
            "tanggal_lahir": (datetime(1960, 1, 1) + timedelta(days=random.randint(0, 20000))).strftime("%Y-%m-%d"),
            "jenis_kelamin": random.choice(["L", "P"]),
            "golongan_darah": random.choice(["A", "B", "AB", "O"]),
            "alamat": f"Jl. Simulasi No. {i}",
            "no_telepon": f"0812{random.randint(1000000, 9999999)}"
        })
        
    # b. Data Dokter (Misal kita buat 100 dokter)
    spesialisasi_list = ["Kardiologi", "Neurologi", "Umum", "Anak", "Penyakit Dalam", "Bedah"]
    dokter_data = []
    for i in range(1, 101):
        dokter_data.append({
            "id_dokter": f"D-{i:03d}",
            "nama": f"dr. Dokter_{i}",
            "spesialisasi": random.choice(spesialisasi_list),
            "no_telepon": f"0813{random.randint(1000000, 9999999)}"
        })
        
    # c. Data Obat (Misal kita buat 200 jenis obat)
    obat_data = []
    for i in range(1, 201):
        obat_data.append({
            "id_obat": f"OB-{i:03d}",
            "nama_obat": f"Obat_{i}",
            "jenis_obat": random.choice(["Tablet", "Sirup", "Kapsul", "Salep"]),
            "harga": random.randint(10, 250) * 1000  # Harga antara 10rb - 250rb
        })

    # 2. GENERATE TRANSACTIONAL DATA (Selama 2 Tahun)
    # ---------------------------------------------------------
    kunjungan_data = []
    resep_data = []
    tagihan_data = []
    
    id_kunj_counter = 1
    id_resep_counter = 1
    id_tagihan_counter = 1
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        
        # Logika keramaian: Senin-Jumat ramai, Sabtu-Minggu sepi
        if current_date.weekday() < 5:
            daily_visits = random.randint(20, 50)
        else:
            daily_visits = random.randint(5, 15)
            
        for _ in range(daily_visits):
            id_kunjungan = f"K-{id_kunj_counter:05d}"
            p_selected = random.choice(pasien_data)
            d_selected = random.choice(dokter_data)
            
            # -- Tabel Kunjungan --
            kunjungan_data.append({
                "id_kunjungan": id_kunjungan,
                "id_pasien": p_selected["id_pasien"],
                "id_dokter": d_selected["id_dokter"],
                "tanggal_masuk": current_date.strftime("%Y-%m-%d"),
                "diagnosis": f"Diagnosis_{random.randint(1, 50)}"
            })
            
            # -- Tabel Resep (1 kunjungan bisa ada 1-3 resep obat) --
            total_biaya_obat = 0
            for _ in range(random.randint(1, 3)):
                o_selected = random.choice(obat_data)
                jumlah_obat = random.randint(1, 3)
                total_biaya_obat += (o_selected["harga"] * jumlah_obat)
                
                resep_data.append({
                    "id_resep": f"R-{id_resep_counter:05d}",
                    "id_kunjungan": id_kunjungan,
                    "id_obat": o_selected["id_obat"],
                    "jumlah": jumlah_obat
                })
                id_resep_counter += 1
            
            # -- Tabel Tagihan --
            biaya_konsultasi = 150000
            tagihan_data.append({
                "id_tagihan": f"T-{id_tagihan_counter:05d}",
                "id_kunjungan": id_kunjungan,
                "total_biaya": biaya_konsultasi + total_biaya_obat,
                "metode_bayar": random.choice(["BPJS", "Asuransi Swasta", "Tunai"]),
                "status": "Lunas"
            })
            
            id_kunj_counter += 1
            id_tagihan_counter += 1

    # 3. EXPORT KE CSV UNTUK DI-LOAD KE OPENSEARCH NANTI
    # ---------------------------------------------------------
    pd.DataFrame(pasien_data).to_csv("data_pasien.csv", index=False)
    pd.DataFrame(dokter_data).to_csv("data_dokter.csv", index=False)
    pd.DataFrame(obat_data).to_csv("data_obat.csv", index=False)
    pd.DataFrame(kunjungan_data).to_csv("data_kunjungan.csv", index=False)
    pd.DataFrame(resep_data).to_csv("data_resep.csv", index=False)
    pd.DataFrame(tagihan_data).to_csv("data_tagihan.csv", index=False)
    
    print(f"Berhasil men-generate data dengan relasi yang konsisten!")
    print(f"- Pasien: {len(pasien_data)}")
    print(f"- Dokter: {len(dokter_data)}")
    print(f"- Obat: {len(obat_data)}")
    print(f"- Kunjungan: {len(kunjungan_data)}")
    print(f"- Resep: {len(resep_data)}")
    print(f"- Tagihan: {len(tagihan_data)}")

# Eksekusi generator untuk data mulai dari 2 tahun yang lalu
if __name__ == "__main__":
    start = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
    generate_hospital_data(start_date_str=start, days=730)