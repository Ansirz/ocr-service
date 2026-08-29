import io
import os
from flask import Flask, jsonify, request
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

@app.route("/ocr", methods=["POST"])
def ocr():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files["file"]
    
    # Ensure stream position is at the beginning and read bytes
    uploaded_file.seek(0)
    file_bytes = uploaded_file.read()
    
    if not file_bytes or len(file_bytes) == 0:
        return jsonify({"error": "Received empty file stream"}), 400

    filename = uploaded_file.filename.lower()
    extracted_text = ""

    try:
        if filename.endswith(".pdf"):
            images = convert_from_bytes(file_bytes, dpi=300)
            for i, image in enumerate(images):
                extracted_text += f"--- Page {i+1} ---\n" + pytesseract.image_to_string(image) + "\n\n"
        else:
            # Force conversion to RGB mode to support transparency/PNGs cleanly
            image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            extracted_text = pytesseract.image_to_string(image)

        return jsonify({"status": "success", "text": extracted_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
