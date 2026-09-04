"""Shared helpers for Q-learning / SARSA self-play trainers."""

from __future__ import annotations

import argparse
import os
import time

from feature_utils import FEATURE_DIM
from weight_io import default_checkpoint_path, load_checkpoint, save_checkpoint

try:
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.use("Agg")
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print(
        "Note: matplotlib not available. Visualization disabled. "
        "Install with: pip install matplotlib"
    )


def make_arg_parser(description: str, default_out_hint: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--games", type=int, default=1000000, help="Number of training games (smoke: 50-200)."
    )
    parser.add_argument("--save-every", type=int, default=100, help="Overwrite checkpoint every N games.")
    parser.add_argument("--update-every", type=int, default=100, help="Print progress every N games.")
    parser.add_argument(
        "--show-board", action="store_true", help="Print ASCII board during training (slow)."
    )
    parser.add_argument("--resume", metavar="PATH", default=None, help="Load a JSON checkpoint and continue.")
    parser.add_argument(
        "--out",
        metavar="PATH",
        default=None,
        help=f"Checkpoint path (default: {default_out_hint}).",
    )
    parser.add_argument("--no-visualize", action="store_true", help="Skip matplotlib learning curves.")
    parser.add_argument(
        "--show-every-n-moves", type=int, default=5, help="Board print interval when --show-board."
    )
    return parser


def display_board(board, last_move=None, current_player=None, player1=1, player2=2):
    size = board.size
    print("\n" + "=" * 60)
    print("GAME BOARD")
    print("=" * 60)
    print("    ", end="")
    for col in range(size):
        print(f"{col:3d}", end="")
    print()
    for row in range(size):
        print(f"{row:2d} ", end="")
        for col in range(size):
            cell = board.grid[row][col]
            if last_move and (row, col) == last_move:
                if cell == player1:
                    print("[X]", end="")
                elif cell == player2:
                    print("[O]", end="")
                else:
                    print("[.]", end="")
            else:
                if cell == player1:
                    print(" X ", end="")
                elif cell == player2:
                    print(" O ", end="")
                else:
                    print(" . ", end="")
        print()
    print("=" * 60)
    if last_move:
        player_symbol = "X" if current_player == player1 else "O"
        print(f"Last move: {player_symbol} at ({last_move[0]}, {last_move[1]})")
    print()


def save_agent_checkpoint(path, agent, algorithm, games_trained, also_history=True):
    save_checkpoint(
        path,
        agent.weights,
        algorithm=algorithm,
        alpha=agent.alpha,
        gamma=agent.gamma,
        epsilon=agent.epsilon,
        games_trained=games_trained,
        also_history=also_history,
    )
    print(f"Saved checkpoint -> {path} (feature_dim={FEATURE_DIM}, games_trained={games_trained})")
    return path


def apply_resume(path, agents, stats):
    import numpy as np

    data = load_checkpoint(path)
    weights = list(data["weights"])
    for agent in agents:
        agent.weights = np.array(weights, dtype=float)
        if "alpha" in data:
            agent.alpha = float(data["alpha"])
        if "gamma" in data:
            agent.gamma = float(data["gamma"])
        if "epsilon" in data:
            agent.epsilon = float(data["epsilon"])
    stats["games_trained_base"] = int(data.get("games_trained", 0))
    print(f"Resumed from {path} (games_trained so far: {stats['games_trained_base']})")
    return [list(a.weights) for a in agents]


