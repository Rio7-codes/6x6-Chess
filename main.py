import pygame
import copy
import os
import random

# --- SETUP ---
pygame.init()
WIDTH, HEIGHT = 480, 480
SQUARE_SIZE = WIDTH // 6
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("6x6 Chess ♟️")

# --- COLORS ---
WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
HIGHLIGHT = (255, 255, 0, 150)
CHECK_COLOR = (255, 0, 0, 150)

# --- FONT ---
end_font = pygame.font.SysFont("dejavusans", 50)

# --- IMAGE PIECES ---
IMAGE_PATH = r"C:\Users\KIIT\Desktop\Programs\6x6 Chess\Images"

PIECE_IMAGES = {
    'P': pygame.image.load(os.path.join(IMAGE_PATH, 'WP.png')),
    'N': pygame.image.load(os.path.join(IMAGE_PATH, 'WK.png')),
    'R': pygame.image.load(os.path.join(IMAGE_PATH, 'WR.png')),
    'Q': pygame.image.load(os.path.join(IMAGE_PATH, 'WQ.png')),
    'K': pygame.image.load(os.path.join(IMAGE_PATH, 'WKing.png')),
    'p': pygame.image.load(os.path.join(IMAGE_PATH, 'BP.png')),
    'n': pygame.image.load(os.path.join(IMAGE_PATH, 'BK.png')),
    'r': pygame.image.load(os.path.join(IMAGE_PATH, 'BR.png')),
    'q': pygame.image.load(os.path.join(IMAGE_PATH, 'BQ.png')),
    'k': pygame.image.load(os.path.join(IMAGE_PATH, 'BKing.png')),
}

for key in PIECE_IMAGES:
    PIECE_IMAGES[key] = pygame.transform.smoothscale(PIECE_IMAGES[key], (SQUARE_SIZE, SQUARE_SIZE))

# --- BOARD SETUP ---
board = [
    ['r', 'n', 'q', 'k', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p'],
    [None] * 6,
    [None] * 6,
    ['P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'Q', 'K', 'N', 'R']
]

moved = {'K': False, 'R_L': False, 'R_R': False, 'k': False, 'r_l': False, 'r_r': False}
turn = "white"
selected_square = None
highlighted_moves = []
game_over = False
winner = None

# --- DRAW FUNCTIONS --- (unchanged, omitted for brevity, use your original draw_board(), draw_pieces(), etc.)

def draw_board():
    for row in range(6):
        for col in range(6):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces():
    for r in range(6):
        for c in range(6):
            piece = board[r][c]
            if piece:
                screen.blit(PIECE_IMAGES[piece], (c * SQUARE_SIZE, r * SQUARE_SIZE))

def draw_highlights():
    for r, c in highlighted_moves:
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(150)
        s.fill(HIGHLIGHT)
        screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))

def draw_check(king_pos):
    r, c = king_pos
    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
    s.set_alpha(150)
    s.fill(CHECK_COLOR)
    screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))

def draw_game_over():
    text = end_font.render(f"{winner} wins!", True, (255, 0, 0))
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, rect)

# --- UTILITY FUNCTIONS --- (unchanged, omitted for brevity, use your original functions)

def in_board(r, c):
    return 0 <= r < 6 and 0 <= c < 6

def is_white(piece):
    return piece.isupper() if piece else False

def find_king(is_white_turn):
    target = 'K' if is_white_turn else 'k'
    for r in range(6):
        for c in range(6):
            if board[r][c] == target:
                return (r, c)
    return None

def is_in_check(is_white_turn, b=None):
    if b is None:
        b = board
    king_pos = None
    for r in range(6):
        for c in range(6):
            if b[r][c] == 'K' and is_white_turn:
                king_pos = (r, c)
            elif b[r][c] == 'k' and not is_white_turn:
                king_pos = (r, c)
    if not king_pos:
        return True
    kr, kc = king_pos
    for r in range(6):
        for c in range(6):
            piece = b[r][c]
            if piece and (piece.isupper() != is_white_turn):
                for move in get_legal_moves((r, c), b, ignore_check=True):
                    if move == (kr, kc):
                        return True
    return False

