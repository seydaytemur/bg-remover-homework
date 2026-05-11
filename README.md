# Background Removal Tool (Deep Learning - U²-Net)

This project is a Python-based desktop application developed for an Image Processing and Computer Vision coursework. The background removal process is strictly powered by the **U²-Net (U-Square-Net) Deep Learning architecture**, a state-of-the-art Salient Object Detection (SOD) model.

*(As per the coursework requirement, traditional computer vision techniques were substituted with Deep Learning approaches like U-Net for unconstrained environments).*

### Features
- **Deep Learning (AI) Core:** Background removal powered by the high-accuracy `u2net` deep learning architecture via `rembg`.
- **Streamlined UI:** A simplified, one-click interface designed for ease of use without complex settings.
- **Maximum Accuracy (Auto-configured):** Alpha matting and high-resolution processing (2000px) are hardcoded for flawless edge detection on hair, fur, and complex objects.
- **Automatic EXIF Orientation:** Built-in rotation correction based on image metadata for both preview and output.
- **Evaluation Dataset Included:** Comes with a `test_gorselleri` folder containing real-world challenging photos (animals, transparent objects, complex backgrounds) to test the AI's robustness.
- **Modern CustomTkinter UI:** A premium, dark-themed responsive interface.

### How to Run
Install the necessary deep learning packages and run the application:
```bash
pip install rembg numpy customtkinter Pillow
python main.py
```
