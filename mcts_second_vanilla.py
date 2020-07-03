from mcts_node import MCTSNode
from random import choice
from math import sqrt, log, inf
import sys
sys.setrecursionlimit(1500)

num_nodes = 10
explore_faction = 2.

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.
    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.
    Returns:        A node from which the next stage of the search can proceed.
    """
    
    if not node.child_nodes:
        node.visits+=1
        return node

    value = None
    leaf_node = None

    for child in node.child_nodes:
        child = node.child_nodes[child]
        value_bound = uct_evaluation(child)
        if value is None or value_bound < bound:
            bound = value_bound
            leaf_node = child

    next_state = board.next_state(state, leaf_node.parent_action)

    return traverse_nodes(leaf_node, board, next_state, board.current_player(next_state))

    # Hint: return leaf_node

def uct_evaluation(node):
    """
        Args:
        node:       A tree node from which the search is traversing.
        Returns:    UCT of given Node
    """
    # (1 - bot's win rate) + 2 * sqrt( ln(n)/ (nj) )
    # n is the number of times the parent has been visited
    # nj is the number of times the child has been visited
    calculation = 0
    if node.visits > 0:
        calculation = (node.wins/node.visits) + 2 * sqrt(log(node.parent.visits) / node.visits)
    return calculation 


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.
    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.
    Returns:    The added child node.
    """
    #Global Var for placeholder Node
    next_move = choice(board.legal_actions(state))
    # returns a new state constructed by applying action in state
    next_state = board.next_state(state, next_move)
    # add new MCTSNode to the three
    new_leaf = MCTSNode(parent=node, parent_action=next_move,
                        action_list=board.legal_actions(next_state))
    node.child_nodes[next_move] = new_leaf

    return new_leaf
    # Hint: return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.
    Args:
        board:  The game setup.
        state:  The state of the game.
    """
    #While current board of legal actions is not empty, keep iterating
    boardstate = state
    while(board.legal_actions(boardstate)!=[]):
        boardstate = board.next_state(boardstate,choice(board.legal_actions(boardstate)))

    score = board.points_values(boardstate)
    state = boardstate

    if score == None:
        winner = 0
        return winner
    elif score[1] == 1:
        winner = 1
        return winner
    elif score[2] == 1:
        winner = 2
        return winner
    


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.
    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.
    """
    while node != None:
        if won:
            node.wins+=1
        node.visits+=1
        node = node.parent


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.
    Args:
        board:  The game setup.
        state:  The state of the game.
    Returns:    The action to be taken.
    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None,
                         action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!

        #Selection
        new_leaf_node = traverse_nodes(node, board, sampled_game, identity_of_bot)
        # Expansion
        expansion_leaf = expand_leaf(new_leaf_node, board, sampled_game)

        #Simulate and assign var to winner
        winner = rollout(board,sampled_game)
        #figure out who won based on rollout, use var won

        #Backpropogate
        backpropagate(expansion_leaf,identity_of_bot == winner)

    
    highscore=-1
    bestAction = None
    for child in root_node.child_nodes:
        child = root_node.child_nodes[child]
        if child.wins/child.visits > highscore:
            highscore = child.wins/child.visits
            bestAction = child.parent_action

    print("Vanilla bot picking %s with expected score %f" % (str(bestAction), highscore))
    return bestAction           
