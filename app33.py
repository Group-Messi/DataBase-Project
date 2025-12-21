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
# 1. CLUB_GAMES (KULÜP MAÇLARI) CRUD - (DÜZELTİLDİ)
# ==========================================
@app.route('/club_games', methods=['GET', 'POST'])
def club_games():
    # POST: Yeni Maç Ekleme (Burası doğruydu)
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
            return handle_exception(e)

    # GET: Listeleme (Burası doğruydu)
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
        return handle_exception(e)

    return render_template('club_games.html', games=games_data, clubs=clubs_data, current_page="club_games")

# DELETE İŞLEMİ GÜNCELLENDİ: Hem game_id hem club_id lazım
@app.route('/club_games/delete/<int:game_id>/<int:club_id>', methods=['POST'])
def delete_club_game(game_id, club_id):
    try:
        # Composite Key olduğu için ikisini birden kontrol ediyoruz
        delete_sql = "DELETE FROM club_games WHERE game_id = %s AND club_id = %s"
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(delete_sql, (game_id, club_id))
            conn.commit()
        return redirect(url_for('club_games'))
    except Exception as e:
        return handle_exception(e)

# UPDATE İŞLEMİ GÜNCELLENDİ: club_id WHERE koşuluna eklendi
@app.route('/club_games/update', methods=['POST'])
def update_club_game():
    try:
        game_id = int(request.form['game_id'])
        club_id = int(request.form['club_id']) # HTML Form'da bu input hidden olarak bulunmalı
        hosting = request.form['hosting']
        own_goals = int(request.form['own_goals'])
        opponent_goals = int(request.form['opponent_goals'])
        
        # Sadece o maçtaki o kulübü güncelle
        update_sql = """
            UPDATE club_games 
            SET hosting=%s, own_goals=%s, opponent_goals=%s 
            WHERE game_id=%s AND club_id=%s
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(update_sql, (hosting, own_goals, opponent_goals, game_id, club_id))
            conn.commit()
        return redirect(url_for('club_games'))
    except Exception as e:
        return handle_exception(e)
# ==========================================
# 2. GAMES (MAÇLAR) CRUD - (DÜZELTİLDİ)
# ==========================================
@app.route('/games', methods=['GET', 'POST'])
def games():
    # POST: Yeni Maç Ekleme
    if request.method == 'POST':
        try:
            home_club_id = int(request.form['home_club_id'])
            away_club_id = int(request.form['away_club_id'])
            game_date = request.form['game_date']
            home_club_goals = int(request.form.get('home_club_goals', 0))
            away_club_goals = int(request.form.get('away_club_goals', 0))
            
            insert_sql = """
                INSERT INTO games (home_club_id, away_club_id, game_date, home_club_goals, away_club_goals)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(insert_sql, (home_club_id, away_club_id, game_date, home_club_goals, away_club_goals))
                conn.commit()
            return redirect(url_for('games'))
        except Exception as e:
            return handle_exception(e)


    clubs_sql = "SELECT club_id, name FROM clubs ORDER BY name ASC"
    
    select_sql = """
        SELECT g.game_id, g.home_club_id, g.away_club_id, g.game_date, 
               g.home_club_goals, g.away_club_goals,
               hc.name AS home_club_name, ac.name AS away_club_name
        FROM games g
        LEFT JOIN clubs hc ON g.home_club_id = hc.club_id
        LEFT JOIN clubs ac ON g.away_club_id = ac.club_id  
        ORDER BY g.game_Date DESC, g.home_club_id ASC LIMIT 50
    """

    # DÜZELTME: is_major_national_league = 1 (Boolean/TinyInt kontrolü)
    complex_sql = """
        SELECT SUM(g.home_club_goals + g.away_club_goals) AS total_goals
        FROM games g
         JOIN clubs c1 ON g.home_club_id = c1.club_id
         Join clubs c2 on g.away_club_id = c2.club_id
         JOIN competitions comp ON c1.domestic_competition_id = comp.competition_id AND c2.domestic_competition_id = comp.competition_id
         WHERE comp.is_major_national_league = 1
    """

    # NOT: stadium_seats clubs tablosunda duruyorsa bu çalışır.
    # GÜNCELLENDİ: Takım değeri 0.7 Milyar (700 Milyon) Euro'dan büyük olan kulüplerin maçları
    # Bu sorgu players tablosundan toplama yaparak (SUM) filtreleme yapar.
    nested_sql = """
        SELECT g.game_id, g.game_date, hc.name as home_name, ac.name as away_name
        FROM games g
        JOIN clubs hc ON g.home_club_id = hc.club_id
        JOIN clubs ac ON g.away_club_id = ac.club_id
        WHERE g.home_club_id IN (
            -- NESTED QUERY: Toplam değeri 700.000.000 Euro üzeri olan kulüpler
            SELECT current_club_id 
            FROM players 
            GROUP BY current_club_id 
            HAVING SUM(market_value_in_eur) > 700000000
        )
        ORDER BY g.game_date DESC LIMIT 7
    """

    groupby_sql = """
        SELECT comp.name, COUNT(g.game_id) as match_count, SUM(g.home_club_goals + g.away_club_goals) as total_goals
        FROM games g
        JOIN clubs c ON g.home_club_id = c.club_id
        JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
        GROUP BY comp.competition_id
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
                # Dönen değer Decimal olabilir, int/float'a çevirmek güvenlidir
                major_league_goals = int(res['total_goals']) if res and res['total_goals'] else 0

                cursor.execute(nested_sql)
                big_stadium_games = cursor.fetchall()

                cursor.execute(groupby_sql)
                league_stats = cursor.fetchall()

    except Exception as e:
        return handle_exception(e)

    return render_template('games.html', 
                           games=games_data, 
                           clubs=clubs_data, 
                           major_goals=major_league_goals,
                           stadium_games=big_stadium_games,
                           league_stats=league_stats,
                           current_page="games")

# delete_game ve update_game kısımları standart olduğu için (game_id unique) bir sorun yok.
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
        return handle_exception(e)

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
        return handle_exception(e)
# ==========================================
# 3. TRANSFERS CRUD
# ==========================================
# ==========================================
# 3. TRANSFERS CRUD (3NF UYUMLU - DÜZELTİLDİ)
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
            
            # NOT: player_name formdan gelse bile veritabanına YAZMIYORUZ.
            # Çünkü transfers tablosundan o sütunu sildik.

            # Eğer season boşsa, tarihten otomatik hesapla
            if not transfer_season and transfer_date:
                transfer_season = calculate_season_from_date(transfer_date)

            # transfer_id AUTO_INCREMENT mantığı
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    try:
                        # 1. YÖNTEM: AUTO_INCREMENT (player_name SİLİNDİ)
                        insert_sql = """
                            INSERT INTO transfers (player_id, transfer_date, from_club_id, to_club_id, transfer_season)
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_sql, (player_id, transfer_date, from_club_id, to_club_id, transfer_season))
                    except Exception as auto_inc_error:
                        # 2. YÖNTEM: Manuel ID Hesaplama (Eğer auto_inc yoksa)
                        if "doesn't have a default value" in str(auto_inc_error) or "Field 'transfer_id'" in str(auto_inc_error):
                            cursor.execute("SELECT COALESCE(MAX(transfer_id), 0) as max_id FROM transfers FOR UPDATE")
                            result = cursor.fetchone()
                            next_transfer_id = (result['max_id'] if result else 0) + 1
                            
                            # player_name BURADAN DA SİLİNDİ
                            insert_sql = """
                                INSERT INTO transfers (transfer_id, player_id, transfer_date, from_club_id, to_club_id, transfer_season)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(insert_sql, (next_transfer_id, player_id, transfer_date, from_club_id, to_club_id, transfer_season))
                        else:
                            raise auto_inc_error
                conn.commit()
            return redirect(url_for('transfers'))
        except Exception as e:
            return handle_exception(e)

    # GET logic
    try:
        sort_by = request.args.get('sort_by', 'transfer_date')
        order = request.args.get('order', 'DESC')
        player_search = request.args.get('player_search', '').strip()
        
        # Güvenlik: player_name artık sadece p.name (JOIN tablosundan) geliyor
        allowed_sort_columns = {
            'transfer_date': 't.transfer_date',
            'player_name': 'p.name',  # DEĞİŞTİ: Artık t.player_name yok
            'from_club': 'cf.name',
            'to_club': 'ct.name',
            'season': 't.transfer_season'
        }
        
        sort_column = allowed_sort_columns.get(sort_by, 't.transfer_date')
        
        if order not in ['ASC', 'DESC']:
            order = 'DESC'
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT club_id, name FROM clubs ORDER BY name ASC LIMIT 500")
                clubs_data = cursor.fetchall()
                
                cursor.execute("SELECT player_id, name FROM players ORDER BY name ASC LIMIT 200")
                players_data = cursor.fetchall()

                # WHERE koşulu (Sadece players tablosundaki isme bakıyoruz)
                where_clause = ""
                params = []
                
                if player_search:
                    # DEĞİŞTİ: t.player_name kontrolü kaldırıldı
                    where_clause = "WHERE p.name LIKE %s"
                    search_pattern = f"%{player_search}%"
                    params = [search_pattern]

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
                # DEĞİŞTİ: t.player_name kalktı, p.name kullanıldı
                most_transferred_player = None
                try:
                    most_transferred_player_sql = """
                        SELECT 
                            COALESCE(p.name, 'Bilinmiyor') AS player_name,
                            COUNT(*) AS transfer_count
                        FROM transfers t
                        LEFT JOIN players p ON t.player_id = p.player_id
                        GROUP BY p.player_id, p.name
                        ORDER BY transfer_count DESC
                        LIMIT 1
                    """
                    cursor.execute(most_transferred_player_sql)
                    most_transferred_player = cursor.fetchone()
                except Exception as e:
                    print(f"Nested query 1 error: {e}")
                    most_transferred_player = None
                
                # --- NESTED QUERY 2: (Bu kısım değişmedi, çünkü clubs ve transfers ID kullanıyor) ---
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
        return handle_exception(e)

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
        return handle_exception(e)

@app.route('/transfers/update', methods=['POST'])
def update_transfer():
    try:
        transfer_id = int(request.form['transfer_id'])
        player_id = int(request.form['player_id'])
        transfer_date = request.form['transfer_date']
        from_club_id = int(request.form.get('from_club_id')) if request.form.get('from_club_id') else None
        to_club_id = int(request.form.get('to_club_id')) if request.form.get('to_club_id') else None
        transfer_season = request.form.get('transfer_season', '').strip()
        
        # NOT: player_name formdan gelse de update etmiyoruz.
        
        if not transfer_season and transfer_date:
            transfer_season = calculate_season_from_date(transfer_date)

        # DEĞİŞTİ: player_name SET kısmından çıkarıldı
        update_sql = """
            UPDATE transfers SET player_id=%s, transfer_date=%s, from_club_id=%s, to_club_id=%s, transfer_season=%s
            WHERE transfer_id=%s
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(update_sql, (player_id, transfer_date, from_club_id, to_club_id, transfer_season, transfer_id))
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
        return handle_exception(e)

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
        return handle_exception(e)


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
            return handle_exception(e)

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
        return handle_exception(e)

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
        return handle_exception(e)

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
        return handle_exception(e)

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
        return handle_exception(e)


