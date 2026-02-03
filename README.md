# minimax_chess

A simple UCI chess engine written in Python, using [bulletchess](https://pypi.org/project/bulletchess/) for move generation and board representation.

## Features

- Negamax search with alpha-beta pruning
- Iterative deepening with time management
- MVV-LVA move ordering
- Material evaluation with pawn advancement bonus
- Full UCI protocol support

## Requirements

- **Python 3.13+** (required by bulletchess)
- **Linux** (bulletchess provides manylinux wheels). macOS/Windows may work if bulletchess publishes wheels for those platforms — check [PyPI](https://pypi.org/project/bulletchess/#files) for available builds.

## Setup

```bash
./setup_host.sh
```

This creates a `venv_host` virtualenv with Python 3.13 and installs bulletchess. If Python 3.13 isn't installed, on Ubuntu/Debian you can get it from the deadsnakes PPA:

```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.13 python3.13-venv
```

## Running

### Standalone (manual UCI commands)

```bash
./engine.sh
```

Then type UCI commands:

```
uci
isready
position startpos moves e2e4 e7e5
go depth 5
quit
```

### With a chess GUI

The engine speaks the [UCI protocol](https://en.wikipedia.org/wiki/Universal_Chess_Interface) and should work with any UCI-compatible GUI. Point the GUI at the full path to `engine.sh`.

Tested/expected to work with:

- **[Cute Chess](https://cutechess.com/)** — recommended for engine-vs-engine matches
- **[PyChess](https://pychess.github.io/)** — Settings → Engines → Add → set command to `/path/to/engine.sh`
- **[Arena](http://www.playwitharena.de/)** — Engines → Install New Engine → select `engine.sh`
- **[Banksia GUI](https://banksiagui.com/)**

### Supported UCI commands

| Command | Description |
|---|---|
| `uci` | Identify the engine |
| `isready` | Synchronisation check |
| `ucinewgame` | Reset the board |
| `position startpos [moves ...]` | Set position from start |
| `position fen <fen> [moves ...]` | Set position from FEN |
| `go depth N` | Search to fixed depth |
| `go movetime N` | Search for N milliseconds |
| `go wtime N btime N` | Search with clock time management |
| `go infinite` | Search until `quit` |
| `quit` | Exit |

## Playing strength

Roughly 1000–1400 Elo with the current material + pawn advancement evaluation. Search reaches depth 4–5 comfortably within a few seconds from most positions.

## Project structure

```
main.py        UCI protocol loop
search.py      Negamax, alpha-beta, iterative deepening, move ordering
evaluate.py    Board evaluation (material + pawn advancement)
engine.sh      Wrapper script (finds the right venv/python)
setup_host.sh  Creates venv_host and installs dependencies
```

## License

See [LICENSE](LICENSE).
