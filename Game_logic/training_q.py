import os
import sys
import time
from game_board import Board
sys.path.append("../ai_players")
from q_learning import QLearning

# Try to import matplotlib for optional visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Note: matplotlib not available. Visualization disabled. Install with: pip install matplotlib")

PLTYP1 = 'q-learning'
PLTYP2 = 'q-learning'

q_player_two = QLearning(epsilon=0.2, alpha=0.3, gamma=1, size=15, weights=[18, -18, -0.25, 14.625, -0.25, -0.25, -0.25, -0.25, -0.25, 0.625])
q_player_one = QLearning(epsilon=0.2, alpha=0.3, gamma=1, size=15, weights=[-18, -0.25, -0.25, -0.25, 18, -0.25, -0.25, -18, 0.625, 0.625])

PLAYER1 = 1
PLAYER2 = 2

player_one_score = 0
player_two_score = 0

# Statistics tracking
stats = {
    'games_played': 0,
    'player1_wins': 0,
    'player2_wins': 0,
    'game_lengths': [],
    'win_rates_p1': [],
    'win_rates_p2': [],
    'weight_changes_p1': [],
    'weight_changes_p2': [],
    'start_time': time.time()
}

# Store initial weights for tracking changes
initial_weights_p1 = q_player_one.weights.copy()
initial_weights_p2 = q_player_two.weights.copy()


def display_board(board, last_move=None, current_player=None):
    """Display the game board in ASCII format"""
    size = board.size
    print("\n" + "=" * 60)
    print("GAME BOARD")
    print("=" * 60)
    
    # Print column numbers
    print("    ", end="")
    for col in range(size):
        print(f"{col:3d}", end="")
    print()
    
    # Print board with row numbers
    for row in range(size):
        print(f"{row:2d} ", end="")
        for col in range(size):
            cell = board.grid[row][col]
            if last_move and (row, col) == last_move:
                # Highlight the last move with brackets
                if cell == PLAYER1:
                    print("[X]", end="")  # Player 1 (X) - last move
                elif cell == PLAYER2:
                    print("[O]", end="")  # Player 2 (O) - last move
                else:
                    print("[.]", end="")
            else:
                if cell == PLAYER1:
                    print(" X ", end="")  # Player 1 (X)
                elif cell == PLAYER2:
                    print(" O ", end="")  # Player 2 (O)
                else:
                    print(" . ", end="")  # Empty
        print()
    
    print("=" * 60)
    if last_move:
        player_symbol = "X" if current_player == PLAYER1 else "O"
        print(f"Last move: {player_symbol} at ({last_move[0]}, {last_move[1]})")
    print()


def play_gomoku(show_board=False, show_every_n_moves=5):
    global player_one_score, player_two_score, stats
    gomoku_board = Board()
    current_player = PLAYER1
    theWinner = 0
    move_count = 0
    last_move = None

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
            move_count += 1
            last_move = (row, col)
            
            # Display board if enabled
            if show_board and move_count % show_every_n_moves == 0:
                display_board(gomoku_board, last_move, current_player)
            
            # Change the player
            if current_player == PLAYER1:
                current_player = PLAYER2
            else:
                current_player = PLAYER1

        # Track game statistics
        stats['game_lengths'].append(move_count)
        
        # Show final board state if board display is enabled
        if show_board:
            display_board(gomoku_board, last_move, theWinner)
            print(f"Game Over! Winner: Player {theWinner} ({'X' if theWinner == PLAYER1 else 'O'})")
            print(f"Total moves: {move_count}\n")
        
        if theWinner == PLAYER1:
            player_one_score += 1
            stats['player1_wins'] += 1
            q_player_one.game_over(gomoku_board, PLAYER1)
            q_player_two.game_over(gomoku_board, PLAYER2)
        else:
            player_two_score += 1
            stats['player2_wins'] += 1
            q_player_one.game_over(gomoku_board, PLAYER1)
            q_player_two.game_over(gomoku_board, PLAYER2)
        break
    return theWinner


def print_weights():
    file_number = 0
    # prints the weights to the file
    filename = f"q_weights_alpha03_{file_number}"
    if os.path.exists(filename):
        file_stat = os.stat(filename)
        if file_stat.st_size > 100000000:
            file_number += 1
            filename = f"q_weights_alpha03_{file_number}"
            
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


