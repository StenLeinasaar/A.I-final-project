import os
import sys
from game_board import Board
sys.path.append("../ai_players")
from sarsa_agent import SarsaAgent


PLTYP1 = 'sarsa'
PLTYP2 = 'sarsa'

sarsa_player_two = SarsaAgent()
sarsa_player_one = SarsaAgent()

PLAYER1 = 1
PLAYER2 = 2

player_one_score = 0
player_two_score = 0



def play_gomoku():
    global player_one_score, player_two_score
    gomoku_board = Board()
    current_player = PLAYER1
    theWinner = 0

    # Main loop
    while True: 
        while theWinner == 0:
            # players play in turn
            if current_player == PLAYER2 and PLTYP2 == 'sarsa':
                row, col = sarsa_player_two.get_move(gomoku_board, current_player)
            elif current_player == PLAYER1 and PLTYP1=='sarsa':
                row, col = sarsa_player_one.get_move(gomoku_board, current_player)
                
            # check winner
            theWinner = gomoku_board.is_win(current_player)
            gomoku_board.play(current_player, (row,col))
 
            # Change the player
            if current_player == PLAYER1:
                current_player = PLAYER2
            else:
                current_player = PLAYER1

        # print('Winner: Player', theWinner)
        # gomoku_board.print_board()
        if theWinner == PLAYER1:
            player_one_score += 1
            sarsa_player_one.game_over(gomoku_board, current_player)
            sarsa_player_two.game_over(gomoku_board, current_player)
            break

        else:
            player_two_score += 1
            sarsa_player_one.game_over(gomoku_board, current_player)
            sarsa_player_two.game_over(gomoku_board, current_player )
            break
    return theWinner


def print_weights():
    file_number = 0
    # prints the weights to the file
    filename = f"sarsa_weights_{file_number}"
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
        file.write(f"Player1 score: {player_one_score}")
        file.write("  ")
        file.write(f"Player2 score: {player_two_score}")
        file.write("\n")


def main():
    games_played = 0
    i = 0
    while i < 1000000:
        print(f"starting {i} game")
        play_gomoku()
        if games_played == 100:
            print_weights()
            games_played = 0
        
        games_played += 1
        print(f"games played so far {games_played}")
        i += 1


    

main()
