from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# --- Configuración ---
UPLOAD_FOLDER = os.path.join(os.getcwd(), "proyecto", "audio_raw")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Plantilla HTML mínima ---
UPLOAD_FORM = """
<!doctype html>
<title>Subir pista</title>
<h1>Subir archivo de audio</h1>
<form method=post enctype=multipart/form-data action="/upload">
  <input type=file name=file>
  <input type=submit value="Subir">
</form>
"""

@app.route('/')
def index():
    return render_template_string(UPLOAD_FORM)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No se envió archivo", 400

    file = request.files['file']
    if file.filename == '':
        return "Archivo vacío", 400

    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_name = f"{timestamp}_{filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], save_name))

    return f"Archivo {save_name} subido correctamente"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