def display_progress(current_game, total_games=None, update_interval=100, show_board=False):
    """Display real-time training progress"""
    if stats['games_played'] % update_interval != 0 and current_game != 0:
        return
    
    elapsed_time = time.time() - stats['start_time']
    games_per_sec = stats['games_played'] / elapsed_time if elapsed_time > 0 else 0
    
    # Calculate win rates
    total_wins = stats['player1_wins'] + stats['player2_wins']
    win_rate_p1 = (stats['player1_wins'] / total_wins * 100) if total_wins > 0 else 0
    win_rate_p2 = (stats['player2_wins'] / total_wins * 100) if total_wins > 0 else 0
    
    # Calculate average game length
    avg_game_length = sum(stats['game_lengths'][-update_interval:]) / len(stats['game_lengths'][-update_interval:]) if len(stats['game_lengths']) >= update_interval else sum(stats['game_lengths']) / len(stats['game_lengths']) if stats['game_lengths'] else 0
    
    # Calculate weight changes
    weight_change_p1 = sum(abs(q_player_one.weights[i] - initial_weights_p1[i]) for i in range(len(initial_weights_p1)))
    weight_change_p2 = sum(abs(q_player_two.weights[i] - initial_weights_p2[i]) for i in range(len(initial_weights_p2)))
    
    # Store for plotting
    stats['win_rates_p1'].append(win_rate_p1)
    stats['win_rates_p2'].append(win_rate_p2)
    stats['weight_changes_p1'].append(weight_change_p1)
    stats['weight_changes_p2'].append(weight_change_p2)
    
    # Clear screen and display progress
    os.system('clear' if os.name != 'nt' else 'cls')
    
    print("=" * 80)
    print("Q-LEARNING TRAINING PROGRESS")
    print("=" * 80)
    print(f"\nGames Played: {stats['games_played']:,}" + (f" / {total_games:,}" if total_games else ""))
    print(f"Elapsed Time: {elapsed_time:.1f}s ({elapsed_time/60:.1f} minutes)")
    print(f"Games/Second: {games_per_sec:.2f}")
    print(f"Estimated Time Remaining: {(total_games - stats['games_played']) / games_per_sec / 60:.1f} minutes" if total_games and games_per_sec > 0 else "")
    print("\n" + "-" * 80)
    print("WIN RATES (Last {} games):".format(update_interval))
    print(f"  Player 1 (Q-Learning): {win_rate_p1:.2f}% ({stats['player1_wins']} wins)")
    print(f"  Player 2 (Q-Learning): {win_rate_p2:.2f}% ({stats['player2_wins']} wins)")
    print("\n" + "-" * 80)
    print("GAME STATISTICS:")
    print(f"  Average Game Length: {avg_game_length:.1f} moves")
    print(f"  Total Moves Played: {sum(stats['game_lengths']):,}")
    print("\n" + "-" * 80)
    print("WEIGHT CHANGES (from initial):")
    print(f"  Player 1 Total Change: {weight_change_p1:.4f}")
    print(f"  Player 2 Total Change: {weight_change_p2:.4f}")
    print(f"\n  Player 1 Current Weights: {[f'{w:.3f}' for w in q_player_one.weights]}")
    print(f"  Player 2 Current Weights: {[f'{w:.3f}' for w in q_player_two.weights]}")
    print("\n" + "-" * 80)
    print("TRAINING PARAMETERS:")
    print(f"  Epsilon (exploration): {q_player_one.epsilon}")
    print(f"  Alpha (learning rate): {q_player_one.alpha}")
    print(f"  Gamma (discount): {q_player_one.gamma}")
    print("=" * 80)
    print("\nPress Ctrl+C to stop training and save weights...\n")


