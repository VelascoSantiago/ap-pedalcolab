from pedalboard import Pedalboard, Chorus, Distortion, Compressor
from pedalboard.io import AudioFile

# Cargar audio
with AudioFile("input.wav").resampled_to(44100) as f:
    audio = f.read(f.frames)
    samplerate = f.samplerate

# Crear pedalera
board = Pedalboard([
    Chorus(),
    Distortion(),
    Compressor()
])

# Procesar
effected = board(audio, samplerate)

# Guardar audio procesado
with AudioFile("output.wav", 'w', samplerate, effected.shape[0]) as f:
    f.write(effected)
