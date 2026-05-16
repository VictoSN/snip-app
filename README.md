# Snip-OCR
A Python desktop application made with PyQt6 for capturing screenshots and extracting text using OCR with snipping tool like functionalities.

## Features
1. Full screen or region capture
2. Interactive snipping overlay with drag-to-select
3. OCR text extraction via pytesseract
4. Persistent storage in SQLite
5. Multi-monitor support (Excluding drag-to-select)

## How it works
- Overlay captures a frozen screenshot of all monitors as background
- Drag to select a region, which is then captured and saved
- pytesseract extracts text from the captured image with preprocessing
- Snip's details are stored in database

## Screenshots
### Default Interface
![Default](/images/Default.png)

### Drag-to-Select
![Drag-to-Select](/images/Drag-to-Select.png)

### Coordinates
![Coordinates](/images/Coordinates.png)

### Full-Window
![Full-Window](/images/Full-Window.png)

### Multiple Snips
![Multiple Snips](/images/Multiple.png)

### Viewer
![Viewer](/images/Viewer.png)

## How to run (Windows Only)
1. Clone the repo
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install PyQt6 pytesseract Pillow mss
```
4. Install Tesseract:
```bash
# Debian/Ubuntu
sudo apt install tesseract-ocr

# Windows: download installer from https://github.com/tesseract-ocr/tesseract
```
5. Run:
```bash
python main.py
```

## License
This project is licensed under the [MIT License](LICENSE)