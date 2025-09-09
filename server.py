
# server.py
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Importamos nuestro motor de efectos desde el nuevo archivo daw-app.py
from daw-app import procesar_audio
from pedalboard import Distortion, Chorus, Reverb, Delay, Compressor

# --- Configuración de carpetas ---
UPLOAD_FOLDER = os.path.join(os.getcwd(), "audio_raw")
OUTPUT_FOLDER = os.path.join(os.getcwd(), "audio_fx")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/', methods=['GET'])
def index():
    # Esta ruta ahora muestra la lista de archivos ya subidos
    tracks = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('ui-app.html', tracks=tracks)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file.filename == '':
        return "Archivo vacío", 400

    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_name = f"{timestamp}_{filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], save_name))

    # Redirige a la página principal para mostrar la lista de archivos actualizada
    return redirect(url_for('index'))

@app.route('/process/<filename>', methods=['GET', 'POST'])
def process_track(filename):
    tracks = os.listdir(app.config['UPLOAD_FOLDER'])
    
    if request.method == 'GET':
        return render_template('ui-app.html', tracks=tracks, selected_track=filename)

    elif request.method == 'POST':
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_name = f"fx_{filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_name)

        # Tomar valores de los sliders
        dist = float(request.form.get("dist", 0))
        chorus = float(request.form.get("chorus", 0))
        reverb = float(request.form.get("reverb", 0))
        delay = float(request.form.get("delay", 0))
        comp = float(request.form.get("comp", 0))

        efectos = []
        if dist > 0:
            efectos.append(Distortion(drive_db=dist * 30))
        if chorus > 0:
            efectos.append(Chorus(rate_hz=1.5, depth=chorus))
        if reverb > 0:
            efectos.append(Reverb(room_size=reverb))
        if delay > 0:
            efectos.append(Delay(delay_seconds=delay, feedback=0.3))
        if comp > 0:
            efectos.append(Compressor(threshold_db=-20, ratio=1 + comp*4))

        # Llama a la función de la daw-app para procesar el audio
        procesar_audio(input_path, output_path, efectos) 

        return render_template('ui-app.html', tracks=tracks, processed_track=output_name)


@app.route('/download/raw/<filename>')
def download_raw(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download/fx/<filename>')
def download_fx(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
