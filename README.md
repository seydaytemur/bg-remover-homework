# Background Removal Tool (Deep Learning - U²-Net)

This project is a Python-based desktop application developed for an Image Processing and Computer Vision coursework. The background removal process is strictly powered by the **U²-Net (U-Square-Net) Deep Learning architecture**, a state-of-the-art Salient Object Detection (SOD) model.

*(As per the coursework requirement, traditional computer vision techniques were substituted with Deep Learning approaches like U-Net for unconstrained environments).*

### Features
- **Deep Learning (AI) Core:** Background removal powered by the `u2net` deep learning architecture via `rembg`.
- **Dynamic Model Selection:** Choose from different pre-trained models (`u2net`, `u2netp`, `u2net_human`) based on your hardware and detail requirements.
- **Alpha Matting Support:** Enhanced edge smoothing for fine details like hair and complex shapes.
- **Adjustable Resolution:** Scale processing (500px to 2500px) to balance speed, memory usage, and final quality.
- **Custom Background Options:** Save your results with Transparent (PNG), White, or Black backgrounds.
- **Stability & Reset:** Real-time progress feedback and a "Reset AI Session" button for memory cleanup.
- **Automatic EXIF Orientation:** Built-in rotation correction based on image metadata.
- **Modern CustomTkinter UI:** A premium, dark-themed responsive interface.

### How to Run
Install the necessary deep learning packages and run the application:
```bash
pip install rembg numpy customtkinter Pillow
python main.py
```
