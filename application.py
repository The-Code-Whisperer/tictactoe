from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
from tempfile import mkdtemp

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    if "board" not in session:
        session["board"] = [[None, None, None], [None, None, None], [None, None, None]]
        session["turn"] = "X"
    winner = None
    for row in session["board"]:
        if set(row) == set("X"):
            winner = "X"
        if set(row) == set("O"):
            winner = "O"
    for i in range(3):
        col_lst = []
        for row in session["board"]:
            col_lst.append(row[i])
        if set(col_lst) == set("X"):
            winner = "X"
        if set(col_lst) == set("O"):
            winner = "O"
    if session["board"][0][0] == session["board"][1][1] == session["board"][2][2] == "X":
        winner = "X"
    if session["board"][0][0] == session["board"][1][1] == session["board"][2][2] == "O":
        winner = "O"
    if session["board"][0][2] == session["board"][1][1] == session["board"][2][0] == "X":
        winner = "X"
    if session["board"][0][2] == session["board"][1][1] == session["board"][2][0] == "O":
        winner = "O"
    return render_template("game.html", game=session["board"], turn=session["turn"], winner=winner)


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