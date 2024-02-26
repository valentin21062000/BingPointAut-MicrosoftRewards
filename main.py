import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import random
import string
from PyQt5.QtGui import QPixmap, QIcon

class Worker(QThread):
    update_report = pyqtSignal(str)

    def run(self):
        driver_path = 'msedgedriver.exe'
        service = Service(executable_path=driver_path)
        options = webdriver.EdgeOptions()
        options.use_chromium = True
        browser = webdriver.Edge(service=service, options=options)
        wait = WebDriverWait(browser, 10)

        while True:
            browser.get('https://rewards.bing.com/redeem/pointsbreakdown')
            p_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.pointsDetail.c-subheading-3.ng-binding")))
            progress_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "p[ng-bind-html='$ctrl.pointProgressText'].pointsDetail.c-subheading-3.ng-binding")))
            time.sleep(5)
            if p_element and p_element.text and progress_element and progress_element.text:
                points_earned = int(p_element.text.split()[0])
                total_points_needed = int(progress_element.text.split('/')[-1].strip())
                if points_earned >= total_points_needed:
                    self.update_report.emit("Required points earned. Script completed successfully.")
                    break
                else:
                    result = (total_points_needed - points_earned) // 3
                    self.update_report.emit(f"Calculations result: {result}")
                    while result > 0:
                        self.update_report.emit(f"Remaining searches: {result}")
                        browser.execute_script("window.open('');")
                        browser.switch_to.window(browser.window_handles[-1])
                        browser.get('https://www.bing.com/')
                        search_input = wait.until(EC.element_to_be_clickable((By.ID, "sb_form_q")))
                        search_input.clear()
                        search_input.send_keys(self.generate_random_string())
                        search_input.send_keys(Keys.RETURN)
                        result -= 1
                        time.sleep(5)
                    self.update_report.emit("Iteration completed successfully.")
            else:
                self.update_report.emit("No points detail found.")
                break
        browser.quit()

    def generate_random_string(self, min_length=5, max_length=11):
        length = random.randint(min_length, max_length)
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('BingPoitAut')
        self.setWindowIcon(QIcon('bing.png'))
        self.layout = QVBoxLayout()
        self.startButton = QPushButton('Start')
        self.startButton.clicked.connect(self.startScript)
        self.layout.addWidget(self.startButton)
        self.reportLabel = QLabel('')
        self.layout.addWidget(self.reportLabel)
        self.setLayout(self.layout)
        self.resize(400, 200)

    def startScript(self):
        self.startButton.setEnabled(False)
        self.startButton.setText('Run...')
        self.worker = Worker()
        self.worker.update_report.connect(self.updateReport)
        self.worker.finished.connect(self.onScriptFinish)
        self.worker.start()

    def updateReport(self, message):
        self.reportLabel.setText(message)

    def onScriptFinish(self):
        self.startButton.setEnabled(True)
        self.startButton.setText('Start')

if __name__ == '__main__':
     app = QApplication(sys.argv)
     ex = MyApp()
     ex.show()
     sys.exit(app.exec_())
