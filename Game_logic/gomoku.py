import pygame
import sys
import random
import re
from pygame.locals import *

pygame.init()

PLTYP1 = 'human'
PLTYP2 = 'human'

play_music = True
play_sound = True

# T_MAX = 60
# T_MIN = 0.1

white = (255,255,255)
black = (0,0,0)
red = (175,0,0)
green = (0,120,0)
lightgreen = (0,175,0)
bg = (32,32,32,255)

PLAYER1 = 1
PLAYER2 = 2

fp = './sources/'

img_board = pygame.image.load(fp+'pics/board.png')
img_cp1 = pygame.image.load(fp+'pics/cp_k_29.png')
img_cp2 = pygame.image.load(fp+'pics/cp_w_29.png')
img_panel = pygame.image.load(fp+'pics/panel.png')
img_icon = pygame.image.load(fp+'pics/catsmall.png')
pygame.display.set_icon(img_icon)

fps = 10

dispWidth = 900
dispHeight = 645

lineWidth = 1
lineWidth2 = 4
lineWidth3 = 4
boxWidth = 40

marginWidth = 24

N = 15
n_win = 5 ##

boardWidth = lineWidth*N+boxWidth*(N-1)

starty = (dispHeight-boardWidth)/2
startx = starty+0

infox = 2*marginWidth+boardWidth+48
infoy1 = startx+marginWidth+(lineWidth+boxWidth)*1
infoy2 = infoy1+(lineWidth+boxWidth)*4
infoWidth = (lineWidth+boxWidth)*4
infoHeight = (lineWidth+boxWidth)*3
bgWidth = (dispWidth-infox)-1

cpSize = 29

plyrInfo1 = {'score': 0, 'time': 0}
plyrInfo2 = {'score': 0, 'time': 0}

def hex2rgb(pxValue):
    print("I made it do the hex to rgb method")
    print(f"pixel value is {pxValue}")
    v = pxValue//256
    print(f'value of v is {v}')
    b = (pxValue-v)*256
    print(f'value for b is {b}')
    pxValue = v
    print(f'new pxValues is {pxValue}')
    v = pxValue//256
    g = (pxValue-v)*256
    pxValue = v
    v = pxValue//256
    r = (pxValue-v)*256
    print(f'Before returning—value for r: {r}, g: {g}, b: {b}')
    return r, g, b


            
def updateInfo(info1,info2,plyr):

    setDisplay.blit(img_panel, (infox,0))
    if plyr == PLAYER1:
        pygame.draw.rect(setDisplay, lightgreen, (infox+2,infoy1+2,infoWidth-1,infoHeight-1), lineWidth3)
    else:
        pygame.draw.rect(setDisplay, lightgreen, (infox+2,infoy2+2,infoWidth-1,infoHeight-1), lineWidth3)

    ttlText = pygame.font.SysFont('Calibri', 24)
    scoreText = pygame.font.SysFont('Calibri', 20)
    timeText = pygame.font.SysFont('Calibri', 20)
    
    textttl = 'Player 1'
    textsc = 'Score: %d' %info1['score']
    texttm = 'Time: %.2f s' %info1['time']
    textSurf, textRect = makeTextObjs(textttl, scoreText, red)
    textRect.center = (int(infox+infoWidth/2), int(infoy1+infoHeight/2)-30)
    setDisplay.blit(textSurf, textRect)
    textSurf, textRect = makeTextObjs(textsc, scoreText, green)
    textRect.center = (int(infox+infoWidth/2), int(infoy1+infoHeight/2))
    setDisplay.blit(textSurf, textRect)
    textSurf, textRect = makeTextObjs(texttm, scoreText, white)
    textRect.center = (int(infox+infoWidth/2), int(infoy1+infoHeight/2)+26)
    setDisplay.blit(textSurf, textRect)

    textttl = 'Player 2'
    textsc = 'Score: %d' %info2['score']
    texttm = 'Time: %.2f s' %info2['time']
    textSurf, textRect = makeTextObjs(textttl, scoreText, red)
    textRect.center = (int(infox+infoWidth/2), int(infoy2+infoHeight/2)-30)
    setDisplay.blit(textSurf, textRect)
    textSurf, textRect = makeTextObjs(textsc, scoreText, green)
    textRect.center = (int(infox+infoWidth/2), int(infoy2+infoHeight/2))
    setDisplay.blit(textSurf, textRect)
    textSurf, textRect = makeTextObjs(texttm, scoreText, white)
    textRect.center = (int(infox+infoWidth/2), int(infoy2+infoHeight/2)+26)
    setDisplay.blit(textSurf, textRect)

def whatNext():
    for event in pygame.event.get([KEYDOWN, KEYUP, QUIT]):
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            continue
        return event.key
    return None

def makeTextObjs(text, font, tcolor):
    textSurface = font.render(text, True, tcolor)
    return textSurface, textSurface.get_rect()

def msgSurface(plyr, textColor):

    # darkenBackground()
    
    smallText = pygame.font.SysFont('Calibri', 30)
    largeText = pygame.font.SysFont('Calibri', 65)

    if plyr == PLAYER1:
        text = 'Player 1 (black) Wins!'
    else:
        text = 'Player 2 (white) Wins!'

    titleTextSurf, titleTextRect = makeTextObjs(text, largeText, textColor)
    titleTextRect.center = (int(dispWidth/2), int(dispHeight/2))
    setDisplay.blit(titleTextSurf, titleTextRect)

    typTextSurf, typTextRect = makeTextObjs('Press any key to play again....', smallText, white)
    typTextRect.center = (int(dispWidth/2), int(dispHeight/2)+120)
    setDisplay.blit(typTextSurf, typTextRect)
    pygame.display.update()


    while whatNext() == None:
        for event in pygame.event.get([QUIT]):
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
    runGame()