def display_progress(
    title,
    stats,
    agents,
    initial_weights,
    labels,
    checkpoint_path,
    current_game,
    total_games=None,
    update_interval=100,
):
    if stats["games_played"] % update_interval != 0 and current_game != 0:
        return
    elapsed_time = time.time() - stats["start_time"]
    games_per_sec = stats["games_played"] / elapsed_time if elapsed_time > 0 else 0
    total_wins = stats["player1_wins"] + stats["player2_wins"]
    win_rate_p1 = (stats["player1_wins"] / total_wins * 100) if total_wins > 0 else 0
    win_rate_p2 = (stats["player2_wins"] / total_wins * 100) if total_wins > 0 else 0
    recent = stats["game_lengths"][-update_interval:] or stats["game_lengths"]
    avg_game_length = sum(recent) / len(recent) if recent else 0
    changes = [
        sum(abs(agents[i].weights[j] - initial_weights[i][j]) for j in range(len(initial_weights[i])))
        for i in range(2)
    ]
    stats["win_rates_p1"].append(win_rate_p1)
    stats["win_rates_p2"].append(win_rate_p2)
    stats["weight_changes_p1"].append(changes[0])
    stats["weight_changes_p2"].append(changes[1])
    os.system("clear" if os.name != "nt" else "cls")
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(f"\nGames Played: {stats['games_played']:,}" + (f" / {total_games:,}" if total_games else ""))
    print(f"Elapsed Time: {elapsed_time:.1f}s ({elapsed_time/60:.1f} minutes)")
    print(f"Games/Second: {games_per_sec:.2f}")
    if total_games and games_per_sec > 0:
        print(f"Estimated Time Remaining: {(total_games - stats['games_played']) / games_per_sec / 60:.1f} minutes")
    print("\n" + "-" * 80)
    print("WIN RATES:")
    print(f"  {labels[0]}: {win_rate_p1:.2f}% ({stats['player1_wins']} wins)")
    print(f"  {labels[1]}: {win_rate_p2:.2f}% ({stats['player2_wins']} wins)")
    print("\n" + "-" * 80)
    print("GAME STATISTICS:")
    print(f"  Average Game Length: {avg_game_length:.1f} moves")
    print(f"  Total Moves Played: {sum(stats['game_lengths']):,}")
    print("\n" + "-" * 80)
    print("WEIGHT CHANGES (from initial):")
    print(f"  Player 1 Total Change: {changes[0]:.4f}")
    print(f"  Player 2 Total Change: {changes[1]:.4f}")
    print(f"\n  Player 1 Current Weights: {[f'{w:.3f}' for w in agents[0].weights]}")
    print(f"  Player 2 Current Weights: {[f'{w:.3f}' for w in agents[1].weights]}")
    print("\n" + "-" * 80)
    print("TRAINING PARAMETERS:")
    print(f"  Feature dim: {FEATURE_DIM}")
    print(f"  Checkpoint: {checkpoint_path}")
    print(f"  Epsilon (exploration): {agents[0].epsilon}")
    print(f"  Alpha (learning rate): {agents[0].alpha}")
    print(f"  Gamma (discount): {agents[0].gamma}")
    print("=" * 80)
    print("\nPress Ctrl+C to stop training and save weights...\n")


def save_learning_curves(stats, title, filename_prefix):
    if not HAS_MATPLOTLIB or len(stats["win_rates_p1"]) < 2:
        return
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(title, fontsize=16)
    games = list(range(0, len(stats["win_rates_p1"]) * 100, 100))
    axes[0, 0].plot(games[: len(stats["win_rates_p1"])], stats["win_rates_p1"], label="Player 1", linewidth=2)
    axes[0, 0].plot(games[: len(stats["win_rates_p2"])], stats["win_rates_p2"], label="Player 2", linewidth=2)
    axes[0, 0].set_xlabel("Games Played")
    axes[0, 0].set_ylabel("Win Rate (%)")
    axes[0, 0].set_title("Win Rates Over Time")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 1].plot(games[: len(stats["weight_changes_p1"])], stats["weight_changes_p1"], label="Player 1", linewidth=2)
    axes[0, 1].plot(games[: len(stats["weight_changes_p2"])], stats["weight_changes_p2"], label="Player 2", linewidth=2)
    axes[0, 1].set_xlabel("Games Played")
    axes[0, 1].set_ylabel("Total Weight Change")
    axes[0, 1].set_title("Weight Changes Over Time")
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    if stats["game_lengths"]:
        axes[1, 0].hist(stats["game_lengths"], bins=50, edgecolor="black", alpha=0.7)
        axes[1, 0].set_xlabel("Game Length (moves)")
        axes[1, 0].set_ylabel("Frequency")
        axes[1, 0].set_title("Game Length Distribution")
        axes[1, 0].grid(True, alpha=0.3)
    if len(stats["win_rates_p1"]) > 10:
        axes[1, 1].plot(games[-10:], stats["win_rates_p1"][-10:], "o-", label="Player 1", linewidth=2, markersize=6)
        axes[1, 1].plot(games[-10:], stats["win_rates_p2"][-10:], "s-", label="Player 2", linewidth=2, markersize=6)
        axes[1, 1].set_xlabel("Games Played")
        axes[1, 1].set_ylabel("Win Rate (%)")
        axes[1, 1].set_title("Recent Win Rates (Last 10 Updates)")
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    plt.tight_layout()
    filename = f"{filename_prefix}_{int(time.time())}.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    print(f"\nLearning curves saved to: {filename}")
    plt.close()


def empty_stats():
    return {
        "games_played": 0,
        "player1_wins": 0,
        "player2_wins": 0,
        "game_lengths": [],
        "win_rates_p1": [],
        "win_rates_p2": [],
        "weight_changes_p1": [],
        "weight_changes_p2": [],
        "start_time": time.time(),
        "games_trained_base": 0,
    }
