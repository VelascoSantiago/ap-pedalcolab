from flask import Flask, request, render_template, send_from_directory, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from daw_app import procesar_audio

# --- Configuración ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "audio_raw")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "audio_fx")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# --- Helper para listas de pistas ---
def _get_tracks_lists():
    try:
        raw_tracks = sorted(os.listdir(app.config['UPLOAD_FOLDER']), reverse=True)
    except Exception:
        raw_tracks = []
    try:
        processed_tracks = sorted(os.listdir(app.config['OUTPUT_FOLDER']), reverse=True)
    except Exception:
        processed_tracks = []
    return raw_tracks, processed_tracks

def _get_unique_filename(folder, filename):
    """Genera un nombre único agregando _2, _3... si ya existe."""
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(folder, new_filename)):
        counter += 1
        new_filename = f"{base}_{counter}{ext}"
    return new_filename

# --- Rutas de la Aplicación ---
@app.route('/')
def index():
    raw_tracks, processed_tracks = _get_tracks_lists()
    return render_template('daw_ui.html', raw_tracks=raw_tracks, processed_tracks=processed_tracks)

@app.route('/mobile')
def mobile_view():
    # DEVOLVEMOS LOS LISTADOS para la carga inicial del cliente móvil
    raw_tracks, processed_tracks = _get_tracks_lists()
    return render_template('client_app.html', raw_tracks=raw_tracks, processed_tracks=processed_tracks)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No se encontró el archivo", 400
    file = request.files['file']
    if file.filename == '':
        return "Archivo no seleccionado", 400

    filename = secure_filename(file.filename)
    save_name = _get_unique_filename(app.config['UPLOAD_FOLDER'], filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], save_name))

    return redirect(request.referrer or url_for('mobile_view'))

@app.route('/process/<filename>', methods=['POST'])
def process_track(filename):
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    base_name, ext = os.path.splitext(filename)

    output_name = f"{base_name}_fx.wav"
    output_name = _get_unique_filename(app.config['OUTPUT_FOLDER'], output_name)
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_name)

    effects_config = {
        "dist": float(request.form.get("dist", 0)),
        "bitcrush": float(request.form.get("bitcrush", 0)),
        "clipping": float(request.form.get("clipping", 0)),
        "chorus": float(request.form.get("chorus", 0)),
        "phaser": float(request.form.get("phaser", 0)),
        "reverb": float(request.form.get("reverb", 0)),
        "delay": float(request.form.get("delay", 0)),
        "pitchshift": float(request.form.get("pitchshift", 0)),
        "comp": float(request.form.get("comp", 0)),
    }

    try:
        procesar_audio(input_path, output_path, effects_config)
    except Exception as e:
        print("Error procesando pista:", e)

    return redirect(url_for('index'))

# --- Rutas API y de Descarga ---
@app.route('/download/raw/<filename>')
def download_raw(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/download/fx/<filename>')
def download_fx(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

@app.route('/api/tracks')
def api_tracks():
    """
    Devuelve JSON con ambas listas:
    { "raw_tracks": [...], "processed_tracks": [...] }
    """
    raw_tracks, processed_tracks = _get_tracks_lists()
    return jsonify({
        'raw_tracks': raw_tracks,
        'processed_tracks': processed_tracks
    })

@app.route('/delete/<string:track_type>/<string:filename>', methods=['POST'])
def delete_track(track_type, filename):
    try:
        # Validar el nombre del archivo para evitar ataques (Path Traversal)
        filename = secure_filename(filename)

        if track_type == 'raw':
            folder = app.config['UPLOAD_FOLDER']
        elif track_type == 'fx':
            folder = app.config['OUTPUT_FOLDER']
        else:
            return jsonify({"success": False, "error": "Tipo de pista inválido"}), 400

        file_path = os.path.join(folder, filename)

        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"success": True, "message": f"Archivo {filename} eliminado."})
        else:
            return jsonify({"success": False, "error": "El archivo no existe."}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def print_server_instructions():
    print("="*50)
    print("      Servidor de PedalColab")
    print("="*50)
    print("   - Para la DAW en la PC, abre: http://127.0.0.1:5000")
    print("   - Para el celular, busca tu IP (con 'ipconfig' o 'ifconfig') y abre en su navegador: http://<TU_IP>:5000/mobile")
    print("="*50)

if __name__ == "__main__":
    print_server_instructions()
    app.run(debug=True, host="0.0.0.0", port=5000)

