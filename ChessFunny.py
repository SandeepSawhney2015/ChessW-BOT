import pygame
import sys
import copy

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
BOARD_SIZE = 8
SQUARE_SIZE = SCREEN_WIDTH // BOARD_SIZE
LIGHT_COLOR = (255, 204, 173)
DARK_COLOR = (143, 69, 20)
BACKGROUND_COLOR = (0, 0, 0)
HIGHLIGHT_COLOR = (0, 255, 0)
CAPTURE_HIGHLIGHT_COLOR = (255, 0, 0)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Load chess piece images
piece_images = {
    "wp": pygame.image.load('/Users/sandeepsawhney/Desktop/VSCode/pygameTest/Project Chess/Assets/White/w_pawn_svg_withShadow.png'),
    "wr": pygame.image.load('/Users/sandeepsawhney/Desktop/VSCode/pygameTest/Project Chess/Assets/White/w_rook_svg_withShadow.png'),
    "wn": pygame.image.load('/Users/sandeepsawhney/Desktop/VSCode/pygameTest/Project Chess/Assets/White/w_knight_svg_withShadow.png'),
    "wb": pygame.image.load('/Users/sandeepsawhney/Desktop/VSCode/pygameTest/Project Chess/Assets/White/w_bishop_svg_withShadow.png'),
    "wq": pygame.image.load('/Users/sandeepsawhney/Desktop/VSCode/pygameTest/Project Chess/Assets/White/w_queen_svg_withShadow.png'),
    "wk": pygame.image.load('/Users/sandeepsawhney/Desktop/VSCode/pygameTest/Project Chess/Assets/White/w_king_svg_withShadow.png'),
    "bp": pygame.image.load('/Users/sandeepsawhney/Desktop/VSCode/pygameTest/Project Chess/Assets/Black/b_pawn_svg_withShadow.png'),
    "br": pygame.image.load('/Users/sandeepsawhney/Desktop/VSCode/pygameTest/Project Chess/Assets/Black/b_rook_svg_withShadow.png'),
    "bn": pygame.image.load('/Users/sandeepsawhney/Desktop/VSCode/pygameTest/Project Chess/Assets/Black/b_knight_svg_withShadow.png'),
    "bb": pygame.image.load('/Users/sandeepsawhney/Desktop/VSCode/pygameTest/Project Chess/Assets/Black/b_bishop_svg_withShadow.png'),
    "bq": pygame.image.load('/Users/sandeepsawhney/Desktop/VSCode/pygameTest/Project Chess/Assets/Black/b_queen_svg_withShadow.png'),
    "bk": pygame.image.load('/Users/sandeepsawhney/Desktop/VSCode/pygameTest/Project Chess/Assets/Black/b_king_svg_withShadow.png')
}

# Resize images to fit the board squares
for key in piece_images:
    piece_images[key] = pygame.transform.scale(piece_images[key], (SQUARE_SIZE, SQUARE_SIZE))

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess Game")

# Initial position of the pieces
initial_positions = {
    "a2": "wp", "b2": "wp", "c2": "wp", "d2": "wp", "e2": "wp", "f2": "wp", "g2": "wp", "h2": "wp",
    "a1": "wr", "b1": "wn", "c1": "wb", "d1": "wq", "e1": "wk", "f1": "wb", "g1": "wn", "h1": "wr",
    "a7": "bp", "b7": "bp", "c7": "bp", "d7": "bp", "e7": "bp", "f7": "bp", "g7": "bp", "h7": "bp",
    "a8": "br", "b8": "bn", "c8": "bb", "d8": "bq", "e8": "bk", "f8": "bb", "g8": "bn", "h8": "br",
}

# Track piece positions
board = initial_positions.copy()

# Selected piece
selected_piece = None
selected_pos = None

# Track turns
turn = 'w'

# Game state
game_over = False
game_mode = None

# Fonts
font = pygame.font.SysFont(None, 36)

# Transposition Table
transposition_table = {}

def display_text(text, color, x, y):
    screen_text = font.render(text, True, color)
    screen.blit(screen_text, (x, y))

