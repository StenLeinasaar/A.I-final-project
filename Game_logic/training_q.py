import os
import sys
from game_board import Board
sys.path.append("../ai_players")
from q_learning import QLearning


PLTYP1 = 'q-learning'
PLTYP2 = 'q-learning'

q_player_two = QLearning(epsilon=0.2, alpha=0.3, gamma=1, size=15, weights=[18, -18, -0.25, 14.625, -0.25, -0.25, -0.25, -0.25, -0.25, 0.625])
q_player_one = QLearning(epsilon=0.2, alpha=0.3, gamma=1, size=15, weights=[-18, -0.25, -0.25, -0.25, 18, -0.25, -0.25, -18, 0.625, 0.625])

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
            if current_player == PLAYER2 and PLTYP2 == 'q-learning':
                row, col = q_player_two.get_move(gomoku_board, current_player)
            elif current_player == PLAYER1 and PLTYP1=='q-learning':
                row, col = q_player_one.get_move(gomoku_board, current_player)
                
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
            q_player_one.game_over(gomoku_board, current_player)
            q_player_two.game_over(gomoku_board, current_player)
            break

        else:
            player_two_score += 1
            q_player_one.game_over(gomoku_board, current_player)
            q_player_two.game_over(gomoku_board, current_player )
            break
    return theWinner

    





def print_weights():
    file_number = 0
    # prints the weights to the file
    filename = f"q_weights_alpha03_{file_number}"
    print("file about to be written", filename)
    if os.path.exists(f"Game_logic/{filename}"):
        file_stat = os.stat(filename)
        if file_stat.st_size() > 100000000:
            file_number += 1
            filename = f"weights_{file_number}"
            
        
    with open(filename, 'a') as file:
        file.write("player 1 weights")
        file.write(str(q_player_one.weights))
        file.write("  ")
        file.write("player 2 weights")
        file.write(str(q_player_two.weights))
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