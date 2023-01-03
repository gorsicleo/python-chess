class Move:
    ranks_to_rows = {
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 0
    }

    files_to_columns = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7
    }

    rows_to_ranks = {
        v: k for k, v in ranks_to_rows.items()  # reversing a dictionary
    }

    columns_to_files = {
        v: k for k, v in files_to_columns.items()  # reversing a dictionary
    }

    def __init__(self, start_position, end_position, board):
        self.start_row = start_position[0]
        self.start_column = start_position[1]
        self.end_row = end_position[0]
        self.end_column = end_position[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]

    def get_chess_notation(self):
        # Note this is not real chess notation, but simplification
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, row, column):
        return self.columns_to_files[column] + self.rows_to_ranks[row]


"""
Chess engine is responsible for storing all information about chess game.
It needs to determine valid moves, keep game log,
"""


class Game_state:

    def __init__(self):
        # Board is represented with 2D array of strings. Blank position is denoted by "--" string.
        # Regularly, position is denoted with two letters. First letter (b or w) stands for color
        # Second letter is the piece (Rook, Knight, Bishop, Queen, King)
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.white_to_move = True
        self.game_log = []

    def make_move(self, move: Move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved
        self.game_log.append(move) # logs moves for undoing or history
        self.white_to_move = not self.white_to_move
