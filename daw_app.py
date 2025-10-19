# daw_app.py
import soundfile as sf
from pedalboard import (
    Pedalboard,
    Distortion,
    Bitcrush,
    Clipping,
    Chorus,
    Phaser,
    Reverb,
    Delay,
    PitchShift,
    Compressor
)

def procesar_audio(input_path, output_path, effects_config):
    """
    Procesa audio a partir de un dict de configuración de efectos.
    """
    try:
        audio, sample_rate = sf.read(input_path)

        # Construir lista de efectos según la configuración
        efectos = []

        # Distorsión / saturación
        if effects_config.get("dist", 0) > 0:
            efectos.append(Distortion(drive_db=effects_config["dist"] * 30))

        # Bitcrush (mapear slider 0..1 a bit depth 4..24)
        if effects_config.get("bitcrush", 0) > 0:
            bd = max(4, int(24 - effects_config["bitcrush"] * 20))
            efectos.append(Bitcrush(bit_depth=bd))

        # Clipping (umbral mapeado)
        if effects_config.get("clipping", 0) > 0:
            threshold_db = -0.1 - effects_config["clipping"] * 1.9
            efectos.append(Clipping(threshold_db=threshold_db))

        # Modulación
        if effects_config.get("chorus", 0) > 0:
            efectos.append(Chorus(rate_hz=1.5, depth=effects_config["chorus"], mix=0.5))
        if effects_config.get("phaser", 0) > 0:
            efectos.append(Phaser(rate_hz=1.0, depth=effects_config["phaser"], feedback=0.5))

        # Reverb / Delay
        if effects_config.get("reverb", 0) > 0:
            efectos.append(Reverb(room_size=effects_config["reverb"], damping=0.5, wet_level=0.3))
        if effects_config.get("delay", 0) > 0:
            efectos.append(Delay(delay_seconds=effects_config["delay"], feedback=0.3, mix=0.4))

        # Pitch shift
        if effects_config.get("pitchshift", 0) != 0:
            efectos.append(PitchShift(semitones=effects_config["pitchshift"]))

        # Compresor
        if effects_config.get("comp", 0) > 0:
            efectos.append(Compressor(threshold_db=-20, ratio=1 + effects_config["comp"] * 4))

        # Crear la pedalera con sample_rate — patrón compatible
        board = Pedalboard(efectos)

        # Procesar
        processed_audio = board(audio, sample_rate=sample_rate)

        # Guardar resultado
        sf.write(output_path, processed_audio, sample_rate)
        print(f"Audio procesado y guardado en: {output_path}")

    except Exception as e:
        print(f"Error al procesar el audio: {e}")
        raise
