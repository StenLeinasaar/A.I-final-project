import re
class Board:
    def __init__(self, size=15):
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]

    def play(self, player, move):
        """
        Update the board by placing the player's move on the board.
        """
        x, y = move
        self.grid[x][y] = player

    def undo(self, move):
        """
        Undo the given move on the board.
        """
        x, y = move
        self.grid[x][y] = 0

    def is_win(self, player):
        """
        Check if the player has won the game.
        """
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == player:
                    if self.check_win_from(i, j):
                        return player
        return False
       
    
    def is_valid(self, move):
        new_row = move[0]
        new_col = move[1]

        if new_row < 0 or new_row > self.size-1:
            return False
        elif new_col < 0 or new_col > self.size-1:
            return False

        return self.grid[new_row][new_col] == 0

    def check_win_from(self, x, y):
        """
        Check if there is a win starting from the given position.
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            for i in range(1, 5):
                tx, ty = x + i * dx, y + i * dy
                if tx < 0 or tx >= self.size or ty < 0 or ty >= self.size or self.grid[tx][ty] != self.grid[x][y]:
                    break
                count += 1
            for i in range(1, 5):
                tx, ty = x - i * dx, y - i * dy
                if tx < 0 or tx >= self.size or ty < 0 or ty >= self.size or self.grid[tx][ty] != self.grid[x][y]:
                    break
                count += 1
            if count >= 5:
                return True
        return False

    def has_neighbor(self, x, y):
        """
        Check if the given position has a neighboring piece.
        """
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                tx, ty = x + dx, y + dy
                if tx >= 0 and tx < self.size and ty >= 0 and ty < self.size and self.grid[tx][ty] != 0:
                    return True
        return False

    def count_open(self, x, y):
        """
        Count the number of open rows, columns, and diagonals that the given position belongs to.
        """
        count = 0
        for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            length = 0
            for i in range(-4, 5):
                tx, ty = x + i * dx, y + i * dy
                if tx >= 0 and tx < self.size and ty >= 0 and ty < self.size and self.grid[tx][ty] == 0:
                    length += 1
                else:
                    if length > 0 and (i > 0 or length >= 4):
                        count += 1
                    length = 0
        return count
    
    def get_possible_moves(self):
       
        nearby_moves = []
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0: 
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (1, -1), (-1,1), (1,1), (-1,-1), (-1,0)]: 
                        x, y = i + dx, j + dy
                        if x >= 0 and x < self.size and y >= 0 and y < len(self.grid[x]) and self.grid[x][y] != 0:
                            nearby_moves.append((i, j))
                            break
        return nearby_moves

    def count_immediate_wins(self, player):
        moves = self.get_possible_moves()
        if not moves:
            moves = [
                (row, col)
                for row in range(self.size)
                for col in range(self.size)
                if self.grid[row][col] == 0
            ]
        wins = 0
        for move in moves:
            self.play(player, move)
            if self.is_win(player):
                wins += 1
            self.undo(move)
        return wins
    

    def get_reward(self, player):
        opponent = 3- player
        if self.is_win(player):
            return 1.0
        elif self.is_win(opponent):
            return -1.0
        elif all(cell != 0 for row in self.grid for cell in row):
            return 0.0
        immediate_delta = self.count_immediate_wins(player) - self.count_immediate_wins(opponent)
        return 0.01 * immediate_delta
    

    def print_board(self):
        for bdraw in self.grid:
            print(bdraw)
        print('=' * 45)
