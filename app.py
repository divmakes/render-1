from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/video_info', methods=['POST'])
def video_info():
    video_url = request.json.get('video_url')
    if not video_url:
        return jsonify({"success": False, "message": "No URL provided"}), 400

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            resolutions = sorted({f.get('height') for f in info['formats'] if f.get('height')}, reverse=True)
            return jsonify({
                "success": True,
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "resolutions": resolutions
            })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('video_url')
    resolution = str(data.get('resolution', 'best'))

    if not url:
        return jsonify({"success": False, "message": "No URL provided"}), 400

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = secure_filename(info.get("title", "video"))
            filename = f"{title}_{resolution}p.mp4"

        format_code = f"bestvideo[height<={resolution}]+bestaudio/best" if resolution != 'best' else 'best'

        ydl_opts = {
            'format': format_code,
            'outtmpl': f'{DOWNLOAD_DIR}/{filename}',
            'noplaylist': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        host_url = request.host_url.rstrip('/')
        return jsonify({
            "success": True,
            "download_url": f"{host_url}/downloads/{filename}"
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/downloads/<path:filename>')
def serve_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)
