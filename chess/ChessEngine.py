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

    def __init__(self, start_position, end_position, board, enpassant_possible=False, is_castle_move=False):
        self.start_row = start_position[0]
        self.start_column = start_position[1]
        self.end_row = end_position[0]
        self.end_column = end_position[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]
        #  pawn promotion
        self.is_pawn_promotion = False
        if (self.piece_moved == "wp" and self.end_row == 0) or (self.piece_moved == "bp" and self.end_row == 7):
            self.is_pawn_promotion = True

        #  en passant
        self.is_enpassant_move = enpassant_possible
        # if self.piece_moved[1] == "p" and (self.end_row, self.end_column) == enpassant_possible:
        #    self.is_enpassant_move = True
        if self.is_enpassant_move:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"

        self.moveID = self.start_row * 1000 + self.start_column * 100 + self.end_row * 10 + self.end_column

        # castle move
        self.is_castle_move = is_castle_move

    def get_chess_notation(self):
        # Note this is not real chess notation, but simplification
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, row, column):
        return self.columns_to_files[column] + self.rows_to_ranks[row]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


class CastleRights:
    def __init__(self, white_king_side, black_king_side, white_queen_side, black_queen_side):
        self.white_king_side = white_king_side
        self.black_king_side = black_king_side
        self.white_queen_side = white_queen_side
        self.black_queen_side = black_queen_side


"""
Chess engine is responsible for storing all information about chess game.
It needs to determine valid moves, keep game log,
"""


