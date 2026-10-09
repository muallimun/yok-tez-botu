import os
import sys
import time
import threading
import subprocess
import re
import webbrowser
import urllib.request
import json
from PIL import Image
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from datetime import datetime
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By

# Programın Mevcut Sürümü (Yeni sürüm yayınlarken burayı güncelleyeceksiniz)
MEVCUT_SURUM = "3.6"
GITHUB_REPO = "muallimun/yok-tez-botu"

# PyInstaller İçin Gerekli Dosya Yolu Bulucu (Klasörlü Derleme İçin Güncellendi)
def kaynak_yolu(relative_path):
    """ .exe'nin veya .py'nin çalıştığı ana dizini kesin olarak bulur """
    if hasattr(sys, 'frozen'):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Tema Ayarları
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PremiumTezBot(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"YÖK Tez Merkezi | Profesyonel Veri Kazıma Aracı v{MEVCUT_SURUM}")
        self.geometry("1020x820")
        self.minsize(980, 800)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.islem_devam_ediyor = False
        self.toplam_bulunan_tez = 0
        self.islenen_tez_sayisi = 0
        self.arayuzu_olustur()
        
        # YENİ EKLENEN: Arka planda güncelleme kontrolünü başlat
        self.guncelleme_kontrolunu_baslat()

    def guncelleme_kontrolunu_baslat(self):
        threading.Thread(target=self._guncelleme_denetle, daemon=True).start()

    def _guncelleme_denetle(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_tag = data.get("tag_name", "").replace("v", "")
                release_url = data.get("html_url", "")
                
                # Versiyon kıyaslaması
                if self._versiyon_karsilastir(MEVCUT_SURUM, latest_tag):
                    self.after(2000, lambda: self._guncelleme_uyarisi_goster(latest_tag, release_url))
        except Exception:
            pass # İnternet yoksa veya API hatası verirse sessizce geç

    def _versiyon_karsilastir(self, mevcut, yeni):
        try:
            mevcut_parcalar = [int(x) for x in mevcut.split(".")]
            yeni_parcalar = [int(x) for x in yeni.split(".")]
            return yeni_parcalar > mevcut_parcalar
        except:
            return False

    def _guncelleme_uyarisi_goster(self, yeni_surum, url):
        cevap = messagebox.askyesno(
            "Yeni Sürüm Mevcut!",
            f"YÖK Tez Botu'nun yeni bir sürümü yayınlandı!\n\n"
            f"Mevcut Sürüm: v{MEVCUT_SURUM}\n"
            f"Yeni Sürüm: v{yeni_surum}\n\n"
            "Yeni özellikleri ve hata düzeltmelerini içeren bu güncellemeyi indirmek için indirme sayfasına gitmek ister misiniz?"
        )
        if cevap:
            webbrowser.open(url)

    def arayuzu_olustur(self):
        # ==================== KENAR ÇUBUĞU ====================
        self.sidebar = ctk.CTkFrame(self, width=290, corner_radius=0, fg_color="#1a1a24")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="🎓 YÖK TEZ BOTU", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 5))
        
        self.versiyon_label = ctk.CTkLabel(self.sidebar, text=f"Akademik Veritabanı Sürümü v{MEVCUT_SURUM}", text_color="#AAB7B8", font=ctk.CTkFont(size=12))
        self.versiyon_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.amac_frame = ctk.CTkFrame(self.sidebar, fg_color="#1F618D", corner_radius=8)
        self.amac_frame.grid(row=2, column=0, padx=15, pady=5, sticky="ew")
        amac_text = (
            "📌 KULLANIM AMACI\n\n"
            "Bu araç, YÖK Ulusal Tez\n"
            "Merkezi'ndeki araştırmaları,\n"
            "analiz etmeniz için tek bir\n"
            "Excel veritabanına dönüştürür."
        )
        ctk.CTkLabel(self.amac_frame, text=amac_text, justify="left", font=ctk.CTkFont(size=12), text_color="white").pack(padx=10, pady=10, anchor="w")

        self.uyari_frame = ctk.CTkFrame(self.sidebar, fg_color="#922B21", corner_radius=8)
        self.uyari_frame.grid(row=3, column=0, padx=15, pady=5, sticky="ew")
        uyari_text = (
            "⚠️ ÖNEMLİ UYARI\n\n"
            "İşlem başladıktan sonra Chrome\n"
            "penceresini KAPATMAYIN ve\n"
            "simge durumuna küçültmeyin!\n"
            "Arka planda açık bırakın."
        )
        ctk.CTkLabel(self.uyari_frame, text=uyari_text, justify="left", font=ctk.CTkFont(size=12, weight="bold"), text_color="white").pack(padx=10, pady=10, anchor="w")

        self.btn_tarayici = ctk.CTkButton(self.sidebar, text="🌐 1. Tarayıcıyı Başlat", command=self.tarayiciyi_ac, height=45, fg_color="#2980B9", hover_color="#1A5276", font=ctk.CTkFont(weight="bold", size=14))
        self.btn_tarayici.grid(row=4, column=0, padx=15, pady=(20, 10), sticky="ew")
        
        self.kilavuz_frame = ctk.CTkFrame(self.sidebar, fg_color="#2C3E50", corner_radius=8)
        self.kilavuz_frame.grid(row=5, column=0, padx=15, pady=(0, 10), sticky="ew")
        # E-devlet uyarınız KORUNDU
        kilavuz_text = (
            "📝 ADIM ADIM KILAVUZ\n\n"
            "1. Üstteki butonla tarayıcıyı açın.\n"
            "2. Kelimelerinizi girip aratın ve\n"
            "   gerekirse sonuçları filtreleyin.\n"
            "3. Liste sonucunun 2000 veya daha\n"
            "   az olduğunu ekranda görün.\n"
            "4. Tarayıcıyı ASLA KAPATMADAN\n"
            "   tekrar bu programa geri dönün.\n"
            "5. Yandaki '2. Verileri Çek'\n"
            "   butonuna basıp işlemi başlatın."
        )
        ctk.CTkLabel(self.kilavuz_frame, text=kilavuz_text, justify="left", font=ctk.CTkFont(size=12), text_color="#ECF0F1").pack(padx=10, pady=10, anchor="w")
        
        # Tıklanabilir Şirket Logosu 
        try:
            logo_path = kaynak_yolu("logo.png")
            logo_image = ctk.CTkImage(light_image=Image.open(logo_path), dark_image=Image.open(logo_path), size=(140, 45)) 
            self.logo_buton = ctk.CTkButton(self.sidebar, image=logo_image, text="", fg_color="transparent", hover_color="#2C3E50", width=140, command=lambda: webbrowser.open("https://www.muallimun.com"))
            self.logo_buton.grid(row=6, column=0, pady=(10, 5))
            self.logo_buton.configure(cursor="hand2")
        except Exception:
            self.logo_hata = ctk.CTkLabel(self.sidebar, text="muallimun.com", font=ctk.CTkFont(underline=True), cursor="hand2")
            self.logo_hata.grid(row=6, column=0, pady=(10, 5))
            self.logo_hata.bind("<Button-1>", lambda e: webbrowser.open("https://www.muallimun.com"))
            
        self.lbl_sistem_durumu = ctk.CTkLabel(self.sidebar, text="Sistem: Beklemede", text_color="#2ECC71", font=ctk.CTkFont(weight="bold"))
        self.lbl_sistem_durumu.grid(row=7, column=0, padx=20, pady=15, sticky="s")

        self.btn_yasal = ctk.CTkButton(self.sidebar, text="⚖️ Yasal Uyarı ve Şartlar", command=self.yasal_uyari_goster, fg_color="transparent", text_color="#95A5A6", hover_color="#2C3E50", font=ctk.CTkFont(size=11, underline=True))
        self.btn_yasal.grid(row=8, column=0, pady=(0, 15), sticky="s")

        # ==================== ANA EKRAN ====================
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.main_view.grid_columnconfigure(0, weight=1)
        self.main_view.grid_rowconfigure(3, weight=1)

        self.settings_card = ctk.CTkFrame(self.main_view, corner_radius=10, fg_color="#212130")
        self.settings_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.settings_card.grid_columnconfigure(0, weight=1)
        
        self.info_card = ctk.CTkFrame(self.settings_card, fg_color="#181824", corner_radius=8)
        self.info_card.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        
        self.lbl_varsayilan_baslik = ctk.CTkLabel(self.info_card, text="✅ Varsayılan Kayıt Sütunları:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#2ECC71")
        self.lbl_varsayilan_baslik.grid(row=0, column=0, padx=15, pady=(12, 0), sticky="w")
        self.lbl_varsayilan_metin = ctk.CTkLabel(self.info_card, text="Tez No, Tez Adı, İngilizce Adı, Yazar, Yıl, Tür, Dil, Konu, Üniversite, Enstitü, Anabilim Dalı, Bilim Dalı, Danışman.", font=ctk.CTkFont(size=12), text_color="#BDC3C7", justify="left")
        self.lbl_varsayilan_metin.grid(row=1, column=0, padx=15, pady=(2, 10), sticky="w")

        self.lbl_dikkat_baslik = ctk.CTkLabel(self.info_card, text="⚠️ Dikkat:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#F1C40F")
        self.lbl_dikkat_baslik.grid(row=2, column=0, padx=15, pady=(5, 0), sticky="w")
        self.lbl_dikkat_metin = ctk.CTkLabel(self.info_card, text="Aşağıdaki ekstra verileri eklemek, programın her tez için ek sekmeler açmasını gerektireceğinden toplam işlem süresini bir miktar uzatacaktır.", font=ctk.CTkFont(size=12), text_color="#BDC3C7", justify="left")
        self.lbl_dikkat_metin.grid(row=3, column=0, padx=15, pady=(2, 12), sticky="w")

        self.lbl_ayarlar = ctk.CTkLabel(self.settings_card, text="⚙️ Ekstra Sütun Ayarları (İsteğe Bağlı)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#F39C12")
        self.lbl_ayarlar.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.var_tr = ctk.BooleanVar(value=False)
        self.var_en = ctk.BooleanVar(value=False)
        self.var_atif = ctk.BooleanVar(value=False)
        
        self.chk_frame = ctk.CTkFrame(self.settings_card, fg_color="transparent")
        self.chk_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")
        
        self.chk_tr = ctk.CTkCheckBox(self.chk_frame, text="Türkçe Özet", variable=self.var_tr)
        self.chk_tr.pack(side="left", padx=(0, 20))
        self.chk_en = ctk.CTkCheckBox(self.chk_frame, text="İngilizce Özet", variable=self.var_en)
        self.chk_en.pack(side="left", padx=(0, 20))
        self.chk_atif = ctk.CTkCheckBox(self.chk_frame, text="Atıf Bilgisi", variable=self.var_atif)
        self.chk_atif.pack(side="left")

        self.progress_card = ctk.CTkFrame(self.main_view, corner_radius=10, fg_color="#212130")
        self.progress_card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        self.prog_header = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        self.prog_header.pack(fill="x", padx=20, pady=(15, 5))
        self.lbl_ilerleme_baslik = ctk.CTkLabel(self.prog_header, text="📊 İşlem Durumu", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_ilerleme_baslik.pack(side="left")
        self.lbl_yuzde = ctk.CTkLabel(self.prog_header, text="Bekleniyor...", font=ctk.CTkFont(size=14, weight="bold"), text_color="#F1C40F")
        self.lbl_yuzde.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_card, height=18, fg_color="#2C3E50", progress_color="#27AE60")
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 20))

        self.btn_baslat = ctk.CTkButton(self.main_view, text="🚀 2. Verileri Çek ve Excel'e Kaydet", command=self.baslat_thread, height=55, font=ctk.CTkFont(size=16, weight="bold"), fg_color="#27AE60", hover_color="#1E8449", text_color="white", text_color_disabled="white")
        self.btn_baslat.grid(row=2, column=0, sticky="ew", pady=(0, 20))

        self.log_card = ctk.CTkFrame(self.main_view, corner_radius=10, fg_color="#212130")
        self.log_card.grid(row=3, column=0, sticky="nsew")
        self.log_card.grid_columnconfigure(0, weight=1)
        self.log_card.grid_rowconfigure(1, weight=1)
        
        self.lbl_konsol = ctk.CTkLabel(self.log_card, text="🖥️ Canlı İşlem Konsolu", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_konsol.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.konsol = ctk.CTkTextbox(self.log_card, font=ctk.CTkFont(family="Consolas", size=13), fg_color="#111118", text_color="#2ECC71")
        self.konsol.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.konsol.insert("0.0", "Sistem hazır. Lütfen soldaki adımları takip ederek tarayıcıyı başlatın.\n")
        self.konsol.configure(state="disabled")

    def yasal_uyari_goster(self):
        uyari_metni = (
            "YASAL SORUMLULUK REDDİ:\n\n"
            "Bu yazılım, akademik araştırmacılara kolaylık sağlamak amacıyla geliştirilmiş "
            "ücretsiz bir otomasyon aracıdır.\n\n"
            "• Programın kullanımından tamamen son kullanıcı sorumludur.\n"
            "• Çekilen tez künyeleri ve özet metinlerinin KVKK ile Telif Hakları kapsamındaki hukuki güvenliği yazılımı çalıştıran kişiye aittir.\n"
            "• Yazılımı geliştiren (Muallimun.Net), verilerin dağıtılmasından veya sistemin kötüye kullanımından sorumlu tutulamaz.\n\n"
            "Programı kullanan her birey bu şartları okumuş ve kabul etmiş sayılır."
        )
        messagebox.showinfo("⚖️ Yasal Uyarı ve Kullanım Koşulları", uyari_metni)
    
    def log_yaz(self, mesaj):
        self.konsol.configure(state="normal")
        saat = datetime.now().strftime("%H:%M:%S")
        self.konsol.insert("end", f"[{saat}] {mesaj}\n")
        self.konsol.see("end")
        self.konsol.configure(state="disabled")
        
    def ilerleme_guncelle(self):
        if self.toplam_bulunan_tez > 0:
            oran = self.islenen_tez_sayisi / self.toplam_bulunan_tez
            oran = min(oran, 1.0) 
            yuzde = int(oran * 100)
            self.progress_bar.set(oran)
            self.lbl_yuzde.configure(text=f"{self.islenen_tez_sayisi} / {self.toplam_bulunan_tez} Kayıt Tamamlandı (%{yuzde})")
        else:
            self.lbl_yuzde.configure(text=f"{self.islenen_tez_sayisi} Kayıt Tamamlandı")

    def tarayiciyi_ac(self):
        try:
            # 1. Chrome'un olabileceği muhtemel tüm yolları tara
            olasi_yollar = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Google\Chrome\Application\chrome.exe")
            ]
            
            chrome_path = None
            for yol in olasi_yollar:
                if os.path.exists(yol):
                    chrome_path = yol
                    break
                    
            if not chrome_path:
                messagebox.showerror("Hata", "Google Chrome bilgisayarınızda bulunamadı!\nLütfen Chrome'un bilgisayarınızda standart konuma kurulu olduğundan emin olun.")
                return

            # 2. C: ana dizini yerine, kullanıcının kendi AppData klasöründe profil oluştur (İzin hatasını kesin çözer)
            user_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), "yok_tez_bot_chrome_profile")
            url = "https://tez.yok.gov.tr/UlusalTezMerkezi/tarama.jsp"
            
            subprocess.Popen(f'"{chrome_path}" --remote-debugging-port=9222 --user-data-dir="{user_data_dir}" "{url}"', shell=True)
            self.lbl_sistem_durumu.configure(text="Tarayıcı Açıldı", text_color="#F1C40F")
            self.log_yaz("🌐 Tarayıcı başarıyla başlatıldı. Lütfen giriş yapıp filtrenizi uygulayın.")
        except Exception as e:
            messagebox.showerror("Hata", f"Tarayıcı başlatılırken beklenmeyen bir hata oluştu:\n{e}")

    def baslat_thread(self):
        if self.islem_devam_ediyor: return
        kayit_yeri = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=f"YOK_Tez_Veritabani_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            filetypes=[("Excel Dosyası", "*.xlsx")],
            title="Veritabanının Kaydedileceği Excel Dosyası"
        )
        if not kayit_yeri: return

        self.islem_devam_ediyor = True
        self.konsol.configure(state="normal")
        self.konsol.delete("0.0", "end")
        self.konsol.configure(state="disabled")
        
        self.btn_baslat.configure(state="disabled", text="⏳ İşlem Devam Ediyor... Lütfen Bekleyin")
        self.btn_tarayici.configure(state="disabled")
        self.chk_tr.configure(state="disabled")
        self.chk_en.configure(state="disabled")
        self.chk_atif.configure(state="disabled")
        self.lbl_sistem_durumu.configure(text="Sistem: Çalışıyor...", text_color="#E67E22")
        
        self.islenen_tez_sayisi = 0
        self.toplam_bulunan_tez = 0
        self.progress_bar.set(0)
        self.lbl_yuzde.configure(text="Sistem Analiz Ediliyor...")
        self.log_yaz("⚠️ DİKKAT: Veri çekme işlemi başlatıldı! Lütfen tarayıcı penceresine DOKUNMAYIN.")
        threading.Thread(target=self.veri_cek, args=(kayit_yeri,), daemon=True).start()

    def pane_bekle_ve_oku(self, kart, buton_metni):
        try:
            buton = kart.find_element(By.XPATH, f".//button[contains(text(), '{buton_metni}')]")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", buton)
            time.sleep(0.3)
            
            if "active" not in buton.get_attribute("class"):
                self.driver.execute_script("arguments[0].click();", buton)
            
            bekleme = 0
            while bekleme < 6.0:
                time.sleep(0.5)
                paneller = kart.find_elements(By.CSS_SELECTOR, "div.sub-content[style*='display: block']")
                if paneller and len(paneller[-1].get_attribute("innerText").strip()) > 5:
                    return paneller[-1].get_attribute("innerText").strip()
                bekleme += 0.5
            return ""
        except:
            return ""

    def veri_cek(self, kayit_yeri):
        try:
            options = webdriver.ChromeOptions()
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self.driver = webdriver.Chrome(options=options)
        except Exception:
            self.after(0, self.arayuz_sifirla, "Hata: Tarayıcıya bağlanılamadı. Chrome açık mı?", False)
            return

        tum_tezler = []
        sayfa_sayaci = 1

        try:
            bilgi_metni = self.driver.find_element(By.XPATH, "//*[contains(text(), 'kayıt bulundu')]").text
            rakamlar = re.findall(r'([\d\.]+)\s*kayıt', bilgi_metni)
            if rakamlar:
                self.toplam_bulunan_tez = int(rakamlar[0].replace('.', ''))
                self.after(0, self.log_yaz, f"🔍 Sistem {self.toplam_bulunan_tez} adet hedef kayıt tespit etti.")
                self.after(0, self.ilerleme_guncelle)
        except:
            pass

        while True:
            self.after(0, self.log_yaz, f"\n--- 📄 {sayfa_sayaci}. Sayfa Taranıyor ---")
            time.sleep(3)
            
            kartlar = self.driver.find_elements(By.CSS_SELECTOR, "div.result-card")
            if not kartlar:
                self.after(0, self.log_yaz, "Sayfada tez bulunamadı veya son sayfaya gelindi.")
                break
                
            for i in range(len(kartlar)):
                if not self.islem_devam_ediyor: return 
                
                try:
                    guncel_kartlar = self.driver.find_elements(By.CSS_SELECTOR, "div.result-card")
                    if i >= len(guncel_kartlar): break
                    kart = guncel_kartlar[i]
                    
                    tez_adi, ingilizce_adi = "", ""
                    try:
                        text_group = kart.find_element(By.CSS_SELECTOR, "div.text-group")
                        basliklar = [b.strip() for b in text_group.get_attribute("textContent").strip().split('\n') if b.strip()]
                        if len(basliklar) > 0: tez_adi = basliklar[0]
                        if len(basliklar) > 1: ingilizce_adi = basliklar[1]
                    except: pass
                    
                    tez_no = ""
                    try:
                        tum_metin = kart.get_attribute("textContent")
                        if "Tez No:" in tum_metin:
                            tez_no_kismi = tum_metin.split("Tez No:")[1].strip().split()[0]
                            tez_no = "".join(filter(str.isdigit, tez_no_kismi))
                    except: pass
                    if not tez_no: tez_no = "Yok"

                    self.pane_bekle_ve_oku(kart, "Tez Künye")
                    
                    yazar, yil, tur, dil, konu, yer_bilgisi, danisman = "", "", "", "", "", "", ""
                    try:
                        bilgiler = kart.find_elements(By.CSS_SELECTOR, "div.sub-content[style*='display: block'] div.card-info")
                        if not bilgiler:
                            bilgiler = kart.find_elements(By.CSS_SELECTOR, "div.card-info")
                            
                        for bilgi in bilgiler:
                            metin = bilgi.get_attribute("textContent").strip()
                            if metin.startswith("Yazar:"): yazar = metin.replace("Yazar:", "").strip()
                            elif metin.startswith("Yıl:"): yil = metin.replace("Yıl:", "").strip()
                            elif metin.startswith("Tür:"): tur = metin.replace("Tür:", "").strip()
                            elif metin.startswith("Dil:"): dil = metin.replace("Dil:", "").strip()
                            elif metin.startswith("Konu:"): konu = metin.replace("Konu:", "").strip()
                            elif metin.startswith("Yer Bilgisi:"): yer_bilgisi = metin.replace("Yer Bilgisi:", "").strip()
                            elif metin.startswith("Danışman:"): danisman = metin.replace("Danışman:", "").strip()
                    except: pass

                    univ, enst, anabilim, bilim = "", "", "", ""
                    if yer_bilgisi:
                        parcalar = [p.strip() for p in yer_bilgisi.split('/')]
                        if len(parcalar) > 0: univ = parcalar[0]
                        if len(parcalar) > 1: enst = parcalar[1]
                        if len(parcalar) > 2: anabilim = parcalar[2]
                        if len(parcalar) > 3: bilim = parcalar[3]

                    tr_ozet, en_ozet, atif = "", "", ""
                    if self.var_tr.get(): tr_ozet = self.pane_bekle_ve_oku(kart, "Türkçe özet")
                    if self.var_en.get(): en_ozet = self.pane_bekle_ve_oku(kart, "İngilizce özet")
                    if self.var_atif.get(): atif = self.pane_bekle_ve_oku(kart, "Atıf")

                    if yazar or tez_adi:
                        veri = {
                            "Tez No": tez_no, "Tez Adı": tez_adi, "İngilizce Adı": ingilizce_adi,
                            "Yazar": yazar, "Yıl": yil, "Tür": tur, "Dil": dil, "Konu": konu,
                            "Üniversite": univ, "Enstitü": enst, "Anabilim Dalı": anabilim, "Bilim Dalı": bilim,
                            "Danışman": danisman
                        }
                        if self.var_tr.get(): veri["Türkçe Özet"] = tr_ozet
                        if self.var_en.get(): veri["İngilizce Özet"] = en_ozet
                        if self.var_atif.get(): veri["Atıf"] = atif
                        
                        tum_tezler.append(veri)
                        self.islenen_tez_sayisi += 1
                        self.after(0, self.ilerleme_guncelle)
                        durum_msj = f"[+] {yazar} (Tez No: {tez_no})" if yazar else f"[-] Yazar Boş (Tez No: {tez_no})"
                        self.after(0, self.log_yaz, durum_msj)

                    time.sleep(1.2) 
                except Exception:
                    continue

            try:
                hedef_sayfa = str(sayfa_sayaci + 1)
                sayfa_btn = self.driver.find_elements(By.XPATH, f"//a[text()='{hedef_sayfa}']")
                ok_btn = self.driver.find_elements(By.XPATH, "//a[contains(text(), '»')]")
                
                if sayfa_btn:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sayfa_btn[0])
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", sayfa_btn[0])
                    sayfa_sayaci += 1
                elif ok_btn:
                    if "disabled" in ok_btn[0].get_attribute("class") or ok_btn[0].get_attribute("disabled"):
                        break
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ok_btn[0])
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", ok_btn[0])
                    sayfa_sayaci += 1
                else:
                    break
            except:
                break

        # ZIRHLI KAYDETME
        if tum_tezler:
            self.after(0, self.log_yaz, "💾 Veriler temizleniyor ve diske yazılıyor, lütfen bekleyin...")
            df = pd.DataFrame(tum_tezler)
            for col in df.columns:
                df[col] = df[col].apply(lambda x: ILLEGAL_CHARACTERS_RE.sub('', str(x)) if pd.notnull(x) else x)
            try:
                df.to_excel(kayit_yeri, index=False)
                self.after(0, self.arayuz_sifirla, f"BÜYÜK BAŞARI! {len(tum_tezler)} tez '{kayit_yeri}' konumuna kaydedildi.", True)
            except Exception as e:
                try:
                    kurtarma_yeri = kayit_yeri.replace(".xlsx", "_KURTARMA.csv")
                    df.to_csv(kurtarma_yeri, index=False, sep=";", encoding="utf-8-sig")
                    hata_mesaji = f"Excel hatası oluştu ancak veriler KURTARILDI!\n\nVerileriniz CSV formatında kaydedildi:\n{kurtarma_yeri}\n\nHata detayı: {e}"
                    self.after(0, self.arayuz_sifirla, hata_mesaji, True)
                except Exception as e2:
                    self.after(0, self.arayuz_sifirla, f"Kritik Kayıt Hatası! Veriler diske yazılamadı: {e2}", False)
        else:
            self.after(0, self.arayuz_sifirla, "İşlem bitti ancak veri toplanamadı.", False)

    def arayuz_sifirla(self, mesaj, basarili=False):
        self.islem_devam_ediyor = False
        self.btn_baslat.configure(state="normal", text="🚀 2. Verileri Çek ve Excel'e Kaydet")
        self.btn_tarayici.configure(state="normal")
        self.chk_tr.configure(state="normal")
        self.chk_en.configure(state="normal")
        self.chk_atif.configure(state="normal")
        renk = "#2ECC71" if basarili else "#E74C3C"
        self.lbl_sistem_durumu.configure(text="Sistem: Beklemede", text_color=renk)
        self.log_yaz(mesaj)
        if basarili:
            messagebox.showinfo("İşlem Tamamlandı", mesaj)
        else:
            messagebox.showwarning("Uyarı", mesaj)

if __name__ == "__main__":
    app = PremiumTezBot()
    app.mainloop()