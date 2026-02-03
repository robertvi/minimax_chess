# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A simple chess engine in Python using the `bulletchess` library for move generation and board representation, with minimax/alpha-beta search and a UCI protocol interface.

## Environment

- Running in a container with repo files at `/workspace/minimax_chess`
- Host: Ubuntu 24.04, 32GB RAM, 8 hyperthreaded cores, RTX 3060 (no GPU passthrough to container)
- System is usually busy with multiple tasks
- Install project dependencies in a `venv_container` virtualenv (container is shared across projects)
- For host-specific dependencies, set up a `venv_host`
- Passwordless `sudo` is available inside the container
- `claude-conversation-extractor` (from PyPI) should be installed in the container

## Host Interaction

- Git commits are handled on the host side, not in the container
- When the user needs to run something on the host, write all commands into a single temporary script file
- Never output multi-line commands directly in chat (trailing whitespace from the chat UI breaks line continuations)
- Embed `nohup` and log capture into host scripts if needed
- Capture relevant output into temporary log files rather than asking the user to copy-paste output back

## Dependencies

```bash
pip install bulletchess
```

## Architecture

Three logical layers, implemented as a single file (`engine.py`) or a small package:

1. **UCI Interface** (`main.py`) — reads stdin/writes stdout, handles UCI protocol commands (`uci`, `isready`, `position`, `go`, `stop`, `quit`)
2. **Search** (`search.py`) — negamax with alpha-beta pruning, iterative deepening, move ordering (MVV-LVA)
3. **Evaluation** (`evaluate.py`) — material counting in centipawns from side-to-move perspective

The engine uses `bulletchess` for all chess logic: board state, legal move generation, make/unmake moves (`board.apply()`/`board.undo()`), and game-state detection (`board in CHECKMATE`, `board in DRAW`).

## Key bulletchess API

- `Board()` / `Board.from_fen(fen)` — create boards
- `board.legal_moves()` — generate legal moves
- `board.apply(move)` / `board.undo()` — make/unmake moves
- `board[square]` — get piece at square
- `Move.from_uci("e2e4")` / `str(move)` — UCI move parsing/formatting
- `board in CHECKMATE` / `board in DRAW` — terminal state detection

## Running

```bash
python engine.py
```

Then type UCI commands (`uci`, `position startpos`, `go depth 4`, etc.) or connect via a UCI-compatible GUI (Cute Chess, PyChess, Arena).

## UCI Protocol Notes

- Always flush stdout after UCI responses (`print(..., flush=True)`)
- Time management: use ~1/30th of remaining time per move
- Default search depth: 5, default time limit: 5 seconds

## Piece Values (centipawns)

Pawn=100, Knight=320, Bishop=330, Rook=500, Queen=900, King=0

## Testing

- Test `evaluate()` with known material imbalances
- Test search with mate-in-1 and mate-in-2 positions
- Test UCI loop by typing commands manually
- Watch edge cases: promotions (`e7e8q`), en passant, castling, stalemate

## Performance Expectations

Pure Python + bulletchess: depth 4 instant, depth 5 a few seconds, depth 6 10-30s without move ordering. Playing strength ~1000-1400 Elo with material-only eval.
