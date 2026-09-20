import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout, QLabel, QLineEdit, QStackedWidget, QScrollArea, QVBoxLayout, QMessageBox,
)
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

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

        button1 = QPushButton("Create Account")
        button1.clicked.connect(self.register)
        layout.addWidget(button1, 3, 1)

        button2 = QPushButton("Login")
        button2.setObjectName("primaryButton")  
        button2.clicked.connect(self.login)
        layout.addWidget(button2, 3, 2)

    def login(self):
        username = self.input1.text()
        password = self.input2.text()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Missing Field")
            return

        if user and check_password_hash(user[2], password):
            self.window.current_user_id = user[0]
            self.window.main_app_page.refresh_decks()
            self.stack.setCurrentIndex(1)   
        else:
            QMessageBox.warning(self, "Error", "Invalid User")
            return

        self.input1.clear()
        self.input2.clear()


    def register(self):
        self.stack.setCurrentIndex(6)  


class CreateAccount(QWidget):
    def __init__(self, stack, window):
        super().__init__()
        self.stack = stack
        self.window = window

        layout = QGridLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self.setLayout(layout)

        title = QLabel("Register Form")
        layout.addWidget(title, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        cancel_button = QPushButton("Cancel")
        layout.addWidget(cancel_button, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        cancel_button.clicked.connect(self.cancel)

        user = QLabel("Username:")
        layout.addWidget(user, 1, 0)

        password = QLabel("Password:")
        layout.addWidget(password, 2, 0)

        confirm = QLabel("Confirm Password")
        layout.addWidget(confirm, 3, 0)

        self.input1 = QLineEdit()
        layout.addWidget(self.input1, 1, 1, 1, 2)

        self.input2 = QLineEdit()
        self.input2.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input2, 2, 1, 1, 2)

        self.input3 = QLineEdit()
        self.input3.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input3, 3, 1, 1, 2)

        button1 = QPushButton("Create Account")
        button1.clicked.connect(self.register)
        button1.setObjectName("primaryButton")  
        layout.addWidget(button1, 4, 1)


    def cancel(self):
        self.input1.clear()
        self.input2.clear()
        self.input3.clear()
        self.stack.setCurrentIndex(0) 


    def register(self):
        name = self.input1.text()
        password = self.input2.text()
        confirm = self.input3.text()

        if not name or not password or not confirm:
            QMessageBox.warning(self, "Error", "Missing Field")
            return

        if confirm != password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return

        check = db.execute("SELECT username FROM users WHERE username = ?", (name,)).fetchall()

        if check:
            QMessageBox.warning(self, "Error", "Name Already Exists")
            return


        hash = generate_password_hash(password, method="scrypt", salt_length=16)

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (name, hash))

        self.input1.clear()
        self.input2.clear()
        self.input3.clear()

        self.stack.setCurrentIndex(0) 