def save_learning_curves():
    """Save learning curve plots if matplotlib is available"""
    if not HAS_MATPLOTLIB or len(stats['win_rates_p1']) < 2:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Q-Learning Training Progress', fontsize=16)
    
    # Win rates over time
    games = list(range(0, len(stats['win_rates_p1']) * 100, 100))
    axes[0, 0].plot(games[:len(stats['win_rates_p1'])], stats['win_rates_p1'], label='Player 1', linewidth=2)
    axes[0, 0].plot(games[:len(stats['win_rates_p2'])], stats['win_rates_p2'], label='Player 2', linewidth=2)
    axes[0, 0].set_xlabel('Games Played')
    axes[0, 0].set_ylabel('Win Rate (%)')
    axes[0, 0].set_title('Win Rates Over Time')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Weight changes over time
    axes[0, 1].plot(games[:len(stats['weight_changes_p1'])], stats['weight_changes_p1'], label='Player 1', linewidth=2)
    axes[0, 1].plot(games[:len(stats['weight_changes_p2'])], stats['weight_changes_p2'], label='Player 2', linewidth=2)
    axes[0, 1].set_xlabel('Games Played')
    axes[0, 1].set_ylabel('Total Weight Change')
    axes[0, 1].set_title('Weight Changes Over Time')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Game length distribution
    if stats['game_lengths']:
        axes[1, 0].hist(stats['game_lengths'], bins=50, edgecolor='black', alpha=0.7)
        axes[1, 0].set_xlabel('Game Length (moves)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Game Length Distribution')
        axes[1, 0].grid(True, alpha=0.3)
    
    # Recent win rates (last 10 updates)
    if len(stats['win_rates_p1']) > 10:
        recent_games = games[-10:]
        recent_p1 = stats['win_rates_p1'][-10:]
        recent_p2 = stats['win_rates_p2'][-10:]
        axes[1, 1].plot(recent_games, recent_p1, 'o-', label='Player 1', linewidth=2, markersize=6)
        axes[1, 1].plot(recent_games, recent_p2, 's-', label='Player 2', linewidth=2, markersize=6)
        axes[1, 1].set_xlabel('Games Played')
        axes[1, 1].set_ylabel('Win Rate (%)')
        axes[1, 1].set_title('Recent Win Rates (Last 10 Updates)')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    filename = f"q_learning_training_curves_{int(time.time())}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\nLearning curves saved to: {filename}")
    plt.close()


def main(total_games=1000000, update_interval=100, save_weights_interval=100, visualize=True, show_board=False, show_every_n_moves=5):
    """
    Main training function
    
    Args:
        total_games: Total number of games to play
        update_interval: How often to display progress (in games)
        save_weights_interval: How often to save weights to file (in games)
        visualize: Whether to save learning curve plots at the end
        show_board: Whether to display the game board during play
        show_every_n_moves: Display board every N moves (only if show_board=True)
    """
    global stats
    
    print("Starting Q-Learning Training...")
    print(f"Total Games: {total_games:,}")
    print(f"Progress Update Every: {update_interval} games")
    print(f"Weights Saved Every: {save_weights_interval} games")
    if show_board:
        print(f"Board Display: Enabled (showing every {show_every_n_moves} moves)")
    else:
        print("Board Display: Disabled (set show_board=True to enable)")
    print("\nPress Ctrl+C to stop training early...\n")
    time.sleep(2)
    
    try:
        for i in range(total_games):
            play_gomoku(show_board=show_board, show_every_n_moves=show_every_n_moves)
            stats['games_played'] += 1
            
            # Display progress
            display_progress(i, total_games, update_interval, show_board=show_board)
            
            # Save weights periodically
            if stats['games_played'] % save_weights_interval == 0:
                print_weights()
        
        print("\n" + "=" * 80)
        print("TRAINING COMPLETE!")
        print("=" * 80)
        print(f"Total Games: {stats['games_played']:,}")
        print(f"Player 1 Wins: {stats['player1_wins']:,} ({stats['player1_wins']/stats['games_played']*100:.2f}%)")
        print(f"Player 2 Wins: {stats['player2_wins']:,} ({stats['player2_wins']/stats['games_played']*100:.2f}%)")
        
        # Save final weights
        print_weights()
        
        # Save learning curves if matplotlib is available
        if visualize and HAS_MATPLOTLIB:
            save_learning_curves()
            
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
        print(f"Games completed: {stats['games_played']:,}")
        print_weights()
        if visualize and HAS_MATPLOTLIB:
            save_learning_curves()


if __name__ == "__main__":
    # You can customize these parameters
    main(
        total_games=1000000,      # Total number of games to play
        update_interval=100,       # Display progress every N games
        save_weights_interval=100, # Save weights every N games
        visualize=True,           # Save learning curve plots
        show_board=True,          # Show game board during play
        show_every_n_moves=5      # Display board every N moves (only if show_board=True)
    )
