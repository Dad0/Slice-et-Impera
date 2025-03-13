"""
Questo script può essere eseguito per fare una domanda al sistema di Graph RAG con agenti tramite GUI, oppure
tramite un classico input di python (interfaccia = False). In entrambi i casi, il sistema risponderà alla domanda.
I log vengono monitorati in tempo reale e visualizzati nella GUI.

Non viene monitorato il log Query per evitare sovraccarichi di informazioni, ma è possibile trovare il log con tutte
le query effettuate in "Slice et Impera\logs\Query.log"

La GUI è davvero semplice e piena di potenziali migliorie attuabili, ed è solo a scopo dimostrativo.
Al momento, dopo ogni domanda è meglio chiuderla e riavviarla in modo che vengano resettati i log
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QGridLayout, QLabel, QLineEdit
from PyQt6.QtCore import QTimer, Qt
import agents.run_agent_system as ras

# Percorso della cartella dei log relativo alla posizione dello script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FOLDER = os.path.join(BASE_DIR, "logs")

# Configurazione delle finestre e dei rispettivi file di log per 9 agenti
WINDOWS = [
    "Ingrediente", "Tecnica", "Ristorante",
    "Distanza", "Licenza", "Ordine",
    "Chef", "Abilitazione", "Legale"
]
# Percorsi dei file di log per gli agenti
LOG_FILES = {win: os.path.join(LOG_FOLDER, f"{win.capitalize()}.log") for win in WINDOWS}
# Percorsi dei file di log aggiuntivi
SET_EVALUATOR_LOG = os.path.join(LOG_FOLDER, "Set evaluator.log")
RESULTS_LOG = os.path.join(LOG_FOLDER, "Results.log")

def clear_logs():
    """Cancella il contenuto di tutti i file di log all'avvio (inclusi Results e SetEvaluator)."""
    files_to_clear = list(LOG_FILES.values()) + [SET_EVALUATOR_LOG, RESULTS_LOG]
    for log_file in files_to_clear:
        if os.path.exists(log_file):
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("")
    print("Log files cleared.")

class LogViewer(QWidget):
    def __init__(self, title, log_file):
        super().__init__()
        self.log_file = log_file
        # Variabili per l'effetto "typewriter"
        self.current_text = ""
        self.target_text = ""
        self.init_ui(title)
        self.start_log_monitoring()
        self.start_typing_effect()

    def init_ui(self, title):
        layout = QVBoxLayout()
        self.label = QLabel(title)
        layout.addWidget(self.label)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def start_log_monitoring(self):
        # Timer per controllare ogni secondo eventuali modifiche nel file di log
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_log)
        self.timer.start(1000)

    def update_log(self):
        if os.path.exists(self.log_file) and os.path.getsize(self.log_file) > 0:
            with open(self.log_file, "r", encoding="utf-8") as f:
                new_content = f.read()
            if new_content != self.target_text:
                self.target_text = new_content

    def start_typing_effect(self):
        # Timer per l'effetto digitazione: aggiorna ogni 50ms
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self.type_next_character)
        self.typing_timer.start(50)

    def type_next_character(self):
        # Se il testo corrente non corrisponde al testo target, aggiunge un carattere alla volta
        if self.current_text != self.target_text:
            self.current_text = self.target_text[:len(self.current_text) + 1]
            scroll_position = self.text_edit.verticalScrollBar().value()
            self.text_edit.setPlainText(self.current_text)
            self.text_edit.verticalScrollBar().setValue(scroll_position)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle("Log Monitor")
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        grid_layout = QGridLayout()
        self.windows = {}

        # Creazione delle finestre di log per i singoli agenti
        for i, name in enumerate(WINDOWS):
            viewer = LogViewer(f"Agente {name.capitalize()}", LOG_FILES[name])
            self.windows[name] = viewer
            grid_layout.addWidget(viewer, i // 3, i % 3)
        layout.addLayout(grid_layout)

        # Finestra SetEvaluator
        self.set_evaluator = LogViewer("Agente SetEvaluator", SET_EVALUATOR_LOG)
        layout.addWidget(self.set_evaluator)

        # Finestra finale "Results"
        self.final_window = LogViewer("Results", RESULTS_LOG)
        layout.addWidget(self.final_window)

        # Sezione di input dell'utente
        self.input_section = QWidget()
        input_layout = QVBoxLayout()
        self.input_label = QLabel("Inserisci qui la domanda per favore")
        self.input_field = QLineEdit()
        self.input_field.setFixedHeight(40)
        self.input_field.returnPressed.connect(self.capture_input)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_field)
        self.input_section.setLayout(input_layout)
        layout.addWidget(self.input_section)

        self.setLayout(layout)

    def capture_input(self):
        user_input = self.input_field.text()
        print("Input ricevuto:", user_input)
        ras.find_dishes(user_input)
        self.input_field.clear()

if __name__ == "__main__":

    interfaccia = True

    if interfaccia:

        app = QApplication(sys.argv)
        clear_logs()  # Pulisce i log (inclusi i campi Results e SetEvaluator)

        main_window = MainWindow()
        main_window.show()

        sys.exit(app.exec())

    else:
        print("Ciao, scrivi pure la tua domanda!")
        while True:
            user_input = input()
            ras.find_dishes(user_input)
            print("Scrivi pure la tua domanda!")
