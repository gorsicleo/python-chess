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
        self.moveID = self.start_row * 1000 + self.start_column * 100 + self.end_row * 10 + self.end_column

    def get_chess_notation(self):
        # Note this is not real chess notation, but simplification
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, row, column):
        return self.columns_to_files[column] + self.rows_to_ranks[row]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


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

        self.moveFunctions = {
            'p': self.get_pawn_moves,
            'R': self.get_rook_moves,
            'N': self.get_knight_moves,
            'B': self.get_bishop_moves,
            'Q': self.get_queen_moves,
            'K': self.get_king_moves
        }
        self.white_to_move = True
        self.game_log = []

    """
    Takes a Move as parameter and executes it (this will not work for castling, pawn promotion, en-passant)
    """

    def make_move(self, move: Move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved
        self.game_log.append(move)  # logs moves for undoing or history
        self.white_to_move = not self.white_to_move

    """
    Undo the last move
    """

    def undo_move(self):
        if len(self.game_log) != 0:  # make sure there is a move to undo
            move = self.game_log.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            self.white_to_move = not self.white_to_move  # switch turns back

    """
    All moves considering checks.
    Basic algorithm is the following:
    - get all possible moves
    - for each possible move, check to see if it is a valid move by doing the following:
        - make the move
        - generate all possible moves for the opposing player
        - see if any of the moves attack your king
        - if your king is safe, it is a valid move and add it to a list
    - return the list of valid moves only
    """

    def get_valid_moves(self):
        return self.get_all_possible_moves()  # for now we will not worry about checks

    """
    All moves without considering checks
    """

    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                turn = self.board[row][column][0]  # get first character -> Color indicator
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[row][column][1]  # get the piece

                    self.moveFunctions[piece](row, column, moves)  # This calls appropriate move functions based on keys
        return moves

    """
    Get all the pawn moves for the pawn at location (row, column), add these moves to the list
    """

    def get_pawn_moves(self, row, column, moves):
        if self.white_to_move:  # focus on white pawn moves
            if self.board[row - 1][column] == "--":  # if one square in front is empty append it to move list
                moves.append(Move((row, column), (row - 1, column), self.board))
                if row == 6 and self.board[row - 2][column] == "--":  # two square pawn advance
                    moves.append(Move((row, column), (row - 2, column), self.board))
            if column - 1 >= 0:  # Note, we don't want to check negative columns and this check is independent since
                # it is diagonal move (left capture)
                if self.board[row - 1][column - 1][0] == 'b':  # There is piece of opposite color to capture
                    moves.append(Move((row, column), (row - 1, column - 1), self.board))
            if column + 1 <= 7:  # right capture
                if self.board[row - 1][column + 1][0] == 'b':
                    moves.append(Move((row, column), (row - 1, column + 1), self.board))
        else:
            if self.board[row + 1][column] == "--":  # first square move
                moves.append(Move((row, column), (row + 1, column), self.board))
                if row == 1 and self.board[row + 2][column] == "--":  # two square move
                    moves.append(Move((row, column), (row + 2, column), self.board))
            if column - 1 >= 0:  # Left capture, see analogous explanation above
                if self.board[row + 1][column - 1][0] == 'w':
                    moves.append(Move((row, column), (row + 1, column - 1), self.board))
            if column + 1 <= 7:  # right capture
                if self.board[row + 1][column + 1][0] == 'w':
                    moves.append(Move((row, column), (row + 1, column + 1), self.board))
            # TODO: Pawn promotion!

    """
    Get all the rook moves for the rook at location (row, column), add these moves to the list
    """

    def get_rook_moves(self, row, column, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if self.white_to_move else "w"
        for direction in directions:
            for square_number in range(1, 8):
                end_row = row + direction[0] * square_number
                end_column = column + direction[1] * square_number

                if 0 <= end_row < 8 and 0 <= end_column < 8:  # check if that position is on board
                    end_piece = self.board[end_row][end_column]
                    if end_piece == "--":  # if that position is empty then move to this position is valid
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                    elif end_piece[0] == enemy_color:  # this move is also valid because enemy piece can be captured!
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                        break  # after capture no further scan is necessary because I cant jump over that piece
                    else:
                        break  # this is possibly our piece that we cannot capture
                else:
                    break  # Positions that are off board should not be scanned

    """
    Get all the knight moves for the rook at location (row, column), add these moves to the list
    """

    def get_knight_moves(self, row, column, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for move in knight_moves:
            end_row = row + move[0]
            end_column = column + move[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                end_piece = self.board[end_row][end_column]
                # Enemy piece can be captured, or I can move to empty square
                if end_piece[0] == enemy_color or end_piece == "--":
                    moves.append(Move((row, column), (end_row, end_column), self.board))

    """
    Get all the bishop moves for the rook at location (row, column), add these moves to the list
    """

    def get_bishop_moves(self, row, column, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # top-left, top-right, bottom-left, bottom-right
        enemy_color = "b" if self.white_to_move else "w"
        for direction in directions:
            for square_number in range(1, 8):
                end_row = row + direction[0] * square_number
                end_column = column + direction[1] * square_number

                if 0 <= end_row < 8 and 0 <= end_column < 8:  # check if that position is on board
                    end_piece = self.board[end_row][end_column]
                    if end_piece == "--":  # if that position is empty then move to this position is valid
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                    elif end_piece[0] == enemy_color:  # this move is also valid because enemy piece can be captured!
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                        break  # after capture no further scan is necessary because I cant jump over that piece
                    else:
                        break  # this is possibly our piece that we cannot capture
                else:
                    break  # Positions that are off board should not be scanned

    """
    Get all the queen moves for the rook at location (row, column), add these moves to the list
    """

    def get_queen_moves(self, row, column, moves):
        self.get_rook_moves(row, column, moves)
        self.get_bishop_moves(row, column, moves)

    """
    Get all the king moves for the rook at location (row, column), add these moves to the list
    """

    def get_king_moves(self, row, column, moves):
        # king can move any square arond him (but only one square)
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for move in range(8):
            end_row = row + king_moves[move][0]
            end_column = column + king_moves[move][1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                end_piece = self.board[end_row][end_column]
                # King can capture enemy piece or move to the empty square
                if end_piece[0] == enemy_color or end_piece == "--":
                    moves.append(Move((row, column), (end_row, end_column), self.board))

