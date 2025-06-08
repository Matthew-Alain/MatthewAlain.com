import tkinter as tk
from tkinter import messagebox
import random as rand

window = tk.Tk()                #Creates window that objects will be placed in
window.geometry("1300x700")     #Sets window size
window.title("Battleship")      #Sets window title
enemyBoard = []                 #The array that contains enemy buttons
playerBoard = []                #The array that contains player buttons
rowLabels = []                  #Array containing the row labels (used for button labeling)
gridFrame = tk.Frame(window)    #The grid in which the buttons are contained
gameState = ""                  #Establishes the gamestate that is changed to perform different game actions
shipsPlaced = 0                 #The number of ships placed by the player
playerSunkCount = 0             #The opponent's score
enemySunkCount = 0              #The player's score
gridSize = 10                   #The default length of the grid
maxShips = 5                    #The default number of ships to be placed by both players

class Rules:

    def __init__(self):
        #Creates a grid frame to hold the rules
        self.rulesFrame = tk.Frame(window)
        self.rulesFrame.columnconfigure(0,weight=1)

        #Creates string objects to hold the user inputs for grid size and number of ships
        self.gridUserInput = tk.StringVar(window, str(gridSize))
        self.shipUserInput = tk.StringVar(window, str(maxShips))

        #Displays the instructions and adds them to the frame
        instructions = '''Welcome!
To play, click the player board on the right to place your ships
Then, the computer will place the same number of ships on the enemy board on the left
You will take turns selecting squares to fire at. If you select a square that has a ship on it, it will sink!
Sink all of the enemy ships before they sink all of yours to win!
To begin, click the start button below!
'''
        self.label = tk.Label(self.rulesFrame, text=instructions, font=("Arial",18))
        self.label.grid(row=0, sticky=tk.W + tk.E)

        #Create the button to start the game
        self.startGame = tk.Button(self.rulesFrame, text="Start game!", font=("Arial",18), command=self.callBoard)
        self.startGame.grid(row=1, pady=10)

        #Creates the label and text input for the grid size input
        gridSizeLabel = tk.Label(self.rulesFrame, text="Grid Size", font=("Arial",18))      #Creates label
        gridSizeLabel.grid(row=2, pady=(100,0))                                             #Adds label to grid
        self.gridUserInput.trace_add('write',self.limitGridSize)                            #Links variable to function, function is called whenever the variable is modified
        gridSizeInput = tk.Entry(self.rulesFrame, font=("Arial",18), 
                    textvariable=self.gridUserInput, justify="center", width=5)             #Links variable to input
        gridSizeInput.grid(row=3, pady=5)                                                   #Adds input to grid

        #Same as grid size, but for number of ships
        shipNumLabel = tk.Label(self.rulesFrame, text="Number of Ships", font=("Arial",18))
        shipNumLabel.grid(row=4, pady=(100,0))
        self.shipUserInput.trace_add('write',self.limitShipNum)
        shipNumInput = tk.Entry(self.rulesFrame, font=("Arial",18), 
                    textvariable=self.shipUserInput, justify="center", width=5)
        shipNumInput.grid(row=5, pady=5)

        self.rulesFrame.pack(fill='x')                                                      #Attaches frame to the created window
        window.mainloop()                                                                   #calls the window to be shown on screen

    #Function to validate user input for grid size
    def limitGridSize(self, *args):
        gridNum = self.gridUserInput.get()
        shipNum = self.shipUserInput.get()

        #User can delete default number without error
        if not (gridNum==""):

            if(gridNum=="0"):
                messagebox.showinfo(title="Invalid Entry",message="Grid size should be greater than 0")
                self.gridUserInput.set("1")
                self.shipUserInput.set("1")
                return

            #Prevents non-numeric input
            if(not gridNum.isdigit()):
                messagebox.showinfo(title="Invalid Entry",message="Please only input digits")
                self.gridUserInput.set("1")
                self.shipUserInput.set("1")
                return
            
            #Limits input to two characters
            if len(gridNum)>2:
                self.gridUserInput.set(gridNum[:2])

            #Max grid size is 12 for screen resolution purposes
            if(int(gridNum)>12):
                self.gridUserInput.set("12")
                messagebox.showinfo(title="Maximum Size", message="The maximum grid length is 12")

            #Prevents having more ships than grid squares
            maxSpaces = int(gridNum) * int(gridNum)
            if(maxSpaces < int(shipNum)):
                self.shipUserInput.set(str(maxSpaces-1))
                if(maxSpaces==1):
                    self.shipUserInput.set("1")

    #Function to validate user input for number of ships
    def limitShipNum(self, *args):
        gridNum = self.gridUserInput.get()
        shipNum = self.shipUserInput.get()

        #User can delete default number without error
        if not self.shipUserInput.get()=="":

            #Prevents non-numeric input
            if(not shipNum.isdigit()):
                messagebox.showinfo(title="Invalid Entry",message="Please only input digits")
                self.shipUserInput.set("1")
                return
            
            #Limits input to two characters
            if len(shipNum)>2:
                self.shipUserInput.set(shipNum[:2])

            
            #Limits ship number to one less than size of grid, and double digits
            maxSpaces = int(gridNum) * int(gridNum)
            if(maxSpaces < int(shipNum)):
                if(maxSpaces>100):
                    self.shipUserInput.set("99")
                else:
                    self.shipUserInput.set(str(maxSpaces-1))

            #Minimum ship number of 1
            if(int(shipNum)<1):
                self.shipUserInput.set("1")

    #Gets user inputed values for validation
    def getUserInputs(self):
        return int(self.gridUserInput.get()), int(self.shipUserInput.get())

    def callBoard(self):

        #If user input is invalid, set default values
        gridNum, shipNum = self.getUserInputs()
        if(gridNum<=1):
            self.gridUserInput.set("2")
            messagebox.showinfo(title="Default size", message="Grid too small to play, minimum size set")
        if(shipNum<1):
            self.shipUserInput.set("1")
            messagebox.showinfo(title="Default ships", message="Number of ships too low, minimum number set")

        #Accesses and sets user inputs as values used in rest of program
        global gridSize, maxShips
        gridSize, maxShips = self.getUserInputs()

        #Removes rules display, shows the gameboard
        self.rulesFrame.pack_forget()
        setGameState("DisplayBoard")


