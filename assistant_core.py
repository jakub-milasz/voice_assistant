import speech_recognition as sr
from gtts import gTTS
import winsound
from pydub import AudioSegment


def listen_for_command():
    """Listening to commands"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None


def assistant_response(text):
    """Change text to speech"""
    tts = gTTS(text=text, lang="en")
    tts.save("response.mp3")
    sound = AudioSegment.from_mp3("response.mp3")
    sound.export("response.wav", format="wav")
    winsound.PlaySound("response.wav", winsound.SND_FILENAME)