def runGame():

    theWinner = 0
    currPlayer = PLAYER1

    

    setDisplay.blit(img_board, (0,0))
    updateInfo(plyrInfo1, plyrInfo2, currPlayer)
    
    pygame.display.update()

    chessMat = []
    for dummy_iy in range(N):
        chessMat.append([0 for dummy_idx in range(N)])


    while True: # main game loop
        # While there is no winner.
        while theWinner == 0:
            # Event handling loop.
            for event in pygame.event.get(): 
                # When they quit.
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            # players play in turn
            if currPlayer == PLAYER1 and PLTYP1 == 'human':
                row, col = getPiecePos()
                while not isValid((row, col), chessMat):
                    row, col = getPiecePos()
                    
            elif currPlayer == PLAYER2 and PLTYP2 == 'human':
                row, col = getPiecePos()
                while not isValid((row, col),chessMat):
                    row, col = getPiecePos()
                    
            # add new piece
            chessMat[row][col] = currPlayer
            theWinner = checkIfWins(chessMat, currPlayer)
            drawPiece((row, col), currPlayer)
 
            # Change the player
            if currPlayer == PLAYER1:
                currPlayer = PLAYER2
            else:
                currPlayer = PLAYER1


            # update the board and update the display.
            updateInfo(plyrInfo1, plyrInfo2, currPlayer)
            pygame.display.update()

        print('Winner: Player', theWinner)
        printMat(chessMat)
        if theWinner == PLAYER1:
            plyrInfo1['score'] += 1
        else:
            plyrInfo2['score'] += 1
        
        msgSurface(theWinner, green)

def printMat(mat):
    for bdraw in mat:
        print(bdraw)
    print('=' * 45)

def drawPiece(indice, player):
    x = startx+lineWidth/2+indice[1]*(lineWidth+boxWidth)-(cpSize-1)/2
    y = starty+lineWidth/2+indice[0]*(lineWidth+boxWidth)-(cpSize-1)/2

    if player == PLAYER1:
        setDisplay.blit(img_cp1, (x,y))
    else:
        setDisplay.blit(img_cp2, (x,y))

def getPiecePos():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()

                row = int(round((y-starty-lineWidth/2.0)/(lineWidth+boxWidth)))
                col = int(round((x-startx-lineWidth/2.0)/(lineWidth+boxWidth)))
                
                return row, col

def isValid(indice, mat):
    
    newRow = indice[0]
    newCol = indice[1]

    if newRow < 0 or newRow > N-1:
        return False
    elif newCol < 0 or newCol > N-1:
        return False

    return mat[newRow][newCol] == 0

def sysIndexGen(mat, player):
    for row in range(N):
        for col in range(N):
            if mat[row][col] == 0:
                return row, col

# Main Logic to check for winner.
def checkIfWins(mat, player):
    flag = 'x'
    # rows:
    for row in range(N):
        s_row = ''
        for col in range(N):
            if mat[row][col] == player:
                s_row += flag
            else:
                s_row += '0'
        isMatch = re.search(flag*n_win,s_row)
        if isMatch != None:
            return player
        
    # cols:
    for col in range(N):
        s_col = ''
        for row in range(N):
            if mat[row][col] == player:
                s_col += flag
            else:
                s_col += '0'
        isMatch = re.search(flag*n_win,s_col)
        if isMatch != None:
            return player

    # (0,0) --> (1,1):
    for k in range(n_win-1,N,1):
        s_line = ''
        xs = range(0,k+1)
        for x in xs:
            y = k - x
            if mat[y][N-1-x] == player:
                s_line += flag
            else:
                s_line += '0'
        isMatch = re.search(flag*n_win,s_line)
        if isMatch is not None:
            return player
    for k in range(N,2*(N-1)-(n_win-1)+1,1):
        s_line = ''
        xs = range(k-(N-1),N)
        for x in xs:
            y = k - x
            if mat[y][N-1-x] == player:
                s_line += flag
            else:
                s_line += '0'
        isMatch = re.search(flag*n_win,s_line)
        if isMatch != None:
            return player

    # (1,0) --> (0,1):
    for k in range(n_win-1,N,1):
        s_line = ''
        xs = range(0,k+1)
        for x in xs:
            y = k - x
            if mat[y][x] == player:
                s_line += flag
            else:
                s_line += '0'
        isMatch = re.search(flag*n_win,s_line)
        if isMatch is not None:
            return player
    for k in range(N,2*(N-1)-(n_win-1)+1,1):
        s_line = ''
        xs = range(k-(N-1),N)
        for x in xs:
            y = k - x
            if mat[y][x] == player:
                s_line += flag
            else:
                s_line += '0'
        isMatch = re.search(flag*n_win,s_line)
        if isMatch != None:
            return player
        
    return 0

while True:
    global cpSound
    global setDisplay

    point1 = 0
    point2 = 0
    
    setDisplay = pygame.display.set_mode((dispWidth,dispHeight))
    pygame.display.set_caption('Gomoku')

    if play_music:
        pygame.mixer.pre_init(44100)
        bgSound = pygame.mixer.Sound(fp+'music/BackgroundMusic.ogg')
        bgSound.set_volume(3)
        bgSound.play(-1)
    if play_sound:
        pygame.mixer.pre_init(44100)
        cpSound = pygame.mixer.Sound(fp+'music/Snd_click.ogg')
        cpSound.set_volume(12)

    runGame()