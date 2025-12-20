from flask import Flask, render_template, request, redirect, url_for, jsonify
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

# --- SEASON HESAPLAMA FONKSİYONU ---
def calculate_season_from_date(transfer_date):
    """
    Tarihten season hesaplar.
    Futbol sezonları Temmuz'dan Haziran'a kadar sürer.
    Örn: 2026-01-10 → "25/26"
    """
    if not transfer_date:
        return None
    
    # Tarihi parse et (YYYY-MM-DD formatı)
    try:
        year = int(transfer_date[:4])
        month = int(transfer_date[5:7])
        
        # Temmuz-Aralık (ay >= 7): yıl/yıl+1
        # Ocak-Haziran (ay < 7): yıl-1/yıl
        if month >= 7:
            season_start = year
            season_end = year + 1
        else:
            season_start = year - 1
            season_end = year
        
        # Son 2 haneyi al
        return f"{str(season_start)[-2:]}/{str(season_end)[-2:]}"
    except (ValueError, IndexError):
        return None

# --- ROTALAR ---

@app.route("/")
def home():
    return render_template("main.html")

# ==========================================
# 1. CLUB_GAMES (KULÜP MAÇLARI) CRUD
# ==========================================
@app.route('/club_games', methods=['GET', 'POST'])
def club_games():
    # POST: Yeni Maç Ekleme
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
            return redirect(url_for('club_games'))
        except Exception as e:
            return f"<h1>Kayıt Hatası:</h1><p>{e}</p>"

    # GET: Listeleme
    clubs_sql = "SELECT club_id, name FROM clubs ORDER BY name ASC"
    select_sql = """
        SELECT cg.game_id, cg.club_id, cg.hosting, cg.own_goals, cg.opponent_goals, c.name AS club_name
        FROM club_games cg
        LEFT JOIN clubs c ON cg.club_id = c.club_id
        ORDER BY cg.game_id DESC LIMIT 100
    """
    
    games_data = []
    clubs_data = []
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(clubs_sql)
                clubs_data = cursor.fetchall()
                cursor.execute(select_sql)
                games_data = cursor.fetchall()
    except Exception as e:
        return f"<h1>Veri Çekme Hatası:</h1><p>{e}</p>"

    return render_template('club_games.html', games=games_data, clubs=clubs_data, current_page="club_games")

@app.route('/club_games/delete/<int:game_id>', methods=['POST'])
def delete_club_game(game_id):
    try:
        delete_sql = "DELETE FROM club_games WHERE game_id = %s"
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(delete_sql, (game_id,))
            conn.commit()
        return redirect(url_for('club_games'))
    except Exception as e:
        return f"<h1>Silme Hatası:</h1><p>{e}</p>"

@app.route('/club_games/update', methods=['POST'])
def update_club_game():
    try:
        game_id = int(request.form['game_id'])
        hosting = request.form['hosting']
        own_goals = int(request.form['own_goals'])
        opponent_goals = int(request.form['opponent_goals'])
        
        update_sql = "UPDATE club_games SET hosting=%s, own_goals=%s, opponent_goals=%s WHERE game_id=%s"
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(update_sql, (hosting, own_goals, opponent_goals, game_id))
            conn.commit()
        return redirect(url_for('club_games'))
    except Exception as e:
        return f"<h1>Güncelleme Hatası:</h1><p>{e}</p>"