class Game_state:
    # TODO: Game state list - possible improvement
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

        # Check for pinned pieces, for simplicity and efficiency king position is tracked
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)

        self.check_mate = False
        self.stale_mate = False
        self.enpassant_possible = ()  # coordinates for the square where en passant capture is possible
        self.enpassant_possible_log = [self.enpassant_possible]
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.white_king_side,
                                               self.current_castling_rights.black_king_side,
                                               self.current_castling_rights.white_queen_side,
                                               self.current_castling_rights.black_king_side)]

    """
    Takes a Move as parameter and executes it (this will not work for castling, pawn promotion, en-passant)
    """

    def make_move(self, move: Move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved
        self.game_log.append(move)  # logs moves for undoing or history
        self.white_to_move = not self.white_to_move
        # update kings locations
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_column)
        if move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_column)

        # pawn promotion
        if move.is_pawn_promotion:
            # NOTE: Here is not the best place to ask user for piece selection because of legal move generation(check
            # for checks)
            self.board[move.end_row][move.end_column] = move.piece_moved[0] + "Q"

        # en passant
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_column] = "--"  # capturing the pawn

        # update en passant possible variable
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:  # only on 2 square advance
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_column)
        else:
            self.enpassant_possible = ()

        # castle move
        if move.is_castle_move:
            if move.end_column - move.start_column == 2: #king side castle
                self.board[move.end_row][move.end_column - 1] = self.board[move.end_row][move.end_column + 1] # copies the rook in new square
                self.board[move.end_row][move.end_column + 1] = "--" # erase the old rook
            else:  # queen side castle
                self.board[move.end_row][move.end_column + 1] = self.board[move.end_row][move.end_column - 2] # copies the rook in new square
                self.board[move.end_column][move.end_column - 2] = "--" # erase the old rook

        # en passant log
        self.enpassant_possible_log.append(self.enpassant_possible)

        # update castling rights - whenever a king or rook move
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.white_king_side,
                                                   self.current_castling_rights.black_king_side,
                                                   self.current_castling_rights.white_queen_side,
                                                   self.current_castling_rights.black_king_side))



    """
    Undo the last move
    """

    def undo_move(self):
        if len(self.game_log) != 0:  # make sure there is a move to undo
            move = self.game_log.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            self.white_to_move = not self.white_to_move  # switch turns back
            # update kings locations
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_column)
            if move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_column)

            # undo en passant move
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_column] = "--"
                self.board[move.start_row][move.end_column] = move.piece_captured
            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            # undo castling rights
            self.castle_rights_log.pop()  # get rid of the new castle rights from the move we are undoing

            self.current_castling_rights = CastleRights(self.castle_rights_log[-1].white_king_side,
                                                      self.castle_rights_log[-1].black_king_side,
                                                      self.castle_rights_log[-1].white_queen_side,
                                                      self.castle_rights_log[-1].black_queen_side)  # set the current castle rights to the last one in the list

            # undo castle move
            if move.is_castle_move:
                if move.end_column - move.start_column == 2: # king side
                    self.board[move.end_row][move.end_column + 1] = self.board[move.end_row][move.end_column - 1]
                    self.board[move.end_row][move.end_column - 1] = "--"
                else: # queen side
                    self.board[move.end_row][move.end_column - 2] = self.board[move.end_row][move.end_column + 1]
                    self.board[move.end_row][move.end_column + 1] = "--"

            self.check_mate = False
            self.stale_mate = False

    """
    Update the castle rights given the move
    """

    def update_castle_rights(self, move):
        if move.piece_moved == "wK":
            self.current_castling_rights.white_king_side = False
            self.current_castling_rights.white_queen_side = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.black_king_side = False
            self.current_castling_rights.black_queen_side = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_column == 0:  # left rook
                    self.current_castling_rights.white_queen_side = False
                elif move.start_column == 7:  # right rook
                    self.current_castling_rights.white_king_side = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_column == 0:  # left rook
                    self.current_castling_rights.black_queen_side = False
                elif move.start_column == 7:  # right rook
                    self.current_castling_rights.black_king_side = False

        # if a rook is captured
        if move.piece_captured == "wR":
            if move.end_row == 7:
                if move.end_column == 0:
                    self.current_castling_rights.white_queen_side = False
                elif move.end_column == 7:
                    self.current_castling_rights.white_king_side = False
        elif move.piece_captured == "bR":
            if move.end_row == 0:
                if move.end_column == 0:
                    self.current_castling_rights.black_queen_side = False
                elif move.end_column == 7:
                    self.current_castling_rights.black_king_side = False


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
        # Naive algorithm (very inefficient)

        # Since generating moves changes en_passant_possible variable
        # it is crucial to save its state and return it back after move generation
        temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = CastleRights(self.current_castling_rights.white_king_side,
                                          self.current_castling_rights.black_king_side,
                                          self.current_castling_rights.white_queen_side,
                                          self.current_castling_rights.black_queen_side)
        # Generate all possible moves
        moves = self.get_all_possible_moves()
        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        # For each move, make a move
        # We will be removing items from list, to avoid bugs (because indices will shift) we iterate on reverse order
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])

            # Generate all of my opponents moves, and for each check if they can attack your king
            self.white_to_move = not self.white_to_move  # make_move() method switches turns internally!
            if self.in_check():
                # If here we are in check this is not a valid move! We need to remove it from valid moves
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()

        # Check for checkmate or stalemate (if there are no valid moves)
        if len(moves) == 0:
            if self.in_check():
                self.check_mate = True
            else:
                self.stale_mate = True
        else:
            self.check_mate = False
            self.stale_mate = False

        self.enpassant_possible = temp_enpassant_possible  # return saved state
        self.current_castling_rights = temp_castle_rights
        self.castle_rights_log[-1] = CastleRights(self.current_castling_rights.white_king_side,
                                          self.current_castling_rights.black_king_side,
                                          self.current_castling_rights.white_queen_side,
                                          self.current_castling_rights.black_queen_side)
        return moves

    """
    Determines if current player is in check
    """

    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    """
    Determines if the enemy can attack the square at position (row, column)
    """

    def square_under_attack(self, row, column) -> bool:
        # Switch to the opponent turn to see its perspective (opponents moves)
        self.white_to_move = not self.white_to_move
        opponent_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move  # Switch turns back
        for move in opponent_moves:
            if move.end_row == row and move.end_column == column:  # square is under attack
                return True
        return False

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
                elif (row - 1, column - 1) == self.enpassant_possible:  # en passant move
                    moves.append(Move((row, column), (row - 1, column - 1), self.board, enpassant_possible=True))
            if column + 1 <= 7:  # right capture
                if self.board[row - 1][column + 1][0] == 'b':
                    moves.append(Move((row, column), (row - 1, column + 1), self.board))
                elif (row - 1, column + 1) == self.enpassant_possible:  # en passant move
                    moves.append(Move((row, column), (row - 1, column + 1), self.board, enpassant_possible=True))
        else:
            if self.board[row + 1][column] == "--":  # first square move
                moves.append(Move((row, column), (row + 1, column), self.board))
                if row == 1 and self.board[row + 2][column] == "--":  # two square move
                    moves.append(Move((row, column), (row + 2, column), self.board))
            if column - 1 >= 0:  # Left capture, see analogous explanation above
                if self.board[row + 1][column - 1][0] == 'w':
                    moves.append(Move((row, column), (row + 1, column - 1), self.board))
                elif (row + 1, column - 1) == self.enpassant_possible:  # en passant move
                    moves.append(Move((row, column), (row + 1, column - 1), self.board, enpassant_possible=True))
            if column + 1 <= 7:  # right capture
                if self.board[row + 1][column + 1][0] == 'w':
                    moves.append(Move((row, column), (row + 1, column + 1), self.board))
                elif (row + 1, column + 1) == self.enpassant_possible:  # en passant move
                    moves.append(Move((row, column), (row + 1, column + 1), self.board, enpassant_possible=True))
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


    """
    Generate all valid castle moves for the king at (row, column) and add them to the list of moves
    """

    def get_castle_moves(self, row, column, moves):
        if self.square_under_attack(row, column):
            return  # we cant castle when in check
        if (self.white_to_move and self.current_castling_rights.white_king_side) or \
                (not self.white_to_move and self.current_castling_rights.black_king_side):
            self.get_king_side_castle_moves(row, column, moves)
        if (self.white_to_move and self.current_castling_rights.white_queen_side) or \
                (not self.white_to_move and self.current_castling_rights.black_queen_side):
            self.get_queen_side_castle_moves(row, column, moves)

    def get_king_side_castle_moves(self, row, column, moves):
        if self.board[row][column + 1] == "--" and self.board[row][column + 2] == "--":
            if not self.square_under_attack(row, column + 1) and not self.square_under_attack(row, column + 2):
                moves.append(Move((row, column), (row, column + 2), self.board, is_castle_move=True))

    def get_queen_side_castle_moves(self, row, column, moves):
        if self.board[row][column - 1] == "--" and self.board[row][column - 2] == "--" and self.board[row][column - 3] == "--":
            if not self.square_under_attack(row, column - 1) and not self.square_under_attack(row, column - 2):
                moves.append(Move((row, column), (row, column - 2), self.board, is_castle_move=True))
