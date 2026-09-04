"""Gomoku feature vectors for linear Q / SARSA function approximation.

Features describe the *afterstate* (board after a candidate stone is placed)
from the acting player's perspective. Detection covers solid runs and jump /
broken patterns used in Gomoku theory (VCF/VCT, open/sleep four, forks).

Board edges count as blocked — they are not treated as empty cells.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Feature layout (must stay in sync with DEFAULT_WEIGHTS)
# Priority mapping (Gomoku theory → feature index):
#   1 Five              → player_five / opp_five
#   2 Open four         → player_open4 / opp_open4
#   3 Double-four 4-4   → player_double_four / opp_double_four
#   4 Four-three 4-3    → player_four_three / opp_four_three
#   5 Double-three 3-3  → player_double_three / opp_double_three
#   6 Sleep / half four → player_sleep4 / opp_sleep4
#   7 Broken/jump four  → player_broken4 / opp_broken4
#   8 Open three        → player_open3 / opp_open3
#   9 Broken/jump three → player_broken3 / opp_broken3
#  10 Half-open three   → player_half3 / opp_half3
#  11 Open two          → player_open2 / opp_open2
# Plus: bias, center bias, own_immediate_wins, opp_immediate_wins
# ---------------------------------------------------------------------------
FEATURE_NAMES = [
    "bias",                  # 0
    "player_five",           # 1
    "player_open4",          # 2
    "player_double_four",    # 3  fork 4-4
    "player_four_three",     # 4  fork 4-3
    "player_double_three",   # 5  fork 3-3
    "player_sleep4",         # 6  half-open four
    "player_broken4",        # 7  jump four (XXX.X / XX.XX / X.XXX)
    "player_open3",          # 8
    "player_broken3",        # 9  jump three (XX.X / X.XX)
    "player_half3",          # 10
    "player_open2",          # 11
    "opp_five",              # 12
    "opp_open4",             # 13
    "opp_double_four",       # 14
    "opp_four_three",        # 15
    "opp_double_three",      # 16
    "opp_sleep4",            # 17
    "opp_broken4",           # 18
    "opp_open3",             # 19
    "opp_broken3",           # 20
    "opp_half3",             # 21
    "opp_open2",             # 22
    "center",                # 23  light center occupancy
    "own_immediate_wins",    # 24
    "opp_immediate_wins",    # 25
]
FEATURE_DIM = len(FEATURE_NAMES)  # 26

# Per-player raw threat bucket indices before fork derivation
_FIVE = 0
_OPEN4 = 1
_SLEEP4 = 2
_BROKEN4 = 3
_OPEN3 = 4
_BROKEN3 = 5
_HALF3 = 6
_OPEN2 = 7
_N_THREATS = 8


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


def _cell(line, index):
    if 0 <= index < len(line):
        return line[index]
    return None  # out of bounds acts as blocked / non-empty


def _count_solid_threats(line, player):
    """Count solid (contiguous) run threats for one player on a line."""
    counts = [0] * _N_THREATS
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
                counts[_SLEEP4] += 1
        elif length == 3:
            if open_ends == 2:
                counts[_OPEN3] += 1
            elif open_ends == 1:
                counts[_HALF3] += 1
        elif length == 2:
            if open_ends == 2:
                counts[_OPEN2] += 1
    return counts


def _count_broken_patterns(line, player):
    """Detect jump/broken fours and threes on a line.

    Broken four: exactly 4 player stones + 1 empty in a length-5 window
    (patterns XXX.X, XX.XX, X.XXX), and the window is not fully blocked on
    both outer sides (at least one approachable end outside the window or
    the gap itself is the connect point for an immediate threat).

    Broken three: exactly 3 player stones + 1 empty in a length-4 window
    (XX.X, X.XX) with both outer ends open (alive jump-three), counted
    once per distinct gap so solid open-threes are not double-counted as
    broken when no gap exists.
    """
    broken4 = 0
    broken3 = 0
    n = len(line)
    opponent = 3 - player

    # Broken fours: sliding windows of 5
    seen4 = set()
    for start in range(n - 4):
        window = line[start : start + 5]
        if any(c == opponent for c in window):
            continue
        stones = sum(1 for c in window if c == player)
        empties = sum(1 for c in window if c == 0)
        if stones != 4 or empties != 1:
            continue
        # Require a genuine gap (not a solid four already counted)
        gap = window.index(0)
        if gap == 0 or gap == 4:
            # Gap on the rim of the window is a solid four approach, not jump
            continue
        # Outer ends: prefer not both blocked by opponent/edge
        left_out = _cell(line, start - 1)
        right_out = _cell(line, start + 5)
        left_blocked = left_out not in (0, None) and left_out != player
        # None (edge) is blocked; opponent is blocked; empty is open
        left_open = left_out == 0
        right_open = right_out == 0
        # Edge (None) or opponent = blocked
        if left_out is None:
            left_open = False
        if right_out is None:
            right_open = False
        if left_out == opponent:
            left_open = False
        if right_out == opponent:
            right_open = False
        # Count if at least one outer side is open OR the pattern is interior
        # (gap fill creates four/five threat either way when not both edges)
        if left_open or right_open or (left_out != opponent and right_out != opponent):
            key = (start, gap)
            if key not in seen4:
                seen4.add(key)
                broken4 += 1

    # Broken threes: sliding windows of 4 with pattern X.XX / XX.X
    seen3 = set()
    for start in range(n - 3):
        window = line[start : start + 4]
        if any(c == opponent for c in window):
            continue
        stones = sum(1 for c in window if c == player)
        empties = sum(1 for c in window if c == 0)
        if stones != 3 or empties != 1:
            continue
        gap = window.index(0)
        if gap == 0 or gap == 3:
            continue  # rim gap → solid three, not jump
        left_out = _cell(line, start - 1)
        right_out = _cell(line, start + 4)
        left_open = left_out == 0
        right_open = right_out == 0
        # Alive broken three needs both outer ends open
        if left_open and right_open:
            key = (start, gap)
            if key not in seen3:
                seen3.add(key)
                broken3 += 1

    return broken4, broken3


def _sum_threats(lines, player):
    totals = [0] * _N_THREATS
    for line in lines:
        solid = _count_solid_threats(line, player)
        for i in range(_N_THREATS):
            totals[i] += solid[i]
        b4, b3 = _count_broken_patterns(line, player)
        totals[_BROKEN4] += b4
        totals[_BROKEN3] += b3
    return totals


def _derive_forks(threats):
    """Binary fork indicators from threat counts.

    fours  = open4 + sleep4 + broken4
    threes = open3 + broken3   (alive-style threes for fork theory)
    """
    fours = threats[_OPEN4] + threats[_SLEEP4] + threats[_BROKEN4]
    alive_threes = threats[_OPEN3] + threats[_BROKEN3]
    double_four = 1.0 if fours >= 2 else 0.0
    four_three = 1.0 if fours >= 1 and alive_threes >= 1 else 0.0
    double_three = 1.0 if alive_threes >= 2 else 0.0
    return double_four, four_three, double_three


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
    p_df, p_ft, p_dt = _derive_forks(player_t)
    o_df, o_ft, o_dt = _derive_forks(opp_t)

    features = np.zeros(FEATURE_DIM, dtype=float)
    features[0] = 1.0
    features[1] = player_t[_FIVE]
    features[2] = player_t[_OPEN4]
    features[3] = p_df
    features[4] = p_ft
    features[5] = p_dt
    features[6] = player_t[_SLEEP4]
    features[7] = player_t[_BROKEN4]
    features[8] = player_t[_OPEN3]
    features[9] = player_t[_BROKEN3]
    features[10] = player_t[_HALF3]
    features[11] = player_t[_OPEN2]
    features[12] = opp_t[_FIVE]
    features[13] = opp_t[_OPEN4]
    features[14] = o_df
    features[15] = o_ft
    features[16] = o_dt
    features[17] = opp_t[_SLEEP4]
    features[18] = opp_t[_BROKEN4]
    features[19] = opp_t[_OPEN3]
    features[20] = opp_t[_BROKEN3]
    features[21] = opp_t[_HALF3]
    features[22] = opp_t[_OPEN2]

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
        features[23] = player_center / total_center

    features[24] = count_immediate_wins(board, player)
    features[25] = count_immediate_wins(board, opponent)
    return features


# Advanced priors: own threats >> basic; opponent counts negated.
# Magnitudes encode strategy priority (five > open4 > forks > sleep4 > …).
DEFAULT_WEIGHTS = [
    0.0,     # 0  bias
    200.0,   # 1  player five
    120.0,   # 2  player open four
    150.0,   # 3  player double-four fork
    130.0,   # 4  player four-three fork
    90.0,    # 5  player double-three fork
    60.0,    # 6  player sleep / half-open four
    45.0,    # 7  player broken four
    35.0,    # 8  player open three
    25.0,    # 9  player broken three
    15.0,    # 10 player half-open three
    5.0,     # 11 player open two
    -200.0,  # 12 opp five
    -130.0,  # 13 opp open four
    -160.0,  # 14 opp double-four
    -140.0,  # 15 opp four-three
    -100.0,  # 16 opp double-three
    -70.0,   # 17 opp sleep four
    -50.0,   # 18 opp broken four
    -40.0,   # 19 opp open three
    -28.0,   # 20 opp broken three
    -18.0,   # 21 opp half-open three
    -6.0,    # 22 opp open two
    2.0,     # 23 center (light bias)
    80.0,    # 24 own immediate wins
    -90.0,   # 25 opp immediate wins
]

assert len(DEFAULT_WEIGHTS) == FEATURE_DIM
assert len(FEATURE_NAMES) == FEATURE_DIM
