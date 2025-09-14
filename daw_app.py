# daw_app.py
# Este archivo contiene el motor de procesamiento de audio.
import soundfile as sf
from pedalboard import Pedalboard

def procesar_audio(input_path, output_path, efectos):
    """
    Lee un archivo de audio, le aplica una cadena de efectos
    y lo guarda en una nueva ubicación.

    Args:
        input_path (str): Ruta al archivo de audio de entrada.
        output_path (str): Ruta donde se guardará el archivo procesado.
        efectos (list): Una lista de objetos de efecto de la librería pedalboard.
    """
    try:
        # Cargar el archivo de audio
        audio, sample_rate = sf.read(input_path)

        # Crear una pedalera (cadena de efectos) con los efectos seleccionados
        board = Pedalboard(efectos, sample_rate=sample_rate)

        # Procesar el audio
        processed_audio = board(audio)

        # Guardar el nuevo archivo de audio
        sf.write(output_path, processed_audio, sample_rate)

        print(f"Archivo procesado y guardado en: {output_path}")

    except Exception as e:
        print(f"Error al procesar el audio: {e}")