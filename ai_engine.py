from PIL import Image, ImageOps
from rembg import remove, new_session
import io

class BgRemoverAI:
    """
    Derin Öğrenme (U-2-Net) modelini barındıran yapay zeka motoru.
    Görüntüleri işler ve arka planı ayıklanmış binary formata döndürür.
    """
    def __init__(self, model_name: str = "u2net"):
        """
        Oturumu bir kez başlatarak modelin her seferinde yeniden yüklenmesini engelle (Hız Optimizasyonu)
        """
        self.model_name = model_name
        self.session = new_session(model_name)

    def change_model(self, model_name: str):
        """
        Kullanılan AI modelini değiştirir.
        """
        if self.model_name != model_name:
            self.model_name = model_name
            self.session = new_session(model_name)

    def reset_session(self):
        """
        AI oturumunu sıfırlar (Bellek temizliği için).
        """
        self.session = new_session(self.model_name)

    def process_image(self, image_path: str, max_dim: int = 1500, alpha_matting: bool = False, bg_color: str = "Transparent") -> bytes:
        try:
            # Görseli yükle ve EXIF yatay/dikey rotasyonunu otomatik düzelt
            pil_img = Image.open(image_path)
            pil_img = ImageOps.exif_transpose(pil_img)
        except Exception as e:
            raise ValueError("Görsel yüklenemedi. Dosya yolunu veya formatını kontrol ediniz.")

        # Çok büyük görsellerde RAM taşmasını engellemek için optimize et
        if max(pil_img.size) > max_dim:
            pil_img.thumbnail((max_dim, max_dim), Image.LANCZOS)

        try:
            # U-2-Net modeli ile arkaplanı ayıkla (Önbelleğe alınmış oturumu kullan)
            # alpha_matting: Kenar yumuşatma ve saç/kıl gibi detaylar için ek işlem
            result_img = remove(
                pil_img, 
                session=self.session,
                alpha_matting=alpha_matting,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=10
            )
            
            # Eğer arka plan rengi şeffaf değilse, arka planı boya
            if bg_color != "Transparent":
                # Yeni bir arka plan oluştur
                color_map = {"White": (255, 255, 255), "Black": (0, 0, 0)}
                fill_color = color_map.get(bg_color, (255, 255, 255))
                
                background = Image.new("RGB", result_img.size, fill_color)
                # Saydam görseli arka plan üzerine yapıştır (maske olarak kendisini kullan)
                background.paste(result_img, (0, 0), result_img)
                result_img = background
            
            # Arayüze geri döndürmek üzere uygun formatta byte dizisine dönüştür
            img_byte_arr = io.BytesIO()
            save_format = 'PNG' if bg_color == "Transparent" else 'JPEG'
            result_img.save(img_byte_arr, format=save_format)
            return img_byte_arr.getvalue()
        except Exception as e:
            raise RuntimeError(f"İşlem sırasında beklenmedik bir hata oluştu: {str(e)}")
