from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
from tempfile import mkdtemp
from math import inf
from random import randint

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#app.config['SECRET_KEY'] = '08wytnowyr84a9nwyrobseyorfarbo74tbsilco'
Session(app)


@app.route("/")
def index():
    # if there is no board yet, make the board and turn in session
    if "board" not in session:
        session["board"] = [[None, None, None], [
            None, None, None], [None, None, None]]
        session["turn"] = "X"
    winner, gameOver = check_game_winner()
    return render_template("game.html", game=session["board"], turn=session["turn"],
                           winner=winner, gameOver=gameOver)


def check_game_winner():
    winner = None
    gameOver = False
    # check rows
    for row in session["board"]:
        if set(row) == set("X"):
            winner = "X"
        if set(row) == set("O"):
            winner = "O"
    # check columns
    for i in range(3):
        col_lst = []
        for row in session["board"]:
            col_lst.append(row[i])
        if set(col_lst) == set("X"):
            winner = "X"
        if set(col_lst) == set("O"):
            winner = "O"
    # check diagonals
    if session["board"][0][0] == session["board"][1][1] == session["board"][2][2] == "X":
        winner = "X"
    if session["board"][0][0] == session["board"][1][1] == session["board"][2][2] == "O":
        winner = "O"
    if session["board"][0][2] == session["board"][1][1] == session["board"][2][0] == "X":
        winner = "X"
    if session["board"][0][2] == session["board"][1][1] == session["board"][2][0] == "O":
        winner = "O"
    # check if board is filled up (tied)
    if winner or None not in session["board"][0] and None not in session["board"][1] and \
            None not in session["board"][2]:
        gameOver = True
    return winner, gameOver


@app.route("/aiMove")
def aiMove():
    # return random move if board is empty.
    empty = True
    board = session["board"]
    for row in board:
        if "X" in row or "O" in row:
            empty = False
    if empty == True:
        row = randint(0, 2)
        col = randint(0, 2)
        return redirect(url_for("play", row=row, col=col))
    # recursive max or min value finding function based on possible moves.

    def minimax(board, turn):
        # return a value if the hypothetical game is over.
        winner, gameOver = check_game_winner()
        if winner == "X":
            return 1
        if winner == "O":
            return -1
        if gameOver:
            return 0
        # if the game is still going, simulate best moves for current turn. which means that it's brute forcing every possible outcome.
        # make a list of tuples representing possible moves.
        moves = []
        for row in range(3):
            for col in range(3):
                if not board[row][col]:
                    moves.append((row, col))
        if turn == "X":
            value = -inf
            for move in moves:
                row, col = move
                # hypothesize a board with that move
                board[row][col] = turn
                # check how good the new board is
                value = max(value, minimax(board, "O"))
                # put the board back to its original state to check the next move
                board[row][col] = None
                # which of these moves produced the highest score?
        else:
            value = inf
            for move in moves:
                row, col = move
                # hypothesize a board with that move
                board[row][col] = turn
                # check how good the new board is
                value = min(value, minimax(board, "X"))
                # put the board back to its original state to check the next move
                board[row][col] = None
                # which of these moves produced the lowest score?
        return value
    # find the row and col of the best move. Need to find the coordinates of the first move that
    # gives best value.
    turn = session["turn"]
    # make a list of tuples representing possible moves.
    moves = []
    for row in range(3):
        for col in range(3):
            if not board[row][col]:
                moves.append((row, col))
    # iterate over each move. Find each move's minimax.
    for move in moves:
        if turn == "X":
            value = -inf
            for move in moves:
                row, col = move
                # hypothesize a board with that move
                board[row][col] = turn
                # check how good the new board is
                value = max(value, minimax(board, "O"))
                # put the board back to its original state to check the next move
                board[row][col] = None
                # return first available best move.
                if value == 1:
                    return redirect(url_for("play", row=row, col=col))
            # if there is never a best move, return a 2nd best (tie 0)
            value = -inf
            for move in moves:
                row, col = move
                # hypothesize a board with that move
                board[row][col] = turn
                # check how good the new board is
                value = max(value, minimax(board, "O"))
                # put the board back to its original state to check the next move
                board[row][col] = None
                # return first available 2nd best move.
                if value == 0:
                    return redirect(url_for("play", row=row, col=col))
            # otherwise just return row and col for whatever the last one was.
            return redirect(url_for("play", row=row, col=col))
        else:
            value = inf
            for move in moves:
                row, col = move
                # hypothesize a board with that move
                board[row][col] = turn
                # check how good the new board is
                value = min(value, minimax(board, "X"))
                # put the board back to its original state to check the next move
                board[row][col] = None
                # return first available best move.
                if value == -1:
                    return redirect(url_for("play", row=row, col=col))
            # if there is never a best move, return a 2nd best (tie 0)
            value = inf
            for move in moves:
                row, col = move
                # hypothesize a board with that move
                board[row][col] = turn
                # check how good the new board is
                value = min(value, minimax(board, "X"))
                # put the board back to its original state to check the next move
                board[row][col] = None
                # return first available 2nd best move.
                if value == 0:
                    return redirect(url_for("play", row=row, col=col))
            # otherwise just return row and col for whatever the last one was.
            return redirect(url_for("play", row=row, col=col))
    # should have been redirected within the for loop. if not, just crash.


@app.route("/play/<int:row>/<int:col>")
def play(row, col):
    session["board"][row][col] = session["turn"]
    if session["turn"] == "X":
        session["turn"] = "O"
    else:
        session["turn"] = "X"
    return redirect(url_for("index"))


@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))
