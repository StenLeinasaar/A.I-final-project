from node import Node


def max_val(node: Node, depth: int, alpha: int, beta: int) -> int:
    if depth == 0 or node.state in [0,-1,1]: # or (node is either draw, lose or win.
        return evaluate(node)
    best_value = -float("inf")
    for child in node.children:
        value = max_val(child, depth-1, alpha, beta, False)
        best_value = max(best_value, value)
        alpha = max(alpha, best_value)
        
        if beta <= alpha:
            break
    return best_value




def min_val(node: Node, depth: int, alpha: int, beta: int) -> int:
    if depth == 0 or node.state in [0,-1,1]: # or (node is either draw, lose or win.
        return evaluate(node)

    best_value = float("inf")
    for child in node.children:
        value = min_val(child, depth-1, alpha, beta, True)
        best_value = min(best_value, value)
        beta = min(beta, best_value)
        if beta <= alpha:
            break
    return best_value

# driver function
def alpha_beta_pruning(node:Node, depth:int, alpha:int, beta:int, maximizingPlayer:bool):
    return max_val(node,depth,alpha, beta) if maximizingPlayer else min_val(node,depth,alpha, beta)

def evaluate(node):
    pass


