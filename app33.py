from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor

# --- .ENV YÜKLEME ---
# .env dosyasındaki şifre ve ayarları yükler
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
    """Veritabanı bağlantısını kuran yardımcı fonksiyon"""
    return pymysql.connect(**DB_SETTINGS)

# --- ROTALAR ---

@app.route("/")
def home():
    return render_template("main.html")

# --- GAMES CRUD OPERASYONLARI ---

# 1. READ (Listeleme) ve CREATE (Ekleme)
@app.route('/games', methods=['GET', 'POST'])
def games():
    # POST İsteği: Yeni Maç Ekleme
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
    # Önce kulüp listesini çekelim ki formda dropdown olarak gösterelim
    clubs_sql = """
        SELECT club_id, name
        FROM clubs
        ORDER BY name ASC
    """

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
    
    games_data = []
    clubs_data = []
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Kulüpleri çek
                cursor.execute(clubs_sql)
                clubs_data = cursor.fetchall()
                # Maçları çek
                cursor.execute(select_sql)
                games_data = cursor.fetchall()
    except Exception as e:
        return f"<h1>Veri Çekme Hatası:</h1><p>{e}</p>"

    return render_template('games.html', games=games_data, clubs=clubs_data)

# 2. DELETE (Silme İşlemi)
@app.route('/games/delete/<int:game_id>', methods=['POST'])
def delete_game(game_id):
    try:
        delete_sql = "DELETE FROM club_games WHERE game_id = %s"
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(delete_sql, (game_id,))
            conn.commit()
            
        return redirect(url_for('games'))
    except Exception as e:
        return f"<h1>Silme Hatası:</h1><p>{e}</p>"

# 3. UPDATE (Güncelleme İşlemi)
@app.route('/games/update', methods=['POST'])
def update_game():
    try:
        # Formdan gelen veriler (Hidden input ile game_id gelmeli)
        game_id = int(request.form['game_id'])
        hosting = request.form['hosting']
        own_goals = int(request.form['own_goals'])
        opponent_goals = int(request.form['opponent_goals'])
        
        update_sql = """
            UPDATE club_games 
            SET hosting = %s, own_goals = %s, opponent_goals = %s 
            WHERE game_id = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(update_sql, (hosting, own_goals, opponent_goals, game_id))
            conn.commit()
            
        return redirect(url_for('games'))
    except Exception as e:
        return f"<h1>Güncelleme Hatası:</h1><p>{e}</p>"


# --- DİĞER SAYFALAR ---

@app.route("/players")
def players():
    return render_template("players.html")

@app.route("/clubs")
def clubs():
    return render_template("clubs.html")

@app.route('/transfers', methods=['GET', 'POST'])
def transfers():
    if request.method == 'POST':
        try:
            transfer_id = int(request.form['transfer_id'])
            player_id = int(request.form['player_id'])
            transfer_date = request.form['transfer_date']
            from_club_id_raw = request.form.get('from_club_id')
            to_club_id_raw = request.form.get('to_club_id')
            transfer_season = request.form['transfer_season']
            player_name = request.form['player_name']

            from_club_id = int(from_club_id_raw) if from_club_id_raw else None
            to_club_id = int(to_club_id_raw) if to_club_id_raw else None

            insert_sql = """
                INSERT INTO transfers (
                    transfer_id, player_id, transfer_date,
                    from_club_id, to_club_id, transfer_season, player_name
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        insert_sql,
                        (
                            transfer_id,
                            player_id,
                            transfer_date,
                            from_club_id,
                            to_club_id,
                            transfer_season,
                            player_name,
                        ),
                    )
                conn.commit()

            return redirect(url_for('transfers'))
        except Exception as e:
            return f"<h1>Transfer Ekleme Hatası:</h1><p>{e}</p>"

    clubs_sql = """
        SELECT club_id, name
        FROM clubs
        ORDER BY name ASC
        LIMIT 500
    """

    players_sql = """
        SELECT player_id, name
        FROM players
        ORDER BY name ASC
        LIMIT 200
    """

    select_sql = """
        SELECT
            t.transfer_id,
            t.player_id,
            t.transfer_date,
            t.from_club_id,
            t.to_club_id,
            t.transfer_season,
            t.player_name,
            p.name AS player_full_name,
            cf.name AS from_club_name,
            ct.name AS to_club_name
        FROM transfers t
        LEFT JOIN players p ON t.player_id = p.player_id
        LEFT JOIN clubs cf ON t.from_club_id = cf.club_id
        LEFT JOIN clubs ct ON t.to_club_id = ct.club_id
        ORDER BY t.transfer_date DESC
        LIMIT 100
    """

    transfers_data = []
    clubs_data = []
    players_data = []

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(clubs_sql)
                clubs_data = cursor.fetchall()

                cursor.execute(players_sql)
                players_data = cursor.fetchall()

                cursor.execute(select_sql)
                transfers_data = cursor.fetchall()
    except Exception as e:
        return f"<h1>Transfer Verileri Çekilemedi:</h1><p>{e}</p>"

    return render_template(
        "transfers.html",
        transfers=transfers_data,
        clubs=clubs_data,
        players=players_data,
    )


@app.route('/transfers/delete/<int:transfer_id>', methods=['POST'])
def delete_transfer(transfer_id):
    try:
        delete_sql = "DELETE FROM transfers WHERE transfer_id = %s"

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(delete_sql, (transfer_id,))
            conn.commit()

        return redirect(url_for('transfers'))
    except Exception as e:
        return f"<h1>Transfer Silme Hatası:</h1><p>{e}</p>"


@app.route('/transfers/update', methods=['POST'])
def update_transfer():
    try:
        transfer_id = int(request.form['transfer_id'])
        player_id = int(request.form['player_id'])
        transfer_date = request.form['transfer_date']
        from_club_id_raw = request.form.get('from_club_id')
        to_club_id_raw = request.form.get('to_club_id')
        transfer_season = request.form['transfer_season']
        player_name = request.form['player_name']

        from_club_id = int(from_club_id_raw) if from_club_id_raw else None
        to_club_id = int(to_club_id_raw) if to_club_id_raw else None

        update_sql = """
            UPDATE transfers
            SET player_id = %s,
                transfer_date = %s,
                from_club_id = %s,
                to_club_id = %s,
                transfer_season = %s,
                player_name = %s
            WHERE transfer_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    update_sql,
                    (
                        player_id,
                        transfer_date,
                        from_club_id,
                        to_club_id,
                        transfer_season,
                        player_name,
                        transfer_id,
                    ),
                )
            conn.commit()

        return redirect(url_for('transfers'))
    except Exception as e:
        return f"<h1>Transfer Güncelleme Hatası:</h1><p>{e}</p>"

@app.route("/competitions")
def competitions():
    return render_template("competitions.html")   


@app.route('/api/player/<int:player_id>')
def get_player(player_id):
    query = """
        SELECT player_id, name
        FROM players
        WHERE player_id = %s
        LIMIT 1
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (player_id,))
                result = cursor.fetchone()
                if not result:
                    return jsonify({"player_id": player_id, "name": None}), 404
                return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)