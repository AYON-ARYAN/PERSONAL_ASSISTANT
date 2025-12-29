import sys
import threading
from PySide6.QtWidgets import QApplication

from ui.assistant_ui import AssistantUI
from core.assistant_worker import AssistantWorker


def main():
    app = QApplication(sys.argv)

    ui = AssistantUI()
    # ❌ Do NOT call ui.show() here
    # The UI controls its own visibility (fade-in / fade-out)

    worker = AssistantWorker()

    # ✅ Connect worker signals → UI state methods
    worker.listening.connect(ui.show_listening)
    worker.thinking.connect(ui.show_thinking)
    worker.speaking.connect(ui.show_speaking)
    worker.session_ended.connect(ui.hide_ui)

    # ✅ Run assistant logic in background thread
    t = threading.Thread(target=worker.run, daemon=True)
    t.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
