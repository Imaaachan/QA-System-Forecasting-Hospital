import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from opensearchpy import OpenSearch, helpers

print("1. Membaca data historis dari data_kunjungan.csv...")
# Menggunakan nama file yang baru kita generate
df = pd.read_csv("backend\data\data_kunjungan.csv")
df['tanggal_masuk'] = pd.to_datetime(df['tanggal_masuk'])

# Mengagregasi data: Menghitung total kunjungan per hari
daily_visits = df.groupby('tanggal_masuk').size().reset_index(name='jumlah_pasien')

print("2. Melakukan Feature Engineering...")
# Mengekstrak pola waktu agar model Machine Learning paham
daily_visits['day_of_week'] = daily_visits['tanggal_masuk'].dt.dayofweek
daily_visits['month'] = daily_visits['tanggal_masuk'].dt.month
daily_visits['day'] = daily_visits['tanggal_masuk'].dt.day

print("3. Melatih Model Random Forest...")
X = daily_visits[['day_of_week', 'month', 'day']]
y = daily_visits['jumlah_pasien']

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

print("4. Memprediksi volume pasien untuk 30 hari ke depan...")
last_date = daily_visits['tanggal_masuk'].max()
future_dates = [last_date + timedelta(days=i) for i in range(1, 31)]

future_df = pd.DataFrame({'tanggal_masuk': future_dates})
future_df['day_of_week'] = future_df['tanggal_masuk'].dt.dayofweek
future_df['month'] = future_df['tanggal_masuk'].dt.month
future_df['day'] = future_df['tanggal_masuk'].dt.day

predictions = model.predict(future_df[['day_of_week', 'month', 'day']])
future_df['estimasi_pasien'] = predictions.astype(int)

print("5. Mengirim hasil prediksi ke OpenSearch...")
client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_compress=True,
    use_ssl=False
)

index_name = "prediksi_kunjungan"

# Hapus index lama jika ada
if client.indices.exists(index=index_name):
    client.indices.delete(index=index_name)
client.indices.create(index=index_name)

# Siapkan data prediksi untuk OpenSearch
actions = []
for index, row in future_df.iterrows():
    action = {
        "_index": index_name,
        "_source": {
            "tanggal": row['tanggal_masuk'].strftime("%Y-%m-%d"),
            "estimasi_pasien": row['estimasi_pasien']
        }
    }
    actions.append(action)

# Bulk insert
helpers.bulk(client, actions)
print("Selesai! Hasil prediksi 30 hari ke depan berhasil disimpan ke index 'prediksi_kunjungan'.")