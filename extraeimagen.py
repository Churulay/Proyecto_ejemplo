import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import pytesseract
import os

# Nombre del archivo donde se guardará la ruta de Tesseract
CONFIG_FILE = "tesseract_config.txt"

def get_tesseract_path():
    """
    Intenta obtener la ruta de Tesseract desde el archivo de configuración.
    Si no la encuentra, le pide al usuario que la seleccione y la guarda.
    """
    
    # 1. Comprobar si la ruta ya está guardada
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            path = f.read().strip()
            if os.path.exists(path):
                return path
            else:
                os.remove(CONFIG_FILE) # La ruta es inválida, borrar el archivo
    
    # 2. Si no, pedir al usuario que la seleccione
    try:
        messagebox.showinfo("Configuración", "Por favor, selecciona el archivo tesseract.exe. Solo tendrás que hacer esto una vez.")
        file_path = filedialog.askopenfilename(
            title="Selecciona el ejecutable de Tesseract (tesseract.exe)",
            filetypes=[("Archivos ejecutables", "tesseract.exe")]
        )
        
        if file_path:
            with open(CONFIG_FILE, "w") as f:
                f.write(file_path)
            return file_path
    except Exception as e:
        print(f"Error al intentar mostrar el cuadro de diálogo: {e}")
        return None

    return None

class OCRApp:
    def __init__(self, root, tesseract_path):
        self.root = root
        self.tesseract_path = tesseract_path
        
        try:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        except Exception as e:
            messagebox.showerror("Error de Configuración", f"No se pudo configurar la ruta de Tesseract. {e}")
            self.root.destroy()
            return
            
        self.root.title("Extractor de Texto de Imagen")
        self.root.geometry("600x500")

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        btn_select_image = tk.Button(main_frame, text="Seleccionar Imagen", command=self.open_file_dialog)
        btn_select_image.pack(pady=5)

        self.text_output = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20, font=("Arial", 12))
        self.text_output.pack(pady=10, fill=tk.BOTH, expand=True)
        self.text_output.insert(tk.END, "El texto extraído de la imagen aparecerá aquí.")
        self.text_output.configure(state='disabled')

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename(
            title="Selecciona una imagen",
            filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if file_path:
            self.process_image(file_path)

    def process_image(self, file_path):
        try:
            self.text_output.configure(state='normal')
            self.text_output.delete("1.0", tk.END)
            self.text_output.insert(tk.END, "Extrayendo texto de la imagen...")
            self.root.update_idletasks()

            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image, lang='spa')

            if not extracted_text.strip():
                extracted_text = "No se pudo extraer texto. Intenta con una imagen más clara o con texto más legible."

            self.text_output.delete("1.0", tk.END)
            self.text_output.insert(tk.END, extracted_text)

        except pytesseract.TesseractNotFoundError:
            messagebox.showerror("Error", "El motor de Tesseract no se encontró. Asegúrate de que está instalado y en el PATH de tu sistema.")
            self.text_output.delete("1.0", tk.END)
            self.text_output.insert(tk.END, "Error: Tesseract no se encontró.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")
            self.text_output.delete("1.0", tk.END)
            self.text_output.insert(tk.END, f"Error: {e}")
        finally:
            self.text_output.configure(state='disabled')

if __name__ == "__main__":
    tesseract_path = get_tesseract_path()
    if tesseract_path:
        root = tk.Tk()
        app = OCRApp(root, tesseract_path)
        root.mainloop()
    else:
        messagebox.showerror("Error de Configuración", "No se pudo encontrar o configurar la ruta de Tesseract. El programa no se puede ejecutar.")