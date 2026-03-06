from flask import Flask, request, jsonify, render_template_string, send_file
from yt_dlp import YoutubeDL
import logging
import os
import tempfile

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Download directory (use temp dir so we can send file and clean up; works when deployed)
DOWNLOAD_DIR = os.environ.get('DOWNLOAD_DIR', tempfile.gettempdir())

# Optional: set COOKIES_TXT in Render (or .env) with your cookies.txt content for Instagram/private content
# So the app can download without you pasting cookies every time.
DEFAULT_COOKIES = os.environ.get('COOKIES_TXT', '').strip()

def get_ydl_opts(cookiefile_path=None):
    opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }
    if cookiefile_path and os.path.isfile(cookiefile_path):
        opts['cookiefile'] = cookiefile_path
    return opts

DARK_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>anyvideoDownloader</title>
    <style>
        body {
            background: #181a1b;
            color: #f1f1f1;
            font-family: 'Segoe UI', Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            background: #23272a;
            padding: 2rem 2.5rem;
            border-radius: 1rem;
            box-shadow: 0 4px 32px #000a;
            max-width: 400px;
            width: 100%;
        }
        h1 {
            margin-bottom: 1.5rem;
            font-size: 2rem;
            text-align: center;
            color: #00bfae;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 0.75rem;
            border-radius: 0.5rem;
            border: none;
            margin-bottom: 1rem;
            font-size: 1rem;
            background: #181a1b;
            color: #f1f1f1;
            box-sizing: border-box;
        }
        textarea { min-height: 80px; resize: vertical; font-family: monospace; font-size: 0.85rem; }
        label.optional { font-size: 0.9rem; color: #888; display: block; margin-bottom: 0.35rem; }
        button {
            width: 100%;
            padding: 0.75rem;
            border-radius: 0.5rem;
            border: none;
            background: #00bfae;
            color: #181a1b;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: #009e8e;
        }
        .result {
            margin-top: 1.5rem;
            padding: 1rem;
            border-radius: 0.5rem;
            background: #22262a;
            color: #f1f1f1;
            word-break: break-all;
            text-align: center;
        }
        .spinner {
            margin: 1rem auto 0 auto;
            border: 4px solid #23272a;
            border-top: 4px solid #00bfae;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        a.download-link {
            color: #00bfae;
            text-decoration: underline;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>anyvideoDownloader</h1>
        <form id="downloadForm">
            <input type="text" id="url" name="url" placeholder="Paste video URL here..." required />
            <label class="optional" for="cookies">Cookies (optional – for Instagram / private content)</label>
            <textarea id="cookies" name="cookies" placeholder="Paste cookies.txt content here, or set COOKIES_TXT on the server to use by default."></textarea>
            <button type="submit">Download</button>
        </form>
        <div id="spinner" class="spinner" style="display:none;"></div>
        <div id="result" class="result" style="display:none;"></div>
    </div>
    <script>
        const form = document.getElementById('downloadForm');
        const resultDiv = document.getElementById('result');
        const spinner = document.getElementById('spinner');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            resultDiv.style.display = 'none';
            spinner.style.display = 'block';
            const url = document.getElementById('url').value;
            const cookies = document.getElementById('cookies').value.trim();
            const body = { url };
            if (cookies) body.cookies = cookies;
            try {
                const res = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                const contentType = res.headers.get('Content-Type') || '';
                if (contentType.includes('application/json')) {
                    const data = await res.json();
                    spinner.style.display = 'none';
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = data.error ? `❌ Error: ${data.error}` : `✅ ${data.filename || 'Done'}`;
                    return;
                }
                if (res.ok && res.headers.get('Content-Disposition')) {
                    const blob = await res.blob();
                    const disp = res.headers.get('Content-Disposition');
                    const match = disp && disp.match(/filename="?([^";]+)"?/);
                    const filename = match ? match[1].trim() : 'video.mp4';
                    const link = document.createElement('a');
                    link.href = window.URL.createObjectURL(blob);
                    link.download = filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(link.href);
                    spinner.style.display = 'none';
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `✅ Download started: <span class='download-link'>${filename}</span>`;
                    return;
                }
                spinner.style.display = 'none';
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '❌ Error: Invalid response.';
            } catch (err) {
                spinner.style.display = 'none';
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = `❌ Error: ${err.message}`;
            }
        });
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(DARK_HTML)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json(force=True, silent=True)
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing "url" in request body'}), 400
    url = data['url']
    if not isinstance(url, str) or not url.strip():
        return jsonify({'error': 'Invalid URL'}), 400
    url = url.strip()
    # Cookies: from request body, or fall back to server default (e.g. COOKIES_TXT on Render)
    cookies_raw = (data.get('cookies') or '').strip() or DEFAULT_COOKIES
    cookie_path = None
    if cookies_raw:
        try:
            fd, cookie_path = tempfile.mkstemp(suffix='.txt', prefix='cookies')
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(cookies_raw)
            logging.info("Using cookies for this request")
        except Exception as e:
            logging.warning(f"Could not write cookie file: {e}")
            cookie_path = None
    logging.info(f"Received download request for URL: {url}")
    try:
        opts = get_ydl_opts(cookie_path)
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        if not os.path.isfile(filename):
            return jsonify({'error': 'Download failed: no file produced'}), 500
        logging.info(f"Download completed: {filename}")
        try:
            return send_file(
                filename,
                as_attachment=True,
                download_name=os.path.basename(filename),
                mimetype='video/mp4',
            )
        finally:
            try:
                os.remove(filename)
            except OSError:
                pass
    except Exception as e:
        logging.error(f"Download failed: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if cookie_path and os.path.isfile(cookie_path):
            try:
                os.remove(cookie_path)
            except OSError:
                pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 