# ==========================================
# 2. GAMES (MAÇLAR) CRUD
# ==========================================
@app.route('/games', methods=['GET', 'POST'])
def games():
    # POST: Yeni Maç Ekleme
    if request.method == 'POST':
        try:
            game_id = int(request.form['game_id'])
            home_club_id = int(request.form['home_club_id'])
            away_club_id = int(request.form['away_club_id'])
            game_date = request.form['game_date']
            home_club_goals = int(request.form.get('home_club_goals', 0))
            away_club_goals = int(request.form.get('away_club_goals', 0))
            
            insert_sql = """
                INSERT INTO games (game_id, home_club_id, away_club_id, game_date, home_club_goals, away_club_goals)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(insert_sql, (game_id, home_club_id, away_club_id, game_date, home_club_goals, away_club_goals))
                conn.commit()
            return redirect(url_for('games'))
        except Exception as e:
            return f"<h1>Kayıt Hatası:</h1><p>{e}</p>"


    clubs_sql = "SELECT club_id, name FROM clubs ORDER BY name ASC"
    
    select_sql = """
        SELECT g.game_id, g.home_club_id, g.away_club_id, g.game_date, 
               g.home_club_goals, g.away_club_goals,
               hc.name AS home_club_name, ac.name AS away_club_name
        FROM games g
        LEFT JOIN clubs hc ON g.home_club_id = hc.club_id
        LEFT JOIN clubs ac ON g.away_club_id = ac.club_id  
        ORDER BY g.game_date DESC, g.game_id DESC LIMIT 50
    """

  
    complex_sql = """
        SELECT SUM(g.home_club_goals + g.away_club_goals) AS total_goals
        FROM games g
         JOIN clubs c1 ON g.home_club_id = c1.club_id
         Join clubs c2 on g.away_club_id = c2.club_id
         JOIN competitions comp ON c1.domestic_competition_id = comp.competition_id AND c2.domestic_competition_id = comp.competition_id
         WHERE comp.is_major_national_league = 'True'
    """

    nested_sql = """
        SELECT g.game_id, g.game_date, hc.name as home_name, ac.name as away_name
        FROM games g
        JOIN clubs hc ON g.home_club_id = hc.club_id
        JOIN clubs ac ON g.away_club_id = ac.club_id
        WHERE g.home_club_id IN (
            SELECT club_id FROM clubs WHERE stadium_seats > 35000
        )
        ORDER BY g.game_date DESC LIMIT 7
    """

 
    groupby_sql = """
        SELECT comp.name, COUNT(g.game_id) as match_count, SUM(g.home_club_goals + g.away_club_goals) as total_goals
        FROM games g
        JOIN clubs c ON g.home_club_id = c.club_id
        JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
        GROUP BY comp.name
        ORDER BY total_goals DESC LIMIT 7
    """

    games_data = []
    clubs_data = []
    major_league_goals = 0
    big_stadium_games = []
    league_stats = []

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(clubs_sql)
                clubs_data = cursor.fetchall()
                cursor.execute(select_sql)
                games_data = cursor.fetchall()

                cursor.execute(complex_sql)
                res = cursor.fetchone()
                major_league_goals = res['total_goals'] if res and res['total_goals'] else 0

                cursor.execute(nested_sql)
                big_stadium_games = cursor.fetchall()

                cursor.execute(groupby_sql)
                league_stats = cursor.fetchall()

    except Exception as e:
        return f"<h1>Veri Çekme Hatası:</h1><p>{e}</p>"

    return render_template('games.html', 
                           games=games_data, 
                           clubs=clubs_data, 
                           major_goals=major_league_goals,
                           stadium_games=big_stadium_games,
                           league_stats=league_stats,
                           current_page="games")

@app.route('/games/delete/<int:game_id>', methods=['POST'])
def delete_game(game_id):
    try:
        delete_sql = "DELETE FROM games WHERE game_id = %s"
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(delete_sql, (game_id,))
            conn.commit()
        return redirect(url_for('games'))
    except Exception as e:
        return f"<h1>Silme Hatası:</h1><p>{e}</p>"

@app.route('/games/update', methods=['POST'])
def update_game():
    try:
        game_id = int(request.form['game_id'])
        home_club_id = int(request.form['home_club_id'])
        away_club_id = int(request.form['away_club_id'])
        game_date = request.form['game_date']
        home_club_goals = int(request.form.get('home_club_goals', 0))
        away_club_goals = int(request.form.get('away_club_goals', 0))
        
        update_sql = """
            UPDATE games 
            SET home_club_id=%s, away_club_id=%s, game_date=%s, 
                home_club_goals=%s, away_club_goals=%s 
            WHERE game_id=%s
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(update_sql, (home_club_id, away_club_id, game_date, home_club_goals, away_club_goals, game_id))
            conn.commit()
        return redirect(url_for('games'))
    except Exception as e:
        return f"<h1>Güncelleme Hatası:</h1><p>{e}</p>"