# ==========================================
# 5. CLUBS (KULÜPLER) CRUD (3NF UYUMLU)
# ==========================================

@app.route('/clubs', methods=['GET', 'POST'])
def clubs_route():
    # --- POST: KULÜP EKLEME ---
    if request.method == 'POST':
        try:
            club_id = int(request.form['club_id'])
            name = request.form['name']
            stadium_name = request.form['stadium_name']
            comp_id = request.form.get('domestic_competition_id')
            domestic_competition_id = comp_id if comp_id else None

            # Sadece fiziksel olarak var olan sütunlara ekleme yapıyoruz.
            # squad_size, market_value gibi alanlar INSERT edilmez, hesaplanır.
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
             return handle_exception(e)

    # --- GET: LİSTELEME ---
    # 3NF olduğu için Squad Size ve Market Value bilgilerini Players tablosundan saydırıyoruz.
    select_sql = """
        SELECT 
            c.club_id, 
            c.name, 
            c.stadium_name, 
            c.domestic_competition_id, 
            comp.name AS competition_name,
            
            -- Anlık Hesaplamalar (Subqueries)
            (SELECT COUNT(*) FROM players WHERE current_club_id = c.club_id) as squad_size,
            (SELECT COALESCE(SUM(market_value_in_eur), 0) / 1000000 FROM players WHERE current_club_id = c.club_id) as total_market_value
            
        FROM clubs c
        LEFT JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
        ORDER BY c.club_id ASC 
        LIMIT 100
    """
    
    comps_sql = "SELECT competition_id, name FROM competitions ORDER BY name ASC"
    
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
        return handle_exception(e)

    return render_template('clubs.html', clubs=clubs_data, competitions=competitions_data, current_page="clubs")

