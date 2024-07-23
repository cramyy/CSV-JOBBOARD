import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
import logging

class JobUpdaterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setup_logging()

    def initUI(self):
        self.setWindowTitle('Job Updater')
        self.setGeometry(100, 100, 500, 400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter your name")
        layout.addWidget(self.name_input)

        self.link_input = QLineEdit(self)
        self.link_input.setPlaceholderText("Enter Google Sheet link")
        layout.addWidget(self.link_input)

        self.update_button = QPushButton('Update Jobs', self)
        self.update_button.setStyleSheet("""
            QPushButton {
                background-color: #8a2be2;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #9b4deb;
            }
        """)
        self.update_button.clicked.connect(self.update_jobs)
        layout.addWidget(self.update_button)

        self.status_label = QLabel('', self)
        layout.addWidget(self.status_label)

        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel, QLineEdit, QTextEdit {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #3b3b3b;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                margin-bottom: 10px;
            }
            QTextEdit {
                background-color: #3b3b3b;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
            }
        """)

        self.update_log_display()

    def setup_logging(self):
        logging.basicConfig(filename='logs.txt', level=logging.INFO, 
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def update_jobs(self):
        updater_name = self.name_input.text()
        sheet_link = self.link_input.text()

        if not updater_name:
            self.status_label.setText("Please enter your name.")
            return

        if not sheet_link:
            self.status_label.setText("Please enter a Google Sheet link.")
            return

        try:
            # Animate button
            self.animate_button()

            # Convert the link
            file_id = sheet_link.split('/')[5]
            download_link = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx'

            # Run the update_jobs.py file with the new link
            self.run_update_jobs(download_link, updater_name)

            self.status_label.setText("Jobs updated successfully!")
            logging.info(f"Jobs updated by {updater_name}")
        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.status_label.setText(error_message)
            logging.error(f"Error occurred while {updater_name} was updating jobs: {error_message}")

        self.update_log_display()

    def animate_button(self):
        animation = QPropertyAnimation(self.update_button, b"geometry")
        animation.setDuration(100)
        animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        start = self.update_button.geometry()
        animation.setStartValue(start)
        animation.setEndValue(start.adjusted(0, 5, 0, 5))
        animation.start()

    def run_update_jobs(self, download_link, updater_name):
        venv_path = os.environ.get('VIRTUAL_ENV')
        if venv_path:
            python_path = os.path.join(venv_path, 'bin', 'python')
            if os.name == 'nt':  # For Windows
                python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:
            python_path = sys.executable

        try:
            subprocess.run([python_path, 'update_jobs.py', download_link, updater_name], check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error running update_jobs.py: {e}")

    def update_log_display(self):
        try:
            with open('logs.txt', 'r') as log_file:
                logs = log_file.read()
                self.log_display.setText(logs)
                self.log_display.verticalScrollBar().setValue(
                    self.log_display.verticalScrollBar().maximum()
                )
        except FileNotFoundError:
            self.log_display.setText("No logs found.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = JobUpdaterGUI()
    ex.show()
    sys.exit(app.exec())