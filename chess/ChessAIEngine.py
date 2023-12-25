import random

piece_score = {"K":0, "Q":10, "R":5, "B":3, "N":3, "p":1}
checkmate = 1000
stalemate = 0
max_depth = 3
def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def find_best_move(game_state, valid_moves):
    opponent_min_max_score = checkmate
    best_move = None
    best_player_move = None
    random.shuffle(valid_moves)
    turn_multiplier = 1 if game_state.white_to_move else -1
    for player_move in valid_moves:
        game_state.make_move(player_move)
        opponent_moves = game_state.get_valid_moves()
        if game_state.stale_mate:
            opponent_max_score = stalemate
        elif game_state.check_mate:
            opponent_max_score = -checkmate
        else:
            opponent_max_score = -checkmate

            for opponent_move in opponent_moves:
                game_state.make_move(opponent_move)
                game_state.get_valid_moves()
                if game_state.check_mate:
                    score = checkmate
                elif game_state.stale_mate:
                    score = stalemate
                else:
                    score = -turn_multiplier * score_material(game_state.board)
                if score > opponent_max_score:
                    opponent_max_score = score
                game_state.undo_move()
        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move
        game_state.undo_move()
    return  best_player_move

'''
Helper method calls initial recursive call and return result
'''
def find_best_move_min_max(game_state, valid_moves):
    global next_move
    next_move = None
    find_move_min_max(game_state, valid_moves,max_depth, game_state.white_to_move)
    return next_move

def find_move_min_max(game_state,valid_moves,depth,white_to_move):
    global next_move
    if depth == 0:
        return score_material(game_state.board)

    if white_to_move:
        max_score = -checkmate
        for move in valid_moves:
            game_state.make_move(move)
            next_moves = game_state.get_valid_moves()
            score = find_move_min_max(game_state, next_moves, depth - 1, False)

            if score > max_score:
                max_score = score
                if depth == max_depth:
                    next_move = move
            game_state.undo_move()
        return max_score
    else:
        min_score = checkmate
        for move in valid_moves:
            game_state.make_move(move)
            next_moves = game_state.get_valid_moves()
            score = find_move_min_max(game_state, next_moves, depth - 1, True)

            if score < min_score:
                min_score = score
                if depth == max_depth:
                    next_move = move
            game_state.undo_move()
        return min_score



'''
A positive score is good for white.
Negative score is good for black.
'''
def score_board(game_state):
    if game_state.check_mate:
        if game_state.white_to_move:
            return -checkmate # Black wins
        else:
            return checkmate # White wins

    elif game_state.stale_mate:
        return stalemate
    score = 0
    for row in game_state.board:
        for square in row:
            if square[0] == "w":
                score += piece_score[square[1]]
            elif square[0] == "b":
                score -= piece_score[square[1]]
    return score
def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += piece_score[square[1]]
            elif square[0] == "b":
                score -= piece_score[square[1]]
    return score
