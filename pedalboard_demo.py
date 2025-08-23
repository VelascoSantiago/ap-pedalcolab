#!/usr/bin/env python3
"""
Pedalboard virtual (demo) - distorsión + delay + filtro pasabajo
- Si das un archivo WAV: lo procesa.
- Si no: genera una señal de guitarra sintética (A4=440Hz con armónicos).
Guarda el resultado como output_processed.wav
"""
import argparse
import numpy as np
from scipy.io import wavfile

def normalize(x, eps=1e-9):
    m = np.max(np.abs(x)) + eps
    return x / m

def to_float(x):
    # Convierte cualquier tipo de dato de audio a float32 en [-1,1]
    if x.dtype == np.int16:
        return x.astype(np.float32) / 32768.0
    if x.dtype == np.int32:
        return x.astype(np.float32) / 2147483648.0
    if x.dtype == np.uint8:
        return (x.astype(np.float32) - 128.0) / 128.0
    return x.astype(np.float32)

def to_int16(x):
    x = np.clip(x, -1.0, 1.0)
    return (x * 32767.0).astype(np.int16)

# --- Efectos ---
def distorsion(signal, gain=8.0, threshold=0.3):
    y = signal * gain
    y = np.clip(y, -threshold, threshold)
    return normalize(y)

def delay(signal, sr, delay_time=0.25, decay=0.4):
    d = int(sr * delay_time)
    out = np.zeros(len(signal) + d, dtype=np.float32)
    out[:len(signal)] = signal
    out[d:] += decay * signal
    return normalize(out)

def filtro_pasabajo(signal, sr, cutoff=2000.0):
    RC = 1.0 / (2.0 * np.pi * cutoff)
    dt = 1.0 / sr
    alpha = dt / (RC + dt)
    y = np.zeros_like(signal, dtype=np.float32)
    for i in range(1, len(signal)):
        y[i] = y[i-1] + alpha * (signal[i] - y[i-1])
    return normalize(y)

def synth_guitar(sr=44100, seconds=2.0, f0=440.0):
    t = np.linspace(0, seconds, int(sr*seconds), endpoint=False)
    s = (np.sin(2*np.pi*f0*t) 
         + 0.5*np.sin(2*np.pi*2*f0*t) 
         + 0.3*np.sin(2*np.pi*3*f0*t))
    # envolvente simple para ataque/caída
    env = np.exp(-3*t)
    s *= env
    return normalize(s).astype(np.float32), sr

def main():
    parser = argparse.ArgumentParser(description="Pedalboard demo: distorsión + delay + LPF")
    parser.add_argument("--in_wav", type=str, default=None, help="Ruta a WAV mono/estéreo")
    parser.add_argument("--gain", type=float, default=8.0, help="Ganancia distorsión")
    parser.add_argument("--clip", type=float, default=0.3, help="Umbral de clipping")
    parser.add_argument("--delay_time", type=float, default=0.25, help="Delay en segundos")
    parser.add_argument("--decay", type=float, default=0.4, help="Decaimiento del delay")
    parser.add_argument("--cutoff", type=float, default=2000.0, help="Corte LPF en Hz")
    parser.add_argument("--out", type=str, default="output_processed.wav", help="Archivo de salida")
    args = parser.parse_args()

    if args.in_wav:
        sr, x = wavfile.read(args.in_wav)
        x = to_float(x)
        # si estéreo, pasar a mono
        if x.ndim == 2 and x.shape[1] == 2:
            x = x.mean(axis=1)
        signal = x.astype(np.float32)
    else:
        signal, sr = synth_guitar()

    y = distorsion(signal, gain=args.gain, threshold=args.clip)
    y = delay(y, sr, delay_time=args.delay_time, decay=args.decay)
    y = filtro_pasabajo(y, sr, cutoff=args.cutoff)

    wavfile.write(args.out, sr, to_int16(y))
    print(f"Listo. Guardado en: {args.out} (sr={sr} Hz)")

if __name__ == "__main__":
    main()