def game_ended():
    global winner
    for color in ["white", "black"]:
        moves = []
        for r in range(6):
            for c in range(6):
                piece = board[r][c]
                if piece and ((piece.isupper() and color == "white") or (piece.islower() and color == "black")):
                    for dst in get_legal_moves((r, c)):
                        temp_board = copy.deepcopy(board)
                        move_piece_sim((r, c), dst, temp_board)
                        if not is_in_check(color == "white", temp_board):
                            moves.append((r, c, dst))
        if not moves:
            winner = "Black" if color == "white" else "White"
            return True
    return False

# --- CASTLING LOGIC ---

def can_castle_kingside(is_white, b):
    r = 5 if is_white else 0
    if is_white:
        if moved['K'] or moved['R_R']:
            return False
        if b[r][3] != 'K' or b[r][4] is not None or b[r][5] is not None or b[r][5] != 'R':
            return False
    else:
        if moved['k'] or moved['r_r']:
            return False
        if b[r][3] != 'k' or b[r][4] is not None or b[r][5] is not None or b[r][5] != 'r':
            return False
    if is_in_check(is_white, b):
        return False
    for sq in [(r, 4), (r, 5)]:
        temp_board = copy.deepcopy(b)
        temp_board[r][3] = None
        temp_board[sq[0]][sq[1]] = 'K' if is_white else 'k'
        if is_in_check(is_white, temp_board):
            return False
    return True

def can_castle_queenside(is_white, b):
    r = 5 if is_white else 0
    if is_white:
        if moved['K'] or moved['R_L']:
            return False
        if b[r][3] != 'K' or b[r][1] is not None or b[r][2] is not None or b[r][0] != 'R':
            return False
    else:
        if moved['k'] or moved['r_l']:
            return False
        if b[r][3] != 'k' or b[r][1] is not None or b[r][2] is not None or b[r][0] != 'r':
            return False
    if is_in_check(is_white, b):
        return False
    for sq in [(r, 2), (r, 1)]:
        temp_board = copy.deepcopy(b)
        temp_board[r][3] = None
        temp_board[sq[0]][sq[1]] = 'K' if is_white else 'k'
        if is_in_check(is_white, temp_board):
            return False
    return True

def move_piece_sim(src, dst, b):
    r1, c1 = src
    r2, c2 = dst
    piece = b[r1][c1]
    b[r2][c2] = piece
    b[r1][c1] = None

    if piece == 'P' and r2 == 0:
        b[r2][c2] = 'Q'
    if piece == 'p' and r2 == 5:
        b[r2][c2] = 'q'

    if piece == 'K':
        moved['K'] = True
        if c1 == 3 and c2 == 5:
            b[r2][4] = b[r2][5]
            b[r2][5] = None
            moved['R_R'] = True
        elif c1 == 3 and c2 == 1:
            b[r2][2] = b[r2][0]
            b[r2][0] = None
            moved['R_L'] = True

    elif piece == 'k':
        moved['k'] = True
        if c1 == 3 and c2 == 5:
            b[r2][4] = b[r2][5]
            b[r2][5] = None
            moved['r_r'] = True
        elif c1 == 3 and c2 == 1:
            b[r2][2] = b[r2][0]
            b[r2][0] = None
            moved['r_l'] = True

    elif piece == 'R':
        if r1 == 5 and c1 == 0:
            moved['R_L'] = True
        elif r1 == 5 and c1 == 5:
            moved['R_R'] = True
    elif piece == 'r':
        if r1 == 0 and c1 == 0:
            moved['r_l'] = True
        elif r1 == 0 and c1 == 5:
            moved['r_r'] = True

def move_piece(src, dst):
    move_piece_sim(src, dst, board)

