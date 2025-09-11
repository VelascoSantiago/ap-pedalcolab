    # server.py
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Asumimos que daw_app.py está en el mismo directorio
from daw_app import procesar_audio
from pedalboard import Distortion, Chorus, Reverb, Delay, Compressor

# --- Configuración de carpetas ---
# Obtenemos la ruta absoluta del directorio del script para evitar problemas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "audio_raw")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "audio_fx")
TEMPLATE_FOLDER = os.path.join(BASE_DIR, "templates")

# Creamos las carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def get_tracks():
    """Función auxiliar para obtener las listas de pistas de forma ordenada."""
    try:
        raw_tracks = sorted(os.listdir(app.config['UPLOAD_FOLDER']), reverse=True)
    except FileNotFoundError:
        raw_tracks = []
    try:
        processed_tracks = sorted(os.listdir(app.config['OUTPUT_FOLDER']), reverse=True)
    except FileNotFoundError:
        processed_tracks = []
    return raw_tracks, processed_tracks

@app.route('/')
def index():
    """
    Ruta principal para la DAW en la computadora.
    Sirve el archivo 'daw_ui.html'.
    """
    raw_tracks, processed_tracks = get_tracks()
    return render_template('daw_ui.html', raw_tracks=raw_tracks, processed_tracks=processed_tracks)

@app.route('/mobile')
def mobile_client():
    """
    Ruta específica para el cliente móvil (celular).
    Sirve el archivo 'client_app.html'.
    """
    # La carga inicial de pistas sigue funcionando igual
    raw_tracks, processed_tracks = get_tracks()
    return render_template('client_app.html', raw_tracks=raw_tracks, processed_tracks=processed_tracks)

# --- NUEVA RUTA API ---
@app.route('/api/tracks')
def api_tracks():
    """
    Esta ruta no devuelve HTML. Devuelve los datos de las pistas en formato JSON
    para que el JavaScript del cliente pueda consumirlos.
    """
    raw_tracks, processed_tracks = get_tracks()
    return jsonify({
        'raw_tracks': raw_tracks,
        'processed_tracks': processed_tracks
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Maneja la subida de archivos desde cualquier cliente."""
    if 'file' not in request.files:
        return "No se encontró el archivo en la petición", 400
    file = request.files['file']
    if file.filename == '':
        return "El archivo no tiene nombre", 400

    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_name = f"{timestamp}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], save_name))
        
        return redirect(request.referrer or url_for('mobile_client'))

@app.route('/process/<filename>', methods=['POST'])
def process_track(filename):
    """Procesa una pista de audio con los efectos seleccionados."""
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_name = f"fx_{os.path.splitext(filename)[0]}.wav"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_name)

    dist = float(request.form.get("dist", 0))
    chorus = float(request.form.get("chorus", 0))
    reverb = float(request.form.get("reverb", 0))
    delay = float(request.form.get("delay", 0))
    comp = float(request.form.get("comp", 0))

    efectos = []
    if dist > 0: efectos.append(Distortion(drive_db=dist * 40))
    if chorus > 0: efectos.append(Chorus(rate_hz=1.0, depth=chorus, mix=0.5))
    if reverb > 0: efectos.append(Reverb(room_size=reverb, damping=0.5, wet_level=0.3, dry_level=0.7))
    if delay > 0: efectos.append(Delay(delay_seconds=delay * 0.8, feedback=0.4, mix=0.5))
    if comp > 0: efectos.append(Compressor(threshold_db=-25, ratio=1 + comp * 9))

    procesar_audio(input_path, output_path, efectos) 

    return redirect(url_for('index'))

@app.route('/download/raw/<filename>')
def download_raw(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download/fx/<filename>')
def download_fx(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == "__main__":
    print("="*50)
    print("      Servidor de Pedalera Digital Colaborativa")
    print("="*50)
    print("   - Para la DAW en la PC, abre: http://127.0.0.1:5000")
    print("   - Para el celular, busca tu IP (con 'ipconfig' o 'ifconfig')")
    print("     y abre en su navegador: http://<TU_IP>:5000/mobile")
    print("="*50)
    app.run(debug=True, host="0.0.0.0", port=5000)