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