class MainAppPage(QWidget):
    def __init__(self, stack, window):
        super().__init__()
        self.stack = stack
        self.window = window
        self.rename_inputs = {}

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Main Application Page")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        log_out_button = QPushButton("Log Out")
        layout.addWidget(log_out_button, alignment=Qt.AlignmentFlag.AlignCenter)
        log_out_button.clicked.connect(self.log_out)

        create_deck_button = QPushButton("Create Deck")
        layout.addWidget(create_deck_button, alignment=Qt.AlignmentFlag.AlignCenter)
        create_deck_button.clicked.connect(self.create_deck)


        decks = QLabel("Decks:")
        layout.addWidget(decks, alignment=Qt.AlignmentFlag.AlignCenter)

        self.scroll_content = QWidget()
        self.deck_layout = QGridLayout()
        self.scroll_content.setLayout(self.deck_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.scroll_content)
        scroll_area.setWidgetResizable(True) 

        layout.addWidget(scroll_area)

        self.refresh_decks()


    def refresh_decks(self):
        # Start from the end of the layout and work backwards since removing items while iterating forward can mess up indexes
        for i in range(self.deck_layout.count() - 1, -1, -1):
            #-1 to get to the last index
            #until greater than 2
            #increment(decrement) -1
            
            # Get the widget item at this row,column position
            item = self.deck_layout.takeAt(i)

            # Get the actual widget inside that layout item
            widget = item.widget()

            # If there is a widget there then delete it
            # deletes later as not to potential mess up the deletion process
            if widget is not None:
                widget.deleteLater()


        deck = db.execute("SELECT * FROM decks WHERE user_id = ?", (self.window.current_user_id,)).fetchall()

        increment = 0
        self.rename_inputs = {}
        
        for row in deck:
            deck_id = row[0]

            button = QPushButton(row[2])
            delete = QPushButton("Delete Deck")
            delete.setObjectName("dangerButton")
            rename = QPushButton("Rename")
            rename_input = QLineEdit()
            rename_input.setVisible(False)
            self.deck_layout.addWidget(rename_input, increment, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            self.deck_layout.addWidget(button, increment, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            self.deck_layout.addWidget(delete, increment, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            self.deck_layout.addWidget(rename, increment, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

            self.rename_inputs[deck_id] = rename_input

            rename_input.returnPressed.connect(lambda deck_id=deck_id: self.confirm_rename(deck_id))
            button.clicked.connect(lambda checked=False, deck_id=deck_id: self.flashcard_page(deck_id))
            delete.clicked.connect(lambda checked=False, deck_id=deck_id: self.delete_deck(deck_id))
            rename.clicked.connect(lambda checked=False, deck_id=deck_id: self.reveal_rename(deck_id))
            increment += 1


    def log_out(self):
        self.stack.setCurrentIndex(0) 

    def reveal_rename(self, deck_id):
        input = self.rename_inputs[deck_id] 
        input.setVisible(True)
        input.setFocus()


    def confirm_rename(self,deck_id):
        input = self.rename_inputs[deck_id]
        renamed = input.text()
        if not renamed:
            QMessageBox.warning(self, "Error", "Missing Field")
            return

        db.execute("UPDATE decks SET name = ? WHERE id = ?", (renamed, deck_id))
        connection.commit()

        input.setVisible(False)
        input.clear()
        self.refresh_decks()


    def create_deck(self):
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

        self.edit_button = QPushButton("Edit Cards")
        self.edit_button.clicked.connect(self.edit_cards)
        layout.addWidget(self.edit_button, 3, 0, 1, 2)

        self.go_back = QPushButton("Return to Decks")
        self.go_back.clicked.connect(self.back)
        layout.addWidget(self.go_back, 4, 0, 1, 2)


    def edit_cards(self,checked=False):
        self.window.edit_cards_page.set_deck_id(self.deck_id)
        self.stack.setCurrentIndex(5)


    def back(self, checked=False):
        self.window.main_app_page.refresh_decks()
        self.stack.setCurrentIndex(1) 

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
            self.flip_button.setVisible(True)
            question, answer = self.cards[self.current_index] #sets pos cards = q and a as a tuple
            self.load_card(question, answer) #sends both to be loaded and displayed
        else:
            self.card_label.setText("No flashcards")
            self.flip_button.setVisible(False)


    def next_card(self):
        if not self.cards:
            return
        
        self.current_index = (self.current_index + 1) % len(self.cards)
        question, answer = self.cards[self.current_index]
        self.load_card(question, answer)


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

        button2 = QPushButton("Cancel")
        button2.clicked.connect(self.cancel)
        layout.addWidget(button2, 3, 2)


    def set_deck_id(self, deck_id): #gets deck_id and initialises it to a variable in class
        self.deck_id = deck_id


    def cancel(self, checked=False):
        self.deckname.clear()
        self.stack.setCurrentIndex(3)


    def insert_card(self, checked=False):
        question = self.question.text()
        answer = self.answer.text()
        if not answer or not question:
            QMessageBox.warning(self, "Error", "Missing Field")
            return

        db.execute("INSERT INTO flashcards (deck_id, question, answer) VALUES (?, ?, ?)", (self.deck_id, question, answer))
        connection.commit()
        self.question.clear()
        self.answer.clear()

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
        layout.addWidget(button1, 1, 3)

        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.cancel)
        layout.addWidget(cancel, 2, 3)


    def cancel(self, checked=False):
        self.stack.setCurrentIndex(1)


    def insert_deck(self):
        name = self.deckname.text()
        if not name:
            QMessageBox.warning(self, "Error", "Missing Field")
            return

        db.execute("INSERT INTO decks (user_id, name) VALUES (?, ?)", (self.window.current_user_id, name))
        connection.commit()
        self.deckname.clear()

        self.window.main_app_page.refresh_decks()
        self.stack.setCurrentIndex(1)


class EditCards(QWidget):
    def __init__(self, stack, window):
        super().__init__()
        self.stack = stack
        self.window = window
        self.deck_id = None

        self.rename_inputs = {}
        self.renameA_inputs = {}

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Edit")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        cards = QLabel("cards:")
        layout.addWidget(cards, alignment=Qt.AlignmentFlag.AlignCenter)

        cancel = QPushButton("Return")
        cancel.clicked.connect(self.cancel)
        layout.addWidget(cancel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.scroll_content = QWidget()
        self.deck_layout = QGridLayout()
        self.scroll_content.setLayout(self.deck_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.scroll_content)
        scroll_area.setWidgetResizable(True) 

        layout.addWidget(scroll_area)

        self.refresh_decks()

    def cancel(self):
        self.stack.setCurrentIndex(3) 
        self.window.deck_handler_page.set_deck_id(self.deck_id)


    def refresh_decks(self):
        # Start from the end of the layout and work backwards since removing items while iterating forward can mess up indexes
        for i in range(self.deck_layout.count() - 1, -1, -1):
            #-1 to get to the last index
            #until greater than 2
            #increment(decrement) -1
            
            # Get the widget item at this row,column position
            item = self.deck_layout.takeAt(i)

            # Get the actual widget inside that layout item
            widget = item.widget()

            # If there is a widget there then delete it
            # deletes later as not to potential mess up the deletion process
            if widget is not None:
                widget.deleteLater()


        cards = db.execute("SELECT * FROM flashcards WHERE deck_id = ?", (self.deck_id,)).fetchall()

        increment = 0
        self.rename_inputs = {}
        self.renameA_inputs = {}
        
        for row in cards:
            card_id = row[0]

            question = QPushButton(row[2])
            answer = QPushButton(row[3])
            delete = QPushButton("Delete Card")
            delete.setObjectName("dangerButton")
            rename = QPushButton("Rename")
            rename_input = QLineEdit()
            renameA = QPushButton("Rename")
            renameA_input = QLineEdit()

            rename_input.setVisible(False)
            renameA_input.setVisible(False)

            grid_row = increment * 2

            self.deck_layout.addWidget(delete, grid_row, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            self.deck_layout.addWidget(question, grid_row, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            self.deck_layout.addWidget(rename, grid_row, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            self.deck_layout.addWidget(rename_input, grid_row, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

            self.deck_layout.addWidget(answer, grid_row + 1, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            self.deck_layout.addWidget(renameA, grid_row + 1, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            self.deck_layout.addWidget(renameA_input, grid_row + 1, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

            self.rename_inputs[card_id] = rename_input
            self.renameA_inputs[card_id] = renameA_input

            rename_input.returnPressed.connect(lambda card_id=card_id: self.confirm_rename(card_id,"q"))
            renameA_input.returnPressed.connect(lambda card_id=card_id: self.confirm_rename(card_id,"a"))

            rename.clicked.connect(lambda checked=False, card_id=card_id: self.reveal_rename(card_id,"q"))
            renameA.clicked.connect(lambda checked=False, card_id=card_id: self.reveal_rename(card_id,"a"))

            delete.clicked.connect(lambda checked=False, card_id=card_id: self.delete_deck(card_id))

            increment += 1


    def reveal_rename(self, card_id, type):
        if type == "q":
            inputQ = self.rename_inputs[card_id]
            inputQ.setVisible(True)
            inputQ.setFocus()
        elif type == "a":
            inputA = self.renameA_inputs[card_id]
            inputA.setVisible(True)
            inputA.setFocus()


    def confirm_rename(self,card_id,type):
        if type == "q":
            inputQ = self.rename_inputs[card_id]
            renamed = inputQ.text()
            if not renamed:
                QMessageBox.warning(self, "Error", "Missing Field")
                return

            db.execute("UPDATE flashcards SET question = ? WHERE id = ?", (renamed, card_id))
            connection.commit()
            inputQ.setVisible(False)
            inputQ.clear()

        elif type == "a":
            inputA = self.renameA_inputs[card_id]
            renamed = inputA.text()
            if not renamed:
                QMessageBox.warning(self, "Error", "Missing Field")
                return

            db.execute("UPDATE flashcards SET answer = ? WHERE id = ?", (renamed, card_id))
            connection.commit()    
            inputA.setVisible(False)
            inputA.clear()


        self.refresh_decks()


    def create_deck(self):
        self.stack.setCurrentIndex(2) 


    def delete_deck(self, card_id):
        db.execute("DELETE FROM flashcards WHERE id = ?",(card_id,))
        connection.commit()
        self.refresh_decks()


    def set_deck_id(self, deck_id): #gets deck_id and initialises it to a variable in class
        self.deck_id = deck_id
        self.refresh_decks()

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MemoryStack")
        self.setFixedSize(900, 600) 
        self.setMinimumSize(600, 400)

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
        self.edit_cards_page = EditCards(self.stack, self)
        self.create_account_page = CreateAccount(self.stack, self)

        self.stack.addWidget(self.login_page)     
        self.stack.addWidget(self.main_app_page)   
        self.stack.addWidget(self.create_deck_page)
        self.stack.addWidget(self.deck_handler_page)
        self.stack.addWidget(self.create_card_page)
        self.stack.addWidget(self.edit_cards_page)
        self.stack.addWidget(self.create_account_page)

        self.stack.setCurrentIndex(0) 



app = QApplication(sys.argv)

with open("style.qss", "r") as f:
    app.setStyleSheet(f.read())

window = Window()
window.show()
app.exec()