from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import random
import os

app = Flask(__name__)

# Proxies and user agents
PROXIES = [
    "http://proxy1:port",
    "http://proxy2:port",
    "http://proxy3:port",
]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

# Route: Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Route: Download Video
@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    # Configure yt-dlp options
    proxy = random.choice(PROXIES)
    user_agent = random.choice(USER_AGENTS)
    ydl_opts = {
        'format': 'best',
        'proxy': proxy,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noprogress': True,
        'quiet': True,
        'user_agent': user_agent,
    }

    try:
        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info).replace(".webm", ".mp3")

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Cleanup downloads on app restart
@app.before_first_request
def cleanup():
    if not os.path.exists('downloads'):
        os.mkdir('downloads')
    for file in os.listdir('downloads'):
        os.remove(os.path.join('downloads', file))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)