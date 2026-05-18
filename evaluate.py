import os
import time
import io
import logging
from PIL import Image, ImageDraw
import numpy as np
from rembg import remove, new_session
from ai_engine import BgRemoverAI

# --- YAPILANDIRMA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(BASE_DIR, "test_gorselleri", "zorlu_kenarlar")
OUTPUT_TXT = os.path.join(BASE_DIR, "evaluation_results.txt")
OUTPUT_IMAGES_DIR = os.path.join(BASE_DIR, "test_gorselleri", "analiz_sonuclari")

os.makedirs(TEST_DIR, exist_ok=True)
os.makedirs(OUTPUT_IMAGES_DIR, exist_ok=True)

# --- LOGLAMA KURULUMU ---
# Hem terminale hem de .txt dosyasına yazdırmak için logger ayarı
logger = logging.getLogger("BgRemoverEvaluator")
logger.setLevel(logging.INFO)

# Dosya İşleyicisi
file_handler = logging.FileHandler(OUTPUT_TXT, mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Konsol İşleyicisi
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def print_header(title):
    logger.info("\n" + "="*50)
    logger.info(f"--- {title} ---")
    logger.info("="*50)

def create_dummy_image(path):
    """Test için görsel yoksa basit bir geometrik şekil oluşturur."""
    img = Image.new('RGB', (800, 800), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.ellipse((200, 200, 600, 600), fill=(255, 100, 100))
    # Saç/Tüy simülasyonu için kenarlara çizgiler
    for i in range(0, 360, 5):
        x = 400 + 200 * np.cos(np.radians(i))
        y = 400 + 200 * np.sin(np.radians(i))
        draw.line((400, 400, x, y), fill=(255, 100, 100), width=2)
    img.save(path)
    return path

def calculate_metrics(mask1_array, mask2_array):
    """İki maske arasındaki IoU ve F1 (Dice) skorunu hesaplar."""
    # Sadece 0 ve 255 olan binary maskelere çevir
    m1 = (mask1_array > 127).astype(np.uint8)
    m2 = (mask2_array > 127).astype(np.uint8)
    
    intersection = np.logical_and(m1, m2).sum()
    union = np.logical_or(m1, m2).sum()
    
    iou = intersection / union if union > 0 else 0
    f1 = 2 * intersection / (m1.sum() + m2.sum()) if (m1.sum() + m2.sum()) > 0 else 0
    
    return iou, f1

def test_pseudo_ground_truth(image_path):
    print_header("1. Matematiksel Analiz (Pseudo-Ground Truth)")
    logger.info("Referans model (isnet-general-use) ve hedef model (u2net) karşılaştırılıyor...")
    
    try:
        img = Image.open(image_path)
        
        # Referans Maske (isnet-general-use)
        logger.info("Referans maske oluşturuluyor (isnet-general-use) - Bu biraz sürebilir...")
        session_isnet = new_session("isnet-general-use")
        ref_out = remove(img, session=session_isnet, only_mask=True)
        ref_mask = np.array(ref_out)
        
        # Hedef Maske (u2net - uygulamamızın varsayılanı)
        logger.info("Hedef maske oluşturuluyor (u2net)...")
        session_u2net = new_session("u2net")
        target_out = remove(img, session=session_u2net, only_mask=True)
        target_mask = np.array(target_out)
        
        iou, f1 = calculate_metrics(ref_mask, target_mask)
        
        logger.info(f"Sonuçlar:")
        logger.info(f"  - IoU (Kesişim Bölü Birleşim): {iou:.4f} (1.0 = Mükemmel Eşleşme)")
        logger.info(f"  - F1-Score (Dice)          : {f1:.4f} (1.0 = Mükemmel Eşleşme)")
        
        if iou > 0.90:
            logger.info("  -> Yorum: u2net modeli, daha ağır olan referans modele çok yakın bir başarım gösteriyor.")
        else:
            logger.info("  -> Yorum: u2net modeli ile referans model arasında belirgin farklar var.")
            
        return iou, f1
            
    except Exception as e:
        logger.error(f"Hata oluştu: {str(e)}")
        return None, None

def test_qualitative_analysis(image_path):
    print_header("2. Niteliksel Analiz (Zorlu Kenar / Alpha Matting Testi)")
    logger.info("Alpha Matting kapalı ve açık durumlar karşılaştırılıyor...")
    
    try:
        img = Image.open(image_path)
        img.thumbnail((800, 800)) # İşlem hızlanması için boyutlandır
        
        ai = BgRemoverAI("u2net")
        
        # 1. Normal İşlem
        start_t = time.time()
        normal_bytes = ai.process_image(image_path, alpha_matting=False)
        normal_out = Image.open(io.BytesIO(normal_bytes))
        logger.info(f"Normal işlem süresi: {time.time()-start_t:.2f} sn")
        
        # 2. Alpha Matting İşlemi
        start_t = time.time()
        matting_bytes = ai.process_image(image_path, alpha_matting=True)
        matting_out = Image.open(io.BytesIO(matting_bytes))
        logger.info(f"Alpha Matting işlem süresi: {time.time()-start_t:.2f} sn")
        
        # Yan yana birleştir (Orijinal | Normal | Matting)
        w, h = img.size
        combo = Image.new('RGBA', (w*3, h), (255, 255, 255, 255))
        combo.paste(img.convert('RGBA'), (0, 0))
        combo.paste(normal_out, (w, 0), normal_out)
        combo.paste(matting_out, (w*2, 0), matting_out)
        
        base_name = os.path.basename(image_path)
        out_path = os.path.join(OUTPUT_IMAGES_DIR, f"karislastirma_{base_name}")
        # RGBA'yı RGB'ye çevirip kaydet
        background = Image.new('RGB', combo.size, (255, 255, 255))
        background.paste(combo, mask=combo.split()[3])
        background.save(out_path, format="JPEG")
        
        logger.info(f"Karşılaştırma görseli kaydedildi: {out_path}")
        logger.info("Lütfen kaydedilen görseli inceleyerek saç/tüy/kenar detaylarındaki iyileşmeyi gözlemleyiniz.")
        
    except Exception as e:
        logger.error(f"Hata oluştu: {str(e)}")

def test_performance(image_path):
    print_header("3. Performans Analizi (Çözünürlük Bazlı Hız Ölçümü)")
    
    resolutions = [(500, 500), (1000, 1000), (2000, 2000)]
    ai = BgRemoverAI("u2net")
    
    try:
        orig_img = Image.open(image_path)
        
        for res in resolutions:
            # Görseli yeniden boyutlandırıp geçici dosyaya kaydet
            temp_img = orig_img.copy()
            temp_img.thumbnail(res, Image.LANCZOS)
            temp_path = os.path.join(BASE_DIR, "temp_perf_img.jpg")
            temp_img.save(temp_path)
            
            logger.info(f"Çözünürlük test ediliyor: ~{temp_img.width}x{temp_img.height} piksel")
            
            # 3 kez çalıştırıp ortalamasını al (Isınma turu dahil)
            times = []
            for i in range(3):
                start = time.time()
                # max_dim'i yüksek veriyoruz ki process_image içindeki resize engellenmesin, 
                # bizim verdiğimiz çözünürlükte çalışsın.
                ai.process_image(temp_path, max_dim=4000, alpha_matting=False)
                times.append(time.time() - start)
            
            avg_time = sum(times[1:]) / 2 if len(times) > 1 else times[0] # İlk turu (ısınma) hariç tut
            logger.info(f"  -> Ortalama İşlem Süresi: {avg_time:.3f} saniye")
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Hata oluştu: {str(e)}")

def main():
    logger.info("=== BAŞARIM ANALİZİ BAŞLATILIYOR ===")
    
    # Test klasöründe görsel var mı kontrol et
    valid_exts = ('.png', '.jpg', '.jpeg')
    test_images = [f for f in os.listdir(TEST_DIR) if f.lower().endswith(valid_exts)]
    
    if not test_images:
        logger.warning(f"'{TEST_DIR}' klasöründe test görseli bulunamadı!")
        logger.info("Otomatik olarak test için örnek bir görsel oluşturuluyor...")
        dummy_path = os.path.join(TEST_DIR, "otomatik_test_gorseli.jpg")
        create_dummy_image(dummy_path)
        test_images = ["otomatik_test_gorseli.jpg"]
    
    # Tüm görseller üzerinde testleri yürüt
    total_iou = []
    total_f1 = []
    
    for img_name in test_images:
        target_image = os.path.join(TEST_DIR, img_name)
        logger.info(f"\n>>>>> Test için seçilen görsel: {target_image} <<<<<")
        
        iou, f1 = test_pseudo_ground_truth(target_image)
        if iou is not None and f1 is not None:
            total_iou.append(iou)
            total_f1.append(f1)
            
        test_qualitative_analysis(target_image)
        test_performance(target_image)
    
    logger.info("\n" + "="*50)
    logger.info("=== GENEL SİSTEM BAŞARISI (TÜM GÖRSELLERİN ORTALAMASI) ===")
    logger.info("="*50)
    if total_iou and total_f1:
        mean_iou = sum(total_iou) / len(total_iou)
        mean_f1 = sum(total_f1) / len(total_f1)
        logger.info(f"Test Edilen Toplam Görsel Sayısı: {len(test_images)}")
        logger.info(f"Mean IoU (mIoU) Ortalama Başarım : {mean_iou:.4f}")
        logger.info(f"Mean F1-Score Ortalama Başarım : {mean_f1:.4f}")
        logger.info("-> Hocanıza sunmanız gereken sistem başarımı (Accuracy/Başarım) metriği budur.")
    else:
        logger.info("Geçerli metrik hesaplanamadı.")

    logger.info("\n=== ANALİZ TAMAMLANDI ===")
    logger.info(f"Sonuçlar {OUTPUT_TXT} dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
