import streamlit as st
import numpy as np
from scipy.io import wavfile
from io import BytesIO

def normalize(x, eps=1e-9):
    m = np.max(np.abs(x)) + eps
    return x / m

def to_float(x):
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

# --- Interfaz Streamlit ---
st.title("🎸 Pedalboard Virtual Demo")

uploaded = st.file_uploader("Sube tu archivo WAV", type=["wav"])

gain = st.slider("Ganancia (Distorsión)", 1.0, 20.0, 8.0, 0.5)
clip = st.slider("Umbral de Clipping", 0.05, 1.0, 0.3, 0.05)
delay_time = st.slider("Tiempo de Delay (s)", 0.05, 1.0, 0.25, 0.05)
decay = st.slider("Decaimiento Delay", 0.0, 1.0, 0.4, 0.05)
cutoff = st.slider("Corte LPF (Hz)", 200, 8000, 2000, 100)

if uploaded:
    sr, x = wavfile.read(uploaded)
    x = to_float(x)
    if x.ndim == 2 and x.shape[1] == 2:
        x = x.mean(axis=1)
    signal = x.astype(np.float32)

    y = distorsion(signal, gain=gain, threshold=clip)
    y = delay(y, sr, delay_time=delay_time, decay=decay)
    y = filtro_pasabajo(y, sr, cutoff=cutoff)

    st.audio(to_int16(y).tobytes(), format="audio/wav", sample_rate=sr)

    # Descargar
    buf = BytesIO()
    wavfile.write(buf, sr, to_int16(y))
    st.download_button("Descargar resultado", buf.getvalue(), file_name="processed.wav", mime="audio/wav")

else:
    st.info("Sube un archivo WAV para comenzar.")
