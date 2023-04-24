"""
This is main driver. Contains current game state in GameState object.
It is responsible for handling user input current state.
"""

import pygame as game
from chess import ChessEngine

# Globals
WIDTH = HEIGHT = 400
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
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
    screen = game.display.set_mode((WIDTH, HEIGHT))
    clock = game.time.Clock()
    screen.fill(game.Color("white"))
    game_state = ChessEngine.Game_state()
    valid_moves = game_state.get_valid_moves()
    move_made = False  # flag variable for when a move is made
    load_images()
    running = True

    square_selected = ()  # initailly no square is selected, keeps track of the last click of the user (row,column)
    player_clicks = []  # keeps track of player clicks, contains two tuples
    # [(row_start, column_start), (row_end,column_end)]

    while running:
        for event in game.event.get():
            if event.type == game.QUIT:
                running = False
                # mouse handler
            elif event.type == game.MOUSEBUTTONDOWN:  # adding event handles for mouse clicks
                location = game.mouse.get_pos()  # (x,y) location of pointer
                column = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE
                if square_selected == (row, column):  # user clicked same square twice, unselect
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
                            square_selected = ()  # reset user clicks
                            player_clicks = []
                    if not move_made:
                        player_clicks = [square_selected]  # Fix for wasted click when my second click was on my piece
            # key handlers
            elif event.type == game.KEYDOWN:
                if event.key == game.K_z:  # undo when 'z' is pressed
                    game_state.undo_move()
                    move_made = True
        # Since generating valid moves is expensive, generating is only done after a valid move!
        if move_made:
            valid_moves = game_state.get_valid_moves()
            move_made = False
        draw_game_state(screen, game_state)
        clock.tick(MAX_FPS)
        game.display.flip()


"""
Responsible for all graphic in game.
Note that order of calling is important! Board must be drawn before pieces!
"""


def draw_game_state(screen, game_state):
    draw_board(screen)
    draw_pieces(screen, game_state.board)


"""
Draws squares on the board. Top-left square is light (no matter of perspective!)
"""


def draw_board(screen):
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


if __name__ == "__main__":
    main()
