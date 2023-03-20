class Node:
    def __init__(self,alpha, beta, state, game_board, parent=None, move=None):
        self.state = state #if state is 0 = draw, -1 loss, or +1 for win
        self.parent = parent
        self.move = move
        self.game_board = game_board
        self.children = []
        self.alpha = alpha
        self.beta = beta

    def add_child(self, child_node):
        self.children.append(child_node)

    def get_children(self):
        return self.children

    def get_parent(self):
        return self.parent
    
    def set_alpha(self, alpha):
        self.alpha = alpha

    def get_alpha(self):
        return self.alpha

    def set_beta(self, beta):
        self.beta = beta

    def get_beta(self):
        return self.beta
    
    def get_state(self):
        return self.state


