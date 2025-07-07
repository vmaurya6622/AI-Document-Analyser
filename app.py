from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
import subprocess
import os
import csv

app = Flask(__name__, static_folder="static", template_folder="templates")

# 📁 Define upload folder path
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # ✅ Ensure the folder exists

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "pdfs" not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            return jsonify({"error": f"Failed to clear uploads folder: {str(e)}"}), 500
        
    uploaded_files = request.files.getlist("pdfs")

    # 🧾 Save uploaded files
    for file in uploaded_files:
        if file and file.filename.endswith(".pdf"):
            # Extract only the filename part, strip folder prefixes
            filename = os.path.basename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # Save the file
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)

        else:
            return jsonify({"error": f"Invalid file type: {file.filename}"}), 400

    # 🚀 Run the classification script (main.py)
    try:
        subprocess.run(["python", "main.py", UPLOAD_FOLDER], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed to process PDFs: {e}"}), 500

    # 📄 Read the generated CSV results
    csv_path = os.path.join(UPLOAD_FOLDER, "document_summary.csv")
    results = []

    if os.path.exists(csv_path):
        with open(csv_path, newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)  # Skip header
            for row in reader:
                results.append(row)
    else:
        return jsonify({"error": "CSV output not found"}), 500

    return jsonify(results)

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(debug=True)
