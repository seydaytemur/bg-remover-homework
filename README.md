# Background Removal Tool (Deep Learning - U²-Net)

This project is a Python-based desktop application developed for an Image Processing and Computer Vision coursework. The background removal process is strictly powered by the **U²-Net (U-Square-Net) Deep Learning architecture**, a state-of-the-art Salient Object Detection (SOD) model.

*(As per the coursework requirement, traditional computer vision techniques were substituted with Deep Learning approaches like U-Net for unconstrained environments).*

### Features
- **Deep Learning (AI) Core:** Arka plan temizleme işlemi `u2net` tabanlı derin öğrenme modeli (`rembg`) ile gerçekleştirilir.
- **Dinamik Model Seçimi:** Kullanıcı, donanımına ve ihtiyacına göre `u2net`, `u2netp` (hafif/hızlı), `u2net_human` gibi modeller arasında geçiş yapabilir.
- **Alpha Matting (Kenar Yumuşatma):** Saç, tüy ve ince detayların daha kusursuz ayıklanması için alpha matting desteği.
- **Çözünürlük Kontrolü:** İşlem hızını ve bellek kullanımını optimize etmek için ayarlanabilir çözünürlük (500px - 2500px).
- **Modern Arayüz:** CustomTkinter ile modern ve kullanıcı dostu tasarım.
- **Otomatik Rotasyon:** EXIF verilerini kullanarak görsel yönünü otomatik düzeltir.

### How to Run
Install the necessary deep learning packages and run the application:
```bash
pip install rembg numpy customtkinter Pillow
python main.py
```
