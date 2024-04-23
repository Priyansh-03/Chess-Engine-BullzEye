import pygame as p
import chessEngine

width = height = 512  # or 400
dimension = 8  # dimension of chess board is 8x8
square_size = height // dimension

maxfps = 15  # for animations

images = {}


def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wp", "wR", "wN", "wK", "wQ", "wB"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (square_size, square_size))


def main():
    p.init()
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    game_state = chessEngine.GameState()
    load_images()
    running = True
    sq_selected=() # no square is selected , keep track of the last click of the user (tuple : (row,cell))
    playerClicks=[] # keep track of player clicks (two tuples: [(6,4),(4,4)])
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                '''
                Suppose:

                square_size = 64 (each square on the chessboard is 64 pixels wide and 64 pixels tall).
                The user clicks at position (150, 250) on the screen.
                Now, let's calculate the row and column of the chessboard square that was clicked:

                location = p.mouse.get_pos(): Retrieves the mouse position (150, 250).
                col = location[0] // square_size: Calculates the column index:
                col = 150 // 64 = 2 (since integer division truncates decimals).
                row = location[1] // square_size: Calculates the row index:
                row = 250 // 64 = 3.
                So, the user clicked on the square at row 3, column 2 of the chessboard.
                '''
                location=p.mouse.get_pos() # x,y location of mouse
                col=location[0]//square_size 
                row=location[1]//square_size
                # sq_selected=(row,col)
                print(playerClicks, sq_selected)
                if sq_selected==(row,col): #if it is a double-click
                    sq_selected = () #deselect
                    playerClicks=[]

                else:    
                    sq_selected=(row,col)
                    playerClicks.append(sq_selected) # append for both 1st and 2nd click
                    # print("\nat line 60\n")
                if len(playerClicks)==2:
                    # print("at line 62")
                    move=chessEngine.Move(playerClicks[0],playerClicks[1],game_state.board)
                    print(move.get_chess_notation())
                    game_state.make_move(move)
                    sq_selected=() # reset user click
                    playerClicks=[]

        drawGameState(screen, game_state)
        clock.tick(maxfps)
        p.display.flip()


def drawGameState(screen, game_state):
    '''
    Responsible for all the graphics within current game state.
    Top left square will always be white
    '''
    drawBoard(screen)  # Draw squares
    drawPieces(screen, game_state.board)  # Draw pieces


def drawBoard(screen):
    '''
    Draw squares on board
    '''
    colors = [(255, 255, 255, 128), (128, 128, 128, 128)]  # Transparent white and transparent gray
    for r in range(dimension):
        for c in range(dimension):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * square_size, r * square_size, square_size, square_size))


def drawPieces(screen, board):
    '''
    Draw Pieces on board
    '''
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(images[piece], p.Rect(c * square_size, r * square_size, square_size, square_size))


if __name__ == "__main__":
    main()
