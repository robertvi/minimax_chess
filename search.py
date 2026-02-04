import time

from bulletchess import Board, Move, CHECKMATE

from evaluate import evaluate, PIECE_VALUES

# Mate score base — adjusted by ply so shorter mates score higher
MATE_SCORE = 99999


def order_moves(board: Board, moves: list[Move]) -> list[Move]:
    """Order moves for better alpha-beta pruning: captures first, MVV-LVA."""
    def move_score(move):
        target = board[move.destination]
        if target is not None:
            attacker = board[move.origin]
            return PIECE_VALUES[target.piece_type] - PIECE_VALUES[attacker.piece_type] // 100
        return 0
    return sorted(moves, key=move_score, reverse=True)


def alphabeta(board: Board, depth: int, alpha: int, beta: int, ply: int = 0) -> int:
    """Negamax with alpha-beta pruning.

    Key fix: Do NOT use `board in DRAW` here. The 50-move rule and threefold
    repetition detection poison the search tree when the halfmove clock is
    high — the engine sees all deep lines as draws and gives up on winning.
    Instead, only detect checkmate and stalemate (no legal moves).
    """
    # Checkmate: side to move has lost
    if board in CHECKMATE:
        return -MATE_SCORE + ply  # prefer shorter mates

    # Generate legal moves — if none exist and not checkmate, it's stalemate
    moves = board.legal_moves()
    if len(moves) == 0:
        return 0  # stalemate = draw

    # Leaf node: return static evaluation
    if depth == 0:
        return evaluate(board)

    moves = order_moves(board, moves)
    for move in moves:
        board.apply(move)
        score = -alphabeta(board, depth - 1, -beta, -alpha, ply + 1)
        board.undo()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


def search(board: Board, depth: int) -> Move | None:
    """Find the best move at the given depth."""
    best_move = None
    alpha = -100000
    beta = 100000

    for move in order_moves(board, board.legal_moves()):
        board.apply(move)
        score = -alphabeta(board, depth - 1, -beta, -alpha, ply=1)
        board.undo()

        if score > alpha:
            alpha = score
            best_move = move

    return best_move


def iterative_deepening(board: Board, max_depth: int = 6,
                        time_limit: float = 5.0) -> Move:
    """Search with iterative deepening and time management."""
    best_move = board.legal_moves()[0]
    start = time.time()

    for depth in range(1, max_depth + 1):
        move = search(board, depth)
        if move is not None:
            best_move = move
        elapsed = time.time() - start

        print(f"info depth {depth} time {int(elapsed * 1000)}", flush=True)

        if elapsed >= time_limit * 0.8:
            break

    return best_move
