import numpy as np


OPEN_TWO = 2
OPEN_THREE = 3
OPEN_FOUR = 4


def _collect_lines(grid):
    size = len(grid)
    lines = []
    # Rows
    lines.extend(grid)
    # Columns
    for col in range(size):
        lines.append([grid[row][col] for row in range(size)])
    # Diagonals (top-left to bottom-right)
    for diag in range(2 * size - 1):
        line = []
        for row in range(size):
            col = diag - row
            if 0 <= col < size:
                line.append(grid[row][col])
        if len(line) >= 5:
            lines.append(line)
    # Anti-diagonals (top-right to bottom-left)
    for diag in range(-(size - 1), size):
        line = []
        for row in range(size):
            col = row - diag
            if 0 <= col < size:
                line.append(grid[row][col])
        if len(line) >= 5:
            lines.append(line)
    return lines


def _count_open_sequences(lines, player, length):
    pattern = f"0{str(player) * length}0"
    total = 0
    for line in lines:
        line_str = "".join(str(cell) for cell in line)
        padded = f"0{line_str}0"
        start = 0
        while True:
            idx = padded.find(pattern, start)
            if idx == -1:
                break
            total += 1
            start = idx + 1
    return total


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
    opponent = 3 - player
    grid = board.grid
    lines = _collect_lines(grid)

    features = np.zeros(10, dtype=float)
    features[0] = 1.0  # bias term

    features[1] = _count_open_sequences(lines, player, OPEN_FOUR)
    features[2] = _count_open_sequences(lines, opponent, OPEN_FOUR)
    features[3] = _count_open_sequences(lines, player, OPEN_THREE)
    features[4] = _count_open_sequences(lines, opponent, OPEN_THREE)
    features[5] = _count_open_sequences(lines, player, OPEN_TWO)
    features[6] = _count_open_sequences(lines, opponent, OPEN_TWO)

    mid = board.size // 2
    radius = 2
    player_center = 0
    opponent_center = 0
    total_center = 0
    for row in range(max(0, mid - radius), min(board.size, mid + radius + 1)):
        for col in range(max(0, mid - radius), min(board.size, mid + radius + 1)):
            total_center += 1
            if grid[row][col] == player:
                player_center += 1
            elif grid[row][col] == opponent:
                opponent_center += 1

    if total_center:
        features[7] = player_center / total_center
        features[8] = opponent_center / total_center

    features[9] = count_immediate_wins(board, player) - count_immediate_wins(board, opponent)

    return features
