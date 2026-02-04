from bulletchess import (
    Board,
    WHITE, BLACK,
    PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
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

# Simple center-distance table for the king (index = square index 0-63)
# Used in endgame to reward pushing the losing king to the edge
# Values: corners/edges = high, center = low
_KING_EDGE_DISTANCE = []
for _sq_idx in range(64):
    _file = _sq_idx % 8
    _rank = _sq_idx // 8
    # Distance from center (0-3 for both file and rank)
    _fd = max(3 - _file, _file - 4)
    _rd = max(3 - _rank, _rank - 4)
    _KING_EDGE_DISTANCE.append(_fd + _rd)  # 0 = center, 6 = corner


def evaluate(board: Board) -> int:
    """Return score in centipawns from the side-to-move's perspective.

    Terminal positions (checkmate, stalemate) are handled by the search,
    NOT here. This function only does static evaluation of non-terminal
    positions.
    """
    white_score = 0
    black_score = 0
    white_king_idx = 0
    black_king_idx = 0
    total_material = 0  # non-king, non-pawn material (for endgame detection)

    for i, sq in enumerate(SQUARES):
        piece = board[sq]
        if piece is None:
            continue
        val = PIECE_VALUES[piece.piece_type]

        # Track king positions for endgame heuristic
        if piece.piece_type == KING:
            if piece.color == WHITE:
                white_king_idx = i
            else:
                black_king_idx = i
            continue  # king value is 0, skip adding

        total_material += val

        # Pawn advancement bonus
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

    # Endgame mop-up: when one side has a big material lead,
    # reward pushing the losing king to the edge of the board.
    # This is what teaches the engine HOW to deliver checkmate.
    material_diff = white_score - black_score
    if abs(material_diff) > 300:  # significant material advantage
        if material_diff > 0:
            # White is winning: reward black king being near the edge
            white_score += _KING_EDGE_DISTANCE[black_king_idx] * 15
            # Also reward white king being close to black king (for mating)
            wk_file, wk_rank = white_king_idx % 8, white_king_idx // 8
            bk_file, bk_rank = black_king_idx % 8, black_king_idx // 8
            king_dist = abs(wk_file - bk_file) + abs(wk_rank - bk_rank)
            white_score += (14 - king_dist) * 5  # closer = better
        else:
            # Black is winning: reward white king being near the edge
            black_score += _KING_EDGE_DISTANCE[white_king_idx] * 15
            wk_file, wk_rank = white_king_idx % 8, white_king_idx // 8
            bk_file, bk_rank = black_king_idx % 8, black_king_idx // 8
            king_dist = abs(wk_file - bk_file) + abs(wk_rank - bk_rank)
            black_score += (14 - king_dist) * 5

    if board.turn == WHITE:
        return white_score - black_score
    else:
        return black_score - white_score
