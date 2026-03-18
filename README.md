# Background Removal Tool (Deep Learning - U²-Net)

This project is a Python-based desktop application developed for an Image Processing and Computer Vision coursework. The background removal process is strictly powered by the **U²-Net (U-Square-Net) Deep Learning architecture**, a state-of-the-art Salient Object Detection (SOD) model.

*(As per the coursework requirement, traditional computer vision techniques were substituted with Deep Learning approaches like U-Net for unconstrained environments).*

### Features
- **Deep Learning (AI) Core:** Flawless background removal using the pre-trained U-Net based salient object detection model (`rembg`).
- **Complex Scene Handling:** Effectively segments decoupled objects (like scattered dice) or complex lighting conditions (like selfies) where traditional contrast-based CV methods fail.
- **Smart EXIF Solution:** Automatically corrects phone vertical and horizontal (Rotation) metadata using PIL.
- **Memory Optimization:** Memory leaks encountered during consecutive image uploads are prevented using a "Dummy Image" rendering technique.
- **Modern UI:** Built on CustomTkinter with Soft-UI (Flat Design) principles for an elegant User Experience.

### How to Run
Install the necessary deep learning packages and run the application:
```bash
pip install rembg numpy customtkinter Pillow
python main.py
```
