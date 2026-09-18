import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout, QLabel, QLineEdit, QStackedWidget,
)
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

from setup_db import apology

connection = sqlite3.connect("revision.db")
db = connection.cursor()


class LoginPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack  

        layout = QGridLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self.setLayout(layout)

        title = QLabel("Login Form")
        layout.addWidget(title, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        user = QLabel("Username:")
        layout.addWidget(user, 1, 0)

        password = QLabel("Password:")
        layout.addWidget(password, 2, 0)

        self.input1 = QLineEdit()
        layout.addWidget(self.input1, 1, 1, 1, 2)

        self.input2 = QLineEdit()
        self.input2.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input2, 2, 1, 1, 2)

        button1 = QPushButton("Register")
        button1.clicked.connect(self.register)
        layout.addWidget(button1, 3, 1)

        button2 = QPushButton("Login")
        button2.clicked.connect(self.login)
        layout.addWidget(button2, 3, 2)

    def login(self):
        username = self.input1.text()
        password = self.input2.text()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not username or not password:
            print("Please fill in all fields")
            return apology()

        if user and check_password_hash(user[2], password):
            print("Login successful")
            self.stack.setCurrentIndex(1)   
        else:
            print("Login failed")
            return apology()

    def register(self):
        username = self.input1.text()
        password = self.input2.text()
        hash = generate_password_hash(password, method="scrypt", salt_length=16)
        if not username or not password:
            print("Please fill in all fields")
            return apology()

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
        connection.commit()
        print("User registered successfully")


class MainAppPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel("Welcome! You're logged in."))


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")

        layout = QGridLayout()
        self.setLayout(layout)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.login_page = LoginPage(self.stack)
        self.main_app_page = MainAppPage()

        self.stack.addWidget(self.login_page)     
        self.stack.addWidget(self.main_app_page)   

        self.stack.setCurrentIndex(0) 


app = QApplication(sys.argv)
window = Window()
window.show()
app.exec()