# ==========================================
# 3. TRANSFERS CRUD
# ==========================================
@app.route('/transfers', methods=['GET', 'POST'])
def transfers():
    if request.method == 'POST':
        try:
            player_id = int(request.form['player_id'])
            transfer_date = request.form['transfer_date']
            from_club_id = int(request.form.get('from_club_id')) if request.form.get('from_club_id') else None
            to_club_id = int(request.form.get('to_club_id')) if request.form.get('to_club_id') else None
            transfer_season = request.form.get('transfer_season', '').strip()
            player_name = request.form['player_name']
            
            # Eğer season boşsa, tarihten otomatik hesapla
            if not transfer_season and transfer_date:
                transfer_season = calculate_season_from_date(transfer_date)

            # transfer_id AUTO_INCREMENT ile otomatik atanacak
            # Eğer AUTO_INCREMENT yoksa (migration yapılmamışsa), manuel olarak MAX+1 hesaplıyoruz
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Önce AUTO_INCREMENT'in çalışıp çalışmadığını test et
                    # Eğer çalışmıyorsa, manuel olarak MAX+1 hesapla
                    try:
                        # AUTO_INCREMENT varsa bu çalışır
                        insert_sql = """
                            INSERT INTO transfers (player_id, transfer_date, from_club_id, to_club_id, transfer_season, player_name)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_sql, (player_id, transfer_date, from_club_id, to_club_id, transfer_season, player_name))
                    except Exception as auto_inc_error:
                        # AUTO_INCREMENT yoksa, manuel olarak MAX+1 hesapla
                        if "doesn't have a default value" in str(auto_inc_error) or "Field 'transfer_id'" in str(auto_inc_error):
                            cursor.execute("SELECT COALESCE(MAX(transfer_id), 0) as max_id FROM transfers FOR UPDATE")
                            result = cursor.fetchone()
                            next_transfer_id = (result['max_id'] if result else 0) + 1
                            
                            insert_sql = """
                                INSERT INTO transfers (transfer_id, player_id, transfer_date, from_club_id, to_club_id, transfer_season, player_name)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(insert_sql, (next_transfer_id, player_id, transfer_date, from_club_id, to_club_id, transfer_season, player_name))
                        else:
                            raise auto_inc_error
                conn.commit()
            return redirect(url_for('transfers'))
        except Exception as e:
            return f"<h1>Transfer Ekleme Hatası:</h1><p>{e}</p>"

    # GET logic
    try:
        # Sıralama parametrelerini al
        sort_by = request.args.get('sort_by', 'transfer_date')  # Varsayılan: transfer_date
        order = request.args.get('order', 'DESC')  # Varsayılan: DESC
        
        # Oyuncu arama parametresi
        player_search = request.args.get('player_search', '').strip()
        
        # Güvenlik: Sadece izin verilen kolonlar
        allowed_sort_columns = {
            'transfer_date': 't.transfer_date',
            'player_name': 'COALESCE(p.name, t.player_name)',
            'from_club': 'cf.name',
            'to_club': 'ct.name',
            'season': 't.transfer_season'
        }
        
        # Sıralama kolonu kontrolü
        sort_column = allowed_sort_columns.get(sort_by, 't.transfer_date')
        
        # ORDER kontrolü (güvenlik)
        if order not in ['ASC', 'DESC']:
            order = 'DESC'
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT club_id, name FROM clubs ORDER BY name ASC LIMIT 500")
                clubs_data = cursor.fetchall()
                
                cursor.execute("SELECT player_id, name FROM players ORDER BY name ASC LIMIT 200")
                players_data = cursor.fetchall()

                # WHERE koşulu oluştur (oyuncu araması için)
                where_clause = ""
                params = []
                
                if player_search:
                    # Oyuncu ismine göre arama (players tablosundan veya transfers tablosundaki player_name'den)
                    where_clause = "WHERE (p.name LIKE %s OR t.player_name LIKE %s)"
                    search_pattern = f"%{player_search}%"
                    params = [search_pattern, search_pattern]

                select_sql = f"""
                    SELECT t.*, p.name AS player_full_name, cf.name AS from_club_name, ct.name AS to_club_name
                    FROM transfers t
                    LEFT JOIN players p ON t.player_id = p.player_id
                    LEFT JOIN clubs cf ON t.from_club_id = cf.club_id
                    LEFT JOIN clubs ct ON t.to_club_id = ct.club_id
                    {where_clause}
                    ORDER BY {sort_column} {order}
                    LIMIT 100
                """
                cursor.execute(select_sql, params)
                transfers_data = cursor.fetchall()
                
                # --- NESTED QUERY 1: En çok transfer yapan oyuncu ---
                # player_id dolu olmasa bile player_name üzerinden hesapla, boş/g-null isimleri "Bilinmiyor" yap
                most_transferred_player = None
                try:
                    most_transferred_player_sql = """
                        SELECT 
                            COALESCE(p.name, t.player_name, 'Bilinmiyor') AS player_name,
                            COUNT(*) AS transfer_count
                        FROM transfers t
                        LEFT JOIN players p ON t.player_id = p.player_id
                        GROUP BY COALESCE(p.name, t.player_name, 'Bilinmiyor')
                        ORDER BY transfer_count DESC
                        LIMIT 1
                    """
                    cursor.execute(most_transferred_player_sql)
                    most_transferred_player = cursor.fetchone()
                except Exception as e:
                    print(f"Nested query 1 error: {e}")
                    most_transferred_player = None
                
                # --- NESTED QUERY 2: Ortalama transfer sayısından fazla transfer yapan kulüpler ---
                # İç sorgu: Ortalama transfer sayısını hesaplıyor
                # Dış sorgu: Bu ortalamadan fazla transfer yapan kulüpleri buluyor
                top_clubs_data = []
                try:
                    top_clubs_sql = """
                        SELECT 
                            c.name AS club_name,
                            COUNT(*) AS transfer_count
                        FROM clubs c
                        INNER JOIN transfers t ON t.to_club_id = c.club_id
                        WHERE t.to_club_id IS NOT NULL
                        GROUP BY c.club_id, c.name
                        HAVING COUNT(*) > (
                            SELECT COALESCE(AVG(transfer_count), 0)
                            FROM (
                                SELECT COUNT(*) AS transfer_count
                                FROM transfers
                                WHERE to_club_id IS NOT NULL
                                GROUP BY to_club_id
                            ) AS avg_calc
                        )
                        ORDER BY transfer_count DESC
                        LIMIT 5
                    """
                    cursor.execute(top_clubs_sql)
                    top_clubs_data = cursor.fetchall() or []
                except Exception as e:
                    print(f"Nested query 2 error: {e}")
                    top_clubs_data = []
                
    except Exception as e:
        return f"<h1>Transfer Verileri Çekilemedi:</h1><p>{e}</p>"

    return render_template("transfers.html", transfers=transfers_data, clubs=clubs_data, players=players_data, 
                         current_page="transfers", sort_by=sort_by, order=order, player_search=player_search,
                         most_transferred_player=most_transferred_player, top_clubs=top_clubs_data)

