from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer
from PySide6.QtGui import QFont


class AssistantUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Wider, calmer layout
        self.setFixedSize(420, 160)

        screen = self.screen().geometry()
        self.move(
            screen.width() - self.width() - 24,
            80
        )

        # Fade animation
        self.setWindowOpacity(0.0)
        self.fade = QPropertyAnimation(self, b"windowOpacity")
        self.fade.setDuration(220)

        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)

        # Icon
        self.icon = QLabel("🤖")
        self.icon.setAlignment(Qt.AlignLeft)
        self.icon.setFont(QFont("Apple Color Emoji", 26))

        # Main text (READABLE)
        self.text = QLabel("")
        self.text.setWordWrap(True)
        self.text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.text.setFont(QFont("San Francisco", 16, QFont.Medium))
        self.text.setStyleSheet("color: #F5F5F5;")

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(self.icon)
        layout.addWidget(self.text)

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                border-radius: 18px;
                padding: 18px;
            }
        """)

    # ---------- Animations ----------
    def fade_in(self):
        self.show()
        self.fade.stop()
        self.fade.setStartValue(0.0)
        self.fade.setEndValue(1.0)
        self.fade.start()

    def fade_out(self):
        self.fade.stop()
        self.fade.setStartValue(1.0)
        self.fade.setEndValue(0.0)
        self.fade.start()
        self.fade.finished.connect(self.hide)

    # ---------- STATES ----------
    def show_listening(self):
        self.fade_in()
        self.hide_timer.stop()
        self.icon.setText("🎤")
        self.text.setText("Listening…")

    def show_thinking(self):
        self.icon.setText("…")
        self.text.setText("Thinking…")

    def show_speaking(self, response):
        self.icon.setText("🤖")
        self.text.setText(self._shorten(response))


    # ---------- Helpers ----------
    def _shorten(self, text, max_chars=180):
        text = text.strip()
        if len(text) <= max_chars:
            return text
        return text[:max_chars].rsplit(" ", 1)[0] + "…"
    def hide_ui(self):
        self.fade_out()
