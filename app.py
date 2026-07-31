from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import tempfile
import subprocess
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_FILE = 'edicoes_audio.json'
UPLOAD_FOLDER = tempfile.mkdtemp()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "api": "Clipador - Edição de Áudio",
        "versao": "2.1.1",
        "status": "online"
    })

@app.route('/api/audio/cortar', methods=['POST'])
def cortar():
    if 'audio' not in request.files:
        return jsonify({"erro": "Áudio não enviado"}), 400
    file = request.files['audio']
    inicio = request.form.get('inicio', '0')
    duracao = request.form.get('duracao', '30')
    formato = request.form.get('formato', 'mp3')
    temp_input = os.path.join(UPLOAD_FOLDER, f'input_{datetime.now().timestamp()}.mp3')
    temp_output = os.path.join(UPLOAD_FOLDER, f'cortado.{formato}')
    file.save(temp_input)
    subprocess.run(['ffmpeg', '-i', temp_input, '-ss', inicio, '-t', duracao, '-c', 'copy', temp_output, '-y'], capture_output=True, timeout=120)
    return send_file(temp_output, as_attachment=True, download_name=f'cortado.{formato}')

@app.route('/api/audio/velocidade', methods=['POST'])
def velocidade():
    if 'audio' not in request.files:
        return jsonify({"erro": "Áudio não enviado"}), 400
    file = request.files['audio']
    fator = request.form.get('fator', '1.5')
    temp_input = os.path.join(UPLOAD_FOLDER, f'input_{datetime.now().timestamp()}.mp3')
    temp_output = os.path.join(UPLOAD_FOLDER, f'speed_{fator}x.mp3')
    file.save(temp_input)
    subprocess.run(['ffmpeg', '-i', temp_input, '-filter:a', f'atempo={fator}', '-vn', temp_output, '-y'], capture_output=True, timeout=120)
    return send_file(temp_output, as_attachment=True, download_name=f'speed_{fator}x.mp3')

@app.route('/api/audio/converter', methods=['POST'])
def converter():
    if 'audio' not in request.files:
        return jsonify({"erro": "Áudio não enviado"}), 400
    file = request.files['audio']
    formato = request.form.get('formato', 'mp3')
    qualidade = request.form.get('qualidade', '320k')
    codecs = {'mp3': 'libmp3lame', 'aac': 'aac', 'ogg': 'libvorbis', 'flac': 'flac', 'wav': 'pcm_s16le'}
    codec = codecs.get(formato, 'libmp3lame')
    temp_input = os.path.join(UPLOAD_FOLDER, f'input_{datetime.now().timestamp()}')
    temp_output = os.path.join(UPLOAD_FOLDER, f'convertido.{formato}')
    file.save(temp_input)
    subprocess.run(['ffmpeg', '-i', temp_input, '-c:a', codec, '-b:a', qualidade, temp_output, '-y'], capture_output=True, timeout=120)
    return send_file(temp_output, as_attachment=True, download_name=f'convertido.{formato}')

@app.route('/api/audio/extrair', methods=['POST'])
def extrair():
    if 'video' not in request.files:
        return jsonify({"erro": "Vídeo não enviado"}), 400
    file = request.files['video']
    formato = request.form.get('formato', 'mp3')
    temp_input = os.path.join(UPLOAD_FOLDER, f'input_{datetime.now().timestamp()}.mp4')
    temp_output = os.path.join(UPLOAD_FOLDER, f'audio.{formato}')
    file.save(temp_input)
    subprocess.run(['ffmpeg', '-i', temp_input, '-vn', '-ar', '44100', '-ac', '2', '-b:a', '320k', temp_output, '-y'], capture_output=True, timeout=120)
    return send_file(temp_output, as_attachment=True, download_name=f'audio.{formato}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5016))
    app.run(host='0.0.0.0', port=port, debug=False)
