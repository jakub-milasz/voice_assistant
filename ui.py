from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QApplication
from PySide6.QtCore import Qt, QThread, Signal
import sys
from assistant_core import listen_for_command, assistant_response
import os
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai


_ = load_dotenv(find_dotenv())
genai.configure(api_key=os.environ.get("GOOGLE_AI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
chat_session = model.start_chat(history=[])

prompt_template = """You are a voice assistant. You answer questions people ask
in short way. Do not answer in long way, maximum 3 sentences. This is a question: {command}"""

def generate_response(command, prompt):
    try:
        filled_command = prompt.format(command=command)
        response = chat_session.send_message(filled_command)
        return response.text
    except Exception as e:
        return f"API Error: {e}"


class VoiceThread(QThread):
    """Thread for listening to commands"""
    recognized = Signal(str)

    def run(self):
        command = listen_for_command()
        if command:
            self.recognized.emit(command)
        else:
            self.recognized.emit("Not recognized 😕")


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Assistant 🎙️")
        self.setGeometry(300, 100, 480, 640)

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Header
        self.label = QLabel("Your Voice Assistant 🤖")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        self.layout.addWidget(self.label)

        # Subtitle
        self.title = QLabel('Press "Listen" to start')
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color: #7f8c8d; font-size: 13px; margin-bottom: 8px;")
        self.layout.addWidget(self.title)

        # Chat area
        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        self.chat_box.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9fb;
                border-radius: 12px;
                padding: 10px;
                border: 1px solid #e0e0e0;
                font-size: 14px;
                color: #2d3436;
            }
        """)
        self.layout.addWidget(self.chat_box)

        # 🎙Button layout
        btn_layout = QHBoxLayout()
        self.listen_btn = QPushButton("🎙️ Listen")
        self.listen_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a5aff;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 10px 25px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #3648db;
            }
            QPushButton:pressed {
                background-color: #2b3bcf;
            }
        """)
        self.listen_btn.clicked.connect(self.start_listening)
        btn_layout.addWidget(self.listen_btn, alignment=Qt.AlignCenter)
        self.layout.addLayout(btn_layout)

        # Voice recognition thread
        self.voice_thread = VoiceThread()
        self.voice_thread.recognized.connect(self.process_command)

    # User message style
    def add_user_message(self, text):
        self.chat_box.insertHtml(
            f"""
            <div style="
                background-color: #4a5aff;
                color: white;
                padding: 4px;
                border-radius: 15px;
                max-width: 75%;
                float: right;
                clear: both;
            ">
                {text}
            </div><br><br>
            """
        )
        self.chat_box.verticalScrollBar().setValue(self.chat_box.verticalScrollBar().maximum())

    # Bot message style
    def add_bot_message(self, text):
        self.chat_box.insertHtml(
            f"""
            <div style="
                background-color: #eceff1;
                color: #2d3436;
                padding: 4px;
                border-radius: 15px;
                max-width: 75%;
                float: left;
                clear: both;
            ">
                {text}
            </div><br><br>
            """
        )
        self.chat_box.verticalScrollBar().setValue(self.chat_box.verticalScrollBar().maximum())

    # Start listening to commands
    def start_listening(self):
        if not self.voice_thread.isRunning():
            self.add_bot_message("🎤 Listening...")
            self.voice_thread.start()

    # Procesing the command and reply
    def process_command(self, command):
        self.add_user_message(command)
        reply = generate_response(command, prompt_template)
        self.add_bot_message(reply)
        assistant_response(reply)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())