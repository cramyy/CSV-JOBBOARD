import sys
import os
import subprocess
import uuid
import getpass
import requests
from git import Repo, GitCommandError
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

class CustomLogger:
    def __init__(self, filename):
        self.filename = filename

    def log(self, level, message):
        username = getpass.getuser()
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                                for elements in range(0,2*6,2)][::-1])
        now = datetime.now()
        time_str = now.strftime("%I:%M%p")
        date_str = now.strftime("%d %B %Y")

        log_entry = f"Username: {username}\n"
        log_entry += f"MAC Address: {mac_address}\n"
        log_entry += f"{level} - {message}\n"
        log_entry += f"TIME: {time_str}\n"
        log_entry += f"DATE: {date_str}\n\n\n"

        with open(self.filename, 'a') as log_file:
            log_file.write(log_entry)

class JobUpdaterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = CustomLogger('logs.txt')
        self.repo = Repo('.')  # Initialize the Git repo
        self.repo_url = "https://github.com/cramyy/CSV-JOBBOARD.git"
        self.repo_owner = "cramyy"
        self.repo_name = "CSV-JOBBOARD"
        self.initUI()
        self.log_system_info()

    def initUI(self):
        self.setWindowTitle('Job Updater')
        self.setGeometry(100, 100, 500, 500)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter your name")
        layout.addWidget(self.name_input)

        self.link_input = QLineEdit(self)
        self.link_input.setPlaceholderText("Enter Google Sheet link")
        layout.addWidget(self.link_input)

        self.token_input = QLineEdit(self)
        self.token_input.setPlaceholderText("Enter Passkey")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.token_input)

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

    def log_system_info(self):
        self.logger.log("INFO", "System Info")

    def update_jobs(self):
        updater_name = self.name_input.text()
        sheet_link = self.link_input.text()
        github_token = self.token_input.text()

        if not updater_name or not sheet_link or not github_token:
            self.status_label.setText("Please fill in all fields.")
            return

        try:
            self.animate_button()

            file_id = sheet_link.split('/')[5]
            download_link = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx'

            self.run_update_jobs(download_link, updater_name, github_token)

            self.status_label.setText("Jobs updated and pull request created successfully!")
            self.logger.log("INFO", f"Jobs updated by {updater_name}")
        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.status_label.setText(error_message)
            self.logger.log("ERROR", f"Error occurred while {updater_name} was updating jobs: {error_message}")

        self.update_log_display()

    def animate_button(self):
        animation = QPropertyAnimation(self.update_button, b"geometry")
        animation.setDuration(100)
        animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        start = self.update_button.geometry()
        animation.setStartValue(start)
        animation.setEndValue(start.adjusted(0, 5, 0, 5))
        animation.start()

    def run_update_jobs(self, download_link, updater_name, github_token):
        try:
            subprocess.run([sys.executable, 'update_jobs.py', download_link, updater_name], check=True)
            self.create_pull_request(updater_name, github_token)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error running update_jobs.py: {e}")

    def create_pull_request(self, updater_name, github_token):
        try:
            repo = self.repo
            repo.git.checkout('main')
            repo.git.pull('origin', 'main')
            
            branch_name = f"update-jobs-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            repo.git.checkout('-b', branch_name)
            
            repo.git.add('.')
            repo.git.commit('-m', f"Update jobs by {updater_name}")
            
            # Set the remote URL with the token
            remote_url = f'https://{github_token}@github.com/{self.repo_owner}/{self.repo_name}.git'
            repo.remotes.origin.set_url(remote_url)
            
            repo.git.push('--set-upstream', 'origin', branch_name)
            
            self.create_github_pr(self.repo_owner, self.repo_name, branch_name, github_token, updater_name)
            
        except GitCommandError as e:
            self.logger.log("ERROR", f"Git error: {str(e)}")
            raise
        except Exception as e:
            self.logger.log("ERROR", f"Error creating pull request: {str(e)}")
            raise

    def create_github_pr(self, repo_owner, repo_name, branch_name, github_token, updater_name): 
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "title": f"Update jobs by {updater_name}",
            "head": branch_name,
            "base": "main",
            "body": f"Automated pull request for job updates by {updater_name}."
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # This will raise an exception for HTTP errors
            pr_url = response.json()["html_url"]
            self.logger.log("INFO", f"Pull request created successfully: {pr_url}")
            return True
        except requests.exceptions.RequestException as e:
            error_message = f"Failed to create pull request. Error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_message += f"\nResponse status code: {e.response.status_code}"
                error_message += f"\nResponse body: {e.response.text}"
            self.logger.log("ERROR", error_message)
            self.status_label.setText(error_message)
            raise

    def update_log_display(self):
        try:
            with open('logs.txt', 'r') as log_file:
                logs = log_file.readlines()
                logs.reverse()
                log_text = ''.join(logs)
                self.log_display.setText(log_text)
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