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