@app.route('/transfers/delete/<int:transfer_id>', methods=['POST'])
def delete_transfer(transfer_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM transfers WHERE transfer_id = %s", (transfer_id,))
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
        from_club_id = int(request.form.get('from_club_id')) if request.form.get('from_club_id') else None
        to_club_id = int(request.form.get('to_club_id')) if request.form.get('to_club_id') else None
        transfer_season = request.form.get('transfer_season', '').strip()
        player_name = request.form['player_name']
        
        # Eğer season boşsa, tarihten otomatik hesapla
        if not transfer_season and transfer_date:
            transfer_season = calculate_season_from_date(transfer_date)

        update_sql = """
            UPDATE transfers SET player_id=%s, transfer_date=%s, from_club_id=%s, to_club_id=%s, transfer_season=%s, player_name=%s
            WHERE transfer_id=%s
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(update_sql, (player_id, transfer_date, from_club_id, to_club_id, transfer_season, player_name, transfer_id))
            conn.commit()
        return redirect(url_for('transfers'))
    except Exception as e:
        return f"<h1>Transfer Güncelleme Hatası:</h1><p>{e}</p>"

@app.route('/api/player/<int:player_id>')
def get_player(player_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT player_id, name FROM players WHERE player_id = %s LIMIT 1", (player_id,))
                result = cursor.fetchone()
                if not result:
                    return jsonify({"player_id": player_id, "name": None}), 404
                return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/players/search')
def search_players():
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify([])
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                search_sql = "SELECT player_id, name FROM players WHERE name LIKE %s ORDER BY name ASC LIMIT 50"
                cursor.execute(search_sql, (f'%{query}%',))
                results = cursor.fetchall()
                return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# 4. PLAYERS (OYUNCULAR) CRUD - (DÜZELTİLDİ)
# ==========================================
@app.route('/players', methods=['GET', 'POST'])
def players():
    # --- POST: YENİ OYUNCU EKLEME --- (Aynı kalıyor)
    if request.method == 'POST':
        # ... (mevcut ekleme kodunuz) ...
        try:
            player_id = int(request.form['player_id'])
            name = request.form['name']
            position = request.form['position']
            market_val_input = request.form.get('market_value_in_eur', 0)
            market_value = float(market_val_input) if market_val_input else 0.0
            
            club_id_val = request.form.get('current_club_id')
            current_club_id = int(club_id_val) if club_id_val else None

            insert_sql = "INSERT INTO players (player_id, name, position, market_value_in_eur, current_club_id) VALUES (%s, %s, %s, %s, %s)"
            
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(insert_sql, (player_id, name, position, market_value, current_club_id))
                conn.commit()
            return redirect(url_for('players'))
        except Exception as e:
            return f"<h1>Oyuncu Ekleme Hatası:</h1><p>{e}</p>"

    # --- GET: LİSTELEME VE GELİŞMİŞ ANALİZ ---
    players_data = []
    clubs_data = []
    advanced_stats = []

    # GELİŞMİŞ ANALİZ SORĞUSU (Rubric Gereksinimleri)
    # 4 Tablo: players, clubs, competitions, transfers [Complex Join]
    # LEFT JOIN kullanıldı [Outer Join]
    # İç sorgu ile ortalama piyasa değeri hesaplandı [Nested Query]
    # Oyuncu başına transfer sayısı hesaplandı [Group By]
    advanced_sql = """
    SELECT 
        p.player_id,  -- Bu sütunu ekledik
        p.name AS player_name, 
        p.position, 
        c.name AS club_name, 
        comp.name AS league_name,
        p.market_value_in_eur,
        COUNT(t.transfer_id) AS total_transfers
    FROM players p
    LEFT JOIN clubs c ON p.current_club_id = c.club_id
    LEFT JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
    LEFT JOIN transfers t ON p.player_id = t.player_id
    WHERE p.market_value_in_eur > (
        SELECT AVG(market_value_in_eur) 
        FROM players 
        WHERE market_value_in_eur > 0
    )
    GROUP BY p.player_id, p.name, p.position, c.name, comp.name, p.market_value_in_eur
    ORDER BY p.market_value_in_eur DESC 
    LIMIT 10
"""

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 1. Dropdown için kulüpler
                cursor.execute("SELECT club_id, name FROM clubs ORDER BY name ASC LIMIT 600")
                clubs_data = cursor.fetchall()
                
                # 2. Standart Oyuncu Listesi
                cursor.execute("""
                    SELECT p.player_id, p.name, p.position, p.market_value_in_eur, p.current_club_id, c.name AS club_name
                    FROM players p
                    LEFT JOIN clubs c ON p.current_club_id = c.club_id
                    ORDER BY p.market_value_in_eur DESC LIMIT 100
                """)
                players_data = cursor.fetchall()

                # 3. Gelişmiş Analiz Verisi (Hocanın istediği yer)
                cursor.execute(advanced_sql)
                advanced_stats = cursor.fetchall()
                
    except Exception as e:
        return f"<h1>Veri Çekme Hatası:</h1><p>{e}</p>"

    return render_template('players.html', 
                           players=players_data, 
                           clubs=clubs_data, 
                           advanced_stats=advanced_stats, 
                           current_page="players")

@app.route('/players/delete/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM players WHERE player_id = %s", (player_id,))
            conn.commit()
        return redirect(url_for('players'))
    except Exception as e:
        return f"<h1>Silme Hatası:</h1><p>{e}</p>"

@app.route('/players/update', methods=['POST'])
def update_player():
    try:
        player_id = int(request.form['player_id'])
        name = request.form['name']
        position = request.form['position']
        
        market_val_input = request.form.get('market_value_in_eur', 0)
        market_value = float(market_val_input) if market_val_input else 0.0
        
        club_id_val = request.form.get('current_club_id')
        current_club_id = int(club_id_val) if club_id_val else None
        
        update_sql = """
            UPDATE players SET name=%s, position=%s, market_value_in_eur=%s, current_club_id=%s
            WHERE player_id=%s
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(update_sql, (name, position, market_value, current_club_id, player_id))
            conn.commit()
        return redirect(url_for('players'))
    except Exception as e:
        return f"<h1>Güncelleme Hatası:</h1><p>{e}</p>"

@app.route('/players/<int:player_id>')
def player_page(player_id):
    try:
        # SELECT * FROM players WHERE player_id = player_id
        # Ayrıca kulüp bilgisini de JOIN ile çekiyoruz
        select_sql = """
            SELECT p.*, c.name AS club_name, c.stadium_name AS club_stadium
            FROM players p
            LEFT JOIN clubs c ON p.current_club_id = c.club_id
            WHERE p.player_id = %s
            LIMIT 1
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(select_sql, (player_id,))
                player = cursor.fetchone()
                
                if not player:
                    return f"<h1>Oyuncu Bulunamadı</h1><p>Player ID: {player_id} bulunamadı.</p>", 404
        
        return render_template('player.html', player=player, current_page="players")
    except Exception as e:
        return f"<h1>Hata:</h1><p>{e}</p>", 500


# ==========================================
# 5. CLUBS (KULÜPLER) CRUD
# ==========================================

@app.route('/clubs', methods=['GET', 'POST'])
def clubs_route():
    if request.method == 'POST':
        try:
            club_id = int(request.form['club_id'])
            name = request.form['name']
            stadium_name = request.form['stadium_name']
            comp_id = request.form.get('domestic_competition_id')
            domestic_competition_id = comp_id if comp_id else None

            insert_sql = """
                INSERT INTO clubs (club_id, name, stadium_name, domestic_competition_id)
                VALUES (%s, %s, %s, %s)
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(insert_sql, (club_id, name, stadium_name, domestic_competition_id))
                conn.commit()
            return redirect(url_for('clubs_route'))
        except Exception as e:
             return f"<h1>Kulüp Ekleme Hatası:</h1><p>{e}</p>"

    # GET
    comps_sql = "SELECT competition_id, name FROM competitions ORDER BY name ASC"
    select_sql = """
        SELECT c.club_id, c.name, c.stadium_name, c.domestic_competition_id, comp.name AS competition_name
        FROM clubs c
        LEFT JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
        ORDER BY c.club_id DESC LIMIT 100
    """
    
    clubs_data = []
    competitions_data = []
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(comps_sql)
                competitions_data = cursor.fetchall()
                cursor.execute(select_sql)
                clubs_data = cursor.fetchall()
    except Exception as e:
        return f"<h1>Veri Hatası:</h1><p>{e}</p>"

    return render_template('clubs.html', clubs=clubs_data, competitions=competitions_data, current_page="clubs")

@app.route('/clubs/update', methods=['POST'])
def update_club():
    try:
        club_id = int(request.form['club_id'])
        name = request.form['name']
        stadium_name = request.form['stadium_name']
        comp_id = request.form.get('domestic_competition_id')
        domestic_competition_id = comp_id if comp_id else None
        
        update_sql = "UPDATE clubs SET name=%s, stadium_name=%s, domestic_competition_id=%s WHERE club_id=%s"
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(update_sql, (name, stadium_name, domestic_competition_id, club_id))
            conn.commit()
        return redirect(url_for('clubs_route'))
    except Exception as e:
        return f"<h1>Güncelleme Hatası:</h1><p>{e}</p>"

@app.route('/clubs/delete/<int:club_id>', methods=['POST'])
def delete_club(club_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM clubs WHERE club_id = %s", (club_id,))
            conn.commit()
        return redirect(url_for('clubs_route'))
    except Exception as e:
        return f"<h1>Silme Hatası:</h1><p>{e}</p>"
#----------------
# 
#COMPETİTİONS
#-----------
@app.route('/competitions', methods=['GET', 'POST'])
def competitions_route():
    # POST İŞLEMİ (Ekleme) - Aynı kalıyor
    if request.method == 'POST':
        try:
            competition_id = request.form['competition_id'] 
            name = request.form['name']
            type_ = request.form['type']
            country_id_val = request.form.get('country_id')
            country_id = int(country_id_val) if country_id_val else None
            
            insert_sql = "INSERT INTO competitions (competition_id, name, type, country_id) VALUES (%s, %s, %s, %s)"
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(insert_sql, (competition_id, name, type_, country_id))
                conn.commit()
            return redirect(url_for('competitions_route'))
        except Exception as e:
            return f"<h1>Lig Ekleme Hatası:</h1><p>{e}</p>"

    # GET İŞLEMİ
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 1. Mevcut Tablo Listesi
                query_list = """
                    SELECT 
                        comp.competition_id, comp.name, comp.type, comp.country_id,
                        c.country_name, c.iso_code, c.confederation, c.latitude, c.longitude
                    FROM competitions comp
                    LEFT JOIN countries c ON comp.country_id = c.country_id
                    ORDER BY comp.name ASC LIMIT 100
                """
                cursor.execute(query_list)
                comps_data = cursor.fetchall()
                
                # 2. Dropdown verisi
                cursor.execute("SELECT country_id, country_name FROM countries ORDER BY country_name ASC")
                countries_list = cursor.fetchall()

                # 3. REKABET ANALİZİ (GÜNCELLENDİ)
                analysis_sql = """
                    SELECT 
                        comp.name AS league_name,
                        c.country_name,
                        c.iso_code,
                        top_club.name AS dominant_club,
                        FORMAT(stats.max_val, 2) AS max_value,
                        FORMAT(stats.avg_val, 2) AS avg_value,
                        stats.dominance_ratio,
                        COUNT(p.player_id) AS total_players  -- YENİ EKLENDİ
                    FROM competitions comp
                    JOIN countries c ON comp.country_id = c.country_id
                    
                    -- 1. NESTED QUERY & GROUP BY (Hesaplama)
                    JOIN (
                        SELECT 
                            domestic_competition_id, 
                            MAX(total_market_value) as max_val,
                            AVG(total_market_value) as avg_val,
                            (MAX(total_market_value) / NULLIF(AVG(total_market_value), 0)) as dominance_ratio
                        FROM clubs
                        WHERE total_market_value > 0
                        GROUP BY domestic_competition_id
                    ) stats ON comp.competition_id = stats.domestic_competition_id
                    
                    -- 2. COMPLEX JOIN (Dominant Kulüp İsmi)
                    JOIN clubs top_club ON top_club.domestic_competition_id = comp.competition_id 
                        AND top_club.total_market_value = stats.max_val
                    
                    -- 3. OUTER JOIN (LEFT JOIN) - Rubrik İçin Oyuncu Sayısı
                    LEFT JOIN players p ON p.current_club_domestic_competition_id = comp.competition_id
                    
                    WHERE comp.type = 'domestic_league' AND stats.avg_val > 0
                    
                    -- Ana sorguda da Group By gerekiyor çünkü COUNT(p.player_id) ekledik
                    GROUP BY comp.competition_id, comp.name, c.country_name, c.iso_code, top_club.name, stats.max_val, stats.avg_val, stats.dominance_ratio
                    
                    ORDER BY stats.dominance_ratio ASC
                    LIMIT 20
                """
                
                cursor.execute(analysis_sql)
                competitiveness_data = cursor.fetchall()

    except Exception as e:
        return f"<h1>Veri Hatası:</h1><p>{e}</p>"

    return render_template('competitions.html', 
                           competitions=comps_data, 
                           all_countries=countries_list,
                           competitiveness_data=competitiveness_data, # Veriyi gönderiyoruz
                           current_page="competitions")

@app.route('/competitions/update', methods=['POST'])
def update_competition():
    try:
        competition_id = request.form['competition_id']
        name = request.form['name']
        type_ = request.form['type']
        
        # Update işleminde country_id
        country_id_val = request.form.get('country_id')
        country_id = int(country_id_val) if country_id_val else None
        
        update_sql = "UPDATE competitions SET name=%s, type=%s, country_id=%s WHERE competition_id=%s"
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(update_sql, (name, type_, country_id, competition_id))
            conn.commit()
        return redirect(url_for('competitions_route'))
    except Exception as e:
         return f"<h1>Güncelleme Hatası:</h1><p>{e}</p>"

# ... (Delete ve diğer rotalar aynı) ...

@app.route('/competitions/delete/<string:competition_id>', methods=['POST'])
def delete_competition(competition_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM competitions WHERE competition_id = %s", (competition_id,))
            conn.commit()
        return redirect(url_for('competitions_route'))
    except Exception as e:
        return f"<h1>Silme Hatası:</h1><p>{e}</p>"

# ... (Kalan kodlar ve main bloğu aynı)

# ==========================================
# 7. CLUB PROFILE (TEK KULÜP DETAYI)
# ==========================================
@app.route('/clubs/<int:club_id>')
def club_profile(club_id):
    try:
        # İzin verilen sütunları ve logo için club_id'yi çekiyoruz
        select_sql = """
            SELECT 
                club_id,
                name,
                squad_size,
                average_age,
                foreigners_number,
                foreigners_percentage,
                national_team_players,
                stadium_name,
                stadium_seats,
                net_transfer_record,
                last_season
            FROM clubs
            WHERE club_id = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(select_sql, (club_id,))
                club_data = cursor.fetchone()
        
        if not club_data:
            return f"<h1>Kulüp Bulunamadı (ID: {club_id})</h1>", 404
            
        return render_template('club.html', club=club_data)
        
    except Exception as e:
        return f"<h1>Veri Çekme Hatası:</h1><p>{e}</p>"
    
# ==========================================
# 8. COMPLEX REPORT (RUBRIC: NESTED QUERY + 4 JOINS)
# ==========================================
@app.route('/reports/top-clubs-performance')
def top_clubs_performance_report():
    try:
        # GÜNCELLENMİŞ SORGU (DAHA GÜVENLİ)
        # 1. INNER JOIN games yerine LEFT JOIN kullandık ki 'games' tablosunda veri eksikse bile rapor çalışsın.
        # 2. Hosting kontrolünü kaldırdık veya esnettik.
        # 3. Nested Query hala aktif (Rubrik puanı için).
        
        complex_sql = """
            SELECT 
                COALESCE(comp.name, 'Unknown League') AS competition_name,
                c.name AS club_name,
                COUNT(cg.game_id) AS games_played,
                SUM(cg.own_goals) AS total_goals,
                AVG(cg.own_goals) AS avg_goals
            FROM club_games cg
            INNER JOIN clubs c ON cg.club_id = c.club_id
            LEFT JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
            LEFT JOIN games g ON cg.game_id = g.game_id  -- INNER JOIN yerine LEFT JOIN yaptık (Veri kaybını önlemek için)
            WHERE c.total_market_value >= (
                -- NESTED QUERY: Ortalamanın üzerindeki (veya eşit) kulüpleri getir
                SELECT COALESCE(AVG(total_market_value), 0) 
                FROM clubs 
            )
            GROUP BY comp.name, c.name
            ORDER BY total_goals DESC
            LIMIT 50
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(complex_sql)
                report_data = cursor.fetchall()
        
        return render_template('report_complex.html', report_data=report_data)
        
    except Exception as e:
        return f"<h1>Rapor Hatası:</h1><p>{e}</p>"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)



