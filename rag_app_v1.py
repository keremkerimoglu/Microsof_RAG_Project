import sqlite3
import json
import time
import logging
import numpy as np
import foundry_local_sdk as foundry_local

logging.basicConfig(
    filename='rag_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BENZERLIK_ESIGI = 0.50

def kosinus_benzerligi(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def en_benzer_parcalari_bul(sorgu_vektoru, top_k=3):
    conn = sqlite3.connect('knowledge_base.db')
    cursor = conn.cursor()
    cursor.execute("SELECT content, embedding, source FROM documents")
    satirlar = cursor.fetchall()
    conn.close()

    benzerlikler = []
    for content, embedding_json, source in satirlar:
        db_vektor = json.loads(embedding_json)
        skor = kosinus_benzerligi(sorgu_vektoru, db_vektor)
        benzerlikler.append((skor, content, source))

    benzerlikler.sort(key=lambda x: x[0], reverse=True)
    filtreli = [b for b in benzerlikler if b[0] >= BENZERLIK_ESIGI]
    return filtreli[:top_k]

def rag_asistani_baslat():
    print("Yapay zeka asistanı ve modeller yükleniyor, lütfen bekleyin...")
    config = foundry_local.Configuration(app_name="local_Asistan")
    manager = foundry_local.FoundryLocalManager(config)

    tum_modeller = manager.catalog.list_models()

    emb_model = None
    for m in tum_modeller:
        isim = str(getattr(m, 'name', '') or getattr(m, 'id', ''))
        if "qwen3-embedding-0.6b" in isim:
            emb_model = m
            break

    if emb_model:
        emb_model.download()
        emb_model.load()
        emb_client = emb_model.get_embedding_client()

    chat_model = None
    for m in tum_modeller:
        isim = str(getattr(m, 'name', '') or getattr(m, 'id', '')).lower()
        if "qwen2.5-7b-instruct" in isim:
            chat_model = m
            break

    if chat_model:
        model_adi = getattr(chat_model, 'name', '') or getattr(chat_model, 'id', 'Bilinmeyen Model')
        print(f"Sohbet modeli başarıyla bulundu: {model_adi}")
        chat_model.download()
        chat_model.load()
        chat_client = chat_model.get_chat_client()
    else:
        print("7B Modeli bulunamadı! Lütfen katalogunuzu kontrol edin.")
        return

    print("\n" + "="*50)
    print("Yerel RAG Asistanı Hazır! (Yüksek Doğruluklu 7B Sürümü)")
    print("Çıkmak için 'q' veya 'çıkış' yazın.")
    print("="*50)

    while True:
        kullanici_sorusu = input("\nSoru sor: ").strip()

        if kullanici_sorusu.lower() in ['q', 'çıkış', 'cikis', 'exit', 'quit']:
            print("Asistan: Görüşmek üzere! Sistem kapatılıyor...")
            break
        if not kullanici_sorusu:
            continue

        toplam_baslangic = time.perf_counter()

        try:
            embedding_baslangic = time.perf_counter()
            sorgu_yanit = emb_client.generate_embedding(kullanici_sorusu)
            sorgu_vec = sorgu_yanit.data[0].embedding
            embedding_suresi = time.perf_counter() - embedding_baslangic
        except Exception as e:
            logger.error("Embedding hatası: %s", e)
            print(f"[Hata] Vektör oluşturulurken bir sorun çıktı: {e}")
            continue

        arama_baslangic = time.perf_counter()
        en_iyi_eslesmeler = en_benzer_parcalari_bul(sorgu_vec, top_k=3)
        arama_suresi = time.perf_counter() - arama_baslangic

        if not en_iyi_eslesmeler:
            toplam_sure = time.perf_counter() - toplam_baslangic
            cevap = "Bilgi tabanımda bu konuyla ilgili kaynak bulunamadı."
            logger.info("Soru: %s | Kaynak: YOK | Toplam süre: %.4f s", kullanici_sorusu, toplam_sure)
            print(f"\nAsistan:\n{cevap}")
            print("\n--- PERFORMANS ÖLÇÜMÜ ---")
            print(f"Embedding süresi : {embedding_suresi:.4f} saniye")
            print(f"Arama süresi     : {arama_suresi:.4f} saniye")
            print(f"LLM cevap süresi : 0.0000 saniye")
            print(f"Toplam süre      : {toplam_sure:.4f} saniye")
            continue

        baglam_metni = ""
        kullanilan_kaynaklar = set()

        for skor, icerik, kaynak in en_iyi_eslesmeler:
            baglam_metni += f"\n--- DOSYA ADI: {kaynak} ---\n{icerik}\n"
            kullanilan_kaynaklar.add(kaynak)

        sistem_mesaji = (
            "Sen katı kuralları olan bir RAG asistanısın. Kullanıcının sorusuna SADECE sağlanan bağlam metinlerindeki bilgilerle cevap ver.\n"
            "KURAL 1: Bağlamda kullanıcının sorusunun cevabı YOKSA, SADECE ŞUNU YAZ: 'Bilgi tabanımda bu konuyla ilgili kaynak bulunamadı.'\n"
            "KURAL 2: Asla kendi eğitim verini kullanarak ekstra bilgi, tavsiye veya antrenman programı EKLEME. Aşırı yardımsever olmaya ÇALIŞMA.\n"
            "KURAL 3: Hangi dosyadan bilgi aldıysan, cevabının en sonuna 'Kaynak: [Dosya Adı]' şeklinde yaz."
        )
        prompt = f"Bağlam Metinleri:\n{baglam_metni}\n\nKullanıcı Sorusu: {kullanici_sorusu}"

        try:
            mesajlar = [
                {"role": "system", "content": sistem_mesaji},
                {"role": "user", "content": prompt}
            ]

            llm_baslangic = time.perf_counter()
            yanit_objesi = chat_client.complete_chat(messages=mesajlar)
            cevap = yanit_objesi.choices[0].message.content
            llm_suresi = time.perf_counter() - llm_baslangic
            toplam_sure = time.perf_counter() - toplam_baslangic

            logger.info(
                "Soru: %s | Kaynaklar: %s | Embedding: %.4f s | Arama: %.4f s | LLM: %.4f s | Toplam: %.4f s",
                kullanici_sorusu,
                ', '.join(sorted(kullanilan_kaynaklar)),
                embedding_suresi,
                arama_suresi,
                llm_suresi,
                toplam_sure
            )

            print(f"\nAsistan:\n{cevap.strip()}")
            print("\n--- PERFORMANS ÖLÇÜMÜ ---")
            print(f"Embedding süresi : {embedding_suresi:.4f} saniye")
            print(f"Arama süresi     : {arama_suresi:.4f} saniye")
            print(f"LLM cevap süresi : {llm_suresi:.4f} saniye")
            print(f"Toplam süre      : {toplam_sure:.4f} saniye")

        except Exception as e:
            logger.error("Model yanıt hatası: %s", e)
            print(f"Model yanıt üretirken hata oluştu: {e}")

if __name__ == "__main__":
    rag_asistani_baslat()
