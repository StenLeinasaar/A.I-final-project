from game_board import Board
import sys

def max_val(game_board:Board, depth: int, alpha: int, beta: int, player:int) -> int:
    # print(f"max val called with depth {depth}")
    if depth == 0: #or game_board.get_state() in [0,-1,1]: # or (node is either draw, lose or win.
        return evaluate(game_board, player,True)
    best_value = -float("inf")
    moves = game_board.get_possible_moves() #NEED a function to get all possible moves
    for move in moves:
        game_board.play(player, move)
        value = min_val(game_board, depth-1, alpha, beta, player)
        best_value = max(best_value, value)
        alpha = max(alpha, best_value)
        game_board.undo(move)
        if alpha >= beta:
            break
    return best_value




def min_val(game_board:Board, depth: int, alpha: int, beta: int, player:int) -> int:
    # print(f"Min val function called, depth is {depth}")
    if depth == 0: #or game_board.get_state() in [0,-1,1]: # or (node is either draw, lose or win.
        # print("returning evaluate score to main function")
        return evaluate(game_board, player, False)
    best_value = float("inf")
    moves = game_board.get_possible_moves()
    for move in moves:
        game_board.play(player,move)
        value = max_val(game_board, depth-1, alpha, beta, player)
        best_value = min(best_value, value)
        beta = min(beta, best_value)
        game_board.undo(move)
        if beta <= alpha:
            break
    return best_value

# driver function
def alpha_beta_pruning(game_board:Board, player:int):
    depth = 2
    # print(f"calling the functions with value of depth being = {depth}")
    alpha = -float("inf")
    beta = float("inf")
    #get all possible moves
    available_moves = game_board.get_possible_moves()
    # print(f"these are available moves {available_moves}")
    max_value = 0
    min_value = 1500000
    best_move = available_moves[0]
    if player == 1:
        # Max player
        for move in available_moves:
            game_board.play(player,move)
            value = max_val(game_board, depth, alpha, beta, player)
            if value > max_value:
                max_value = value
                best_move = move
            game_board.undo(move)
            
    else:
        # min player
        for move in available_moves:
            print("min player")
            # print(f"checking min player with the move {move}")
            game_board.play(player,move)
            # print("made a move, printing a game board")
            # print(f'calling a min player, depth is {depth}')
            value = min_val(game_board, depth, alpha, beta, player)
            if value < min_value:
                min_value = value
                best_move = move
            game_board.undo(move)

    print(f"the min value is {min_value}")
    print(f"the move chosen is {best_move}")
    
    return best_move


# node state can be set here
def evaluate(game_board: Board, player:int, max_player):
    """
    Evaluate the current board state and return a score for the given player.
    """

    # This might not be a correct way. Make sure you can refer to an opponent as well
    opponent = 3 - player
    score = 0
    max_player = max_player

    # Check for winning positions
    if game_board.is_win(player):
        if max_player:
            score += 1000
        else:
            score -= 1000
    elif game_board.is_win(opponent):
        if max_player:
            score -= 1000
        else:
            score += 1000

    # Count open rows, columns, and diagonals
    open_fours = 0
    open_threes = 0
    open_twos = 0
    for i in range(game_board.size):
        for j in range(game_board.size):
            if game_board.grid[i][j] == 0:
                if game_board.has_neighbor(i, j):
                    count = game_board.count_open(i, j)
                    if count >= 4:
                        open_fours += 1
                    elif count == 3:
                        open_threes += 1
                    elif count == 2:
                        open_twos += 1

    if max_player:
        # Add score based on open rows, columns, and diagonals
        score += 100 * open_fours + 10 * open_threes + open_twos
    else:
        score -= 100 * open_fours + 10 * open_threes + open_twos

    # Subtract penalty for opponent's open rows, columns, and diagonals
    open_fours = 0
    open_threes = 0
    open_twos = 0
    for i in range(game_board.size):
        for j in range(game_board.size):
            if game_board.grid[i][j] == opponent:
                if game_board.has_neighbor(i, j):
                    count = game_board.count_open(i, j)
                    if count >= 4:
                        open_fours += 1
                    elif count == 3:
                        open_threes += 1
                    elif count == 2:
                        open_twos += 1
    print(f"Score currently is {score}")
    # print(f"Returning the score of  {score}")
    if max_player:
        # Sbutract based on open rows, columns, and diagonals
        score -= 1000 * open_fours + 100 * open_threes + 10*open_twos
    else:
        score += 1000 * open_fours + 100 * open_threes + 10*open_twos
    
    print(f"Score after punishing is {score}")

    return score



# def max_val(node: Node, depth: int, alpha: int, beta: int) -> int:
#     if depth == 0 or node.state in [0,-1,1]: # or (node is either draw, lose or win.
#         return evaluate(node)
#     best_value = -float("inf")
#     for child in node.children:
#         value = max_val(child, depth-1, alpha, beta)
#         best_value = max(best_value, value)
#         alpha = max(alpha, best_value)
#         if beta <= alpha:
#             break
#     return best_value




# def min_val(node: Node, depth: int, alpha: int, beta: int) -> int:
#     if depth == 0 or node.state in [0,-1,1]: # or (node is either draw, lose or win.
#         return evaluate(node)

#     best_value = float("inf")
#     for child in node.children:
#         value = min_val(child, depth-1, alpha, beta)
#         best_value = min(best_value, value)
#         beta = min(beta, best_value)
#         if beta <= alpha:
#             break
#     return best_value


