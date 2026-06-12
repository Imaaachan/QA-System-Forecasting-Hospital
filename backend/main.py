from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from opensearchpy import OpenSearch

app = FastAPI(title="QA & Prediksi RS Sehat Selalu")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_compress=True,
    use_ssl=False
)

class PrediksiRequest(BaseModel):
    tanggal: str

class QuestionRequest(BaseModel):
    question: str

# ENDPOINT BARU: Untuk menarik total data ke Stats Bar Dashboard
@app.get("/stats")
def get_stats():
    return {
        "pasien": client.count(index="pasien")['count'],
        "dokter": client.count(index="dokter")['count'],
        "kunjungan": client.count(index="kunjungan")['count'],
        "obat": client.count(index="obat")['count'],
        "tagihan": client.count(index="tagihan")['count']
    }

@app.post("/prediksi")
def prediksi_kunjungan(request: PrediksiRequest):
    index_name = "prediksi_kunjungan"
    query = {"query": {"match": {"tanggal": request.tanggal}}}
    response = client.search(index=index_name, body=query)
    
    if response['hits']['total']['value'] > 0:
        return {"tanggal": request.tanggal, "estimasi_pasien": response['hits']['hits'][0]['_source']['estimasi_pasien']}
    return {"error": "Data prediksi tidak ditemukan."}

@app.post("/tanya")
def answer_question(request: QuestionRequest):
    question = request.question.lower()
    
    # PRIORITAS 1: FORECASTING / PREDIKSI (Ditaruh paling atas!)
    if any(word in question for word in ['prediksi', 'estimasi', 'minggu depan', 'bulan depan']):
        query = {"size": 30, "query": {"match_all": {}}, "sort": [{"tanggal": {"order": "asc"}}]}
        res = client.search(index="prediksi_kunjungan", body=query)
        hits = res['hits']['hits']
        if not hits:
            jawaban = "Maaf, data prediksi belum tersedia di sistem."
        else:
            total_minggu_depan = sum([hit['_source']['estimasi_pasien'] for hit in hits[:7]])
            jawaban = f"Prediksi total pasien untuk 7 hari ke depan akan mencapai **{total_minggu_depan} orang**.\n\nRincian 3 hari terdekat:\n"
            for hit in hits[:3]:
                jawaban += f"- {hit['_source']['tanggal']}: ~{hit['_source']['estimasi_pasien']} pasien\n"

    # PRIORITAS 2: PASIEN
    elif any(word in question for word in ['pasien', 'nama pasien']):
        res = client.search(index="pasien", body={"size": 100, "query": {"match_all": {}}})
        hits = res['hits']['hits']
        if not hits:
            jawaban = "Belum ada data pasien di sistem."
        elif 'total' in question or 'berapa' in question:
            jawaban = f"Total pasien yang ada di rumah sakit adalah {client.count(index='pasien')['count']} orang."
        else:
            jawaban = f"Menampilkan daftar pasien:\n\n"
            for hit in hits[:10]:
                src = hit['_source']
                jawaban += f"- {src.get('nama')} (JK: {src.get('jenis_kelamin')}, Gol. Darah: {src.get('golongan_darah')})\n"
                
    # PRIORITAS 3: DOKTER
    elif any(word in question for word in ['dokter', 'spesialis']):
        if 'kardiologi' in question:
            res = client.search(index="dokter", body={"query": {"match": {"spesialisasi": "Kardiologi"}}})
            jawaban = f"Dokter spesialis Kardiologi:\n\n"
            for hit in res['hits']['hits']:
                jawaban += f"- {hit['_source'].get('nama')}\n"
        elif 'neurologi' in question:
            res = client.search(index="dokter", body={"query": {"match": {"spesialisasi": "Neurologi"}}})
            jawaban = f"Dokter spesialis Neurologi:\n\n"
            for hit in res['hits']['hits']:
                jawaban += f"- {hit['_source'].get('nama')}\n"
        elif 'total' in question or 'berapa' in question:
            total_dokter = client.count(index="dokter")['count']
            jawaban = f"Total dokter yang ada di Rumah Sakit Sehat Selalu adalah **{total_dokter} dokter**."
        else:
            res = client.search(index="dokter", body={"size": 10, "query": {"match_all": {}}})
            jawaban = "Menampilkan daftar dokter:\n\n"
            for hit in res['hits']['hits']:
                jawaban += f"- {hit['_source'].get('nama')} - Spesialisasi {hit['_source'].get('spesialisasi')}\n"

    # PRIORITAS 4: OBAT
    elif any(word in question for word in ['obat', 'farmasi', 'harga obat']):
        res = client.search(index="obat", body={"size": 100, "query": {"match_all": {}}})
        hits = res['hits']['hits']
        if not hits:
            jawaban = "Belum ada data obat."
        elif 'total' in question or 'berapa' in question:
            jawaban = f"Terdapat {client.count(index='obat')['count']} jenis obat di sistem."
        else:
            jawaban = f"Daftar beberapa obat beserta harganya:\n\n"
            for hit in hits[:10]:
                src = hit['_source']
                jawaban += f"- {src.get('nama_obat')} ({src.get('jenis_obat')}) - Rp{src.get('harga')}\n"

    # PRIORITAS 5: TAGIHAN
    elif any(word in question for word in ['tagihan', 'biaya', 'bayar']):
        res = client.search(index="tagihan", body={"size": 10, "query": {"match_all": {}}, "sort": [{"total_biaya": {"order": "desc"}}]})
        hits = res['hits']['hits']
        if not hits:
            jawaban = "Belum ada data tagihan."
        elif 'tertinggi' in question: 
            src = hits[0]['_source']
            jawaban = f"Tagihan tertinggi adalah Rp{src.get('total_biaya')} pada kunjungan {src.get('id_kunjungan')}."
        else:
            jawaban = f"Beberapa tagihan dengan nilai tertinggi:\n\n"
            for hit in hits[:5]:
                src = hit['_source']
                jawaban += f"- Kunjungan {src.get('id_kunjungan')}: Rp{src.get('total_biaya')} ({src.get('metode_bayar')})\n"

    # PRIORITAS 6: STATISTIK
    elif any(word in question for word in ['statistik', 'ringkasan']):
        total_pasien = client.count(index="pasien")['count']
        total_dokter = client.count(index="dokter")['count']
        total_kunjungan = client.count(index="kunjungan")['count']
        total_obat = client.count(index="obat")['count']
        jawaban = f"Statistik RS:\n- Total Pasien: {total_pasien}\n- Dokter: {total_dokter}\n- Kunjungan: {total_kunjungan}\n- Obat: {total_obat}"

    else:
        jawaban = "Maaf, sistem belum mengenali pertanyaan tersebut."

    return {"pertanyaan": request.question, "jawaban": jawaban}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)