import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageGrab
import pyperclip
import threading

class OCRApp:
    def __init__(self, root, ocr_engine):
        self.root = root
        self.ocr_engine = ocr_engine
        self.root.title("Text Extractor OCR")
        self.root.geometry("900x600")
        
        self.images_queue = [] 
        self.current_image_index = -1

        self._setup_ui()

    def _setup_ui(self):
        # Upper Frame
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        btn_upload = tk.Button(top_frame, text="Upload Images", command=self.upload_images, bg="#e1e1e1")
        btn_upload.pack(side=tk.LEFT, padx=10)

        btn_paste = tk.Button(top_frame, text="Paste from Clipboard", command=self.paste_from_clipboard, bg="#d1ecf1")
        btn_paste.pack(side=tk.LEFT, padx=10)

        btn_clear = tk.Button(top_frame, text="Clear", command=self.clear_all, bg="#f8d7da")
        btn_clear.pack(side=tk.RIGHT, padx=10)

        # Main Container (Split View)
        paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 1. Left Panel: List of images
        left_frame = tk.LabelFrame(paned_window, text="Image Queue")
        paned_window.add(left_frame, width=200)

        self.listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_image_select)

        # 2. Central Panel: Preview
        center_frame = tk.LabelFrame(paned_window, text="Preview")
        paned_window.add(center_frame, width=350)
        
        self.lbl_preview = tk.Label(center_frame, text="No image selected")
        self.lbl_preview.pack(fill=tk.BOTH, expand=True)
        
        btn_process = tk.Button(center_frame, text="Extract text", command=self.process_current_image, bg="#d4edda")
        btn_process.pack(fill=tk.X, padx=5, pady=5)

        # 3. Right Panel: Results
        right_frame = tk.LabelFrame(paned_window, text="Extracted text")
        paned_window.add(right_frame, width=350)

        self.txt_output = tk.Text(right_frame, wrap=tk.WORD, state=tk.DISABLED) # Read-only
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botón para copiar resultado al portapapeles (SOLICITADO)
        btn_copy = tk.Button(right_frame, text="Copy from clipboard", command=self.copy_result_to_clipboard, bg="#fff3cd")
        btn_copy.pack(fill=tk.X, padx=5, pady=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Buttons logic

    def upload_images(self):
        file_paths = filedialog.askopenfilenames(
            title="Select images",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if file_paths:
            for path in file_paths:
                self._add_image_to_queue(path, is_path=True)

    def paste_from_clipboard(self):
        try:
            image = ImageGrab.grabclipboard()
            if isinstance(image, Image.Image):
                self._add_image_to_queue(image, is_path=False)
            else:
                messagebox.showwarning("Clipboard", "No image was found in the clipboard.")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading clipboard: {e}")

    def _add_image_to_queue(self, image_data, is_path=True):
        if is_path:
            name = image_data.split("/")[-1]
            self.images_queue.append({"type": "path", "data": image_data, "name": name})
        else:
            name = f"Capture_Clipboard_{len(self.images_queue)+1}"
            self.images_queue.append({"type": "obj", "data": image_data, "name": name})
        
        self.listbox.insert(tk.END, name)
        self.status_var.set(f"Image added: {name}")

    def on_image_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.current_image_index = index
            item = self.images_queue[index]
            self._show_preview(item)

    def _show_preview(self, item):
        try:
            if item["type"] == "path":
                img = Image.open(item["data"])
            else:
                img = item["data"]
            
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
            
            self.lbl_preview.config(image=photo, text="")
            self.lbl_preview.image = photo
        except Exception as e:
            self.lbl_preview.config(text="Error loading preview")

    def process_current_image(self):
        if self.current_image_index == -1:
            messagebox.showwarning("Warning", "Select an image for the list first.")
            return

        item = self.images_queue[self.current_image_index]
        
        if item["type"] == "path":
            img_to_process = Image.open(item["data"])
        else:
            img_to_process = item["data"]

        self.status_var.set("Processing OCR...")
        self.root.config(cursor="watch")

        threading.Thread(target=self._run_ocr_thread, args=(img_to_process,)).start()

    def _run_ocr_thread(self, image):
        text = self.ocr_engine.extract_text_from_image(image)
        
        self.root.after(0, self._update_output, text)

    def _update_output(self, text):
        self.txt_output.config(state=tk.NORMAL)
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, text)
        self.txt_output.config(state=tk.DISABLED)
        
        self.status_var.set("Extraction completed.")
        self.root.config(cursor="")

    def copy_result_to_clipboard(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if text:
            pyperclip.copy(text)
            self.status_var.set("Text copied to clipboard!")
        else:
            self.status_var.set("No text to copy.")

    def clear_all(self):
        self.images_queue.clear()
        self.listbox.delete(0, tk.END)
        self.lbl_preview.config(image='', text="No images")
        self.txt_output.config(state=tk.NORMAL)
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.config(state=tk.DISABLED)
        self.current_image_index = -1
        self.status_var.set("All clear.")