"""
This is main driver. Contains current game state in GameState object.
It is responsible for handling user input current state.
"""
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame as game
from multiprocessing import Process, Queue
from chess import ChessEngine, ChessAIEngine

# Globals
BOARD_WIDTH = BOARD_HEIGHT = 400
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

"""
This method initializes images dictionary.
Since this is expensive operation it should be only called once during game startup.
"""


def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]

    for piece in pieces:
        IMAGES[piece] = game.transform.scale(game.image.load("images/{}.png".format(piece)), (SQUARE_SIZE, SQUARE_SIZE))


def main():
    game.init()
    screen = game.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = game.time.Clock()
    screen.fill(game.Color("white"))
    default_move_log_font = game.font.SysFont("Arial", 12, False, False)
    game_state = ChessEngine.Game_state()
    valid_moves = game_state.get_valid_moves()
    move_made = False  # flag variable for when a move is made
    animate = False  # flag variable for when we should animate a move
    load_images()
    running = True

    square_selected = ()  # initailly no square is selected, keeps track of the last click of the user (row,column)
    player_clicks = []  # keeps track of player clicks, contains two tuples
    # [(row_start, column_start), (row_end,column_end)]
    game_over = False
    player_one = True  # If a human is playing white, this will be true. If AI is playing then it will be false
    player_two = False  # TODO: change to int to express difficulty
    AI_thinking = False
    move_finder_process = None
    move_undone = False
    while running:
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
        for event in game.event.get():
            if event.type == game.QUIT:
                running = False
                # mouse handler
            elif event.type == game.MOUSEBUTTONDOWN:  # adding event handles for mouse clicks
                if not game_over and human_turn:
                    location = game.mouse.get_pos()  # (x,y) location of pointer
                    column = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if square_selected == (row, column) or column >= 8:  # user clicked same square twice or user clicked game log, unselect
                        square_selected = ()  # deselect
                        player_clicks = []  # clear player clicks
                    else:
                        square_selected = (row, column)
                        player_clicks.append(square_selected)  # append for both 1st and 2nd clicks
                    if len(player_clicks) == 2:  # after second click
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):

                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()  # reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]  # Fix for wasted click when my second click was on my piece
            # key handlers
            elif event.type == game.KEYDOWN:
                if event.key == game.K_z:  # undo when 'z' is pressed
                    game_state.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                    if AI_thinking:
                        move_finder_process.terminate()
                        AI_thinking = False
                    move_undone = True
                if event.key == game.K_r:  # reset when 'r' is pressed
                    game_state = ChessEngine.Game_state()
                    valid_moves = game_state.get_valid_moves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if AI_thinking:
                        move_finder_process.terminate()
                        AI_thinking = False
                    move_undone = True

        # AI move finder logic
        if not game_over and not human_turn and not move_undone:
            if not AI_thinking:
                AI_thinking = True
                print("Status: Thinking...")
                return_queue = Queue() # Used to pass data between threads
                move_finder_process = Process(target=ChessAIEngine.find_best_move, args=(game_state, valid_moves, return_queue))
                move_finder_process.start() # Calls find_best_move with parameters
            if not move_finder_process.is_alive():
                print("Status: Done Thinking...")
                AI_move = return_queue.get()
                if AI_move is None:
                    AI_move = ChessAIEngine.find_random_move(valid_moves)
                game_state.make_move(AI_move)
                move_made = True
                animate = True
                AI_thinking = False

        # Since generating valid moves is expensive, generating is only done after a valid move!
        if move_made:
            if animate:
                animate_move(game_state.game_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.get_valid_moves()
            move_made = False
            animate = False
            move_undone = False
        draw_game_state(screen, game_state, valid_moves, square_selected, default_move_log_font)

        if game_state.check_mate or game_state.stale_mate:
            game_over = True
            text = "Stalemate" if game_state.stale_mate else "Black wins by checkmate" if game_state.white_to_move else "White wins by checkmate"
            draw_end_game_text(screen, text)

        clock.tick(MAX_FPS)
        game.display.flip()


"""
Highlight square selected and moves for piece selected
"""


def highlight_squares(screen, game_state, valid_moves, square_selected):
    if square_selected != ():
        row, column = square_selected
        if game_state.board[row][column][0] == (
        "w" if game_state.white_to_move else "b"):  # sq selected is a piece that can be moved
            # highlight selected square
            surface = game.Surface((SQUARE_SIZE, SQUARE_SIZE))
            surface.set_alpha(100)  # 0 - transparent, 255 - opaque
            surface.fill("blue")
            screen.blit(surface, (column * SQUARE_SIZE, row * SQUARE_SIZE))
            # highlight moves from that square
            surface.fill(game.Color("yellow"))
            for move in valid_moves:
                if move.start_row == row and move.start_column == column:
                    screen.blit(surface, (SQUARE_SIZE * move.end_column, SQUARE_SIZE * move.end_row))


"""
Responsible for all graphic in game.
Note that order of calling is important! Board must be drawn before pieces!
"""


def draw_game_state(screen, game_state, valid_moves, square_selected, move_log_font):
    draw_board(screen)
    highlight_squares(screen, game_state, valid_moves, square_selected)
    draw_pieces(screen, game_state.board)
    draw_move_log(screen, game_state, move_log_font)

'''
Draws the move log
'''
def draw_move_log(screen, game_state, font):
    move_log_rect = game.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    game.draw.rect(screen, game.Color("black"), move_log_rect)
    move_log = game_state.game_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + ". " + str(move_log[i]) + " "
        if i + 1 < len(move_log): # make sure black made a move
            move_string += str(move_log[i + 1]) + " "
        move_texts.append(move_string)
    padding = 5
    moves_per_row = 3
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i+j]
        text_object = font.render(text, True, game.Color("White"))
        text_loc = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_loc)
        text_y += text_object.get_height()

"""
Draws squares on the board. Top-left square is light (no matter of perspective!)
"""


def draw_board(screen):
    global board_colors
    board_colors = [game.Color("white"), game.Color("light blue")]

    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = board_colors[(row + column) % 2]
            game.draw.rect(screen, color, game.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


"""
Draws pieces on top of the squares
"""


def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]

            if piece != "--":
                screen.blit(IMAGES[piece], game.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def animate_move(move, screen, board, clock):
    global board_colors
    delta_row = move.end_row - move.start_row
    delta_column = move.end_column - move.start_column
    frames_per_square = 10
    frame_count = (abs(delta_row) + abs(delta_column)) * frames_per_square
    for frame in range(frame_count + 1):
        row, column = (
        move.start_row + delta_row * frame / frame_count, move.start_column + delta_column * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)

        # erase the piece moved from its ending square
        color = board_colors[(move.end_row + move.end_column) % 2]
        end_square = game.Rect(move.end_column * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        game.draw.rect(screen, color, end_square)

        if move.piece_captured != "--":
            if move.is_enpassant_move:
                en_passant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = game.Rect(move.end_column * SQUARE_SIZE, en_passant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

            screen.blit(IMAGES[move.piece_captured], end_square)

        screen.blit(IMAGES[move.piece_moved],
                    game.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        game.display.flip()
        clock.tick(60)

def draw_end_game_text(screen, text):
    font = game.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, 0, game.Color("Black"))
    text_loc = game.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2, BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_loc)
if __name__ == "__main__":
    main()
