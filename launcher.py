import customtkinter as ctk
from PIL import Image, ImageOps
import threading
import webbrowser
import time
import os

# Intenta importar la variable 'app' de tu script del servidor.
try:
    from server import app
except ImportError:
    # Si hay un error, lo mostramos antes de que la app falle.
    import tkinter as tk
    root = tk.Tk()
    root.withdraw() # Ocultamos la ventana principal
    tk.messagebox.showerror("Error", "No se pudo encontrar 'server.py'. Asegúrate de que esté en la misma carpeta.")
    exit()

# --- Configuración de la Apariencia ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- LÓGICA PARA CARGAR LA FUENTE PERSONALIZADA ---
FONT_PATH = os.path.join("static", "fonts", "Inter-Regular.ttf")
FONT_FAMILY = "Inter" if os.path.exists(FONT_PATH) else "system" # Usa 'Inter' si existe, si no la fuente del sistema

# --- FUNCIÓN PARA INVERTIR COLORES DE LA IMAGEN ---
def invert_image_colors(image_obj):
    """Invierte los colores de una imagen PIL, preservando la transparencia."""
    if image_obj.mode == 'RGBA':
        # Separar los canales de color (R, G, B) de la transparencia (A)
        r, g, b, a = image_obj.split()
        rgb_image = Image.merge('RGB', (r, g, b))
        
        # Invertir solo los canales de color
        inverted_rgb = ImageOps.invert(rgb_image)
        
        # Volver a juntar los canales invertidos con la transparencia original
        r2, g2, b2 = inverted_rgb.split()
        return Image.merge('RGBA', (r2, g2, b2, a))
    else:
        # Si no hay transparencia, simplemente invertir la imagen
        return ImageOps.invert(image_obj.convert('RGB'))

# --- Funciones para el lanzador (la lógica es la misma) ---

def start_flask_server():
    """Esta función se ejecuta en un hilo separado para no bloquear la interfaz."""
    try:
        app.run(host="0.0.0.0", port=5000, use_reloader=False)
    except Exception:
        # En una app real, aquí registraríamos el error en un log.
        # Por ahora, simplemente evitamos que la app se cierre.
        print("Error: El puerto 5000 podría estar ocupado.")

def launch_application():
    """Se llama al presionar el botón 'Launch'."""
    launch_button.configure(state="disabled", text="Iniciando...")
    
    server_thread = threading.Thread(target=start_flask_server, daemon=True)
    server_thread.start()
    
    time.sleep(2)
    
    # Corregido: La IP correcta es 127.0.0.1
    webbrowser.open_new("http://127.0.0.1:5000")
    
    status_label.configure(text="¡Servidor en ejecución!", text_color="green")
    launch_button.configure(text="Servidor Activo")

# --- Creación de la Interfaz Gráfica (GUI) con CustomTkinter ---

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("pedalColab Launcher")

        # --- LÍNEA NUEVA PARA EL ICONO ---
        # Definimos la ruta al icono y lo aplicamos a la ventana
        icon_path = os.path.join("static", "images", "launcherlogo.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.geometry("500x450")
        self.resizable(False, False)

        # --- Creación de objetos de fuente ---
        self.description_font = ctk.CTkFont(family=FONT_FAMILY, size=14)
        self.button_font = ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold")
        self.footer_font = ctk.CTkFont(family=FONT_FAMILY, size=12, slant="italic")

        # Contenedor principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(padx=20, pady=20, expand=True, fill="both")
        
        # Cargar el logo
        logo_path_jpg = os.path.join("static", "images", "logo.png") # O usa logo.png
        if os.path.exists(logo_path_jpg):
            # 1. Abrir la imagen original
            original_image = Image.open(logo_path_jpg)
            
            # 2. Invertir sus colores con nuestra nueva función
            inverted_image = invert_image_colors(original_image)
            
            # 3. Usar la imagen invertida en la interfaz
            logo_ctk_image = ctk.CTkImage(light_image=inverted_image,
                                          dark_image=inverted_image,
                                          size=(100, 100))
            logo_label = ctk.CTkLabel(self.main_frame, image=logo_ctk_image, text="")
            logo_label.pack(pady=10)
        
        # Descripción del proyecto
        description_text = (
            "Este proyecto permite una colaboración musical simple y directa.\n"
            "Usa el celular para subir pistas y la DAW para aplicar efectos."
        )
        description_label = ctk.CTkLabel(self.main_frame, text=description_text,
                                         wraplength=400, justify="center", font=self.description_font)
        description_label.pack(pady=10, padx=20)
        
        # Botón de lanzamiento
        global launch_button
        launch_button = ctk.CTkButton(self.main_frame, text="Launch",
                                      font=self.button_font,
                                      command=launch_application,
                                      width=200, height=50, corner_radius=25)
        launch_button.pack(pady=20)
        
        # Etiqueta de estado
        global status_label
        status_label = ctk.CTkLabel(self.main_frame, text="Servidor detenido.", text_color="gray", font=self.description_font)
        status_label.pack(pady=5)

        # --- SECCIÓN DE PIE DE PÁGINA ---
        separator = ctk.CTkFrame(self.main_frame, height=2, corner_radius=1, fg_color="gray20")
        separator.pack(fill="x", padx=30, pady=10)

        author_label = ctk.CTkLabel(self.main_frame, text="Autor: Santiago Velasco García", text_color="gray50", font=self.footer_font)
        author_label.pack()

        competition_label = ctk.CTkLabel(self.main_frame, text="Presentado en: Telecommpetition 2026-1", text_color="gray50", font=self.footer_font)
        competition_label.pack()


if __name__ == "__main__":
    app_gui = App()
    app_gui.mainloop()
