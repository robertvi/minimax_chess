from bulletchess import (
    Board,
    WHITE, BLACK,
    PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    CHECKMATE, DRAW,
    SQUARES,
)

PIECE_VALUES = {
    PAWN: 100,
    KNIGHT: 320,
    BISHOP: 330,
    ROOK: 500,
    QUEEN: 900,
    KING: 0,
}


def evaluate(board: Board) -> int:
    """Return score in centipawns from the side-to-move's perspective."""
    if board in CHECKMATE:
        return -99999
    if board in DRAW:
        return 0

    white_score = 0
    black_score = 0
    for sq in SQUARES:
        piece = board[sq]
        if piece is None:
            continue
        val = PIECE_VALUES[piece.piece_type]
        if piece.color == WHITE:
            white_score += val
        else:
            black_score += val

    if board.turn == WHITE:
        return white_score - black_score
    else:
        return black_score - white_score
