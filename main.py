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
    def __init__(self, stack, window):
        super().__init__()
        self.stack = stack
        self.window = window

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
            return apology("Missing name/password")

        if user and check_password_hash(user[2], password):
            print("Login successful")
            self.window.current_user_id = user[0]
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
    def __init__(self, stack, window):
        super().__init__()
        self.stack = stack
        self.window = window

        layout = QGridLayout()
        self.setLayout(layout)

        title = QLabel("Main Application Page")
        layout.addWidget(title, 0, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        create_deck_button = QPushButton("Create Deck")
        layout.addWidget(create_deck_button, 1, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        create_deck_button.clicked.connect(self.create_deck)


        decks = QLabel("Decks:")
        layout.addWidget(decks, 2, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        self.refresh_decks()


    def refresh_decks(self):
        # Start from the end of the layout and work backwards since removing items while iterating forward can mess up indexes
        for i in range(self.layout().count() - 1, 2, -1):
            #-1 to get to the last index
            #until greater than 2
            #increment(decrement) -1
            
            # Get the widget item at this row,column position
            item = self.layout().takeAt(i)

            # Get the actual widget inside that layout item
            widget = item.widget()

            # If there is a widget there then delete it
            # deletes later as not to potential mess up the deletion process
            if widget is not None:
                widget.deleteLater()
                
        deck = db.execute("SELECT * FROM decks").fetchall()

        increment = 0
        
        for row in deck:
            button = QPushButton(row[2])
            delete = QPushButton("Delete Deck")
            self.layout().addWidget(button, increment + 3, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
            self.layout().addWidget(delete, increment + 3, 2, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
            button.clicked.connect(lambda checked=False, deck_id=row[0]: self.flashcard_page(deck_id))
            delete.clicked.connect(lambda checked=False, deck_id=row[0]: self.delete_deck(deck_id))
            increment += 1


    def create_deck(self):
        print("Create Deck button clicked")
        self.stack.setCurrentIndex(2) 


    def flashcard_page(self, deck_id):
        self.window.deck_handler_page.set_deck_id(deck_id)
        self.stack.setCurrentIndex(3)


    def delete_deck(self, deck_id):
        db.execute("DELETE FROM decks WHERE id = ?",(deck_id,))
        connection.commit()
        self.refresh_decks()


class DeckHandler(QWidget):
    def __init__(self,stack,window):
        super().__init__()
        self.stack = stack
        self.window = window
        self.deck_id = None
        self.cards = []
        self.current_index = 0


        layout = QGridLayout()
        self.setLayout(layout)

        self.card_label = QLabel("")
        layout.addWidget(self.card_label, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        self.flip_button = QPushButton("Show Answer")
        self.flip_button.clicked.connect(self.toggle_answer)
        layout.addWidget(self.flip_button, 1, 0, 1, 1)

        self.next_button = QPushButton("Next Card")
        self.next_button.clicked.connect(self.next_card)
        layout.addWidget(self.next_button, 1, 1, 1, 1)

        self.add_button = QPushButton("Add Card")
        self.add_button.clicked.connect(self.add_card)
        layout.addWidget(self.add_button, 2, 0, 1, 2)


    def load_card(self, question, answer): #assings question and answer vars
        self.question = question
        self.answer = answer
        self.showing_answer = False #sets bool of toggle
        self.card_label.setText(self.question) #sets text to question first
        self.flip_button.setText("Show Answer") #sets text

    def toggle_answer(self):
        self.showing_answer = not self.showing_answer #toggles true and false
        if self.showing_answer == True:
            self.card_label.setText(self.answer) #change text
            self.flip_button.setText("Show Question") #change text
        else:
            self.card_label.setText(self.question) #same as above
            self.flip_button.setText("Show Answer")

    def set_deck_id(self, deck_id): #gets deck_id and initialises it to a variable in class
        self.deck_id = deck_id
        self.start_deck(deck_id)
        #self.refresh_decks()

    def start_deck(self, deck_id): #Gets q and as from database
        self.cards = []   # handles stale data
        self.current_index = 0  
        flashcards = db.execute("SELECT * FROM flashcards WHERE deck_id = ?", (deck_id,)).fetchall()

        for row in flashcards:
            self.cards.append((row[2], row[3])) #store q and as in list
 
        if self.cards: #if any cards
            question, answer = self.cards[self.current_index] #sets pos cards = q and a as a tuple
            self.load_card(question, answer) #sends both to be loaded and displayed
        else:
            self.card_label.setText("No flashcards")


    def next_card(self):
        if not self.cards:
            return
        
        self.current_index = (self.current_index + 1) % len(self.cards)
        question, answer = self.cards[self.current_index]
        self.load_card(question, answer)
        print("Next card")


    def add_card(self, checked=False):
        self.window.create_card_page.set_deck_id(self.deck_id)
        self.stack.setCurrentIndex(4)


class CreateCardPage(QWidget):
    def __init__(self, stack, window):
        super().__init__()
        self.stack = stack
        self.window = window
        self.deck_id = None

        layout = QGridLayout()
        self.setLayout(layout)

        title = QLabel("Card Creation Form")
        layout.addWidget(title, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        question = QLabel("Question:")
        layout.addWidget(question, 1, 0)

        self.question = QLineEdit()
        layout.addWidget(self.question, 1, 1, 1, 1)

        answer = QLabel("Answer:")
        layout.addWidget(answer, 2, 0)

        self.answer = QLineEdit()
        layout.addWidget(self.answer, 2, 1, 1, 1)

        button1 = QPushButton("Create Card")
        button1.clicked.connect(self.insert_card)
        layout.addWidget(button1, 3, 1)


    def set_deck_id(self, deck_id): #gets deck_id and initialises it to a variable in class
        self.deck_id = deck_id


    def insert_card(self, checked=False):
        question = self.question.text()
        answer = self.answer.text()
        if not answer or not question:
            print("Please fill in all boxes")
            return apology()

        db.execute("INSERT INTO flashcards (deck_id, question, answer) VALUES (?, ?, ?)", (self.deck_id, question, answer))
        connection.commit()
        print("Card created successfully")

        self.window.deck_handler_page.start_deck(self.deck_id)
        self.stack.setCurrentIndex(3)


class CreateDeckPage(QWidget):
    def __init__(self, stack, window):
        super().__init__()
        self.stack = stack
        self.window = window

        layout = QGridLayout()
        self.setLayout(layout)

        title = QLabel("Deck Creation Form")
        layout.addWidget(title, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        name = QLabel("Name:")
        layout.addWidget(name, 1, 0)

        self.deckname = QLineEdit()
        layout.addWidget(self.deckname, 1, 1, 1, 2)

        button1 = QPushButton("Create Deck")
        button1.clicked.connect(self.insert_deck)
        layout.addWidget(button1, 3, 1)


    def insert_deck(self):
        name = self.deckname.text()
        if not name:
            print("Please fill in the deck name")
            return apology()

        db.execute("INSERT INTO decks (user_id, name) VALUES (?, ?)", (self.window.current_user_id, name))
        connection.commit()
        print("Deck created successfully")

        self.window.main_app_page.refresh_decks()
        self.stack.setCurrentIndex(1)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")

        self.current_user_id = None

        layout = QGridLayout()
        self.setLayout(layout)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.login_page = LoginPage(self.stack, self)
        self.main_app_page = MainAppPage(self.stack, self)
        self.create_deck_page = CreateDeckPage(self.stack, self)
        self.deck_handler_page = DeckHandler(self.stack, self)
        self.create_card_page = CreateCardPage(self.stack, self)

        self.stack.addWidget(self.login_page)     
        self.stack.addWidget(self.main_app_page)   
        self.stack.addWidget(self.create_deck_page)
        self.stack.addWidget(self.deck_handler_page)
        self.stack.addWidget(self.create_card_page)

        self.stack.setCurrentIndex(0) 



app = QApplication(sys.argv)
window = Window()
window.show()
app.exec()