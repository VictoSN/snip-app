import mss, mss.tools
from pathlib import Path
from datetime import datetime

class Snipping:
    def __init__(self):
        self.screenshots_folder = Path("screenshots")
    
    def screenshot(self, x='', y='', w='', h=''):
        self.screenshots_folder.mkdir(exist_ok=True)
        name = "Image_" + datetime.now().strftime('%y%m%d_%H%M%S.%f')[:-5]
        output = str(self.screenshots_folder / f"{name}.png")

        with mss.mss() as sct:
            if not all([x, y, w, h]):
                monitor = sct.monitors[1]
                img = sct.grab(monitor)
            else:
                region = {
                    "left": x,
                    "top": y,
                    "width": w,
                    "height": h
                }
                img = sct.grab(region)
            mss.tools.to_png(img.rgb, img.size, output=output)