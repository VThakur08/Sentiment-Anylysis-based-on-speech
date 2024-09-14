from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QTextEdit, QFileDialog, QHBoxLayout, QProgressBar, QFrame, QMessageBox, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient, QGradient, QIcon
import pyttsx3 # type: ignore

class BlurredTextBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setFixedHeight(180)
        self.setContentsMargins(5, 5, 5, 5)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setObjectName("outputLabel")
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #aaa;
                padding: 10px;
                color: #333;
                font-size: 20px;
                font-family: "Arial";
                border-radius: 10px;
                margin: 5px 5;
            }
        """)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(50)
        shadow_effect.setColor(QColor(0, 0, 0, 200))
        shadow_effect.setOffset(3, 3)
        self.text_edit.setGraphicsEffect(shadow_effect)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.text_edit)

class SpeechRecognitionThread(QThread):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def run(self):
        import speech_recognition as sr
        listener = sr.Recognizer()
        text = ""
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                listener.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                audio = listener.listen(source, timeout=3)
                print("Recognizing...")
            text = listener.recognize_google(audio)
            print(f"Recognized text: {text}")
        except sr.UnknownValueError:
            self.error_occurred.emit("Can't understand audio")
        except sr.RequestError as e:
            self.error_occurred.emit(f"Can't request results from Google: {e}")
        except Exception as e:
            self.error_occurred.emit(f"Error: {e}")
        else:
            self.result_ready.emit(text)

class Speech(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.recognized_text = ""
        self.settings()
        self.initUI()
        self.connects()
        self.tts_engine = pyttsx3.init()  # Initialize text-to-speech engine

    def settings(self):
        self.setWindowTitle("Voice Box")
        self.setMinimumSize(1200, 600)
        self.setMaximumSize(1800, 1200)

    def toggle_dark_mode(self):
        if self.dark_mode:
            self.set_light_mode()
        else:
            self.set_dark_mode()
        self.dark_mode = not self.dark_mode
        self.toggle_theme.setText("Dark Mode" if not self.dark_mode else "Light Mode")

    def set_light_mode(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1, stop:0 rgba(63,94, 251, 100), stop:1 rgba(200, 0, 50, 100));
                color: #000000;
                font-size: 18px;  /* Increased font size */
                font-weight: bold;
                border: 1px solid #888;
                padding: 15px 30px;  /* Increased padding */
                border-radius: 10px;
                margin: 5px;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1, stop:0 rgba(238, 174, 202, 255), stop:1 rgba(148, 187, 233, 255));
                cursor: pointer;
            }
            QLabel {
                color: #000000;
                font-family: "Poppins";
            }
            QLabel#sentimentLabel {
                font-weight: bold;
                font-size: 20px;
            }
            QProgressBar {
                text-align: center;
                color: #fff;
                background: #2d2d2d;
                border-radius: 10px;
            }
            QProgressBar::chunk {
                background-color: #02f01e;
                width: 25px;
            }
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(210, 210, 210, 255));
            }
        """)
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient.setColorAt(0.0, QColor("#FFFFFF"))
        gradient.setColorAt(1.0, QColor("#DDDDDD"))
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)
        
    def set_dark_mode(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(60, 60, 60, 255));
                color: #FFFFFF;
                font-size: 18px;  /* Increased font size */
                font-weight: bold;
                border: 1px solid #888;
                padding: 15px 30px;  /* Increased padding */
                border-radius: 10px;
                margin: 5px;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1, stop:0 rgba(50, 50, 50, 255), stop:1 rgba(100, 100, 100, 255));
                cursor: pointer;
            }
            QLabel {
                color: #FFFFFF;
                font-family: "Poppins";
            }
            QLabel#sentimentLabel {
                font-weight: bold;
                font-size: 20px;
            }
            QProgressBar {
                text-align: center;
                color: #fff;
                background: #2d2d2d;
                border-radius: 10px;
            }
            QProgressBar::chunk {
                background-color: #02f01e;
                width: 25px;
            }
            QWidget {
                background-color: #1a1a1a;
            }
        """)
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient.setColorAt(0.0, QColor("#333333"))
        gradient.setColorAt(1.0, QColor("#1a1a1a"))
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)

    def initUI(self):
        title = QLabel("VOCALINK")
        title.setFont(QFont("Poppins", 35, QFont.Bold))  # Changed to modern font and increased size

        self.output_box = BlurredTextBox()

        self.sentiment_text = QLabel("Sentiment: ")
        self.sentiment_text.setObjectName("sentimentLabel")

        sentiment_frame = QFrame()
        sentiment_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 15px;
                padding: 10px;
            }
        """)
        sentiment_layout = QVBoxLayout()
        sentiment_layout.addWidget(self.sentiment_text)
        sentiment_frame.setLayout(sentiment_layout)

        self.submit = QPushButton("Speak Now")
        self.submit.setIcon(QIcon("microphone_icon.png"))
        self.save = QPushButton("Save Note")
        self.save.setIcon(QIcon("save_icon.png"))
        self.clear = QPushButton("Clear Text")
        self.clear.setIcon(QIcon("clear_icon.png"))
        self.read_aloud = QPushButton("Read Aloud")
        self.read_aloud.setIcon(QIcon("read_aloud_icon.png"))
        self.toggle_theme = QPushButton("Dark Mode")
        self.toggle_theme.setIcon(QIcon("moon.png"))

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Infinite progress bar
        self.progress_bar.setVisible(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.submit)
        button_layout.addWidget(self.save)
        button_layout.addWidget(self.clear)
        button_layout.addWidget(self.read_aloud)
        button_layout.addWidget(self.toggle_theme)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.output_box)
        main_layout.addWidget(sentiment_frame, alignment=Qt.AlignCenter)
        main_layout.addSpacing(40)  # Add some vertical spacing
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)
        main_layout.addStretch(1)  # Stretch to bottom

        self.setLayout(main_layout)

        self.set_dark_mode()  # Start in dark mode

    def connects(self):
        self.submit.clicked.connect(self.button_clicked)
        self.save.clicked.connect(self.save_clicked)
        self.clear.clicked.connect(self.clear_text)
        self.read_aloud.clicked.connect(self.read_aloud_clicked)
        self.toggle_theme.clicked.connect(self.toggle_dark_mode)

    def button_clicked(self):
        self.submit.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.thread = SpeechRecognitionThread()
        self.thread.result_ready.connect(self.display_text)
        self.thread.error_occurred.connect(self.show_error)
        self.thread.finished.connect(self.reset_ui)
        self.thread.start()

    @pyqtSlot(str)
    def display_text(self, text):
        self.recognized_text = text
        self.output_box.text_edit.append(text)
        sentiment = self.analyze_sentiment(text)
        self.sentiment_text.setText(f"Sentiment: {sentiment}")
        if sentiment == "Positive":
            self.sentiment_text.setStyleSheet("color: green;")
        elif sentiment == "Negative":
            self.sentiment_text.setStyleSheet("color: red;")
        else:
            self.sentiment_text.setStyleSheet("color: orange;")

    @pyqtSlot(str)
    def show_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

    def reset_ui(self):
        self.submit.setEnabled(True)
        self.progress_bar.setVisible(False)

    def analyze_sentiment(self, text):
        from textblob import TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity > 0.3:
            return "Positive"
        elif polarity < -0.3:
            return "Negative"
        else:
            return "Neutral"

    def save_clicked(self):
        if self.recognized_text:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Text", "", "Text Files (*.txt);;All Files (*)", options=options)
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(self.recognized_text)
        else:
            QMessageBox.warning(self, "Warning", "No text to save")

    def clear_text(self):
        self.recognized_text = ""
        self.output_box.text_edit.clear()
        self.sentiment_text.setText("Sentiment: ")
        self.sentiment_text.setStyleSheet("")  # Reset color

    def read_aloud_clicked(self):
        text = self.output_box.text_edit.toPlainText()
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

if __name__ == "__main__":
    app = QApplication([])
    speech_app = Speech()
    speech_app.show()
    app.exec_()
