from flask import Flask, request, send_from_directory
import os
import uuid
import threading
import whisper

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Whisper-Modell einmalig laden
print("[INIT] Lade Whisper-Modell...")
model = whisper.load_model("base")
print("[INIT] Whisper-Modell geladen.")

def transcribe(file_id, file_path):
    try:
        print(f"[TRANSCRIBE] Starte Transkription: {file_path}")
        result = model.transcribe(file_path)
        output_path = os.path.join(RESULT_FOLDER, file_id + ".txt")

        with open(output_path, "w") as f:
            f.write(result["text"])

        print(f"[TRANSCRIBE] Fertig. Transkript gespeichert unter: {output_path}")
    except Exception as e:
        print(f"[ERROR] Fehler bei Transkription: {e}")

@app.route("/", methods=["GET"])
def index():
    return """
    <h2>MP3/WAV Upload</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file"><br><br>
        <input type="submit" value="Hochladen">
    </form>
    """

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    file_id = str(uuid.uuid4())
    filename = file_id + ".wav"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    print(f"[UPLOAD] Datei empfangen und gespeichert: {file_path}")

    threading.Thread(target=transcribe, args=(file_id, file_path)).start()

    return f"Upload erfolgreich! Schau in ein paar Minuten hier rein: <a href='/result/{file_id}'>Dein Transkript</a>"

@app.route("/result/<file_id>")
def result(file_id):
    output_path = os.path.join(RESULT_FOLDER, file_id + ".txt")
    if os.path.exists(output_path):
        return send_from_directory(RESULT_FOLDER, file_id + ".txt", as_attachment=False)
    else:
        return "Noch nicht fertig. Versuch's in einer Minute nochmal."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
