from flask import Flask, send_from_directory, jsonify, request
import os

app = Flask(__name__)

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_from_directory('hex_files', filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/list-files')
def list_files():
    try:
        files = os.listdir('hex_files')
        hex_files = [f for f in files if f.endswith('.hex')]
        return jsonify(hex_files=hex_files)
    except FileNotFoundError:
        return "hex_files directory not found", 404

@app.route('/')
def index():
    return """
    <html>
    <body>
        <h1>Firmware Download Server</h1>
        <a href="/list-files">List Available Firmware Files</a>
    </body>
    </html>
    """

@app.route('/hello')
def hello():
    return jsonify(message="hello world")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))