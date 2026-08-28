# Yerel RAG Asistanı (Local RAG Assistant)

Bu proje, dış API'lere (OpenAI, Anthropic vb.) bağımlı olmadan, tamamen yerel donanım üzerinde çalışan gizlilik odaklı bir RAG (Retrieval-Augmented Generation) sistemidir. Sistem, metin verilerini vektörleştirip yerel bir SQLite veritabanında saklar ve Kosinüs Benzerliği (Cosine Similarity) algoritması kullanarak kullanıcının sorularına en uygun bağlamı bularak LLM üzerinden cevap üretir.

## Özellikler

* **Tamamen Yerel Çalışma (Offline-First):** Hiçbir veri dış sunuculara gönderilmez. KVKK ve kurumsal veri gizliliği standartlarına tam uyumludur.
* **Hafif Vektör Veritabanı:** Ağır sunucu kurulumları yerine, vektör verileri JSON serileştirmesi ile sunucusuz `SQLite` üzerinde saklanır.
* **Gelişmiş Anlamsal Arama:** SQL LIKE operatörü yerine, `NumPy` kullanılarak matematiksel Kosinüs Benzerliği hesabı yapılır.
* **Halüsinasyon Koruması:** Qwen 7B modeline uygulanan katı sistem komutları (Prompt Engineering) sayesinde, modelin uydurma cevap vermesi engellenmiş ve kaynak şeffaflığı (Source Traceability) sağlanmıştır.

## Kullanılan Modeller (Microsoft Foundry Local SDK)
* **Embedding (Vektörleştirme):** `qwen3-embedding-0.6b`
* **Generation (Metin Üretimi):** `qwen2.5-7b-instruct`

## Sistem Gereksinimleri
* **Python:** 3.8 veya üzeri.
* **Donanım:** 7 Milyar parametreli LLM'in yerel belleğe yüklenebilmesi için yeterli RAM ve VRAM.

## Kurulum
1. `git clone https://github.com/kullaniciadiniz/yerel-rag-asistani.git`
2. `python -m venv venv` ve aktif edin (`.\venv\Scripts\activate` veya `source venv/bin/activate`)
3. `pip install -r requirements.txt`

## Kullanım Adımları
1. `data` adında bir klasör oluşturup içine `.txt` dosyalarınızı atın.
2. `python database_v1.py` ile veritabanını kurun.
3. `python generate_embeddings.py` ile metinleri vektörleştirin.
4. `python rag_app_v1.py` ile asistanı başlatın.

## Geliştirici
Ahmet Kerem Kerimoğlu
