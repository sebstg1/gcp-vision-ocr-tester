import tkinter as tk
from config.settings import Config
from services.vision_engine import OcrEngine
from ui.interface import OCRApp

def main():
    Config.validate()

    ocr_service = OcrEngine(credentials_path=Config.GOOGLE_CREDENTIALS_PATH)

    root = tk.Tk()
        
    app = OCRApp(root, ocr_service)
    
    root.mainloop()

if __name__ == "__main__":
    main()