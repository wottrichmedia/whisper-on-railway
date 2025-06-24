
from flask import Flask, request, render_template, send_from_directory
import os
from threading import Thread
from faster_whisper import WhisperModel
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "static/results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

model = WhisperModel("base", compute_type="int8")

def transcribe_file(input_path, output_path):
    segments, _ = model.transcribe(input_path)
    text = "\n".join([segment.text for segment in segments])
    with open(output_path, "w") as f:
        f.write(text)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["audio"]
        if file:
            file_id = str(uuid.uuid4())
            input_path = os.path.join(UPLOAD_FOLDER, file_id + ".mp3")
            output_path = os.path.join(RESULT_FOLDER, file_id + ".txt")
            file.save(input_path)

            thread = Thread(target=transcribe_file, args=(input_path, output_path))
            thread.start()

            return f"Upload erfolgreich! Schau in ein paar Minuten hier rein: <a href='/result/{file_id}'>Dein Transkript</a>"

    return render_template("index.html")

@app.route("/result/<file_id>")
def result(file_id):
    output_path = os.path.join(RESULT_FOLDER, file_id + ".txt")
    if os.path.exists(output_path):
        return send_from_directory(RESULT_FOLDER, file_id + ".txt", as_attachment=True)
    else:
        return "Noch nicht fertig. Versuch's in einer Minute nochmal."

if __name__ == "__main__":
    app.run(debug=True)
