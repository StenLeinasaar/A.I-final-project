import pygame
import sys
from pygame.locals import *
from game_board import Board
sys.path.append("/Users/stenleinasaar/Desktop/A.I-final-project/ai_players")
from alpha_beta_pruning import alpha_beta_pruning
from sarsa_agent import SarsaAgent
import os
from q_learning import QLearning

pygame.init()

PLTYP1 = 'human'
PLTYP2 = 'q-learning'

sarsa_player_one = SarsaAgent(weights=[-18, -18, 0.38326323200000023, -0.6448000000000005, -18, -18, 18, 18, -0.03990640383383198, -0.20010044800514182])
sarsa_player_two = SarsaAgent(weights=[18, -18, -2.156316160000002, 2.120000000000001, -18, -18, 18, -18, -4.1794220451862873e-05, -0.4332209069536925])

q_player_one = QLearning(weights=[18, -18, 18, 18, -18, 18, -18, 18, 0.07980480000000104, -0.2519999934689009] )
q_player_two = QLearning(weights=[18, -18, 18, -6.044169600000005, -18, -18, -18, -18, -0.036000236644109146, -0.19529999996772648])

white = (255,255,255)
black = (0,0,0)
red = (175,0,0)
green = (0,120,0)
lightgreen = (0,175,0)
bg = (32,32,32,255)
games_played = 0

PLAYER1 = 1
PLAYER2 = 2

img_board = pygame.image.load('./sources/pics/board.png')
img_black_stone = pygame.image.load('./sources/pics/stone_black.png')
image_white_stone = pygame.image.load('./sources/pics/stone_white.png')


fps = 5

display_width = 900
display_height = 645

line_width = 1
line_width2 = 4
line_width3 = 4
box_width = 40

margin_width = 24

N = 15
number_to_win = 5 ##

board_width = line_width*N+box_width*(N-1)

starty = (display_height-board_width)/2
startx = starty+0

info_x_position = 2*margin_width+board_width+48
info_y_position1= startx+margin_width+(line_width+box_width)*1
info_y_position2 = info_y_position1+(line_width+box_width)*4
info_width = (line_width+box_width)*4
info_height = (line_width+box_width)*3
background_width = (display_width-info_x_position)-1

stone_size= 29

player_info1 = {'score': 0}
player_info2 = {'score': 0}

            
def update_info(info1,info2,player):

    # Handle drawing whose turn it is
    if player == PLAYER1:
        pygame.draw.rect(set_display, lightgreen, (info_x_position+2,info_y_position1+2,info_width-1,info_height-1), line_width3)
        pygame.draw.rect(set_display, black, (info_x_position+2,info_y_position2+2,info_width-1,info_height-1), line_width3)
    else:
        pygame.draw.rect(set_display, lightgreen, (info_x_position+2,info_y_position2+2,info_width-1,info_height-1), line_width3)
        pygame.draw.rect(set_display, black, (info_x_position+2,info_y_position1+2,info_width-1,info_height-1), line_width3)

    title_text_font = pygame.font.SysFont('Calibri', 24)
    score_text_font = pygame.font.SysFont('Calibri', 20)
    
    ##### Set the player 1 Information ###########
    title = 'Player 1'
    text_score = 'Score: %d' %info1['score']

    text_surface, textRect = make_text_objects(title, title_text_font, red)
    textRect.center = (int(info_x_position+info_width/2), int(info_y_position1+info_height/2)-30)
    set_display.blit(text_surface, textRect)

    text_surface, textRect = make_text_objects(text_score, score_text_font, green)
    textRect.center = (int(info_x_position+info_width/2), int(info_y_position1+info_height/2))
    set_display.blit(text_surface, textRect)


    #####  Set player 2 information  ########

    title = 'Player 2'
    text_score = 'Score: %d' %info2['score']

    text_surface, textRect = make_text_objects(title, title_text_font, red)
    textRect.center = (int(info_x_position+info_width/2), int(info_y_position2+info_height/2)-30)
    set_display.blit(text_surface, textRect)

    text_surface, textRect = make_text_objects(text_score, score_text_font, green)
    textRect.center = (int(info_x_position+info_width/2), int(info_y_position2+info_height/2))
    set_display.blit(text_surface, textRect)
    


def check_next():
    for event in pygame.event.get([KEYDOWN, KEYUP, QUIT]):
        if event.type == QUIT:
            # print_weights()
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            print("key down was pressed")
            continue
        return event.key
    return None

def make_text_objects(text, font, tcolor):
    text_surface = font.render(text, True, tcolor)
    return text_surface, text_surface.get_rect()

