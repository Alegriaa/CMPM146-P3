from mcts_node import MCTSNode
from random import choice
from math import sqrt, log, inf

num_nodes = 1000
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


    leaf_node = node
    bestScore = 0
    if leaf_node.untried_actions != None:
        if leaf_node.child_nodes != None:
            for child in leaf_node.child_nodes:

                score = uct_evaluation(node.child_nodes[child])

                if(score>bestScore):
                    bestScore = score
                    leaf_node = node.child_nodes[child]

        return leaf_node

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
        calculation = (1 - (node.wins/node.visits)) + 2 * sqrt(log(node.parent.visits) / node.visits)
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
    #While current board of legal actions is not empty, keep iterating
    boardstate = state
    while(board.legal_actions(boardstate)!=[]):
        boardstate = board.next_state(boardstate,choice(board.legal_actions(boardstate)))


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
        print('test')
        print(identity_of_bot)
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!

        #Selection
        while node.untried_actions==[] and node.child_nodes != {}:
            node.visits+=1
            node = traverse_nodes(node, board, sampled_game, identity_of_bot)
            if node.parent_action!=None:
                board.next_state(sampled_game, node.parent_action)
        #Expansion
        if(node.untried_actions != []):
            node = expand_leaf(node, board, sampled_game)
            node = traverse_nodes(node, board, sampled_game, identity_of_bot)
            board.next_state(sampled_game, node.parent_action)

        #Simulate
        rollout(board,sampled_game)
        #figure out who won based on rollout, use var won
        score = board.points_values(sampled_game)

        if score == None:
            winner = 0
        elif score[1] == 1:
            winner = 1
        elif score[2] == 1:
            winner = 2
        
        if identity_of_bot == winner:
            won = True
        else:
            won = False

        #Backpropogate
        backpropagate(node,won)

    
    bestScore = -1

    for child in root_node.child_nodes:
        temp_node = root_node.child_nodes[child]
        if child != None and ((temp_node.wins/temp_node.visits)>bestScore):
            bestScore=(temp_node.wins/temp_node.visits)
            bestAction = child

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    return bestAction
