'''
This class is responsible for all infomation about current state of game.
Also responsible for valid moves at the current state with a move log.
'''
class GameState():
    def __init__(self):
        '''
        The first letter represent color of the piece:
            'b' -  black, 'w' - white
         
        and the second one - type of the piece:
            'B' - Bishop, 'N' - Knight, 'R' - Rook, 'Q' - Queen, 'K' - King, 'p' - Pawn
        '''

        #can use numpy for Ai and optimized
        self.board = [ 
            ["bR" , "bN" , "bB" , "bQ" , "bK" , "bB" , "bN" , "bR"],
            ["bp" , "bp" , "bp" , "bp" , "bp" , "bp" , "bp" , "bp" ],
            ["--" , "--" , "--" , "--" , "--" , "--" , "--" , "--"],
            ["--" , "--" , "--" , "--" , "--" , "--" , "--" , "--"],
            ["--" , "--" , "--" , "--" , "--" , "--" , "--" , "--"],
            ["--" , "--" , "--" , "--" , "--" , "--" , "--" , "--"],
            ["wp" , "wp" , "wp" , "wp" , "wp" , "wp" , "wp" , "wp" ],
            ["wR" , "wN" , "wB" , "wQ" , "wK" , "wB" , "wN" , "wR"]
            
        ]

        self.moveFunctions={
            'p':self.getPawnMoves,
            'R':self.getRookMoves,
            'N':self.getKnightMoves,
            'B':self.getBishopMoves,
            'Q':self.getQueenMoves,
            'K':self.getKingMoves
        }

        self.whiteToMove= True
        self.moveLog=[]
        self.whiteKingLocation=(7,4)
        self.blackKingLocation=(0,4)
        self.checkMate=False
        self.staleMate=False


    def make_move(self,move):
        ''''
        Takes move as parameter and executes it 
        Exception --> This will not work for Casteling and en-passant
        '''
        self.board[move.startRow][move.startCol]= '--'
        self.board[move.endRow][move.endCol]=move.piece_moved_from
        self.moveLog.append(move)
        self.whiteToMove= not self.whiteToMove
        # update king's location if moved
        if move.piece_moved_from=="wK":
            self.whiteKingLocation=(move.endRow,move.endCol)
        elif move.piece_moved_from=="bK":
            self.whiteKingLocation=(move.endRow,move.endCol)

    
    def undoMove(self):
        if len(self.moveLog) != 0:
            move=self.moveLog.pop()
            self.board[move.startRow][move.startCol]=move.piece_moved_from
            self.board[move.endRow][move.endCol]=move.piece_captured_at
            self.whiteToMove=not self.whiteToMove
            # update king's location if needed
            if move.piece_moved_from=="wK":
                self.whiteKingLocation=(move.startRow,move.startCol)
            elif move.piece_moved_from=="bK":
                self.whiteKingLocation=(move.startRow,move.startCol)
 


    def valid_move(self ):
        if len(self.moveLog)!=0:
            move=self.moveLog.pop() 
            self.board[move.startRow][move.startCol]=move.piece_moved_from
            self.board[move.endRow][move.endCol]=move.piece_captured_at
            return False
        

    def get_valid_move(self):
        # steps
        # 1) generate all the moves, wether valid or not
        moves=self.get_all_possible_moves()
        # 2) for each move, make move
        for i in range(len(moves)-1,-1,-1):
            self.make_move(moves[i])
            # 3) generate all oponent Move --> in squareUnderAttack()
        
            # 4) for each of the opponent's move , see if they attack your king --> in squareUnderAttack()
            self.whiteToMove=not self.whiteToMove

            # 5) if they do attack your king, not a vild move
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove=not self.whiteToMove
            self.undoMove()
        if len(moves)==0:
            if self.inCheck():
                self.checkMate=True
            else:
                self.staleMate=True
        else:
            self.checkMate=False
            self.staleMate=False
        return moves


    def inCheck(self):
        '''
        Determines if current player is in check
        '''
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
    
    def squareUnderAttack(self,r,c):
        '''
        determine if the enemy can attack the square r,c
        '''
        self.whiteToMove= not self.whiteToMove # switch to opponent turn
        oppMoves=self.get_all_possible_moves() 
        self.whiteToMove=not self.whiteToMove # switch the turn back
        for move in oppMoves:
            if move.endRow==r and move.endCol==c: # square is under attack
                return True
        return False


    def get_all_possible_moves(self):
        moves=[]
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn=self.board[r][c][0]
                if (turn=='w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece=self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves
    

    def getPawnMoves(self,r,c,moves):
        '''
        get all the pawn moves for the pawn located at row, col, and add these moves to the list
        '''
        if self.whiteToMove:
            if self.board[r-1][c]=="--": # 1 square pawn advance
                moves.append(Move((r,c),(r-1,c),self.board))
                if r==6 and self.board[r-2][c]=="--":# 2 square pawn advance
                    moves.append(Move((r,c),(r-2,c),self.board)) 
                    # print("Pawn Moved")
            
            if c-1>=0: # capture at left
                if self.board[r-1][c-1][0]=='b':# check enemy piece to capture
                    moves.append(Move((r,c),(r-1,c-1),self.board))
                    # print("White Pawn captured enemy at left")

            if c+1<=7: # capture at right
                if self.board[r-1][c+1][0]=='b':# check enemy piece to capture
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                    # print("White Pawn captured enemy at right")

        else: #black pawn
            if self.board[r+1][c]=="--": #square move
                moves.append(Move((r,c),(r+1,c),self.board))
                if r==1 and self.board[r+2][c]=="--": # 2 square move
                    moves.append(Move((r,c),(r+2,c),self.board))
                
                #captures
                if c-1>=0: # captures to left
                    if self.board[r+1][c-1][0]=='w':
                        moves.append(Move((r,c),(r+1,c-1),self.board))
                        # print("Black Pawn captured enemy at left")
                if c+1<=7: # captures to right
                    if self.board[r+1][c+1][0]=='w':
                        moves.append(Move((r,c),(r+1,c+1),self.board))
                        # print("Black Pawn captured enemy at right")
                #add pawn promotion
  
    def getRookMoves(self,r,c,moves):
        '''
        get all the rook moves for the pawn located at row, col, and add these moves to the list
        '''
        directions=((-1,0),(0,-1),(1,0),(0,1)) # up ,left, down ,right
        enemyColor="b" if self.whiteToMove else "w"

        for d in directions:
            for i in range(1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8: # on board
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--": # empty space valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        # print("rook moved")
                    elif endPiece[0]==enemyColor: # enemy piece valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        # print("rook captured enemy")
                        break
                    else : # friendly pieces invalid
                        break
                else: # off board
                    break

    def getKnightMoves(self,r,c,moves):
        '''
        get all the Kingt moves for the pawn located at row, col, and add these moves to the list
        '''
        knightMoves=((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        allyColor="w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow=r+m[0]
            endCol=c+m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece= self.board[endRow][endCol]
                if endPiece[0] != allyColor: # enemy or empty , then it is valid
                    moves.append(Move((r,c),(endRow,endCol),self.board))

    def getBishopMoves(self,r,c,moves):
        '''
        get all the Bishop moves for the pawn located at row, col, and add these moves to the list
        '''
        directions=((-1,-1),(-1,1),(1,-1),(1,1)) # 4 diagonals
        enemyColor="b" if self.whiteToMove else "w"

        for d in directions:
            for i in range(1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8: # on board
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--": # empty space valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        # print("rook moved")
                    elif endPiece[0]==enemyColor: # enemy piece valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        # print("rook captured enemy")
                        break
                    else : # friendly pieces invalid
                        break
                else: # off board
                    break

        pass
    
    def getQueenMoves(self,r,c,moves):
        '''
        get all the Queen moves for the pawn located at row, col, and add these moves to the list --> uses abstraction method
        '''
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    def getKingMoves(self,r,c,moves):
        '''
        get all the King moves for the pawn located at row, col, and add these moves to the list
        '''
        kingMoves=((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        allyColor="w" if self.whiteToMove else "b"
        for i in range(8):
            endRow=r+kingMoves[i][0]
            endCol=c+kingMoves[i][1]
            if 0 <= endRow < 8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0] !=allyColor: # not an ally piece or empty is valid
                    moves.append(Move((r,c),(endRow,endCol),self.board)) 




class Move():

    # Maping rows and columns to numbers
    ranks_to_rows={
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 0
    }
    rows_to_ranks={v:k for k,v in ranks_to_rows.items()}

    files_to_cols = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3,
    "E": 4,
    "F": 5,
    "G": 6,
    "H": 7
    }

    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self,start_sq,end_sq,board):
        self.startRow =start_sq[0]
        self.startCol =start_sq[1]
        self.endRow =end_sq[0]
        self.endCol =end_sq[1]
        self.piece_moved_from = board[self.startRow] [self.startCol]
        self.piece_captured_at = board[self.endRow][self.endCol]
        self.moveID=self.startRow * 1000 + self.startCol *100 +self.endRow*10+self.endCol
        print("Move ID = ", self.moveID)


    def __eq__(self,other):
        '''
        overriding the equals method
        '''
        if isinstance(other,Move):
            return self.moveID==other.moveID
        return False


    def get_chess_notation(self):
        return self.get_rank_file(self.startRow,self.startCol)+self.get_rank_file(self.endRow,self.endCol)
    
    def get_rank_file(self,r,c):
        return self.cols_to_files[c]+self.rows_to_ranks[r]
    
