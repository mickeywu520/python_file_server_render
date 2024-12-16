from flask import Flask, send_from_directory, jsonify, request, render_template_string
import os
import json

app = Flask(__name__)

# 設定檔案上傳資料夾
UPLOAD_FOLDER = 'hex_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename,
                                   as_attachment=True)
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
            filepath = os.path.join(app.config['UPLOAD_FOLDER'],
                                    file.filename)
            file.save(filepath)
            return f"File {file.filename} uploaded successfully!"
        else:
            return "Invalid file type. Only .hex files are allowed.", 400

    # 使用 render_template_string 將 HTML 內嵌在 Python 檔案中
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
        <ul id="file-list">
        </ul>

        <button onclick="clearLatestVersion()">Clear Latest Version</button>

        <script>
            fetch('/list-files')
                .then(response => response.json())
                .then(data => {
                    const fileList = document.getElementById('file-list');
                    data.hex_files.forEach(file => {
                        const listItem = document.createElement('li');
                        listItem.innerHTML = `${file} <button onclick="setLatestVersion('${file}')">Set as Latest</button>`;
                        fileList.appendChild(listItem);
                    });
                })
                .catch(error => console.error('Error fetching files:', error));

            function setLatestVersion(filename) {
                if (confirm(`Are you sure you want to set ${filename} as the latest version?`)) {
                    fetch('/set-latest-version', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ filename: filename })
                    })
                    .then(response => response.text())
                    .then(data => alert(data))
                    .catch(error => console.error('Error setting latest version:', error));
                }
            }

            function clearLatestVersion() {
                fetch('/clear-version', { method: 'POST' })
                    .then(response => response.text())
                    .then(data => alert(data))
                    .catch(error => console.error('Error clearing latest version:', error));
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/hello')
def hello():
    return jsonify(message="hello world")

@app.route('/version')
def version():
    try:
        with open("version.json", "r") as f:
            version_data = json.load(f)
        return jsonify(latest_version=version_data.get("latest_version"))
    except FileNotFoundError:
        return jsonify(latest_version="Version file not found"), 404

@app.route('/set-latest-version', methods=['POST'])
def set_latest_version():
    try:
        data = request.get_json()
        filename = data.get('filename')
        if not filename:
            return "Filename is required", 400

        #latest_version = filename[:-4]  # 移除 ".hex" 副檔名
        latest_version = filename
        version_data = {"latest_version": latest_version}
        with open("version.json", "w") as f:
            json.dump(version_data, f)

        return f"Latest version set to {latest_version}"
    except Exception as e:
        return f"Error setting latest version: {str(e)}", 500

@app.route('/clear-version', methods=['POST'])  # 新增的 API endpoint
def clear_version():
    try:
        version_data = {"latest_version": None}  # 設定 latest_version 為 null
        with open("version.json", "w") as f:
            json.dump(version_data, f)
        return "Latest version cleared."
    except Exception as e:
        return f"Error clearing latest version: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))