# Simple Chess Engine Plan
## bulletchess + Minimax/Alpha-Beta + UCI

---

## Architecture Overview

The engine is a single Python file (or a small package) with three logical layers:

```
┌──────────────────────────┐
│      UCI Interface       │  ← reads stdin, writes stdout
├──────────────────────────┤
│     Search (Minimax)     │  ← alpha-beta pruning, iterative deepening
├──────────────────────────┤
│      Evaluation          │  ← material counting via bulletchess
├──────────────────────────┤
│  bulletchess (Board/Move)│  ← move gen, make/unmake, game-state detection
└──────────────────────────┘
```

---

## 1. Board Representation — bulletchess Cheat Sheet

All chess logic is delegated to `bulletchess`. Key API you'll use:

| Task | bulletchess API |
|---|---|
| New starting board | `Board()` |
| Board from FEN | `Board.from_fen(fen_string)` |
| Board to FEN | `board.fen()` |
| Side to move | `board.turn` → `WHITE` or `BLACK` |
| Legal moves | `board.legal_moves()` → list of `Move` |
| Make a move | `board.apply(move)` |
| Unmake last move | `board.undo()` |
| Piece at square | `board[E4]` → `Piece` or `None` |
| Piece's type | `piece.piece_type` → `PAWN`, `KNIGHT`, etc. |
| Piece's color | `piece.color` → `WHITE` or `BLACK` |
| Parse UCI move | `Move.from_uci("e2e4")` |
| Move to UCI string | `str(move)` → `"e2e4"` |
| Is checkmate? | `board in CHECKMATE` |
| Is draw? | `board in DRAW` |
| Bitboard of a color | `board[WHITE]` → `Bitboard` |
| Bitboard of a type | `board[PAWN]` → `Bitboard` |
| Popcount | `board[PAWN].popcount()` or iterate squares |

**Imports you'll need:**
```python
from bulletchess import (
    Board, Move, Piece, Color, PieceType,
    WHITE, BLACK,
    PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    CHECKMATE, DRAW,
    SQUARES,  # list of all 64 squares
    PIECE_TYPES,
)
```

---

## 2. Evaluation Function

The simplest useful evaluation: **material count** from the side-to-move's perspective.

### Piece Values
| Piece | Value |
|-------|-------|
| Pawn | 100 |
| Knight | 320 |
| Bishop | 330 |
| Rook | 500 |
| Queen | 900 |
| King | 0 (not counted — always present) |

> Use centipawns (multiply classic values by 100) so you have integer arithmetic
> and room for fractional bonuses later.

### Algorithm

```python
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
        return -99999  # side to move is checkmated
    if board in DRAW:
        return 0

    score = 0
    for sq in SQUARES:
        piece = board[sq]
        if piece is None:
            continue
        val = PIECE_VALUES[piece.piece_type]
        if piece.color == board.turn:
            score += val
        else:
            score -= val
    return score
```

**Alternative (faster, using bitboards):** Instead of iterating all 64 squares, iterate over piece types and use the bitboard popcount:

```python
def evaluate(board: Board) -> int:
    if board in CHECKMATE:
        return -99999
    if board in DRAW:
        return 0

    white_score = 0
    black_score = 0
    for pt in (PAWN, KNIGHT, BISHOP, ROOK, QUEEN):
        val = PIECE_VALUES[pt]
        # board[WHITE] & board[pt] would give white pieces of that type
        # but we may need to count them — check if popcount is available
        # Fallback: iterate SQUARES and check
        for sq in SQUARES:
            piece = board[sq]
            if piece is not None and piece.piece_type == pt:
                if piece.color == WHITE:
                    white_score += val
                else:
                    black_score += val

    if board.turn == WHITE:
        return white_score - black_score
    else:
        return black_score - white_score
```

### Future Enhancements (not for v1, but easy to add later)
- Piece-square tables (PSTs) — give positional bonuses per piece per square
- Mobility bonus — `len(board.legal_moves())` as a small bonus
- King safety heuristics
- Pawn structure (doubled, isolated, passed pawns)

---

## 3. Search — Minimax with Alpha-Beta Pruning

### Core Algorithm

```python
def alphabeta(board: Board, depth: int, alpha: int, beta: int) -> int:
    """Negamax with alpha-beta pruning."""
    # Terminal / leaf node
    if depth == 0 or board in CHECKMATE or board in DRAW:
        return evaluate(board)

    moves = board.legal_moves()
    if len(moves) == 0:
        return evaluate(board)  # checkmate or stalemate handled by evaluate

    for move in moves:
        board.apply(move)
        score = -alphabeta(board, depth - 1, -beta, -alpha)
        board.undo()

        if score >= beta:
            return beta        # beta cutoff
        if score > alpha:
            alpha = score

    return alpha
```

