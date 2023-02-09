class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)