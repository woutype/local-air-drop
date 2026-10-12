import socket
import io
import qrcode
import os

from flask import Flask, render_template, send_file, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_local_ip():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/qr')
def qr_code():

    ip = get_local_ip()
    server_url = f"http://{ip}:5000"

    img = qrcode.make(server_url)

    buffer = io.BytesIO
    img.save(buffer, format='PNG')

    buffer.seek(0)

    return send_file(buffer, mimetype='image.png')

@app.route('/upload', methods=["POST"])
def upload_file():

    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    file.save(filepath)

    return jsonify({'success': True, 'filename': filename}), 200

@app.route('/files', methods=['GET'])
def get_files():

    file_list = []

    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(filepath):
            file_size = os.path.getsize(filepath)
            file_list.append({
                'name': filename,
                'size': file_size
            })

    return jsonify(file_list), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        return jsonify({'error': 'Файл не найден'}), 404

    return jsonify({'success': True, 'message': 'Файл успешно удален'}), 200

if __name__ == '__main__':

    ip = get_local_ip()
    port = 5000

    print(f"\n[AirDrop Local] Сервер успешно запущен!")
    print(f"[AirDrop Local] Локальный адрес на ПК: http://127.0.0.1:{port}")
    print(f"[AirDrop Local] Адрес для смартфона: http://{ip}:{port}\n")

    app.run(host='0.0.0.0', port=port, debug=True)