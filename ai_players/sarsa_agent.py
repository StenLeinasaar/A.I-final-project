import numpy as np
from random import randint
from game_board import Board
from feature_utils import compute_features


class SarsaAgent:
    def __init__(self, epsilon=0.4, alpha=0.5, gamma=1, size=15,weights = [-18, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -18, -0.25] ):
        self.weights = weights
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
            return (self.size // 2, self.size // 2)
        if np.random.uniform() < self.epsilon:
            return moves[randint(0, len(moves) - 1)]
        return self._best_move(board, player)

#     #  Function for updating weights: 
#     '''

#     for each weight in weights: 
    
#         weight  = weight + alpha(gamma + gamma(weight_old * feature_vector(new_State, new_Action) - weight * feature_vectore(state, action))) * feature(state, action) 
    
#     '''
    def update_weights(self, state, action, next_state, next_action, player):
        if state is None or action is None:
            return
        state_features = self._features_for_move(state, player, action)
        q_current = np.dot(self.weights, state_features)
        if next_state is None or next_action is None:
            q_next = 0.0
        else:
            q_next = np.dot(self.weights, self._features_for_move(next_state, player, next_action))
        td_error = self.gamma * q_next - q_current
        self.weights = self.weights + (self.alpha * td_error * state_features)
        self._clip_weights()

    def update_weights_reward(self, state, action, reward, player):
        if state is None or action is None:
            return
        state_features = self._features_for_move(state, player, action)
        q_current = np.dot(self.weights, state_features)
        td_error = reward - q_current
        self.weights = self.weights + (self.alpha * td_error * state_features)
        self._clip_weights()

    def _clip_weights(self):
        for i, weight in enumerate(self.weights):
            if weight >= 20:
                self.weights[i] = 18
            elif weight <= -20:
                self.weights[i] = -18

    def _features_for_move(self, board, player, move):
        board.play(player, move)
        features = compute_features(board, player)
        board.undo(move)
        return features

    def _best_move(self, board, player):
        best_value = None
        best_moves = []
        for move in board.get_possible_moves():
            q_value = np.dot(self.weights, self._features_for_move(board, player, move))
            if best_value is None or q_value > best_value:
                best_value = q_value
                best_moves = [move]
            elif q_value == best_value:
                best_moves.append(move)
        return best_moves[randint(0, len(best_moves) - 1)]
            
    def get_move(self, board:Board, player):

        self.current_state = board

        self.current_action = self.choose_action(board, player)

        if self.previous_state is not None:
            self.update_weights(
                self.previous_state,
                self.previous_action,
                self.current_state,
                self.current_action,
                player,
            )
            

        self.previous_state = self.current_state
        self.previous_action = self.current_action
        return self.current_action
    
    def game_over(self, board:Board, player:int):

        reward = board.get_reward(player)
        self.update_weights_reward(self.previous_state, self.previous_action, reward, player)
        self.previous_state = None
        self.previous_action = None






 
    
      
