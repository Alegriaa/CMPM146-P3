from typing import Any, Union

from mcts_node import MCTSNode
from random import choice
from math import sqrt, log, inf

num_nodes = 100


# def evaluate_node(node):
#     """
#     This function evaluates a node following the formula seen in class
#     """
#     evaluation = 0
#     if (node.visits != 0):
#         evaluation = (node.wins / node.visits) + 2 * sqrt(log(node.parent.visits) / node.visits)
#     return evaluation


def traverse_leafs(node, optimal_node):
    if node.untried_actions:
        if optimal_node is None:
            optimal_node = node
        if node.parent is not None:
            utc_node: Union[Union[float, int], Any] = uct_evaluation(node)
            utc_optimal: Union[Union[float, int], Any] = uct_evaluation(optimal_node)
            if utc_node > utc_optimal:
                optimal_node = node
    else:
        if node.child_nodes:
            for key, child in node.child_nodes.items():
                optimal_node = traverse_leafs(child, optimal_node)
    return optimal_node


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
        calculation = (1 - node.wins) + 2 * sqrt(log(node.parent.visits) / node.visits)
    return calculation


def traverse_nodes(node):
    """ Traverses the tree until the end criterion are met.
    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.
    Returns:        A node from which the next stage of the search can proceed.
    """

    optimal_node = None
    leaf_node = None
    leaf_node = traverse_leafs(node, optimal_node)
    return leaf_node
    # Hint: return leaf_node


# def traverse_nodes(node, board, state, identity):
#     """ Traverses the tree until the end criterion are met.
#
#     Args:
#         node:       A tree node from which the search is traversing.
#         board:      The game setup.
#         state:      The state of the game.
#         identity:   The bot's identity, either 'red' or 'blue'.
#
#     Returns:        A node from which the next stage of the search can proceed.
#
#     """
#     optimal_node = MCTSNode(parent=None, parent_action=None,
#                          action_list=board.legal_actions(state))
#     leaf_node = node
#     if leaf_node.untried_actions != None:
#         if leaf_node.child_nodes != None:
#             for value, child in leaf_node.child_nodes.items():
#                 uct_eval = traverse_nodes(child, board, state, identity)
#
#         if node.parent:
#             red = uct_evaluation(leaf_node)
#             blue = uct_evaluation(optimal_node)
#
#             if blue < red:
#                 optimal_node = node
#         print('returned op')
#         return optimal_node
#
#     else:
#         print('returned non op')
#         return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """

    next_move = node.untried_actions.pop(0)
    # returns a new state constructed by applying action in state
    state = board.next_state(state, next_move)
    # add new MCTSNode to the three
    new_leaf = MCTSNode(parent=node, parent_action=next_move,
                        action_list=board.legal_actions(state))
    node.child_nodes[next_move] = new_leaf

    return new_leaf
    # Hint: return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

   """

    moves = board.legal_actions(state)
    rollout_state = state
    sim_score = {}
    while not board.is_ended(rollout_state):
        rollout_state = board.next_state(rollout_state, choice(moves))
        moves = board.legal_actions(rollout_state)
        sim_score = board.points_values(rollout_state)
    return sim_score


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    while (node.parent != None):
        node.visits += 1
        if (won == True):
            node.wins += 1
        node = node.parent
    node.visits += 1
    if (won == True):
        node.wins += 1


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

        # Selection
        new_leaf_node = traverse_nodes(node)
        if new_leaf_node is None:
            break
        # Expansion
        expansion_leaf = expand_leaf(new_leaf_node, board, sampled_game)
        # Simulate
        sim_score = rollout(board, sampled_game)

        game_won = False
        if (identity_of_bot == 1 and sim_score is {1: 1, 2: -1}) or (
                identity_of_bot == 2 and sim_score is {1: -1, 2: 1}):
            game_won = True
        # Backpropogate
        backpropagate(expansion_leaf, game_won)
        # MCTS completed!

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate
    best_action = None
    for value, child in root_node.child_nodes.items():
        if best_action is None or child.visits > best_action.visits:
            best_action = child
    return best_action.parent_action
