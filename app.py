from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import yt_dlp as youtube_dl
import os
from werkzeug.utils import secure_filename

# Ensure downloads folder exists
os.makedirs("downloads", exist_ok=True)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template("index.html")  # Make sure templates/index.html exists

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({"success": False, "message": "No URL provided"}), 400

    try:
        with youtube_dl.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)

            desired_resolutions = [360, 480, 720, 1080]
            available_resolutions = sorted(
                list({f.get('height') for f in info['formats'] if f.get('height') in desired_resolutions}),
                reverse=True
            )

            return jsonify({
                "success": True,
                "title": info.get("title", "Video"),
                "thumbnail": info.get("thumbnail"),
                "resolutions": available_resolutions
            })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    video_url = data.get('video_url')
    resolution = data.get('resolution', 'best')

    if not video_url:
        return jsonify({"success": False, "message": "No URL provided"}), 400

    try:
        with youtube_dl.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = secure_filename(info.get("title", "video"))
            filename = f"{title}_{resolution}p.mp4"

        format_code = f"bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]" if resolution != "best" else "best"

        ydl_opts = {
            'format': format_code,
            'outtmpl': f'downloads/{filename}',
            'noplaylist': True
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # Use dynamic base URL
        base_url = request.host_url.rstrip('/')
        return jsonify({
            "success": True,
            "download_url": f"{base_url}/downloads/{filename}"
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/downloads/<path:filename>')
def serve_file(filename):
    return send_from_directory('downloads', filename, as_attachment=True)
