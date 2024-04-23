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
        self.whiteToMove= True
        self.moveLog=[]

    def make_move(self,move):
        self.board[move.startRow][move.startCol]= '--'
        self.board[move.endRow][move.endCol]=move.piece_moved_from
        self.moveLog.append(move)
        self.whiteToMove= not self.whiteToMove

    def valid_move(self ):
        if len(self.moveLog)!=0:
            move=self.moveLog.pop() 
            self.board[move.startRow][move.startCol]=move.piece_moved_from
            self.board[move.endRow][move.endCol]=move.piece_captured_at
            return False

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

    def get_chess_notation(self):
        return self.get_rank_file(self.startRow,self.startCol)+self.get_rank_file(self.endRow,self.endCol)
    
    def get_rank_file(self,r,c):
        return self.cols_to_files[c]+self.rows_to_ranks[r]
    
