import pandas as pd
from opensearchpy import OpenSearch, helpers

# Koneksi ke OpenSearch
client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_compress=True,
    use_ssl=False
)

def load_csv_to_opensearch(csv_filename, index_name):
    print(f"Membaca {csv_filename} dan memuat ke index '{index_name}'...")
    
    # 1. Baca data mentah dari CSV menggunakan Pandas
    df = pd.read_csv(csv_filename)
    
    # Menghapus index lama jika ada, lalu membuat yang baru
    if client.indices.exists(index=index_name):
        client.indices.delete(index=index_name)
    client.indices.create(index=index_name)
    
    # 2. Mengubah setiap baris DataFrame menjadi format JSON/Dictionary
    # Orient='records' akan secara otomatis mengubah tabel menjadi list of JSON
    records = df.to_dict(orient='records')
    
    # 3. Menyiapkan payload untuk Bulk API
    actions = [
        {
            "_index": index_name,
            "_source": record # record ini sudah berupa JSON objek
        }
        for record in records
    ]
    
    # 4. Load ke OpenSearch dengan Bulk API (Chunking otomatis)
    helpers.bulk(client, actions, chunk_size=500)
    print(f"Berhasil memuat {len(records)} dokumen ke index '{index_name}'!\n")

if __name__ == "__main__":
    # Mengeksekusi proses load untuk semua CSV
    load_csv_to_opensearch("backend\data\data_pasien.csv", "pasien")
    load_csv_to_opensearch("backend\data\data_dokter.csv", "dokter")
    load_csv_to_opensearch("backend\data\data_obat.csv", "obat")
    load_csv_to_opensearch("backend\data\data_kunjungan.csv", "kunjungan")
    load_csv_to_opensearch("backend\data\data_resep.csv", "resep")
    load_csv_to_opensearch("backend\data\data_tagihan.csv", "tagihan")
    
    print("Semua data berhasil di-load ke OpenSearch dalam format JSON!")