class Board:

    #Sets up the game boards
    def setup(self):

        #Creates frame to display current instructions
        self.instructFrame = tk.Frame(window)
        self.instructFrame.columnconfigure(0,weight=1)

        #Creates current instructions and passes it into the grid
        self.instructionLabel = tk.Label(self.instructFrame, text="Select "+str(maxShips)+" squares on the player grid ("+str(maxShips-shipsPlaced)+" more)", font=('Arial',24))
        self.instructionLabel.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.instructFrame.pack(fill='x')

        #Creates frame to display the name labels for the player and enemy grids
        self.labelFrame = tk.Frame(window)
        self.labelFrame.columnconfigure(0,weight=1)
        self.labelFrame.columnconfigure(1,weight=1)

        #Name labels for enemy grid and player grid
        eGridLabel = tk.Label(self.labelFrame, text="Enemy Grid", font=('Arial',18))
        eGridLabel.grid(row=0, column=0, sticky=tk.W + tk.E)
        pGridLabel = tk.Label(self.labelFrame, text="Player Grid", font=('Arial',18))
        pGridLabel.grid(row=0, column=1, sticky=tk.W + tk.E)
        self.labelFrame.pack(fill='x')

        #Creates number of columns to display buttons based on grid size
        for i in range((gridSize+1)*2):
            gridFrame.columnconfigure(i,weight=1)

        #Column labels begin at A, and are then incremented
        colLabel = 'A'

        #Looping through 2D array, beginning with rows
        for i in range(gridSize+1):
            
            #Empty arrays to be populated with buttons for each game board
            eRow = []
            pRow = []

            #First row is only for num labels
            if(i==0):
                for k in range (gridSize+1):
                    
                    #First column is blank, all others display column number
                    if(k>0):
                        eNumLabel = tk.Label(gridFrame, text=k, font=('Arial',18))
                        eNumLabel.grid(row=0, column=k, sticky=tk.W + tk.E)
                        pNumLabel = tk.Label(gridFrame, text=k, font=('Arial',18))
                        pNumLabel.grid(row=0, column=k+gridSize+1, sticky=tk.W + tk.E)

            #Every other row contains buttons
            else:
                for j in range(gridSize+1):

                    #First column in each row is character label for each grid
                    if (j == 0):
                        
                        eCharLabel = tk.Label(gridFrame, text=colLabel, font=('Arial',18))
                        eCharLabel.grid(row=i, column=j, sticky=tk.W + tk.E)
                        pCharLabel = tk.Label(gridFrame, text=colLabel, font=('Arial',18))
                        pCharLabel.grid(row=i, column=j+gridSize+1, sticky=tk.W + tk.E)

                        #Add row label to array for button naming purposes, then increment row label
                        rowLabels.append(colLabel)
                        colLabel = chr(ord(colLabel) + 1)
                    else:
                        #Create button for enemy grid and place in enemy row array
                        eBtn = Button(i, j)
                        eRow.append(eBtn)

                        #Create button for player grid and place in player row array
                        pBtn = Button(i, j+gridSize+1)
                        pRow.append(pBtn)
                
                #At end of each loop, place the rows within the enemy and player board arrays
                enemyBoard.append(eRow)
                playerBoard.append(pRow)

        #Once buttons are created, create a reset button and place it below the current grid in the center
        self.resetButton = tk.Button(gridFrame, text="Reset", font=('Arial',18), command=board.reset)
        self.resetButton.grid(row=gridFrame.grid_size()[1]+1, column=int(gridFrame.grid_size()[0]/2), pady=10)

        #Add the grid to the window to be displayed
        gridFrame.pack(fill='x')

        #Allow the player to begin placing their ships
        setGameState("PlayerPlacing")

    #dude i spent like an hour and a half trying to find a way to delete this stupid reset button, i couldnt 
    #figure out any other way to do it, i had to make a whole function just for this one purpose, this is so dumb
    def destroyReset(self):
        self.resetButton.destroy()

    #Calls the reset function on each button in both grids, resets the global variables, and allows players to place ships again
    def reset(self):
        for i in range(gridSize):
            for j in range(gridSize):
                    enemyBoard[i][j].reset()
                    playerBoard[i][j].reset()
        global playerSunkCount, enemySunkCount, shipsPlaced, enemyTurnCount
        playerSunkCount, enemySunkCount, shipsPlaced, enemyTurnCount = 0, 0, 0, 0
        setGameState("PlayerPlacing")

    #Changes the current displayed instruction
    def setText(self, newText):
        self.instructionLabel.config(text=newText)

    #Calls the reveal function on each button of the enemy grid if there are enemy ships placed
    def revealAll(self):
        if(gameState=="PlayerShooting" or gameState=="EnemyShooting"):
            for i in range(gridSize):
                for j in range(gridSize):
                        enemyBoard[i][j].reveal()
        else:
            messagebox.showinfo(title="Reveal",message="There are no pieces to reveal")


