import customtkinter as ctk
from PIL import Image, ImageOps
import threading
import webbrowser
import time
import os
import sys
import tkinter.messagebox

# --- LÓGICA DE RUTAS ---
try:
    base_path = sys._MEIPASS
except AttributeError:
    base_path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_path)
STATIC_PATH = os.path.join(base_path, "static")

# --- Importar el servidor ---
try:
    from server import app
except ImportError:
    tkinter.messagebox.showerror("Error", "No se pudo encontrar 'server.py'.")
    exit()

# --- Configuración ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
FONT_PATH = os.path.join(STATIC_PATH, "fonts", "Inter-Regular.ttf")
FONT_FAMILY = "Inter" if os.path.exists(FONT_PATH) else "system"

def invert_image_colors(image_obj):
    if image_obj.mode == 'RGBA':
        r, g, b, a = image_obj.split()
        inverted_rgb = ImageOps.invert(Image.merge('RGB', (r, g, b)))
        r2, g2, b2 = inverted_rgb.split()
        return Image.merge('RGBA', (r2, g2, b2, a))
    else:
        return ImageOps.invert(image_obj.convert('RGB'))

def start_flask_server():
    try:
        app.run(host="0.0.0.0", port=5000, use_reloader=False)
    except Exception as e:
        tkinter.messagebox.showerror("Error de Servidor", f"El puerto 5000 podría estar ocupado.\nError: {e}")

def launch_application():
    launch_button.configure(state="disabled", text="Iniciando...")
    server_thread = threading.Thread(target=start_flask_server, daemon=True)
    server_thread.start()
    time.sleep(2)
    webbrowser.open_new("http://127.0.0.1:5000")
    status_label.configure(text="¡Servidor en ejecución!", text_color="green")
    launch_button.configure(text="Servidor Activo")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("pedalColab Launcher")
        icon_path = os.path.join(STATIC_PATH, "images", "launcherlogo.ico")
        if os.path.exists(icon_path): self.iconbitmap(icon_path)
        self.geometry("500x450")
        self.resizable(False, False)
        # Objetos fuente
        self.description_font = ctk.CTkFont(family=FONT_FAMILY, size=14)
        self.button_font = ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold")
        self.footer_font = ctk.CTkFont(family=FONT_FAMILY, size=12, slant="italic")

        # Contenedor principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(padx=20, pady=20, expand=True, fill="both")
        logo_path = os.path.join(STATIC_PATH, "images", "logo.png")

        # Cargar el logo
        if os.path.exists(logo_path):
            original_image = Image.open(logo_path)
            inverted_image = invert_image_colors(original_image)
            logo_ctk_image = ctk.CTkImage(light_image=inverted_image, dark_image=inverted_image, size=(100, 100))
            logo_label = ctk.CTkLabel(self.main_frame, image=logo_ctk_image, text="")
            logo_label.pack(pady=10)

        # Descripción del proyecto
        description_text = ("Este proyecto permite una colaboración musical simple y directa.\n" "Usa el celular para subir pistas y la DAW para aplicar efectos.")
        description_label = ctk.CTkLabel(self.main_frame, text=description_text, wraplength=400, justify="center", font=self.description_font)
        description_label.pack(pady=10, padx=20)
        # Botón de lanzamiento
        global launch_button
        launch_button = ctk.CTkButton(self.main_frame, text="Launch", font=self.button_font, command=launch_application, width=200, height=50, corner_radius=25)
        launch_button.pack(pady=20)
        # Etiqueta de estado
        global status_label
        status_label = ctk.CTkLabel(self.main_frame, text="Servidor detenido.", text_color="gray", font=self.description_font)
        status_label.pack(pady=5)
        # Pie de página
        separator = ctk.CTkFrame(self.main_frame, height=2, corner_radius=1, fg_color="gray20")
        separator.pack(fill="x", padx=30, pady=10)
        author_label = ctk.CTkLabel(self.main_frame, text="Autor: Santiago Velasco García", text_color="gray50", font=self.footer_font)
        author_label.pack()
        competition_label = ctk.CTkLabel(self.main_frame, text="Presentado en: Telecommpetition 2026-1", text_color="gray50", font=self.footer_font)
        competition_label.pack()

if __name__ == "__main__":
    app_gui = App()
    app_gui.mainloop()

