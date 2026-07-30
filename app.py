from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import json
import os
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_FILE = 'tiktok_posts.json'
TIKTOK_CLIENT_KEY = os.environ.get('TIKTOK_CLIENT_KEY', '')
TIKTOK_CLIENT_SECRET = os.environ.get('TIKTOK_CLIENT_SECRET', '')
REDIRECT_URI = os.environ.get('REDIRECT_URI', '')

def carregar():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return []

def salvar(dados):
    with open(DB_FILE, 'w') as f:
        json.dump(dados, f)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "api": "Clipador - TikTok Post",
        "versao": "1.0.0",
        "status": "online",
        "endpoints": [
            "/api/tiktok/auth - Autorizar TikTok",
            "/api/tiktok/callback - Callback OAuth",
            "/api/tiktok/post - Postar vídeo",
            "/api/tiktok/posts - Listar posts"
        ]
    })

@app.route('/api/tiktok/auth', methods=['GET'])
def auth():
    url = f"https://www.tiktok.com/auth/authorize/?client_key={TIKTOK_CLIENT_KEY}&scope=video.upload&response_type=code&redirect_uri={REDIRECT_URI}"
    return jsonify({"url": url})

@app.route('/api/tiktok/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    # Trocar code por access token
    return jsonify({"status": "Autorizado!", "code": code})

@app.route('/api/tiktok/post', methods=['POST'])
def postar():
    data = request.json
    posts = carregar()
    
    post = {
        "id": len(posts) + 1,
        "videoUrl": data.get('videoUrl'),
        "titulo": data.get('titulo', ''),
        "descricao": data.get('descricao', ''),
        "hashtags": data.get('hashtags', []),
        "status": "pendente",
        "criado_em": str(datetime.now())
    }
    posts.append(post)
    salvar(posts)
    
    return jsonify({
        "status": "Post agendado!",
        "post": post,
        "mensagem": "Vídeo será postado no TikTok em instantes"
    }), 201

@app.route('/api/tiktok/posts', methods=['GET'])
def listar():
    return jsonify(carregar())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5006))
    app.run(host='0.0.0.0', port=port)