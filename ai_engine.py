from PIL import Image, ImageOps
from rembg import remove, new_session
import io

class BgRemoverAI:
    """
    Derin Öğrenme (U-2-Net) modelini barındıran yapay zeka motoru.
    Görüntüleri işler ve arka planı ayıklanmış binary formata döndürür.
    """
    def __init__(self):
        # Oturumu bir kez başlatarak modelin her seferinde yeniden yüklenmesini engelle (Hız Optimizasyonu)
        self.session = new_session()

    def process_image(self, image_path: str, max_dim: int = 1000) -> bytes:
        try:
            # Görseli yükle ve EXIF yatay/dikey rotasyonunu otomatik düzelt
            pil_img = Image.open(image_path)
            pil_img = ImageOps.exif_transpose(pil_img)
        except Exception as e:
            raise ValueError("Görsel yüklenemedi. Dosya yolunu veya formatını kontrol ediniz.")

        # Çok büyük görsellerde RAM taşmasını engellemek için optimize et
        if max(pil_img.size) > max_dim:
            pil_img.thumbnail((max_dim, max_dim), Image.LANCZOS)

        # U-2-Net modeli ile arkaplanı ayıkla (Önbelleğe alınmış oturumu kullan)
        result_img = remove(pil_img, session=self.session)
        
        # Arayüze geri döndürmek üzere PNG (saydam) formatında byte dizisine dönüştür
        img_byte_arr = io.BytesIO()
        result_img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