@app.route('/clubs/update', methods=['POST'])
def update_club():
    try:
        club_id = int(request.form['club_id'])
        name = request.form['name']
        stadium_name = request.form['stadium_name']
        comp_id = request.form.get('domestic_competition_id')
        domestic_competition_id = comp_id if comp_id else None
        
        # Sadece düzenlenebilir alanları güncelliyoruz
        update_sql = "UPDATE clubs SET name=%s, stadium_name=%s, domestic_competition_id=%s WHERE club_id=%s"
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(update_sql, (name, stadium_name, domestic_competition_id, club_id))
            conn.commit()
        return redirect(url_for('clubs_route'))
    except Exception as e:
        return handle_exception(e)

@app.route('/clubs/delete/<int:club_id>', methods=['POST'])
def delete_club(club_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM clubs WHERE club_id = %s", (club_id,))
            conn.commit()
        return redirect(url_for('clubs_route'))
    except Exception as e:
        return handle_exception(e)
# ==========================================
# 6. COMPETITIONS (LİGLER/KUPALAR) CRUD (3NF UYUMLU)
# ==========================================

@app.route('/competitions', methods=['GET', 'POST'])
def competitions_route():
    # --- POST: EKLEME İŞLEMİ (Değişmedi) ---
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
            return handle_exception(e)

    # --- GET: LİSTELEME VE ANALİZ ---
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

                # 3. REKABET ANALİZİ (3NF UYUMLU GÜNCELLENDİ)
                # clubs.total_market_value sütunu silindiği için değerleri players tablosundan topluyoruz.
                analysis_sql = """
                    SELECT 
                        comp.name AS league_name,
                        c.country_name,
                        c.iso_code,
                        
                        -- En değerli kulübün ismini bulmak için joinlenen tablo
                        top_club_calc.name AS dominant_club,
                        
                        FORMAT(stats.max_val / 1000000, 2) AS max_value, -- Milyon Euro
                        FORMAT(stats.avg_val / 1000000, 2) AS avg_value, -- Milyon Euro
                        stats.dominance_ratio,
                        stats.total_players
                        
                    FROM competitions comp
                    JOIN countries c ON comp.country_id = c.country_id
                    
                    JOIN (
                        -- 2. ADIM: LİG SEVİYESİNDE İSTATİSTİKLER (MAX, AVG, SUM)
                        SELECT 
                            domestic_competition_id, 
                            MAX(club_val) as max_val,
                            AVG(club_val) as avg_val,
                            (MAX(club_val) / NULLIF(AVG(club_val), 0)) as dominance_ratio,
                            SUM(squad_size) as total_players
                        FROM (
                            -- 1. ADIM: KULÜP SEVİYESİNDE HESAPLAMA (Calculated Value)
                            SELECT 
                                cl.domestic_competition_id, 
                                COALESCE(SUM(p.market_value_in_eur), 0) as club_val,
                                COUNT(p.player_id) as squad_size
                            FROM clubs cl
                            LEFT JOIN players p ON cl.club_id = p.current_club_id
                            GROUP BY cl.club_id, cl.domestic_competition_id
                        ) as club_calc
                        GROUP BY domestic_competition_id
                    ) stats ON comp.competition_id = stats.domestic_competition_id
                    
                    -- Dominant kulübün ismini almak için tekrar hesaplanmış tabloya join
                    JOIN (
                        SELECT 
                            cl.domestic_competition_id,
                            cl.name,
                            COALESCE(SUM(p.market_value_in_eur), 0) as club_val
                        FROM clubs cl
                        LEFT JOIN players p ON cl.club_id = p.current_club_id
                        GROUP BY cl.club_id, cl.domestic_competition_id, cl.name
                    ) top_club_calc ON top_club_calc.domestic_competition_id = comp.competition_id 
                                   AND top_club_calc.club_val = stats.max_val
                    
                    WHERE comp.type = 'domestic_league' AND stats.avg_val > 0
                    ORDER BY stats.dominance_ratio ASC
                    LIMIT 20
                """
                
                cursor.execute(analysis_sql)
                competitiveness_data = cursor.fetchall()

    except Exception as e:
        return handle_exception(e)

    return render_template('competitions.html', 
                           competitions=comps_data, 
                           all_countries=countries_list,
                           competitiveness_data=competitiveness_data,
                           current_page="competitions")

@app.route('/competitions/update', methods=['POST'])
def update_competition():
    try:
        competition_id = request.form['competition_id']
        name = request.form['name']
        type_ = request.form['type']
        
        country_id_val = request.form.get('country_id')
        country_id = int(country_id_val) if country_id_val else None
        
        update_sql = "UPDATE competitions SET name=%s, type=%s, country_id=%s WHERE competition_id=%s"
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(update_sql, (name, type_, country_id, competition_id))
            conn.commit()
        return redirect(url_for('competitions_route'))
    except Exception as e:
         return handle_exception(e)

@app.route('/competitions/delete/<string:competition_id>', methods=['POST'])
def delete_competition(competition_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM competitions WHERE competition_id = %s", (competition_id,))
            conn.commit()
        return redirect(url_for('competitions_route'))
    except Exception as e:
        return handle_exception(e)
# ==========================================
# 7. CLUB PROFILE (TEK KULÜP DETAYI - 3NF UYUMLU)
# ==========================================
@app.route('/clubs/<int:club_id>')
def club_profile(club_id):
    try:
        # Derived Attribute'ları (Türetilmiş Sütunlar) hesaplayarak çekiyoruz
        select_sql = """
            SELECT 
                c.club_id,
                c.name,
                c.stadium_name,
                -- c.stadium_seats SİLİNDİ
                c.net_transfer_record,
                c.last_season,
                
                -- SQUAD SIZE
                (SELECT COUNT(*) FROM players WHERE current_club_id = c.club_id) as squad_size,
                
                -- AVERAGE AGE
                (SELECT AVG(TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE())) 
                 FROM players 
                 WHERE current_club_id = c.club_id) as average_age,
                 
                -- FOREIGNERS
                (SELECT COUNT(*) 
                 FROM players p
                 JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
                 JOIN countries country ON comp.country_id = country.country_id
                 WHERE p.current_club_id = c.club_id 
                 AND p.country_of_citizenship != country.country_name) as foreigners_number,

                 -- MARKET VALUE
                 (SELECT COALESCE(SUM(market_value_in_eur), 0) / 1000000 
                  FROM players 
                  WHERE current_club_id = c.club_id) as total_market_value

            FROM clubs c
            WHERE c.club_id = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(select_sql, (club_id,))
                club_data = cursor.fetchone()
        
        if not club_data:
            return f"<h1>Kulüp Bulunamadı (ID: {club_id})</h1>", 404
            
        return render_template('club.html', club=club_data)
        
    except Exception as e:
        return handle_exception(e)

# ==========================================
# 8. COMPLEX REPORT (RUBRIC: NESTED QUERY + 4 JOINS + 3NF UYUMLU)
# ==========================================
@app.route('/reports/top-clubs-performance')
def top_clubs_performance_report():
    try:
        # GÜNCELLENMİŞ SORGU (3NF İÇİN)
        # total_market_value olmadığı için bunu hesaplamalıyız.
        
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
            LEFT JOIN games g ON cg.game_id = g.game_id
            
            -- WHERE Koşulu: Kulübün değeri > Ortalama Kulüp Değeri
            -- Burada iç içe sorgularla hesaplama yapıyoruz.
            WHERE (
                SELECT COALESCE(SUM(p.market_value_in_eur), 0)
                FROM players p
                WHERE p.current_club_id = c.club_id
            ) >= (
                -- TÜM KULÜPLERİN ORTALAMA DEĞERİ (Nested Query)
                SELECT AVG(club_val)
                FROM (
                    SELECT SUM(p2.market_value_in_eur) as club_val
                    FROM clubs c2
                    JOIN players p2 ON c2.club_id = p2.current_club_id
                    GROUP BY c2.club_id
                ) as avg_calc
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
        return handle_exception(e)
    
## 9 - ERROR HANDLING

@app.errorhandler(404)
def page_not_found(e):
    # This handles when a user goes to a URL that doesn't exist
    return render_template('error.html', 
                           error_title="404 - Page Not Found", 
                           error_message="The page you are looking for might have been removed or is temporarily unavailable."), 404

@app.errorhandler(500)
@app.errorhandler(Exception) # This catches any unhandled python exceptions
def handle_exception(e):
    # This handles database errors, logic errors, etc.
    # We pass the exception message to the template for debugging
    return render_template('error.html', 
                           error_title="Internal Server Error",error_message=str(e)), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)



