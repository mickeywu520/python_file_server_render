from flask import Flask, send_from_directory, jsonify, request, render_template_string
import os

app = Flask(__name__)

# 設定檔案上傳資料夾
UPLOAD_FOLDER = 'hex_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/list-files')
def list_files():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        hex_files = [f for f in files if f.endswith('.hex')]
        return jsonify(hex_files=hex_files)
    except FileNotFoundError:
        return "hex_files directory not found", 404

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 檢查是否有檔案上傳
        if 'file' not in request.files:
            return "No file part", 400

        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        if file and file.filename.endswith('.hex'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            return f"File {file.filename} uploaded successfully!"
        else:
            return "Invalid file type. Only .hex files are allowed.", 400

    return render_template_string('''
    <html>
    <body>
        <h1>Firmware Download Server</h1>
        <h2>Upload Firmware</h2>
        <form action="/" method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit">Upload</button>
        </form>
        <h2>Available Firmware</h2>
        <a href="/list-files">List Available Firmware Files</a>
    </body>
    </html>
    ''')

@app.route('/hello')
def hello():
    return jsonify(message="hello world")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))