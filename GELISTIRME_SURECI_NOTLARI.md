# Proje Geliştirme Sürecinde Karşılaşılan Engeller, Çözümler ve Öğrenimler

Bu doküman, yerel asistan projesinin geliştirilmesi sırasında karşılaşılan teknik problemleri, bu problemlerin nasıl aşıldığını ve süreçten elde edilen mühendislik kazanımlarını özetlemektedir.

## 1. Donanım ve Kaynak Yönetimi
* **Karşılaşılan Engel:** Sistemin tamamen internet bağlantısı olmadan çalışması hedeflendiğinden, kullanılacak olan yazılım paketlerinin ve dosyaların bilgisayarın hafızasını (RAM) tamamen doldurma ve işletim sistemini kilitleme riski bulunuyordu.
* **Uygulanan Çözüm:** Doğrudan indirme işlemleri yapmak yerine, sistemin desteklediği dosyaları listeleyen bir ön kontrol kodu yazıldı. Sadece mevcut bilgisayar donanımının kapasitesine uygun olan, hafif boyutlu paketler seçilerek sisteme dahil edildi.
* **Öğrenilen Ders:** Kod yazarken sadece yazılımın çalışmasını sağlamak yeterli değildir; yazılımın üzerinde çalıştığı donanımın fiziksel sınırlarını da hesaba katan, kaynak dostu (resource-aware) bir mimari kurmak şarttır.

## 2. Veritabanı ve Veri Tipleri Uyumsuzluğu
* **Karşılaşılan Engel:** Metinleri birbirleriyle karşılaştırabilmek için onları uzun sayı dizilerine dönüştürmemiz gerekiyordu. Ancak projede gereksiz yük oluşturmaması için seçilen hafif veritabanı (SQLite), bu karmaşık sayı dizilerini doğrudan kaydedebilecek bir yapıya sahip değildi.
* **Uygulanan Çözüm:** Sayı dizileri veritabanına kaydedilmeden hemen önce yapılandırılmış düz metin (JSON) formatına çevrildi. Veritabanından okunurken de tekrar matematiksel sayı dizilerine dönüştürüldü.
* **Öğrenilen Ders:** Farklı yazılım bileşenlerinin birbiriyle sorunsuz iletişim kurabilmesi için veri serileştirme (serialization) işlemlerinin ne kadar kritik bir köprü görevi gördüğü anlaşıldı.

## 3. Kaynak İzlenebilirliği Sorunu
* **Karşılaşılan Engel:** Sistem, sorulan soruya uygun metin parçalarını bulabiliyor ancak bu metinlerin hangi dosyadan geldiğini unutuyordu. Bu durum, verilen cevapların doğruluğunun kullanıcı tarafından kontrol edilmesini imkansız kılıyordu.
* **Uygulanan Çözüm:** İlk oluşturulan veritabanı yapısı tamamen iptal edilip baştan tasarlandı. Tabloya, metin içeriklerinin yanında o metnin ait olduğu dosya adını da zorunlu olarak tutan yeni bir kayıt sütunu eklendi.
* **Öğrenilen Ders:** Yazılım geliştirme sürecinde ilk tasarlanan yapının ilerleyen aşamalarda yetersiz kalabileceği ve gerektiğinde temel mimariyi yıkıp yeniden kurmaktan çekinmemek gerektiği görüldü.

## 4. Yavaş Hesaplama Süreleri
* **Karşılaşılan Engel:** Binlerce ondalıklı sayıyı birbiriyle karşılaştırıp benzerlik oranlarını bulmak için yazılan standart döngüler çok yavaş çalışıyor, sistemin her soruya cevap verme süresini ciddi şekilde uzatıyordu.
* **Uygulanan Çözüm:** Bu ağır matematiksel işlemler için standart döngüler iptal edildi ve sadece bu işler için optimize edilmiş olan NumPy kütüphanesi sisteme entegre edildi.
* **Öğrenilen Ders:** Yoğun matematiksel işlemlerde standart kod blokları yerine, doğrudan bellekte hızlı işlem yapabilen amaca uygun kütüphanelerin kullanılması gerektiği deneyimlendi.

## 5. Veri Tekrarı (Kopya Veri) Sorunu
* **Karşılaşılan Engel:** Sistem aynı belgenin farklı sayfalarından bilgiler bulduğunda, kullanıcıya referans verirken "Kaynak: dosya, dosya, dosya" şeklinde aynı belgeyi defalarca tekrar ediyordu.
* **Uygulanan Çözüm:** Bulunan kaynakları alt alta listelemek yerine, aynı elemanın sadece bir kez kayıt edilmesine izin veren Küme (Set) veri yapısı kullanıldı.
* **Öğrenilen Ders:** Doğru veri yapısının seçilmesi durumunda, karmaşık kontrol kodları yazmaya gerek kalmadan mantıksal hataların temelden çözülebileceği anlaşıldı.

## 6. Sistemin Kilitlenmesi ve Hata Yönetimi
* **Karşılaşılan Engel:** Sistemin arka planda metinleri işlediği veya ağır hesaplamalar yaptığı anlarda terminal kilitleniyor, beklenmedik bir girdi olduğunda ise program tamamen çöküp kapanıyordu.
* **Uygulanan Çözüm:** Çökme riski olan tüm adımlar hata yakalama (try-except) blokları içine alındı. Böylece sistem başarısız olsa bile çökmek yerine kullanıcıya durumu bildirip çalışmaya devam edecek şekilde ayarlandı.
* **Öğrenilen Ders:** Kesintisiz bir sistem için kodun her zaman kusursuz çalışacağını varsaymak yerine, hataları öngörüp onları yönetebilecek bir esneklik (hata toleransı) kurmanın zorunlu olduğu kavrandı.

## 7. Kontrol Dışı Yanıt Üretimi
* **Karşılaşılan Engel:** Sistemin, kendisine verilen metinlere bağlı kalmak yerine, kendi kendine uydurma bilgiler üretme veya sorulan soruya metinde olmayan alakasız tavsiyeler ekleme eğilimi vardı.
* **Uygulanan Çözüm:** Sistemin karar alma mekanizmasına çok katı sınırlandırmalar eklendi. "Sadece sağlanan metinleri kullan", "Metinde cevap yoksa sadece 'bilmiyorum' de" ve "Tavsiye ekleme" şeklinde kesin kurallar zorunlu kılındı.
* **Öğrenilen Ders:** Karmaşık yazılımların varsayılan davranışlarına güvenilemeyeceği; sistemin doğru, tutarlı ve kesin çalışması için çok net sınırlarla programlanması gerektiği tecrübe edildi.