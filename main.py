#!/usr/bin/env python3
"""Simple chess engine with UCI protocol interface."""

import sys

from bulletchess import Board, Move, WHITE

from search import iterative_deepening


class UCIEngine:
    def __init__(self):
        self.board = Board()

    def uci_loop(self):
        while True:
            try:
                line = input().strip()
            except EOFError:
                break
            if not line:
                continue

            tokens = line.split()
            cmd = tokens[0]

            if cmd == "uci":
                print("id name SimpleEngine")
                print("id author minimax_chess")
                print("uciok", flush=True)

            elif cmd == "isready":
                print("readyok", flush=True)

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
            fen_parts = []
            idx = 2
            while idx < len(tokens) and tokens[idx] != "moves":
                fen_parts.append(tokens[idx])
                idx += 1
            self.board = Board.from_fen(" ".join(fen_parts))

        if idx < len(tokens) and tokens[idx] == "moves":
            idx += 1
            while idx < len(tokens):
                move = Move.from_uci(tokens[idx])
                self.board.apply(move)
                idx += 1

    def _handle_go(self, tokens):
        depth = 5
        time_limit = 5.0
        wtime = None
        btime = None

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

        if wtime is not None and btime is not None:
            my_time = wtime if self.board.turn == WHITE else btime
            time_limit = my_time / 30000.0

        best_move = iterative_deepening(self.board, depth, time_limit)
        print(f"bestmove {best_move}", flush=True)


if __name__ == "__main__":
    engine = UCIEngine()
    engine.uci_loop()
