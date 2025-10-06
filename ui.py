from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QApplication, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
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
in short way. Do not answer in long way, maximum 2 sentences. This is a question: {command}"""

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

class AudioThread(QThread):
    """Thread for voice response"""
    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        assistant_response(self.text)


class Bubble(QWidget):
    """Class for bubble"""
    def __init__(self, text, is_user, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        h = QHBoxLayout(self)
        h.setContentsMargins(4, 2, 4, 2)
        h.setSpacing(6)

        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bubble.setMaximumWidth(360)
        font = bubble.font()
        font.setPointSize(11)
        bubble.setFont(font)

        if is_user:
            # user bubble
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #0084ff;
                    color: white;
                    padding: 10px 14px;
                    border-radius: 18px;
                    border-top-right-radius: 6px;
                }
            """)
            h.addStretch()
            h.addWidget(bubble, 0, Qt.AlignRight)
        else:
            # bot bubble
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #e4e6eb;
                    color: #050505;
                    padding: 10px 14px;
                    border-radius: 18px;
                    border-top-left-radius: 6px;
                }
            """)
            h.addWidget(bubble, 0, Qt.AlignLeft)
            h.addStretch()


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Assistant 🎙️")
        self.setGeometry(200, 50, 480, 640)

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(8)

        # Header
        self.header = QLabel("Your Voice Assistant 🤖")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("""
            QLabel { font-size: 20px; font-weight: bold; color: #2c3e50; }
        """)
        self.layout.addWidget(self.header)

        # Subtitle
        self.suptitle = QLabel('Press "Listen" to start')
        self.suptitle.setAlignment(Qt.AlignCenter)
        self.suptitle.setStyleSheet("color: #7f8c8d; font-size: 13px; margin-bottom: 6px;")
        self.layout.addWidget(self.suptitle)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { background-color: #f0f2f5; border: none; }")

        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setSpacing(8)
        self.messages_layout.setContentsMargins(6, 6, 6, 6)

        self.scroll.setWidget(self.messages_widget)
        self.layout.addWidget(self.scroll)

        # Button
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
            QPushButton:hover { background-color: #3648db; }
            QPushButton:pressed { background-color: #2b3bcf; }
        """)
        self.listen_btn.clicked.connect(self.start_listening)
        btn_layout.addStretch()
        btn_layout.addWidget(self.listen_btn)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)

        # Voice thread
        self.voice_thread = VoiceThread()
        self.voice_thread.recognized.connect(self.process_command)


    def add_user_message(self, text):
        bubble = Bubble(text.capitalize(), is_user=True)
        self.messages_layout.addWidget(bubble)

    def add_bot_message(self, text):
        bubble = Bubble(text, is_user=False)
        self.messages_layout.addWidget(bubble)

    def start_listening(self):
        if not self.voice_thread.isRunning():
            self.add_bot_message("🎤 Listening...")
            self.voice_thread.start()

    def process_command(self, command):
        self.add_user_message(command)
        reply = generate_response(command, prompt_template)
        self.add_bot_message(reply)
        # voice response
        audio_thread = AudioThread(reply)
        audio_thread.start()
        # Keep reference
        self.audio_thread = audio_thread


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
