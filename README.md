# 🖼️ Background Removal Tool

This project is a Python-based desktop application developed for an Image Processing coursework. It does not use Artificial Intelligence; the background removal process is entirely based on the OpenCV GrabCut algorithm (GMM - Gaussian Mixture Models).

### 🚀 Features
- **OpenCV Operations:** Offline, smooth `cv2.grabCut` analysis.
- **Smart EXIF Solution:** Automatically corrects phone vertical and horizontal (Rotation) metadata.
- **Memory Optimization:** Memory and sizing issues encountered during consecutive image uploads are prevented using a "Dummy Image" logic.
