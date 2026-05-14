import pytesseract
import mss, mss.tools
from PIL import (
    Image, ImageOps
)
from storage import Storage
from pathlib import Path
from datetime import datetime

class Snipping:
    def __init__(self):
        self.storage = Storage()
        self.screenshots_folder = Path("screenshots")
    
    def ocr(self, img):
        pil_img = Image.frombytes("RGB", img.size, img.rgb)

        # Image Processing
        ## 1. Convert to grayscale
        pil_img = pil_img.convert("L") 

        ## 2. Upscale
        pil_img = pil_img.resize((pil_img.width * 2, pil_img.height *2))

        ## 3. Thresholds
        pil_img = pil_img.point(lambda p: 255 if p > 160 else 0)

        print("OCR Done")
        config = "--psm 6"
        return pytesseract.image_to_string(pil_img, config=config)

    def screenshot(self, x='', y='', w='', h=''):
        self.screenshots_folder.mkdir(exist_ok=True)

        with mss.mss() as sct:
            if not all([x, y, w, h]):
                monitor = sct.monitors[2]
                img = sct.grab(monitor)
            else:
                x = int(x); y = int(y); w = int(w); h = int(h)
                region = {
                    "left": x,
                    "top": y,
                    "width": w,
                    "height": h
                }
                img = sct.grab(region)

            now = datetime.now() # Capture the time for name and date
            name = "Image_" + now.strftime('%y%m%d_%H%M%S.%f')[:-3]
            date = now.strftime('%Y%m%d_%H%M%S.%f')[:-3]
            ocr_text = self.ocr(img) # Convert image into text
            output = str(self.screenshots_folder / f"{name}.png")

            mss.tools.to_png(img.rgb, img.size, output=output)
            self.storage.add_snip(name, ocr_text, x, y, w, h, date, f"{self.screenshots_folder}/{name}.png")