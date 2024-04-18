'''
This is the main file. 
Responsible for handeling user input and current Game state object.
'''
import pygame as p
import chessEngine

width=height=512 #or 400
dimension= 8 # dimension of chess board is 8x8
square_size=height//dimension

maxfps=15 # for animations

images={

}

'''
Initialize global dictionary for images and it will be calledc only once
'''

def load_images():
    pieces=["bR" , "bN" , "bB" , "bQ" , "bK", "bp", "wp", "wR", "wN", "wK", "wQ", "wB"]
    for piece in pieces:
        images[piece]=p.transform.scale(p.image.load("images/"+piece+".png"),(square_size,square_size))

def main():
    p.init()
    screen=p.display.set_mode((width,height))
    clock=p.time.Clock()
    screen.fill(p.Color('white'))
    gs=chessEngine.GameState()
    load_images()
    running=True

    while running:
        for e in p.event.get():
            if e.type==p.QUIT:
                running=False
        drawGameState(screen,gs)
        clock.tick(maxfps)
        p.display.flip()

def drawGameState(screen,gs):
    '''
    Responsible for all the graphics within current game state.
    Top left square will always be white
    '''
    drawBoard(screen) # Draw squares
    drawPieces(screen,gs.board) # Draw pieces

def drawBoard(screen):
    '''
    Draw squares on board
    '''
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(dimension):
        for c in range(dimension):
            color=colors[((r+c)%2)]
            p.draw.rect(screen,color,p.Rect(c*square_size,r*square_size,square_size,square_size))

def drawPieces(screen,board):
    '''
    Draw Pieces on board
    '''
    for r in range(dimension):
        for c in range(dimension):
            piece=board[r][c]
            if piece != "--": #not empty square
                screen.blit(images[piece],p.Rect(c*square_size,r*square_size,square_size,square_size))




if __name__=="__main__":
    main()