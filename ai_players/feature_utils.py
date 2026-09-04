"""Gomoku feature vectors for linear Q / SARSA function approximation.

Features describe the *afterstate* (board after a candidate stone is placed)
from the acting player's perspective. Threats are solid runs classified by
whether each end is open (empty) or blocked (edge / opponent). Board edges
count as closed — they are not treated as empty cells.
"""

from __future__ import annotations

import numpy as np

# Feature layout (must stay in sync with default agent weights):
#  0  bias
#  1  player fives
#  2  player open fours
#  3  player half-open fours
#  4  player open threes
#  5  player half-open threes
#  6  player open twos
#  7  opponent fives
#  8  opponent open fours
#  9  opponent half-open fours
# 10  opponent open threes
# 11  opponent half-open threes
# 12  opponent open twos
# 13  player center occupancy (normalized)
# 14  immediate-win advantage (player wins-in-one minus opponent)
FEATURE_DIM = 15

# Indices within a per-player threat bucket (five, open4, half4, open3, half3, open2)
_FIVE = 0
_OPEN4 = 1
_HALF4 = 2
_OPEN3 = 3
_HALF3 = 4
_OPEN2 = 5


def _collect_lines(grid):
    size = len(grid)
    lines = []
    lines.extend(grid)
    for col in range(size):
        lines.append([grid[row][col] for row in range(size)])
    for diag in range(2 * size - 1):
        line = []
        for row in range(size):
            col = diag - row
            if 0 <= col < size:
                line.append(grid[row][col])
        if len(line) >= 5:
            lines.append(line)
    for diag in range(-(size - 1), size):
        line = []
        for row in range(size):
            col = row - diag
            if 0 <= col < size:
                line.append(grid[row][col])
        if len(line) >= 5:
            lines.append(line)
    return lines


def _empty_end(line, index):
    """True if index is in-bounds and empty. Out of bounds = blocked."""
    return 0 <= index < len(line) and line[index] == 0


def _count_threats_on_line(line, player):
    """Count solid-run threats for one player on a single line."""
    counts = [0, 0, 0, 0, 0, 0]
    n = len(line)
    i = 0
    while i < n:
        if line[i] != player:
            i += 1
            continue
        start = i
        while i < n and line[i] == player:
            i += 1
        length = i - start
        left_open = _empty_end(line, start - 1)
        right_open = _empty_end(line, i)
        open_ends = int(left_open) + int(right_open)

        if length >= 5:
            counts[_FIVE] += 1
        elif length == 4:
            if open_ends == 2:
                counts[_OPEN4] += 1
            elif open_ends == 1:
                counts[_HALF4] += 1
        elif length == 3:
            if open_ends == 2:
                counts[_OPEN3] += 1
            elif open_ends == 1:
                counts[_HALF3] += 1
        elif length == 2:
            if open_ends == 2:
                counts[_OPEN2] += 1
        # length 1 ignored — too weak / noisy for linear FA
    return counts


def _sum_threats(lines, player):
    totals = [0, 0, 0, 0, 0, 0]
    for line in lines:
        part = _count_threats_on_line(line, player)
        for i in range(6):
            totals[i] += part[i]
    return totals


def count_immediate_wins(board, player):
    moves = board.get_possible_moves()
    if not moves:
        moves = [
            (row, col)
            for row in range(board.size)
            for col in range(board.size)
            if board.grid[row][col] == 0
        ]
    wins = 0
    for move in moves:
        board.play(player, move)
        if board.is_win(player):
            wins += 1
        board.undo(move)
    return wins


def compute_features(board, player):
    """Return a length-FEATURE_DIM feature vector for the current board afterstate."""
    opponent = 3 - player
    grid = board.grid
    lines = _collect_lines(grid)

    player_t = _sum_threats(lines, player)
    opp_t = _sum_threats(lines, opponent)

    features = np.zeros(FEATURE_DIM, dtype=float)
    features[0] = 1.0
    features[1] = player_t[_FIVE]
    features[2] = player_t[_OPEN4]
    features[3] = player_t[_HALF4]
    features[4] = player_t[_OPEN3]
    features[5] = player_t[_HALF3]
    features[6] = player_t[_OPEN2]
    features[7] = opp_t[_FIVE]
    features[8] = opp_t[_OPEN4]
    features[9] = opp_t[_HALF4]
    features[10] = opp_t[_OPEN3]
    features[11] = opp_t[_HALF3]
    features[12] = opp_t[_OPEN2]

    mid = board.size // 2
    radius = 2
    player_center = 0
    total_center = 0
    for row in range(max(0, mid - radius), min(board.size, mid + radius + 1)):
        for col in range(max(0, mid - radius), min(board.size, mid + radius + 1)):
            total_center += 1
            if grid[row][col] == player:
                player_center += 1
    if total_center:
        features[13] = player_center / total_center

    features[14] = count_immediate_wins(board, player) - count_immediate_wins(
        board, opponent
    )
    return features


# Sensible priors: reward own threats, penalize opponent threats.
DEFAULT_WEIGHTS = [
    0.0,   # bias
    100.0, # player five
    50.0,  # player open four
    30.0,  # player half-open four
    15.0,  # player open three
    8.0,   # player half-open three
    3.0,   # player open two
    -100.0,  # opponent five
    -55.0,   # opponent open four
    -35.0,   # opponent half-open four
    -18.0,   # opponent open three
    -10.0,   # opponent half-open three
    -4.0,    # opponent open two
    2.0,     # center
    20.0,    # immediate-win delta
]
