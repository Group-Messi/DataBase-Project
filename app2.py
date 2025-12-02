from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("main.html")

@app.route("/games")
def matches():
    return render_template("games.html")

@app.route("/players")
def players():
    return render_template("players.html")

@app.route("/clubs")
def clubs():
    return render_template("clubs.html")

@app.route("/transfers")
def transfers():
    return render_template("transfers.html")

@app.route("/competitions")
def competitions():
    return render_template("competitions.html")   

if __name__ == "__main__":
    app.run(debug=True)
