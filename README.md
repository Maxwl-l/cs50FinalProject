# Project Title: MemoryStack
#### Video Demo:  <[URL HERE](https://www.youtube.com/watch?v=Txlhxn4HTD4)>
#### Description: MemoryStack is a flashcard app used for revision. It allows the user to create new decks and input flashcards in them. Additionally allowing the user
#### to edit either the deck or individual card by renaming them or deleting them completely. Each user is allowed to create an account and each deck/cards are specific
#### to each user.


main.py
The entirety of the code.
class LoginPage:
This is the first window the user sees when running the app. Alongside the title it includes two text boxes for the user to enter their name and password along with two buttons
to either login or create a new account.
The class handles any missing field or invalid user, displaying a message box warning to the user.
Pressing Login with valid text inputs directs the user to the the main window, passing in the user's id.
Pressing Create Account will direct the user to a new window where they can create their account.

class CreateAccount:
This is where the user can create their account if they do not have one already.
Aside from the title, it features three text boxes for their name, password and another box to confirm their password. Similarly, there are two buttons, Create Account and Cancel.
Pressing Cancel will send the user back to the login page, pressing create account with valid inputs will direct the user back to the login page aswell, but with their details now being inserted into the users table, making them a valid user.
The class handles any missing field or mismatched passwords, displaying a message box warning to the user.

class MainAppPage:
This is the main page for the user and will show all their decks they have created that are specific to their account.
It features alongside the title, two buttons, log out and create deck, along with a scroll area for if the user has too many decks, it will enable scrolling.
The main bulk of the page is where the users decks appear, on either side of the deck (which is a button) are two buttons, delete deck and rename deck.
As per the name, delete deck will delete the deck from the table decks and remove its display along with its adjacent buttons.
Rename deck will set a text box visible for the user to type the new name of their deck, and upon pressing enter will change the name of the deck in the table decks and in the display.
At the top, the two buttons Log out and Create Deck, respectively return the user back to the log in page and create a new deck which will display in the scroll area.
Whenever something changes the decks table, the function refresh_decks is called. This essentially deletes the decks displayed and rebuilds the display to show the new decks.
Pressing the deck name which itself is a button will direct the user to the a new window, passing in that deck's id.

class DeckHandler:
This is where the user can cycle through their cards. It has five buttons, one of which is hidden if their are no cards available: Show Answer (the initially hidden one), Next Card, Add Card, Edit Card and Return to Decks. It also features a label set as "" which is for showing either the answer or question whether its toggled.
The majority of the functions in this class take the deck_id that was passed into a function in this class and load the cards of that deck from the tables flashcards into a list. Then whether the Show answer has been toggled, it will display the question or answer into the "" label. Again, if no cards in the table, then the Show answer button is hidden. Pressing Add card directs the user to a new window, same with edit cards. The return to decks button directs the user back to the main page.
Pressing Next card, if there are any more cards, will change the "" label to display the question of the next card in the table.

class CreateCardPage:
This is where the user can create a new card in their deck. It features a title, two text boxes for the question and answer of the new cards and two buttons two either return to the deckhander window or to create the card.
If the user tries to press the create card button without filling in all the forms, then it will display a message box warning to the user. Once there are valid inputs and the user presses the create card button, then the question and answer will be added to a new card in the table and can be seen in the deckhandler page where the user will be directed to after pressing the create card button.

class CreateDeckPage:
Users are directed here after pressing the create deck button in the main page. It features a title, one text box for the name of the deck and two buttons to confirm the creation of the deck and to cancel.
If the user tries to create the deck without any name being entered, then a message box warning will be displayed. Clicking the cancel button will direct the user back to the main page. If the create deck button is clicked with a name in the text box, then that deck will be added to the table decks where the user_id is the id of the current user. Similarly, the new deck is displayed on the main page after refresh_decks is called once the create deck button was clicked.

class EditCards:
Users are directed here after clicking the edit cards button on the deckhandler window. Similarly to the main page, on this window, it displays a title alongside a return button that when pressed, directs the user back to the deckhandler window. Below that is a scroll area which will display every card in the deck. It will display the question and answer of each card in the deck, alongside a delete card button on the left and two rename buttons for both the question and answer of the card. Like the main page, pressing the delete card button will delete the card from display and the table flashcards. Pressing rename will prompt a text box where the user can type in a new question or answer depending on which rename button was pressed. Then pressing enter will change the display and the question or answer in the table.

class Window:
This is where the stack is made. This holds all the stacks of each page which allows each class to direct the user to another window. Additionally it is where i set the size of the app and is also where I store the current_user_id, passing the window object to the classes that need the ID.

with open("style.qss", "r") as f:
    app.setStyleSheet(f.read())
This links my css file to my main.py file

setup_db.py:
This is where I made my three tables, users to hold user log in details, decks to hold each deck that each user makes or has and flashcards to hold the flashcards of each of the decks.

