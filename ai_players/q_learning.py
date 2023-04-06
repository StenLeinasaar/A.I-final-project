import numpy as np
import math
import sys
from random import randint
from game_board import Board
import os



'''



'''


class QLearning:
    def __init__(self, epsilon=0.4, alpha=0.5, gamma=1, size=15):
        self.weights = [-12,12,-10,10,-6,6]
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.size = size
        self.previous_state = None
        self.current_state = None
        self.previous_action = None
        self.current_action = None

    
    def choose_action(self, board:Board, player):
        moves = board.get_possible_moves()
        if len(moves) == 0:
            return (7,7)
        if np.random.uniform() < self.epsilon:
            return moves[randint(0, len(moves)-1)]
        else:
            q_values = {}
            for move in moves:
                '''
                Should be a tuple of x and y coordinate. It will be in dictionary with its value
                '''
                # Make the move
                board.play(player, move)
                q_values[move] = np.dot(self.weights, self.feature_vector(board, player) )
                # Undo the move
                board.undo(move)

                
            # print(f"sending a move {max(q_values)}")
            return max(q_values)#key=q_values.get)  == send the move back

#     #  Function for updating weights: 
#     '''

#     for each weight in weights: 
    
#         weight  = weight + alpha(gamma + gamma(weight_old * feature_vector(new_State, new_Action) - weight * feature_vectore(state, action))) * feature(state, action) 
    