### Root Search (returns best move)

```python
def search(board: Board, depth: int) -> Move:
    """Find the best move at the given depth."""
    best_move = None
    alpha = -100000
    beta = 100000

    for move in board.legal_moves():
        board.apply(move)
        score = -alphabeta(board, depth - 1, -beta, -alpha)
        board.undo()

        if score > alpha:
            alpha = score
            best_move = move

    return best_move
```

### Iterative Deepening (recommended)

Wrap the root search in an iterative-deepening loop so the engine can respond to `stop` commands and respect time limits:

```python
import time

def iterative_deepening(board: Board, max_depth: int = 6,
                        time_limit: float = 5.0) -> Move:
    best_move = board.legal_moves()[0]  # fallback
    start = time.time()

    for depth in range(1, max_depth + 1):
        move = search(board, depth)
        if move is not None:
            best_move = move
        elapsed = time.time() - start

        # Print info line for UCI GUIs
        print(f"info depth {depth} time {int(elapsed * 1000)}")

        if elapsed >= time_limit * 0.8:
            break  # don't start a deeper search if time is tight

    return best_move
```

### Move Ordering (easy win for alpha-beta efficiency)

Alpha-beta prunes much more when good moves are searched first. Simple ordering heuristics:

1. **Captures first** — check if `board[move.destination]` is not `None` before applying
2. **MVV-LVA** (Most Valuable Victim – Least Valuable Attacker) — sort captures by `victim_value - attacker_value`

```python
def order_moves(board: Board, moves: list[Move]) -> list[Move]:
    def move_score(move):
        target = board[move.destination]
        if target is not None:
            # Capture: score = victim value - attacker value / 100
            attacker = board[move.origin]
            return PIECE_VALUES[target.piece_type] - PIECE_VALUES[attacker.piece_type] // 100
        return 0
    return sorted(moves, key=move_score, reverse=True)
```

Then in `alphabeta`, replace `moves = board.legal_moves()` with:
```python
moves = order_moves(board, board.legal_moves())
```

---

## 4. UCI Protocol Interface

The UCI protocol is text-based over stdin/stdout. Your engine needs to handle these commands:

### Commands to Handle

| UCI Command | Your Response |
|---|---|
| `uci` | Print `id name MyEngine`, `id author YourName`, then `uciok` |
| `isready` | Print `readyok` |
| `ucinewgame` | Reset board to starting position |
| `position startpos` | Set board to start |
| `position startpos moves e2e4 e7e5 ...` | Set board and apply moves |
| `position fen <fen>` | Set board from FEN |
| `position fen <fen> moves ...` | Set board from FEN then apply moves |
| `go depth N` | Search to depth N, then print `bestmove <uci_move>` |
| `go wtime X btime Y` | Search with time management, print `bestmove` |
| `go movetime X` | Search for X milliseconds, print `bestmove` |
| `go infinite` | Search until `stop` |
| `stop` | Stop searching, print `bestmove` immediately |
| `quit` | Exit the program |

### Implementation Skeleton

```python
import sys

class UCIEngine:
    def __init__(self):
        self.board = Board()

    def uci_loop(self):
        while True:
            line = input().strip()
            if not line:
                continue

            tokens = line.split()
            cmd = tokens[0]

            if cmd == "uci":
                print("id name SimpleEngine")
                print("id author YourName")
                print("uciok")
                sys.stdout.flush()

            elif cmd == "isready":
                print("readyok")
                sys.stdout.flush()

            elif cmd == "ucinewgame":
                self.board = Board()

            elif cmd == "position":
                self._handle_position(tokens)

            elif cmd == "go":
                self._handle_go(tokens)

            elif cmd == "quit":
                break

    def _handle_position(self, tokens):
        idx = 1
        if tokens[idx] == "startpos":
            self.board = Board()
            idx = 2
        elif tokens[idx] == "fen":
            # Collect FEN parts (up to 6 tokens)
            fen_parts = []
            idx = 2
            while idx < len(tokens) and tokens[idx] != "moves":
                fen_parts.append(tokens[idx])
                idx += 1
            fen = " ".join(fen_parts)
            self.board = Board.from_fen(fen)

        # Apply moves if present
        if idx < len(tokens) and tokens[idx] == "moves":
            idx += 1
            while idx < len(tokens):
                move = Move.from_uci(tokens[idx])
                self.board.apply(move)
                idx += 1

    def _handle_go(self, tokens):
        # Parse search parameters
        depth = 5  # default
        time_limit = 5.0  # default seconds

        i = 1
        while i < len(tokens):
            if tokens[i] == "depth" and i + 1 < len(tokens):
                depth = int(tokens[i + 1])
                i += 2
            elif tokens[i] == "movetime" and i + 1 < len(tokens):
                time_limit = int(tokens[i + 1]) / 1000.0
                i += 2
            elif tokens[i] == "wtime" and i + 1 < len(tokens):
                wtime = int(tokens[i + 1])
                i += 2
            elif tokens[i] == "btime" and i + 1 < len(tokens):
                btime = int(tokens[i + 1])
                i += 2
            elif tokens[i] == "infinite":
                depth = 20
                time_limit = 3600
                i += 1
            else:
                i += 1

        # Simple time management: use 1/30th of remaining time
        if 'wtime' in dir() or 'btime' in dir():
            my_time = wtime if self.board.turn == WHITE else btime
            time_limit = my_time / 30000.0  # ms → s, divide by 30

        best_move = iterative_deepening(self.board, depth, time_limit)
        print(f"bestmove {best_move}")
        sys.stdout.flush()

if __name__ == "__main__":
    engine = UCIEngine()
    engine.uci_loop()
```

