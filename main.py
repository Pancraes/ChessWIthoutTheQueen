import pygame as p
import os
from renderGame import *
import sys

# creating screen dimensions
WIDTH = 560
HEIGHT = 560
#Board Dimensions
ROWS = 7
COLUMNS = 7
SQUARESIZE = HEIGHT//ROWS
MAXFPS = 15
IMAGES = {}

def createImages():
    pieces = ["wP", "wR", "wB", "wN", "wK", "bP", "bR", "bB", "bN", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f'assets/images/imgs-128px/{piece}.png'),(SQUARESIZE, SQUARESIZE))




"""shit the needs to be fixed:
pawn promotion
castling
checkmate/stalemate logic
"""

def main():
    p.init()
    pygame.display.set_caption('Chess Without a Queen')
    icon = pygame.image.load("icon.png")
    pygame.display.set_icon(icon)
    
    screen = p.display.set_mode((WIDTH, HEIGHT)) #setting screen dimensions
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    
    rg = RenderGame()
    vm = rg.validMoves()
    moveMade = False #variable for when move is made by player
    createImages() #loading in the images of the pieces
    running = True
    animate = False
    squareSelected = () #no square selected, keeps track of user
    clicks = [] #keeps track of player clicks, no click
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                sys.exit()
                
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    position = p.mouse.get_pos()#x and y of the mouse
                    column = position[0]//SQUARESIZE
                    row = position[1]//SQUARESIZE

                    if squareSelected == (row, column): #undo action basically
                        squareSelected =()#deselect
                        clicks = []#clear player clicks
                        
                    else:
                        squareSelected = (row, column)
                        clicks.append(squareSelected)
                        
                    if len(clicks) == 2: #after 2nd click
                        move = Move(clicks[0], clicks[1], rg.board)
                        
                        for i in range(len(vm)):
                            if move == vm[i]:
                                rg.makeMove(vm[i])
                                animate = True
                                moveMade = True
                                squareSelected = ()#deselect
                                clicks=[]#clear player clicks
                        
                        if not moveMade:
                            clicks = [squareSelected]
                        
            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:
                    rg.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r:
                    rg = RenderGame()
                    vm = rg.validMoves()
                    squareSelected = ()
                    clicks = []
                    moveMade = False
                    animate = False
        
        if moveMade:
            if animate:
                animateMove(rg.moveLog[-1], screen, rg.board, clock)
            vm = rg.validMoves()
            moveMade = False
            animate = False
        
        createGame(screen, rg, vm, squareSelected)
        
        if rg.checkmate:
            gameOver = True
            if rg.whiteToMove:
                drawText(screen, "White uninstall the game ur bad")
            else:
                drawText(screen, "Black uninstall the game ur bad")
        elif rg.stalemate:
            gameOver = True
            drawText(screen, "Imagine stalemating LMAO")
            
        
        clock.tick(MAXFPS)
        p.display.flip()


#highlight square selected
def highlightSquare(screen, rg, validMoves, squareSelected):
    if squareSelected != ():
        row, column = squareSelected
        if rg.board[row][column][0] == ('w' if rg.whiteToMove else 'b'):
            s = p.Surface((SQUARESIZE, SQUARESIZE))
            s.set_alpha(100) #transparency
            s.fill(p.Color('yellow'))#selcted square
            screen.blit(s, (column*SQUARESIZE, row*SQUARESIZE))
            s.fill(p.Color('azure4'))#moves from that square
            for move in validMoves:
                if move.startRow == row and move.startColumn == column:
                    screen.blit(s, (SQUARESIZE*move.endColumn, SQUARESIZE*move.endRow))
            

def createGame(screen, rg, validMoves, squareSelected):#creating checkered board and all the pieces on it
    createBoard(screen)
    highlightSquare(screen, rg, validMoves, squareSelected)
    createPieces(screen, rg.board)
    
def createBoard(screen):
    global colours
    colours = [p.Color("mintcream"), p.Color("cadetblue3")]
    for row in range(ROWS):
        for column in range(COLUMNS):
            colour = colours[((row+column)%2)]
            p.draw.rect(screen, colour, p.Rect(column*SQUARESIZE, row*SQUARESIZE, SQUARESIZE, SQUARESIZE))
            

def createPieces(screen, board):
    for row in range(ROWS):
        for column in range(COLUMNS):
            piece = board[row][column]
            if piece != '  ':
                screen.blit(IMAGES[piece], p.Rect(column*SQUARESIZE, row*SQUARESIZE, SQUARESIZE, SQUARESIZE))



def animateMove(move, screen, board, clock):
    global colours
    dRow = move.endRow - move.startRow
    dColumn = move.endColumn - move.startColumn
    fps = 5
    frameCount = (abs(dRow) + abs(dColumn))*fps
    for frames in range(frameCount + 1):
        row, column = (move.startRow + dRow*frames/frameCount, move.startColumn + dColumn*frames/frameCount)
        createBoard(screen)
        createPieces(screen, board)
        colour = colours[(move.endRow + move.endColumn) % 2]
        endSquare = p.Rect(move.endColumn*SQUARESIZE, move.endRow*SQUARESIZE, SQUARESIZE, SQUARESIZE)
        p.draw.rect(screen, colour, endSquare)
        if move.pieceCaptured!= '  ':
            if move.enpassant:
                enpassantRow = move.endRow+1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endColumn*SQUARESIZE, enpassantRow*SQUARESIZE, SQUARESIZE, SQUARESIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(column*SQUARESIZE, row*SQUARESIZE, SQUARESIZE, SQUARESIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvetica", 30, True, False)
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

if __name__ == "__main__":
    main()