def message_surface(player, text_color):

    # darkenBackground()
    
    small_text = pygame.font.SysFont('Calibri', 30)
    large_text = pygame.font.SysFont('Calibri', 65)

    if player == PLAYER1:
        text = 'Player 1 (black) Wins!'
    else:
        text = 'Player 2 (white) Wins!'

    title_text_surface, title_text_rectangle = make_text_objects(text, large_text, text_color)
    title_text_rectangle.center = (int(display_width/2), int(display_height/2))
    set_display.blit(title_text_surface, title_text_rectangle)

    typTextSurf, typTextRect = make_text_objects('Press any key to play again....', small_text, white)
    typTextRect.center = (int(display_width/2), int(display_height/2)+120)
    set_display.blit(typTextSurf, typTextRect)
    pygame.display.update()


    while check_next() == None:
        for event in pygame.event.get([QUIT]):
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
    runGame()

def runGame():

    theWinner = 0
    current_player = PLAYER1

    

    set_display.blit(img_board, (0,0))
    update_info(player_info1, player_info2, current_player)
    
    pygame.display.update()

    gomoku_board = Board()

    # Main loop
    while True: 
        while theWinner == 0:
            for event in pygame.event.get(): 
                if event.type == QUIT:
                    # print_weights()
                    pygame.quit()
                    sys.exit()

            # players play in turn
            if current_player == PLAYER1 and PLTYP1 == 'human':
                row, col = get_piece_position()
                while not gomoku_board.is_valid((row, col)):
                    row, col = get_piece_position()
                    
            elif current_player == PLAYER2 and PLTYP2 == 'human':
                row, col = get_piece_position()
                while not gomoku_board.is_valid((row, col)):
                    row, col = get_piece_position()

            elif current_player == PLAYER2 and PLTYP2 == 'alpha-beta':
                row, col = alpha_beta_pruning(gomoku_board, current_player)
            elif current_player == PLAYER1 and PLTYP1 == 'alpha-beta':
                row,col = alpha_beta_pruning(gomoku_board, current_player)
            elif current_player == PLAYER2 and PLTYP2 == 'sarsa':
                row, col = sarsa_player_two.get_move(gomoku_board, current_player)
                # print(f"{row}, {col}")
            elif current_player == PLAYER1 and PLTYP1=='sarsa':
                row, col = sarsa_player_one.get_move(gomoku_board, current_player)
            elif current_player == PLAYER2 and PLTYP2 == 'q-learning':
                row, col = q_player_two.get_move(gomoku_board, current_player)
                # print(f"{row}, {col}")
            elif current_player == PLAYER1 and PLTYP1=='q-learning':
                row, col = q_player_one.get_move(gomoku_board, current_player)
                
                    
            # add new piece
            gomoku_board.play(current_player,(row, col))
            # gomoku_board[row][col] = current_player
            theWinner = gomoku_board.is_win(current_player)#check_winner(gomoku_board, current_player)
            draw_piece((row, col), current_player)
 
            # Change the player
            if current_player == PLAYER1:
                current_player = PLAYER2
            else:
                current_player = PLAYER1


            # update the board and update the display.
            update_info(player_info1, player_info2, current_player)
            pygame.display.update()

        # print('Winner: Player', theWinner)
        # gomoku_board.print_board()
        if theWinner == PLAYER1:
            player_info1['score'] += 1
            # sarsa_player_one.game_over(gomoku_board, current_player)
            # sarsa_player_two.game_over(gomoku_board, current_player )

        else:
            player_info2['score'] += 1
            # sarsa_player_one.game_over(gomoku_board, current_player)
            # sarsa_player_two.game_over(gomoku_board, current_player )
        
        message_surface(theWinner, green)



def draw_piece(indice, player):
    x = startx+line_width/2+indice[1]*(line_width+box_width)-(stone_size-1)/2
    y = starty+line_width/2+indice[0]*(line_width+box_width)-(stone_size-1)/2

    if player == PLAYER1:
        set_display.blit(img_black_stone, (x,y))
    else:
        set_display.blit(image_white_stone, (x,y))

def get_piece_position():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()

                row = int(round((y-starty-line_width/2.0)/(line_width+box_width)))
                col = int(round((x-startx-line_width/2.0)/(line_width+box_width)))
                
                return row, col
def print_weights():
    file_number = 0
    # prints the weights to the file
    filename = f"weights_{file_number}"
    print("file about to be written", filename)
    if os.path.exists(f"Game_logic/{filename}"):
        file_stat = os.stat(filename)
        if file_stat.st_size() > 100000000:
            file_number += 1
            filename = f"weights_{file_number}"
            
        
    with open(filename, 'a') as file:
        file.write("player 1 weights")
        file.write(str(sarsa_player_one.weights))
        file.write("  ")
        file.write("player 2 weights")
        file.write(str(sarsa_player_two.weights))
        file.write("  ")
        file.write(f"Player1 score: {player_info1.get('score')}")
        file.write("  ")
        file.write(f"Player2 score: {player_info2.get('score')}")
        file.write("\n")


while True:
    global set_display

    point1 = 0
    point2 = 0
    
    set_display = pygame.display.set_mode((display_width,display_height))
    pygame.display.set_caption('Gomoku')


    runGame()