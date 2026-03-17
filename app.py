import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps
import cv2
import numpy as np
import io
import os
import threading

class BackgroundRemoverApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Arka Plan Kaldırma Aracı")
        self.geometry("1000x700")

        # Modern Tema Ayarları
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Değişkenler
        self.input_image_path = None
        self.output_image_data = None
        self.processing = False

        # Arayüz Oluşturma
        self.setup_ui()

    def setup_ui(self):
        # Ana Frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Başlık ve Alt Başlık
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        self.label_title = ctk.CTkLabel(self.header_frame, text="Arka Plan Temizleme Aracı", font=ctk.CTkFont(size=28, weight="bold"))
        self.label_title.pack()
        
        self.label_subtitle = ctk.CTkLabel(self.header_frame, text="Görüntü İşleme (OpenCV) algoritmaları ile saniyeler içinde arka planı temizleyin", font=ctk.CTkFont(size=14))
        self.label_subtitle.pack()

        # Görsel Alanı (Giriş ve Çıkış Yan Yana)
        self.image_area = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.image_area.pack(fill="both", expand=True)

        # Giriş Görseli Paneli
        self.input_frame = ctk.CTkFrame(self.image_area)
        self.input_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.input_label = ctk.CTkLabel(self.input_frame, text="Orijinal Görsel", font=ctk.CTkFont(weight="bold"))
        self.input_label.pack(pady=10)
        
        self.input_preview = ctk.CTkLabel(self.input_frame, text="Lütfen bir görsel seçin", width=400, height=400, fg_color="gray15", corner_radius=10)
        self.input_preview.pack(padx=20, pady=10, fill="both", expand=True)

        # Çıkış Görseli Paneli
        self.output_frame = ctk.CTkFrame(self.image_area)
        self.output_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.output_label = ctk.CTkLabel(self.output_frame, text="Sonuç", font=ctk.CTkFont(weight="bold"))
        self.output_label.pack(pady=10)
        
        self.output_preview = ctk.CTkLabel(self.output_frame, text="İşlemden sonra burada görünecek", width=400, height=400, fg_color="gray15", corner_radius=10)
        self.output_preview.pack(padx=20, pady=10, fill="both", expand=True)

        # Kontrol Paneli
        self.controls_frame = ctk.CTkFrame(self.main_frame, height=100)
        self.controls_frame.pack(fill="x", pady=20)

        self.btn_select = ctk.CTkButton(self.controls_frame, text="Görsel Seç", height=40, font=ctk.CTkFont(size=14, weight="bold"), command=self.select_image)
        self.btn_select.pack(side="left", expand=True, padx=20, pady=20)

        self.btn_remove = ctk.CTkButton(self.controls_frame, text="Arka Planı Sil", height=40, font=ctk.CTkFont(size=14, weight="bold"), command=self.start_removal, state="disabled", fg_color="#2ecc71", hover_color="#27ae60")
        self.btn_remove.pack(side="left", expand=True, padx=20, pady=20)

        self.btn_save = ctk.CTkButton(self.controls_frame, text="Kaydet", height=40, font=ctk.CTkFont(size=14, weight="bold"), command=self.save_image, state="disabled")
        self.btn_save.pack(side="left", expand=True, padx=20, pady=20)

        # İlerleme Çubuğu Area
        self.progress_frame = ctk.CTkFrame(self.main_frame, height=40, fg_color="transparent")
        self.progress_frame.pack(fill="x", pady=(0, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=100)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget() # Başlangıçta gizli

        # Durum Çubuğu
        self.status_bar = ctk.CTkFrame(self, height=30, fg_color="gray10")
        self.status_bar.pack(side="bottom", fill="x")
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Hazır", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=20)

    def select_image(self):
        if self.processing: return
        
        file_path = filedialog.askopenfilename(filetypes=[("Görsel Dosyaları", "*.jpg *.jpeg *.png")])
        if file_path:
            self.input_image_path = file_path
            img = Image.open(file_path)
            img = ImageOps.exif_transpose(img) # EXIF rotasyonunu düzelt
            
            # Önizleme boyutlandırma
            preview_img = self.resize_for_preview(img)
            ctk_img = ctk.CTkImage(light_image=preview_img, dark_image=preview_img, size=preview_img.size)
            
            # Temizlik - Askıda kalmayı önlemek için yeni resim eklendiğinde eski sonuçları GUI'den düşür
            # CustomTkinter'da image=None hatası ("pyimage doesn't exist") yaşanmaması için boş bir resim ataması
            empty_img = ctk.CTkImage(light_image=Image.new("RGBA", (1, 1), (255, 255, 255, 0)), size=(1, 1))
            self.output_image_data = None
            self.input_preview.configure(image=ctk_img, text="")
            self.output_preview.configure(image=empty_img, text="İşlemden sonra burada görünecek")
            self.btn_remove.configure(state="normal")
            self.btn_save.configure(state="disabled")
            self.status_label.configure(text=f"Dosya yüklendi: {os.path.basename(file_path)}")

    def resize_for_preview(self, img):
        # En boy oranını koruyarak 400x400 içine sığdır
        img.thumbnail((400, 400))
        return img

    def start_removal(self):
        if not self.input_image_path or self.processing:
            return

        self.processing = True
        self.btn_remove.configure(state="disabled")
        self.btn_select.configure(state="disabled")
        self.btn_save.configure(state="disabled")
        
        self.progress_bar.pack(fill="x", padx=100)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        self.status_label.configure(text="İşleniyor: OpenCV (GrabCut) algoritması resimdeki tüm objeleri tarıyor. Lütfen bekleyin...")
        
        # Kullanıcının net görebilmesi için işlemi büyük kutuya da yaz!
        # Hata önlemek için geçici 1x1 şeffaf görsel
        dummy_img = ctk.CTkImage(light_image=Image.new("RGBA", (1, 1), (255, 255, 255, 0)), size=(1, 1))
        self.output_preview.configure(image=dummy_img, text="⏳ İŞLEM BAŞLADI\nLütfen bekleyin, pikseller taranıyor...")
        self.update_idletasks() # UI'nin thread'e girmeden önce kendini yenilemesini zorunlu kıl
        
        # Thread başlat
        thread = threading.Thread(target=self.remove_background_thread)
        thread.daemon = True
        thread.start()

    def remove_background_thread(self):
        try:
            # OpenCV ile doğrudan okumak yerine Pillow ile okuyup EXIF rotasyonunu düzeltiyoruz.
            try:
                pil_img = Image.open(self.input_image_path)
                pil_img = ImageOps.exif_transpose(pil_img) # Telefon kamerası vb. EXIF yan yatmalarını 90 derece düzelt
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                # Pillow'dan numpy matrisine çevir ve OpenCV'nin BGR formatına uyarla
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            except Exception as e:
                raise ValueError("Görsel yüklenemedi. Dosya yolunu veya formatını kontrol ediniz.")

            # Optimizasyon: Çok büyük resimlerde GrabCut'ın donmasını engellemek için küçült
            max_dim = 800
            height, width = img.shape[:2]
            if max(height, width) > max_dim:
                scale = max_dim / max(height, width)
                img = cv2.resize(img, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # GrabCut için maske ve modeller
            mask = np.zeros(img.shape[:2], np.uint8)
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)
            
            # Adımlar teke indiği için UI bildirimini kaldırıyoruz ve tüm işi GrabCut dikdörtgen hesaplamasına devrediyoruz.
            # Olası ilgi alanını merkeze oturt (Kenarlardan daha az pay ver ki objelerin kenarları kesilmesin - %5)
            height, width = img.shape[:2]
            rect = (int(width * 0.05), int(height * 0.05), int(width * 0.9), int(height * 0.9))
            
            # Tüm işi doğrudan GrabCut algoritmasının kendi zekasına (Komşuluk analizine) bırakıyoruz (10 Döngü)
            cv2.grabCut(img_rgb, mask, rect, bgdModel, fgdModel, 10, cv2.GC_INIT_WITH_RECT)
            
            # Ön plan (1, 3) ve arka plan (0, 2) piksellerini ayırarak 0 ve 1'lerden oluşan nihai maskeyi bul
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            
            # RGB'yi RGBA'ya (Saydamlık - Alpha kanalı) çevir
            rgba = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2RGBA)
            
            # Maskeye göre asıl ön planda kalan alanın dışını şeffaf (görünmez) yap
            rgba[:, :, 3] = mask2 * 255
            
            # Arayüzde gösterebilmek ve Pillow ile kaydedebilmek için array'i binary veriye çevir
            pil_img = Image.fromarray(rgba)
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='PNG')
            output_data = img_byte_arr.getvalue()
                
            self.after(0, self.on_processing_complete, output_data)
        except Exception as e:
            self.after(0, self.on_processing_error, str(e))

    def on_processing_complete(self, output_data):
        self.output_image_data = output_data
        
        # Sonucu göster
        img = Image.open(io.BytesIO(output_data))
        preview_img = self.resize_for_preview(img)
        ctk_img = ctk.CTkImage(light_image=preview_img, dark_image=preview_img, size=preview_img.size)
        
        self.output_preview.configure(image=ctk_img, text="")
        self.finish_processing("İşlem başarıyla tamamlandı!")
        self.btn_save.configure(state="normal")

    def on_processing_error(self, error_msg):
        self.finish_processing(f"Hata: {error_msg}")
        messagebox.showerror("Hata", f"Görsel işlenirken bir sorun oluştu:\n{error_msg}")

    def finish_processing(self, status_text):
        self.processing = False
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_select.configure(state="normal")
        self.btn_remove.configure(state="normal")
        self.status_label.configure(text=status_text)

    def save_image(self):
        if not self.output_image_data:
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png", 
            filetypes=[("PNG dosyası", "*.png")],
            initialfile="arkaplan_silindi.png"
        )
        
        if save_path:
            try:
                with open(save_path, "wb") as o:
                    o.write(self.output_image_data)
                self.status_label.configure(text=f"Kaydedildi: {os.path.basename(save_path)}")
                messagebox.showinfo("Başarılı", "Görsel başarıyla kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Kaydedilirken bir sorun oluştu: {str(e)}")

if __name__ == "__main__":
    app = BackgroundRemoverApp()
    app.mainloop()
