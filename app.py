import os, uuid, threading, re
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from deep_translator import GoogleTranslator
from docx import Document

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

translator = GoogleTranslator(source="en", target="hi")

# In-memory job store
jobs = {}

# -------- Garbage cleanup --------
def clean_text(text):
    # Remove OCR garbage like hetJe& Keespe
    text = re.sub(r"[A-Za-z]{2,}[&@#]{1,}[A-Za-z]+", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

# -------- Background job --------
def process_doc(job_id, input_path, output_path):
    doc = Document(input_path)
    out = Document()

    total = len(doc.paragraphs)
    jobs[job_id]["total"] = total

    for i, para in enumerate(doc.paragraphs, start=1):
        text = para.text.strip()
        cleaned = clean_text(text)

        jobs[job_id]["current"] = i
        jobs[job_id]["line"] = cleaned

        print(f"[JOB {job_id}] Translating line {i}/{total}")
        print(cleaned)

        if cleaned:
            try:
                hi = translator.translate(cleaned)
            except:
                hi = cleaned
            out.add_paragraph(hi)
        else:
            out.add_paragraph("")

    out.save(output_path)
    jobs[job_id]["done"] = True
    jobs[job_id]["file"] = output_path
    print(f"[JOB {job_id}] DONE")

# -------- Routes --------
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or not file.filename.endswith(".docx"):
        return jsonify(error="Only DOCX allowed"), 400

    job_id = str(uuid.uuid4())
    input_path = f"{UPLOAD_DIR}/{job_id}.docx"
    output_path = f"{OUTPUT_DIR}/{job_id}_hi.docx"

    file.save(input_path)

    jobs[job_id] = {
        "current": 0,
        "total": 0,
        "line": "",
        "done": False,
        "file": None
    }

    threading.Thread(
        target=process_doc,
        args=(job_id, input_path, output_path),
        daemon=True
    ).start()

    return jsonify(job_id=job_id)

@app.route("/status/<job_id>")
def status(job_id):
    return jsonify(jobs.get(job_id, {}))

@app.route("/download/<job_id>")
def download(job_id):
    job = jobs.get(job_id)
    if job and job["done"]:
        return send_file(job["file"], as_attachment=True)
    return jsonify(error="Not ready"), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
