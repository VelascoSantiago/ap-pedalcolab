# pedalera.py
from pedalboard import Pedalboard, Chorus, Distortion, Compressor, Delay, Reverb
from pedalboard.io import AudioFile

def procesar_audio(input_file, output_file, efectos=None):
    """
    Procesa un archivo de audio con la lista de efectos que pases.

    input_file: str → ruta del audio de entrada (.wav, .mp3)
    output_file: str → ruta del audio de salida procesado
    efectos: list → lista de instancias de efectos de pedalboard
    """
    if efectos is None:
        efectos = []

    # Cargar audio
    with AudioFile(input_file).resampled_to(44100) as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate

    # Crear pedalera
    board = Pedalboard(efectos)

    # Procesar señal
    effected = board(audio, samplerate)

    # Guardar audio procesado
    with AudioFile(output_file, 'w', samplerate, effected.shape[0]) as f:
        f.write(effected)

    return output_file


# Ejemplo de uso
if __name__ == "__main__":
    efectos = [
        Distortion(drive_db=15),
        Chorus(),
        Reverb(room_size=0.4),
        Delay(delay_seconds=0.25, feedback=0.3),
        Compressor(threshold_db=-20, ratio=2.5)
    ]

    procesar_audio("input.wav", "output.wav", efectos)
    print("Procesado guardado en output.wav")
