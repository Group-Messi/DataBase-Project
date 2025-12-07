from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor

# --- .ENV YÜKLEME ---
load_dotenv()
app = Flask(__name__)

# --- VERİTABANI AYARLARI ---
DB_SETTINGS = {
    "host": os.environ.get("MYSQL_HOST"),
    "user": os.environ.get("MYSQL_USER"),
    "password": os.environ.get("MYSQL_PASSWORD"),
    "database": os.environ.get("MYSQL_DATABASE"),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "cursorclass": DictCursor,
    "charset": "utf8mb4",
    "autocommit": False,
}

def get_db_connection():
    return pymysql.connect(**DB_SETTINGS)

# --- ROTALAR ---

# Ana sayfa (Şimdilik games'e yönlendirebiliriz veya main.html kullanabiliriz)
@app.route('/')
def home():
    return render_template("main.html") # app2.py'deki gibi ana sayfa

# GAMES ROTASI (Senin Görevin Burasıydı)
@app.route('/games', methods=['GET', 'POST'])
def games():
    # POST İsteği: Yeni Maç Ekleme (Kayra'nın mantığını koruyoruz)
    if request.method == 'POST':
        try:
            game_id = int(request.form['game_id'])
            club_id = int(request.form['club_id'])
            hosting = request.form['hosting']
            own_goals = int(request.form['own_goals'])
            opponent_goals = int(request.form['opponent_goals'])
            
            insert_sql = """
                INSERT INTO club_games (game_id, club_id, hosting, own_goals, opponent_goals)
                VALUES (%s, %s, %s, %s, %s)
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(insert_sql, (game_id, club_id, hosting, own_goals, opponent_goals))
                conn.commit()
            return redirect(url_for('games'))
        except Exception as e:
            return f"<h1>Kayıt Hatası:</h1><p>{e}</p>"

    # GET İsteği: Listeleme
    select_sql = """
        SELECT cg.game_id,
               cg.club_id,
               cg.hosting,
               cg.own_goals,
               cg.opponent_goals,
               c.name AS club_name
        FROM club_games cg
        LEFT JOIN clubs c ON cg.club_id = c.club_id
        ORDER BY cg.game_id DESC
        LIMIT 100
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(select_sql)
                games_data = cursor.fetchall()
    except Exception as e:
        return f"<h1>Veri Çekme Hatası:</h1><p>{e}</p>"

    # İŞTE KRİTİK KISIM: Senin HTML dosyanı render ediyoruz
    return render_template('games.html', games=games_data)

# Diğer rotalar (app2.py'deki gibi boş kalabilir şimdilik)
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001)) 
    app.run(debug=True, port=port)