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
    for i, sq in enumerate(SQUARES):
        piece = board[sq]
        if piece is None:
            continue
        val = PIECE_VALUES[piece.piece_type]
        if piece.piece_type == PAWN:
            rank = i // 8  # 0-based: 0=rank1, 7=rank8
            if piece.color == WHITE:
                val += (rank - 1) * 10  # rank2=0, rank3=10, ... rank7=50
            else:
                val += (6 - rank) * 10  # rank7=0, rank6=10, ... rank2=50
        if piece.color == WHITE:
            white_score += val
        else:
            black_score += val

    if board.turn == WHITE:
        return white_score - black_score
    else:
        return black_score - white_score
