import sqlite3
import json
import numpy as np
import foundry_local_sdk as foundry_local

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
    return benzerlikler[:top_k]

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

        try:
            sorgu_yanit = emb_client.generate_embedding(kullanici_sorusu)
            sorgu_vec = sorgu_yanit.data[0].embedding
        except Exception as e:
            print(f"[Hata] Vektör oluşturulurken bir sorun çıktı: {e}")
            continue

        en_iyi_eslesmeler = en_benzer_parcalari_bul(sorgu_vec, top_k=3)

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
            
            yanit_objesi = chat_client.complete_chat(messages=mesajlar)
            cevap = yanit_objesi.choices[0].message.content
            
            print(f"\nAsistan:\n{cevap.strip()}")
            
        except Exception as e:
            print(f"Model yanıt üretirken hata oluştu: {e}")

if __name__ == "__main__":
    rag_asistani_baslat()