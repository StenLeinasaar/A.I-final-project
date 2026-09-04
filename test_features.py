"""Tests for advanced Gomoku Q-learning features, rewards, and greedy policy."""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "Game_logic"))
sys.path.insert(0, os.path.join(ROOT, "ai_players"))

import numpy as np
from game_board import Board
from feature_utils import (
    FEATURE_DIM,
    FEATURE_NAMES,
    DEFAULT_WEIGHTS,
    compute_features,
)
from q_learning import QLearning


def _empty_board(size=15):
    return Board(size=size)


def _place(board, player, cells):
    for r, c in cells:
        board.play(player, (r, c))


def test_feature_dim_and_weights():
    assert FEATURE_DIM == 26
    assert len(FEATURE_NAMES) == FEATURE_DIM
    assert len(DEFAULT_WEIGHTS) == FEATURE_DIM
    agent = QLearning(epsilon=0.0, weights=list(DEFAULT_WEIGHTS))
    assert len(agent.weights) == FEATURE_DIM
    try:
        QLearning(weights=[0.0] * 10)
        raise AssertionError("expected ValueError for wrong weight length")
    except ValueError:
        pass


def test_open_three_open_four_five():
    # Open three: .XXX. on a row
    b = _empty_board()
    _place(b, 1, [(7, 5), (7, 6), (7, 7)])
    f = compute_features(b, 1)
    assert f[FEATURE_NAMES.index("player_open3")] >= 1, f"open3={f[8]}"

    # Open four: .XXXX.
    b2 = _empty_board()
    _place(b2, 1, [(7, 5), (7, 6), (7, 7), (7, 8)])
    f2 = compute_features(b2, 1)
    assert f2[FEATURE_NAMES.index("player_open4")] >= 1, f"open4={f2[2]}"

    # Five
    b3 = _empty_board()
    _place(b3, 1, [(7, 4), (7, 5), (7, 6), (7, 7), (7, 8)])
    f3 = compute_features(b3, 1)
    assert f3[FEATURE_NAMES.index("player_five")] >= 1, f"five={f3[1]}"
    assert b3.is_win(1)


def test_broken_three_xx_x():
    # Pattern XX_X with both outer ends open → broken/jump three
    b = _empty_board()
    _place(b, 1, [(7, 5), (7, 6), (7, 8)])  # XX_X at cols 5,6,8
    f = compute_features(b, 1)
    idx = FEATURE_NAMES.index("player_broken3")
    assert f[idx] >= 1, f"expected broken3, got features broken3={f[idx]}, open3={f[8]}, half3={f[10]}"


def test_forks_high_q_vs_open_two():
    # Afterstate with double-three / four-three should beat plain open two under DEFAULT_WEIGHTS
    # Setup A: open two only
    open2 = _empty_board()
    _place(open2, 1, [(7, 7), (7, 8)])
    q_open2 = float(np.dot(DEFAULT_WEIGHTS, compute_features(open2, 1)))

    # Setup B: double-three afterstate — two open threes on different lines
    # Horizontal open three at row 7 cols 5-7, vertical open three at col 7 rows 5-7
    # Shared stone at (7,7): stones (7,5)(7,6)(7,7) and (5,7)(6,7)(7,7)
    d3 = _empty_board()
    _place(d3, 1, [(7, 5), (7, 6), (7, 7), (5, 7), (6, 7)])
    feat_d3 = compute_features(d3, 1)
    q_d3 = float(np.dot(DEFAULT_WEIGHTS, feat_d3))
    assert feat_d3[FEATURE_NAMES.index("player_double_three")] >= 1 or feat_d3[
        FEATURE_NAMES.index("player_open3")
    ] >= 2, f"double-three features: {feat_d3}"
    assert q_d3 > q_open2, f"double-three Q={q_d3} should beat open-two Q={q_open2}"

    # Setup C: four-three — open four on row + open three on column
    f3 = _empty_board()
    _place(f3, 1, [(7, 5), (7, 6), (7, 7), (7, 8), (5, 7), (6, 7)])
    feat_f3 = compute_features(f3, 1)
    q_f3 = float(np.dot(DEFAULT_WEIGHTS, feat_f3))
    assert (
        feat_f3[FEATURE_NAMES.index("player_four_three")] >= 1
        or feat_f3[FEATURE_NAMES.index("player_open4")] >= 1
    ), feat_f3
    assert q_f3 > q_open2, f"four-three Q={q_f3} should beat open-two Q={q_open2}"


def test_epsilon0_takes_win_and_blocks_open_four():
    agent = QLearning(epsilon=0.0, weights=list(DEFAULT_WEIGHTS))

    # Winning move: four in a row, empty completing cell
    b = _empty_board()
    # Seed neighbors so get_possible_moves returns candidates
    _place(b, 1, [(7, 5), (7, 6), (7, 7), (7, 8)])
    _place(b, 2, [(0, 0)])  # irrelevant distant stone — need neighbor near win cell
    # Actually get_possible_moves only returns cells adjacent to stones.
    # Cells (7,4) and (7,9) are adjacent to the four.
    move = agent.choose_action_max(b, 1)
    assert move in ((7, 4), (7, 9)), f"expected winning move at end of four, got {move}"
    b.play(1, move)
    assert b.is_win(1)

    # Block opponent open four
    b2 = _empty_board()
    _place(b2, 2, [(7, 5), (7, 6), (7, 7), (7, 8)])  # opponent open four
    _place(b2, 1, [(10, 10)])  # our stone elsewhere so we have moves
    block = agent.choose_action_max(b2, 1)
    assert block in ((7, 4), (7, 9)), f"expected block of open four, got {block}"


def test_get_reward_terminal_only():
    b = _empty_board()
    _place(b, 1, [(7, 5), (7, 6), (7, 7)])
    assert b.get_reward(1) == 0.0
    assert b.get_reward(2) == 0.0

    win = _empty_board()
    _place(win, 1, [(7, 4), (7, 5), (7, 6), (7, 7), (7, 8)])
    assert win.get_reward(1) == 1.0
    assert win.get_reward(2) == -1.0

    # Full board draw (no five) — fill without five-in-a-row is hard on 15x15;
    # instead verify mid-game with immediate threats still returns 0.
    mid = _empty_board()
    _place(mid, 1, [(7, 5), (7, 6), (7, 7), (7, 8)])  # open four → immediate win avail
    assert mid.get_reward(1) == 0.0
    assert mid.count_immediate_wins(1) >= 1


def test_training_play_order_semantics():
    """Sanity: after play then is_win, a completing five is detected."""
    b = _empty_board()
    _place(b, 1, [(7, 5), (7, 6), (7, 7), (7, 8)])
    assert not b.is_win(1)
    b.play(1, (7, 9))
    assert b.is_win(1)


def run_all():
    tests = [
        test_feature_dim_and_weights,
        test_open_three_open_four_five,
        test_broken_three_xx_x,
        test_forks_high_q_vs_open_two,
        test_epsilon0_takes_win_and_blocks_open_four,
        test_get_reward_terminal_only,
        test_training_play_order_semantics,
    ]
    failed = []
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as e:
            failed.append((t.__name__, e))
            print(f"FAIL {t.__name__}: {e}")
    if failed:
        print(f"\n{len(failed)} FAILED")
        for name, err in failed:
            print(f"  - {name}: {err}")
        sys.exit(1)
    print(f"\nAll {len(tests)} tests passed. FEATURE_DIM={FEATURE_DIM}")


if __name__ == "__main__":
    run_all()
