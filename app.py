import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from rembg import remove
import io
import os
import threading

class BackgroundRemoverApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Arka Plan Silici")
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
        
        self.label_title = ctk.CTkLabel(self.header_frame, text="AI Background Remover", font=ctk.CTkFont(size=28, weight="bold"))
        self.label_title.pack()
        
        self.label_subtitle = ctk.CTkLabel(self.header_frame, text="Yapay zeka ile saniyeler içinde arka planı temizleyin", font=ctk.CTkFont(size=14))
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
            
            # Önizleme boyutlandırma
            preview_img = self.resize_for_preview(img)
            ctk_img = ctk.CTkImage(light_image=preview_img, dark_image=preview_img, size=preview_img.size)
            
            self.input_preview.configure(image=ctk_img, text="")
            self.output_preview.configure(image="", text="İşlemden sonra burada görünecek")
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
        
        self.status_label.configure(text="İşleniyor... Lütfen bekleyin. (İlk çalıştırmada yapay zeka modeli indirilebilir)")
        
        # Thread başlat
        thread = threading.Thread(target=self.remove_background_thread)
        thread.daemon = True
        thread.start()

    def remove_background_thread(self):
        try:
            with open(self.input_image_path, "rb") as i:
                input_data = i.read()
                output_data = remove(input_data)
                
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