def draw_buttons():
    pvp_button = pygame.Rect(100, SCREEN_HEIGHT // 2 - 75, 200, 50)
    pvb_button = pygame.Rect(100, SCREEN_HEIGHT // 2 + 25, 200, 50)
    pygame.draw.rect(screen, GREEN, pvp_button)
    pygame.draw.rect(screen, RED, pvb_button)
    display_text("Player vs Player", WHITE, 130, SCREEN_HEIGHT // 2 - 65)
    display_text("Player vs Bot", WHITE, 130, SCREEN_HEIGHT // 2 + 35)
    return pvp_button, pvb_button

def draw_game_over_buttons():
    new_game_button = pygame.Rect(100, SCREEN_HEIGHT // 2 - 25, 200, 50)
    quit_button = pygame.Rect(SCREEN_WIDTH - 300, SCREEN_HEIGHT // 2 - 25, 200, 50)
    pygame.draw.rect(screen, GREEN, new_game_button)
    pygame.draw.rect(screen, RED, quit_button)
    display_text("New Game", WHITE, 130, SCREEN_HEIGHT // 2 - 15)
    display_text("Quit", WHITE, SCREEN_WIDTH - 250, SCREEN_HEIGHT // 2 - 15)
    return new_game_button, quit_button

def evaluate_board(board):
    piece_values = {
        'p': 10, 'n': 30, 'b': 30,
        'r': 50, 'q': 90, 'k': 900
    }
    position_values = {
        'p': [
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [ 5,  5, 10, 25, 25, 10,  5,  5],
            [ 0,  0,  0, 20, 20,  0,  0,  0],
            [ 5, -5,-10,  0,  0,-10, -5,  5],
            [ 5, 10, 10,-20,-20, 10, 10,  5],
            [ 0,  0,  0,  0,  0,  0,  0,  0]
        ],
        'n': [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ],
        'b': [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ],
        'r': [
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [ 5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [ 0,  0,  0,  5,  5,  0,  0,  0]
        ],
        'q': [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [ -5,  0,  5,  5,  5,  5,  0, -5],
            [  0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ],
        'k': [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [ 20, 20,  0,  0,  0,  0, 20, 20],
            [ 20, 30, 10,  0,  0, 10, 30, 20]
        ]
    }
    
    score = 0
    for position, piece in board.items():
        col = ord(position[0]) - ord('a')
        row = BOARD_SIZE - int(position[1])
        value = piece_values[piece[1]]
        position_value = position_values[piece[1]][row][col]
        if piece[0] == 'w':
            score += value + position_value
        else:
            score -= value + position_value
    return score

def board_to_fen(board):
    fen = ""
    empty = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            position = chr(col + ord('a')) + str(BOARD_SIZE - row)
            if position in board:
                if empty > 0:
                    fen += str(empty)
                    empty = 0
                fen += board[position]
            else:
                empty += 1
        if empty > 0:
            fen += str(empty)
            empty = 0
        if row != BOARD_SIZE - 1:
            fen += "/"
    return fen

def minimax(board, depth, alpha, beta, maximizing_player):
    board_fen = board_to_fen(board)
    if board_fen in transposition_table:
        return transposition_table[board_fen]

    if depth == 0 or check_winner():
        eval = evaluate_board(board)
        transposition_table[board_fen] = eval
        return eval

    if maximizing_player:
        max_eval = -float('inf')
        for start_pos, piece in list(board.items()):
            if piece[0] == 'b':
                possible_moves = get_possible_moves(piece, start_pos)
                for move in possible_moves:
                    end_pos = chr(move[0] + ord('a')) + str(BOARD_SIZE - move[1])
                    captured_piece = board.get(end_pos)
                    board[end_pos] = piece
                    del board[start_pos]
                    eval = minimax(board, depth - 1, alpha, beta, False)
                    board[start_pos] = piece
                    if captured_piece:
                        board[end_pos] = captured_piece
                    else:
                        del board[end_pos]
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        transposition_table[board_fen] = max_eval
        return max_eval
    else:
        min_eval = float('inf')
        for start_pos, piece in list(board.items()):
            if piece[0] == 'w':
                possible_moves = get_possible_moves(piece, start_pos)
                for move in possible_moves:
                    end_pos = chr(move[0] + ord('a')) + str(BOARD_SIZE - move[1])
                    captured_piece = board.get(end_pos)
                    board[end_pos] = piece
                    del board[start_pos]
                    eval = minimax(board, depth - 1, alpha, beta, True)
                    board[start_pos] = piece
                    if captured_piece:
                        board[end_pos] = captured_piece
                    else:
                        del board[end_pos]
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        transposition_table[board_fen] = min_eval
        return min_eval

def get_best_move():
    best_score = -float('inf')
    best_move = None
    for start_pos, piece in list(board.items()):
        if piece[0] == 'b':
            possible_moves = get_possible_moves(piece, start_pos)
            for move in possible_moves:
                end_pos = chr(move[0] + ord('a')) + str(BOARD_SIZE - move[1])
                captured_piece = board.get(end_pos)
                board[end_pos] = piece
                del board[start_pos]
                score = minimax(board, 5, -float('inf'), float('inf'), False)  # Increased depth to 5
                board[start_pos] = piece
                if captured_piece:
                    board[end_pos] = captured_piece
                else:
                    del board[end_pos]
                if score > best_score:
                    best_score = score
                    best_move = (start_pos, end_pos)
    return best_move

# Calculate possible moves for the selected piece
def get_possible_moves(piece, position):
    possible_moves = []
    start_col, start_row = ord(position[0]) - ord('a'), BOARD_SIZE - int(position[1])
    
    if piece[1] == 'p':  # Pawn
        if piece[0] == 'w':  # White pawn
            if (chr(start_col + ord('a')) + str(BOARD_SIZE - (start_row - 1))) not in board:
                possible_moves.append((start_col, start_row - 1))
            if start_row == 6 and (chr(start_col + ord('a')) + str(BOARD_SIZE - (start_row - 2))) not in board:
                possible_moves.append((start_col, start_row - 2))
            for dc in [-1, 1]:
                capture_pos = chr(start_col + dc + ord('a')) + str(BOARD_SIZE - (start_row - 1))
                if capture_pos in board and board[capture_pos][0] == 'b':
                    possible_moves.append((start_col + dc, start_row - 1))
        else:  # Black pawn
            if (chr(start_col + ord('a')) + str(BOARD_SIZE - (start_row + 1))) not in board:
                possible_moves.append((start_col, start_row + 1))
            if start_row == 1 and (chr(start_col + ord('a')) + str(BOARD_SIZE - (start_row + 2))) not in board:
                possible_moves.append((start_col, start_row + 2))
            for dc in [-1, 1]:
                capture_pos = chr(start_col + dc + ord('a')) + str(BOARD_SIZE - (start_row + 1))
                if capture_pos in board and board[capture_pos][0] == 'w':
                    possible_moves.append((start_col + dc, start_row + 1))
    
    elif piece[1] == 'r':  # Rook
        for i in range(start_row - 1, -1, -1):
            pos = chr(start_col + ord('a')) + str(BOARD_SIZE - i)
            if pos in board:
                if board[pos][0] != piece[0]:
                    possible_moves.append((start_col, i))
                break
            possible_moves.append((start_col, i))
        for i in range(start_row + 1, BOARD_SIZE):
            pos = chr(start_col + ord('a')) + str(BOARD_SIZE - i)
            if pos in board:
                if board[pos][0] != piece[0]:
                    possible_moves.append((start_col, i))
                break
            possible_moves.append((start_col, i))
        for i in range(start_col - 1, -1, -1):
            pos = chr(i + ord('a')) + str(BOARD_SIZE - start_row)
            if pos in board:
                if board[pos][0] != piece[0]:
                    possible_moves.append((i, start_row))
                break
            possible_moves.append((i, start_row))
        for i in range(start_col + 1, BOARD_SIZE):
            pos = chr(i + ord('a')) + str(BOARD_SIZE - start_row)
            if pos in board:
                if board[pos][0] != piece[0]:
                    possible_moves.append((i, start_row))
                break
            possible_moves.append((i, start_row))

    elif piece[1] == 'n':  # Knight
        for dc, dr in [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]:
            new_col, new_row = start_col + dc, start_row + dr
            if 0 <= new_col < BOARD_SIZE and 0 <= new_row < BOARD_SIZE:
                pos = chr(new_col + ord('a')) + str(BOARD_SIZE - new_row)
                if pos not in board or board[pos][0] != piece[0]:
                    possible_moves.append((new_col, new_row))

    elif piece[1] == 'b':  # Bishop
        for dc, dr in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            new_col, new_row = start_col + dc, start_row + dr
            while 0 <= new_col < BOARD_SIZE and 0 <= new_row < BOARD_SIZE:
                pos = chr(new_col + ord('a')) + str(BOARD_SIZE - new_row)
                if pos in board:
                    if board[pos][0] != piece[0]:
                        possible_moves.append((new_col, new_row))
                    break
                possible_moves.append((new_col, new_row))
                new_col += dc
                new_row += dr

    elif piece[1] == 'q':  # Queen
        for dc, dr in [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]:
            new_col, new_row = start_col + dc, start_row + dr
            while 0 <= new_col < BOARD_SIZE and 0 <= new_row < BOARD_SIZE:
                pos = chr(new_col + ord('a')) + str(BOARD_SIZE - new_row)
                if pos in board:
                    if board[pos][0] != piece[0]:
                        possible_moves.append((new_col, new_row))
                    break
                possible_moves.append((new_col, new_row))
                new_col += dc
                new_row += dr

    elif piece[1] == 'k':  # King
        for dc, dr in [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]:
            new_col, new_row = start_col + dc, start_row + dr
            if 0 <= new_col < BOARD_SIZE and 0 <= new_row < BOARD_SIZE:
                pos = chr(new_col + ord('a')) + str(BOARD_SIZE - new_row)
                if pos not in board or board[pos][0] != piece[0]:
                    possible_moves.append((new_col, new_row))

    print(f"Possible moves for {piece} at {position}: {possible_moves}")
    return possible_moves

# Draw the chessboard
def draw_chessboard(possible_moves=[]):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
            for move in possible_moves:
                if col == move[0] and row == BOARD_SIZE - move[1] - 1:
                    color = HIGHLIGHT_COLOR
                    if (chr(move[0] + ord('a')) + str(BOARD_SIZE - move[1])) in board:
                        color = CAPTURE_HIGHLIGHT_COLOR
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Draw pieces on the board
def draw_pieces():
    for position, piece in board.items():
        col = ord(position[0]) - ord('a')
        row = BOARD_SIZE - int(position[1])
        screen.blit(piece_images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Get board position from mouse position
def get_board_pos(mouse_pos):
    x, y = mouse_pos
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    return chr(col + ord('a')) + str(BOARD_SIZE - row)

# Check if the move is valid according to chess rules
def is_valid_move(piece, start_pos, end_pos):
    start_col, start_row = ord(start_pos[0]) - ord('a'), BOARD_SIZE - int(start_pos[1])
    end_col, end_row = ord(end_pos[0]) - ord('a'), BOARD_SIZE - int(end_pos[1])
    
    delta_col = end_col - start_col
    delta_row = end_row - start_row

    print(f"Checking move for {piece} from {start_pos} to {end_pos}")
    print(f"Delta col: {delta_col}, Delta row: {delta_row}")

    if piece[1] == 'p':  # Pawn
        if piece[0] == 'w':  # White pawn
            if start_col == end_col and delta_row == -1 and end_pos not in board:
                return True
            if start_col == end_col and start_row == 6 and delta_row == -2 and end_pos not in board and (chr(start_col + ord('a')) + str(BOARD_SIZE - (start_row - 1))) not in board:
                return True
            if abs(delta_col) == 1 and delta_row == -1 and end_pos in board and board[end_pos][0] == 'b':
                return True
        else:  # Black pawn
            if start_col == end_col and delta_row == 1 and end_pos not in board:
                return True
            if start_col == end_col and start_row == 1 and delta_row == 2 and end_pos not in board and (chr(start_col + ord('a')) + str(BOARD_SIZE - (start_row + 1))) not in board:
                return True
            if abs(delta_col) == 1 and delta_row == 1 and end_pos in board and board[end_pos][0] == 'w':
                return True

    elif piece[1] == 'r':  # Rook
        if delta_col == 0 or delta_row == 0:
            step_col = 0 if delta_col == 0 else int(delta_col / abs(delta_col))
            step_row = 0 if delta_row == 0 else int(delta_row / abs(delta_row))
            for i in range(1, max(abs(delta_col), abs(delta_row))):
                if board.get(chr(start_col + step_col * i + ord('a')) + str(BOARD_SIZE - (start_row + step_row * i))) is not None:
                    return False
            return True

    elif piece[1] == 'n':  # Knight
        if (abs(delta_col) == 2 and abs(delta_row) == 1) or (abs(delta_col) == 1 and abs(delta_row) == 2):
            return True

    elif piece[1] == 'b':  # Bishop
        if abs(delta_col) == abs(delta_row):
            step_col = int(delta_col / abs(delta_col))
            step_row = int(delta_row / abs(delta_row))
            for i in range(1, abs(delta_col)):
                if board.get(chr(start_col + step_col * i + ord('a')) + str(BOARD_SIZE - (start_row + step_row * i))) is not None:
                    return False
            return True

    elif piece[1] == 'q':  # Queen
        if delta_col == 0 or delta_row == 0 or abs(delta_col) == abs(delta_row):
            step_col = 0 if delta_col == 0 else int(delta_col / abs(delta_col))
            step_row = 0 if delta_row == 0 else int(delta_row / abs(delta_row))
            for i in range(1, max(abs(delta_col), abs(delta_row))):
                if board.get(chr(start_col + step_col * i + ord('a')) + str(BOARD_SIZE - (start_row + step_row * i))) is not None:
                    return False
            return True

    elif piece[1] == 'k':  # King
        if abs(delta_col) <= 1 and abs(delta_row) <= 1:
            return True

    return False

def check_winner():
    if 'wk' not in board.values():
        return 'Black'
    if 'bk' not in board.values():
        return 'White'
    return None

def reset_game():
    global board, selected_piece, selected_pos, turn, game_over, game_mode
    board = initial_positions.copy()
    selected_piece = None
    selected_pos = None
    turn = 'w'
    game_over = False
    game_mode = None

# Main loop
running = True
start_menu = True
while running:
    possible_moves = []
    if start_menu:
        screen.fill(BACKGROUND_COLOR)
        pvp_button, pvb_button = draw_buttons()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pvp_button.collidepoint(event.pos):
                    game_mode = 'PVP'
                    start_menu = False
                elif pvb_button.collidepoint(event.pos):
                    game_mode = 'PVB'
                    start_menu = False
    else:
        if game_mode == 'PVB' and turn == 'b' and not game_over:
            move = get_best_move()
            if move:
                start_pos, end_pos = move
                board[end_pos] = board[start_pos]
                del board[start_pos]
                turn = 'w'
                if check_winner():
                    game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_over:
                    new_game_button, quit_button = draw_game_over_buttons()
                    if new_game_button.collidepoint(event.pos):
                        reset_game()
                    elif quit_button.collidepoint(event.pos):
                        running = False
                else:
                    pos = get_board_pos(pygame.mouse.get_pos())
                    if selected_piece:
                        # If the same piece is clicked again, deselect it
                        if pos == selected_pos:
                            selected_piece = None
                            selected_pos = None
                            possible_moves = []
                        elif pos in board and board[pos][0] == turn:
                            # If another piece of the same color is clicked, select it
                            selected_piece = board[pos]
                            selected_pos = pos
                            possible_moves = get_possible_moves(selected_piece, selected_pos)
                        elif is_valid_move(selected_piece, selected_pos, pos):
                            if pos in board and board[pos][0] != selected_piece[0]:
                                board[pos] = selected_piece
                                del board[selected_pos]
                                selected_piece = None
                                selected_pos = None
                                turn = 'b' if turn == 'w' else 'w'
                            elif pos not in board:
                                board[pos] = selected_piece
                                del board[selected_pos]
                                selected_piece = None
                                selected_pos = None
                                turn = 'b' if turn == 'w' else 'w'
                        else:
                            print(f"Invalid move for {selected_piece}")
                    elif pos in board and board[pos][0] == turn:
                        selected_piece = board[pos]
                        selected_pos = pos
                        possible_moves = get_possible_moves(selected_piece, selected_pos)

        # Fill the background
        screen.fill(BACKGROUND_COLOR)
        
        # Draw the chessboard with highlights
        draw_chessboard(possible_moves)
        
        # Draw the pieces
        draw_pieces()

        # Highlight the selected piece
        if selected_piece:
            col = ord(selected_pos[0]) - ord('a')
            row = BOARD_SIZE - int(selected_pos[1])
            pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

        # Check for winner
        winner = check_winner()
        if winner:
            game_over = True
            display_text(f"{winner} wins!", WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100)
            new_game_button, quit_button = draw_game_over_buttons()

        # Update the display
        pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