**Critical detail:** Always call `sys.stdout.flush()` after printing UCI responses, or use `print(..., flush=True)`. UCI GUIs read line-by-line and won't see your output if it's buffered.

---

## 5. File Structure

For a minimal engine, a single file works fine:

```
simple_engine/
├── engine.py          # Everything: eval, search, UCI loop
└── README.md
```

Or for cleaner separation:

```
simple_engine/
├── main.py            # Entry point — UCI loop
├── search.py          # alphabeta, iterative_deepening, move ordering
├── evaluate.py        # evaluate(), PIECE_VALUES
└── README.md
```

---

## 6. Running It

### Install bulletchess
```bash
pip install bulletchess
```

### Run directly
```bash
python engine.py
```
Then type UCI commands manually to test.

### Connect to PyChess / Arena / Cute Chess
Most GUIs let you add a custom UCI engine:
- **Cute Chess** (recommended for engine-vs-engine): Settings → Engines → Add → point to `python /path/to/engine.py`
- **PyChess**: same idea — add engine, specify the command as `python engine.py`
- **Arena**: Engines → Install New Engine → select the script

The command the GUI runs should be:
```
python /full/path/to/engine.py
```

On Linux you can also add a shebang (`#!/usr/bin/env python3`) and `chmod +x engine.py` to run it directly.

---

## 7. Implementation Order (Suggested Steps)

| Step | What to Build | How to Test |
|------|--------------|-------------|
| **1** | `evaluate()` — material count | Unit test: set up a board with known material imbalance, verify score |
| **2** | `alphabeta()` + `search()` at fixed depth | Feed it a mate-in-1 or mate-in-2 position, verify it finds the move |
| **3** | UCI `position` + `go depth N` | Run engine, type `position startpos`, then `go depth 3`, check output |
| **4** | Full UCI loop (all commands) | Connect to Cute Chess and play a game against it |
| **5** | Iterative deepening + time management | Run engine-vs-engine matches with time controls |
| **6** | Move ordering (captures first) | Compare nodes searched with and without ordering at depth 5 |

---

## 8. Testing & Debugging Tips

- **Print `info` lines** during search so you can see what depth it reaches and how long it takes.
- **Test with known positions:** Use positions where the best move is obvious (mate-in-2, winning a queen) and verify the engine finds them.
- **Compare against Stockfish:** Use Cute Chess to play your engine vs Stockfish set to a very low depth/time. Your engine will lose, but it should play legal moves and not crash.
- **Perft testing:** Use bulletchess's move generation to run perft tests and confirm correct move generation (this is handled by the library, but good to verify your apply/undo usage).
- **Edge cases to watch:**
  - Promotions (UCI format: `e7e8q`)
  - En passant
  - Castling
  - Stalemate (must return draw, not crash)
  - 50-move rule / threefold repetition (handled by `board in DRAW`)

---

## 9. Performance Expectations

With pure Python + bulletchess (C move generation):
- Depth 4: instant (under 1 second from most positions)
- Depth 5: a few seconds
- Depth 6: 10–30 seconds without move ordering; much less with ordering
- Depth 7+: may need additional pruning or be too slow

Playing strength will be roughly **1000–1400 Elo** with pure material evaluation. Adding piece-square tables can push it to **1400–1600**.

---

## 10. Easy Improvements for Later

Once the basic engine works, these are the highest-impact additions ranked by effort-to-reward:

1. **Piece-Square Tables** — ~50 lines of code, biggest eval improvement
2. **Quiescence Search** — search all captures at depth 0 to avoid the "horizon effect"
3. **Transposition Table** — cache positions with Zobrist hashing (`board.__hash__()`)
4. **Killer Move Heuristic** — remember non-capture moves that caused beta cutoffs
5. **Null Move Pruning** — skip a move to get a quick lower bound
6. **Opening Book** — play known good openings from a Polyglot book file
