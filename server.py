# server.py
from flask import Flask, request, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Importamos nuestro motor de efectos
from effects import procesar_audio
from pedalboard import Distortion, Chorus, Reverb, Delay, Compressor

# --- Configuración de carpetas ---
UPLOAD_FOLDER = os.path.join(os.getcwd(), "proyecto", "audio_raw")
OUTPUT_FOLDER = os.path.join(os.getcwd(), "proyecto", "audio_fx")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# --- HTML ---
UPLOAD_FORM = """
<!doctype html>
<title>Pedalera Digital</title>
<h1>Subir archivo de audio</h1>
<form method=post enctype=multipart/form-data action="/upload">
  <input type=file name=file required>
  <input type=submit value="Subir">
</form>

{% if filename %}
<hr>
<h2>Aplicar efectos a {{ filename }}</h2>
<form method=post action="/procesar/{{ filename }}">
  <label>Distorsión:</label>
  <input type=range name=dist value=0 min=0 max=1 step=0.1><br>

  <label>Chorus:</label>
  <input type=range name=chorus value=0 min=0 max=1 step=0.1><br>

  <label>Reverb:</label>
  <input type=range name=reverb value=0 min=0 max=1 step=0.1><br>

  <label>Delay:</label>
  <input type=range name=delay value=0 min=0 max=1 step=0.1><br>

  <label>Compresor:</label>
  <input type=range name=comp value=0 min=0 max=1 step=0.1><br>

  <input type=submit value="Procesar">
</form>
{% endif %}
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(UPLOAD_FORM)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file.filename == '':
        return "Archivo vacío", 400

    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_name = f"{timestamp}_{filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], save_name))

    return render_template_string(UPLOAD_FORM, filename=save_name)

@app.route('/procesar/<filename>', methods=['POST'])
def procesar(filename):
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

    procesar_audio(input_path, output_path, efectos)

    return f"""
    <h2>Procesado listo</h2>
    <audio controls>
      <source src="/download/{output_name}" type="audio/wav">
      Tu navegador no soporta audio.
    </audio>
    <br><a href="/download/{output_name}">Descargar</a>
    """

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
