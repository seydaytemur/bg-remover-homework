import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps
import threading
import os
import io

class BackgroundRemoverUI(ctk.CTk):
    def __init__(self, ai_engine):
        super().__init__()
        self.ai_engine = ai_engine

        self.title("Arka Plan Kaldırma Aracı")
        self.geometry("1000x800")

        # Modern Tema Ayarları
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.configure(fg_color="#1E1E24")

        # Değişkenler
        self.input_image_path = None
        self.output_image_data = None
        self.processing = False

        self.setup_ui()

    def setup_ui(self):
        # Ana Frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Başlık ve Alt Başlık
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        self.label_title = ctk.CTkLabel(self.header_frame, text="✨ Arka Plan Temizleme Aracı", font=ctk.CTkFont(family="Roboto", size=32, weight="bold"), text_color="#E0E0E0")
        self.label_title.pack()
        
        self.label_subtitle = ctk.CTkLabel(self.header_frame, text="Derin Öğrenme (U²-Net) Yapay Zeka modeli ile arka plan temizliği", font=ctk.CTkFont(family="Roboto", size=15), text_color="#A0A0A0")
        self.label_subtitle.pack(pady=(5, 0))

        # Görsel Alanı (Giriş ve Çıkış Yan Yana)
        self.image_area = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.image_area.pack(fill="both", expand=True)

        # Giriş Görseli Paneli
        self.input_frame = ctk.CTkFrame(self.image_area, fg_color="#2B2B36", corner_radius=15, border_width=1, border_color="#3A3A4A")
        self.input_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.input_label = ctk.CTkLabel(self.input_frame, text="📸 Orijinal Görsel", font=ctk.CTkFont(family="Roboto", size=16, weight="bold"), text_color="#CCCCCC")
        self.input_label.pack(pady=(15, 5))
        
        self.input_preview = ctk.CTkLabel(self.input_frame, text="Lütfen bir görsel seçin", width=400, height=400, fg_color="#1F1F28", corner_radius=15)
        self.input_preview.pack(padx=20, pady=(5, 20), fill="both", expand=True)

        # Çıkış Görseli Paneli
        self.output_frame = ctk.CTkFrame(self.image_area, fg_color="#2B2B36", corner_radius=15, border_width=1, border_color="#3A3A4A")
        self.output_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.output_label = ctk.CTkLabel(self.output_frame, text="🎯 Sonuç", font=ctk.CTkFont(family="Roboto", size=16, weight="bold"), text_color="#CCCCCC")
        self.output_label.pack(pady=(15, 5))
        
        self.output_preview = ctk.CTkLabel(self.output_frame, text="İşlemden sonra burada görünecek", width=400, height=400, fg_color="#1F1F28", corner_radius=15)
        self.output_preview.pack(padx=20, pady=(5, 20), fill="both", expand=True)

        # Kontrol Paneli
        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="#2B2B36", corner_radius=15, border_width=1, border_color="#3A3A4A")
        self.controls_frame.pack(fill="x", pady=20)

        self.btn_select = ctk.CTkButton(self.controls_frame, text="🖼️ Görsel Seç", height=60, corner_radius=6, font=ctk.CTkFont(family="Arial", size=17, weight="bold"), command=self.select_image, fg_color="#3498DB", hover_color="#2980B9")
        self.btn_select.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        self.btn_remove = ctk.CTkButton(self.controls_frame, text="✂️ Arka Planı Sil", height=60, corner_radius=6, font=ctk.CTkFont(family="Arial", size=17, weight="bold"), command=self.start_removal, state="disabled", fg_color="#2ECC71", hover_color="#27AE60", text_color_disabled="#E0E0E0")
        self.btn_remove.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        self.btn_save = ctk.CTkButton(self.controls_frame, text="💾 Kaydet", height=60, corner_radius=6, font=ctk.CTkFont(family="Arial", size=17, weight="bold"), command=self.save_image, state="disabled", fg_color="#9B59B6", hover_color="#8E44AD", text_color_disabled="#E0E0E0")
        self.btn_save.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        # İlerleme Çubuğu Area
        self.progress_frame = ctk.CTkFrame(self.main_frame, height=40, fg_color="transparent")
        self.progress_frame.pack(fill="x", pady=(0, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=100)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()

        # Durum Çubuğu
        self.status_bar = ctk.CTkFrame(self, height=35, fg_color="#18181D", corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="✅ Hazır", font=ctk.CTkFont(family="Roboto", size=13), text_color="#AAAAAA")
        self.status_label.pack(side="left", padx=20, pady=5)

    def select_image(self):
        if self.processing: return
        
        file_path = filedialog.askopenfilename(filetypes=[("Görsel Dosyaları", "*.jpg *.jpeg *.png")])
        if file_path:
            self.input_image_path = file_path
            img = Image.open(file_path)
            img = ImageOps.exif_transpose(img)
            
            preview_img = self.resize_for_preview(img)
            ctk_img = ctk.CTkImage(light_image=preview_img, dark_image=preview_img, size=preview_img.size)
            
            empty_img = ctk.CTkImage(light_image=Image.new("RGBA", (1, 1), (255, 255, 255, 0)), size=(1, 1))
            self.output_image_data = None
            self.input_preview.configure(image=ctk_img, text="")
            self.output_preview.configure(image=empty_img, text="İşlemden sonra burada görünecek")
            self.btn_remove.configure(state="normal")
            self.btn_save.configure(state="disabled")
            self.status_label.configure(text=f"Dosya yüklendi: {os.path.basename(file_path)}")

    def resize_for_preview(self, img):
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
        
        self.status_label.configure(text="🧠 İşleniyor: U²-Net Derin Öğrenme (AI) modeli devrede. Lütfen bekleyin...")
        
        dummy_img = ctk.CTkImage(light_image=Image.new("RGBA", (1, 1), (255, 255, 255, 0)), size=(1, 1))
        self.output_preview.configure(image=dummy_img, text="⏳ İŞLEM BAŞLADI\n\nLütfen bekleyin...", font=ctk.CTkFont(family="Roboto", size=16, weight="bold"), text_color="#F39C12")
        self.update_idletasks()
        
        # Yüksek doğruluk için her zaman alpha matting açık, çözünürlük 2000 ve saydam arka plan kullanılıyor
        thread = threading.Thread(target=self.remove_background_thread, args=(True, 2000, "Transparent"))
        thread.daemon = True
        thread.start()

    def remove_background_thread(self, use_alpha, resolution, bg_color):
        try:
            output_data = self.ai_engine.process_image(self.input_image_path, alpha_matting=use_alpha, max_dim=resolution, bg_color=bg_color)
            self.after(0, self.on_processing_complete, output_data)
        except Exception as e:
            self.after(0, self.on_processing_error, str(e))

    def on_processing_complete(self, output_data):
        try:
            self.output_image_data = output_data
            
            # Sonucu Pillow ile belleğe yüklerken io.BytesIO kullanıyoruz (io import edildi)
            result_img = Image.open(io.BytesIO(output_data))
            preview_img = self.resize_for_preview(result_img)
            ctk_img = ctk.CTkImage(light_image=preview_img, dark_image=preview_img, size=preview_img.size)
            
            self.output_preview.configure(image=ctk_img, text="")
            self.finish_processing("✅ İşlem tamamlandı!")
            self.btn_save.configure(state="normal")
        except Exception as e:
             self.on_processing_error(f"Görüntü oluşturma hatası: {str(e)}")

    def on_processing_error(self, error_msg):
        messagebox.showerror("Hata", f"İşlem sırasında bir hata oluştu:\n{error_msg}")
        self.finish_processing("❌ Hata oluştu!")

    def finish_processing(self, status_text):
        self.processing = False
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_select.configure(state="normal")
        self.status_label.configure(text=status_text)
        
    def save_image(self):
        if not self.output_image_data:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Görseli", "*.png")],
            initialfile="arkaplan_temizlenmis.png"
        )
        
        if file_path:
            with open(file_path, 'wb') as f:
                f.write(self.output_image_data)
            self.status_label.configure(text=f"✅ Görsel kaydedildi: {os.path.basename(file_path)}")
            messagebox.showinfo("Başarılı", "Görsel başarıyla kaydedildi!")
