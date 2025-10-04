from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
import winsound

app = FastAPI(title="Voice Assistant")

# statyczne pliki i szablony
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Strona główna"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/voice/recognize")
async def recognize_voice(file: UploadFile = File(...)):
    """Rozpoznaje mowę z przesłanego pliku audio"""
    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(await file.read())
        temp_audio_path = temp_audio.name

    with sr.AudioFile(temp_audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="pl-PL")
        except sr.UnknownValueError:
            text = "Nie zrozumiałem, spróbuj jeszcze raz."
        except sr.RequestError:
            text = "Błąd połączenia z serwerem rozpoznawania mowy."

    os.remove(temp_audio_path)
    return {"recognized_text": text}


@app.post("/voice/respond")
async def voice_response(request: Request):
    """Tworzy głosową odpowiedź z tekstu"""
    data = await request.json()
    text = data.get("text", "Nie otrzymałem wiadomości.")

    tts = gTTS(text=text, lang="pl")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        audio_path = fp.name

    # odtwórz dźwięk lokalnie (opcjonalnie)
    winsound.PlaySound(audio_path, winsound.SND_FILENAME)

    # zwróć plik mp3 do przeglądarki
    return FileResponse(audio_path, media_type="audio/mpeg", filename="response.mp3")