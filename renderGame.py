from operator import truediv
from pickle import FALSE
from turtle import bk
import pygame
from constants import *
from main import *


class RenderGame:
    
    def __init__(self):
        #the board is a 7x8 board bc its a normal chess game where there all of the pieces except for the queen bc the queen is too op
        self.board = [
            ["bR", "bB", "bN", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wB", "wN", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'P': self.pawnMoves,'N': self.knightMoves,'B': self.bishopMoves,'R': self.rookMoves,'K': self.kingMoves}
        
        self.whiteToMove = True
        self.moveLog = []
        self.wKLocation = (6, 3)
        self.bKLocation = (0, 3)
        self.checks = []
        self.in_Check = False
        self.pins = []
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]
            
    def makeMove(self, move):
        self.board[move.startRow][move.startColumn] = "  "
        self.board[move.endRow][move.endColumn] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        #king location update
        if move.pieceMoved == 'wK':
            self.wKLocation = (move.endRow, move.endColumn)
        elif move.pieceMoved == "bK":
            self.bKLocation = (move.endRow, move.endColumn)
            
        if move.pawnPromotion:
            self.board[move.endRow][move.endColumn] = move.pieceMoved[0] + 'R'
        
        if move.enpassant:
            self.board[move.startRow][move.endColumn] = "  "
            
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2: #only on two square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startColumn)
        else:
            self.enpassantPossible=()
        
        if move.isCastleMove:
            if move.endColumn - move.startColumn == 2: 
                self.board[move.endRow][move.endColumn-1] = self.board[move.endRow][move.endColumn+1]
                self.board[move.endRow][move.endColumn+1] = "  "
            else:
                self.board[move.endRow][move.endColumn+1] = self.board[move.endRow][move.endColumn-1]
                self.board[move.endRow][move.endColumn-1] = "  "
                
        
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))
        

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()#returns element and removes the last element from that list
            self.board[move.startRow][move.startColumn] = move.pieceMoved
            self.board[move.endRow][move.endColumn] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #switches turn back to other player
            
            #king location update if move undone
            if move.pieceMoved == 'wK':
                self.wKLocation = (move.startRow, move.startColumn)
            elif move.pieceMoved == "bK":
                self.bKLocation = (move.startRow, move.startColumn)
            
            if move.enpassant:
                self.board[move.endRow][move.endColumn] = "  "
                self.board[move.startRow][move.endColumn] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endColumn)
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            
            self.castleRightsLog.pop() #get rid of new castle rights
            self.currentCastlingRights = self.castleRightsLog[-1] #set the current castle rights to the last one in the list
            
            if move.isCastleMove:
                if move.endColumn - move.startColumn == 2:
                    self.board[move.endRow][move.endColumn+1] = self.board[move.endRow][move.endColumn-1]
                    self.board[move.endRow][move.endColumn-1] = "  "
                else:
                    self.board[move.endRow][move.endColumn-1] = self.board[move.endRow][move.endColumn+1]
                    self.board[move.endRow][move.endColumn+1] = "  "

            self.checkmate = False
            self.stalemate = False
            
            
    def updateCastleRights(self, move):
        if move.pieceCaptured == 'wR':
            if move.endColumn == 0:
                self.currentCastlingRights.wqs = False
            elif move.endColumn == 6:
                self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endColumn == 0:
                self.currentCastlingRights.bqs = False
            elif move.endColumn == 6:
                self.currentCastlingRights.bks = False
                    
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 6:
                if move.startColumn == 0:
                    self.currentCastlingRights.wqs = False
                if move.startColumn == 6:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startColumn == 0:
                    self.currentCastlingRights.bqs = False
                if move.startColumn == 6:
                    self.currentCastlingRights.bks = False
    
    
    #to check if a move is illegal or not, if the move that the player does after is able to take the king, than that needs to be stopped
    def validMoves(self):#deletes all moves that result in the king being unneededly captured
        # for log in self.castleRightsLog:
        #     print(log.wks, log.wqs, log.bks, log.bqs, end=", ")
        tempEP = self.enpassantPossible
        tempCR = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        moves = []

        self.in_Check, self.pins, self.checks = self.pinsAndChecks()
        if self.whiteToMove:
            kingRow = self.wKLocation[0]
            kingColumn = self.wKLocation[1]
        else:
            kingRow = self.bKLocation[0]
            kingColumn = self.bKLocation[1]
        if self.in_Check:
            if len(self.checks) == 1:
                moves = self.possibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkColumn = check[1]
                pieceChecking = self.board[checkRow][checkColumn]
                validSquares = []
                #if its a knight, the king always has to be moved or the knight has to be taken
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkColumn)]
                else:
                    for i in range(1, 7):
                        validSquare = (kingRow + check[2] * i, kingColumn + check[3]*i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkColumn:
                            break
                #gets rid of any moves that doesnt clock the check or you can move the king
                for i in range (len(moves) -1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endColumn) in validSquares:
                            moves.remove(moves[i])
            else: #double check, king has to move
                self.kingMoves(kingRow, kingColumn, moves)
        else: #not in check soall moves are ok
            moves = self.possibleMoves()
            ####################### BRO WTF IS THIS ###############################################
            if self.whiteToMove:
                self.castleMoves(self.wKLocation[0], self.wKLocation[1], moves)
            else:
                self.castleMoves(self.bKLocation[0], self.bKLocation[1], moves)
            
        
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        
        self.enpassantPossible = tempEP
        self.currentCastlingRights = tempCR
        return moves
    
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.wKLocation[0], self.wKLocation[1])
        else:
            return self.squareUnderAttack(self.bKLocation[0], self.bKLocation[1])
        
    def squareUnderAttack(self, row, column):
        self.whiteTomove = not self.whiteToMove
        opponentMoves = self.possibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponentMoves:
            if move.endRow == row and move.endColumn == column:
                return True
        return False
    
    def possibleMoves(self):#shows all possible moves regardless of checks for the opponent
        moves = []
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                turn = self.board[row][column][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][column][1]
                    self.moveFunctions[piece](row, column, moves) #calls correct move function
        return moves
                    
    def pinsAndChecks(self):
        pins = []
        checks = []
        in_Check = False
        if self.whiteToMove:
            enemyColour = "b"
            allyColour = "w"
            startRow = self.wKLocation[0]
            startColumn = self.wKLocation[1]
        else:
            enemyColour = "w"
            allyColour = "b"
            startRow = self.bKLocation[0]
            startColumn = self.bKLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range (1, 7):
                endRow = startRow + d[0]*i
                endColumn = startColumn + d[1]*i
                if 0<= endRow < 7 and 0 <= endColumn < 7:
                    endPiece = self.board[endRow][endColumn]
                    if endPiece[0] == allyColour and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endColumn, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColour:
                        type = endPiece[1]
                        if (0<=j<=3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'P' and ((enemyColour == 'w' and 6<= j <= 7) or (enemyColour == 'b' and 4 <= j <= 5))) or \
                                (i==1 and type == 'K'):
                            if possiblePin ==():
                                in_Check = True
                                checks.append((endRow, endColumn, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                            
                        else:
                            break
                else:
                    break
        
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endColumn = startColumn + m[1]
            if 0 <= endRow < 7 and 0 <= endColumn < 7:
                endPiece = self.board[endRow][endColumn]
                if endPiece[0] == enemyColour and endPiece[1] == 'N':
                    in_Check = True
                    checks.append((endRow, endColumn, m[0], m[1]))
        return in_Check, pins, checks
    
    
    def pawnMoves(self, row, column, moves):
        piecePinned = False
        pinDirection = ()
        
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.whiteToMove:
            moveAmount = -1
            startRow = 5
            enemyColour = "b"
            kingRow, kingColumn = self.wKLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColour = "w"
            kingRow, kingColumn = self.bKLocation

        if self.board[row + moveAmount][column] == "  ":  # 1 square pawn advance
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((row, column), (row + moveAmount, column), self.board))
                if row == startRow and self.board[row + 2 * moveAmount][column] == "  ":  # 2 square pawn advance
                    moves.append(Move((row, column), (row + 2 * moveAmount, column), self.board))
        if column - 1 >= 0:  # capture to the left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[row + moveAmount][column - 1][0] == enemyColour:
                    moves.append(Move((row, column), (row + moveAmount, column - 1), self.board))
                if (row + moveAmount, column - 1) == self.enpassantPossible:
                    attacking_piece = blocking_piece = False
                    if kingRow == row:
                        if kingColumn < column:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(kingColumn + 1, column - 1)
                            outside_range = range(column + 1, 7)
                        else:  # king right of the pawn
                            inside_range = range(kingColumn - 1, column, -1)
                            outside_range = range(column - 2, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "  ":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemyColour and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "  ":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, column), (row + moveAmount, column - 1), self.board, is_enpassant_move=True))
        if column + 1 <= 7:  # capture to the right
            if not piecePinned or pinDirection == (moveAmount, +1):
                if self.board[row + moveAmount][column + 1][0] == enemyColour:
                    moves.append(Move((row, column), (row + moveAmount, column + 1), self.board))
                if (row + moveAmount, column + 1) == self.enpassantPossible:
                    attacking_piece = blocking_piece = False
                    if kingRow == row:
                        if kingColumn < column:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(kingColumn + 1, column)
                            outside_range = range(column + 2, 7)
                        else:  # king right of the pawn
                            inside_range = range(kingColumn - 1, column + 1, -1)
                            outside_range = range(column - 1, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "  ":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemyColour and (square[1] == "R"):
                                attacking_piece = True
                            elif square != "  ":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, column), (row + moveAmount, column + 1), self.board, is_enpassant_move=True))
        
    def rookMoves(self, row, column, moves):
        piecePinned = False
        pinDirection = ()
        
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break 
        
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1)) #up down left right
        if self.whiteToMove:
            enemyColour = 'b'
        else:
            enemyColour = "w"
        for d in directions:
            for i in range(1, 7):
                endRow = row + d[0]*i
                endColumn = column + d[1]*i
                if 0<= endRow<7 and 0<= endColumn <7:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        
                        endPiece = self.board[endRow][endColumn]
                        if endPiece == "  ":
                            moves.append(Move((row, column), (endRow, endColumn), self.board))
                        elif endPiece[0] == enemyColour:
                            moves.append(Move((row, column), (endRow, endColumn), self.board))
                            break
                        else:
                            break
                else: 
                    break
    
    
    def knightMoves(self, row, column, moves):
        piecePinned = False
        
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break 
        
        knightDirections = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        if self.whiteToMove:
            allyColour = 'w'
        else:
            allyColour = "b"
        for i in knightDirections:
            endRow = row+i[0]
            endColumn = column+i[1]
            if 0 <= endRow < 7 and 0<=endColumn < 7:
                if not piecePinned:
                    endPiece = self.board[endRow][endColumn]
                    if endPiece[0] != allyColour:
                        moves.append(Move((row, column), (endRow, endColumn), self.board))
            
        
    
    def bishopMoves(self, row, column, moves):
        
        piecePinned = False
        pinDirection = ()
        
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break 
            
        directions = ((-1, -1), (1, 1), (1, -1), (-1, 1)) #all different diagonals
        if self.whiteToMove:
            enemyColour = 'b'
        else:
            enemyColour = "w"
        for d in directions:
            for i in range(1, 7):
                endRow = row + d[0]*i
                endColumn = column + d[1]*i
                if 0<= endRow<7 and 0<= endColumn <7:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endColumn]
                        if endPiece == "  ":
                            moves.append(Move((row, column), (endRow, endColumn), self.board))
                        elif endPiece[0] == enemyColour:
                            moves.append(Move((row, column), (endRow, endColumn), self.board))
                            break
                        else:
                            break
                else: 
                    break
    
    
            
            
            
    def kingMoves(self, row, column, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        columnMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        if self.whiteToMove:
            allyColour = 'w'
        else:
            allyColour = "b"
        for i in range(7):
            endRow = row + rowMoves[i]
            endColumn = column + columnMoves[i]
            if 0 <= endRow < 7 and 0 <= endColumn < 7:
                endPiece = self.board [endRow][endColumn]
                if endPiece[0] != allyColour:
                    if allyColour == 'w':
                        self.wKLocation = (endRow, endColumn)
                    else: 
                        self.bKLocation = (endRow, endColumn)
                        
                    in_Check, pins, checks = self.pinsAndChecks()
                    if not in_Check:
                        moves.append(Move((row, column), (endRow, endColumn), self.board))
                    if allyColour == 'w':
                        self.wKLocation = (row, column)
                    else:
                        self.bKLocation = (row, column)
        
                        
    def castleMoves(self, row, column, moves):
        if self.squareUnderAttack(row, column):
            return #cannot castle if in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.kingSideCastleMoves(row, column, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.queenSideCastleMoves(row, column, moves)
        
    
    def kingSideCastleMoves(self, row, column, moves):
        if self.board[row][column+1] == "  " and self.board[row][column+2] == "  ":
            if not self.squareUnderAttack(row, column+1) and not self.squareUnderAttack(row, column+2):            
                    moves.append(Move((row, column), (row, column+2), self.board, isCastleMove=True))
    
    def queenSideCastleMoves(self, row, column, moves):
        if self.board[row][column-1] == "  " and self.board[row][column-2] == "  ":
            if not self.squareUnderAttack(row, column-1) and not self.squareUnderAttack(row, column-2):            
                    moves.append(Move((row, column), (row, column-2), self.board, isCastleMove=True))
                        
    
            
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs): #(even though there is no queen, queenside will be left for white and right for black and king will be the opposite side of queenside)
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    ranksToRows = {"1":6, "2":5,"3":4,"4":3,"5":2,"6":1,"7":0,}
    rowsToRanks = {v:k for k, v in ranksToRows.items()} #reverses the list
    filesToColumns = {"g":6,"f":5,"e":4,"d":3,"c":2,"b":1,"a":0}
    columnsToFiles = {v:k for k, v in filesToColumns.items()}
    
    def __init__(self, startSquare, endSquare, board, enpassant = False, isCastleMove = False):
        self.startRow = startSquare[0]
        self.startColumn = startSquare[1]
        self.endRow = endSquare[0]
        self.endColumn = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startColumn]
        self.pieceCaptured = board[self.endRow][self.endColumn]
        self.pawnPromotion = False
        if (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 6):
            self.pawnPromotion == True
        self.enpassant = enpassant
        if self.enpassant:
            if self.pieceMoved == "bP":
                self.pieceCaptured = 'wP'
            else:
                self.pieceCaptured = 'bP'
        self.isCastleMove = isCastleMove
            
            
            
        self.moveID = self.startRow * 1000 + self.startColumn *100 + self.endRow * 10 + self.endColumn
    
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def chessPosition(self):
        return self.getPosition(self.startRow, self.startColumn) + self.getPosition(self.endRow, self.endColumn)
    
    def getPosition(self, row, column):
        return self.columnsToFiles[column] + self.rowsToRanks[row]