#Class for each square on both grids
class Button:
    def __init__(self, x, y):
        #Initializes coordinates in grid and defaults state to be empty
        self.x = x
        self.y = y
        self.state = "Empty"

        #Identifies if button is in the player grid or enemy grid
        if(y>gridSize+1):
            self.playerSquare = True
        else:
            self.playerSquare = False
        
        #Labels each button based on their relative location of their own grid
        if(self.playerSquare):
            self.label = rowLabels[x-1]+str(y-gridSize-1) 
        else:
            self.label = rowLabels[x-1]+str(y)                   

        #For each object, create a button at the passed coordinates
        self.btn = tk.Button(gridFrame, text=self.label, font=("Arial",18), command=self.click, bg="#00AAFF")
        self.btn.grid(row=x,column=y, sticky=tk.W + tk.E)

    #Defines what should happen when a button is clicked depending on the game state
    def click(self):
        match gameState:
            case "PlayerPlacing":
                #If a user tries to place a ship where they have already placed one
                if(self.playerSquare):
                    if(self.state=="Occupied"):
                        board.setText("That space is occupied, select a square on the player board")
                    #Labels the ship location, marks it as occupied, and increments the number of ships placed until the max number have been placed
                    else:
                        shipNum = "S"+str(shipsPlaced+1)
                        self.btn.config(text=shipNum,bg="#CCCCCC")
                        self.state = "Occupied"
                        Counter.increment()
                #If the user tries to place a ship on the enemy board
                else:
                    board.setText("Invalid square, select a square on the player board")

            #Places enemy ships without labelling or colouring them
            case "EnemyPlacing":
                self.state = "Occupied"

            case "PlayerShooting":
                #Prevents player from targeting an invalid square
                if(self.playerSquare):
                    board.setText("Invalid square, select a square on the enemy board")
                elif(self.state=="Sunk" or self.state=="Missed"):
                    board.setText("You've already shot that square, try another square")
                else:
                    #Identifies squares that have been shot at
                    if(self.state=="Occupied"):
                        self.state="Sunk"
                        self.btn.config(text="X",bg="#FF0000")
                        global enemySunkCount
                        enemySunkCount += 1     #Increments player score
                    else:
                        self.state="Missed"
                        self.btn.config(text="--",bg="#444444")

                    #Check if the game is over, if not, pass turn to computer
                    if not checkIfWon():
                        setGameState("EnemyShooting")

            case "EnemyShooting":
                if(self.state == "Occupied"):
                    self.state="Sunk"
                    self.btn.config(text="X",bg="#FF0000")
                    global playerSunkCount
                    playerSunkCount += 1    #Increments computer score
                else:
                    self.state="Missed"
                    self.btn.config(text="-",bg="#444444")

                #Check if game is over, if not, pass turn to player
                if not checkIfWon():
                    setGameState("PlayerShooting")

    #Reset the button's characteristics to their default
    def reset(self):
        self.__init__(self.x, self.y)

    #Highlight only the occupied squares
    def reveal(self):
        if(self.state=="Occupied"):
            self.btn.config(bg="#FFFF00")

