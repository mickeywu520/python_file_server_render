from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_from_directory('hex_files', filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/')
def index():
    return """
    <html>
    <body>
        <h1>Firmware Download Server</h1>
        <a href="/download/test_firmware.hex">Download Test Firmware</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))