def get_legal_moves(pos, b=None, ignore_check=False):
    if b is None:
        b = board
    r, c = pos
    piece = b[r][c]
    moves = []
    if not piece:
        return moves
    is_white_turn = piece.isupper()

    if piece.upper() == 'P':
        dir = -1 if is_white_turn else 1
        start_row = 4 if is_white_turn else 1
        if in_board(r + dir, c) and b[r + dir][c] is None:
            moves.append((r + dir, c))
            if r == start_row and b[r + 2 * dir][c] is None:
                moves.append((r + 2 * dir, c))
        for dc in [-1, 1]:
            if in_board(r + dir, c + dc):
                target = b[r + dir][c + dc]
                if target and is_white(target) != is_white_turn:
                    moves.append((r + dir, c + dc))

    elif piece.upper() == 'R':
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            while in_board(nr, nc):
                target = b[nr][nc]
                if target is None:
                    moves.append((nr, nc))
                else:
                    if is_white(target) != is_white_turn:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc

    elif piece.upper() == 'N':
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = r + dr, c + dc
            if in_board(nr, nc):
                target = b[nr][nc]
                if target is None or is_white(target) != is_white_turn:
                    moves.append((nr, nc))

    elif piece.upper() == 'Q':
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = r + dr, c + dc
            while in_board(nr, nc):
                target = b[nr][nc]
                if target is None:
                    moves.append((nr, nc))
                else:
                    if is_white(target) != is_white_turn:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc

    elif piece.upper() == 'K':
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if in_board(nr, nc):
                    target = b[nr][nc]
                    if target is None or is_white(target) != is_white_turn:
                        moves.append((nr, nc))

        # Castling moves only if king on start square col 3 and first rank
        if not ignore_check and c == 3 and ((r == 5 and is_white_turn) or (r == 0 and not is_white_turn)):
            if can_castle_kingside(is_white_turn, b):
                moves.append((r, 5))
            if can_castle_queenside(is_white_turn, b):
                moves.append((r, 1))

    if not ignore_check:
        legal = []
        for dst in moves:
            temp = copy.deepcopy(b)
            move_piece_sim((r, c), dst, temp)
            if not is_in_check(is_white_turn, temp):
                legal.append(dst)
        return legal
    return moves

def evaluate(b):
    vals = {'P':1, 'N':3, 'R':5, 'Q':9, 'K':1000,
            'p':-1, 'n':-3, 'r':-5, 'q':-9, 'k':-1000}
    score = 0
    for row in b:
        for c in row:
            if c:
                score += vals.get(c, 0)
    return score

def minimax(b, depth, alpha, beta, maximizing):
    if depth == 0:
        return evaluate(b), None

    is_white_turn = maximizing
    best_move = None

    if maximizing:
        max_eval = -float('inf')
        for r in range(6):
            for c in range(6):
                piece = b[r][c]
                if piece and piece.isupper():
                    for dst in get_legal_moves((r,c), b):
                        temp_board = copy.deepcopy(b)
                        move_piece_sim((r,c), dst, temp_board)
                        if is_in_check(True, temp_board):
                            continue
                        eval_score, _ = minimax(temp_board, depth-1, alpha, beta, False)
                        if eval_score > max_eval:
                            max_eval = eval_score
                            best_move = ((r, c), dst)
                        alpha = max(alpha, eval_score)
                        if beta <= alpha:
                            break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for r in range(6):
            for c in range(6):
                piece = b[r][c]
                if piece and piece.islower():
                    for dst in get_legal_moves((r,c), b):
                        temp_board = copy.deepcopy(b)
                        move_piece_sim((r,c), dst, temp_board)
                        if is_in_check(False, temp_board):
                            continue
                        eval_score, _ = minimax(temp_board, depth-1, alpha, beta, True)
                        if eval_score < min_eval:
                            min_eval = eval_score
                            best_move = ((r, c), dst)
                        beta = min(beta, eval_score)
                        if beta <= alpha:
                            break
        return min_eval, best_move

def ai_move():
    _, move = minimax(board, 3, -float('inf'), float('inf'), False)
    if move:
        move_piece(*move)

def handle_events():
    global selected_square, highlighted_moves, turn, game_over

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif not game_over and event.type == pygame.MOUSEBUTTONDOWN and turn == "white":
            x, y = pygame.mouse.get_pos()
            row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
            piece = board[row][col]
            if selected_square is None:
                if piece and piece.isupper():
                    selected_square = (row, col)
                    highlighted_moves = get_legal_moves(selected_square)
            else:
                if (row, col) in highlighted_moves:
                    move_piece(selected_square, (row, col))
                    selected_square = None
                    highlighted_moves = []
                    turn = "black"
                    if not game_ended():
                        ai_move()
                        turn = "white"
                    else:
                        game_over = True
                else:
                    selected_square = None
                    highlighted_moves = []
    return True

running = True
while running:
    draw_board()
    draw_pieces()
    draw_highlights()
    king_pos = find_king(turn == "white")
    if king_pos and is_in_check(turn == "white"):
        draw_check(king_pos)
    if game_over:
        draw_game_over()
    pygame.display.flip()
    running = handle_events()

pygame.quit()