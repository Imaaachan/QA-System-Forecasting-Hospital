import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_kunjungan_data(start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    data = []
    
    kunjungan_id = 1
    for current_date in date_range:
        # Pola: Hari kerja lebih ramai dari akhir pekan
        if current_date.weekday() < 5:  # Senin - Jumat
            base_visits = np.random.randint(20, 50)
            if current_date.weekday() == 0: # Senin biasanya paling ramai
                base_visits += np.random.randint(10, 20)
        else:  # Sabtu - Minggu
            base_visits = np.random.randint(5, 15)
            
        # Menambahkan sedikit noise (variabilitas acak)
        noise = np.random.randint(-5, 5)
        total_visits = max(1, base_visits + noise)
        
        for _ in range(total_visits):
            data.append({
                "id_kunjungan": f"K-{kunjungan_id:05d}",
                "tanggal_masuk": current_date.strftime("%Y-%m-%d"),
                "status": "Selesai"
            })
            kunjungan_id += 1
            
    df = pd.DataFrame(data)
    df.to_csv("data_kunjungan_historis.csv", index=False)
    print(f"Berhasil membuat {len(df)} data kunjungan dari {start_date} hingga {end_date}.")
    return df

# Eksekusi pembuatan data untuk 2 tahun terakhir
if __name__ == "__main__":
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730) # 2 tahun lalu
    generate_kunjungan_data(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))