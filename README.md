# Voice assistant
Voice assistant is an application created in Python.

<img width="400" height="559" alt="Zrzut ekranu 2025-10-06 163850" src="https://github.com/user-attachments/assets/a10ce590-c5be-4367-a696-a14e800f0f1d" />

## Table of contents
* [Set up](#set-up)
* [General info](#general-info)
* [Technologies](#technologies)

## Set up
To run project on your computer, you have to clone the repository, then open project in code editor and enter in terminal `pip install -r requirements.txt`. Then, you have to enter `python ui.py` and GUI window appears. You have to also create .env file with your API key and assign it to GOOGLE_AI_API_KEY constant.

## General info
This is a Python application which works like a Google Assistant. You can communicate with the assistant using your voice. Gemini 2.5-Flash is applied to generate responses.
SpeechRecognition library is used to recognize commands from user. The recognized text is then sent to Gemini, which prepares a reply. The gTTS library converts Gemini’s response into speech. Finally, the generated MP3 file is saved and converted to WAV format to be played using the winsound module.

## Technologies
The app was created by using suitable libraries in Python such as SpeechRecognition, gTTS, google-generativeai and PySide6 to crerate GUI.
