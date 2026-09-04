import os
import sys
import time

from game_board import Board

sys.path.append("../ai_players")
from feature_utils import DEFAULT_WEIGHTS, FEATURE_DIM
from sarsa_agent import SarsaAgent
from weight_io import default_checkpoint_path
from rl_training_lib import (
    HAS_MATPLOTLIB,
    apply_resume,
    display_board,
    display_progress,
    empty_stats,
    make_arg_parser,
    save_agent_checkpoint,
    save_learning_curves,
)

PLTYP1 = "sarsa"
PLTYP2 = "sarsa"
DEFAULT_ALPHA = 0.2
DEFAULT_EPSILON = 0.1
DEFAULT_GAMMA = 1.0

sarsa_player_two = SarsaAgent(
    epsilon=DEFAULT_EPSILON, alpha=DEFAULT_ALPHA, gamma=DEFAULT_GAMMA, size=15, weights=list(DEFAULT_WEIGHTS)
)
sarsa_player_one = SarsaAgent(
    epsilon=DEFAULT_EPSILON, alpha=DEFAULT_ALPHA, gamma=DEFAULT_GAMMA, size=15, weights=list(DEFAULT_WEIGHTS)
)

PLAYER1 = 1
PLAYER2 = 2
player_one_score = 0
player_two_score = 0
stats = empty_stats()
initial_weights_p1 = list(sarsa_player_one.weights)
initial_weights_p2 = list(sarsa_player_two.weights)
CHECKPOINT_PATH = default_checkpoint_path("sarsa", DEFAULT_ALPHA)


def play_gomoku(show_board=False, show_every_n_moves=5):
    global player_one_score, player_two_score, stats
    gomoku_board = Board()
    current_player = PLAYER1
    theWinner = 0
    move_count = 0
    last_move = None
    while True:
        while theWinner == 0:
            if current_player == PLAYER2 and PLTYP2 == "sarsa":
                row, col = sarsa_player_two.get_move(gomoku_board, current_player)
            elif current_player == PLAYER1 and PLTYP1 == "sarsa":
                row, col = sarsa_player_one.get_move(gomoku_board, current_player)
            gomoku_board.play(current_player, (row, col))
            theWinner = gomoku_board.is_win(current_player)
            move_count += 1
            last_move = (row, col)
            if show_board and move_count % show_every_n_moves == 0:
                display_board(gomoku_board, last_move, current_player)
            current_player = PLAYER2 if current_player == PLAYER1 else PLAYER1
        stats["game_lengths"].append(move_count)
        if show_board:
            display_board(gomoku_board, last_move, theWinner)
            print(f"Game Over! Winner: Player {theWinner} ({'X' if theWinner == PLAYER1 else 'O'})")
            print(f"Total moves: {move_count}\n")
        if theWinner == PLAYER1:
            player_one_score += 1
            stats["player1_wins"] += 1
        else:
            player_two_score += 1
            stats["player2_wins"] += 1
        sarsa_player_one.game_over(gomoku_board, PLAYER1)
        sarsa_player_two.game_over(gomoku_board, PLAYER2)
        break
    return theWinner


def save_weights(path=None, also_history=True):
    global CHECKPOINT_PATH
    out = path or CHECKPOINT_PATH
    total_games = stats["games_trained_base"] + stats["games_played"]
    return save_agent_checkpoint(out, sarsa_player_one, "sarsa", total_games, also_history=also_history)


def main(
    total_games=1000000,
    update_interval=100,
    save_weights_interval=100,
    visualize=True,
    show_board=False,
    show_every_n_moves=5,
    out_path=None,
    resume_path=None,
):
    global stats, CHECKPOINT_PATH, initial_weights_p1, initial_weights_p2
    CHECKPOINT_PATH = out_path or default_checkpoint_path("sarsa", sarsa_player_one.alpha)
    if resume_path:
        initial_weights_p1, initial_weights_p2 = apply_resume(
            resume_path, [sarsa_player_one, sarsa_player_two], stats
        )
    print("Starting SARSA Training...")
    print(f"feature_dim: {FEATURE_DIM}")
    print(f"output path: {CHECKPOINT_PATH}")
    print(f"Total Games: {total_games:,}")
    print(f"Progress Update Every: {update_interval} games")
    print(f"Weights Saved Every: {save_weights_interval} games")
    print("Board Display: Enabled" if show_board else "Board Display: Disabled (pass --show-board to enable)")
    print("\nPress Ctrl+C to stop training early...\n")
    time.sleep(1)
    try:
        for i in range(total_games):
            play_gomoku(show_board=show_board, show_every_n_moves=show_every_n_moves)
            stats["games_played"] += 1
            display_progress(
                "SARSA TRAINING PROGRESS",
                stats,
                [sarsa_player_one, sarsa_player_two],
                [initial_weights_p1, initial_weights_p2],
                ["Player 1 (SARSA)", "Player 2 (SARSA)"],
                CHECKPOINT_PATH,
                i,
                total_games,
                update_interval,
            )
            if stats["games_played"] % save_weights_interval == 0:
                save_weights(CHECKPOINT_PATH)
        print("\n" + "=" * 80)
        print("TRAINING COMPLETE!")
        print("=" * 80)
        print(f"Total Games: {stats['games_played']:,}")
        print(f"Player 1 Wins: {stats['player1_wins']:,} ({stats['player1_wins']/stats['games_played']*100:.2f}%)")
        print(f"Player 2 Wins: {stats['player2_wins']:,} ({stats['player2_wins']/stats['games_played']*100:.2f}%)")
        save_weights(CHECKPOINT_PATH)
        if visualize and HAS_MATPLOTLIB:
            save_learning_curves(stats, "SARSA Training Progress", "sarsa_training_curves")
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
        print(f"Games completed: {stats['games_played']:,}")
        save_weights(CHECKPOINT_PATH)
        if visualize and HAS_MATPLOTLIB:
            save_learning_curves(stats, "SARSA Training Progress", "sarsa_training_curves")


if __name__ == "__main__":
    args = make_arg_parser(
        "Self-play train SARSA agents and save JSON weight checkpoints.",
        "weights/sarsa_alpha0.2.json",
    ).parse_args()
    main(
        total_games=args.games,
        update_interval=args.update_every,
        save_weights_interval=args.save_every,
        visualize=not args.no_visualize,
        show_board=args.show_board,
        show_every_n_moves=args.show_every_n_moves,
        out_path=args.out,
        resume_path=args.resume,
    )
