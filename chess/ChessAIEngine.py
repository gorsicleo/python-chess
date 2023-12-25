import random

piece_score = {"K":0, "Q":10, "R":5, "B":3, "N":3, "p":1}
checkmate = 1000
stalemate = 0
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

def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += piece_score[square[1]]
            elif square[0] == "b":
                score -= piece_score[square[1]]
    return score
