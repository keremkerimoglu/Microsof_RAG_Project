import os
import sqlite3
import json
import foundry_local_sdk as foundry_local

def metinleri_vektorlestir_ve_kaydet():
    config = foundry_local.Configuration(app_name="local_Asistan")
    manager = foundry_local.FoundryLocalManager(config)
    
    hedef_model_anahtari = "qwen3-embedding-0.6b"
    
    print("1. Katalogdan embedding modeli aranıyor...")
    tum_modeller = manager.catalog.list_models()
    secilen_model = None
    
    for m in tum_modeller:
        isim = getattr(m, 'name', '') or getattr(m, 'id', '')
        if hedef_model_anahtari in str(isim):
            secilen_model = m
            break
            
    if secilen_model is None:
        print(f"Hata: '{hedef_model_anahtari}' modeli bulunamadı!")
        return
        
    print("2. Model belleğe yükleniyor...")
    secilen_model.download()
    secilen_model.load()
    istemci = secilen_model.get_embedding_client()

    conn = sqlite3.connect('knowledge_base.db')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS documents")
    cursor.execute('''
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL,
            source TEXT NOT NULL
        )
    ''')

    veri_klasoru = "data"
    
    if not os.path.exists(veri_klasoru):
        print(f"\nHata: Proje dizininde '{veri_klasoru}' adında bir klasör bulunamadı.")
        print("Lütfen ana dizinde 'data' klasörü oluşturup içine .txt dosyalarınızı atın.")
        conn.close()
        return

    print(f"\n3. '{veri_klasoru}' klasöründeki dosyalar taranıyor...")

    dosyalar = os.listdir(veri_klasoru)
    islenen_dosya_sayisi = 0

    for dosya_adi in dosyalar:
        if dosya_adi.endswith(".txt"):
            dosya_yolu = os.path.join(veri_klasoru, dosya_adi)
            
            with open(dosya_yolu, 'r', encoding='utf-8') as dosya:
                metin = dosya.read().strip()
                
            if not metin:
                continue

            try:
                yanit = istemci.generate_embedding(metin)
                if hasattr(yanit, 'data') and len(yanit.data) > 0:
                    vektor_verisi = yanit.data[0].embedding
                    vektor_metni = json.dumps(vektor_verisi)
                    
                    cursor.execute(
                        "INSERT INTO documents (content, embedding, source) VALUES (?, ?, ?)",
                        (metin, vektor_metni, dosya_adi)
                    )
                    print(f"Başarılı: '{dosya_adi}' vektörleştirilip eklendi.")
                    islenen_dosya_sayisi += 1
                else:
                    print(f"Uyarı: '{dosya_adi}' için boş yanıt döndü.")
            except Exception as e:
                print(f"Hata oluştu ('{dosya_adi}'): {e}")

    conn.commit()
    conn.close()
    print(f"\nTüm işlemler tamamlandı. Toplam {islenen_dosya_sayisi} dosya veritabanına işlendi.")

if __name__ == "__main__":
    metinleri_vektorlestir_ve_kaydet()