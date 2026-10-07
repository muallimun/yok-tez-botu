# 🎓 YÖK Tez Botu Premium (Web Scraping Tool)

YÖK Ulusal Tez Merkezi'ndeki açık erişimli akademik tez künyelerini ve özetlerini otomatik olarak tarayan, analiz eden ve yapılandırılmış bir Excel/CSV veritabanına dönüştüren profesyonel bir Python otomasyon aracıdır.

Bu araç, özellikle literatür taraması aşamasında olan yüksek lisans ve doktora öğrencileri ile akademisyenlerin manuel veri kopyalama yükünü ortadan kaldırmak için geliştirilmiştir.

## ✨ Öne Çıkan Özellikler
* **Kapsamlı Veri Çekimi:** Tez No, Yazar, Yıl, Danışman, Üniversite/Enstitü, Konu, Dil vb. temel künye bilgileri.
* **İsteğe Bağlı Ekstra Veriler:** Türkçe Özet, İngilizce Özet ve Atıf bilgilerini sekme okuma (toggle) mantığıyla çekebilme.
* **Zırhlı Kayıt Mekanizması:** Excel (`openpyxl`) yazma hatalarına sebep olan görünmez web karakterlerini (NULL bytes, kontrol karakterleri) Regex ile otomatik temizleme.
* **Acil Kurtarma (B Planı):** Excel dosyasının açık unutulması veya beklenmedik kilitlenmeler durumunda verileri anında UTF-8 formatlı `.csv` dosyasına yedekleme.
* **Modern ve İnteraktif Arayüz:** CustomTkinter ile tasarlanmış, canlı işlem konsoluna sahip koyu tema (dark mode) arayüz.

## 🛠️ Kullanılan Teknolojiler
* **Python 3.x**
* **Arayüz (GUI):** CustomTkinter
* **Web Otomasyonu:** Selenium WebDriver (Chrome Debugging Port)
* **Veri İşleme:** Pandas, Regex (`re`), Openpyxl

## 🚀 Kurulum ve Çalıştırma

Geliştirici ortamında çalıştırmak için:
1. Depoyu klonlayın: `git clone https://github.com/KULLANICI_ADINIZ/yok-tez-botu.git`
2. Gerekli kütüphaneleri yükleyin: `pip install -r requirements.txt`
3. Chrome tarayıcınızı hata ayıklama moduyla (debugging port) başlatın (Kılavuz program arayüzünde mevcuttur).
4. Uygulamayı çalıştırın: `python yok_tez_bot.py`


## ⚖️ Yasal Uyarı ve Sorumluluk Reddi
Bu yazılım, araştırmacılara kolaylık sağlamak amacıyla geliştirilmiş **ücretsiz ve açık kaynaklı** bir otomasyon aracıdır. 
Programın kullanımından, YÖK sunucularında oluşturulan anlık trafikten ve çekilen verilerin (KVKK ve Telif Hakları kapsamında) saklanması/dağıtılmasından tamamen son kullanıcı sorumludur. Proje, hedef web sitesinin arayüz güncellemelerine karşı bir çalışma garantisi sunmaz ("As-Is" olarak sağlanır).

---
**Geliştirici:** | **Yayıncı:** muallimun.net