#     '''

    '''
    for q learning 

    """
        Updates the Q-values for a given state-action pair using the Q-learning algorithm.
        
        Args:
            Q (np.ndarray): The Q-value table.
            state (int): The current state.
            action (int): The current action.
            reward (float): The reward for taking the current action in the current state.
            next_state (int): The next state.
            alpha (float): The learning rate.
            gamma (float): The discount factor.
            
        Returns:
            np.ndarray: The updated Q-value table.
        """
        # Calculate the TD error
        td_error = reward + gamma * np.max(Q[next_state]) - Q[state, action]
        
        # Update the Q-value for the current state-action pair
        Q[state, action] += alpha * td_error
        
        return Q

    '''
    def update_weights(self, state, next_state, player):
        pass

        

        # print(f"weights before updating {self.weights}")

        # new_weights = self.alpha * (self.gamma * (self.weights * self.feature_vector(next_state, player)) - (self.weights * self.feature_vector(state, player)) * self.feature_vector(state, player))
        # # print(f"the new weights are {new_weights}")
        # for i, weight in enumerate(self.weights):
        #     self.weights[i] = weight +  new_weights[i]
        #     if self.weights[i] >= 20:
        #         self.weights[i] = 18
        #     elif self.weights[i] <= -20:
        #         self.weights[i] = -18
        # print(f"updated weights are {self.weights}")

    def update_weights_reward(self, state, next_state, reward,player):
        pass
        # print(f"weights before updating {self.weights}")

        # new_weights = self.alpha * (reward + self.gamma * (self.weights * self.feature_vector(next_state, player)) - (self.weights * self.feature_vector(state, player)) * self.feature_vector(state, player))
        # # print(f"the new weights are {new_weights}")
        # for i, weight in enumerate(self.weights):
        #     self.weights[i] = weight +  new_weights[i]
        #     if self.weights[i] >= 20:
        #         self.weights[i] = 18
        #     elif self.weights[i] <= -20:
        #         self.weights[i] = -18
        # print(f"updated weights are {self.weights}")

    def feature_vector(self, board:Board, player):
        opponent = 3 - player
        features = np.zeros(6)
        # iterate over each cell of the board
        for i in range(board.size):
            for j in range(board.size):
                # # if the cell is empty, append a 0 to the feature vector
                # if board.grid[i][j] == 0:
                #     features.append(0)
                # else:
                #     # if the cell contains a player's piece, append a 1 to the feature vector
                #     features.append(1)
                
                # Feature of how many straight line of four pieces opponent has
                # add feature to detect straight line of four pieces
                for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1)]:
                    count = 0
                    for k in range(-3, 1):
                        x = i + k*dx
                        y = j + k*dy
                        if x >= 0 and x < board.size and y >= 0 and y < board.size and board.grid[x][y] == opponent:
                            count += 1
                    if count == 4:
                        features[0] -= 1


                # feature of how many fours pieces in a line for the player

                for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1)]:
                    count = 0
                    for k in range(-3, 1):
                        x = i + k*dx
                        y = j + k*dy
                        if x >= 0 and x < board.size and y >= 0 and y < board.size and board.grid[x][y] == player:
                            count += 1
                    if count == 4:
                        features[1] += 1

                

            
                #feature of number of open threes opponent has
                for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1)]:
                    count = 0
                    for k in range(-2, 1):
                        x = i + k*dx
                        y = j + k*dy
                        if x >= 0 and x < board.size and y >= 0 and y < board.size and board.grid[x][y] == opponent:
                            count += 1
                    if count == 3:
                        features[2] -= 1


                # Feature of numbre of open threes player has

                for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1)]:
                    count = 0
                    for k in range(-2, 1):
                        x = i + k*dx
                        y = j + k*dy
                        if x >= 0 and x < board.size and y >= 0 and y < board.size and board.grid[x][y] == player:
                            count += 1
                    if count == 3:
                        features[3] += 1


                #feature of number of open twos/ possible open threes for the opponent
                for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1)]:
                    count = 0
                    for k in range(-1, 1):
                        x = i + k*dx
                        y = j + k*dy
                        if x >= 0 and x < board.size and y >= 0 and y < board.size and board.grid[x][y] == opponent:
                            count += 1
                    if count == 2:
                        features[4] -= 1

                # feature of number of open twos/possible open threes for the player
                for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1)]:
                    count = 0
                    for k in range(-1, 1):
                        x = i + k*dx
                        y = j + k*dy
                        if x >= 0 and x < board.size and y >= 0 and y < board.size and board.grid[x][y] == opponent:
                            count += 1
                    if count == 2:
                        features[5] += 1

                
                
                # add feature to capture influence map
                # player_influence = np.zeros((self.size, self.size))
                # opponent_influence = np.zeros((self.size, self.size))
                # for x in range(board.size):
                #     for y in range(board.size):
                #         if board.grid[x][y] != 0:
                #             if board.grid[x][y] == 1:
                #                 influence_map = player_influence
                #             else:
                #                 influence_map = opponent_influence
                #             for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1)]:
                #                 for k in range(1, 4):
                #                     i = x + k*dx
                #                     j = y + k*dy
                #                     if i >= 0 and i < board.size and j >= 0 and j < board.size:
                #                         influence_map[i][j] += 1 / k
                # features.extend(player_influence.flatten())
                # features.extend(opponent_influence.flatten())
                
                # # add feature to capture mobility
                # player_mobility = np.zeros((self.size, self.size))
                # opponent_mobility = np.zeros((self.size, self.size))
                # for x in range(board.size):
                #     for y in range(board.size):
                #         if board.grid[x][y] == 0:
                #             for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1)]:
                #                 i = x + dx
                #                 j = y + dy
                #                 if i >= 0 and i < board.size and j >= 0 and j < board.size:
                #                     if board.grid[i][j] == 1:
                #                         mobility_map = player_mobility
                #                     elif board.grid[i][j] == -1:
                #                         mobility_map = opponent_mobility
                #                     else:
                #                         continue
                #                     for k in range(2, 5):
                #                         i = x + k*dx
                #                         j = y + k*dy
                #                         if i >= 0 and i < board.size and j >= 0 and j < board.size and board.grid[i][j] == 0:
                #                             mobility_map[x][y] += 1 / k
                # features.extend(player_mobility.flatten())
                # features.extend(opponent_mobility.flatten())

                # add feature to capture positional features
                # center_x = board.size // 2
                # center_y = board.size // 2
                # distance from center
                # distance = math.sqrt((i - center_x)**2 + (j - center_y)**2)
                # features.append(distance)
               
                return features
            
    def get_move(self, board:Board, player):

        self.current_state = board

        self.current_action = self.choose_action(board, player)

        if self.previous_state != None:
            self.update_weights(self.previous_state, self.current_state, player)
            

        self.previous_state = self.current_state
        self.previous_action = self.current_action
        # print(f"sending a move {self.current_action} ")
        return self.current_action
    
    def game_over(self, board:Board, player:int):

        reward = self.alpha * (board.get_reward(player))
        self.update_weights_reward(self.previous_state, self.current_state, reward, player)
        # update weight based on reward. Question...
            





 
    
      