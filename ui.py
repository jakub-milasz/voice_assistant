from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QApplication
from PySide6.QtCore import Qt, QThread, Signal
import sys
from assistant_core import listen_for_command, assistant_response, bag_processing, predict_new_command
from PIL import ImageGrab
import random


class VoiceThread(QThread):
    """Wątek do słuchania głosu (żeby nie blokować GUI)"""
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
        self.setGeometry(300, 100, 450, 600)

        self.cv, self.classifier = bag_processing()
        self.tasks = []
        self.thanks_responses = ["You're welcome!", "Always at your service!", "No problem!"]

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Your voice assistant 🤖")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(self.label)

        self.title = QLabel('Press "Listen" to start')
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        self.layout.addWidget(self.chat_box)

        btn_layout = QHBoxLayout()
        self.listen_btn = QPushButton("🎙️ Listening...")
        self.listen_btn.clicked.connect(self.start_listening)
        btn_layout.addWidget(self.listen_btn)

        self.layout.addLayout(btn_layout)

        self.voice_thread = VoiceThread()
        self.voice_thread.recognized.connect(self.process_command)


    def add_user_message(self, text):
        self.chat_box.append(f"<p style='text-align:right; color:white; background:#5563DE; padding:6px; border-radius:10px;'>{text}</p>")

    def add_bot_message(self, text):
        self.chat_box.append(f"<p style='text-align:left; background:#f1f1f1; padding:6px; border-radius:10px;'>{text}</p>")

    def start_listening(self):
        self.add_bot_message("🎤 Listening...")
        self.voice_thread.start()

    def process_command(self, command):
        self.add_user_message(command)
        num = predict_new_command(command, self.cv, self.classifier)
        # odpowiedzi na komendy
        if num == 1:
            reply = "Hello, how can I help you?"
            self.add_bot_message(reply)
        elif num == 2:
            screenshot = ImageGrab.grab()
            screenshot.save("screenshot.png")
            screenshot.close()
            reply = "Screenshot saved successfully."
            self.add_bot_message(reply)
        elif num == 3:
            reply = "What task would you like to add?"
            self.add_bot_message(reply)
            assistant_response(reply)
            task = listen_for_command()
            if task not in self.tasks:
                self.tasks.append(task)
        elif num == 4:
            reply = f"Your tasks: {', '.join(self.tasks) if self.tasks else 'no tasks yet.'}"
            self.add_bot_message(reply)
        elif num == 5:
            reply = random.choice(self.thanks_responses)
            self.add_bot_message(reply)
        elif num == 6:
            reply = "Goodbye!"
            self.add_bot_message(reply)
        elif num == 7:
            reply = "Which task would you like to remove?"
            self.add_bot_message(reply)
            assistant_response(reply)
            task = listen_for_command()
            if task in self.tasks:
                self.tasks.remove(task)
                reply = f"Task {task} removed successfully."
                self.add_bot_message(reply)
                assistant_response(reply)
            else:
                reply = "There is no such task."
                self.add_bot_message(reply)
                assistant_response(reply)
        else:
            reply = f"Unknown command: {command}"
            self.add_bot_message(reply)
        assistant_response(reply)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