#Change the gamestate, and direct flow control as necessary
def setGameState(newState):
    global gameState
    gameState = newState
    match gameState:
        case "Rules":   #Display the rules and home screen
            Rules()

        case "DisplayBoard":    #Perform initial board setup
            board.setup()

        case "PlayerPlacing":   #Informs the player how many ships they have left to place
            board.setText("Select "+str(maxShips)+" squares on the player grid ("+str(maxShips-shipsPlaced)+" more)")

        case "EnemyPlacing":

            #Places enemy ships randomly in an unoccupied space on the enemy board
            for i in range(maxShips):
                randX = rand.randint(0,gridSize-1)
                randY = rand.randint(0,gridSize-1)

                while(enemyBoard[randX][randY].state == "Occupied"):
                    randX = rand.randint(0,gridSize-1)
                    randY = rand.randint(0,gridSize-1)
                
                enemyBoard[randX][randY].click()

            #Once all ships have been placed, allow the player to shoot
            setGameState("PlayerShooting")

        case "PlayerShooting":
            board.setText("Your turn to shoot!")
    
        case "EnemyShooting":

            #Select a square at random that has not already been targeted
            randX = rand.randint(0,gridSize-1)
            randY = rand.randint(0,gridSize-1)

            while(playerBoard[randX][randY].state == "Missed" or playerBoard[randX][randY].state == "Sunk"):
                randX = rand.randint(0,gridSize-1)
                randY = rand.randint(0,gridSize-1)
            
            playerBoard[randX][randY].click()
    
        #Default just in case, shhhhhhhhhhhh
        case _:
            board.setText("This text should never show, if it does, oops")
            return

#Heck dude, I don't know why I made a whole class for this, this is dumb.
#It tells the player how many ships they have left to place, and when they're done, starts the computer turn
class Counter:
    def increment():
        global shipsPlaced
        shipsPlaced += 1
        board.setText("Select "+str(maxShips)+" squares on the player grid ("+str(maxShips-shipsPlaced)+" more)")
        if(shipsPlaced==maxShips):
            setGameState("EnemyPlacing")

#Checks if one side has sunk all of the other's ships, displays a result message, and returns to the home screen
def checkIfWon():
    if(enemySunkCount==maxShips):
        board.setText("You win!")
        messagebox.showinfo(title="You win!",message="You win!")
        showRules()
        return True
    elif(playerSunkCount==maxShips):
        board.setText("You lost...")
        messagebox.showinfo(title="You lost",message="You lost...")
        showRules()
        return True
    else:
        return False    #If the game is not over, continue play

#Resets all global variables, empties all frames, and clears all arrays, and returns to the home page
def showRules():
    if(not gameState=="Rules"):
        global gridFrame, enemyBoard, playerBoard, rowLabels, board

        board.reset()

        gridFrame.destroy()
        gridFrame = tk.Frame(window)
        board.labelFrame.pack_forget()
        board.instructFrame.pack_forget()
        board.destroyReset()

        enemyBoard = []
        playerBoard = []
        rowLabels = []

        setGameState("Rules")

#Creates and populates menu bar
def setupMenuBar():
    mainMenuBar = tk.Menu(window)                                                   #Creates a menu bar
    subMenuFile = tk.Menu(mainMenuBar, tearoff=0)                                   #Creates the sub-menu
    mainMenuBar.add_cascade(menu=subMenuFile, label="File")                         #Adds the sub-menu to the menu bar
    subMenuFile.add_command(label="Rules",command=showRules)                        #Creates button to return to the home page
    subMenuFile.add_command(label="Reveal Enemy Ships", command=board.revealAll)    #Creates button to show all enemy ships
    window.config(menu=mainMenuBar)                                                 #Actually adds the menubar to the window

board = Board()             #Initially creates the board to be populated (this is just so i don't have to type "self." before everything)
setupMenuBar()              #Calls the menu bar creation
setGameState("Rules")       #Opens the home screen