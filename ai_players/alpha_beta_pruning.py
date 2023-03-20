from node import Node


def max_val(node: Node, depth: int, alpha: int, beta: int) -> int:
    if depth == 0 or node.get_state() in [0,-1,1]: # or (node is either draw, lose or win.
        return evaluate(node)
    best_value = -float("inf")
    children = node.get_children()
    for child in children:
        value = max_val(child, depth-1, node.get_alpha(), node.get_beta())
        best_value = max(best_value, value)
        node.set_alpha(max(node.get_alpha(), best_value))
        if node.get_beta() <= node.get_alpha():
            break
    return best_value




def min_val(node: Node, depth: int, alpha: int, beta: int) -> int:
    if depth == 0 or node.get_state() in [0,-1,1]: # or (node is either draw, lose or win.
        return evaluate(node)

    best_value = float("inf")
    children = node.get_children()
    for child in children:
        value = min_val(child, depth-1, node.get_alpha(), node.get_beta())
        best_value = min(best_value, value)
        node.set_beta(min(beta, best_value))
        if node.get_beta() <= node.get_alpha():
            break
    return best_value

# driver function
def alpha_beta_pruning(node:Node, depth:int, alpha:int, beta:int, maximizingPlayer:bool):
    return max_val(node,depth,alpha, beta) if maximizingPlayer else min_val(node,depth,alpha, beta)


# node state can be set here
def evaluate(node):
    pass



# def max_val(node: Node, depth: int, alpha: int, beta: int) -> int:
#     if depth == 0 or node.state in [0,-1,1]: # or (node is either draw, lose or win.
#         return evaluate(node)
#     best_value = -float("inf")
#     for child in node.children:
#         value = max_val(child, depth-1, alpha, beta)
#         best_value = max(best_value, value)
#         alpha = max(alpha, best_value)
#         if beta <= alpha:
#             break
#     return best_value




# def min_val(node: Node, depth: int, alpha: int, beta: int) -> int:
#     if depth == 0 or node.state in [0,-1,1]: # or (node is either draw, lose or win.
#         return evaluate(node)

#     best_value = float("inf")
#     for child in node.children:
#         value = min_val(child, depth-1, alpha, beta)
#         best_value = min(best_value, value)
#         beta = min(beta, best_value)
#         if beta <= alpha:
#             break
#     return best_value


